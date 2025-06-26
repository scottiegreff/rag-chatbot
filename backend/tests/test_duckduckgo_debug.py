#!/usr/bin/env python3
"""
Debug script to test DuckDuckGo API specifically
"""

import requests
import json

def test_duckduckgo_api():
    """Test DuckDuckGo API directly"""
    print("🔍 Testing DuckDuckGo API...")
    
    # Test queries
    test_queries = [
        "latest AI developments",
        "Python programming",
        "weather",
        "calculator",
        "2+2",
        "population of Canada",
        "capital of France",
        "who is Albert Einstein",
        "what is photosynthesis",
        "how to make coffee"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for instant answer
            if data.get('Abstract'):
                print(f"   ✅ Abstract found: {data['Abstract'][:100]}...")
            else:
                print(f"   ❌ No Abstract found")
            
            # Check for related topics
            related_topics = data.get('RelatedTopics', [])
            print(f"   Related topics: {len(related_topics)}")
            
            # Check for redirect
            if data.get('Redirect'):
                print(f"   ✅ Redirect: {data['Redirect']}")
            
            # Check for answer
            if data.get('Answer'):
                print(f"   ✅ Answer: {data['Answer']}")
            
            # Check for definition
            if data.get('Definition'):
                print(f"   ✅ Definition: {data['Definition']}")
            
            # Show first few related topics
            for i, topic in enumerate(related_topics[:3]):
                if isinstance(topic, dict):
                    print(f"   Topic {i+1}: {topic.get('Text', 'No text')[:50]}...")
                else:
                    print(f"   Topic {i+1}: {str(topic)[:50]}...")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_alternative_search():
    """Test alternative search approaches"""
    print("\n🔍 Testing Alternative Search Approaches...")
    
    # Test with different parameters
    query = "latest AI developments"
    
    # Test 1: Without skip_disambig
    print(f"\n1. Testing without skip_disambig...")
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        related_topics = data.get('RelatedTopics', [])
        print(f"   Related topics: {len(related_topics)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: With different query format
    print(f"\n2. Testing with different query...")
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': "AI developments 2024",
            'format': 'json',
            'no_html': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        related_topics = data.get('RelatedTopics', [])
        print(f"   Related topics: {len(related_topics)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 DuckDuckGo API Debug Test")
    print("=" * 50)
    
    test_duckduckgo_api()
    test_alternative_search()
    
    print("\n" + "=" * 50)
    print("✅ DuckDuckGo debug test completed!")

if __name__ == "__main__":
    main() 