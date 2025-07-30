#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.langchain_sql_service import LangChainSQLService
from backend.services.llm_service import LLMService

def test_sql_flow():
    """Test the complete SQL processing flow"""
    
    # Initialize services
    llm_service = LLMService()
    sql_service = LangChainSQLService()
    
    # Test query
    query = "how many products do we have?"
    
    print(f"Testing query: {query}")
    
    # Process the query
    result = sql_service.process_query(query)
    
    if result:
        print(f"Success: {result.get('success')}")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"SQL Query: {result.get('sql_query', 'No SQL')}")
        print(f"Enhanced with results: {result.get('enhanced_with_results', False)}")
        
        # Check if the response contains the table format
        if "**Query Results:**" in result.get('response', ''):
            print("✅ Response contains query results table!")
        else:
            print("❌ Response does not contain query results table")
    else:
        print("❌ No result returned")

if __name__ == "__main__":
    test_sql_flow() 