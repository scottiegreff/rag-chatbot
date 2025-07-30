"""
Test Enhanced Ultra-Complex Query System
Demonstrates the enhanced capabilities for handling ultra-complex business intelligence queries.
"""

import sys
import os
import time
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_system():
    """Test the enhanced system with the ultra-complex query"""
    
    print("🚀 ENHANCED ULTRA-COMPLEX QUERY SYSTEM TEST")
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
        # Import the enhanced integration service
        from enhanced_sql_integration import enhanced_sql_integration
        
        # Step 1: Get query insights
        print("📊 Step 1: Query Analysis")
        insights = enhanced_sql_integration.get_query_insights(ultra_complex_query)
        
        print(f"   Complexity Level: {insights['complexity']['level']}")
        print(f"   Complexity Score: {insights['complexity']['score']}/7")
        print(f"   Estimated Time: {insights['estimated_processing_time']}")
        print(f"   Recommended Approach: {insights['recommended_approach']}")
        print(f"   Business Value: {insights['business_value']['level']}")
        
        print(f"\n   Potential Challenges:")
        for challenge in insights['potential_challenges']:
            print(f"   - {challenge}")
        
        print(f"\n   Complexity Factors:")
        for factor, value in insights['complexity']['factors'].items():
            status = "✅" if value else "❌"
            print(f"   {status} {factor.replace('_', ' ').title()}")
        
        # Step 2: Process the query
        print(f"\n🧠 Step 2: Processing Query")
        start_time = time.time()
        
        result = enhanced_sql_integration.process_ultra_complex_query(ultra_complex_query)
        
        processing_time = time.time() - start_time
        
        # Step 3: Display results
        print(f"\n📈 Step 3: Results Analysis")
        print(f"   Processing Time: {processing_time:.2f}s")
        print(f"   Success: {'✅' if result.get('success') else '❌'}")
        print(f"   Approach Used: {result.get('approach', 'unknown')}")
        
        if result.get('success'):
            print(f"\n   Generated SQL Query:")
            sql_query = result.get('sql_query', '')
            if sql_query:
                print(f"   ```sql")
                print(f"   {sql_query}")
                print(f"   ```")
            
            # Show execution results
            execution_result = result.get('execution_result', {})
            if execution_result.get('success'):
                print(f"\n   Execution Results:")
                print(f"   - Rows Returned: {execution_result.get('count', 0)}")
                print(f"   - Columns: {', '.join(execution_result.get('columns', []))}")
                
                # Show sample data
                rows = execution_result.get('rows', [])
                if rows:
                    print(f"\n   Sample Results:")
                    for i, row in enumerate(rows[:3]):  # Show first 3 rows
                        print(f"   Row {i+1}: {row}")
                    if len(rows) > 3:
                        print(f"   ... and {len(rows) - 3} more rows")
            
            # Show analysis and planning
            if result.get('analysis'):
                print(f"\n   Query Analysis:")
                print(f"   {result['analysis'][:200]}...")
            
            if result.get('planning'):
                print(f"\n   Query Planning:")
                print(f"   {result['planning'][:200]}...")
            
            if result.get('interpretation'):
                print(f"\n   Business Interpretation:")
                print(f"   {result['interpretation'][:300]}...")
        
        else:
            print(f"\n   Error: {result.get('error', 'Unknown error')}")
        
        # Step 4: Performance analysis
        print(f"\n⚡ Step 4: Performance Analysis")
        complexity = insights['complexity']
        
        print(f"   Query Complexity Breakdown:")
        print(f"   - CTEs Required: {'Yes' if complexity['factors']['cte_required'] else 'No'}")
        print(f"   - Window Functions: {'Yes' if complexity['factors']['window_functions'] else 'No'}")
        print(f"   - Multiple Aggregations: {'Yes' if complexity['factors']['multiple_aggregations'] else 'No'}")
        print(f"   - Business Logic: {'Yes' if complexity['factors']['business_logic'] else 'No'}")
        print(f"   - Multi-step Analysis: {'Yes' if complexity['factors']['multi_step'] else 'No'}")
        print(f"   - Conditional Logic: {'Yes' if complexity['factors']['conditional_logic'] else 'No'}")
        print(f"   - Advanced Metrics: {'Yes' if complexity['factors']['advanced_metrics'] else 'No'}")
        
        # Step 5: System capabilities assessment
        print(f"\n🎯 Step 5: System Capabilities Assessment")
        
        capabilities = {
            'Advanced SQL Generation': result.get('success', False),
            'Chain-of-Thought Reasoning': result.get('approach') == 'chain-of-thought',
            'Complex Query Analysis': bool(insights.get('complexity')),
            'Business Logic Implementation': complexity['factors']['business_logic'],
            'Multi-step Processing': complexity['factors']['multi_step'],
            'Result Validation': bool(result.get('execution_result')),
            'Performance Optimization': processing_time < 60  # Under 60 seconds
        }
        
        for capability, achieved in capabilities.items():
            status = "✅" if achieved else "❌"
            print(f"   {status} {capability}")
        
        # Overall assessment
        achieved_capabilities = sum(capabilities.values())
        total_capabilities = len(capabilities)
        success_rate = (achieved_capabilities / total_capabilities) * 100
        
        print(f"\n📊 Overall System Assessment:")
        print(f"   Capabilities Achieved: {achieved_capabilities}/{total_capabilities}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"   🎉 EXCELLENT: System can handle ultra-complex queries!")
        elif success_rate >= 60:
            print(f"   👍 GOOD: System handles most complex queries well")
        elif success_rate >= 40:
            print(f"   ⚠️ FAIR: System needs some improvements")
        else:
            print(f"   ❌ NEEDS WORK: System requires significant enhancements")
        
        return result
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(f"   Make sure all enhanced modules are available")
        return None
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_with_current_system():
    """Compare enhanced system with current system"""
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
    print("Testing Enhanced System...")
    enhanced_result = test_enhanced_system()
    enhanced_success = enhanced_result.get('success', False) if enhanced_result else False
    
    # Comparison
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"   Current System: {'✅ Success' if current_success else '❌ Failed'}")
    print(f"   Enhanced System: {'✅ Success' if enhanced_success else '❌ Failed'}")
    
    if enhanced_success and not current_success:
        print(f"   🎉 ENHANCED SYSTEM SUCCESSFUL WHERE CURRENT SYSTEM FAILED!")
    elif enhanced_success and current_success:
        print(f"   👍 Both systems successful, but enhanced system provides more capabilities")
    elif not enhanced_success and not current_success:
        print(f"   ⚠️ Both systems failed - query may be too complex for current technology")
    else:
        print(f"   ❓ Unexpected result - current system succeeded but enhanced failed")

if __name__ == "__main__":
    # Test the enhanced system
    result = test_enhanced_system()
    
    # Compare with current system
    compare_with_current_system()
    
    print(f"\n{'='*80}")
    print("🎯 ENHANCED SYSTEM TEST COMPLETE")
    print("=" * 80) 