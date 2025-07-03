#!/usr/bin/env python3
"""
Test Chain of Thought Reasoning
Demonstrates the automatic detection and application of CoT reasoning
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.llm_service import LLMService

def test_chain_of_thought_detection():
    """Test the Chain of Thought detection logic"""
    
    print("🧠 Testing Chain of Thought Detection...")
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test cases that should trigger CoT
    cot_test_cases = [
        "Calculate 15% of 200",
        "If all roses are flowers and some flowers are red, can we conclude that some roses are red?",
        "Write a function to calculate the factorial of a number",
        "What comes next in the sequence: 2, 4, 8, 16, __?",
        "Step by step, explain how photosynthesis works",
        "Show your work: solve for x in 2x + 5 = 13"
    ]
    
    # Test cases that should NOT trigger CoT
    non_cot_test_cases = [
        "What is the capital of France?",
        "Tell me a joke",
        "How are you today?",
        "What's the weather like?",
        "Can you help me with something?"
    ]
    
    print("\n✅ Testing CoT Detection (should return True):")
    for i, test_case in enumerate(cot_test_cases, 1):
        result = llm_service._should_use_chain_of_thought(test_case)
        print(f"{i}. '{test_case}' -> {result}")
    
    print("\n❌ Testing Non-CoT Detection (should return False):")
    for i, test_case in enumerate(non_cot_test_cases, 1):
        result = llm_service._should_use_chain_of_thought(test_case)
        print(f"{i}. '{test_case}' -> {result}")

def test_chain_of_thought_prompt():
    """Test the Chain of Thought prompt enhancement"""
    
    print("\n🧠 Testing Chain of Thought Prompt Enhancement...")
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test case
    original_message = "Calculate 15% of 200"
    enhanced_message = llm_service._add_chain_of_thought_prompt(original_message)
    
    print(f"Original: {original_message}")
    print(f"Enhanced: {enhanced_message}")

def test_full_cot_integration():
    """Test the full Chain of Thought integration"""
    
    print("\n🧠 Testing Full Chain of Thought Integration...")
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test cases
    test_cases = [
        "What is 25% of 80?",
        "If a train travels 120 miles in 2 hours, what is its average speed?",
        "Write a Python function to check if a number is prime"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_case}'")
        
        # Check if CoT should be used
        should_use_cot = llm_service._should_use_chain_of_thought(test_case)
        print(f"   CoT Detection: {should_use_cot}")
        
        if should_use_cot:
            # Show enhanced prompt
            enhanced = llm_service._add_chain_of_thought_prompt(test_case)
            print(f"   Enhanced Prompt: {enhanced[:100]}...")
            
            # Show full prompt
            full_prompt = llm_service._prepare_prompt(test_case)
            print(f"   Full Prompt: {full_prompt[:200]}...")

if __name__ == "__main__":
    print("🧠 Chain of Thought Reasoning Test")
    print("=" * 50)
    
    try:
        test_chain_of_thought_detection()
        test_chain_of_thought_prompt()
        test_full_cot_integration()
        
        print("\n✅ All Chain of Thought tests completed successfully!")
        print("\n💡 The system will now automatically apply Chain of Thought reasoning to:")
        print("   - Mathematical calculations")
        print("   - Logical reasoning problems")
        print("   - Programming questions")
        print("   - Complex multi-step problems")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 