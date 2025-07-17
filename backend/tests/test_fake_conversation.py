#!/usr/bin/env python3
"""
Test script to verify that the chatbot doesn't generate fake conversations.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8010/api"

async def test_fake_conversation():
    """Test that the chatbot doesn't generate fake conversations."""
    
    print("🧪 Testing for fake conversation generation...")
    print("=" * 50)
    
    # Test questions that might trigger fake conversations
    test_questions = [
        "What are the continents?",
        "Tell me about world population",
        "What is the highest mountain?",
        "List the planets in our solar system",
        "What are the oceans?"
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            print("-" * 30)
            
            try:
                # Make request to the chat API
                payload = {
                    "message": question,
                    "session_id": None
                }
                
                async with session.post(f"{API_BASE_URL}/chat", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        chatbot_response = data.get("response", "")
                        session_id = data.get("session_id", "")
                        
                        print(f"Session ID: {session_id}")
                        print(f"Response: {chatbot_response}")
                        
                        # Check for fake conversation indicators
                        fake_conversation_indicators = [
                            "User:",
                            "User: Do you",
                            "User: Can you", 
                            "User: What",
                            "User: How",
                            "User: When",
                            "User: Where",
                            "User: Why",
                            "User: Which",
                            "Assistant: I don't have access",
                            "Assistant: Again, I don't have access"
                        ]
                        
                        has_fake_conversation = any(indicator in chatbot_response for indicator in fake_conversation_indicators)
                        if has_fake_conversation:
                            print("❌ Response contains fake conversation elements")
                        else:
                            print("✅ Response is clean - no fake conversation")
                            
                        # Check for repetitive patterns
                        if chatbot_response.count("I don't have access") > 1:
                            print("⚠️  Response contains repetitive 'I don't have access' patterns")
                        elif "I don't have access" in chatbot_response:
                            print("⚠️  Response contains 'I don't have access' (but not repetitive)")
                        else:
                            print("✅ No 'I don't have access' patterns found")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()

async def test_specific_fake_conversation():
    """Test the specific question that triggered the fake conversation."""
    
    print("\n🧪 Testing specific fake conversation trigger...")
    print("=" * 50)
    
    question = "What are the continents?"
    print(f"Question: {question}")
    print("-" * 30)
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "message": question,
                "session_id": None
            }
            
            async with session.post(f"{API_BASE_URL}/chat", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    chatbot_response = data.get("response", "")
                    session_id = data.get("session_id", "")
                    
                    print(f"Session ID: {session_id}")
                    print(f"Response: {chatbot_response}")
                    
                    # Check for the specific fake conversation pattern
                    if "User: Do you know which continent has the most population?" in chatbot_response:
                        print("❌ Still generating fake conversation")
                    elif "User:" in chatbot_response:
                        print("❌ Still generating fake conversation elements")
                    else:
                        print("✅ No fake conversation detected")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting fake conversation detection tests...")
    print("Make sure the chatbot API is running on http://localhost:8010")
    print()
    
    # Test general fake conversation detection
    await test_fake_conversation()
    
    # Test specific trigger
    await test_specific_fake_conversation()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 