#!/usr/bin/env python3
"""
Simple debug script to test chat functionality
"""

import requests
import time
import json

def test_chat():
    print("🧪 Testing basic chat functionality...")
    
    # Test 1: Simple request
    print("📤 Sending simple chat request...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat/stream",
            json={"message": "What is the capital of France?", "session_id": "debug-test"},
            timeout=30,
            stream=True
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("📥 Reading response...")
            tokens = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    print(f"📄 Line: {line_str}")
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str != '{"end": true}':
                            try:
                                data = json.loads(data_str)
                                if 'delta' in data:
                                    tokens.append(data['delta'])
                            except json.JSONDecodeError:
                                continue
                        else:
                            break
            
            end_time = time.time()
            print(f"✅ Completed in {end_time - start_time:.2f}s")
            print(f"📊 Generated {len(tokens)} tokens")
            print(f"📝 Response: {''.join(tokens)}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_chat() 