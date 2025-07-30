"""
Test Hard Chatbot Questions
This script tests the chatbot with complex business intelligence questions and compares with direct SQL queries.
"""

import requests
import json
import time
from sqlalchemy import create_engine, text
import os

# Database connection
db_params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),  # Use backend database
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

def test_hard_question(question, sql_query, expected_type="currency", description=""):
    """Test a challenging question comparing SQL vs Chatbot"""
    print(f"\n🔍 Testing: {question}")
    if description:
        print(f"   Description: {description}")
    print("-" * 80)
    
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
    """Main test function with hard questions"""
    print("🚀 HARD CHATBOT QUESTIONS TEST")
    print("=" * 80)
    
    # Complex test cases
    test_cases = [
        {
            "question": "What is the revenue per customer on average?",
            "sql_query": """
                SELECT AVG(customer_revenue) as avg_revenue_per_customer
                FROM (
                    SELECT c.id, c.first_name, c.last_name, 
                           COALESCE(SUM(o.total), 0) as customer_revenue
                    FROM customers c
                    LEFT JOIN orders o ON c.id = o.customer_id
                    GROUP BY c.id, c.first_name, c.last_name
                ) customer_revenues
            """,
            "expected_type": "currency",
            "description": "Complex aggregation with subquery and LEFT JOIN"
        },
        {
            "question": "Which category generates the highest revenue?",
            "sql_query": """
                SELECT c.name as category_name, 
                       COALESCE(SUM(oi.quantity * oi.price), 0) as category_revenue
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                LEFT JOIN order_items oi ON p.id = oi.product_id
                GROUP BY c.id, c.name
                ORDER BY category_revenue DESC
                LIMIT 1
            """,
            "expected_type": "currency",
            "description": "Multi-table JOIN with aggregation and ordering"
        },
        {
            "question": "What is the total revenue from completed orders only?",
            "sql_query": """
                SELECT SUM(total) as completed_orders_revenue
                FROM orders 
                WHERE status = 'completed'
            """,
            "expected_type": "currency",
            "description": "Filtered aggregation with WHERE clause"
        },
        {
            "question": "How much revenue comes from orders with more than one item?",
            "sql_query": """
                SELECT COALESCE(SUM(o.total), 0) as multi_item_revenue
                FROM orders o
                WHERE o.id IN (
                    SELECT order_id 
                    FROM order_items 
                    GROUP BY order_id 
                    HAVING COUNT(*) > 1
                )
            """,
            "expected_type": "currency",
            "description": "Subquery with HAVING clause and IN operator"
        },
        {
            "question": "What is the average order value for customers who have made more than one order?",
            "sql_query": """
                SELECT AVG(avg_customer_order) as overall_avg
                FROM (
                    SELECT customer_id, AVG(total) as avg_customer_order
                    FROM orders
                    WHERE customer_id IN (
                        SELECT customer_id
                        FROM orders
                        GROUP BY customer_id
                        HAVING COUNT(*) > 1
                    )
                    GROUP BY customer_id
                ) customer_averages
            """,
            "expected_type": "currency",
            "description": "Nested subqueries with multiple aggregations"
        },
        {
            "question": "What percentage of total revenue comes from the top 3 customers?",
            "sql_query": """
                SELECT ROUND(
                    (top_3_revenue / total_revenue) * 100, 2
                ) as top_3_percentage
                FROM (
                    SELECT 
                        (SELECT COALESCE(SUM(total), 0) FROM orders) as total_revenue,
                        (SELECT COALESCE(SUM(customer_revenue), 0)
                         FROM (
                             SELECT COALESCE(SUM(o.total), 0) as customer_revenue
                             FROM customers c
                             LEFT JOIN orders o ON c.id = o.customer_id
                             GROUP BY c.id
                             ORDER BY customer_revenue DESC
                             LIMIT 3
                         ) top_3) as top_3_revenue
                ) revenue_calc
            """,
            "expected_type": "currency",
            "description": "Complex percentage calculation with multiple subqueries"
        },
        {
            "question": "What is the revenue per product category, ordered from highest to lowest?",
            "sql_query": """
                SELECT c.name as category_name, 
                       COALESCE(SUM(oi.quantity * oi.price), 0) as category_revenue
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                LEFT JOIN order_items oi ON p.id = oi.product_id
                GROUP BY c.id, c.name
                ORDER BY category_revenue DESC
            """,
            "expected_type": "text",
            "description": "Multi-table aggregation with ordering - returns multiple rows"
        },
        {
            "question": "Which customers have spent more than the average customer spending?",
            "sql_query": """
                SELECT c.first_name, c.last_name, 
                       COALESCE(SUM(o.total), 0) as total_spent
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id, c.first_name, c.last_name
                HAVING COALESCE(SUM(o.total), 0) > (
                    SELECT AVG(customer_revenue)
                    FROM (
                        SELECT COALESCE(SUM(o2.total), 0) as customer_revenue
                        FROM customers c2
                        LEFT JOIN orders o2 ON c2.id = o2.customer_id
                        GROUP BY c2.id
                    ) avg_calc
                )
                ORDER BY total_spent DESC
            """,
            "expected_type": "text",
            "description": "HAVING clause with correlated subquery"
        },
        {
            "question": "What is the revenue growth rate between the first and last order?",
            "sql_query": """
                SELECT 
                    CASE 
                        WHEN first_order_revenue > 0 THEN 
                            ROUND(((last_order_revenue - first_order_revenue) / first_order_revenue) * 100, 2)
                        ELSE 0 
                    END as growth_percentage
                FROM (
                    SELECT 
                        (SELECT total FROM orders ORDER BY order_date ASC LIMIT 1) as first_order_revenue,
                        (SELECT total FROM orders ORDER BY order_date DESC LIMIT 1) as last_order_revenue
                ) revenue_comparison
            """,
            "expected_type": "currency",
            "description": "Complex growth calculation with CASE statement"
        },
        {
            "question": "What is the customer lifetime value (CLV) for the top spender?",
            "sql_query": """
                SELECT 
                    c.first_name, 
                    c.last_name,
                    COALESCE(SUM(o.total), 0) as clv,
                    COUNT(DISTINCT o.id) as total_orders,
                    ROUND(COALESCE(SUM(o.total), 0) / NULLIF(COUNT(DISTINCT o.id), 0), 2) as avg_order_value
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id, c.first_name, c.last_name
                ORDER BY clv DESC
                LIMIT 1
            """,
            "expected_type": "currency",
            "description": "Customer lifetime value calculation with multiple metrics"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} HARD TEST {i}/{len(test_cases)} {'='*20}")
        
        success = test_hard_question(
            test_case["question"],
            test_case["sql_query"],
            test_case["expected_type"],
            test_case["description"]
        )
        
        results.append({
            "test": i,
            "question": test_case["question"],
            "description": test_case["description"],
            "success": success
        })
        
        # Small delay between requests
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 HARD QUESTIONS TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"Total Hard Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 PERFECT! All hard tests passed - Chatbot handles complex SQL perfectly!")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} hard tests failed")
        
        print("\nFailed Tests:")
        for result in results:
            if not result["success"]:
                print(f"   ❌ Test {result['test']}: {result['question']}")
                print(f"      Description: {result['description']}")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    main() 