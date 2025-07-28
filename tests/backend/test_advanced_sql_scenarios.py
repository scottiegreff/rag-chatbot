"""
Advanced SQL Test Scenarios
Tests edge cases, complex joins, window functions, and advanced analytics
"""

import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime, timedelta
import json

class TestAdvancedSQLScenarios:
    """Advanced SQL test scenarios for edge cases and complex queries"""
    
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
    
    def test_1_window_functions_ranking(self):
        """Test 1: Advanced window functions with ranking and partitioning"""
        print("\n🔍 Test 1: Window Functions with Ranking")
        
        query = """
        WITH product_rankings AS (
            SELECT 
                p.id,
                p.name,
                p.price,
                c.name as category,
                COALESCE(SUM(oi.quantity), 0) as total_sold,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.id) as review_count,
                ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY COALESCE(SUM(oi.quantity * oi.price), 0) DESC) as revenue_rank_in_category,
                RANK() OVER (ORDER BY COALESCE(SUM(oi.quantity * oi.price), 0) DESC) as overall_revenue_rank,
                DENSE_RANK() OVER (ORDER BY COALESCE(AVG(r.rating), 0) DESC) as quality_rank,
                LAG(p.price) OVER (PARTITION BY c.id ORDER BY p.price) as prev_price_in_category,
                LEAD(p.price) OVER (PARTITION BY c.id ORDER BY p.price) as next_price_in_category,
                NTILE(4) OVER (ORDER BY COALESCE(SUM(oi.quantity * oi.price), 0) DESC) as revenue_quartile
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN reviews r ON p.id = r.product_id
            GROUP BY p.id, p.name, p.price, c.id, c.name
        )
        SELECT 
            id,
            name,
            price,
            category,
            total_sold,
            total_revenue,
            avg_rating,
            review_count,
            revenue_rank_in_category,
            overall_revenue_rank,
            quality_rank,
            prev_price_in_category,
            next_price_in_category,
            revenue_quartile,
            CASE 
                WHEN revenue_rank_in_category = 1 THEN 'Category Leader'
                WHEN revenue_quartile = 1 THEN 'Top Performer'
                WHEN revenue_quartile = 2 THEN 'Good Performer'
                WHEN revenue_quartile = 3 THEN 'Average Performer'
                ELSE 'Low Performer'
            END as performance_tier
        FROM product_rankings
        ORDER BY overall_revenue_rank
        LIMIT 15;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} products with advanced rankings")
        
        if results:
            # Show category leaders
            category_leaders = [row for row in results if row[8] == 1]
            print(f"   🏆 Category Leaders: {len(category_leaders)}")
            for row in category_leaders[:3]:
                print(f"      {row[3]}: {row[1]} (Revenue: ${row[5]:.2f})")
        
        return results
    
    def test_2_recursive_cte_hierarchy(self):
        """Test 2: Recursive CTE for hierarchical data analysis"""
        print("\n🔍 Test 2: Recursive CTE Hierarchy Analysis")
        
        # First, let's create a simple hierarchy based on customer spending tiers
        query = """
        WITH RECURSIVE customer_hierarchy AS (
            -- Base case: Top spenders (VIP customers)
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                COALESCE(SUM(o.total), 0) as total_spent,
                1 as level,
                ARRAY[c.id] as path,
                c.first_name || ' ' || c.last_name as hierarchy_path
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id, c.first_name, c.last_name
            HAVING COALESCE(SUM(o.total), 0) >= 1000
            
            UNION ALL
            
            -- Recursive case: Find customers with similar spending patterns
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                COALESCE(SUM(o.total), 0) as total_spent,
                ch.level + 1,
                ch.path || c.id,
                ch.hierarchy_path || ' -> ' || c.first_name || ' ' || c.last_name
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            JOIN customer_hierarchy ch ON 
                ABS(COALESCE(SUM(o.total), 0) - ch.total_spent) < 200
                AND c.id != ALL(ch.path)
            GROUP BY c.id, c.first_name, c.last_name, ch.level, ch.path, ch.hierarchy_path
            HAVING ch.level < 3
        )
        SELECT 
            id,
            first_name,
            last_name,
            total_spent,
            level,
            hierarchy_path,
            CASE 
                WHEN level = 1 THEN 'VIP Tier'
                WHEN level = 2 THEN 'Similar Spending'
                ELSE 'Extended Network'
            END as hierarchy_level
        FROM customer_hierarchy
        ORDER BY level, total_spent DESC
        LIMIT 20;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} customers in hierarchy analysis")
        
        if results:
            for level in range(1, 4):
                level_customers = [row for row in results if row[4] == level]
                if level_customers:
                    print(f"   Level {level}: {len(level_customers)} customers")
        
        return results
    
    def test_3_advanced_aggregation_pivot(self):
        """Test 3: Advanced aggregation with pivot-like analysis"""
        print("\n🔍 Test 3: Advanced Aggregation with Pivot Analysis")
        
        query = """
        WITH category_pivot AS (
            SELECT 
                c.name as category,
                COUNT(DISTINCT p.id) as total_products,
                COUNT(DISTINCT CASE WHEN i.quantity = 0 THEN p.id END) as out_of_stock,
                COUNT(DISTINCT CASE WHEN i.quantity < 10 THEN p.id END) as low_stock,
                COUNT(DISTINCT CASE WHEN i.quantity >= 10 THEN p.id END) as well_stocked,
                COALESCE(SUM(CASE WHEN i.quantity > 0 THEN i.quantity * p.price END), 0) as inventory_value,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.id) as total_reviews
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            LEFT JOIN inventory i ON p.id = i.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN reviews r ON p.id = r.product_id
            GROUP BY c.id, c.name
        ),
        supplier_pivot AS (
            SELECT 
                s.name as supplier,
                COUNT(DISTINCT p.id) as total_products,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(DISTINCT r.id) as total_reviews
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN reviews r ON p.id = r.product_id
            GROUP BY s.id, s.name
        )
        SELECT 
            'Category Analysis' as analysis_type,
            category as name,
            total_products,
            out_of_stock,
            low_stock,
            well_stocked,
            inventory_value,
            total_revenue,
            avg_rating,
            total_reviews
        FROM category_pivot
        
        UNION ALL
        
        SELECT 
            'Supplier Analysis' as analysis_type,
            supplier as name,
            total_products,
            NULL as out_of_stock,
            NULL as low_stock,
            NULL as well_stocked,
            NULL as inventory_value,
            total_revenue,
            avg_rating,
            total_reviews
        FROM supplier_pivot
        ORDER BY analysis_type, total_revenue DESC;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} pivot analysis records")
        
        if results:
            categories = [row for row in results if row[0] == 'Category Analysis']
            suppliers = [row for row in results if row[0] == 'Supplier Analysis']
            
            print(f"   📊 Categories: {len(categories)}")
            print(f"   📊 Suppliers: {len(suppliers)}")
            
            # Show top categories by revenue
            for row in categories[:3]:
                print(f"      {row[1]}: Revenue ${row[7]:.2f}, Products: {row[2]}")
        
        return results
    
    def test_4_complex_date_analysis(self):
        """Test 4: Complex date-based analysis with time series"""
        print("\n🔍 Test 4: Complex Date Analysis")
        
        query = """
        WITH date_series AS (
            SELECT 
                DATE(o.order_date) as order_date,
                COUNT(DISTINCT o.id) as daily_orders,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                COALESCE(SUM(o.total), 0) as daily_revenue,
                COALESCE(AVG(o.total), 0) as avg_order_value
            FROM orders o
            GROUP BY DATE(o.order_date)
        ),
        date_analysis AS (
            SELECT 
                order_date,
                daily_orders,
                unique_customers,
                daily_revenue,
                avg_order_value,
                LAG(daily_revenue) OVER (ORDER BY order_date) as prev_day_revenue,
                LEAD(daily_revenue) OVER (ORDER BY order_date) as next_day_revenue,
                AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg_3d,
                SUM(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as weekly_revenue
            FROM date_series
        )
        SELECT 
            order_date,
            daily_orders,
            unique_customers,
            daily_revenue,
            avg_order_value,
            prev_day_revenue,
            next_day_revenue,
            moving_avg_3d,
            weekly_revenue,
            CASE 
                WHEN daily_revenue > moving_avg_3d * 1.2 THEN 'Above Trend'
                WHEN daily_revenue < moving_avg_3d * 0.8 THEN 'Below Trend'
                ELSE 'On Trend'
            END as trend_status,
            CASE 
                WHEN daily_revenue > prev_day_revenue THEN 'Increasing'
                WHEN daily_revenue < prev_day_revenue THEN 'Decreasing'
                ELSE 'Stable'
            END as day_over_day
        FROM date_analysis
        ORDER BY order_date DESC
        LIMIT 10;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} date analysis records")
        
        if results:
            # Analyze trends
            above_trend = [row for row in results if 'Above Trend' in row[9]]
            below_trend = [row for row in results if 'Below Trend' in row[9]]
            
            print(f"   📈 Above Trend Days: {len(above_trend)}")
            print(f"   📉 Below Trend Days: {len(below_trend)}")
        
        return results
    
    def test_5_advanced_join_patterns(self):
        """Test 5: Advanced join patterns with multiple conditions"""
        print("\n🔍 Test 5: Advanced Join Patterns")
        
        query = """
        WITH customer_product_analysis AS (
            SELECT 
                c.id as customer_id,
                c.first_name,
                c.last_name,
                c.email,
                p.id as product_id,
                p.name as product_name,
                p.price as product_price,
                c2.name as category,
                COUNT(DISTINCT o.id) as times_ordered,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_spent_on_product,
                r.rating as customer_rating,
                r.comment as customer_review,
                CASE 
                    WHEN wi.product_id IS NOT NULL THEN 'In Wishlist'
                    WHEN ci.product_id IS NOT NULL THEN 'In Cart'
                    ELSE 'Not Saved'
                END as product_status
            FROM customers c
            CROSS JOIN products p
            LEFT JOIN categories c2 ON p.category_id = c2.id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.customer_id = c.id
            LEFT JOIN reviews r ON p.id = r.product_id AND r.customer_id = c.id
            LEFT JOIN wishlists w ON c.id = w.customer_id
            LEFT JOIN wishlist_items wi ON w.id = wi.wishlist_id AND wi.product_id = p.id
            LEFT JOIN cart ca ON c.id = ca.customer_id
            LEFT JOIN cart_items ci ON ca.id = ci.cart_id AND ci.product_id = p.id
            GROUP BY c.id, c.first_name, c.last_name, c.email, p.id, p.name, p.price, c2.name, r.rating, r.comment, wi.product_id, ci.product_id
        )
        SELECT 
            customer_id,
            first_name,
            last_name,
            product_name,
            category,
            product_price,
            times_ordered,
            total_quantity,
            total_spent_on_product,
            customer_rating,
            product_status,
            CASE 
                WHEN times_ordered > 0 THEN 'Purchased'
                WHEN product_status = 'In Wishlist' THEN 'Interested'
                WHEN product_status = 'In Cart' THEN 'Considering'
                ELSE 'Not Engaged'
            END as engagement_level
        FROM customer_product_analysis
        WHERE times_ordered > 0 OR product_status != 'Not Saved'
        ORDER BY customer_id, total_spent_on_product DESC
        LIMIT 20;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} customer-product relationships")
        
        if results:
            # Analyze engagement levels
            engagement_counts = {}
            for row in results:
                level = row[11]
                engagement_counts[level] = engagement_counts.get(level, 0) + 1
            
            print("   📊 Engagement Levels:")
            for level, count in engagement_counts.items():
                print(f"      {level}: {count} interactions")
        
        return results
    
    def test_6_performance_optimization_queries(self):
        """Test 6: Performance optimization and query analysis"""
        print("\n🔍 Test 6: Performance Optimization Analysis")
        
        # Check for slow queries and optimization opportunities
        query = """
        WITH table_stats AS (
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation,
                most_common_vals,
                most_common_freqs
            FROM pg_stats
            WHERE schemaname = 'public'
        ),
        index_usage AS (
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
        ),
        table_activity AS (
            SELECT 
                relname as table_name,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_rows,
                n_dead_tup as dead_rows,
                n_tup_hot_upd as hot_updates,
                CASE 
                    WHEN n_dead_tup > n_live_tup * 0.1 THEN 'Needs VACUUM'
                    WHEN n_dead_tup > n_live_tup * 0.05 THEN 'Consider VACUUM'
                    ELSE 'OK'
                END as maintenance_status
            FROM pg_stat_user_tables
        )
        SELECT 
            ta.table_name,
            ta.live_rows,
            ta.dead_rows,
            ta.inserts,
            ta.updates,
            ta.deletes,
            ta.maintenance_status,
            COUNT(i.indexname) as index_count,
            COALESCE(SUM(i.idx_scan), 0) as total_index_scans
        FROM table_activity ta
        LEFT JOIN index_usage i ON ta.table_name = i.tablename
        GROUP BY ta.table_name, ta.live_rows, ta.dead_rows, ta.inserts, ta.updates, ta.deletes, ta.maintenance_status
        ORDER BY ta.dead_rows DESC, ta.live_rows DESC;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} tables with performance metrics")
        
        if results:
            # Identify tables needing attention
            needs_vacuum = [row for row in results if 'Needs VACUUM' in row[6]]
            consider_vacuum = [row for row in results if 'Consider VACUUM' in row[6]]
            
            print(f"   ⚠️  Tables needing VACUUM: {len(needs_vacuum)}")
            print(f"   ⚠️  Tables to consider VACUUM: {len(consider_vacuum)}")
            
            for row in needs_vacuum[:3]:
                print(f"      {row[0]}: {row[2]} dead rows, {row[1]} live rows")
        
        return results
    
    def test_7_complex_business_logic(self):
        """Test 7: Complex business logic scenarios"""
        print("\n🔍 Test 7: Complex Business Logic Scenarios")
        
        query = """
        WITH customer_lifetime_value AS (
            SELECT 
                c.id,
                c.first_name,
                c.last_name,
                c.email,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(o.total), 0) as total_spent,
                COALESCE(AVG(o.total), 0) as avg_order_value,
                MIN(o.order_date) as first_order,
                MAX(o.order_date) as last_order,
                EXTRACT(DAYS FROM (MAX(o.order_date) - MIN(o.order_date))) as customer_lifespan_days,
                COUNT(DISTINCT r.id) as total_reviews,
                COALESCE(AVG(r.rating), 0) as avg_rating
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            LEFT JOIN reviews r ON c.id = r.customer_id
            GROUP BY c.id, c.first_name, c.last_name, c.email
        ),
        customer_segments AS (
            SELECT 
                *,
                CASE 
                    WHEN total_spent >= 1000 AND total_orders >= 3 THEN 'VIP'
                    WHEN total_spent >= 500 AND total_orders >= 2 THEN 'Regular'
                    WHEN total_spent >= 100 THEN 'Occasional'
                    WHEN total_spent > 0 THEN 'One-time'
                    ELSE 'Prospect'
                END as spending_segment,
                CASE 
                    WHEN customer_lifespan_days > 365 THEN 'Long-term'
                    WHEN customer_lifespan_days > 90 THEN 'Medium-term'
                    WHEN customer_lifespan_days > 30 THEN 'Short-term'
                    ELSE 'New'
                END as tenure_segment,
                CASE 
                    WHEN avg_rating >= 4.5 THEN 'Highly Satisfied'
                    WHEN avg_rating >= 4.0 THEN 'Satisfied'
                    WHEN avg_rating >= 3.0 THEN 'Neutral'
                    WHEN avg_rating > 0 THEN 'Dissatisfied'
                    ELSE 'No Reviews'
                END as satisfaction_segment
            FROM customer_lifetime_value
        ),
        business_insights AS (
            SELECT 
                spending_segment,
                tenure_segment,
                satisfaction_segment,
                COUNT(*) as customer_count,
                AVG(total_spent) as avg_spent,
                AVG(total_orders) as avg_orders,
                AVG(avg_rating) as avg_rating,
                SUM(total_spent) as segment_revenue
            FROM customer_segments
            GROUP BY spending_segment, tenure_segment, satisfaction_segment
        )
        SELECT 
            spending_segment,
            tenure_segment,
            satisfaction_segment,
            customer_count,
            avg_spent,
            avg_orders,
            avg_rating,
            segment_revenue,
            ROUND(segment_revenue / SUM(segment_revenue) OVER() * 100, 2) as revenue_percentage,
            CASE 
                WHEN customer_count >= 5 AND avg_spent >= 500 THEN 'High Priority'
                WHEN customer_count >= 3 AND avg_spent >= 200 THEN 'Medium Priority'
                ELSE 'Low Priority'
            END as business_priority
        FROM business_insights
        ORDER BY segment_revenue DESC, customer_count DESC;
        """
        
        results = self.execute_query(query)
        print(f"✅ Found {len(results)} business insight segments")
        
        if results:
            # Analyze high priority segments
            high_priority = [row for row in results if 'High Priority' in row[9]]
            print(f"   🎯 High Priority Segments: {len(high_priority)}")
            
            for row in high_priority:
                print(f"      {row[0]}-{row[1]}-{row[2]}: {row[3]} customers, ${row[7]:.2f} revenue")
        
        return results
    
    def test_8_edge_case_scenarios(self):
        """Test 8: Edge case scenarios and data anomalies"""
        print("\n🔍 Test 8: Edge Case Scenarios")
        
        edge_cases = [
            {
                "name": "Products with No Sales but High Inventory",
                "query": """
                SELECT 
                    p.id,
                    p.name,
                    p.price,
                    i.quantity as inventory,
                    (i.quantity * p.price) as inventory_value,
                    COUNT(oi.id) as sales_count
                FROM products p
                JOIN inventory i ON p.id = i.product_id
                LEFT JOIN order_items oi ON p.id = oi.product_id
                GROUP BY p.id, p.name, p.price, i.quantity
                HAVING COUNT(oi.id) = 0 AND i.quantity > 50
                ORDER BY inventory_value DESC
                LIMIT 10;
                """
            },
            {
                "name": "Customers with Multiple Orders Same Day",
                "query": """
                SELECT 
                    c.id,
                    c.first_name,
                    c.last_name,
                    DATE(o.order_date) as order_date,
                    COUNT(o.id) as orders_same_day,
                    SUM(o.total) as total_spent_same_day
                FROM customers c
                JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id, c.first_name, c.last_name, DATE(o.order_date)
                HAVING COUNT(o.id) > 1
                ORDER BY orders_same_day DESC, total_spent_same_day DESC
                LIMIT 10;
                """
            },
            {
                "name": "Products with Extreme Price Differences",
                "query": """
                SELECT 
                    c.name as category,
                    p.name as product,
                    p.price,
                    AVG(p.price) OVER (PARTITION BY c.id) as category_avg_price,
                    p.price - AVG(p.price) OVER (PARTITION BY c.id) as price_deviation,
                    ROUND((p.price / AVG(p.price) OVER (PARTITION BY c.id)) * 100, 2) as price_percentage
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.price > AVG(p.price) OVER (PARTITION BY c.id) * 2
                   OR p.price < AVG(p.price) OVER (PARTITION BY c.id) * 0.5
                ORDER BY price_deviation DESC
                LIMIT 10;
                """
            },
            {
                "name": "Orders with Unusual Item Quantities",
                "query": """
                SELECT 
                    o.id as order_id,
                    c.first_name,
                    c.last_name,
                    p.name as product,
                    oi.quantity,
                    oi.price,
                    (oi.quantity * oi.price) as item_total,
                    o.total as order_total,
                    ROUND((oi.quantity * oi.price) / o.total * 100, 2) as percentage_of_order
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE oi.quantity > 10 OR (oi.quantity * oi.price) > o.total * 0.8
                ORDER BY oi.quantity DESC, percentage_of_order DESC
                LIMIT 10;
                """
            }
        ]
        
        edge_case_results = {}
        
        for case in edge_cases:
            print(f"   🔍 Testing: {case['name']}")
            results = self.execute_query(case['query'])
            edge_case_results[case['name']] = results
            
            if results:
                print(f"      Found {len(results)} edge cases")
                if len(results) > 0:
                    print(f"      Example: {results[0]}")
            else:
                print(f"      No edge cases found")
        
        return edge_case_results

def run_advanced_sql_tests():
    """Run all advanced SQL test scenarios"""
    print("🚀 Starting Advanced SQL Test Scenarios")
    print("=" * 60)
    
    test_suite = TestAdvancedSQLScenarios()
    test_suite.setup_method()
    
    results = {}
    
    # Run all tests
    test_methods = [
        test_suite.test_1_window_functions_ranking,
        test_suite.test_2_recursive_cte_hierarchy,
        test_suite.test_3_advanced_aggregation_pivot,
        test_suite.test_4_complex_date_analysis,
        test_suite.test_5_advanced_join_patterns,
        test_suite.test_6_performance_optimization_queries,
        test_suite.test_7_complex_business_logic,
        test_suite.test_8_edge_case_scenarios
    ]
    
    for i, test_method in enumerate(test_methods, 1):
        try:
            print(f"\n{'='*20} Advanced Test {i} {'='*20}")
            result = test_method()
            results[f"advanced_test_{i}"] = result
        except Exception as e:
            print(f"❌ Advanced Test {i} failed: {e}")
            results[f"advanced_test_{i}"] = {"error": str(e)}
    
    # Generate advanced analysis report
    print("\n" + "="*60)
    print("📊 ADVANCED SQL TEST ANALYSIS REPORT")
    print("="*60)
    
    # Window Functions Analysis
    if "advanced_test_1" in results and results["advanced_test_1"]:
        window_results = results["advanced_test_1"]
        print(f"\n📈 Window Functions Analysis:")
        print(f"   Products analyzed: {len(window_results)}")
        if window_results:
            top_performers = [row for row in window_results if 'Top Performer' in row[14]]
            print(f"   Top performers: {len(top_performers)}")
    
    # Edge Cases Analysis
    if "advanced_test_8" in results and isinstance(results["advanced_test_8"], dict):
        edge_cases = results["advanced_test_8"]
        print(f"\n🔍 Edge Cases Analysis:")
        total_edge_cases = sum(len(cases) if cases else 0 for cases in edge_cases.values())
        print(f"   Total edge cases found: {total_edge_cases}")
        
        for case_name, case_results in edge_cases.items():
            if case_results:
                print(f"   {case_name}: {len(case_results)} cases")
    
    # Performance Analysis
    if "advanced_test_6" in results and results["advanced_test_6"]:
        perf_results = results["advanced_test_6"]
        print(f"\n⚡ Performance Analysis:")
        if perf_results:
            needs_vacuum = [row for row in perf_results if 'Needs VACUUM' in row[6]]
            print(f"   Tables needing immediate maintenance: {len(needs_vacuum)}")
    
    print(f"\n✅ Advanced SQL test scenarios completed!")
    return results

if __name__ == "__main__":
    run_advanced_sql_tests() 