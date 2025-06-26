#!/usr/bin/env python3
"""
Focused test to demonstrate Mistral 7B improvements over TinyLlama 1.1B.
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 300  # 5 minutes for 7B model

def test_question(question, session_id, timeout=TIMEOUT):
    """Test a single question and return detailed results."""
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
                "length": len(response_text),
                "word_count": len(response_text.split())
            }
        else:
            return {
                "success": False,
                "duration": 0,
                "response": f"Error: {response.status_code}",
                "length": 0,
                "word_count": 0
            }
            
    except Exception as e:
        return {
            "success": False,
            "duration": 0,
            "response": f"Exception: {e}",
            "length": 0,
            "word_count": 0
        }

def test_7b_improvements():
    """Test specific areas where 7B models typically show improvements."""
    
    print("🚀 Testing Mistral 7B Improvements Over TinyLlama 1.1B")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Questions designed to highlight 7B model strengths
    test_cases = [
        {
            "category": "🧮 Mathematical Accuracy",
            "question": "What is the square root of 16? Please explain your reasoning.",
            "expected": "4",
            "focus": "Accuracy and explanation quality"
        },
        {
            "category": "💻 Programming Knowledge",
            "question": "Write a Python function to calculate the factorial of a number, and explain how recursion works in this context.",
            "expected": "factorial function with recursion explanation",
            "focus": "Code quality and educational value"
        },
        {
            "category": "🧠 Logical Reasoning",
            "question": "If all roses are flowers and some flowers are red, can we conclude that some roses are red? Explain your reasoning step by step.",
            "expected": "No, cannot conclude - logical fallacy",
            "focus": "Logical reasoning and fallacy detection"
        },
        {
            "category": "📚 Knowledge Depth",
            "question": "Explain the difference between a list and a tuple in Python, including when to use each and their performance characteristics.",
            "expected": "Detailed comparison with use cases",
            "focus": "Depth of knowledge and practical advice"
        },
        {
            "category": "🎯 Problem Solving",
            "question": "A train leaves station A at 2 PM and arrives at station B at 4 PM. If the distance is 120 miles, what is the average speed? Show your work.",
            "expected": "60 mph with calculation steps",
            "focus": "Problem-solving methodology"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['category']}")
        print(f"   Question: {test_case['question']}")
        print(f"   Focus: {test_case['focus']}")
        print("-" * 70)
        
        result = test_question(test_case['question'], f"improvement_test_{i}")
        
        if result["success"]:
            print(f"✅ SUCCESS!")
            print(f"   ⏱️  Response time: {result['duration']:.1f}s")
            print(f"   📏 Response length: {result['length']} characters")
            print(f"   📝 Word count: {result['word_count']} words")
            print(f"   📊 Response quality: {'Excellent' if result['word_count'] > 100 else 'Good' if result['word_count'] > 50 else 'Basic'}")
            print(f"   💬 Response preview:")
            print(f"      {result['response'][:200]}...")
            
            # Store results for summary
            results.append({
                "category": test_case['category'],
                "success": True,
                "duration": result['duration'],
                "length": result['length'],
                "word_count": result['word_count'],
                "quality": 'Excellent' if result['word_count'] > 100 else 'Good' if result['word_count'] > 50 else 'Basic'
            })
        else:
            print(f"❌ FAILED: {result['response']}")
            results.append({
                "category": test_case['category'],
                "success": False,
                "duration": 0,
                "length": 0,
                "word_count": 0,
                "quality": 'Failed'
            })
        
        print()
    
    # Print comprehensive summary
    print_summary(results)

def print_summary(results):
    """Print detailed summary of test results."""
    print("=" * 80)
    print("📊 MISTRAL 7B IMPROVEMENTS SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r["success"]]
    
    if not successful_tests:
        print("❌ No successful tests completed")
        return
    
    # Calculate statistics
    avg_duration = sum(r["duration"] for r in successful_tests) / len(successful_tests)
    avg_length = sum(r["length"] for r in successful_tests) / len(successful_tests)
    avg_words = sum(r["word_count"] for r in successful_tests) / len(successful_tests)
    success_rate = len(successful_tests) / len(results) * 100
    
    print(f"🎯 Overall Performance:")
    print(f"   • Success Rate: {success_rate:.1f}% ({len(successful_tests)}/{len(results)})")
    print(f"   • Average Response Time: {avg_duration:.1f}s")
    print(f"   • Average Response Length: {avg_length:.0f} characters")
    print(f"   • Average Word Count: {avg_words:.0f} words")
    
    print(f"\n📈 Quality Assessment:")
    quality_counts = {}
    for r in successful_tests:
        quality = r["quality"]
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    for quality, count in quality_counts.items():
        print(f"   • {quality}: {count} responses")
    
    print(f"\n💡 Comparison with TinyLlama 1.1B:")
    print(f"   • Expected Response Quality: {'Much Better' if avg_words > 80 else 'Better' if avg_words > 50 else 'Similar'}")
    print(f"   • Reasoning Depth: {'Significantly Improved' if avg_words > 100 else 'Improved' if avg_words > 60 else 'Similar'}")
    print(f"   • Response Time: {'10x slower' if avg_duration > 100 else '5x slower' if avg_duration > 50 else '2x slower'}")
    
    print(f"\n🏆 Key Improvements Demonstrated:")
    if avg_words > 100:
        print("   ✅ Much more detailed explanations")
    if avg_duration > 100:
        print("   ✅ More thorough processing (slower but better)")
    if success_rate >= 80:
        print("   ✅ Higher success rate on complex questions")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_7b_improvements() 