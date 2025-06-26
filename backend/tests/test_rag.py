"""
Test RAG Service

This module contains tests for the RAG (Retrieval-Augmented Generation) service.
"""

import pytest
from backend.services.rag_service import RAGService

@pytest.fixture
def rag_service():
    """Create a RAG service instance for testing."""
    return RAGService()

@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "id": "weaviate_intro",
            "text": "Weaviate is a vector database for storing and retrieving embeddings.",
            "metadata": {"source": "weaviate_docs"}
        },
        {
            "id": "rag_explanation",
            "text": "RAG combines language models with external knowledge retrieval.",
            "metadata": {"source": "ai_research"}
        },
        {
            "id": "fastapi_info",
            "text": "FastAPI is a modern web framework for building APIs with Python.",
            "metadata": {"source": "python_docs"}
        }
    ]

def test_add_document(rag_service, sample_documents):
    """Test adding a document to the vector store."""
    doc = sample_documents[0]
    
    # Add document
    rag_service.add_document(
        document_id=doc["id"],
        text=doc["text"],
        metadata=doc["metadata"]
    )
    
    # Query to verify it was added
    results = rag_service.query_documents("vector database", n_results=1)
    
    assert results is not None
    assert len(results.objects) > 0

def test_query_documents(rag_service, sample_documents):
    """Test querying documents from the vector store."""
    # Add sample documents
    for doc in sample_documents:
        rag_service.add_document(
            document_id=doc["id"],
            text=doc["text"],
            metadata=doc["metadata"]
        )
    
    # Test query
    query = "What is Weaviate used for?"
    results = rag_service.query_documents(query, n_results=3)
    
    assert results is not None
    assert len(results.objects) > 0
    
    # Check that results contain relevant content
    content = " ".join([obj.properties.get("content", "") for obj in results.objects])
    assert "vector" in content.lower() or "weaviate" in content.lower()

def test_clear_documents(rag_service, sample_documents):
    """Test clearing all documents from the vector store."""
    # Add a document first
    doc = sample_documents[0]
    rag_service.add_document(
        document_id=doc["id"],
        text=doc["text"],
        metadata=doc["metadata"]
    )
    
    # Clear all documents
    rag_service.clear_all_documents()
    
    # Verify no documents remain
    results = rag_service.query_documents("test", n_results=10)
    assert len(results.objects) == 0 