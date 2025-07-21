#!/usr/bin/env python3
"""
Timing Analysis Test Script

This script helps analyze the timing performance of different components
in the AI-Chatbot pipeline to identify bottlenecks.
"""

import asyncio
import time
import requests
import json
from datetime import datetime

def test_chat_timing():
    """Test the chat endpoint and analyze timing"""
    print("🚀 Starting timing analysis test...")
    print("=" * 60)
    
    # Test message
    test_message = "What is the main topic of the uploaded documents?"
    
    print(f"📝 Test message: '{test_message}'")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print("-" * 60)
    
    # Make request to chat endpoint
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat/stream",
            json={
                "message": test_message,
                "session_id": None  # Create new session
            },
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Request successful, analyzing response...")
            
            # Process streaming response
            full_response = ""
            first_token_time = None
            last_token_time = None
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            
                            if 'delta' in data:
                                if first_token_time is None:
                                    first_token_time = time.time()
                                full_response += data['delta']
                                last_token_time = time.time()
                            
                            if 'done' in data:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            
            # Calculate timing metrics
            total_time = (end_time - start_time) * 1000  # Convert to ms
            time_to_first_token = (first_token_time - start_time) * 1000 if first_token_time else 0
            generation_time = (last_token_time - first_token_time) * 1000 if last_token_time and first_token_time else 0
            
            print("\n📊 TIMING RESULTS:")
            print(f"   • Total request time: {total_time:.2f}ms")
            print(f"   • Time to first token: {time_to_first_token:.2f}ms")
            print(f"   • Token generation time: {generation_time:.2f}ms")
            print(f"   • Response length: {len(full_response)} characters")
            print(f"   • Response preview: {full_response[:100]}...")
            
            # Performance analysis
            print("\n🔍 PERFORMANCE ANALYSIS:")
            if time_to_first_token > total_time * 0.8:
                print("   ⚠️  High latency to first token - possible LLM loading or RAG bottleneck")
            elif generation_time > total_time * 0.7:
                print("   ⚠️  Slow token generation - LLM performance bottleneck")
            else:
                print("   ✅ Good overall performance")
                
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

def test_rag_timing():
    """Test RAG performance specifically"""
    print("\n🔍 Testing RAG performance...")
    print("-" * 60)
    
    # Test different query types
    test_queries = [
        "What is the main topic?",
        "Can you summarize the key points?",
        "What are the important details?",
        "How does this work?",
        "What are the requirements?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query}'")
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/api/chat/stream",
                json={"message": query},
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code == 200:
                # Just get the first token to measure RAG + initial response time
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: ') and 'delta' in line_str:
                            first_token_time = time.time()
                            response_time = (first_token_time - start_time) * 1000
                            print(f"   ⏱️  First token received in: {response_time:.2f}ms")
                            break
            else:
                print(f"   ❌ Failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("AI-Chatbot Timing Analysis")
    print("=" * 60)
    print("This script will help identify performance bottlenecks.")
    print("Make sure your server is running on http://localhost:8000")
    print()
    
    # Run tests
    test_chat_timing()
    test_rag_timing()
    
    print("\n" + "=" * 60)
    print("💡 TIPS FOR OPTIMIZATION:")
    print("   • If RAG search is slow: Consider reducing chunk size or using a faster embedding model")
    print("   • If LLM generation is slow: Consider using a smaller model or optimizing GPU usage")
    print("   • If database operations are slow: Check database indexes and connection pooling")
    print("   • If prompt preparation is slow: Optimize history management and context length")
    print("\n📋 Check your server logs for detailed timing breakdowns!") 