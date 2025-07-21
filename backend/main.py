import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
from fastapi.responses import FileResponse

# Load environment variables
load_dotenv()

from backend.routes import chat
from backend.routes import upload
from backend.routes import ecommerce
from backend.routes import database
from backend.routes import url_validation
from backend.database import init_db

# Get server configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Initialize FastAPI app
app = FastAPI(title="AI Chatbot", description="AI local chatbot with LLM integration")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(ecommerce.router, prefix="/api/ecommerce", tags=["ecommerce"])
app.include_router(database.router, prefix="/api/database", tags=["database"])
app.include_router(url_validation.router, tags=["url-validation"])

# Mount static files for frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")

# Mount frontend HTML files at root (serve index.html as default)
@app.get("/")
async def read_index():
    return FileResponse(frontend_dir / "index.html")

# Handle specific frontend files
@app.get("/css/{path:path}")
async def read_css(path: str):
    file_path = frontend_dir / "css" / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/js/{path:path}")
async def read_js(path: str):
    file_path = frontend_dir / "js" / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/favicon.ico")
async def read_favicon():
    file_path = frontend_dir / "favicon.ico"
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/test")
def test_endpoint():
    return {"message": "API is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=DEBUG) 