#!/usr/bin/env python3
"""
RAG Performance Test Script

This script tests whether the RAG system is causing LLM slowdown
by comparing performance with and without RAG context.
"""

import time
import requests
import json
from datetime import datetime

def test_without_rag():
    """Test LLM performance without any RAG context"""
    print("🧪 Testing LLM Performance WITHOUT RAG")
    print("=" * 60)
    
    test_messages = [
        "Hello, how are you?",
        "What is 2+2?",
        "Tell me a joke",
        "What's the weather like?",
        "Can you help me?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔄 Test {i}: '{message}'")
        start_time = time.time()
        
        try:
            # Use a simple endpoint that bypasses RAG
            response = requests.post(
                "http://localhost:8010/api/test-stream-post",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code == 200:
                # Get first token to measure time to first response
                first_token_received = False
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: ') and 'delta' in line_str:
                            first_token_time = time.time()
                            response_time = (first_token_time - start_time) * 1000
                            print(f"   ⏱️  First token received in: {response_time:.2f}ms")
                            first_token_received = True
                            break
                
                if not first_token_received:
                    print("   ❌ No tokens received")
                    
            else:
                print(f"   ❌ Request failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def test_with_rag():
    """Test LLM performance with RAG context"""
    print("\n🔍 Testing LLM Performance WITH RAG")
    print("=" * 60)
    
    test_messages = [
        "Hello, how are you?",
        "What is 2+2?",
        "Tell me a joke",
        "What's the weather like?",
        "Can you help me?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔄 Test {i}: '{message}'")
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8010/api/chat/stream",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code == 200:
                # Get first token to measure time to first response
                first_token_received = False
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: ') and 'delta' in line_str:
                            first_token_time = time.time()
                            response_time = (first_token_time - start_time) * 1000
                            print(f"   ⏱️  First token received in: {response_time:.2f}ms")
                            first_token_received = True
                            break
                
                if not first_token_received:
                    print("   ❌ No tokens received")
                    
            else:
                print(f"   ❌ Request failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def test_rag_bypass():
    """Test with a modified endpoint that bypasses RAG"""
    print("\n🚀 Testing LLM Performance WITH RAG BYPASS")
    print("=" * 60)
    
    test_messages = [
        "Hello, how are you?",
        "What is 2+2?",
        "Tell me a joke",
        "What's the weather like?",
        "Can you help me?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔄 Test {i}: '{message}'")
        start_time = time.time()
        
        try:
            # Use the chat endpoint with RAG bypass
            response = requests.post(
                "http://localhost:8010/api/chat/stream?bypass_rag=true",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code == 200:
                # Get first token to measure time to first response
                first_token_received = False
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: ') and 'delta' in line_str:
                            first_token_time = time.time()
                            response_time = (first_token_time - start_time) * 1000
                            print(f"   ⏱️  First token received in: {response_time:.2f}ms")
                            first_token_received = True
                            break
                
                if not first_token_received:
                    print("   ❌ No tokens received")
                    
            else:
                print(f"   ❌ Request failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("AI-Chatbot RAG Performance Test")
    print("=" * 60)
    print("This script will help identify if RAG is causing LLM slowdown.")
    print("Make sure your server is running in the correct environment.")
    print()
    
    # Test without RAG (using test endpoint)
    test_without_rag()
    
    # Test with RAG bypass (using chat endpoint with bypass)
    test_rag_bypass()
    
    # Test with RAG (using chat endpoint)
    test_with_rag()
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS:")
    print("   • If all tests are slow: LLM is the bottleneck")
    print("   • If RAG test is much slower than bypass: RAG is causing the issue")
    print("   • If bypass and no-RAG are similar: RAG adds overhead")
    print("   • If bypass is much faster: RAG is interfering with LLM performance")
    print("\n💡 Check server logs for detailed timing information!") 