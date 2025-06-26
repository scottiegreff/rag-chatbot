#!/usr/bin/env python3
"""
Test script to verify markdown list generation with the updated system instruction.
"""

import requests
import json

def test_list_generation():
    """Test if the LLM generates proper markdown lists."""
    
    # Test message that should trigger a list response
    test_message = "Please provide a markdown-formatted unordered list of 5 programming languages."
    
    print("🧪 Testing markdown list generation...")
    print(f"📝 Test message: {test_message}")
    print("-" * 50)
    
    try:
        # Send request to the chat endpoint
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "message": test_message
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get("response", "")
            
            print("✅ Response received successfully!")
            print(f"📊 Response length: {len(llm_response)} characters")
            print("\n📄 Raw LLM Response:")
            print("=" * 50)
            print(repr(llm_response))  # Show raw representation to see any hidden characters
            print("=" * 50)
            print("\n📄 Formatted Response:")
            print("-" * 30)
            print(llm_response)
            print("-" * 30)
            
            # Check if the response contains markdown list syntax
            has_unordered_list = "- " in llm_response or "* " in llm_response
            has_ordered_list = any(f"{i}. " in llm_response for i in range(1, 10))
            
            print(f"\n🔍 List Detection:")
            print(f"   • Unordered list markers (- or *): {has_unordered_list}")
            print(f"   • Ordered list markers (1. 2. 3.): {has_ordered_list}")
            
            if has_unordered_list or has_ordered_list:
                print("✅ Markdown list syntax detected in response!")
            else:
                print("⚠️ No markdown list syntax detected in response")
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing list generation: {e}")

def test_simple_list():
    """Test with a simpler prompt to see if the issue is with complexity."""
    
    test_message = "List 3 colors"
    
    print("\n🧪 Testing simple list generation...")
    print(f"📝 Test message: {test_message}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "message": test_message
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get("response", "")
            
            print("✅ Response received successfully!")
            print(f"📊 Response length: {len(llm_response)} characters")
            print("\n📄 Raw Response:")
            print(repr(llm_response))
            print("\n📄 Formatted Response:")
            print(llm_response)
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing simple list: {e}")

if __name__ == "__main__":
    test_list_generation()
    test_simple_list() 