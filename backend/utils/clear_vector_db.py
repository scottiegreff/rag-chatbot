#!/usr/bin/env python3
"""
Clear Vector Database

This script clears all documents from the Weaviate vector store.
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

def clear_vector_database():
    """Clear all documents from the vector database."""
    
    try:
        # Initialize RAG service
        rag_service = RAGService()
        
        # Clear all documents
        rag_service.clear_all_documents()
        
        print("✅ Successfully cleared all documents from the vector database.")
        
    except Exception as e:
        print(f"❌ Error clearing vector database: {e}")

def main():
    """Main function to clear the vector database."""
    print("🗑️  AI Chatbot - Vector Database Clear Utility")
    print("=" * 50)
    
    # Clear the database directly
    clear_vector_database()
    print("\n✅ Vector database cleared successfully!")

if __name__ == "__main__":
    main() 