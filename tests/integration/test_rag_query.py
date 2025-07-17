#!/usr/bin/env python3
"""
Test script to debug RAG query format
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_rag_query():
    """Test RAG query and see the actual format returned"""
    print("🧪 Testing RAG query format...")
    
    try:
        from backend.services.rag_service import RAGService
        
        # Initialize RAG service
        rag = RAGService()
        print("✅ RAG service initialized")
        
        # Test query
        query = "How do I find the top 5 customers by total spending?"
        print(f"🔍 Querying: {query}")
        
        results = rag.query_documents(query, n_results=3)
        print(f"📊 Results type: {type(results)}")
        print(f"📊 Results: {results}")
        
        # Try to access the results
        if hasattr(results, 'objects'):
            print(f"📊 Objects: {results.objects}")
            print(f"📊 Number of objects: {len(results.objects)}")
            
            for i, obj in enumerate(results.objects):
                print(f"\n--- Object {i+1} ---")
                print(f"Properties: {obj.properties}")
                print(f"Score: {getattr(obj, 'score', 'N/A')}")
                print(f"Content preview: {obj.properties.get('content', '')[:100]}...")
        else:
            print("❌ No 'objects' attribute found")
            print(f"📊 Available attributes: {dir(results)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_query() 