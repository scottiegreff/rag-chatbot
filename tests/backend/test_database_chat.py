#!/usr/bin/env python3
"""
Test script for database query integration with chat system
Tests the ability to ask questions about the PostgreSQL database via chat
"""

import requests
import json

BASE_URL = "http://localhost:8010/api"

def test_database_chat_queries():
    """Test various database-related chat queries"""
    print("Testing Database Chat Integration")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What tables are in the database?",
        "Show me the database schema",
        "How many customers do we have?",
        "What are the sales statistics?",
        "Tell me about customer 1",
        "Show me order details for order 1",
        "What products do we have?",
        "Search for products with 'laptop'",
        "What's the total revenue?",
        "How many orders are pending?"
    ]
    
    session_id = "test-db-chat-session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json={
                "message": query,
                "session_id": session_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result['response'][:200]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("Database chat integration test completed!")

def test_specific_database_queries():
    """Test specific database query patterns"""
    print("\nTesting Specific Database Query Patterns")
    print("=" * 50)
    
    specific_queries = [
        "SELECT COUNT(*) FROM customers",
        "SELECT * FROM products LIMIT 5",
        "SELECT status, COUNT(*) FROM orders GROUP BY status"
    ]
    
    session_id = "test-sql-chat-session"
    
    for i, query in enumerate(specific_queries, 1):
        print(f"\n{i}. Testing SQL: {query}")
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json={
                "message": query,
                "session_id": session_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result['response'][:200]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def main():
    """Run all database chat tests"""
    try:
        test_database_chat_queries()
        test_specific_database_queries()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running on http://localhost:8010")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main() 