from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
import logging
from datetime import datetime
from fastapi.responses import StreamingResponse
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.database import get_db
from backend.models.chat import ChatSession, ChatMessage
from backend.services.llm_service import LLMService
from backend.services.rag_service import RAGService

# Define request and response models using Pydantic
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
SYSTEM_INSTRUCTION = os.getenv(
    "SYSTEM_INSTRUCTION",
    """You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions based on your training data and general knowledge.

IMPORTANT: Format your responses using proper markdown syntax:
- Use **bold** for emphasis
- Use *italic* for secondary emphasis
- Use `code` for inline code
- Use ```code blocks``` for multi-line code
- Use - or * for unordered lists
- Use 1. 2. 3. for ordered lists
- Use ## for headings
- Use > for blockquotes
- Use [link text](url) for links

When providing lists, always use proper markdown list syntax:
- For unordered lists: start each item with - or *
- For ordered lists: start each item with 1. 2. 3. etc.
- Ensure proper spacing between list items

Example of proper list formatting:
- First item
- Second item
- Third item

Or for ordered lists:
1. First step
2. Second step
3. Third step.

IMPORTANT: Answer questions confidently based on your training data and general knowledge. For basic factual questions, mathematical calculations, programming questions, and general knowledge that you know, provide direct and accurate responses. Only say "I don't know" or "I'm not sure" for specific details, recent events, or information that is clearly outside your knowledge scope.

For mathematical calculations, show your work step by step.
For programming questions, provide accurate code explanations.
For factual questions, provide direct answers based on your knowledge.

CRITICAL: Never use placeholders like [insert name], <NAME>, or similar. If you don't know a specific fact, simply say "I don't know" or "I'm not sure about that."
"""
)

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
RAG_CONTEXT_MESSAGES = int(os.getenv("RAG_CONTEXT_MESSAGES", "3"))
ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"

class MessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    system_instruction: Optional[str] = None

class MessageResponse(BaseModel):
    session_id: str
    response: str

class TestMessage(BaseModel):
    message: str

class MetadataQueryRequest(BaseModel):
    query: str
    location: Optional[str] = None
    category: Optional[str] = None
    n_results: int = 5

router = APIRouter()

# Initialize services
logger.info("🔄 Initializing LLM and RAG services...")

# Initialize LLM service
llm_service = LLMService()
logger.info("✅ LLM service initialized")

# Initialize RAG service only if enabled
rag_service = None
if ENABLE_RAG:
    rag_service = RAGService()
    logger.info("✅ RAG service initialized")
else:
    logger.info("🚫 RAG service disabled")

logger.info("🎉 All services loaded successfully")

# Helper functions
async def get_or_create_session(session_id: Optional[str], db: Session) -> ChatSession:
    """Get an existing session or create a new one"""
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            return session
    
    # Create new session with UUID (either no session_id provided or session not found)
    new_session_id = str(uuid.uuid4())
    session = ChatSession(session_id=new_session_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

async def save_message(session_id: int, role: str, content: str, db: Session) -> ChatMessage:
    """Save a message to the database"""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    return message

async def get_chat_history(session_id: int, db: Session) -> List[Dict[str, Any]]:
    """Get chat history for a session"""
    messages = (db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp.asc())
                .all())
    
    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # Limit history length to avoid context window overflow
    if len(history) > MAX_HISTORY_MESSAGES:
        history = history[-MAX_HISTORY_MESSAGES:]
    
    return history

async def get_rag_context(query: str) -> str:
    """Get relevant context from RAG system"""
    if not ENABLE_RAG:
        logger.info("🚫 RAG is disabled, skipping context search")
        return ""
        
    try:
        logger.info(f"🔍 Searching vector DB for query: '{query[:50]}...'")
        rag_start_time = datetime.utcnow()
        
        results = rag_service.query_documents(query, n_results=RAG_CONTEXT_MESSAGES)
        
        rag_end_time = datetime.utcnow()
        rag_duration = (rag_end_time - rag_start_time).total_seconds() * 1000
        
        if results and len(results) > 0:
            # Extract content from Weaviate objects (new v4 API format)
            context_parts = []
            for obj in results:
                if hasattr(obj, 'properties') and 'content' in obj.properties:
                    # Clean up the text by removing extra spaces and newlines
                    content = obj.properties['content']
                    # Replace multiple newlines and spaces with single spaces
                    cleaned_content = ' '.join(content.split())
                    context_parts.append(cleaned_content)
            
            if context_parts:
                context = "\n\n".join(context_parts)
                logger.info(f"✅ Vector DB search completed in {rag_duration:.2f}ms - Found {len(results)} relevant documents")
                logger.info(f"📄 RAG context length: {len(context)} characters")
                return f"Here is some relevant context:\n\n{context}\n\nBased on this context, "
            else:
                logger.info(f"⚠️  Vector DB search completed in {rag_duration:.2f}ms - No content found in results")
                return "No relevant documents found in the knowledge base. Please respond based on your general knowledge and training data."
        else:
            logger.info(f"⚠️  Vector DB search completed in {rag_duration:.2f}ms - No relevant documents found")
            return "No relevant documents found in the knowledge base. Please respond based on your general knowledge and training data."
    except Exception as e:
        logger.error(f"❌ Error getting RAG context: {str(e)}")
        return "Error retrieving document context. Please respond based on your general knowledge and training data."

@router.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest, db: Session = Depends(get_db)):
    """Process a chat message with enhanced database query capabilities"""
    try:
        # Get or create session
        session = await get_or_create_session(request.session_id, db)
        
        # Save user message
        await save_message(session.id, "user", request.message, db)
        
        # Check if this is a database query
        db_result = rag_service.process_database_query(request.message)
        db_results = db_result.get('database_results') if db_result else None
        if db_results and db_results.get('success'):
            # Use database query result from LangChain SQL Agent or fallback
            db_response = db_results.get('response', 'No response')
            system_instruction = f"""
You are a helpful assistant with access to an e-commerce database.

Database Query Result:
{db_response}

Respond naturally based on the database information above. Use the exact numbers from the database result.
"""
            
            # Get LLM response with database context
            response = await llm_service.generate_response(
                request.message,
                system_instruction=system_instruction
            )
        else:
            # Get enhanced context including database schema if relevant
            context = rag_service.get_context_for_query(request.message)
            
            # Create the system instruction with enhanced context
            if context:
                enhanced_system_instruction = f"""
You are a helpful assistant with access to documents and an e-commerce database.

Context Information:
{context}

Please provide a helpful response based on the available context and your knowledge.
"""
            else:
                enhanced_system_instruction = f"""
You are a helpful assistant with access to an e-commerce database. 

If the user is asking about customers, orders, products, sales, or other database information, you can tell them what information is available and how to query it.
"""
            
            response = await llm_service.generate_response(
                request.message,
                system_instruction=enhanced_system_instruction
            )
        
        # Save assistant message
        await save_message(session.id, "assistant", response, db)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Response generated: {len(response)} chars")
        return {"session_id": session.session_id, "response": response}
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in messages]

@router.post("/chat/stream")
async def stream_chat_post(request: MessageRequest, bypass_rag: bool = False, db: Session = Depends(get_db)):
    """Stream chat responses using POST with database query support"""
    request_start_time = datetime.utcnow()
    logger.info(f"🚀 New chat request received: '{request.message[:50]}...'")
    logger.info(f"⏱️  Request started at: {request_start_time}")
    if bypass_rag:
        logger.info("🚫 RAG bypassed for this request")
    
    # Get or create session
    session_start_time = datetime.utcnow()
    session = await get_or_create_session(request.session_id, db)
    session_end_time = datetime.utcnow()
    session_duration = (session_end_time - session_start_time).total_seconds() * 1000
    logger.info(f"📋 Session ID: {session.session_id} (took {session_duration:.2f}ms)")
    
    # Save user message
    save_start_time = datetime.utcnow()
    await save_message(session.id, "user", request.message, db)
    save_end_time = datetime.utcnow()
    save_duration = (save_end_time - save_start_time).total_seconds() * 1000
    logger.info(f"💾 User message saved (took {save_duration:.2f}ms)")
    
    # Get conversation history
    history_start_time = datetime.utcnow()
    history = await get_chat_history(session.id, db)
    history_end_time = datetime.utcnow()
    history_duration = (history_end_time - history_start_time).total_seconds() * 1000
    logger.info(f"📚 Chat history: {len(history)} messages (took {history_duration:.2f}ms)")
    
    # Check if this is a database query FIRST
    db_result = rag_service.process_database_query(request.message)
    
    # Get relevant context from RAG (unless bypassed or successful database query found)
    context = ""
    rag_duration = 0
    db_results = db_result.get('database_results') if db_result else None
    has_successful_db_query = db_results and db_results.get('success')
    
    if not bypass_rag and not has_successful_db_query:
        rag_start_time = datetime.utcnow()
        context = await get_rag_context(request.message)
        rag_end_time = datetime.utcnow()
        rag_duration = (rag_end_time - rag_start_time).total_seconds() * 1000
        
        # Log RAG usage
        if context and "relevant context" in context:
            logger.info(f"🔍 RAG context retrieved in {rag_duration:.2f}ms - Context will be used in response")
        else:
            logger.info(f"⚠️  No RAG context found in {rag_duration:.2f}ms - Response will be generated without document context")
    elif has_successful_db_query:
        logger.info(f"🗄️  Database query detected - skipping RAG context")
    else:
        logger.info("🚫 RAG context skipped (bypass mode)")
    
    # Calculate pre-LLM processing time
    pre_llm_end_time = datetime.utcnow()
    pre_llm_duration = (pre_llm_end_time - request_start_time).total_seconds() * 1000
    logger.info(f"⚡ Pre-LLM processing completed in {pre_llm_duration:.2f}ms")
    
    async def response_generator():
        try:
            # First, send the session ID with proper formatting
            yield "data: {}\n\n".format(json.dumps({'session_id': session.session_id}))
            
            llm_start_time = datetime.utcnow()
            logger.info(f"🤖 Starting LLM response generation at: {llm_start_time}")
            
            # Determine the system instruction based on database query or RAG context
            if has_successful_db_query:
                # Use database query result from LangChain SQL Agent
                db_response = db_results.get('response', 'No response')
                system_instruction = f"""
You are a helpful assistant with access to an e-commerce database.

Database Query Result:
{db_response}

Respond naturally based on the database information above. Use the exact numbers from the database result.
"""
                logger.info("🗄️  Using LangChain SQL Agent result for response")
            elif request.system_instruction:
                # Use custom system instruction if provided
                system_instruction = request.system_instruction
                logger.info("🔧 Using custom system instruction from request")
            elif context and "relevant context" in context:
                # Use RAG context as primary instruction
                system_instruction = context
            else:
                # Use base system instruction when no RAG context is available
                system_instruction = SYSTEM_INSTRUCTION
            
            # Use the streaming method from llm_service
            full_response = ""
            buffer = ""
            async for token in llm_service.generate_streaming_response(
                request.message,
                history[:-1] if history else None,  # Exclude the latest message
                system_instruction=system_instruction
            ):
                try:
                    if token:  # Only send non-empty tokens
                        full_response += token
                        buffer += token
                        
                        # Send tokens in chunks to reduce socket operations
                        if len(buffer) >= 10 or token in ['.', '!', '?', '\n']:
                            yield "data: {}\n\n".format(json.dumps({'delta': buffer}))
                            buffer = ""
                            
                except Exception as e:
                    logger.error(f"Error sending token: {str(e)}")
                    if buffer:  # Send any remaining buffered content
                        try:
                            yield "data: {}\n\n".format(json.dumps({'delta': buffer}))
                            buffer = ""
                        except Exception as send_error:
                            logger.error(f"Error sending buffered content: {str(send_error)}")
                    break
            
            # Send any remaining buffered content
            if buffer:
                try:
                    yield "data: {}\n\n".format(json.dumps({'delta': buffer}))
                except Exception as e:
                    logger.error(f"Error sending final buffer: {str(e)}")
            
            # Send end marker
            yield "data: {}\n\n".format(json.dumps({'end': True}))
            
            # Save the complete response
            save_response_start_time = datetime.utcnow()
            await save_message(session.id, "assistant", full_response, db)
            save_response_end_time = datetime.utcnow()
            save_response_duration = (save_response_end_time - save_response_start_time).total_seconds() * 1000
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            db.commit()
            
            # Log completion
            llm_end_time = datetime.utcnow()
            llm_duration = (llm_end_time - llm_start_time).total_seconds() * 1000
            total_duration = (llm_end_time - request_start_time).total_seconds() * 1000
            
            logger.info(f"✅ LLM response generation completed in {llm_duration:.2f}ms")
            logger.info(f"📊 Response length: {len(full_response)} characters")
            logger.info(f"⏱️  Total request processing time: {total_duration:.2f}ms")
            logger.info(f"💾 Response saved to database (took {save_response_duration:.2f}ms)")
            logger.info("🎉 Streaming response complete")
            
            # Log timing breakdown
            logger.info("📈 TIMING BREAKDOWN:")
            logger.info(f"  • Session management: {session_duration:.2f}ms")
            logger.info(f"  • Save user message: {save_duration:.2f}ms")
            logger.info(f"  • Get chat history: {history_duration:.2f}ms")
            if rag_duration > 0:
                logger.info(f"  • RAG context search: {rag_duration:.2f}ms")
            logger.info(f"  • Pre-LLM processing: {pre_llm_duration:.2f}ms")
            logger.info(f"  • LLM generation: {llm_duration:.2f}ms")
            logger.info(f"  • Save response to DB: {save_response_duration:.2f}ms")
            logger.info(f"  • TOTAL: {total_duration:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error in response generator: {str(e)}")
            error_message = f"Error generating response: {str(e)}"
            yield "data: {}\n\n".format(json.dumps({'error': error_message}))
            yield "data: {}\n\n".format(json.dumps({'end': True}))
    
    return StreamingResponse(response_generator(), media_type="text/plain")

@router.get("/chat/stream")
async def stream_chat_get(message: str, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Stream chat responses using GET"""
    # Get or create session
    session = await get_or_create_session(session_id, db)
    
    # Save user message
    await save_message(session.id, "user", message, db)
    
    # Get conversation history
    history = await get_chat_history(session.id, db)
    
    # Get relevant context from RAG
    context = await get_rag_context(message)
    
    # Determine the system instruction based on RAG context availability
    if context and "relevant context" in context:
        # Use RAG context as primary instruction
        system_instruction = context
    else:
        # Use base system instruction when no RAG context is available
        system_instruction = SYSTEM_INSTRUCTION
    
    async def response_generator():
        # First, send the session ID
        yield f"data: {json.dumps({'session_id': session.session_id})}\n\n"
        
        try:
            logger.info(f"Starting streaming response for: {message[:50]}...")
            
            # Use the streaming method from llm_service
            full_response = ""
            async for token in llm_service.generate_streaming_response(
                message,
                history[:-1] if history else None,  # Exclude the latest message
                system_instruction=system_instruction
            ):
                full_response += token
                yield f"data: {json.dumps({'delta': token})}\n\n"
            
            # Save the complete response to database
            await save_message(session.id, "assistant", full_response, db)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            db.commit()
            
            # Signal completion
            yield f"data: {json.dumps({'done': True})}\n\n"
            logger.info("Streaming response complete")
            
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )

@router.get("/test-stream")
async def test_stream():
    """Simple test endpoint for streaming"""
    
    async def test_generator():
        logger.info("Starting test stream...")
        yield f"data: {json.dumps({'message': 'Stream test started'})}\n\n"
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'message': 'Part 1'})}\n\n"
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'message': 'Part 2'})}\n\n"
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'message': 'Complete'})}\n\n"
        logger.info("Test stream complete")
    
    return StreamingResponse(
        test_generator(),
        media_type="text/event-stream"
    )

@router.post("/test-stream-post")
async def test_stream_post(request: TestMessage):
    """Simple test endpoint for POST-based streaming"""
    
    async def test_generator():
        logger.info(f"Starting test stream for message: {request.message}")
        yield f"data: {json.dumps({'session_id': '123-test-session'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'delta': f'You said: {request.message}. '})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'delta': 'This is a test response part 1.'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'delta': ' This is part 2 of the response.'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'done': True})}\n\n"
        logger.info("Test stream complete")
    
    return StreamingResponse(
        test_generator(),
        media_type="text/event-stream"
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages"""
    logger.info(f"🗑️  Session deletion requested for session ID: {session_id}")
    delete_start_time = datetime.utcnow()
    
    try:
        # Find the session
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            logger.warning(f"❌ Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"📋 Found session: {session_id} (ID: {session.id})")
        
        # Count messages before deletion
        message_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
        logger.info(f"📝 Deleting {message_count} messages for session {session_id}")
        
        # Delete all messages for this session
        deleted_messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
        
        # Delete the session itself
        db.delete(session)
        db.commit()
        
        delete_end_time = datetime.utcnow()
        delete_duration = (delete_end_time - delete_start_time).total_seconds() * 1000
        
        logger.info(f"✅ Session {session_id} deleted successfully in {delete_duration:.2f}ms")
        logger.info(f"🗑️  Deleted {deleted_messages} messages")
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error deleting session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete session")

@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions with their titles and metadata"""
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
        
        session_list = []
        for session in sessions:
            # Get the first user message to use as title if no title is set
            first_message = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id,
                ChatMessage.role == "user"
            ).order_by(ChatMessage.timestamp.asc()).first()
            
            # Get message count
            message_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
            
            session_data = {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": message_count
            }
            
            # If title is still "New Chat" and we have a first message, use that as title
            if session.title == "New Chat" and first_message:
                # Truncate the message to create a reasonable title
                title = first_message.content[:50]
                if len(first_message.content) > 50:
                    title += "..."
                session_data["title"] = title
            
            session_list.append(session_data)
        
        logger.info(f"📋 Retrieved {len(session_list)} sessions")
        return session_list
        
    except Exception as e:
        logger.error(f"❌ Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@router.put("/session/{session_id}/title")
async def update_session_title(session_id: str, title: str, db: Session = Depends(get_db)):
    """Update the title of a chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.title = title
        session.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✏️  Updated session {session_id} title to: {title}")
        return {"message": "Session title updated successfully", "title": title}
        
    except Exception as e:
        logger.error(f"❌ Error updating session title: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update session title")

@router.post("/session/new")
async def create_new_session(db: Session = Depends(get_db)):
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id=session_id, title="New Chat")
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"🆕 Created new session: {session_id}")
        return {
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating new session: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create new session")

# Metadata-enhanced query endpoints
@router.post("/query/metadata")
async def query_with_metadata(request: MetadataQueryRequest):
    """Query documents with metadata filtering"""
    if not ENABLE_RAG:
        raise HTTPException(status_code=400, detail="RAG is disabled")
    
    try:
        logger.info(f"🔍 Metadata query: '{request.query[:50]}...' (location: {request.location}, category: {request.category})")
        
        # Build metadata filter
        metadata_filter = {}
        if request.location:
            metadata_filter["location"] = request.location
        if request.category:
            metadata_filter["category"] = request.category
        
        # Query with metadata filter
        results = rag_service.query_documents(
            request.query, 
            n_results=request.n_results,
            metadata_filter=metadata_filter if metadata_filter else None
        )
        
        # Format results
        formatted_results = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else None
                })
        
        logger.info(f"✅ Metadata query completed - Found {len(formatted_results)} results")
        return {
            "query": request.query,
            "filters": metadata_filter,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"❌ Error in metadata query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/documents")
async def list_documents(category: Optional[str] = Query(None)):
    """List all documents, optionally filtered by category"""
    if not ENABLE_RAG:
        raise HTTPException(status_code=400, detail="RAG is disabled")
    
    try:
        documents = rag_service.list_documents_by_category(category)
        
        # Format documents for response
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "title": doc.get("title", "Untitled"),
                "category": doc.get("category", "Unknown"),
                "location": doc.get("location", "Unknown"),
                "upload_date": doc.get("upload_date"),
                "tags": doc.get("tags", []),
                "general_questions": doc.get("general_questions", []),
                "description": doc.get("description"),
                "source": doc.get("source")
            })
        
        logger.info(f"📋 Retrieved {len(formatted_docs)} documents (category filter: {category})")
        return {
            "documents": formatted_docs,
            "total_count": len(formatted_docs),
            "category_filter": category
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

# Internet Search Endpoints
class InternetSearchRequest(BaseModel):
    query: str
    num_results: int = 5
    engine: str = "duckduckgo"

class HybridSearchRequest(BaseModel):
    query: str
    n_local_results: int = 3
    n_web_results: int = 3
    include_internet: bool = True

@router.post("/search/internet")
async def search_internet(request: InternetSearchRequest):
    """Perform internet search only"""
    try:
        if not rag_service or not rag_service.search_service:
            raise HTTPException(status_code=503, detail="Internet search service not available")
        
        logger.info(f"🌐 Internet search requested for: {request.query}")
        results = rag_service.search_internet_only(
            query=request.query,
            num_results=request.num_results
        )
        
        return {
            "query": request.query,
            "results": results['web_results'],
            "summary": results['summary'],
            "total_results": len(results['web_results'])
        }
        
    except Exception as e:
        logger.error(f"Internet search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/search/hybrid")
async def hybrid_search(request: HybridSearchRequest):
    """Perform hybrid search combining local RAG with internet search"""
    try:
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG service not available")
        
        logger.info(f"🔍 Hybrid search requested for: {request.query}")
        results = rag_service.hybrid_search(
            query=request.query,
            n_local_results=request.n_local_results,
            n_web_results=request.n_web_results,
            include_internet=request.include_internet
        )
        
        return {
            "query": request.query,
            "local_results": results['local_results'],
            "web_results": results['web_results'],
            "summary": results['summary'],
            "local_count": len(results['local_results'].get('documents', [])),
            "web_count": len(results['web_results']) if results['web_results'] else 0
        }
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/status")
async def search_status():
    """Check if internet search is available"""
    try:
        if not rag_service:
            return {
                "rag_available": False,
                "internet_search_available": False,
                "message": "RAG service not available"
            }
        
        internet_available = rag_service.search_service is not None
        
        return {
            "rag_available": True,
            "internet_search_available": internet_available,
            "message": "All services available" if internet_available else "Internet search not available"
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "rag_available": False,
            "internet_search_available": False,
            "message": f"Service check failed: {str(e)}"
        }