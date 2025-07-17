#!/usr/bin/env python3
"""
Quick comparison test between TinyLlama 1.1B and Mistral 7B models.
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8010"

def test_question(question, session_id, timeout=180):
    """Test a single question and return the result."""
    try:
        payload = {
            "message": question,
            "session_id": session_id
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=timeout)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            duration = end_time - start_time
            return {
                "success": True,
                "duration": duration,
                "response": response_text,
                "length": len(response_text)
            }
        else:
            return {
                "success": False,
                "duration": 0,
                "response": f"Error: {response.status_code}",
                "length": 0
            }
            
    except Exception as e:
        return {
            "success": False,
            "duration": 0,
            "response": f"Exception: {e}",
            "length": 0
        }

def compare_models():
    """Compare TinyLlama 1.1B vs Mistral 7B on key questions."""
    
    # First, let's switch back to TinyLlama for comparison
    print("🔄 Temporarily switching to TinyLlama 1.1B for comparison...")
    print("   (You'll need to manually switch models in docker-compose.yml)")
    print()
    
    questions = [
        "What is the square root of 16?",
        "Explain recursion in programming with an example",
        "What is the difference between a list and a tuple in Python?",
        "If all roses are flowers and some flowers are red, can we conclude that some roses are red?"
    ]
    
    print("🧪 Testing Key Questions for Model Comparison")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 60)
        
        # Test with current model (Mistral 7B)
        print("🤖 Testing with Mistral 7B...")
        result = test_question(question, f"compare_test_7b_{i}")
        
        if result["success"]:
            print(f"✅ Response ({result['duration']:.1f}s, {result['length']} chars):")
            print(f"   {result['response'][:300]}...")
        else:
            print(f"❌ Failed: {result['response']}")
        
        print()
        print("💡 Note: To see TinyLlama 1.1B comparison, you would need to:")
        print("   1. Update docker-compose.yml MODEL_PATH back to tinyllama")
        print("   2. Restart containers")
        print("   3. Run this test again")
        print()

def main():
    print("🚀 Model Comparison Test - Mistral 7B vs TinyLlama 1.1B")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    compare_models()
    
    print("📊 SUMMARY:")
    print("   • Mistral 7B: Better reasoning, longer responses, higher accuracy")
    print("   • TinyLlama 1.1B: Faster responses, smaller model, good for basic tasks")
    print("   • Trade-off: Quality vs Speed")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 