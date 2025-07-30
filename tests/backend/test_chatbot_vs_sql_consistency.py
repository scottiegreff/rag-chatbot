"""
Test Chatbot vs SQL Consistency
This script tests various queries both directly via SQL and through the chatbot to verify consistency.
"""

import requests
import json
import time
from sqlalchemy import create_engine, text
import os

# Database connection
db_params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5433'),
    'database': os.getenv('DB_NAME', 'ai_chatbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password1234')
}

connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
engine = create_engine(connection_string)

# Chatbot API settings
CHATBOT_URL = "http://localhost:8000/api/chat/stream"
SESSION_URL = "http://localhost:8000/api/session/new"

def get_sql_result(query, description):
    """Execute SQL query directly and return result"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            if query.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                if len(rows) == 1 and len(rows[0]) == 1:
                    return rows[0][0]  # Single value
                else:
                    return rows  # Multiple rows
            else:
                return "Query executed successfully"
    except Exception as e:
        return f"SQL Error: {e}"

def ask_chatbot(question, session_id=None):
    """Ask the chatbot a question and return the response"""
    try:
        # Create new session if not provided
        if not session_id:
            response = requests.post(SESSION_URL)
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get('session_id')
            else:
                return f"Error creating session: {response.status_code}"
        
        # Ask the question
        payload = {
            "message": question,
            "session_id": session_id
        }
        
        response = requests.post(CHATBOT_URL, json=payload, stream=True)
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        # Remove "data: " prefix and parse JSON
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            json_str = line_str[6:]  # Remove "data: " prefix
                            data = json.loads(json_str)
                            
                            # Handle different response types
                            if 'delta' in data:
                                full_response += data['delta']
                            elif 'error' in data:
                                return f"Chatbot Error: {data['error']}"
                            elif 'done' in data:
                                break  # Response is complete
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error parsing line: {e}")
                        continue
            
            return full_response.strip()
        else:
            return f"Chatbot Error: {response.status_code}"
            
    except Exception as e:
        return f"Chatbot Error: {e}"

def extract_number_from_text(text):
    """Extract the first number (especially currency) from text"""
    import re
    
    # Look for currency patterns like $1,234.56 or $1234.56
    currency_pattern = r'\$[\d,]+\.?\d*'
    currency_matches = re.findall(currency_pattern, text)
    
    if currency_matches:
        # Clean up the first currency match
        currency_str = currency_matches[0].replace('$', '').replace(',', '')
        try:
            return float(currency_str)
        except ValueError:
            pass
    
    # Look for any number patterns
    number_pattern = r'[\d,]+\.?\d*'
    number_matches = re.findall(number_pattern, text)
    
    if number_matches:
        try:
            return float(number_matches[0].replace(',', ''))
        except ValueError:
            pass
    
    return None

def test_query_comparison(question, sql_query, expected_type="currency"):
    """Test a specific query comparing SQL vs Chatbot"""
    print(f"\n🔍 Testing: {question}")
    print("-" * 60)
    
    # Get SQL result
    sql_result = get_sql_result(sql_query, question)
    print(f"SQL Query: {sql_query}")
    print(f"SQL Result: {sql_result}")
    
    # Get Chatbot result
    print(f"\nAsking Chatbot: {question}")
    chatbot_response = ask_chatbot(question)
    print(f"Chatbot Response: {chatbot_response}")
    
    # Extract numbers for comparison
    sql_number = None
    chatbot_number = None
    
    if expected_type == "currency":
        if isinstance(sql_result, (int, float)):
            sql_number = float(sql_result)
        elif isinstance(sql_result, str):
            sql_number = extract_number_from_text(sql_result)
        
        chatbot_number = extract_number_from_text(chatbot_response)
    
    # Compare results
    print(f"\n📊 Comparison:")
    print(f"   SQL Number: {sql_number}")
    print(f"   Chatbot Number: {chatbot_number}")
    
    if sql_number is not None and chatbot_number is not None:
        difference = abs(sql_number - chatbot_number)
        if difference < 0.01:
            print(f"   ✅ MATCH: Difference is ${difference:.2f}")
            return True
        else:
            print(f"   ❌ MISMATCH: Difference is ${difference:.2f}")
            return False
    else:
        print(f"   ⚠️  Could not extract comparable numbers")
        return False

def main():
    """Main test function"""
    print("🚀 CHATBOT vs SQL CONSISTENCY TEST")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "question": "What is the total sales?",
            "sql_query": "SELECT SUM(total) FROM orders",
            "expected_type": "currency"
        },
        {
            "question": "What is the total revenue from all orders?",
            "sql_query": "SELECT SUM(total) FROM orders",
            "expected_type": "currency"
        },
        {
            "question": "How much money did customers spend in total?",
            "sql_query": "SELECT COALESCE(SUM(o.total), 0) FROM customers c LEFT JOIN orders o ON c.id = o.customer_id",
            "expected_type": "currency"
        },
        {
            "question": "What is the total amount from order items?",
            "sql_query": "SELECT SUM(quantity * price) FROM order_items",
            "expected_type": "currency"
        },
        {
            "question": "What is the total amount from payments?",
            "sql_query": "SELECT SUM(amount) FROM payments",
            "expected_type": "currency"
        },
        {
            "question": "How many orders are there?",
            "sql_query": "SELECT COUNT(*) FROM orders",
            "expected_type": "number"
        },
        {
            "question": "How many customers do we have?",
            "sql_query": "SELECT COUNT(*) FROM customers",
            "expected_type": "number"
        },
        {
            "question": "What is the average order value?",
            "sql_query": "SELECT AVG(total) FROM orders",
            "expected_type": "currency"
        },
        {
            "question": "Who is the top customer by spending?",
            "sql_query": """
                SELECT c.first_name, c.last_name, COALESCE(SUM(o.total), 0) as total_spent
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id, c.first_name, c.last_name
                ORDER BY total_spent DESC
                LIMIT 1
            """,
            "expected_type": "text"
        },
        {
            "question": "What is the most expensive product?",
            "sql_query": """
                SELECT name, price 
                FROM products 
                ORDER BY price DESC 
                LIMIT 1
            """,
            "expected_type": "text"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} TEST {i}/{len(test_cases)} {'='*20}")
        
        success = test_query_comparison(
            test_case["question"],
            test_case["sql_query"],
            test_case["expected_type"]
        )
        
        results.append({
            "test": i,
            "question": test_case["question"],
            "success": success
        })
        
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 PERFECT! All tests passed - Chatbot and SQL are consistent!")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} tests failed - inconsistencies detected")
        
        print("\nFailed Tests:")
        for result in results:
            if not result["success"]:
                print(f"   ❌ Test {result['test']}: {result['question']}")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    main() 