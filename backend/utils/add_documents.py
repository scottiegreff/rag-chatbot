"""
Add Documents to Vector Store

This script demonstrates how to add documents to the Weaviate vector store.
Weaviate is a vector database that allows you to store and retrieve embeddings
for semantic search and RAG applications.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.services.rag_service import RAGService
import uuid

# --- Configurable chunking parameters from environment ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))  # characters
OVERLAP = int(os.getenv("OVERLAP", "50"))         # characters


def add_sample_documents():
    """Add sample documents to the vector store."""
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Sample documents
    documents = [
        {
            "id": "weaviate_intro",
            "text": "Weaviate is an open-source vector database that allows you to store and retrieve embeddings for semantic search and AI applications.",
            "metadata": {"source": "weaviate_documentation", "category": "vector_database"}
        },
        {
            "id": "rag_explanation", 
            "text": "Retrieval-Augmented Generation (RAG) combines the power of large language models with external knowledge retrieval to provide more accurate and contextual responses.",
            "metadata": {"source": "ai_research", "category": "ai_concepts"}
        },
        {
            "id": "fastapi_info",
            "text": "FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints.",
            "metadata": {"source": "python_docs", "category": "web_framework"}
        }
    ]
    
    # Add documents
    for doc in documents:
        try:
            rag_service.add_document(
                document_id=doc["id"],
                text=doc["text"],
                metadata=doc["metadata"]
            )
            print(f"✅ Added document: {doc['id']}")
        except Exception as e:
            print(f"❌ Failed to add document {doc['id']}: {e}")
    
    print("🎉 Document addition complete!")


def add_custom_document(text: str, source: str, category: str = "custom"):
    """Add a custom document to the vector database"""
    rag_service = RAGService()
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    metadata = {"source": source, "category": category}
    
    rag_service.add_document(doc_id, text, metadata)
    print(f"Added custom document: {source}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If arguments provided, add custom document
        if len(sys.argv) >= 3:
            text = sys.argv[1]
            source = sys.argv[2]
            category = sys.argv[3] if len(sys.argv) > 3 else "custom"
            add_custom_document(text, source, category)
        else:
            print("Usage: python add_documents.py <text> <source> [category]")
    else:
        # Add sample documents
        add_sample_documents() 