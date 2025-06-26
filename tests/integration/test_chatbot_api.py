#!/usr/bin/env python3
"""
Simple API-based test script to verify chatbot functionality after container restart.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the backend is healthy and responding."""
    try:
        response = requests.get(f"{BASE_URL}/test", timeout=10)
        print(f"✅ Health check: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_simple_chat():
    """Test basic chat functionality."""
    try:
        payload = {
            "message": "What is 2+2?",
            "session_id": "test_session_001"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
        print(f"✅ Chat test: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_knowledge_questions():
    """Test questions that should use the model's knowledge."""
    questions = [
        "What is the capital of France?",
        "Who wrote Romeo and Juliet?",
        "What is photosynthesis?"
    ]
    
    results = []
    for i, question in enumerate(questions, 1):
        try:
            payload = {
                "message": question,
                "session_id": f"test_session_knowledge_{i}"
            }
            response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"✅ Q{i}: {question}")
                print(f"   A: {response_text[:150]}...")
                results.append(True)
            else:
                print(f"❌ Q{i}: Failed - {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Q{i}: Exception - {e}")
            results.append(False)
    
    return results

def main():
    print("🧪 Testing FCI Chatbot API after container restart...")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Backend is not responding. Please check if containers are running.")
        return
    
    # Test 2: Simple chat
    if not test_simple_chat():
        print("❌ Basic chat functionality failed.")
        return
    
    # Test 3: Knowledge questions
    print("\n📚 Testing knowledge-based questions...")
    knowledge_results = test_knowledge_questions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Health Check: ✅")
    print(f"   Basic Chat: ✅")
    print(f"   Knowledge Questions: {sum(knowledge_results)}/{len(knowledge_results)} passed")
    
    if all(knowledge_results):
        print("🎉 All tests passed! Chatbot is working correctly.")
    else:
        print("⚠️  Some knowledge questions failed. This may be due to model limitations.")

if __name__ == "__main__":
    main() 