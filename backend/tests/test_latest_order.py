#!/usr/bin/env python3
"""
Test script to verify the latest order functionality
"""

import requests
import json

def test_latest_order():
    """Test the latest order query functionality"""
    
    # Test the question about the last order
    test_questions = [
        "What was the last order made and by who?",
        "Who made the most recent order?",
        "What is the latest order?",
        "Show me the last order",
        "Who placed the most recent order?"
    ]
    
    base_url = "http://localhost:8000/api"
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Testing question: {question}")
        print(f"{'='*60}")
        
        try:
            # Send the question to the chat endpoint
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": question,
                    "session_id": "test_session"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"Response: {result.get('response', 'No response')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("Testing latest order functionality...")
    test_latest_order() 