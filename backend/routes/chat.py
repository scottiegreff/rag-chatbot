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
import time

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
    """You are an AI RAG Chatbot assistant. Your main goal is to assist users with questions and provide helpful information based on the knowledge base. Here are your key guidelines:

# Response Style - CRITICALLY IMPORTANT
- No phrases like "based on my knowledge" or "according to information"
- No explanatory text before giving the answer
- No summaries or repetition
- Hyperlink all URLs
- Respond in user's language
- Use markdown formatting: **bold**, *italic*, `code`, ```blocks```, lists (- or 1.), ## headings, > quotes.

# Knowledge Base Requirements - PREVENT HALLUCINATIONS
- If required information is NOT in the knowledge database: "I don't have enough information in my knowledge base to answer that question accurately."
- NEVER invent or hallucinate URLs, links, product specs, procedures, dates, statistics, names, contacts, or company information
- When knowledge base information is unclear or contradictory, acknowledge the limitation rather than guessing
- Better to admit insufficient information than provide inaccurate answers
- PRIORITIZE the provided context from the knowledge base over any general knowledge"""
)

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
RAG_CONTEXT_MESSAGES = int(os.getenv("RAG_CONTEXT_MESSAGES", "5"))
ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"

class MessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    system_instruction: Optional[str] = None

class MessageResponse(BaseModel):
    session_id: str
    response: str

class HybridSearchRequest(BaseModel):
    query: str
    n_local_results: int = 3
    n_web_results: int = 3
    include_internet: bool = True

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
        
        # Handle Weaviate v4 GenerativeReturn object
        if hasattr(results, 'objects') and results.objects:
            # Extract content from Weaviate objects (new v4 API format)
            context_parts = []
            for i, obj in enumerate(results.objects):
                if hasattr(obj, 'properties') and 'content' in obj.properties:
                    # Clean up the text while preserving important formatting
                    content = obj.properties['content']
                    # Handle excessive newlines and spaces that are common in PDF extractions
                    # First, replace multiple newlines with single newlines
                    content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
                    # Then replace multiple spaces with single space
                    cleaned_content = ' '.join(content.split())
                    # Add document source information
                    source = obj.properties.get('source', 'Unknown source')
                    category = obj.properties.get('category', 'General')
                    context_parts.append(f"[Document {i+1} - {source} - {category}]: {cleaned_content}")
            
            if context_parts:
                context = "\n\n".join(context_parts)
                logger.info(f"✅ Vector DB search completed in {rag_duration:.2f}ms - Found {len(results.objects)} relevant documents")
                logger.info(f"📄 RAG context length: {len(context)} characters")
                return f"""Here is relevant context from the knowledge base:

{context}

Please use this context to provide accurate and detailed information. If the context contains specific details, facts, or information that answers the user's question, make sure to include those details in your response. If the context doesn't fully answer the question, you may supplement with your general knowledge, but prioritize the provided context."""
            else:
                logger.info(f"⚠️  Vector DB search completed in {rag_duration:.2f}ms - No content found in results")
                return "No relevant documents found in the knowledge base. Please respond based on your general knowledge and training data."
        elif isinstance(results, list) and len(results) > 0:
            # Handle legacy list format
            context_parts = []
            for i, obj in enumerate(results):
                if hasattr(obj, 'properties') and 'content' in obj.properties:
                    content = obj.properties['content']
                    content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
                    cleaned_content = ' '.join(content.split())
                    source = obj.properties.get('source', 'Unknown source')
                    category = obj.properties.get('category', 'General')
                    context_parts.append(f"[Document {i+1} - {source} - {category}]: {cleaned_content}")
            
            if context_parts:
                context = "\n\n".join(context_parts)
                logger.info(f"✅ Vector DB search completed in {rag_duration:.2f}ms - Found {len(results)} relevant documents")
                logger.info(f"📄 RAG context length: {len(context)} characters")
                return f"""Here is relevant context from the knowledge base:

{context}

Please use this context to provide accurate and detailed information. If the context contains specific details, facts, or information that answers the user's question, make sure to include those details in your response. If the context doesn't fully answer the question, you may supplement with your general knowledge, but prioritize the provided context."""
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
            context = await get_rag_context(request.message)
            
            # Create the system instruction with enhanced context
            if context and "relevant context" in context:
                # Combine RAG context with the optimized system instruction
                system_instruction = f"{SYSTEM_INSTRUCTION}\n\n{context}"
                logger.info("🔍 Using RAG context combined with optimized system instruction")
            else:
                # Use base system instruction when no RAG context is available
                system_instruction = SYSTEM_INSTRUCTION
            
            response = await llm_service.generate_response(
                request.message,
                system_instruction=system_instruction
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
    request_start_time = time.time()
    logger.info(f"🚀 [TIMING] Request started at: {request_start_time}")
    logger.info(f"🚀 [TIMING] New chat request received: '{request.message[:50]}...'")
    if bypass_rag:
        logger.info("🚫 RAG bypassed for this request")
    
    # Get or create session
    session_start_time = time.time()
    session = await get_or_create_session(request.session_id, db)
    session_end_time = time.time()
    session_duration = (session_end_time - session_start_time) * 1000
    logger.info(f"📋 [TIMING] Session creation completed in {session_duration:.2f}ms")
    logger.info(f"📋 Session ID: {session.session_id}")
    
    # Save user message
    save_start_time = time.time()
    await save_message(session.id, "user", request.message, db)
    save_end_time = time.time()
    save_duration = (save_end_time - save_start_time) * 1000
    logger.info(f"💾 [TIMING] User message saved in {save_duration:.2f}ms")
    
    # Get conversation history
    history_start_time = time.time()
    history = await get_chat_history(session.id, db)
    history_end_time = time.time()
    history_duration = (history_end_time - history_start_time) * 1000
    logger.info(f"📚 [TIMING] Chat history retrieved in {history_duration:.2f}ms")
    logger.info(f"📚 Chat history: {len(history)} messages")
    
    # Check if this is a database query FIRST
    db_query_start_time = time.time()
    db_result = rag_service.process_database_query(request.message)
    db_query_end_time = time.time()
    db_query_duration = (db_query_end_time - db_query_start_time) * 1000
    logger.info(f"🗄️ [TIMING] Database query processing completed in {db_query_duration:.2f}ms")
    
    # Get relevant context from RAG (unless bypassed or successful database query found)
    context = ""
    rag_duration = 0
    db_results = db_result.get('database_results') if db_result else None
    has_successful_db_query = db_results and db_results.get('success')
    
    if not bypass_rag and not has_successful_db_query:
        rag_start_time = time.time()
        context = await get_rag_context(request.message)
        rag_end_time = time.time()
        rag_duration = (rag_end_time - rag_start_time) * 1000
        
        # Log RAG usage
        if context and "relevant context" in context:
            logger.info(f"🔍 [TIMING] RAG context retrieved in {rag_duration:.2f}ms - Context will be used in response")
        else:
            logger.info(f"⚠️ [TIMING] No RAG context found in {rag_duration:.2f}ms - Response will be generated without document context")
    elif has_successful_db_query:
        logger.info(f"🗄️ Database query detected - skipping RAG context")
    else:
        logger.info("🚫 RAG context skipped (bypass mode)")
    
    # Calculate pre-LLM processing time
    pre_llm_end_time = time.time()
    pre_llm_duration = (pre_llm_end_time - request_start_time) * 1000
    logger.info(f"⚡ [TIMING] Pre-LLM processing completed in {pre_llm_duration:.2f}ms")
    
    async def response_generator():
        try:
            # First, send the session ID with proper formatting
            yield "data: {}\n\n".format(json.dumps({'session_id': session.session_id}))
            
            llm_start_time = time.time()
            logger.info(f"🤖 [TIMING] Starting LLM response generation at: {llm_start_time}")
            
            # Determine the system instruction based on database query or RAG context
            instruction_start_time = time.time()
            if has_successful_db_query:
                # Use database query result from LangChain SQL Agent
                db_response = db_results.get('response', 'No response')
                system_instruction = f"""
You are a helpful assistant with access to an e-commerce database.

Database Query Result:
{db_response}

Respond naturally based on the database information above. Use the exact numbers from the database result.
"""
                logger.info("🗄️ Using LangChain SQL Agent result for response")
            elif request.system_instruction:
                # Use custom system instruction if provided
                system_instruction = request.system_instruction
                logger.info("🔧 Using custom system instruction from request")
            elif context and "relevant context" in context:
                # Combine RAG context with the optimized system instruction
                system_instruction = f"{SYSTEM_INSTRUCTION}\n\n{context}"
            else:
                # Use base system instruction when no RAG context is available
                system_instruction = SYSTEM_INSTRUCTION
            
            instruction_end_time = time.time()
            instruction_duration = (instruction_end_time - instruction_start_time) * 1000
            logger.info(f"📝 [TIMING] System instruction preparation completed in {instruction_duration:.2f}ms")
            
            # Use the streaming method from llm_service
            full_response = ""
            buffer = ""
            first_token_time = None
            token_count = 0
            
            async for token in llm_service.generate_streaming_response(
                request.message,
                history[:-1] if history else None,  # Exclude the latest message
                system_instruction=system_instruction
            ):
                try:
                    if token:  # Only send non-empty tokens
                        if first_token_time is None:
                            first_token_time = time.time()
                            first_token_duration = (first_token_time - llm_start_time) * 1000
                            logger.info(f"🎯 [TIMING] First token received in {first_token_duration:.2f}ms")
                        
                        token_count += 1
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
            
            # Save the complete response to database
            await save_message(session.id, "assistant", full_response, db)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            db.commit()
            
            # Calculate final timing
            llm_end_time = time.time()
            llm_duration = (llm_end_time - llm_start_time) * 1000
            total_duration = (llm_end_time - request_start_time) * 1000
            
            logger.info(f"🎯 [TIMING] LLM response generation completed in {llm_duration:.2f}ms")
            logger.info(f"⏱️ [TIMING] Total request time: {total_duration:.2f}ms")
            logger.info(f"📊 [TIMING] Generated {token_count} tokens, {len(full_response)} characters")
            
            # Signal completion
            yield "data: {}\n\n".format(json.dumps({'done': True}))
            logger.info("✅ Streaming response complete")
            
        except Exception as e:
            logger.error(f"Error in response generator: {str(e)}")
            error_message = f"Error generating response: {str(e)}"
            yield "data: {}\n\n".format(json.dumps({'error': error_message}))
            yield "data: {}\n\n".format(json.dumps({'end': True}))
    
    return StreamingResponse(response_generator(), media_type="text/plain")

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
        new_session_id = str(uuid.uuid4())
        session = ChatSession(session_id=new_session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"✅ Created new session: {new_session_id}")
        return {"session_id": new_session_id, "message": "New session created successfully"}
    except Exception as e:
        logger.error(f"❌ Error creating new session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating new session: {str(e)}")

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
        local_results = results['local_results']
        # Handle Weaviate v4 GenerativeReturn object
        if hasattr(local_results, 'objects') and local_results.objects:
            local_count = len(local_results.objects)
        elif isinstance(local_results, dict) and 'documents' in local_results:
            local_count = len(local_results.get('documents', []))
        elif isinstance(local_results, list):
            local_count = len(local_results)
        else:
            local_count = 0
        return {
            "query": request.query,
            "local_results": local_results,
            "web_results": results['web_results'],
            "summary": results['summary'],
            "local_count": local_count,
            "web_count": len(results['web_results']) if results['web_results'] else 0
        }
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")