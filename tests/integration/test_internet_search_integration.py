#!/usr/bin/env python3
"""
Test script for internet search integration in the frontend
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8010"

def test_search_endpoints():
    """Test the search API endpoints"""
    print("🔍 Testing search endpoints...")
    
    # Test internet search
    print("\n1. Testing internet search...")
    try:
        response = requests.post(f"{BASE_URL}/api/search/internet", json={
            "query": "latest AI developments 2024",
            "num_results": 3,
            "engine": "duckduckgo"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Internet search successful")
            print(f"   Found {len(data.get('results', []))} results")
            if data.get('results'):
                print(f"   First result: {data['results'][0].get('title', 'No title')}")
        else:
            print(f"❌ Internet search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Internet search error: {e}")
    
    # Test hybrid search
    print("\n2. Testing hybrid search...")
    try:
        response = requests.post(f"{BASE_URL}/api/search/hybrid", json={
            "query": "company policies",
            "n_local_results": 2,
            "n_web_results": 2,
            "include_internet": True
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Hybrid search successful")
            print(f"   Local results: {len(data.get('local_results', {}).get('documents', [[]])[0] if data.get('local_results') else 0)}")
            print(f"   Web results: {len(data.get('web_results', []))}")
            if data.get('summary'):
                print(f"   Summary: {data['summary'][:100]}...")
        else:
            print(f"❌ Hybrid search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Hybrid search error: {e}")

def test_chat_with_search():
    """Test chat with custom system instruction (simulating search)"""
    print("\n3. Testing chat with custom system instruction...")
    
    # Create a mock search context
    search_context = """You are a helpful AI assistant. Use the following search results to answer the user's question:

**Web Results:**
1. Latest AI Developments 2024
   Artificial intelligence has seen significant advancements in 2024...
   Source: https://example.com/ai-2024

2. Company Policy Updates
   Recent changes to company policies include...
   Source: https://example.com/policies

**Search Summary:**
The search found information about AI developments and company policies.

Please respond to the user's question: "What are the latest AI developments?" """

    try:
        response = requests.post(f"{BASE_URL}/api/chat/stream", json={
            "message": "What are the latest AI developments?",
            "system_instruction": search_context
        })
        
        if response.status_code == 200:
            print(f"✅ Chat with custom system instruction successful")
            print(f"   Response status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            
            # Read the streaming response
            content = response.text
            print(f"   Response length: {len(content)} characters")
            
            # Check for session ID and content
            if 'session_id' in content:
                print(f"   ✅ Session ID found in response")
            if 'delta' in content:
                print(f"   ✅ Streaming content found")
                
        else:
            print(f"❌ Chat with custom system instruction failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat with custom system instruction error: {e}")

def test_frontend_elements():
    """Test if frontend elements are properly set up"""
    print("\n4. Testing frontend elements...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for search button
            if 'search-btn' in html_content:
                print(f"✅ Search button found in HTML")
            else:
                print(f"❌ Search button not found in HTML")
            
            # Check for search icon
            if 'search.svg' in html_content:
                print(f"✅ Search icon found in HTML")
            else:
                print(f"❌ Search icon not found in HTML")
            
            # Check for search functionality in JavaScript
            if 'handleSearchClick' in html_content:
                print(f"✅ Search function found in JavaScript")
            else:
                print(f"❌ Search function not found in JavaScript")
                
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend test error: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing Internet Search Integration")
    print("=" * 50)
    
    # Test search endpoints
    test_search_endpoints()
    
    # Test chat with search
    test_chat_with_search()
    
    # Test frontend elements
    test_frontend_elements()
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")

if __name__ == "__main__":
    main() 