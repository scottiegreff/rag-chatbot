"""
Basic Enhanced System Test
Simple test to check if enhanced components can be imported and initialized.
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_imports():
    """Test if enhanced components can be imported"""
    
    print("🔧 BASIC ENHANCED SYSTEM TEST")
    print("=" * 80)
    
    tests = []
    
    # Test 1: Enhanced LLM Service
    try:
        from enhanced_llm_service import EnhancedLLMService
        enhanced_llm = EnhancedLLMService()
        print("✅ Enhanced LLM Service: Imported and initialized successfully")
        tests.append(True)
    except Exception as e:
        print(f"❌ Enhanced LLM Service: {e}")
        tests.append(False)
    
    # Test 2: Enhanced SQL Context Builder
    try:
        from enhanced_sql_context_builder import EnhancedSQLContextBuilder
        context_builder = EnhancedSQLContextBuilder()
        print("✅ Enhanced SQL Context Builder: Imported and initialized successfully")
        tests.append(True)
    except Exception as e:
        print(f"❌ Enhanced SQL Context Builder: {e}")
        tests.append(False)
    
    # Test 3: Enhanced SQL Agent Config
    try:
        from enhanced_sql_agent_config import AdvancedSQLAgent
        print("✅ Enhanced SQL Agent Config: Imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"❌ Enhanced SQL Agent Config: {e}")
        tests.append(False)
    
    # Test 4: Enhanced SQL Integration
    try:
        from enhanced_sql_integration import enhanced_sql_integration
        print("✅ Enhanced SQL Integration: Imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"❌ Enhanced SQL Integration: {e}")
        tests.append(False)
    
    # Test 5: Test a simple query analysis
    try:
        from enhanced_sql_integration import enhanced_sql_integration
        simple_query = "What is the total revenue?"
        insights = enhanced_sql_integration.get_query_insights(simple_query)
        print("✅ Query Analysis: Working successfully")
        print(f"   Complexity: {insights['complexity']['level']}")
        print(f"   Score: {insights['complexity']['score']}/7")
        tests.append(True)
    except Exception as e:
        print(f"❌ Query Analysis: {e}")
        tests.append(False)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    successful_tests = sum(tests)
    total_tests = len(tests)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"   Tests Passed: {successful_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"   🎉 EXCELLENT: Enhanced system components are working!")
    elif success_rate >= 60:
        print(f"   👍 GOOD: Most enhanced components are working")
    elif success_rate >= 40:
        print(f"   ⚠️ FAIR: Some enhanced components need fixes")
    else:
        print(f"   ❌ NEEDS WORK: Most enhanced components have issues")
    
    return tests

def test_simple_chain_of_thought():
    """Test a simple chain-of-thought query"""
    
    print(f"\n🧠 SIMPLE CHAIN-OF-THOUGHT TEST")
    print("=" * 80)
    
    try:
        from enhanced_llm_service import EnhancedLLMService
        
        enhanced_llm = EnhancedLLMService()
        
        # Simple query to test
        simple_query = "What is the total number of customers?"
        
        print(f"Testing query: {simple_query}")
        
        # Test the chain-of-thought approach
        result = enhanced_llm.generate_complex_sql_response(simple_query, max_iterations=1)
        
        if result.get('success'):
            print("✅ Chain-of-thought processing: Successful")
            print(f"   SQL Generated: {bool(result.get('sql_query'))}")
            print(f"   Analysis: {bool(result.get('analysis'))}")
            print(f"   Planning: {bool(result.get('planning'))}")
            print(f"   Interpretation: {bool(result.get('interpretation'))}")
            return True
        else:
            print(f"❌ Chain-of-thought processing: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Chain-of-thought test error: {e}")
        return False

if __name__ == "__main__":
    # Test imports and initialization
    import_results = test_enhanced_imports()
    
    # Test simple chain-of-thought
    chain_of_thought_result = test_simple_chain_of_thought()
    
    print(f"\n{'='*80}")
    print("🎯 BASIC ENHANCED SYSTEM TEST COMPLETE")
    print("=" * 80) 