#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.langchain_sql_service import LangChainSQLService
from backend.services.llm_service import LLMService

def test_sql_flow_debug():
    """Debug the complete SQL processing flow"""
    
    # Initialize services
    llm_service = LLMService()
    sql_service = LangChainSQLService()
    
    # Test query
    query = "what is the total revenue?"
    
    print(f"Testing query: {query}")
    
    # Check if it's a database query
    is_db_query = sql_service.is_database_query(query)
    print(f"Is database query: {is_db_query}")
    
    if is_db_query:
        # Check complexity
        complexity = sql_service._analyze_query_complexity(query)
        print(f"Complexity: {complexity}")
        
        # Process the query
        result = sql_service.process_query(query)
        
        if result:
            print(f"Success: {result.get('success')}")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"SQL Query: {result.get('sql_query', 'No SQL')}")
            print(f"Processing approach: {result.get('processing_approach', 'Unknown')}")
            print(f"Enhanced with results: {result.get('enhanced_with_results', False)}")
            
            # Check if the response contains the table format
            if "**Query Results:**" in result.get('response', ''):
                print("✅ Response contains query results table!")
            else:
                print("❌ Response does not contain query results table")
        else:
            print("❌ No result returned")
    else:
        print("❌ Not recognized as database query")

if __name__ == "__main__":
    test_sql_flow_debug() 