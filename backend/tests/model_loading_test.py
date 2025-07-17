#!/usr/bin/env python3
"""
Model Loading Test Script

This script tests whether the LLM and RAG models are being loaded once
or multiple times during the application lifecycle.
"""

import time
import requests
import json
from datetime import datetime

def test_model_loading():
    """Test if models are loaded once or multiple times"""
    print("🧪 Testing Model Loading Behavior")
    print("=" * 60)
    
    # Test multiple requests to see if models are reloaded
    test_messages = [
        "Hello, how are you?",
        "What is the weather like?",
        "Can you help me with a question?",
        "Tell me a joke",
        "What is 2+2?"
    ]
    
    print("📝 Making 5 consecutive requests to test model loading...")
    print("-" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔄 Request {i}: '{message}'")
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
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS:")
    print("   • If first request is slow (>10s) but subsequent requests are fast (<2s):")
    print("     ✅ Models are loaded once and cached properly")
    print("   • If all requests are slow (>10s):")
    print("     ❌ Models are being reloaded on each request")
    print("   • If requests get progressively slower:")
    print("     ⚠️  Memory leak or resource exhaustion")
    print("\n💡 Check the server logs for detailed loading information!")

def test_service_initialization():
    """Test service initialization timing"""
    print("\n🔧 Testing Service Initialization")
    print("=" * 60)
    
    # Test the test endpoint to see initialization logs
    try:
        response = requests.get("http://localhost:8010/test")
        if response.status_code == 200:
            print("✅ Server is running and responding")
            print("📋 Check server logs for service initialization timing")
        else:
            print(f"❌ Server test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("💡 Make sure the server is running on http://localhost:8010")

if __name__ == "__main__":
    print("AI-Chatbot Model Loading Test")
    print("=" * 60)
    print("This script will help identify if models are being loaded once or multiple times.")
    print("Make sure your server is running with --log-level info")
    print()
    
    test_service_initialization()
    test_model_loading()
    
    print("\n" + "=" * 60)
    print("🔍 NEXT STEPS:")
    print("   1. Check server logs for '🔄 Initializing' messages")
    print("   2. Look for multiple '🎉 Model loaded successfully' messages")
    print("   3. Compare timing between first and subsequent requests")
    print("   4. If models are reloading, check for singleton pattern issues") 