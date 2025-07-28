"""
Document Ingestion Utility

This script processes and ingests documents into the Weaviate vector store.
Supports PDF and DOCX files with automatic text extraction and chunking.
"""

import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
import weaviate
from weaviate.connect import ConnectionParams

load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
client = weaviate.WeaviateClient(ConnectionParams.from_url(WEAVIATE_URL, grpc_port=50051))
client.connect()

# ---
def process_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    processed = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, datetime):
            processed[key] = value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"
        elif isinstance(value, list):
            processed[key] = ", ".join(str(item) for item in value if item is not None)
        else:
            processed[key] = str(value)
    return processed

def extract_text_from_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        try:
            import PyPDF2
        except ImportError:
            print("❌ PyPDF2 is not installed. Please install it to process PDF files.")
            sys.exit(1)
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    elif ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            print("❌ python-docx is not installed. Please install it to process DOCX files.")
            sys.exit(1)
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def ingest_document(file_path: str, metadata: Dict[str, Any] = None) -> str:
    """Ingest a single .txt, .pdf, or .docx document into the vector store."""
    document_id = str(uuid.uuid4())
    if metadata is None:
        metadata = {}
    file_info = {
        "filename": os.path.basename(file_path),
        "file_path": file_path,
        "ingestion_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}Z",
        "document_id": document_id
    }
    metadata.update(file_info)
    processed_metadata = process_metadata(metadata)
    
    # Use RAG service to properly ingest with embeddings
    from backend.services.rag_service import RAGService
    rag_service = RAGService()
    
    # Extract text from file
    text = extract_text_from_file(file_path)
    
    # Add document using RAG service (which handles chunking and embedding)
    rag_service.add_document(document_id, text, processed_metadata)
    
    print(f"✅ Successfully ingested: {file_path} as {len(text) // 500 + 1} chunks")
    return document_id

def ingest_directory(directory_path: str, metadata: Dict[str, Any] = None) -> List[str]:
    supported_extensions = {'.txt', '.pdf', '.docx'}
    ingested_files = []
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    files = [f for f in directory.rglob('*') if f.is_file() and f.suffix.lower() in supported_extensions]
    if not files:
        print(f"📭 No supported files found in {directory_path}")
        return []
    print(f"📁 Found {len(files)} files to ingest:")
    for file in files:
        print(f"   - {file}")
    for file_path in files:
        try:
            document_id = ingest_document(str(file_path), metadata)
            ingested_files.append(document_id)
        except Exception as e:
            print(f"⚠️  Skipping {file_path}: {e}")
            continue
    print(f"🎉 Successfully ingested {len(ingested_files)} out of {len(files)} files")
    return ingested_files

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest .txt, .pdf, .docx documents into vector store")
    parser.add_argument("path", help="File or directory path to ingest")
    parser.add_argument("--metadata", help="Additional metadata as JSON string")
    args = parser.parse_args()
    metadata = {}
    if args.metadata:
        import json
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("❌ Invalid JSON metadata")
            sys.exit(1)
    path = Path(args.path)
    if path.is_file():
        try:
            document_id = ingest_document(str(path), metadata)
            print(f"📄 Document ID: {document_id}")
        except Exception as e:
            print(f"❌ Failed to ingest file: {e}")
            sys.exit(1)
    elif path.is_dir():
        try:
            document_ids = ingest_directory(str(path), metadata)
            print(f"📁 Document IDs: {document_ids}")
        except Exception as e:
            print(f"❌ Failed to ingest directory: {e}")
            sys.exit(1)
    else:
        print(f"❌ Path not found: {args.path}")
        sys.exit(1) 