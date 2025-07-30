#!/usr/bin/env python3
"""
Utility script to clear the vector database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.rag_service import RAGService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_vector_database():
    """Clear all documents from the vector database"""
    try:
        logger.info("🔄 Initializing RAG service...")
        rag_service = RAGService()
        
        logger.info("🗑️ Clearing all documents from vector database...")
        rag_service.clear_all_documents()
        
        logger.info("✅ Vector database cleared successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error clearing vector database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clear_vector_database() 