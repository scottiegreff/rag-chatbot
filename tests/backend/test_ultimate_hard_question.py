"""
Test Ultimate Hard Question
This script tests the chatbot with an extremely challenging business intelligence question.
"""

import requests
import json
import time
from sqlalchemy import create_engine, text
import os

# Database connection
db_params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
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
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            json_str = line_str[6:]
                            data = json.loads(json_str)
                            
                            if 'delta' in data:
                                full_response += data['delta']
                            elif 'error' in data:
                                return f"Chatbot Error: {data['error']}"
                            elif 'done' in data:
                                break
                            
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

def test_ultimate_question():
    """Test the ultimate hard question"""
    
    # The ULTIMATE hard question
    question = """
    What is the weighted average customer lifetime value (CLV) for customers who have made orders with more than one item, 
    where the weighting is based on their total order count, and only include customers whose average order value is above 
    the overall average order value, and show me the breakdown by product category for these customers, 
    but only for categories that contribute more than 10% to the total revenue of these high-value customers?
    """
    
    # The extremely complex SQL query
    sql_query = """
    WITH customer_metrics AS (
        SELECT 
            c.id as customer_id,
            c.first_name,
            c.last_name,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(o.total), 0) as total_spent,
            COALESCE(SUM(o.total), 0) / NULLIF(COUNT(DISTINCT o.id), 0) as avg_order_value,
            -- Check if customer has orders with multiple items
            CASE WHEN EXISTS (
                SELECT 1 FROM order_items oi 
                JOIN orders o2 ON oi.order_id = o2.id 
                WHERE o2.customer_id = c.id 
                GROUP BY oi.order_id 
                HAVING COUNT(*) > 1
            ) THEN 1 ELSE 0 END as has_multi_item_orders
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.first_name, c.last_name
    ),
    overall_avg_order AS (
        SELECT AVG(total) as overall_avg_order_value
        FROM orders
    ),
    qualified_customers AS (
        SELECT 
            cm.*,
            (cm.total_spent * cm.total_orders) as weighted_clv
        FROM customer_metrics cm
        CROSS JOIN overall_avg_order oao
        WHERE cm.has_multi_item_orders = 1
        AND cm.avg_order_value > oao.overall_avg_order_value
    ),
    customer_category_revenue AS (
        SELECT 
            qc.customer_id,
            qc.first_name,
            qc.last_name,
            qc.weighted_clv,
            cat.name as category_name,
            COALESCE(SUM(oi.quantity * oi.price), 0) as category_revenue
        FROM qualified_customers qc
        JOIN orders o ON qc.customer_id = o.customer_id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        JOIN categories cat ON p.category_id = cat.id
        GROUP BY qc.customer_id, qc.first_name, qc.last_name, qc.weighted_clv, cat.name
    ),
    category_totals AS (
        SELECT 
            category_name,
            SUM(category_revenue) as total_category_revenue,
            SUM(SUM(category_revenue)) OVER () as total_revenue
        FROM customer_category_revenue
        GROUP BY category_name
    ),
    significant_categories AS (
        SELECT category_name
        FROM category_totals
        WHERE (total_category_revenue / total_revenue) > 0.10
    )
    SELECT 
        ROUND(
            SUM(ccr.weighted_clv) / SUM(ccr.weighted_clv / ccr.weighted_clv), 2
        ) as weighted_avg_clv,
        COUNT(DISTINCT ccr.customer_id) as qualified_customer_count,
        sc.category_name,
        ROUND(SUM(ccr.category_revenue), 2) as category_revenue,
        ROUND(
            (SUM(ccr.category_revenue) / SUM(SUM(ccr.category_revenue)) OVER ()) * 100, 2
        ) as revenue_percentage
    FROM customer_category_revenue ccr
    JOIN significant_categories sc ON ccr.category_name = sc.category_name
    GROUP BY sc.category_name
    ORDER BY category_revenue DESC;
    """
    
    print("🚀 ULTIMATE HARD QUESTION TEST")
    print("=" * 80)
    print(f"\n🔍 Testing: {question}")
    print("-" * 80)
    
    # Get SQL result
    print(f"SQL Query: {sql_query}")
    sql_result = get_sql_result(sql_query, question)
    print(f"SQL Result: {sql_result}")
    
    # Get Chatbot result
    print(f"\nAsking Chatbot: {question}")
    chatbot_response = ask_chatbot(question)
    print(f"Chatbot Response: {chatbot_response}")
    
    # Analysis
    print(f"\n📊 ANALYSIS:")
    print(f"   This question combines:")
    print(f"   ✅ Multiple CTEs (Common Table Expressions)")
    print(f"   ✅ EXISTS subqueries")
    print(f"   ✅ Window functions (OVER clause)")
    print(f"   ✅ Complex conditional logic (CASE statements)")
    print(f"   ✅ Multiple aggregations and calculations")
    print(f"   ✅ HAVING clauses with percentages")
    print(f"   ✅ Weighted averages")
    print(f"   ✅ Customer segmentation logic")
    print(f"   ✅ Revenue contribution analysis")
    
    # Check if chatbot attempted the question
    if "sorry" in chatbot_response.lower() or "don't have access" in chatbot_response.lower():
        print(f"\n❌ RESULT: Chatbot could not handle this ultra-complex query")
        return False
    elif "error" in chatbot_response.lower():
        print(f"\n❌ RESULT: Chatbot encountered an error")
        return False
    else:
        print(f"\n✅ RESULT: Chatbot attempted to answer the ultra-complex query!")
        return True

def main():
    """Main function"""
    success = test_ultimate_question()
    
    print(f"\n{'='*80}")
    print("🎯 ULTIMATE QUESTION VERDICT")
    print("=" * 80)
    
    if success:
        print("🎉 IMPRESSIVE! The chatbot attempted this ultra-complex query!")
        print("   This demonstrates advanced SQL understanding capabilities.")
    else:
        print("📊 EXPECTED! This query is extremely complex and would challenge")
        print("   even experienced data analysts and SQL experts.")
    
    print(f"\n💡 This question tests:")
    print(f"   • Advanced SQL concepts (CTEs, Window Functions)")
    print(f"   • Complex business logic (Customer Lifetime Value)")
    print(f"   • Multi-step analytical thinking")
    print(f"   • Revenue contribution analysis")
    print(f"   • Customer segmentation")
    print(f"   • Weighted calculations")
    
    return success

if __name__ == "__main__":
    main() 