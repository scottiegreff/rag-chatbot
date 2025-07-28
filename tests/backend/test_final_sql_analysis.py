"""
Final Comprehensive SQL Database Analysis
Complete analysis with corrected queries and detailed reporting
"""

import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime, timedelta
import json

class FinalSQLAnalysis:
    """Final comprehensive SQL database analysis"""
    
    def setup_method(self):
        """Setup database connection"""
        self.db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5433'),
            'database': os.getenv('DB_NAME', 'ai_chatbot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password1234')
        }
        
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
    
    def test_1_comprehensive_customer_analysis(self):
        """Test 1: Comprehensive customer analysis with all metrics"""
        print("\n🔍 Test 1: Comprehensive Customer Analysis")
        
        query = """
        WITH customer_comprehensive AS (
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                c.email,
                c.created_at as customer_since,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(o.total), 0) as total_spent,
                COALESCE(AVG(o.total), 0) as avg_order_value,
                MIN(o.order_date) as first_order_date,
                MAX(o.order_date) as last_order_date,
                EXTRACT(DAYS FROM (MAX(o.order_date) - MIN(o.order_date))) as customer_lifespan_days,
                COUNT(DISTINCT r.id) as total_reviews,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT wi.product_id) as wishlist_items,
                COUNT(DISTINCT ci.product_id) as cart_items,
                COUNT(DISTINCT p.id) as unique_products_purchased
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            LEFT JOIN reviews r ON c.id = r.customer_id
            LEFT JOIN wishlists w ON c.id = w.customer_id
            LEFT JOIN wishlist_items wi ON w.id = wi.wishlist_id
            LEFT JOIN cart ca ON c.id = ca.customer_id
            LEFT JOIN cart_items ci ON ca.id = ci.cart_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.created_at
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
            first_order_date,
            last_order_date,
            customer_lifespan_days,
            total_reviews,
            avg_rating,
            wishlist_items,
            cart_items,
            unique_products_purchased,
            CASE 
                WHEN total_spent >= 1000 THEN 'VIP'
                WHEN total_spent >= 500 THEN 'Regular'
                WHEN total_spent >= 100 THEN 'Occasional'
                WHEN total_spent > 0 THEN 'One-time'
                ELSE 'Prospect'
            END as spending_tier,
            CASE 
                WHEN customer_lifespan_days > 365 THEN 'Long-term'
                WHEN customer_lifespan_days > 90 THEN 'Medium-term'
                WHEN customer_lifespan_days > 30 THEN 'Short-term'
                ELSE 'New'
            END as tenure_tier,
            CASE 
                WHEN avg_rating >= 4.5 THEN 'Highly Satisfied'
                WHEN avg_rating >= 4.0 THEN 'Satisfied'
                WHEN avg_rating >= 3.0 THEN 'Neutral'
                WHEN avg_rating > 0 THEN 'Dissatisfied'
                ELSE 'No Reviews'
            END as satisfaction_tier
        FROM customer_comprehensive
        ORDER BY total_spent DESC, total_orders DESC
        LIMIT 15;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} customers with comprehensive analysis")
        
        if results:
            # Analyze tiers
            vip_customers = [row for row in results if row[16] == 'VIP']
            regular_customers = [row for row in results if row[16] == 'Regular']
            
            print(f"   🏆 VIP Customers: {len(vip_customers)}")
            print(f"   📊 Regular Customers: {len(regular_customers)}")
            
            if vip_customers:
                total_vip_revenue = sum(row[6] for row in vip_customers)
                print(f"   💰 VIP Revenue: ${total_vip_revenue:.2f}")
        
        return results
    
    def test_2_product_performance_deep_dive(self):
        """Test 2: Deep dive product performance analysis"""
        print("\n🔍 Test 2: Product Performance Deep Dive")
        
        query = """
        WITH product_performance AS (
            SELECT 
                p.id,
                p.name,
                p.sku,
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
                COUNT(DISTINCT ci.cart_id) as cart_count,
                COUNT(DISTINCT o.customer_id) as unique_customers
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            LEFT JOIN reviews r ON p.id = r.product_id
            LEFT JOIN wishlist_items wi ON p.id = wi.product_id
            LEFT JOIN cart_items ci ON p.id = ci.product_id
            GROUP BY p.id, p.name, p.sku, p.price, c.name, s.name, i.quantity
        ),
        product_rankings AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (PARTITION BY category ORDER BY total_revenue DESC) as category_rank,
                RANK() OVER (ORDER BY total_revenue DESC) as overall_rank,
                DENSE_RANK() OVER (ORDER BY avg_rating DESC) as quality_rank,
                NTILE(4) OVER (ORDER BY total_revenue DESC) as revenue_quartile
            FROM product_performance
        )
        SELECT 
            id,
            name,
            sku,
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
            unique_customers,
            category_rank,
            overall_rank,
            quality_rank,
            revenue_quartile,
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
        FROM product_rankings
        ORDER BY total_revenue DESC, avg_rating DESC
        LIMIT 20;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} products with deep performance analysis")
        
        if results:
            # Analyze performance categories
            high_performers = [row for row in results if row[19] == 'High Performer']
            medium_performers = [row for row in results if row[19] == 'Medium Performer']
            
            print(f"   🚀 High Performers: {len(high_performers)}")
            print(f"   📈 Medium Performers: {len(medium_performers)}")
            
            # Show category leaders
            category_leaders = [row for row in results if row[15] == 1]
            print(f"   🏆 Category Leaders: {len(category_leaders)}")
        
        return results
    
    def test_3_order_workflow_complete_analysis(self):
        """Test 3: Complete order workflow analysis"""
        print("\n🔍 Test 3: Complete Order Workflow Analysis")
        
        query = """
        WITH order_workflow_complete AS (
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
                p.amount as payment_amount,
                s.shipped_date,
                s.delivery_date,
                s.carrier,
                s.tracking_number,
                s.status as shipping_status,
                COUNT(oi.id) as item_count,
                STRING_AGG(p2.name, ', ' ORDER BY p2.name) as products_ordered,
                EXTRACT(DAYS FROM (COALESCE(s.delivery_date, CURRENT_DATE) - o.order_date)) as days_to_delivery
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN payments p ON o.id = p.order_id
            LEFT JOIN shipping s ON o.id = s.order_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN products p2 ON oi.product_id = p2.id
            GROUP BY o.id, o.order_date, o.status, o.total, c.first_name, c.last_name, c.email,
                     p.payment_date, p.payment_method, p.status, p.amount, s.shipped_date, s.delivery_date, s.carrier, s.tracking_number, s.status
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
            payment_amount,
            shipped_date,
            delivery_date,
            carrier,
            tracking_number,
            shipping_status,
            item_count,
            products_ordered,
            days_to_delivery,
            CASE 
                WHEN order_status = 'completed' AND payment_status = 'completed' AND shipping_status = 'delivered' THEN 'Fully Processed'
                WHEN order_status = 'shipped' AND payment_status = 'completed' THEN 'In Transit'
                WHEN order_status = 'processing' AND payment_status = 'completed' THEN 'Ready to Ship'
                WHEN order_status = 'pending' AND payment_status = 'pending' THEN 'Awaiting Payment'
                WHEN order_status = 'pending' AND payment_status = 'completed' THEN 'Payment Received'
                ELSE 'Processing'
            END as workflow_status,
            CASE 
                WHEN days_to_delivery <= 3 THEN 'Fast Delivery'
                WHEN days_to_delivery <= 7 THEN 'Standard Delivery'
                WHEN days_to_delivery <= 14 THEN 'Slow Delivery'
                ELSE 'Very Slow Delivery'
            END as delivery_speed
        FROM order_workflow_complete
        ORDER BY order_date DESC
        LIMIT 15;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} orders with complete workflow analysis")
        
        if results:
            # Analyze workflow statuses
            fully_processed = [row for row in results if row[19] == 'Fully Processed']
            in_transit = [row for row in results if row[19] == 'In Transit']
            
            print(f"   ✅ Fully Processed: {len(fully_processed)}")
            print(f"   🚚 In Transit: {len(in_transit)}")
            
            # Analyze delivery speeds
            fast_delivery = [row for row in results if row[20] == 'Fast Delivery']
            print(f"   ⚡ Fast Delivery: {len(fast_delivery)}")
        
        return results
    
    def test_4_revenue_analytics_comprehensive(self):
        """Test 4: Comprehensive revenue analytics"""
        print("\n🔍 Test 4: Comprehensive Revenue Analytics")
        
        query = """
        WITH revenue_breakdown AS (
            SELECT 
                c.name as category,
                s.name as supplier,
                DATE(o.order_date) as order_date,
                COUNT(DISTINCT o.id) as daily_orders,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                COALESCE(SUM(oi.quantity), 0) as units_sold,
                COALESCE(SUM(oi.quantity * oi.price), 0) as daily_revenue,
                COALESCE(AVG(oi.price), 0) as avg_unit_price
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            GROUP BY c.name, s.name, DATE(o.order_date)
        ),
        revenue_summary AS (
            SELECT 
                category,
                supplier,
                COUNT(DISTINCT order_date) as active_days,
                SUM(daily_orders) as total_orders,
                SUM(unique_customers) as total_customers,
                SUM(units_sold) as total_units,
                SUM(daily_revenue) as total_revenue,
                AVG(daily_revenue) as avg_daily_revenue,
                AVG(avg_unit_price) as avg_unit_price
            FROM revenue_breakdown
            GROUP BY category, supplier
        ),
        revenue_rankings AS (
            SELECT 
                *,
                RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
                RANK() OVER (ORDER BY total_units DESC) as units_rank,
                RANK() OVER (ORDER BY total_orders DESC) as orders_rank,
                NTILE(3) OVER (ORDER BY total_revenue DESC) as revenue_tier
            FROM revenue_summary
        )
        SELECT 
            category,
            supplier,
            active_days,
            total_orders,
            total_customers,
            total_units,
            total_revenue,
            avg_daily_revenue,
            avg_unit_price,
            revenue_rank,
            units_rank,
            orders_rank,
            revenue_tier,
            CASE 
                WHEN revenue_tier = 1 THEN 'Top Tier'
                WHEN revenue_tier = 2 THEN 'Middle Tier'
                ELSE 'Bottom Tier'
            END as performance_tier
        FROM revenue_rankings
        ORDER BY total_revenue DESC, total_units DESC
        LIMIT 20;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} revenue analytics records")
        
        if results:
            # Analyze performance tiers
            top_tier = [row for row in results if row[13] == 'Top Tier']
            middle_tier = [row for row in results if row[13] == 'Middle Tier']
            
            print(f"   🏆 Top Tier: {len(top_tier)}")
            print(f"   📊 Middle Tier: {len(middle_tier)}")
            
            # Show top performers
            if top_tier:
                total_top_revenue = sum(row[6] for row in top_tier)
                print(f"   💰 Top Tier Revenue: ${total_top_revenue:.2f}")
        
        return results
    
    def test_5_data_quality_comprehensive_check(self):
        """Test 5: Comprehensive data quality check"""
        print("\n🔍 Test 5: Comprehensive Data Quality Check")
        
        quality_checks = [
            {
                "name": "Orphaned Records",
                "query": """
                SELECT 
                    'Orphaned Order Items' as check_type,
                    COUNT(*) as issue_count
                FROM order_items oi
                LEFT JOIN orders o ON oi.order_id = o.id
                WHERE o.id IS NULL
                
                UNION ALL
                
                SELECT 
                    'Orphaned Cart Items' as check_type,
                    COUNT(*) as issue_count
                FROM cart_items ci
                LEFT JOIN cart c ON ci.cart_id = c.id
                WHERE c.id IS NULL
                
                UNION ALL
                
                SELECT 
                    'Products Without Inventory' as check_type,
                    COUNT(*) as issue_count
                FROM products p
                LEFT JOIN inventory i ON p.id = i.product_id
                WHERE i.id IS NULL
                """
            },
            {
                "name": "Data Consistency",
                "query": """
                SELECT 
                    'Orders Without Payments' as check_type,
                    COUNT(*) as issue_count
                FROM orders o
                LEFT JOIN payments p ON o.id = p.order_id
                WHERE p.id IS NULL AND o.status != 'cancelled'
                
                UNION ALL
                
                SELECT 
                    'Duplicate SKUs' as check_type,
                    COUNT(*) as issue_count
                FROM (
                    SELECT sku, COUNT(*) as cnt
                    FROM products
                    WHERE sku IS NOT NULL
                    GROUP BY sku
                    HAVING COUNT(*) > 1
                ) as duplicates
                
                UNION ALL
                
                SELECT 
                    'Invalid Email Formats' as check_type,
                    COUNT(*) as issue_count
                FROM customers
                WHERE email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
                """
            },
            {
                "name": "Business Logic",
                "query": """
                SELECT 
                    'Negative Inventory' as check_type,
                    COUNT(*) as issue_count
                FROM inventory
                WHERE quantity < 0
                
                UNION ALL
                
                SELECT 
                    'Invalid Ratings' as check_type,
                    COUNT(*) as issue_count
                FROM reviews
                WHERE rating < 1 OR rating > 5
                
                UNION ALL
                
                SELECT 
                    'Future Order Dates' as check_type,
                    COUNT(*) as issue_count
                FROM orders
                WHERE order_date > CURRENT_DATE
                """
            }
        ]
        
        quality_results = {}
        
        for check in quality_checks:
            print(f"   🔍 Running: {check['name']}")
            results = self.execute_query(check["query"])
            quality_results[check["name"]] = results
            
            if results:
                total_issues = sum(row[1] for row in results)
                print(f"      Found {total_issues} issues")
                
                for row in results:
                    if row[1] > 0:
                        print(f"      ⚠️  {row[0]}: {row[1]} issues")
            else:
                print(f"      ✅ No issues found")
        
        return quality_results
    
    def test_6_performance_analysis_simple(self):
        """Test 6: Simple performance analysis"""
        print("\n🔍 Test 6: Performance Analysis")
        
        query = """
        SELECT 
            relname as table_name,
            n_live_tup as live_rows,
            n_dead_tup as dead_rows,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            CASE 
                WHEN n_dead_tup > n_live_tup * 0.1 THEN 'Needs VACUUM'
                WHEN n_dead_tup > n_live_tup * 0.05 THEN 'Consider VACUUM'
                ELSE 'OK'
            END as maintenance_status
        FROM pg_stat_user_tables
        ORDER BY n_dead_tup DESC, n_live_tup DESC;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} tables with performance metrics")
        
        if results:
            needs_vacuum = [row for row in results if 'Needs VACUUM' in row[6]]
            consider_vacuum = [row for row in results if 'Consider VACUUM' in row[6]]
            
            print(f"   ⚠️  Tables needing VACUUM: {len(needs_vacuum)}")
            print(f"   ⚠️  Tables to consider VACUUM: {len(consider_vacuum)}")
            
            for row in needs_vacuum[:3]:
                print(f"      {row[0]}: {row[2]} dead rows, {row[1]} live rows")
        
        return results

def run_final_comprehensive_analysis():
    """Run final comprehensive SQL analysis"""
    print("🚀 Starting Final Comprehensive SQL Database Analysis")
    print("=" * 70)
    
    analyzer = FinalSQLAnalysis()
    analyzer.setup_method()
    
    results = {}
    
    # Run all tests
    test_methods = [
        analyzer.test_1_comprehensive_customer_analysis,
        analyzer.test_2_product_performance_deep_dive,
        analyzer.test_3_order_workflow_complete_analysis,
        analyzer.test_4_revenue_analytics_comprehensive,
        analyzer.test_5_data_quality_comprehensive_check,
        analyzer.test_6_performance_analysis_simple
    ]
    
    for i, test_method in enumerate(test_methods, 1):
        try:
            print(f"\n{'='*25} Final Test {i} {'='*25}")
            result = test_method()
            results[f"final_test_{i}"] = result
        except Exception as e:
            print(f"❌ Final Test {i} failed: {e}")
            results[f"final_test_{i}"] = {"error": str(e)}
    
    # Generate comprehensive analysis report
    print("\n" + "="*70)
    print("📊 FINAL COMPREHENSIVE SQL DATABASE ANALYSIS REPORT")
    print("="*70)
    
    # Customer Analysis Summary
    if "final_test_1" in results and results["final_test_1"]:
        customer_results = results["final_test_1"]
        print(f"\n👥 CUSTOMER ANALYSIS:")
        print(f"   Total Customers Analyzed: {len(customer_results)}")
        
        if customer_results:
            vip_count = len([row for row in customer_results if row[16] == 'VIP'])
            regular_count = len([row for row in customer_results if row[16] == 'Regular'])
            total_revenue = sum(row[6] for row in customer_results)
            
            print(f"   VIP Customers: {vip_count}")
            print(f"   Regular Customers: {regular_count}")
            print(f"   Total Revenue: ${total_revenue:.2f}")
    
    # Product Analysis Summary
    if "final_test_2" in results and results["final_test_2"]:
        product_results = results["final_test_2"]
        print(f"\n📦 PRODUCT ANALYSIS:")
        print(f"   Total Products Analyzed: {len(product_results)}")
        
        if product_results:
            high_performers = len([row for row in product_results if row[19] == 'High Performer'])
            category_leaders = len([row for row in product_results if row[15] == 1])
            total_product_revenue = sum(row[9] for row in product_results)
            
            print(f"   High Performers: {high_performers}")
            print(f"   Category Leaders: {category_leaders}")
            print(f"   Total Product Revenue: ${total_product_revenue:.2f}")
    
    # Order Analysis Summary
    if "final_test_3" in results and results["final_test_3"]:
        order_results = results["final_test_3"]
        print(f"\n📋 ORDER ANALYSIS:")
        print(f"   Total Orders Analyzed: {len(order_results)}")
        
        if order_results:
            fully_processed = len([row for row in order_results if row[19] == 'Fully Processed'])
            fast_delivery = len([row for row in order_results if row[20] == 'Fast Delivery'])
            total_order_value = sum(row[3] for row in order_results)
            
            print(f"   Fully Processed: {fully_processed}")
            print(f"   Fast Delivery: {fast_delivery}")
            print(f"   Total Order Value: ${total_order_value:.2f}")
    
    # Revenue Analysis Summary
    if "final_test_4" in results and results["final_test_4"]:
        revenue_results = results["final_test_4"]
        print(f"\n💰 REVENUE ANALYSIS:")
        print(f"   Revenue Records Analyzed: {len(revenue_results)}")
        
        if revenue_results:
            top_tier = len([row for row in revenue_results if row[13] == 'Top Tier'])
            total_revenue = sum(row[6] for row in revenue_results)
            
            print(f"   Top Tier Performers: {top_tier}")
            print(f"   Total Revenue: ${total_revenue:.2f}")
    
    # Data Quality Summary
    if "final_test_5" in results and isinstance(results["final_test_5"], dict):
        quality_results = results["final_test_5"]
        print(f"\n🔍 DATA QUALITY ANALYSIS:")
        
        total_issues = 0
        for check_name, check_results in quality_results.items():
            if check_results:
                check_issues = sum(row[1] for row in check_results)
                total_issues += check_issues
                if check_issues > 0:
                    print(f"   ⚠️  {check_name}: {check_issues} issues")
                else:
                    print(f"   ✅ {check_name}: No issues")
        
        if total_issues == 0:
            print(f"   🎉 EXCELLENT: No data quality issues found!")
        elif total_issues < 5:
            print(f"   ✅ GOOD: Only {total_issues} minor issues found")
        else:
            print(f"   ⚠️  ATTENTION: {total_issues} issues need attention")
    
    # Performance Summary
    if "final_test_6" in results and results["final_test_6"]:
        perf_results = results["final_test_6"]
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        print(f"   Tables Analyzed: {len(perf_results)}")
        
        if perf_results:
            needs_vacuum = len([row for row in perf_results if 'Needs VACUUM' in row[6]])
            consider_vacuum = len([row for row in perf_results if 'Consider VACUUM' in row[6]])
            
            if needs_vacuum > 0:
                print(f"   ⚠️  Tables needing VACUUM: {needs_vacuum}")
            if consider_vacuum > 0:
                print(f"   ⚠️  Tables to consider VACUUM: {consider_vacuum}")
            if needs_vacuum == 0 and consider_vacuum == 0:
                print(f"   ✅ All tables in good condition")
    
    # Final Recommendations
    print(f"\n💡 FINAL RECOMMENDATIONS:")
    
    # Data Quality Recommendations
    if "final_test_5" in results and isinstance(results["final_test_5"], dict):
        quality_results = results["final_test_5"]
        for check_name, check_results in quality_results.items():
            if check_results:
                for row in check_results:
                    if row[1] > 0:
                        print(f"   🔧 Address {row[0]} issues")
    
    # Performance Recommendations
    if "final_test_6" in results and results["final_test_6"]:
        perf_results = results["final_test_6"]
        needs_vacuum = [row for row in perf_results if 'Needs VACUUM' in row[6]]
        if needs_vacuum:
            print(f"   🔧 Run VACUUM on tables with high dead row counts")
    
    # Business Recommendations
    if "final_test_1" in results and results["final_test_1"]:
        customer_results = results["final_test_1"]
        if customer_results:
            prospects = len([row for row in customer_results if row[16] == 'Prospect'])
            if prospects > 0:
                print(f"   📈 Focus on converting {prospects} prospects to customers")
    
    print(f"\n✅ Final comprehensive SQL analysis completed!")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    run_final_comprehensive_analysis() 