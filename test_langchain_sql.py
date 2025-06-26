#!/usr/bin/env python3
"""
Test script for LangChain SQL Agent
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.langchain_sql_service import langchain_sql_service

async def test_langchain_sql():
    """Test the LangChain SQL Agent with various queries"""
    
    print("🧪 Testing LangChain SQL Agent...")
    
    # Test queries
    test_queries = [
        "How many customers do we have?",
        "Show me the total revenue",
        "List all products",
        "What's the average order value?",
        "How many orders are there?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            result = langchain_sql_service.process_query(query)
            if result and result.get('success'):
                print(f"✅ Success: {result.get('response', 'No response')}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error') if result else 'No result'}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_langchain_sql()) 