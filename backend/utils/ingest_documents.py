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

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from backend.services.rag_service import RAGService

def process_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Process and clean metadata for vector store compatibility."""
    
    processed = {}
    for key, value in metadata.items():
        if value is None:
            continue
            
        # Convert datetime to ISO string for Weaviate compatibility
        if isinstance(value, datetime):
            processed[key] = value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"
        # Handle None values and convert lists to comma-separated strings for Weaviate compatibility
        elif isinstance(value, list):
            processed[key] = ", ".join(str(item) for item in value if item is not None)
        else:
            processed[key] = str(value)
    
    return processed

def ingest_document(file_path: str, metadata: Dict[str, Any] = None) -> str:
    """Ingest a single document into the vector store."""
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Process metadata
    if metadata is None:
        metadata = {}
    
    # Add file information to metadata
    file_info = {
        "filename": os.path.basename(file_path),
        "file_path": file_path,
        "ingestion_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}Z",
        "document_id": document_id
    }
    metadata.update(file_info)
    
    # Process metadata for compatibility
    processed_metadata = process_metadata(metadata)
    
    try:
        # Add document to vector store
        rag_service.add_document_from_file(
            document_id=document_id,
            file_path=file_path,
            metadata=processed_metadata
        )
        
        print(f"✅ Successfully ingested: {file_path}")
        return document_id
        
    except Exception as e:
        print(f"❌ Failed to ingest {file_path}: {e}")
        raise

def ingest_directory(directory_path: str, metadata: Dict[str, Any] = None) -> List[str]:
    """Ingest all supported documents from a directory."""
    
    supported_extensions = {'.pdf', '.docx', '.txt'}
    ingested_files = []
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Find all supported files
    files = [f for f in directory.rglob('*') if f.is_file() and f.suffix.lower() in supported_extensions]
    
    if not files:
        print(f"📭 No supported files found in {directory_path}")
        return []
    
    print(f"📁 Found {len(files)} files to ingest:")
    for file in files:
        print(f"   - {file}")
    
    # Ingest each file
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
    
    parser = argparse.ArgumentParser(description="Ingest documents into vector store")
    parser.add_argument("path", help="File or directory path to ingest")
    parser.add_argument("--metadata", help="Additional metadata as JSON string")
    
    args = parser.parse_args()
    
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        import json
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("❌ Invalid JSON metadata")
            sys.exit(1)
    
    # Ingest based on path type
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