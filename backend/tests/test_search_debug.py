#!/usr/bin/env python3
"""
Debug script to test the search service and identify issues
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.append('backend')

def test_search_service():
    """Test the search service directly"""
    print("🔍 Testing Search Service...")
    
    try:
        from services.search_service import SearchService
        
        # Initialize search service
        print("✅ Initializing SearchService...")
        search_service = SearchService()
        print("✅ SearchService initialized successfully")
        
        # Test search
        print("🔍 Testing search with query: 'latest AI developments'")
        results = search_service.search("latest AI developments", num_results=3, engine='duckduckgo')
        
        print(f"📊 Search results: {len(results)} found")
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.get('title', 'No title')}")
                print(f"   URL: {result.get('url', 'No URL')}")
                print(f"   Snippet: {result.get('snippet', 'No snippet')[:100]}...")
                print(f"   Source: {result.get('source', 'Unknown')}")
        else:
            print("❌ No search results returned")
            
    except Exception as e:
        print(f"❌ Error testing search service: {e}")
        import traceback
        traceback.print_exc()

def test_rag_service_search():
    """Test the RAG service search functionality"""
    print("\n🔍 Testing RAG Service Search...")
    
    try:
        from services.rag_service import RAGService
        
        # Initialize RAG service
        print("✅ Initializing RAGService...")
        rag_service = RAGService()
        print("✅ RAGService initialized successfully")
        
        # Check if search service is available
        if rag_service.search_service:
            print("✅ Search service is available in RAG service")
            
            # Test hybrid search
            print("🔍 Testing hybrid search...")
            results = rag_service.hybrid_search(
                query="latest AI developments",
                n_local_results=2,
                n_web_results=2,
                include_internet=True
            )
            
            print(f"📊 Hybrid search results:")
            print(f"   Local results: {len(results.get('local_results', {}).get('documents', [[]])[0] if results.get('local_results') else 0)}")
            print(f"   Web results: {len(results.get('web_results', []))}")
            print(f"   Summary: {results.get('summary', 'No summary')[:100]}...")
            
        else:
            print("❌ Search service is NOT available in RAG service")
            print("   This could be due to ENABLE_INTERNET_SEARCH being false")
            
    except Exception as e:
        print(f"❌ Error testing RAG service: {e}")
        import traceback
        traceback.print_exc()

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing Environment Variables...")
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ .env file found: {env_file}")
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"   Content: {content}")
    else:
        print(f"❌ .env file not found: {env_file}")
    
    # Check ENABLE_INTERNET_SEARCH
    enable_internet = os.getenv("ENABLE_INTERNET_SEARCH", "true").lower() == "true"
    print(f"   ENABLE_INTERNET_SEARCH: {enable_internet}")
    
    # Check other relevant environment variables
    print(f"   PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    print(f"   Current working directory: {os.getcwd()}")

def test_network_connectivity():
    """Test network connectivity to search engines"""
    print("\n🔍 Testing Network Connectivity...")
    
    import requests
    
    test_urls = [
        "https://api.duckduckgo.com/",
        "https://www.google.com/",
        "https://www.bing.com/"
    ]
    
    for url in test_urls:
        try:
            print(f"   Testing {url}...")
            response = requests.get(url, timeout=10)
            print(f"   ✅ {url}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url}: {e}")

def main():
    """Run all tests"""
    print("🚀 Search Service Debug Test")
    print("=" * 50)
    
    test_environment_variables()
    test_network_connectivity()
    test_search_service()
    test_rag_service_search()
    
    print("\n" + "=" * 50)
    print("✅ Debug test completed!")

if __name__ == "__main__":
    main() 