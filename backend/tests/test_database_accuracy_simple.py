"""
Simple Database Accuracy Test
Verifies that database queries return correct values and counts

NOTE: This test runs against the local database, while the chatbot runs against the Docker database.
The values may differ between environments.
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

from sqlalchemy import text
from backend.database import engine
from backend.services.langchain_sql_service import langchain_sql_service

def test_database_connection():
    """Test that we can connect to the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_customers_table():
    """Test that customers table exists and has data"""
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'customers'
                )
            """))
            table_exists = result.fetchone()[0]
            if not table_exists:
                print("❌ Customers table does not exist")
                return 0
            
            # Get actual count
            result = conn.execute(text("SELECT COUNT(*) FROM customers"))
            actual_count = result.fetchone()[0]
            print(f"✅ Customers table exists with {actual_count} records")
            
            # Get sample data
            result = conn.execute(text("SELECT * FROM customers LIMIT 3"))
            sample_data = result.fetchall()
            print(f"✅ Sample customer data: {len(sample_data)} records")
            
            return actual_count
    except Exception as e:
        print(f"❌ Customers table test failed: {e}")
        return 0

def test_orders_table():
    """Test that orders table exists and has data"""
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'orders'
                )
            """))
            table_exists = result.fetchone()[0]
            if not table_exists:
                print("❌ Orders table does not exist")
                return 0
            
            # Get actual count
            result = conn.execute(text("SELECT COUNT(*) FROM orders"))
            actual_count = result.fetchone()[0]
            print(f"✅ Orders table exists with {actual_count} records")
            
            # Get sample data
            result = conn.execute(text("SELECT * FROM orders LIMIT 3"))
            sample_data = result.fetchall()
            print(f"✅ Sample order data: {len(sample_data)} records")
            
            return actual_count
    except Exception as e:
        print(f"❌ Orders table test failed: {e}")
        return 0

def test_products_table():
    """Test that products table exists and has data"""
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'products'
                )
            """))
            table_exists = result.fetchone()[0]
            if not table_exists:
                print("❌ Products table does not exist")
                return 0
            
            # Get actual count
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            actual_count = result.fetchone()[0]
            print(f"✅ Products table exists with {actual_count} records")
            
            # Get sample data
            result = conn.execute(text("SELECT * FROM products LIMIT 3"))
            sample_data = result.fetchall()
            print(f"✅ Sample product data: {len(sample_data)} records")
            
            return actual_count
    except Exception as e:
        print(f"❌ Products table test failed: {e}")
        return 0

def test_fallback_customer_count_accuracy():
    """Test that fallback customer count matches actual database count"""
    try:
        # Get actual count from database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM customers"))
            actual_count = result.fetchone()[0]
        
        # Get count from fallback query
        fallback_result = langchain_sql_service._fallback_query("How many customers do we have?")
        
        if not fallback_result['success']:
            print(f"❌ Fallback query failed: {fallback_result.get('error', 'Unknown error')}")
            return False
        
        # Extract count from response
        response = fallback_result['response']
        import re
        count_match = re.search(r'There are (\d+) customers', response)
        if not count_match:
            print(f"❌ Could not extract count from response: {response}")
            return False
        
        fallback_count = int(count_match.group(1))
        
        # Compare counts
        if fallback_count != actual_count:
            print(f"❌ Count mismatch: fallback={fallback_count}, actual={actual_count}")
            return False
        
        print(f"✅ Customer count accuracy verified: {actual_count} customers")
        return True
        
    except Exception as e:
        print(f"❌ Customer count accuracy test failed: {e}")
        return False

def test_fallback_orders_count_accuracy():
    """Test that fallback orders count matches actual database count"""
    try:
        # Get actual count from database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM orders"))
            actual_count = result.fetchone()[0]
        
        # Get count from fallback query
        fallback_result = langchain_sql_service._fallback_query("How many orders do we have?")
        
        if not fallback_result['success']:
            print(f"❌ Fallback query failed: {fallback_result.get('error', 'Unknown error')}")
            return False
        
        # Extract count from response
        response = fallback_result['response']
        import re
        count_match = re.search(r'There are (\d+) orders', response)
        if not count_match:
            print(f"❌ Could not extract count from response: {response}")
            return False
        
        fallback_count = int(count_match.group(1))
        
        # Compare counts
        if fallback_count != actual_count:
            print(f"❌ Count mismatch: fallback={fallback_count}, actual={actual_count}")
            return False
        
        print(f"✅ Orders count accuracy verified: {actual_count} orders")
        return True
        
    except Exception as e:
        print(f"❌ Orders count accuracy test failed: {e}")
        return False

def test_fallback_products_count_accuracy():
    """Test that fallback products count matches actual database count"""
    try:
        # Get actual count from database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            actual_count = result.fetchone()[0]
        
        # Get count from fallback query
        fallback_result = langchain_sql_service._fallback_query("How many products do we have?")
        
        if not fallback_result['success']:
            print(f"❌ Fallback query failed: {fallback_result.get('error', 'Unknown error')}")
            return False
        
        # Extract count from response
        response = fallback_result['response']
        import re
        count_match = re.search(r'There are (\d+) products', response)
        if not count_match:
            print(f"❌ Could not extract count from response: {response}")
            return False
        
        fallback_count = int(count_match.group(1))
        
        # Compare counts
        if fallback_count != actual_count:
            print(f"❌ Count mismatch: fallback={fallback_count}, actual={actual_count}")
            return False
        
        print(f"✅ Products count accuracy verified: {actual_count} products")
        return True
        
    except Exception as e:
        print(f"❌ Products count accuracy test failed: {e}")
        return False

def test_revenue_calculation_accuracy():
    """Test that revenue calculation matches actual database total"""
    try:
        # Get actual total from database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT SUM(total) FROM orders"))
            actual_total = result.fetchone()[0] or 0
        
        # Get total from fallback query
        fallback_result = langchain_sql_service._fallback_query("What is our total revenue?")
        
        if not fallback_result['success']:
            print(f"❌ Fallback query failed: {fallback_result.get('error', 'Unknown error')}")
            return False
        
        # Extract amount from response
        response = fallback_result['response']
        import re
        amount_match = re.search(r'\$([\d,]+\.?\d*)', response)
        if not amount_match:
            print(f"❌ Could not extract amount from response: {response}")
            return False
        
        fallback_amount = float(amount_match.group(1).replace(',', ''))
        
        # Compare amounts (allow small difference for rounding)
        if abs(float(fallback_amount) - float(actual_total)) >= 0.01:
            print(f"❌ Amount mismatch: fallback=${fallback_amount}, actual=${actual_total}")
            return False
        
        print(f"✅ Revenue calculation accuracy verified: ${actual_total:,.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Revenue calculation accuracy test failed: {e}")
        return False

def test_database_schema():
    """Test that all expected tables and columns exist"""
    try:
        with engine.connect() as conn:
            # Check customers table schema
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'customers'
                ORDER BY ordinal_position
            """))
            customer_columns = result.fetchall()
            print(f"✅ Customers table columns: {[col[0] for col in customer_columns]}")
            
            # Check orders table schema
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'orders'
                ORDER BY ordinal_position
            """))
            order_columns = result.fetchall()
            print(f"✅ Orders table columns: {[col[0] for col in order_columns]}")
            
            # Check products table schema
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'products'
                ORDER BY ordinal_position
            """))
            product_columns = result.fetchall()
            print(f"✅ Products table columns: {[col[0] for col in product_columns]}")
            
            # Verify required columns exist
            required_customer_cols = ['id', 'first_name', 'last_name', 'email']
            required_order_cols = ['id', 'customer_id', 'total', 'order_date']
            required_product_cols = ['id', 'name', 'price', 'category_id']
            
            customer_col_names = [col[0] for col in customer_columns]
            order_col_names = [col[0] for col in order_columns]
            product_col_names = [col[0] for col in product_columns]
            
            for col in required_customer_cols:
                if col not in customer_col_names:
                    print(f"❌ Required column '{col}' missing from customers table")
                    return False
            
            for col in required_order_cols:
                if col not in order_col_names:
                    print(f"❌ Required column '{col}' missing from orders table")
                    return False
            
            for col in required_product_cols:
                if col not in product_col_names:
                    print(f"❌ Required column '{col}' missing from products table")
                    return False
            
            print("✅ All required columns present in database schema")
            return True
            
    except Exception as e:
        print(f"❌ Database schema verification failed: {e}")
        return False

def run_all_tests():
    """Run all database accuracy tests"""
    print("🔍 Running Database Accuracy Tests...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test database connection
    total_tests += 1
    if test_database_connection():
        tests_passed += 1
    
    # Test table existence and get counts
    total_tests += 1
    customer_count = test_customers_table()
    if customer_count > 0:
        tests_passed += 1
    
    total_tests += 1
    order_count = test_orders_table()
    if order_count > 0:
        tests_passed += 1
    
    total_tests += 1
    product_count = test_products_table()
    if product_count > 0:
        tests_passed += 1
    
    # Test schema
    total_tests += 1
    if test_database_schema():
        tests_passed += 1
    
    # Test fallback accuracy
    total_tests += 1
    if test_fallback_customer_count_accuracy():
        tests_passed += 1
    
    total_tests += 1
    if test_fallback_orders_count_accuracy():
        tests_passed += 1
    
    total_tests += 1
    if test_fallback_products_count_accuracy():
        tests_passed += 1
    
    total_tests += 1
    if test_revenue_calculation_accuracy():
        tests_passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ ALL DATABASE ACCURACY TESTS PASSED!")
        print(f"📊 Database Summary:")
        print(f"   • Customers: {customer_count}")
        print(f"   • Orders: {order_count}")
        print(f"   • Products: {product_count}")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_all_tests() 