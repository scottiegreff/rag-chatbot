#!/usr/bin/env python3
"""
Comprehensive benchmark test script to evaluate TinyLlama 1.1B model performance.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8010"

def test_math_questions():
    """Test mathematical reasoning capabilities."""
    questions = [
        "What is 15 + 27?",
        "Calculate 8 * 9",
        "What is 100 divided by 4?",
        "What is the square root of 16?",
        "What is 2 to the power of 5?"
    ]
    
    print("🧮 Testing Mathematical Reasoning...")
    results = []
    
    for i, question in enumerate(questions, 1):
        try:
            payload = {
                "message": question,
                "session_id": f"math_test_{i}"
            }
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                duration = end_time - start_time
                print(f"✅ Q{i}: {question}")
                print(f"   A: {response_text[:200]}...")
                print(f"   ⏱️  Response time: {duration:.2f}s")
                results.append({"success": True, "duration": duration, "response": response_text})
            else:
                print(f"❌ Q{i}: Failed - {response.status_code}")
                results.append({"success": False, "duration": 0, "response": ""})
                
        except Exception as e:
            print(f"❌ Q{i}: Exception - {e}")
            results.append({"success": False, "duration": 0, "response": ""})
    
    return results

def test_programming_questions():
    """Test programming knowledge and code generation."""
    questions = [
        "Write a Python function to calculate the factorial of a number",
        "What is the difference between a list and a tuple in Python?",
        "How do you reverse a string in Python?",
        "What is recursion in programming?",
        "Write a simple HTML page with a heading and paragraph"
    ]
    
    print("\n💻 Testing Programming Knowledge...")
    results = []
    
    for i, question in enumerate(questions, 1):
        try:
            payload = {
                "message": question,
                "session_id": f"prog_test_{i}"
            }
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                duration = end_time - start_time
                print(f"✅ Q{i}: {question}")
                print(f"   A: {response_text[:200]}...")
                print(f"   ⏱️  Response time: {duration:.2f}s")
                results.append({"success": True, "duration": duration, "response": response_text})
            else:
                print(f"❌ Q{i}: Failed - {response.status_code}")
                results.append({"success": False, "duration": 0, "response": ""})
                
        except Exception as e:
            print(f"❌ Q{i}: Exception - {e}")
            results.append({"success": False, "duration": 0, "response": ""})
    
    return results

def test_general_knowledge():
    """Test general knowledge and factual questions."""
    questions = [
        "Who was the first President of the United States?",
        "What is the largest planet in our solar system?",
        "What year did World War II end?",
        "What is the chemical symbol for gold?",
        "Who wrote 'To Kill a Mockingbird'?"
    ]
    
    print("\n📚 Testing General Knowledge...")
    results = []
    
    for i, question in enumerate(questions, 1):
        try:
            payload = {
                "message": question,
                "session_id": f"knowledge_test_{i}"
            }
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                duration = end_time - start_time
                print(f"✅ Q{i}: {question}")
                print(f"   A: {response_text[:200]}...")
                print(f"   ⏱️  Response time: {duration:.2f}s")
                results.append({"success": True, "duration": duration, "response": response_text})
            else:
                print(f"❌ Q{i}: Failed - {response.status_code}")
                results.append({"success": False, "duration": 0, "response": ""})
                
        except Exception as e:
            print(f"❌ Q{i}: Exception - {e}")
            results.append({"success": False, "duration": 0, "response": ""})
    
    return results

def test_reasoning_questions():
    """Test logical reasoning and problem-solving."""
    questions = [
        "If all roses are flowers and some flowers are red, can we conclude that some roses are red?",
        "A train leaves station A at 2 PM and arrives at station B at 4 PM. If the distance is 120 miles, what is the average speed?",
        "If you have 3 apples and you give away 1, how many do you have left?",
        "What comes next in the sequence: 2, 4, 8, 16, __?",
        "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?"
    ]
    
    print("\n🧠 Testing Logical Reasoning...")
    results = []
    
    for i, question in enumerate(questions, 1):
        try:
            payload = {
                "message": question,
                "session_id": f"reasoning_test_{i}"
            }
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                duration = end_time - start_time
                print(f"✅ Q{i}: {question}")
                print(f"   A: {response_text[:200]}...")
                print(f"   ⏱️  Response time: {duration:.2f}s")
                results.append({"success": True, "duration": duration, "response": response_text})
            else:
                print(f"❌ Q{i}: Failed - {response.status_code}")
                results.append({"success": False, "duration": 0, "response": ""})
                
        except Exception as e:
            print(f"❌ Q{i}: Exception - {e}")
            results.append({"success": False, "duration": 0, "response": ""})
    
    return results

def print_summary(math_results, prog_results, knowledge_results, reasoning_results):
    """Print comprehensive test summary."""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE BENCHMARK RESULTS - Mistral 7B Instruct v0.2")
    print("=" * 80)
    
    # Calculate statistics
    def calculate_stats(results):
        successful = [r for r in results if r["success"]]
        if not successful:
            return {"count": 0, "success_rate": 0, "avg_duration": 0}
        
        avg_duration = sum(r["duration"] for r in successful) / len(successful)
        success_rate = len(successful) / len(results) * 100
        return {
            "count": len(results),
            "success_rate": success_rate,
            "avg_duration": avg_duration
        }
    
    math_stats = calculate_stats(math_results)
    prog_stats = calculate_stats(prog_results)
    knowledge_stats = calculate_stats(knowledge_results)
    reasoning_stats = calculate_stats(reasoning_results)
    
    print(f"🧮 Mathematical Reasoning:")
    print(f"   Questions: {math_stats['count']}, Success Rate: {math_stats['success_rate']:.1f}%, Avg Time: {math_stats['avg_duration']:.2f}s")
    
    print(f"💻 Programming Knowledge:")
    print(f"   Questions: {prog_stats['count']}, Success Rate: {prog_stats['success_rate']:.1f}%, Avg Time: {prog_stats['avg_duration']:.2f}s")
    
    print(f"📚 General Knowledge:")
    print(f"   Questions: {knowledge_stats['count']}, Success Rate: {knowledge_stats['success_rate']:.1f}%, Avg Time: {knowledge_stats['avg_duration']:.2f}s")
    
    print(f"🧠 Logical Reasoning:")
    print(f"   Questions: {reasoning_stats['count']}, Success Rate: {reasoning_stats['success_rate']:.1f}%, Avg Time: {reasoning_stats['avg_duration']:.2f}s")
    
    # Overall statistics
    all_results = math_results + prog_results + knowledge_results + reasoning_results
    overall_successful = [r for r in all_results if r["success"]]
    overall_success_rate = len(overall_successful) / len(all_results) * 100
    overall_avg_duration = sum(r["duration"] for r in overall_successful) / len(overall_successful) if overall_successful else 0
    
    print(f"\n🎯 OVERALL PERFORMANCE:")
    print(f"   Total Questions: {len(all_results)}")
    print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
    print(f"   Average Response Time: {overall_avg_duration:.2f}s")
    
    print(f"\n📝 MODEL ASSESSMENT:")
    if overall_success_rate >= 90:
        print("   🟢 Excellent performance for a 7B model!")
    elif overall_success_rate >= 80:
        print("   🟡 Good performance, typical for a 7B model")
    elif overall_success_rate >= 70:
        print("   🟠 Moderate performance, some limitations")
    else:
        print("   🔴 Limited performance, may need tuning")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   • Current model: Mistral 7B Instruct v0.2 ({len(all_results)} questions tested)")
    print(f"   • Model size: 4.16GB (vs 668MB for TinyLlama 1.1B)")
    print(f"   • Expected improvements: Better reasoning, accuracy, and consistency")

def main():
    print("🚀 Starting Comprehensive Benchmark Test - Mistral 7B Instruct v0.2")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Run all test categories
    math_results = test_math_questions()
    prog_results = test_programming_questions()
    knowledge_results = test_general_knowledge()
    reasoning_results = test_reasoning_questions()
    
    # Print comprehensive summary
    print_summary(math_results, prog_results, knowledge_results, reasoning_results)
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 