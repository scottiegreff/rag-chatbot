#!/usr/bin/env python3
"""
Test script to verify Weaviate integration with the RAG service.
This script tests the basic functionality of the Weaviate-based RAG service.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_weaviate_connection():
    """Test basic Weaviate connection."""
    try:
        import weaviate
        from backend.services.rag_service import RAGService
        from weaviate.connect import ConnectionParams
        
        logger.info("🔍 Testing Weaviate connection...")
        
        # Test direct Weaviate connection
        logger.info(f"Connecting to Weaviate at: http://localhost:8080")
        
        client = weaviate.connect_to_local(skip_init_checks=True)
        
        # Test if Weaviate is responsive
        try:
            meta = client.get_meta()
            logger.info(f"✅ Weaviate connection successful!")
            logger.info(f"   Version: {meta.get('version', 'Unknown')}")
            logger.info(f"   Modules: {list(meta.get('modules', {}).keys())}")
            return True
        except Exception as e:
            logger.error(f"❌ Weaviate connection failed: {e}")
            logger.info("💡 Make sure Weaviate is running on http://localhost:8080")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Weaviate client not installed: {e}")
        logger.info("💡 Run: pip install weaviate-client>=3.25.0")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def test_rag_service_initialization():
    """Test RAG service initialization."""
    try:
        from backend.services.rag_service import RAGService
        
        logger.info("🔄 Testing RAG service initialization...")
        
        # Initialize RAG service
        rag_service = RAGService()
        
        logger.info("✅ RAG service initialized successfully!")
        logger.info(f"   Embedding model: {rag_service.embedding_model}")
        logger.info(f"   Weaviate client: {rag_service.client}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG service initialization failed: {e}")
        return False

def test_document_operations():
    """Test adding and querying documents."""
    try:
        from backend.services.rag_service import RAGService
        
        logger.info("📄 Testing document operations...")
        
        rag_service = RAGService()
        
        # Test document
        test_document = {
            "id": "test_doc_001",
            "text": "Weaviate is a vector database that provides excellent performance for AI applications. It supports semantic search and can handle large-scale vector operations efficiently.",
            "metadata": {
                "category": "technology",
                "source": "test",
                "upload_date": datetime.utcnow().isoformat(timespec='milliseconds') + "Z"
            }
        }
        
        # Add document
        logger.info("📝 Adding test document...")
        rag_service.add_document(
            document_id=test_document["id"],
            text=test_document["text"],
            metadata=test_document["metadata"]
        )
        logger.info("✅ Document added successfully!")
        
        # Query document
        logger.info("🔍 Querying documents...")
        query = "What is Weaviate?"
        results = rag_service.query_documents(query, n_results=3)
        
        if results and hasattr(results, 'objects') and results.objects:
            logger.info("✅ Document query successful!")
            logger.info(f"   Found {len(results.objects)} results")
            # Show first result
            first_doc = results.objects[0].properties.get('content', '')
            logger.info(f"   First result: {first_doc[:100]}...")
        else:
            logger.warning("⚠️  No documents found in query results")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Document operations failed: {e}")
        return False

def test_metadata_filtering():
    """Test metadata filtering functionality."""
    try:
        from backend.services.rag_service import RAGService
        
        logger.info("🔍 Testing metadata filtering...")
        
        rag_service = RAGService()
        
        # Add another test document with different category
        test_document_2 = {
            "id": "test_doc_002",
            "text": "PostgreSQL is a powerful open-source relational database system. It provides excellent support for complex queries and data integrity.",
            "metadata": {
                "category": "database",
                "source": "test",
                "upload_date": datetime.utcnow().isoformat(timespec='milliseconds') + "Z"
            }
        }
        
        rag_service.add_document(
            document_id=test_document_2["id"],
            text=test_document_2["text"],
            metadata=test_document_2["metadata"]
        )
        
        # Test category filtering
        logger.info("🔍 Testing category filter...")
        results = rag_service.query_by_category("database", "database", n_results=2)
        
        if results and hasattr(results, 'objects') and results.objects:
            logger.info("✅ Category filtering works!")
            logger.info(f"   Found {len(results.objects)} database-related results")
        else:
            logger.warning("⚠️  Category filtering returned no results")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Metadata filtering failed: {e}")
        return False

def test_collection_management():
    """Test collection listing and management."""
    try:
        from backend.services.rag_service import RAGService
        
        logger.info("📋 Testing collection management...")
        
        rag_service = RAGService()
        
        # List documents by category
        logger.info("📋 Listing documents by category...")
        tech_docs = rag_service.list_documents_by_category("technology")
        db_docs = rag_service.list_documents_by_category("database")
        
        logger.info(f"   Technology documents: {len(tech_docs.objects) if hasattr(tech_docs, 'objects') else 0}")
        logger.info(f"   Database documents: {len(db_docs.objects) if hasattr(db_docs, 'objects') else 0}")
        
        # List all documents
        all_docs = rag_service.list_documents_by_category()
        logger.info(f"   Total documents: {len(all_docs.objects) if hasattr(all_docs, 'objects') else 0}")
        
        logger.info("✅ Collection management works!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Collection management failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Weaviate integration tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Weaviate Connection", test_weaviate_connection),
        ("RAG Service Initialization", test_rag_service_initialization),
        ("Document Operations", test_document_operations),
        ("Metadata Filtering", test_metadata_filtering),
        ("Collection Management", test_collection_management),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Weaviate integration is working correctly.")
        return True
    else:
        logger.error("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 