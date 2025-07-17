#!/usr/bin/env python3
"""
Test script to verify dinner list generation.
"""

import requests
import json

def test_dinner_list():
    """Test dinner list generation."""
    
    test_message = "give me a list of dinner ideas for tonight"
    
    print("🍽️ Testing dinner list generation...")
    print(f"📝 Test message: {test_message}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8010/api/chat",
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
            print("\n📄 Full Response:")
            print("=" * 50)
            print(llm_response)
            print("=" * 50)
            
            # Check if the response contains list syntax
            has_unordered_list = "- " in llm_response or "* " in llm_response
            has_ordered_list = any(f"{i}. " in llm_response for i in range(1, 10))
            
            print(f"\n🔍 List Detection:")
            print(f"   • Unordered list markers (- or *): {has_unordered_list}")
            print(f"   • Ordered list markers (1. 2. 3.): {has_ordered_list}")
            
            if has_unordered_list or has_ordered_list:
                print("✅ List syntax detected in response!")
            else:
                print("⚠️ No list syntax detected in response")
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing dinner list: {e}")

if __name__ == "__main__":
    test_dinner_list() 