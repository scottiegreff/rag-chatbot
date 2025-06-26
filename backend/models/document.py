from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Metadata model for documents stored in the vector database."""
    
    # Core metadata
    source: str = Field(..., description="Source of the document (filename, URL, etc.)")
    uploaded_by: str = Field(..., description="User who uploaded the document")
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of upload")
    doc_type: str = Field(..., description="Type of document (PDF, DOCX, TXT, etc.)")
    title: str = Field(..., description="Title of the document")
    tags: List[str] = Field(default=[], description="List of tags/keywords")
    category: str = Field(..., description="Business/domain category (HR, Finance, Legal, etc.)")
    
    # Enhanced metadata
    location: str = Field(..., description="Where the document is relevant (Building A, Floor 3, Remote, etc.)")
    general_questions: List[str] = Field(..., description="Common questions this document helps answer")
    
    # Optional fields
    description: Optional[str] = Field(None, description="Short description or summary")
    language: Optional[str] = Field("en", description="Language of the document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "employee_handbook.pdf",
                "uploaded_by": "admin@company.com",
                "upload_date": "2024-01-15T10:30:00Z",
                "doc_type": "PDF",
                "title": "Employee Handbook 2024",
                "tags": ["policies", "employee", "handbook"],
                "category": "HR",
                "location": "All Locations",
                "general_questions": [
                    "How do I request time off?",
                    "What's the dress code?",
                    "What are the working hours?",
                    "How do I report an incident?"
                ],
                "description": "Comprehensive employee handbook covering company policies and procedures",
                "language": "en"
            }
        } 