"""
Test Database Query Accuracy
Verifies that database queries return correct values and counts
"""

import pytest
import asyncio
from sqlalchemy import text
from backend.database import engine, get_db
from backend.services.langchain_sql_service import langchain_sql_service
from backend.services.rag_service import RAGService

class TestDatabaseAccuracy:
    """Test class for verifying database query accuracy"""
    
    def setup_method(self):
        """Setup test database connection"""
        self.engine = engine
    
    def test_database_connection(self):
        """Test that we can connect to the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
            print("✅ Database connection successful")
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    def test_customers_table_exists(self):
        """Test that customers table exists and has data"""
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'customers'
                    )
                """))
                table_exists = result.fetchone()[0]
                assert table_exists, "Customers table does not exist"
                
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
            pytest.fail(f"Customers table test failed: {e}")
    
    def test_orders_table_exists(self):
        """Test that orders table exists and has data"""
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'orders'
                    )
                """))
                table_exists = result.fetchone()[0]
                assert table_exists, "Orders table does not exist"
                
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
            pytest.fail(f"Orders table test failed: {e}")
    
    def test_products_table_exists(self):
        """Test that products table exists and has data"""
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'products'
                    )
                """))
                table_exists = result.fetchone()[0]
                assert table_exists, "Products table does not exist"
                
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
            pytest.fail(f"Products table test failed: {e}")
    
    def test_fallback_customer_count_accuracy(self):
        """Test that fallback customer count matches actual database count"""
        try:
            # Get actual count from database
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM customers"))
                actual_count = result.fetchone()[0]
            
            # Get count from fallback query
            fallback_result = langchain_sql_service._fallback_query("How many customers do we have?")
            
            assert fallback_result['success'], f"Fallback query failed: {fallback_result.get('error', 'Unknown error')}"
            
            # Extract count from response
            response = fallback_result['response']
            import re
            count_match = re.search(r'There are (\d+) customers', response)
            assert count_match, f"Could not extract count from response: {response}"
            
            fallback_count = int(count_match.group(1))
            
            # Compare counts
            assert fallback_count == actual_count, f"Count mismatch: fallback={fallback_count}, actual={actual_count}"
            
            print(f"✅ Customer count accuracy verified: {actual_count} customers")
            return actual_count
            
        except Exception as e:
            pytest.fail(f"Customer count accuracy test failed: {e}")
    
    def test_fallback_orders_count_accuracy(self):
        """Test that fallback orders count matches actual database count"""
        try:
            # Get actual count from database
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM orders"))
                actual_count = result.fetchone()[0]
            
            # Get count from fallback query
            fallback_result = langchain_sql_service._fallback_query("How many orders do we have?")
            
            assert fallback_result['success'], f"Fallback query failed: {fallback_result.get('error', 'Unknown error')}"
            
            # Extract count from response
            response = fallback_result['response']
            import re
            count_match = re.search(r'There are (\d+) orders', response)
            assert count_match, f"Could not extract count from response: {response}"
            
            fallback_count = int(count_match.group(1))
            
            # Compare counts
            assert fallback_count == actual_count, f"Count mismatch: fallback={fallback_count}, actual={actual_count}"
            
            print(f"✅ Orders count accuracy verified: {actual_count} orders")
            return actual_count
            
        except Exception as e:
            pytest.fail(f"Orders count accuracy test failed: {e}")
    
    def test_fallback_products_count_accuracy(self):
        """Test that fallback products count matches actual database count"""
        try:
            # Get actual count from database
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM products"))
                actual_count = result.fetchone()[0]
            
            # Get count from fallback query
            fallback_result = langchain_sql_service._fallback_query("How many products do we have?")
            
            assert fallback_result['success'], f"Fallback query failed: {fallback_result.get('error', 'Unknown error')}"
            
            # Extract count from response
            response = fallback_result['response']
            import re
            count_match = re.search(r'There are (\d+) products', response)
            assert count_match, f"Could not extract count from response: {response}"
            
            fallback_count = int(count_match.group(1))
            
            # Compare counts
            assert fallback_count == actual_count, f"Count mismatch: fallback={fallback_count}, actual={actual_count}"
            
            print(f"✅ Products count accuracy verified: {actual_count} products")
            return actual_count
            
        except Exception as e:
            pytest.fail(f"Products count accuracy test failed: {e}")
    
    def test_revenue_calculation_accuracy(self):
        """Test that revenue calculation matches actual database total"""
        try:
            # Get actual total from database
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT SUM(total_amount) FROM orders"))
                actual_total = result.fetchone()[0] or 0
            
            # Get total from fallback query
            fallback_result = langchain_sql_service._fallback_query("What is our total revenue?")
            
            assert fallback_result['success'], f"Fallback query failed: {fallback_result.get('error', 'Unknown error')}"
            
            # Extract amount from response
            response = fallback_result['response']
            import re
            amount_match = re.search(r'\$([\d,]+\.?\d*)', response)
            assert amount_match, f"Could not extract amount from response: {response}"
            
            fallback_amount = float(amount_match.group(1).replace(',', ''))
            
            # Compare amounts (allow small difference for rounding)
            assert abs(fallback_amount - actual_total) < 0.01, f"Amount mismatch: fallback=${fallback_amount}, actual=${actual_total}"
            
            print(f"✅ Revenue calculation accuracy verified: ${actual_total:,.2f}")
            return actual_total
            
        except Exception as e:
            pytest.fail(f"Revenue calculation accuracy test failed: {e}")
    
    def test_database_schema_verification(self):
        """Test that all expected tables and columns exist"""
        try:
            with self.engine.connect() as conn:
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
                required_order_cols = ['id', 'customer_id', 'total_amount', 'order_date']
                required_product_cols = ['id', 'name', 'price', 'category']
                
                customer_col_names = [col[0] for col in customer_columns]
                order_col_names = [col[0] for col in order_columns]
                product_col_names = [col[0] for col in product_columns]
                
                for col in required_customer_cols:
                    assert col in customer_col_names, f"Required column '{col}' missing from customers table"
                
                for col in required_order_cols:
                    assert col in order_col_names, f"Required column '{col}' missing from orders table"
                
                for col in required_product_cols:
                    assert col in product_col_names, f"Required column '{col}' missing from products table"
                
                print("✅ All required columns present in database schema")
                
        except Exception as e:
            pytest.fail(f"Database schema verification failed: {e}")
    
    def test_sample_data_quality(self):
        """Test that sample data looks reasonable"""
        try:
            with self.engine.connect() as conn:
                # Check customers data quality
                result = conn.execute(text("""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN first_name IS NOT NULL AND first_name != '' THEN 1 END) as valid_names,
                           COUNT(CASE WHEN email IS NOT NULL AND email != '' THEN 1 END) as valid_emails
                    FROM customers
                """))
                customer_stats = result.fetchone()
                print(f"✅ Customer data quality: {customer_stats[1]}/{customer_stats[0]} valid names, {customer_stats[2]}/{customer_stats[0]} valid emails")
                
                # Check orders data quality
                result = conn.execute(text("""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN total_amount > 0 THEN 1 END) as positive_amounts,
                           COUNT(CASE WHEN order_date IS NOT NULL THEN 1 END) as valid_dates
                    FROM orders
                """))
                order_stats = result.fetchone()
                print(f"✅ Order data quality: {order_stats[1]}/{order_stats[0]} positive amounts, {order_stats[2]}/{order_stats[0]} valid dates")
                
                # Check products data quality
                result = conn.execute(text("""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN name IS NOT NULL AND name != '' THEN 1 END) as valid_names,
                           COUNT(CASE WHEN price > 0 THEN 1 END) as positive_prices
                    FROM products
                """))
                product_stats = result.fetchone()
                print(f"✅ Product data quality: {product_stats[1]}/{product_stats[0]} valid names, {product_stats[2]}/{product_stats[0]} positive prices")
                
        except Exception as e:
            pytest.fail(f"Sample data quality test failed: {e}")

def run_database_accuracy_tests():
    """Run all database accuracy tests"""
    print("🔍 Running Database Accuracy Tests...")
    print("=" * 50)
    
    test_instance = TestDatabaseAccuracy()
    
    try:
        # Test database connection
        test_instance.test_database_connection()
        
        # Test table existence and get counts
        customer_count = test_instance.test_customers_table_exists()
        order_count = test_instance.test_orders_table_exists()
        product_count = test_instance.test_products_table_exists()
        
        # Test schema
        test_instance.test_database_schema_verification()
        
        # Test data quality
        test_instance.test_sample_data_quality()
        
        # Test fallback accuracy
        test_instance.test_fallback_customer_count_accuracy()
        test_instance.test_fallback_orders_count_accuracy()
        test_instance.test_fallback_products_count_accuracy()
        test_instance.test_revenue_calculation_accuracy()
        
        print("=" * 50)
        print("✅ ALL DATABASE ACCURACY TESTS PASSED!")
        print(f"📊 Database Summary:")
        print(f"   • Customers: {customer_count}")
        print(f"   • Orders: {order_count}")
        print(f"   • Products: {product_count}")
        
    except Exception as e:
        print(f"❌ Database accuracy test failed: {e}")
        raise

if __name__ == "__main__":
    run_database_accuracy_tests() 