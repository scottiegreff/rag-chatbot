#!/usr/bin/env python3
"""
Test script to verify fallback method works for "list our 5 cheapest products"
"""

import requests
import json
import time

def test_fallback_list_products():
    """Test that list queries use fallback method"""
    
    # Test queries that should use fallback
    test_queries = [
        "list our 5 cheapest products",
        "show our 3 most expensive products", 
        "top 10 best selling products",
        "list our 7 cheapest products"
    ]
    
    base_url = "http://localhost:8000"
    
    for query in test_queries:
        print(f"\n🧪 Testing: '{query}'")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": query,
                    "session_id": "test_session"
                },
                timeout=30
            )
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received in {duration:.2f}ms")
                print(f"📝 Response: {data.get('response', 'No response')}")
                
                # Check if it used fallback (should be fast)
                if duration < 1000:  # Less than 1 second
                    print(f"⚡ FAST RESPONSE - Likely used fallback method")
                else:
                    print(f"🐌 SLOW RESPONSE - Likely used LangChain agent")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    print("🚀 Testing fallback method for list product queries...")
    test_fallback_list_products() 