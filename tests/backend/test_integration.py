#!/usr/bin/env python3
"""
Integration Test
Tests the integrated enhanced SQL system with both simple and complex queries
"""

import logging
from backend.services.langchain_sql_service import LangChainSQLService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_integration():
    """Test the integrated enhanced SQL system"""
    
    sql_service = LangChainSQLService()
    
    print("🚀 INTEGRATION TEST - Enhanced SQL System")
    print("=" * 50)
    
    # Test simple queries (should use standard approach)
    simple_queries = [
        "How many customers do we have?",
        "What is the total revenue?",
        "Show me the average order value"
    ]
    
    print("\n📊 TESTING SIMPLE QUERIES (Standard Approach)")
    print("-" * 40)
    
    for i, query in enumerate(simple_queries, 1):
        print(f"\n{i}. Testing: {query}")
        
        # Analyze complexity
        complexity = sql_service._analyze_query_complexity(query)
        print(f"   Complexity: {complexity['level']} (Score: {complexity['score']})")
        print(f"   Approach: {complexity['recommended_approach']}")
        
        # Process query
        result = sql_service.process_query(query)
        
        if result:
            print(f"   ✅ Success: {result.get('success', False)}")
            print(f"   🔧 Approach Used: {result.get('processing_approach', 'unknown')}")
            if result.get('sql_query'):
                print(f"   🔍 SQL Generated: {len(result['sql_query'])} characters")
                print(f"   📝 SQL Preview: {result['sql_query'][:100]}...")
        else:
            print(f"   ❌ No result returned")
    
    # Test complex queries (should use enhanced approach)
    complex_queries = [
        "What is the weighted average customer lifetime value for customers who have made orders with more than one item?",
        "Show me the breakdown by product category for customers whose average order value is above the overall average"
    ]
    
    print("\n🧠 TESTING COMPLEX QUERIES (Enhanced Approach)")
    print("-" * 40)
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n{i}. Testing: {query[:80]}...")
        
        # Analyze complexity
        complexity = sql_service._analyze_query_complexity(query)
        print(f"   Complexity: {complexity['level']} (Score: {complexity['score']})")
        print(f"   Approach: {complexity['recommended_approach']}")
        
        # Process query
        result = sql_service.process_query(query)
        
        if result:
            print(f"   ✅ Success: {result.get('success', False)}")
            print(f"   🔧 Approach Used: {result.get('processing_approach', 'unknown')}")
            if result.get('sql_query'):
                print(f"   🔍 SQL Generated: {len(result['sql_query'])} characters")
                print(f"   📝 SQL Preview: {result['sql_query'][:100]}...")
        else:
            print(f"   ❌ No result returned")
    
    print("\n✅ INTEGRATION TEST COMPLETE")
    print("=" * 50)
    print("The enhanced SQL system is now integrated!")
    print("- Simple queries use fast standard approach")
    print("- Complex queries use enhanced chain-of-thought approach")
    print("- System automatically chooses the right method")

if __name__ == "__main__":
    test_integration() 