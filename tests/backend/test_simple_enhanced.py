"""
Simple Enhanced System Test
Tests the chain-of-thought approach for complex SQL queries without complex agent integration.
"""

import sys
import os
import time
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chain_of_thought_approach():
    """Test the chain-of-thought approach for complex queries"""
    
    print("🧠 CHAIN-OF-THOUGHT ENHANCED SYSTEM TEST")
    print("=" * 80)
    
    # The ultra-complex query
    ultra_complex_query = """
    What is the weighted average customer lifetime value (CLV) for customers who have made orders with more than one item, 
    where the weighting is based on their total order count, and only include customers whose average order value is above 
    the overall average order value, and show me the breakdown by product category for these customers, 
    but only for categories that contribute more than 10% to the total revenue of these high-value customers?
    """
    
    print(f"🔍 Testing Ultra-Complex Query:")
    print(f"   {ultra_complex_query}")
    print("-" * 80)
    
    try:
        # Import the enhanced LLM service directly
        from enhanced_llm_service import EnhancedLLMService
        
        # Initialize the enhanced service
        enhanced_llm = EnhancedLLMService()
        
        print("📊 Step 1: Query Analysis")
        print("   Analyzing query complexity...")
        
        # Analyze complexity manually
        query_lower = ultra_complex_query.lower()
        complexity_factors = {
            'cte_required': any(keyword in query_lower for keyword in ['weighted', 'lifetime value', 'clv', 'breakdown']),
            'window_functions': any(keyword in query_lower for keyword in ['percentage', 'rank', 'growth rate']),
            'multiple_aggregations': query_lower.count('average') + query_lower.count('sum') + query_lower.count('count') > 2,
            'business_logic': any(keyword in query_lower for keyword in ['contribute more than', 'above average', 'high-value']),
            'multi_step': len(ultra_complex_query.split(',')) > 3,
            'conditional_logic': any(keyword in query_lower for keyword in ['if', 'when', 'case', 'conditional']),
            'advanced_metrics': any(keyword in query_lower for keyword in ['lifetime value', 'revenue contribution', 'customer segmentation', 'weighted average'])
        }
        
        complexity_score = sum(complexity_factors.values())
        level = 'ultra-high' if complexity_score >= 5 else 'high' if complexity_score >= 4 else 'medium' if complexity_score >= 2 else 'low'
        
        print(f"   Complexity Level: {level}")
        print(f"   Complexity Score: {complexity_score}/7")
        print(f"   Estimated Time: 30-60 seconds (ultra-complex)")
        
        print(f"\n   Complexity Factors:")
        for factor, value in complexity_factors.items():
            status = "✅" if value else "❌"
            print(f"   {status} {factor.replace('_', ' ').title()}")
        
        # Step 2: Process with chain-of-thought
        print(f"\n🧠 Step 2: Chain-of-Thought Processing")
        start_time = time.time()
        
        print("   Starting chain-of-thought reasoning...")
        result = enhanced_llm.generate_complex_sql_response(ultra_complex_query, max_iterations=3)
        
        processing_time = time.time() - start_time
        
        # Step 3: Display results
        print(f"\n📈 Step 3: Results Analysis")
        print(f"   Processing Time: {processing_time:.2f}s")
        print(f"   Success: {'✅' if result.get('success') else '❌'}")
        
        if result.get('success'):
            print(f"\n   Generated SQL Query:")
            sql_query = result.get('sql_query', '')
            if sql_query:
                print(f"   ```sql")
                print(f"   {sql_query}")
                print(f"   ```")
            
            # Show analysis and planning
            if result.get('analysis'):
                print(f"\n   Query Analysis:")
                print(f"   {result['analysis'][:300]}...")
            
            if result.get('planning'):
                print(f"\n   Query Planning:")
                print(f"   {result['planning'][:300]}...")
            
            if result.get('interpretation'):
                print(f"\n   Business Interpretation:")
                print(f"   {result['interpretation'][:400]}...")
            
            # Show reasoning steps
            reasoning_steps = result.get('reasoning_steps', [])
            if reasoning_steps:
                print(f"\n   Reasoning Steps:")
                for i, step in enumerate(reasoning_steps):
                    print(f"   Step {i+1}: {step.get('sql', 'No SQL generated')[:100]}...")
        
        else:
            print(f"\n   Error: {result.get('error', 'Unknown error')}")
        
        # Step 4: Capability assessment
        print(f"\n🎯 Step 4: Capability Assessment")
        
        capabilities = {
            'Chain-of-Thought Reasoning': result.get('success', False),
            'Query Analysis': bool(result.get('analysis')),
            'Query Planning': bool(result.get('planning')),
            'SQL Generation': bool(result.get('sql_query')),
            'Business Interpretation': bool(result.get('interpretation')),
            'Multi-step Processing': len(result.get('reasoning_steps', [])) > 1,
            'Performance': processing_time < 60
        }
        
        for capability, achieved in capabilities.items():
            status = "✅" if achieved else "❌"
            print(f"   {status} {capability}")
        
        # Overall assessment
        achieved_capabilities = sum(capabilities.values())
        total_capabilities = len(capabilities)
        success_rate = (achieved_capabilities / total_capabilities) * 100
        
        print(f"\n📊 Overall Assessment:")
        print(f"   Capabilities Achieved: {achieved_capabilities}/{total_capabilities}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"   🎉 EXCELLENT: Chain-of-thought approach works well!")
        elif success_rate >= 60:
            print(f"   👍 GOOD: Chain-of-thought approach shows promise")
        elif success_rate >= 40:
            print(f"   ⚠️ FAIR: Chain-of-thought approach needs improvement")
        else:
            print(f"   ❌ NEEDS WORK: Chain-of-thought approach requires significant enhancement")
        
        return result
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(f"   Make sure enhanced_llm_service.py is available")
        return None
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_current_system_comparison():
    """Test current system for comparison"""
    print(f"\n🔄 COMPARISON WITH CURRENT SYSTEM")
    print("=" * 80)
    
    # Test current system
    print("Testing Current System...")
    try:
        from test_ultimate_hard_question import test_ultimate_question
        current_result = test_ultimate_question()
        current_success = current_result
    except Exception as e:
        print(f"Current system error: {e}")
        current_success = False
    
    # Test enhanced system
    print("Testing Enhanced Chain-of-Thought System...")
    enhanced_result = test_chain_of_thought_approach()
    enhanced_success = enhanced_result.get('success', False) if enhanced_result else False
    
    # Comparison
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"   Current System: {'✅ Success' if current_success else '❌ Failed'}")
    print(f"   Enhanced Chain-of-Thought: {'✅ Success' if enhanced_success else '❌ Failed'}")
    
    if enhanced_success and not current_success:
        print(f"   🎉 ENHANCED SYSTEM SUCCESSFUL WHERE CURRENT SYSTEM FAILED!")
    elif enhanced_success and current_success:
        print(f"   👍 Both systems successful, but enhanced system provides more capabilities")
    elif not enhanced_success and not current_success:
        print(f"   ⚠️ Both systems failed - query may be too complex for current technology")
    else:
        print(f"   ❓ Unexpected result - current system succeeded but enhanced failed")

if __name__ == "__main__":
    # Test the enhanced chain-of-thought system
    result = test_chain_of_thought_approach()
    
    # Compare with current system
    test_current_system_comparison()
    
    print(f"\n{'='*80}")
    print("🎯 ENHANCED CHAIN-OF-THOUGHT TEST COMPLETE")
    print("=" * 80) 