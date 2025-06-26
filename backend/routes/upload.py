import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from backend.services.rag_service import RAGService
from backend.models.document import DocumentMetadata
import uuid
from typing import List
import json

router = APIRouter()

UPLOAD_DIR = Path("/tmp/fci_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.csv', '.xlsx', '.jpg', '.jpeg'}

# Predefined categories and locations for dropdowns
CATEGORIES = [
    "Human Resources",
    "Finance & Accounting", 
    "Information Technology",
    "Legal & Compliance",
    "Operations & Management"
]

LOCATIONS = [
    "All Locations",
    "Headquarters",
    "Branch Office - North",
    "Branch Office - South", 
    "Remote/Home Office"
]

@router.get("/categories")
async def get_categories():
    """Get available categories for document upload."""
    return {"categories": CATEGORIES}

@router.get("/locations") 
async def get_locations():
    """Get available locations for document upload."""
    return {"locations": LOCATIONS}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    general_questions: str = Form(None),  # JSON string of questions, now optional
    tags: str = Form(None),  # JSON string of tags, now optional
    description: str = Form(None),
    uploaded_by: str = Form("anonymous")
):
    """
    Upload a file with enhanced metadata for better retrieval.
    
    Args:
        file: The file to upload
        title: Document title
        category: Business category (HR, Finance, Legal, etc.)
        location: Where the document is relevant
        general_questions: JSON string of common questions this document answers
        tags: JSON string of tags/keywords
        description: Optional description
        uploaded_by: User who uploaded the document
    """
    # Debug: Print all incoming form fields
    print("[UPLOAD DEBUG] Incoming form fields:")
    print(f"  file: {file.filename}")
    print(f"  title: {title}")
    print(f"  category: {category}")
    print(f"  location: {location}")
    print(f"  general_questions: {general_questions}")
    print(f"  tags: {tags}")
    print(f"  description: {description}")
    print(f"  uploaded_by: {uploaded_by}")

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    
    # Parse JSON fields, handle empty or missing values gracefully
    try:
        if general_questions is None or general_questions.strip() == '':
            questions_list = []
        else:
            questions_list = json.loads(general_questions)
        if tags is None or tags.strip() == '':
            tags_list = []
        else:
            tags_list = json.loads(tags)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in metadata: {e}")
    
    # Create metadata object
    metadata = DocumentMetadata(
        source=file.filename,
        uploaded_by=uploaded_by,
        doc_type=ext.upper().lstrip('.'),
        title=title,
        tags=tags_list,
        category=category,
        location=location,
        general_questions=questions_list,
        description=description
    )
    
    # Save file to temp directory
    temp_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Ingest file using RAGService with metadata
    rag_service = RAGService()
    try:
        from backend.utils.ingest_documents import ingest_document
        doc_id = ingest_document(str(temp_path), metadata.model_dump())
        return {
            "status": "success", 
            "filename": file.filename, 
            "doc_id": doc_id,
            "metadata": metadata.model_dump()
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)}) 