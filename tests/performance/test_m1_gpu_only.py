#!/usr/bin/env python3
"""
Test M1 GPU Performance Only - Assumes backend is already running
"""

import requests
import json
import time
from datetime import datetime

def test_m1_gpu():
    """Test M1 GPU performance"""
    print("🧪 Testing M1 GPU Performance...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Simple query
    print("📝 Test 1: Simple query")
    start_time = time.time()
    response = requests.post(
        f"{base_url}/api/chat/stream",
        json={"message": "What is the capital of France?", "session_id": "m1-test-simple"},
        timeout=30,
        stream=True
    )
    
    if response.status_code == 200:
        tokens = []
        first_token_time = None
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str != '{"end": true}':
                        try:
                            data = json.loads(data_str)
                            if 'delta' in data:
                                tokens.append(data['delta'])
                                if first_token_time is None:
                                    first_token_time = time.time()
                        except json.JSONDecodeError:
                            continue
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        first_token_latency = (first_token_time - start_time) * 1000 if first_token_time else 0
        generation_time = (end_time - first_token_time) * 1000 if first_token_time else 0
        tokens_per_second = len(tokens) / (generation_time / 1000) if generation_time > 0 else 0
        
        print(f"✅ Success!")
        print(f"📊 Total Time: {total_time:.1f}ms")
        print(f"📊 First Token Latency: {first_token_latency:.1f}ms")
        print(f"📊 Generation Time: {generation_time:.1f}ms")
        print(f"📊 Tokens: {len(tokens)}")
        print(f"📊 Tokens/Second: {tokens_per_second:.2f}")
        print(f"📄 Response: {''.join(tokens)[:100]}...")
    else:
        print(f"❌ Failed: HTTP {response.status_code}")
    
    print("=" * 50)
    
    # Test 2: RAG query
    print("📚 Test 2: RAG query")
    start_time = time.time()
    response = requests.post(
        f"{base_url}/api/chat/stream",
        json={"message": "Tell me about Cody and Scott's adventures at FCIAS", "session_id": "m1-test-rag"},
        timeout=30,
        stream=True
    )
    
    if response.status_code == 200:
        tokens = []
        first_token_time = None
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str != '{"end": true}':
                        try:
                            data = json.loads(data_str)
                            if 'delta' in data:
                                tokens.append(data['delta'])
                                if first_token_time is None:
                                    first_token_time = time.time()
                        except json.JSONDecodeError:
                            continue
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        first_token_latency = (first_token_time - start_time) * 1000 if first_token_time else 0
        generation_time = (end_time - first_token_time) * 1000 if first_token_time else 0
        tokens_per_second = len(tokens) / (generation_time / 1000) if generation_time > 0 else 0
        
        print(f"✅ Success!")
        print(f"📊 Total Time: {total_time:.1f}ms")
        print(f"📊 First Token Latency: {first_token_latency:.1f}ms")
        print(f"📊 Generation Time: {generation_time:.1f}ms")
        print(f"📊 Tokens: {len(tokens)}")
        print(f"📊 Tokens/Second: {tokens_per_second:.2f}")
        print(f"📄 Response: {''.join(tokens)[:100]}...")
    else:
        print(f"❌ Failed: HTTP {response.status_code}")
    
    print("=" * 50)
    print("🎉 M1 GPU tests completed!")

if __name__ == "__main__":
    test_m1_gpu() 