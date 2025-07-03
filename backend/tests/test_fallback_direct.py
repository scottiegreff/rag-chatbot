"""
Test fallback query directly
"""

import sys
import os

# Set environment variables to match Docker container
os.environ['DB_HOST'] = 'postgres'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'fci_chatbot'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'password1234'

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.langchain_sql_service import langchain_sql_service

def test_fallback():
    """Test the fallback query directly"""
    try:
        # Test orders query
        result = langchain_sql_service._fallback_query("How many orders do we have?")
        print(f"Orders query result: {result}")
        
        # Test revenue query
        result2 = langchain_sql_service._fallback_query("What is our total revenue?")
        print(f"Revenue query result: {result2}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fallback() 