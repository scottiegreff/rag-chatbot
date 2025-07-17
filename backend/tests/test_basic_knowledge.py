#!/usr/bin/env python3
"""
Test script to verify the chatbot's basic knowledge and reasoning capabilities.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8010/api"

async def test_basic_knowledge():
    """Test the chatbot's basic knowledge and reasoning."""
    
    print("🧪 Testing basic knowledge and reasoning...")
    print("=" * 50)
    
    # Test questions covering different types of knowledge
    test_questions = [
        # Mathematical questions
        ("What is (25 × 4) + (100 ÷ 5)?", "Should be 120 (100 + 20)"),
        ("What is 2 + 2?", "Should be 4"),
        ("What is 15 × 3?", "Should be 45"),
        
        # Programming questions
        ('What does print("3" + "5") output?', "Should be '35' (string concatenation)"),
        ("What is 3 + 5 in Python?", "Should be 8"),
        
        # Factual questions
        ("What is the capital of Brazil?", "Should be Brasília"),
        ("What does GPT stand for?", "Should be Generative Pre-trained Transformer"),
        ("What day of the week was January 1, 2000?", "Should be Saturday"),
        
        # Logic questions
        ("If all bloops are razzies, and all razzies are lazzies, are all bloops definitely lazzies?", "Should be Yes"),
        
        # Basic knowledge
        ("What molecule do plants absorb from the air for photosynthesis?", "Should be carbon dioxide (CO2)"),
        ("What is the largest planet in our solar system?", "Should be Jupiter"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, (question, expected) in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            print(f"   Expected: {expected}")
            print("-" * 50)
            
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
                        
                        print(f"Response: {chatbot_response}")
                        
                        # Check for problematic patterns
                        problematic_patterns = [
                            "I don't have access",
                            "I am not capable",
                            "I couldn't find",
                            "I don't know what",
                            "not specified in your question"
                        ]
                        
                        has_problematic = any(pattern in chatbot_response for pattern in problematic_patterns)
                        if has_problematic:
                            print("❌ Response contains problematic patterns")
                        else:
                            print("✅ Response is clean")
                            
                        # Check for mathematical accuracy (basic check)
                        if "25 × 4" in question and "120" in chatbot_response:
                            print("✅ Mathematical calculation correct")
                        elif "25 × 4" in question and "130" in chatbot_response:
                            print("❌ Mathematical calculation incorrect")
                        elif "2 + 2" in question and "4" in chatbot_response:
                            print("✅ Basic math correct")
                        elif "print" in question and "35" in chatbot_response:
                            print("✅ Programming answer correct")
                        elif "print" in question and "6" in chatbot_response:
                            print("❌ Programming answer incorrect")
                        elif "Brazil" in question and "Brasília" in chatbot_response:
                            print("✅ Factual answer correct")
                        elif "GPT" in question and "Generative" in chatbot_response:
                            print("✅ GPT definition correct")
                        elif "photosynthesis" in question and "carbon dioxide" in chatbot_response:
                            print("✅ Science answer correct")
                        else:
                            print("⚠️  Answer quality unclear")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()

async def test_conversation_continuity():
    """Test if the chatbot can maintain conversation context."""
    
    print("\n🧪 Testing conversation continuity...")
    print("=" * 50)
    
    questions = [
        "What is the capital of France?",
        "What is the population of that city?",
        "What is the main language spoken there?"
    ]
    
    session_id = None
    async with aiohttp.ClientSession() as session:
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. Question: {question}")
            print("-" * 30)
            
            try:
                payload = {
                    "message": question,
                    "session_id": session_id
                }
                
                async with session.post(f"{API_BASE_URL}/chat", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        chatbot_response = data.get("response", "")
                        session_id = data.get("session_id", session_id)
                        
                        print(f"Response: {chatbot_response}")
                        
                        # Check if response acknowledges context
                        if i > 1 and ("that city" in question or "there" in question):
                            if "Paris" in chatbot_response or "France" in chatbot_response:
                                print("✅ Context maintained")
                            else:
                                print("⚠️  Context may be lost")
                        else:
                            print("✅ Direct question answered")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()

async def main():
    """Run all tests."""
    print("🚀 Starting basic knowledge and reasoning tests...")
    print("Make sure the chatbot API is running on http://localhost:8010")
    print()
    
    # Test basic knowledge
    await test_basic_knowledge()
    
    # Test conversation continuity
    await test_conversation_continuity()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 