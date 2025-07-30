"""
Enhanced Complex Query Test
Tests the enhanced system with a complex (but not ultra-complex) query.
"""

import sys
import os
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complex_query():
    """Test the enhanced system with a complex query"""
    
    print("🧠 ENHANCED COMPLEX QUERY TEST")
    print("=" * 80)
    
    # A complex query (but not ultra-complex)
    complex_query = """
    What is the average order value for customers who have made more than 2 orders, 
    and show me the breakdown by product category, but only include categories 
    that have at least 5 orders?
    """
    
    print(f"🔍 Testing Complex Query:")
    print(f"   {complex_query}")
    print("-" * 80)
    
    try:
        from enhanced_llm_service import EnhancedLLMService
        from enhanced_sql_integration import enhanced_sql_integration
        
        # Step 1: Query analysis
        print("📊 Step 1: Query Analysis")
        insights = enhanced_sql_integration.get_query_insights(complex_query)
        
        print(f"   Complexity Level: {insights['complexity']['level']}")
        print(f"   Complexity Score: {insights['complexity']['score']}/7")
        print(f"   Estimated Time: {insights['estimated_processing_time']}")
        print(f"   Recommended Approach: {insights['recommended_approach']}")
        
        print(f"\n   Potential Challenges:")
        for challenge in insights['potential_challenges']:
            print(f"   - {challenge}")
        
        # Step 2: Process with enhanced system
        print(f"\n🧠 Step 2: Enhanced Processing")
        start_time = time.time()
        
        enhanced_llm = EnhancedLLMService()
        result = enhanced_llm.generate_complex_sql_response(complex_query, max_iterations=2)
        
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
                print(f"   {result['analysis'][:400]}...")
            
            if result.get('planning'):
                print(f"\n   Query Planning:")
                print(f"   {result['planning'][:400]}...")
            
            if result.get('interpretation'):
                print(f"\n   Business Interpretation:")
                print(f"   {result['interpretation'][:500]}...")
            
            # Show reasoning steps
            reasoning_steps = result.get('reasoning_steps', [])
            if reasoning_steps:
                print(f"\n   Reasoning Steps:")
                for i, step in enumerate(reasoning_steps):
                    print(f"   Step {i+1}: {step.get('sql', 'No SQL generated')[:150]}...")
        
        else:
            print(f"\n   Error: {result.get('error', 'Unknown error')}")
        
        # Step 4: Capability assessment
        print(f"\n🎯 Step 4: Capability Assessment")
        
        capabilities = {
            'Complex Query Analysis': bool(insights.get('complexity')),
            'Chain-of-Thought Reasoning': result.get('success', False),
            'Query Analysis': bool(result.get('analysis')),
            'Query Planning': bool(result.get('planning')),
            'SQL Generation': bool(result.get('sql_query')),
            'Business Interpretation': bool(result.get('interpretation')),
            'Multi-step Processing': len(result.get('reasoning_steps', [])) > 1,
            'Performance': processing_time < 30
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
            print(f"   🎉 EXCELLENT: Enhanced system handles complex queries well!")
        elif success_rate >= 60:
            print(f"   👍 GOOD: Enhanced system shows promise for complex queries")
        elif success_rate >= 40:
            print(f"   ⚠️ FAIR: Enhanced system needs improvement for complex queries")
        else:
            print(f"   ❌ NEEDS WORK: Enhanced system struggles with complex queries")
        
        return result
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_current_vs_enhanced():
    """Compare current system with enhanced system"""
    print(f"\n🔄 COMPARISON: CURRENT vs ENHANCED")
    print("=" * 80)
    
    complex_query = "What is the average order value for customers who have made more than 2 orders?"
    
    # Test current system
    print("Testing Current System...")
    try:
        from backend.services.langchain_sql_service import langchain_sql_service
        current_result = langchain_sql_service.process_query(complex_query)
        current_success = current_result.get('success', False) if current_result else False
        print(f"   Current System: {'✅ Success' if current_success else '❌ Failed'}")
    except Exception as e:
        print(f"   Current System: ❌ Error - {e}")
        current_success = False
    
    # Test enhanced system
    print("Testing Enhanced System...")
    try:
        from enhanced_llm_service import EnhancedLLMService
        enhanced_llm = EnhancedLLMService()
        enhanced_result = enhanced_llm.generate_complex_sql_response(complex_query, max_iterations=1)
        enhanced_success = enhanced_result.get('success', False) if enhanced_result else False
        print(f"   Enhanced System: {'✅ Success' if enhanced_success else '❌ Failed'}")
    except Exception as e:
        print(f"   Enhanced System: ❌ Error - {e}")
        enhanced_success = False
    
    # Comparison
    print(f"\n📊 COMPARISON RESULTS:")
    if enhanced_success and not current_success:
        print(f"   🎉 ENHANCED SYSTEM SUCCESSFUL WHERE CURRENT SYSTEM FAILED!")
    elif enhanced_success and current_success:
        print(f"   👍 Both systems successful, but enhanced system provides more detailed analysis")
    elif not enhanced_success and not current_success:
        print(f"   ⚠️ Both systems failed - query may be too complex")
    else:
        print(f"   ❓ Unexpected result - current system succeeded but enhanced failed")

if __name__ == "__main__":
    # Test complex query
    result = test_complex_query()
    
    # Compare with current system
    test_current_vs_enhanced()
    
    print(f"\n{'='*80}")
    print("🎯 ENHANCED COMPLEX QUERY TEST COMPLETE")
    print("=" * 80) 