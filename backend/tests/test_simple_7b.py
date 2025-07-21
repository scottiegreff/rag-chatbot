#!/usr/bin/env python3
"""
Simple test script for Mistral 7B model - single question test.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_simple_question():
    """Test a simple question with the 7B model."""
    question = "What is 2+2?"
    
    print(f"🧪 Testing Mistral 7B with: '{question}'")
    print("⏳ This may take a while...")
    
    try:
        payload = {
            "message": question,
            "session_id": "simple_test_7b"
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=120)  # 2 minutes
        end_time = time.time()
        
        duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            print(f"✅ SUCCESS!")
            print(f"   Question: {question}")
            print(f"   Answer: {response_text}")
            print(f"   Response time: {duration:.2f}s")
            return True
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_simple_question() 