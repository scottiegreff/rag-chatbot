from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import json
import os
from datetime import datetime
import uuid

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
sessions = {}
chat_history = {}

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/sessions")
async def get_sessions():
    return list(sessions.values())

@app.post("/api/sessions")
async def create_session():
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "title": f"New Chat {datetime.now().strftime('%H:%M')}",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    sessions[session_id] = session
    chat_history[session_id] = []
    return session

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, title: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    sessions[session_id]["title"] = title
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    return sessions[session_id]

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions[session_id]
    if session_id in chat_history:
        del chat_history[session_id]
    return {"message": "Session deleted"}

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    if session_id not in chat_history:
        return []
    return chat_history[session_id]

@app.post("/api/chat")
async def chat(message: dict):
    session_id = message.get("session_id")
    user_message = message.get("message", "")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # Add user message
    user_msg = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    }
    chat_history[session_id].append(user_msg)
    
    # Generate mock AI response
    ai_response = generate_mock_response(user_message)
    
    ai_msg = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now().isoformat()
    }
    chat_history[session_id].append(ai_msg)
    
    # Update session timestamp
    if session_id in sessions:
        sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    return {
        "response": ai_response,
        "session_id": session_id,
        "message_id": ai_msg["id"]
    }

def generate_mock_response(user_message: str) -> str:
    """Generate a mock AI response based on user input"""
    message_lower = user_message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! I'm the FCI Chatbot. How can I help you today?"
    
    elif "help" in message_lower:
        return "I can help you with:\n- Answering questions about FCI policies\n- Searching through documents\n- Providing information about procedures\n- General inquiries\n\nWhat would you like to know?"
    
    elif "policy" in message_lower:
        return "I can help you find information about FCI policies. Could you be more specific about which policy you're looking for?"
    
    elif "document" in message_lower or "upload" in message_lower:
        return "You can upload documents using the upload button in the chat interface. I'll then be able to answer questions about those documents."
    
    elif "search" in message_lower:
        return "I can search through uploaded documents and provide relevant information. What are you looking for?"
    
    elif "?" in user_message:
        return "That's an interesting question! I'm currently running in demo mode, but I can help you with general information about FCI. For specific document searches, you'll need to upload relevant documents first."
    
    else:
        return "Thank you for your message. I'm the FCI Chatbot and I'm here to help you with questions about FCI policies, procedures, and documents. You can ask me questions or upload documents for me to analyze."

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    tags: str = Form(""),
    general_questions: str = Form(""),
    description: str = Form(""),
    uploaded_by: str = Form("")
):
    # Mock file upload response
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "title": title,
        "category": category,
        "location": location,
        "tags": tags.split(",") if tags else [],
        "uploaded_by": uploaded_by
    }

@app.get("/api/categories")
async def get_categories():
    return [
        "Policy",
        "Procedure", 
        "Handbook",
        "Form",
        "Guideline",
        "Training",
        "Other"
    ]

@app.get("/api/locations")
async def get_locations():
    return [
        "HR",
        "IT",
        "Finance",
        "Operations",
        "Marketing",
        "Sales",
        "Legal",
        "Other"
    ]

@app.post("/api/search")
async def search_web(query: dict):
    # Mock web search response
    return {
        "results": [
            {
                "title": f"Search result for: {query.get('query', '')}",
                "snippet": "This is a mock search result. In the full version, this would contain real search results from the web.",
                "url": "https://example.com"
            }
        ]
    }

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
    app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
except:
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 