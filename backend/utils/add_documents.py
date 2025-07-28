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
import weaviate
from weaviate.connect import ConnectionParams
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
client = weaviate.WeaviateClient(ConnectionParams.from_url(WEAVIATE_URL, grpc_port=50051))
client.connect()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))  # characters
OVERLAP = int(os.getenv("OVERLAP", "50"))         # characters

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+chunk_size])
        i += chunk_size - overlap
    return chunks

def add_sample_documents():
    """Add sample documents to the vector store using v4 client."""
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
    docs = client.collections.get("Documents")
    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]
        document_id = doc["id"]
        chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
        for idx, chunk in enumerate(chunks):
            props = dict(metadata)
            props["content"] = chunk
            props["chunk_index"] = idx
            props["document_id"] = document_id
            props["upload_date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}Z"
            docs.data.insert(properties=props)
        print(f"✅ Added document: {document_id} as {len(chunks)} chunk(s)")
    print("🎉 Document addition complete!")

def add_custom_document(text: str, source: str, category: str = "custom"):
    """Add a custom document to the vector database using v4 client."""
    docs = client.collections.get("Documents")
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    metadata = {"source": source, "category": category}
    chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    for idx, chunk in enumerate(chunks):
        props = dict(metadata)
        props["content"] = chunk
        props["chunk_index"] = idx
        props["document_id"] = doc_id
        props["upload_date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}Z"
        docs.data.insert(properties=props)
    print(f"Added custom document: {source} as {len(chunks)} chunk(s)")

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