#!/usr/bin/env python3
"""
Test script to verify internet search functionality.
This script tests the new search endpoints and functionality.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8010"

def test_search_status():
    """Test the search status endpoint."""
    print("🧪 Testing Search Status")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/search/status")
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search Status Retrieved Successfully!")
            print(f"📋 RAG Available: {data.get('rag_available')}")
            print(f"📋 Internet Search Available: {data.get('internet_search_available')}")
            print(f"📋 Message: {data.get('message')}")
        else:
            print("❌ Failed to get search status")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_internet_search():
    """Test internet search functionality."""
    print("\n🧪 Testing Internet Search")
    print("=" * 50)
    
    test_queries = [
        "latest AI developments 2024",
        "Python programming best practices",
        "machine learning tutorials"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        try:
            data = {
                "query": query,
                "num_results": 3,
                "engine": "duckduckgo"
            }
            
            response = requests.post(f"{BASE_URL}/api/search/internet", json=data)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Internet Search Successful!")
                print(f"📋 Query: {result.get('query')}")
                print(f"📋 Total Results: {result.get('total_results')}")
                print(f"📋 Summary: {result.get('summary', '')[:200]}...")
                
                # Show first result
                results = result.get('results', [])
                if results:
                    first_result = results[0]
                    print(f"📋 First Result:")
                    print(f"   Title: {first_result.get('title', 'N/A')}")
                    print(f"   URL: {first_result.get('url', 'N/A')}")
                    print(f"   Source: {first_result.get('source', 'N/A')}")
            else:
                print("❌ Internet Search Failed!")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait between requests to be respectful
        time.sleep(2)

def test_hybrid_search():
    """Test hybrid search functionality."""
    print("\n🧪 Testing Hybrid Search")
    print("=" * 50)
    
    test_query = "Python programming"
    
    try:
        data = {
            "query": test_query,
            "n_local_results": 2,
            "n_web_results": 2,
            "include_internet": True
        }
        
        response = requests.post(f"{BASE_URL}/api/search/hybrid", json=data)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Hybrid Search Successful!")
            print(f"📋 Query: {result.get('query')}")
            print(f"📋 Local Results: {result.get('local_count')}")
            print(f"📋 Web Results: {result.get('web_count')}")
            print(f"📋 Summary: {result.get('summary', '')[:200]}...")
            
            # Show local results
            local_results = result.get('local_results', {})
            if local_results and local_results.get('documents'):
                print(f"📋 Local Documents Found: {len(local_results['documents'][0])}")
            
            # Show web results
            web_results = result.get('web_results', [])
            if web_results:
                print(f"📋 Web Results Found: {len(web_results)}")
                for i, web_result in enumerate(web_results[:2], 1):
                    print(f"   {i}. {web_result.get('title', 'N/A')}")
                    print(f"      URL: {web_result.get('url', 'N/A')}")
        else:
            print("❌ Hybrid Search Failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_search_without_internet():
    """Test hybrid search with internet disabled."""
    print("\n🧪 Testing Hybrid Search (Internet Disabled)")
    print("=" * 50)
    
    test_query = "Python programming"
    
    try:
        data = {
            "query": test_query,
            "n_local_results": 3,
            "n_web_results": 0,
            "include_internet": False
        }
        
        response = requests.post(f"{BASE_URL}/api/search/hybrid", json=data)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Local-Only Search Successful!")
            print(f"📋 Query: {result.get('query')}")
            print(f"📋 Local Results: {result.get('local_count')}")
            print(f"📋 Web Results: {result.get('web_count')}")
            
            # Show local results
            local_results = result.get('local_results', {})
            if local_results and local_results.get('documents'):
                print(f"📋 Local Documents Found: {len(local_results['documents'][0])}")
                for i, doc in enumerate(local_results['documents'][0][:2], 1):
                    print(f"   {i}. {doc[:100]}...")
        else:
            print("❌ Local-Only Search Failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Internet Search Tests")
    print("=" * 60)
    
    # Test search status first
    test_search_status()
    
    # Test internet search
    test_internet_search()
    
    # Test hybrid search
    test_hybrid_search()
    
    # Test local-only search
    test_search_without_internet()
    
    print("\n🎉 Test Suite Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main() 