#!/usr/bin/env python3
"""
Check Vector Database Contents

This script checks what documents are currently in the Weaviate vector store.
"""

import os
import sys
from pathlib import Path
import logging

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from backend.services.rag_service import RAGService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_vector_database():
    """Check the contents of the vector database."""
    
    try:
        # Initialize RAG service
        rag_service = RAGService()
        
        # Get all documents
        all_docs = rag_service.list_documents_by_category()
        
        if hasattr(all_docs, 'objects') and all_docs.objects:
            print(f"📊 Found {len(all_docs.objects)} documents in the vector database:")
            print("-" * 50)
            
            for i, doc in enumerate(all_docs.objects, 1):
                props = doc.properties
                print(f"\n📄 Document {i}:")
                print(f"   ID: {props.get('document_id', 'N/A')}")
                print(f"   Category: {props.get('category', 'N/A')}")
                print(f"   Source: {props.get('source', 'N/A')}")
                print(f"   Chunk Index: {props.get('chunk_index', 'N/A')}")
                print(f"   Content Preview: {props.get('content', '')[:100]}...")
        else:
            print("📭 No documents found in the vector database.")
            
    except Exception as e:
        print(f"❌ Error checking vector database: {e}")

def main():
    """Main function to check the vector database."""
    print("🔍 AI Chatbot - Vector Database Check Utility")
    print("=" * 50)
    
    check_vector_database()
    print("\n✅ Vector database check completed!")

if __name__ == "__main__":
    main() 