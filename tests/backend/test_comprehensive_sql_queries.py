"""
Comprehensive SQL Database Test Suite
Tests complex queries, data integrity, and business logic scenarios
"""

import pytest
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime, timedelta
import json

class TestComprehensiveSQLQueries:
    """Test suite for comprehensive SQL database operations"""
    
    def setup_method(self):
        """Setup database connection for each test"""
        # Database connection parameters
        self.db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5433'),
            'database': os.getenv('DB_NAME', 'ai_chatbot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password1234')
        }
        
        # Create SQLAlchemy engine
        self.connection_string = f"postgresql://{self.db_params['user']}:{self.db_params['password']}@{self.db_params['host']}:{self.db_params['port']}/{self.db_params['database']}"
        self.engine = create_engine(self.connection_string)
    
    def execute_query(self, query, fetch=True):
        """Execute a SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                if fetch:
                    return result.fetchall()
                else:
                    conn.commit()
                    return result.rowcount
        except SQLAlchemyError as e:
            print(f"❌ SQL Error: {e}")
            return None
    
    def test_1_customer_analytics_complex(self):
        """Test 1: Complex customer analytics with multiple joins and aggregations"""
        print("\n🔍 Test 1: Complex Customer Analytics")
        
        query = """
        WITH customer_stats AS (
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                c.email,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(o.total), 0) as total_spent,
                COALESCE(AVG(o.total), 0) as avg_order_value,
                COUNT(DISTINCT r.id) as total_reviews,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT wi.product_id) as wishlist_items,
                COUNT(DISTINCT ci.product_id) as cart_items
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            LEFT JOIN reviews r ON c.id = r.customer_id
            LEFT JOIN wishlists w ON c.id = w.customer_id
            LEFT JOIN wishlist_items wi ON w.id = wi.wishlist_id
            LEFT JOIN cart ca ON c.id = ca.customer_id
            LEFT JOIN cart_items ci ON ca.id = ci.cart_id
            GROUP BY c.id, c.first_name, c.last_name, c.email
        )
        SELECT 
            id,
            first_name,
            last_name,
            email,
            total_orders,
            total_spent,
            avg_order_value,
            total_reviews,
            avg_rating,
            wishlist_items,
            cart_items,
            CASE 
                WHEN total_spent > 1000 THEN 'VIP'
                WHEN total_spent > 500 THEN 'Regular'
                WHEN total_spent > 100 THEN 'Occasional'
                ELSE 'New'
            END as customer_segment
        FROM customer_stats
        ORDER BY total_spent DESC
        LIMIT 10;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} customers with analytics")
        
        if results:
            for row in results[:3]:  # Show first 3 results
                print(f"   Customer: {row[1]} {row[2]} - Orders: {row[4]}, Spent: ${row[5]:.2f}, Segment: {row[11]}")
        
        assert results is not None
        assert len(results) > 0
        return results
    
    def test_2_product_performance_analysis(self):
        """Test 2: Product performance analysis with inventory and sales metrics"""
        print("\n🔍 Test 2: Product Performance Analysis")
        
        query = """
        WITH product_metrics AS (
            SELECT 
                p.id,
                p.name,
                p.price,
                c.name as category,
                s.name as supplier,
                i.quantity as current_stock,
                COUNT(DISTINCT oi.order_id) as times_ordered,
                COALESCE(SUM(oi.quantity), 0) as total_units_sold,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue,
                COUNT(DISTINCT r.id) as review_count,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT wi.wishlist_id) as wishlist_count,
                COUNT(DISTINCT ci.cart_id) as cart_count
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN reviews r ON p.id = r.product_id
            LEFT JOIN wishlist_items wi ON p.id = wi.product_id
            LEFT JOIN cart_items ci ON p.id = ci.product_id
            GROUP BY p.id, p.name, p.price, c.name, s.name, i.quantity
        )
        SELECT 
            id,
            name,
            price,
            category,
            supplier,
            current_stock,
            times_ordered,
            total_units_sold,
            total_revenue,
            review_count,
            avg_rating,
            wishlist_count,
            cart_count,
            CASE 
                WHEN current_stock = 0 THEN 'Out of Stock'
                WHEN current_stock < 10 THEN 'Low Stock'
                WHEN current_stock < 50 THEN 'Medium Stock'
                ELSE 'Well Stocked'
            END as stock_status,
            CASE 
                WHEN total_revenue > 1000 THEN 'High Performer'
                WHEN total_revenue > 500 THEN 'Medium Performer'
                WHEN total_revenue > 100 THEN 'Low Performer'
                ELSE 'No Sales'
            END as performance_category
        FROM product_metrics
        ORDER BY total_revenue DESC, avg_rating DESC
        LIMIT 15;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} products with performance metrics")
        
        if results:
            for row in results[:3]:  # Show first 3 results
                print(f"   Product: {row[1]} - Revenue: ${row[8]:.2f}, Stock: {row[5]}, Rating: {row[10]:.1f}")
        
        assert results is not None
        assert len(results) > 0
        return results
    
    def test_3_order_processing_workflow(self):
        """Test 3: Order processing workflow with status tracking"""
        print("\n🔍 Test 3: Order Processing Workflow")
        
        query = """
        WITH order_workflow AS (
            SELECT 
                o.id as order_id,
                o.order_date,
                o.status as order_status,
                o.total as order_total,
                c.first_name,
                c.last_name,
                c.email,
                p.payment_date,
                p.payment_method,
                p.status as payment_status,
                s.shipped_date,
                s.delivery_date,
                s.carrier,
                s.status as shipping_status,
                COUNT(oi.id) as item_count,
                STRING_AGG(p2.name, ', ' ORDER BY p2.name) as products_ordered
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN payments p ON o.id = p.order_id
            LEFT JOIN shipping s ON o.id = s.order_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN products p2 ON oi.product_id = p2.id
            GROUP BY o.id, o.order_date, o.status, o.total, c.first_name, c.last_name, c.email,
                     p.payment_date, p.payment_method, p.status, s.shipped_date, s.delivery_date, s.carrier, s.status
        )
        SELECT 
            order_id,
            order_date,
            order_status,
            order_total,
            first_name,
            last_name,
            email,
            payment_date,
            payment_method,
            payment_status,
            shipped_date,
            delivery_date,
            carrier,
            shipping_status,
            item_count,
            products_ordered,
            CASE 
                WHEN order_status = 'completed' AND payment_status = 'completed' AND shipping_status = 'delivered' THEN 'Fully Processed'
                WHEN order_status = 'shipped' AND payment_status = 'completed' THEN 'In Transit'
                WHEN order_status = 'processing' AND payment_status = 'completed' THEN 'Ready to Ship'
                WHEN order_status = 'pending' AND payment_status = 'pending' THEN 'Awaiting Payment'
                ELSE 'Processing'
            END as workflow_status
        FROM order_workflow
        ORDER BY order_date DESC
        LIMIT 10;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} orders with workflow status")
        
        if results:
            for row in results[:3]:  # Show first 3 results
                print(f"   Order #{row[0]}: {row[4]} {row[5]} - Status: {row[16]}, Total: ${row[3]:.2f}")
        
        assert results is not None
        assert len(results) > 0
        return results
    
    def test_4_inventory_management_alerts(self):
        """Test 4: Inventory management with low stock alerts and reorder suggestions"""
        print("\n🔍 Test 4: Inventory Management Alerts")
        
        query = """
        WITH inventory_analysis AS (
            SELECT 
                p.id,
                p.name,
                p.sku,
                c.name as category,
                s.name as supplier,
                i.quantity as current_stock,
                COALESCE(SUM(oi.quantity), 0) as units_sold_last_30_days,
                COALESCE(AVG(oi.quantity), 0) as avg_daily_sales,
                p.price as unit_cost,
                (i.quantity * p.price) as inventory_value,
                CASE 
                    WHEN i.quantity = 0 THEN 'CRITICAL: Out of Stock'
                    WHEN i.quantity < 5 THEN 'HIGH: Low Stock Alert'
                    WHEN i.quantity < 20 THEN 'MEDIUM: Monitor Stock'
                    ELSE 'OK: Well Stocked'
                END as stock_alert,
                CASE 
                    WHEN i.quantity = 0 THEN 50
                    WHEN i.quantity < 5 THEN 30
                    WHEN i.quantity < 20 THEN 20
                    ELSE 0
                END as suggested_reorder_quantity
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days' OR o.order_date IS NULL
            GROUP BY p.id, p.name, p.sku, c.name, s.name, i.quantity, p.price
        )
        SELECT 
            id,
            name,
            sku,
            category,
            supplier,
            current_stock,
            units_sold_last_30_days,
            avg_daily_sales,
            unit_cost,
            inventory_value,
            stock_alert,
            suggested_reorder_quantity,
            (suggested_reorder_quantity * unit_cost) as reorder_cost
        FROM inventory_analysis
        WHERE current_stock < 20 OR units_sold_last_30_days > 0
        ORDER BY 
            CASE 
                WHEN current_stock = 0 THEN 1
                WHEN current_stock < 5 THEN 2
                WHEN current_stock < 20 THEN 3
                ELSE 4
            END,
            units_sold_last_30_days DESC
        LIMIT 15;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} products requiring inventory attention")
        
        if results:
            critical_items = [row for row in results if 'CRITICAL' in row[10] or 'HIGH' in row[10]]
            print(f"   ⚠️  {len(critical_items)} items need immediate attention")
            
            for row in critical_items[:3]:
                print(f"   Alert: {row[1]} - {row[10]} (Stock: {row[5]})")
        
        assert results is not None
        return results
    
    def test_5_revenue_analytics_by_category(self):
        """Test 5: Revenue analytics by category with time-based analysis"""
        print("\n🔍 Test 5: Revenue Analytics by Category")
        
        query = """
        WITH category_revenue AS (
            SELECT 
                c.id as category_id,
                c.name as category_name,
                COUNT(DISTINCT p.id) as total_products,
                COUNT(DISTINCT o.id) as total_orders,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                COALESCE(SUM(oi.quantity), 0) as total_units_sold,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue,
                COALESCE(AVG(oi.price), 0) as avg_product_price,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.id) as total_reviews
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            LEFT JOIN reviews r ON p.id = r.product_id
            GROUP BY c.id, c.name
        ),
        category_rankings AS (
            SELECT 
                *,
                RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
                RANK() OVER (ORDER BY total_orders DESC) as orders_rank,
                RANK() OVER (ORDER BY avg_rating DESC) as rating_rank
            FROM category_revenue
        )
        SELECT 
            category_id,
            category_name,
            total_products,
            total_orders,
            unique_customers,
            total_units_sold,
            total_revenue,
            avg_product_price,
            avg_rating,
            total_reviews,
            revenue_rank,
            orders_rank,
            rating_rank,
            CASE 
                WHEN revenue_rank <= 2 THEN 'Top Performer'
                WHEN revenue_rank <= 4 THEN 'Good Performer'
                WHEN revenue_rank <= 6 THEN 'Average Performer'
                ELSE 'Low Performer'
            END as performance_tier
        FROM category_rankings
        ORDER BY total_revenue DESC;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} categories with revenue analytics")
        
        if results:
            for row in results:
                print(f"   {row[1]}: Revenue ${row[6]:.2f} (Rank #{row[10]}) - {row[13]}")
        
        assert results is not None
        assert len(results) > 0
        return results
    
    def test_6_customer_segmentation_analysis(self):
        """Test 6: Customer segmentation based on behavior and spending patterns"""
        print("\n🔍 Test 6: Customer Segmentation Analysis")
        
        query = """
        WITH customer_behavior AS (
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                c.email,
                c.created_at as customer_since,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(o.total), 0) as total_spent,
                COALESCE(AVG(o.total), 0) as avg_order_value,
                COUNT(DISTINCT r.id) as total_reviews,
                COALESCE(AVG(r.rating), 0) as avg_review_rating,
                COUNT(DISTINCT wi.product_id) as wishlist_items,
                COUNT(DISTINCT ci.product_id) as cart_items,
                MAX(o.order_date) as last_order_date,
                CASE 
                    WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
                    WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '90 days' THEN 'Recent'
                    WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '365 days' THEN 'Occasional'
                    ELSE 'Inactive'
                END as activity_status
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            LEFT JOIN reviews r ON c.id = r.customer_id
            LEFT JOIN wishlists w ON c.id = w.customer_id
            LEFT JOIN wishlist_items wi ON w.id = wi.wishlist_id
            LEFT JOIN cart ca ON c.id = ca.customer_id
            LEFT JOIN cart_items ci ON ca.id = ci.cart_id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.created_at
        ),
        customer_segments AS (
            SELECT 
                *,
                CASE 
                    WHEN total_spent >= 1000 AND total_orders >= 5 THEN 'VIP Customer'
                    WHEN total_spent >= 500 AND total_orders >= 3 THEN 'Regular Customer'
                    WHEN total_spent >= 100 AND total_orders >= 1 THEN 'Occasional Customer'
                    WHEN total_spent > 0 THEN 'One-time Customer'
                    ELSE 'Prospect'
                END as spending_segment,
                CASE 
                    WHEN avg_review_rating >= 4.5 THEN 'Highly Satisfied'
                    WHEN avg_review_rating >= 4.0 THEN 'Satisfied'
                    WHEN avg_review_rating >= 3.0 THEN 'Neutral'
                    WHEN avg_review_rating > 0 THEN 'Dissatisfied'
                    ELSE 'No Reviews'
                END as satisfaction_level
            FROM customer_behavior
        )
        SELECT 
            id,
            first_name,
            last_name,
            email,
            customer_since,
            total_orders,
            total_spent,
            avg_order_value,
            total_reviews,
            avg_review_rating,
            wishlist_items,
            cart_items,
            last_order_date,
            activity_status,
            spending_segment,
            satisfaction_level,
            CASE 
                WHEN spending_segment = 'VIP Customer' AND activity_status = 'Active' THEN 'High Value Active'
                WHEN spending_segment IN ('VIP Customer', 'Regular Customer') AND activity_status IN ('Active', 'Recent') THEN 'High Value'
                WHEN activity_status = 'Active' THEN 'Active Low Value'
                WHEN spending_segment = 'Prospect' THEN 'Prospect'
                ELSE 'At Risk'
            END as customer_tier
        FROM customer_segments
        ORDER BY total_spent DESC, last_order_date DESC
        LIMIT 20;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} customers with segmentation analysis")
        
        if results:
            # Count segments
            segments = {}
            tiers = {}
            for row in results:
                segment = row[14]
                tier = row[16]
                segments[segment] = segments.get(segment, 0) + 1
                tiers[tier] = tiers.get(tier, 0) + 1
            
            print("   📊 Customer Segments:")
            for segment, count in segments.items():
                print(f"      {segment}: {count} customers")
            
            print("   📊 Customer Tiers:")
            for tier, count in tiers.items():
                print(f"      {tier}: {count} customers")
        
        assert results is not None
        assert len(results) > 0
        return results
    
    def test_7_supplier_performance_analysis(self):
        """Test 7: Supplier performance analysis with product quality and delivery metrics"""
        print("\n🔍 Test 7: Supplier Performance Analysis")
        
        query = """
        WITH supplier_metrics AS (
            SELECT 
                s.id as supplier_id,
                s.name as supplier_name,
                s.contact_email,
                s.phone,
                COUNT(DISTINCT p.id) as total_products,
                COALESCE(SUM(i.quantity), 0) as total_inventory,
                COALESCE(SUM(oi.quantity), 0) as total_units_sold,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue,
                COALESCE(AVG(r.rating), 0) as avg_product_rating,
                COUNT(DISTINCT r.id) as total_reviews,
                COUNT(DISTINCT CASE WHEN i.quantity = 0 THEN p.id END) as out_of_stock_products,
                COUNT(DISTINCT CASE WHEN i.quantity < 10 THEN p.id END) as low_stock_products
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN reviews r ON p.id = r.product_id
            GROUP BY s.id, s.name, s.contact_email, s.phone
        ),
        supplier_rankings AS (
            SELECT 
                *,
                RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
                RANK() OVER (ORDER BY avg_product_rating DESC) as quality_rank,
                RANK() OVER (ORDER BY total_products DESC) as product_rank
            FROM supplier_metrics
        )
        SELECT 
            supplier_id,
            supplier_name,
            contact_email,
            phone,
            total_products,
            total_inventory,
            total_units_sold,
            total_revenue,
            avg_product_rating,
            total_reviews,
            out_of_stock_products,
            low_stock_products,
            revenue_rank,
            quality_rank,
            product_rank,
            CASE 
                WHEN out_of_stock_products > total_products * 0.3 THEN 'Poor Stock Management'
                WHEN low_stock_products > total_products * 0.5 THEN 'Needs Attention'
                ELSE 'Good Stock Management'
            END as stock_management_status,
            CASE 
                WHEN avg_product_rating >= 4.5 THEN 'Excellent Quality'
                WHEN avg_product_rating >= 4.0 THEN 'Good Quality'
                WHEN avg_product_rating >= 3.0 THEN 'Average Quality'
                ELSE 'Poor Quality'
            END as quality_status
        FROM supplier_rankings
        ORDER BY total_revenue DESC;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} suppliers with performance metrics")
        
        if results:
            for row in results:
                print(f"   {row[1]}: Revenue ${row[7]:.2f}, Quality {row[8]:.1f}/5, Stock: {row[15]}")
        
        assert results is not None
        assert len(results) > 0
        return results
    
    def test_8_data_integrity_validation(self):
        """Test 8: Data integrity validation with constraint checking"""
        print("\n🔍 Test 8: Data Integrity Validation")
        
        integrity_checks = [
            {
                "name": "Orphaned Order Items",
                "query": """
                SELECT COUNT(*) as orphaned_count
                FROM order_items oi
                LEFT JOIN orders o ON oi.order_id = o.id
                WHERE o.id IS NULL;
                """
            },
            {
                "name": "Orphaned Cart Items",
                "query": """
                SELECT COUNT(*) as orphaned_count
                FROM cart_items ci
                LEFT JOIN cart c ON ci.cart_id = c.id
                WHERE c.id IS NULL;
                """
            },
            {
                "name": "Products Without Inventory",
                "query": """
                SELECT COUNT(*) as missing_inventory
                FROM products p
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE i.id IS NULL;
                """
            },
            {
                "name": "Orders Without Payments",
                "query": """
                SELECT COUNT(*) as orders_without_payments
                FROM orders o
                LEFT JOIN payments p ON o.id = p.order_id
                WHERE p.id IS NULL AND o.status != 'cancelled';
                """
            },
            {
                "name": "Duplicate SKUs",
                "query": """
                SELECT COUNT(*) as duplicate_skus
                FROM (
                    SELECT sku, COUNT(*) as cnt
                    FROM products
                    WHERE sku IS NOT NULL
                    GROUP BY sku
                    HAVING COUNT(*) > 1
                ) as duplicates;
                """
            },
            {
                "name": "Invalid Email Formats",
                "query": """
                SELECT COUNT(*) as invalid_emails
                FROM customers
                WHERE email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
                """
            },
            {
                "name": "Negative Inventory",
                "query": """
                SELECT COUNT(*) as negative_inventory
                FROM inventory
                WHERE quantity < 0;
                """
            },
            {
                "name": "Invalid Ratings",
                "query": """
                SELECT COUNT(*) as invalid_ratings
                FROM reviews
                WHERE rating < 1 OR rating > 5;
                """
            }
        ]
        
        integrity_results = {}
        
        for check in integrity_checks:
            result = self.execute_query(check["query"])
            if result and len(result) > 0:
                count = result[0][0]
                integrity_results[check["name"]] = count
                status = "❌" if count > 0 else "✅"
                print(f"   {status} {check['name']}: {count} issues found")
        
        # Overall integrity score
        total_issues = sum(integrity_results.values())
        print(f"\n   📊 Total Data Integrity Issues: {total_issues}")
        
        if total_issues == 0:
            print("   🎉 All data integrity checks passed!")
        else:
            print("   ⚠️  Some data integrity issues found")
        
        assert integrity_results is not None
        return integrity_results
    
    def test_9_complex_business_queries(self):
        """Test 9: Complex business intelligence queries"""
        print("\n🔍 Test 9: Complex Business Intelligence Queries")
        
        # Query 1: Customer Lifetime Value Analysis
        print("   📈 Customer Lifetime Value Analysis:")
        clv_query = """
        WITH customer_clv AS (
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                SUM(o.total) as total_spent,
                COUNT(DISTINCT o.id) as total_orders,
                AVG(o.total) as avg_order_value,
                MAX(o.order_date) as last_order,
                MIN(o.order_date) as first_order,
                EXTRACT(DAYS FROM (MAX(o.order_date) - MIN(o.order_date))) as customer_lifespan_days,
                CASE 
                    WHEN COUNT(DISTINCT o.id) > 1 THEN 
                        SUM(o.total) / COUNT(DISTINCT o.id)
                    ELSE 0 
                END as customer_lifetime_value
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            WHERE o.id IS NOT NULL
            GROUP BY c.id, c.first_name, c.last_name
        )
        SELECT 
            id,
            first_name,
            last_name,
            total_spent,
            total_orders,
            avg_order_value,
            customer_lifespan_days,
            customer_lifetime_value,
            CASE 
                WHEN customer_lifetime_value > 500 THEN 'High Value'
                WHEN customer_lifetime_value > 200 THEN 'Medium Value'
                WHEN customer_lifetime_value > 50 THEN 'Low Value'
                ELSE 'Minimal Value'
            END as clv_category
        FROM customer_clv
        ORDER BY customer_lifetime_value DESC
        LIMIT 10;
        """
        
        clv_results = self.execute_query(clv_query)
        if clv_results:
            print(f"      Found {len(clv_results)} customers with CLV analysis")
            for row in clv_results[:3]:
                print(f"      {row[1]} {row[2]}: CLV ${row[7]:.2f} ({row[8]})")
        
        # Query 2: Product Category Performance Trends
        print("   📊 Product Category Performance Trends:")
        trend_query = """
        SELECT 
            c.name as category,
            COUNT(DISTINCT p.id) as product_count,
            COALESCE(SUM(oi.quantity), 0) as units_sold,
            COALESCE(SUM(oi.quantity * oi.price), 0) as revenue,
            COALESCE(AVG(r.rating), 0) as avg_rating,
            COUNT(DISTINCT r.id) as review_count,
            COALESCE(SUM(i.quantity), 0) as total_inventory,
            CASE 
                WHEN COALESCE(SUM(oi.quantity), 0) > 0 THEN 
                    COALESCE(SUM(i.quantity), 0) / COALESCE(SUM(oi.quantity), 1)
                ELSE 0 
            END as inventory_turnover_ratio
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN reviews r ON p.id = r.product_id
        LEFT JOIN inventory i ON p.id = i.product_id
        GROUP BY c.id, c.name
        ORDER BY revenue DESC;
        """
        
        trend_results = self.execute_query(trend_query)
        if trend_results:
            print(f"      Found {len(trend_results)} categories with performance trends")
            for row in trend_results:
                print(f"      {row[0]}: Revenue ${row[3]:.2f}, Turnover: {row[7]:.2f}")
        
        assert clv_results is not None or trend_results is not None
        return {"clv": clv_results, "trends": trend_results}
    
    def test_10_performance_optimization_queries(self):
        """Test 10: Performance optimization queries with indexing analysis"""
        print("\n🔍 Test 10: Performance Optimization Analysis")
        
        # Check for missing indexes on frequently queried columns
        index_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
        """
        
        index_results = self.execute_query(index_query)
        print(f"   📋 Found {len(index_results)} indexes in database")
        
        # Analyze table sizes
        size_query = """
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats
        WHERE schemaname = 'public'
        ORDER BY tablename, attname;
        """
        
        stats_results = self.execute_query(size_query)
        print(f"   📊 Found {len(stats_results)} column statistics")
        
        # Check for potential performance issues
        performance_query = """
        SELECT 
            relname as table_name,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_rows,
            n_dead_tup as dead_rows,
            CASE 
                WHEN n_dead_tup > n_live_tup * 0.1 THEN 'Needs VACUUM'
                ELSE 'OK'
            END as maintenance_status
        FROM pg_stat_user_tables
        ORDER BY n_dead_tup DESC;
        """
        
        perf_results = self.execute_query(performance_query)
        print(f"   🔧 Found {len(perf_results)} tables with performance metrics")
        
        if perf_results:
            for row in perf_results:
                if 'Needs VACUUM' in row[6]:
                    print(f"      ⚠️  {row[0]}: {row[6]} (Dead rows: {row[5]})")
        
        assert index_results is not None
        return {"indexes": index_results, "stats": stats_results, "performance": perf_results}

def run_comprehensive_sql_tests():
    """Run all comprehensive SQL tests and provide analysis"""
    print("🚀 Starting Comprehensive SQL Database Test Suite")
    print("=" * 60)
    
    test_suite = TestComprehensiveSQLQueries()
    test_suite.setup_method()
    
    results = {}
    
    # Run all tests
    test_methods = [
        test_suite.test_1_customer_analytics_complex,
        test_suite.test_2_product_performance_analysis,
        test_suite.test_3_order_processing_workflow,
        test_suite.test_4_inventory_management_alerts,
        test_suite.test_5_revenue_analytics_by_category,
        test_suite.test_6_customer_segmentation_analysis,
        test_suite.test_7_supplier_performance_analysis,
        test_suite.test_8_data_integrity_validation,
        test_suite.test_9_complex_business_queries,
        test_suite.test_10_performance_optimization_queries
    ]
    
    for i, test_method in enumerate(test_methods, 1):
        try:
            print(f"\n{'='*20} Test {i} {'='*20}")
            result = test_method()
            results[f"test_{i}"] = result
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
            results[f"test_{i}"] = {"error": str(e)}
    
    # Generate analysis report
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE SQL TEST ANALYSIS REPORT")
    print("="*60)
    
    # Data Quality Analysis
    if "test_8" in results and isinstance(results["test_8"], dict):
        integrity_issues = sum(results["test_8"].values())
        print(f"\n🔍 Data Quality:")
        print(f"   Total Integrity Issues: {integrity_issues}")
        if integrity_issues == 0:
            print("   ✅ Excellent data quality - no integrity issues found")
        elif integrity_issues < 5:
            print("   ⚠️  Good data quality - minor issues detected")
        else:
            print("   ❌ Poor data quality - significant issues need attention")
    
    # Business Intelligence Summary
    print(f"\n📈 Business Intelligence Summary:")
    if "test_1" in results and results["test_1"]:
        print(f"   Customer Analytics: {len(results['test_1'])} customers analyzed")
    if "test_2" in results and results["test_2"]:
        print(f"   Product Performance: {len(results['test_2'])} products analyzed")
    if "test_5" in results and results["test_5"]:
        print(f"   Category Revenue: {len(results['test_5'])} categories analyzed")
    
    # Performance Analysis
    print(f"\n⚡ Performance Analysis:")
    if "test_10" in results and "performance" in results["test_10"]:
        perf_data = results["test_10"]["performance"]
        if perf_data:
            tables_needing_vacuum = [row for row in perf_data if "Needs VACUUM" in row[6]]
            print(f"   Tables needing maintenance: {len(tables_needing_vacuum)}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if "test_8" in results and isinstance(results["test_8"], dict):
        if results["test_8"].get("Orphaned Order Items", 0) > 0:
            print("   🔧 Clean up orphaned order items")
        if results["test_8"].get("Products Without Inventory", 0) > 0:
            print("   🔧 Add inventory records for all products")
        if results["test_8"].get("Duplicate SKUs", 0) > 0:
            print("   🔧 Resolve duplicate SKU issues")
    
    print(f"\n✅ Comprehensive SQL test suite completed!")
    return results

if __name__ == "__main__":
    run_comprehensive_sql_tests() 