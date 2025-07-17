#!/usr/bin/env python3
"""
Test script to verify that the chatbot provides clean, direct responses.
This test makes HTTP requests to the running API instead of importing the service directly.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8010/api"

async def test_response_quality():
    """Test the chatbot API with questions to verify response quality."""
    
    print("🧪 Testing chatbot response quality via API...")
    print("=" * 50)
    
    # Test questions
    test_questions = [
        "How old is the universe?",
        "What is the capital of France?",
        "What is 5 + 7?",
        "Who wrote Hamlet?",
        "What is the chemical symbol for oxygen?"
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            print("-" * 30)
            
            try:
                # Make request to the chat API
                payload = {
                    "message": question,
                    "session_id": None  # Let the API create a new session
                }
                
                async with session.post(f"{API_BASE_URL}/chat", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        chatbot_response = data.get("response", "")
                        session_id = data.get("session_id", "")
                        
                        print(f"Session ID: {session_id}")
                        print(f"Response: {chatbot_response}")
                        
                        # Check for unwanted text
                        unwanted_phrases = [
                            "Implementing this functionality",
                            "This functionality will help",
                            "This will help users",
                            "This improves the overall",
                            "This will reduce the need"
                        ]
                        
                        has_unwanted = any(phrase in chatbot_response for phrase in unwanted_phrases)
                        if has_unwanted:
                            print("❌ Response contains unwanted text")
                        else:
                            print("✅ Response is clean")
                            
                        # Check response length
                        if len(chatbot_response.strip()) < 5:
                            print("⚠️  Response seems too short")
                        elif len(chatbot_response.strip()) > 500:
                            print("⚠️  Response seems too long")
                        else:
                            print("✅ Response length is appropriate")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()

async def test_streaming_response():
    """Test the streaming chat endpoint."""
    
    print("\n🧪 Testing streaming response...")
    print("=" * 50)
    
    question = "What is the capital of Canada?"
    print(f"Question: {question}")
    print("-" * 30)
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": question,
                "session_id": None
            }
            
            async with session.post(f"{API_BASE_URL}/chat/stream", json=payload) as response:
                if response.status == 200:
                    full_response = ""
                    session_id = None
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                
                                if 'session_id' in data:
                                    session_id = data['session_id']
                                    print(f"Session ID: {session_id}")
                                elif 'delta' in data:
                                    token = data['delta']
                                    full_response += token
                                    print(token, end='', flush=True)
                                elif 'end' in data:
                                    print("\n\n✅ Streaming completed")
                                    break
                                elif 'error' in data:
                                    print(f"\n❌ Error: {data['error']}")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"\n\n📄 Full response: {full_response}")
                    
                    # Check for unwanted text
                    unwanted_phrases = [
                        "Implementing this functionality",
                        "This functionality will help",
                        "This will help users",
                        "This improves the overall",
                        "This will reduce the need"
                    ]
                    
                    has_unwanted = any(phrase in full_response for phrase in unwanted_phrases)
                    if has_unwanted:
                        print("❌ Response contains unwanted text")
                    else:
                        print("✅ Response is clean")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting chatbot response quality tests...")
    print("Make sure the chatbot API is running on http://localhost:8010")
    print()
    
    # Test regular chat endpoint
    await test_response_quality()
    
    # Test streaming endpoint
    await test_streaming_response()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 