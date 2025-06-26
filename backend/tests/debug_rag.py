"""
Debug RAG Service

This script helps debug the RAG service and Weaviate integration.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from backend.services.rag_service import RAGService

def debug_rag_service():
    """Debug the RAG service and Weaviate connection."""
    
    print("🔍 Debugging RAG Service...")
    print("=" * 50)
    
    try:
        # Test RAG service initialization
        print("1. Testing RAG service initialization...")
        rag_service = RAGService()
        print("✅ RAG service initialized successfully")
        
        # Test Weaviate connection
        print("\n2. Testing Weaviate connection...")
        client = rag_service.weaviate_client
        if client.is_ready():
            print("✅ Weaviate connection successful")
        else:
            print("❌ Weaviate connection failed")
            return
        
        # Test collection existence
        print("\n3. Testing collection existence...")
        collection_name = "Documents"
        if client.collections.exists(collection_name):
            print(f"✅ Collection '{collection_name}' exists")
        else:
            print(f"❌ Collection '{collection_name}' does not exist")
        
        # Test document count
        print("\n4. Testing document count...")
        try:
            count = client.collections.get(collection_name).aggregate.over_all().with_fields('total').do()
            total_count = count.total
            print(f"✅ Total documents in collection: {total_count}")
        except Exception as e:
            print(f"❌ Error getting document count: {e}")
        
        # Test embedding model
        print("\n5. Testing embedding model...")
        try:
            test_text = "This is a test sentence for embedding."
            embedding = rag_service.embedding_model.encode(test_text)
            print(f"✅ Embedding model working (vector length: {len(embedding)})")
        except Exception as e:
            print(f"❌ Error with embedding model: {e}")
        
        print("\n🎉 RAG service debug complete!")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rag_service() 