#!/usr/bin/env python3
"""
SQL Context Builder - Provides schema and example queries for SQL agents
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.database import engine

class SQLContextBuilder:
    """Builds comprehensive SQL context for agents"""
    
    def __init__(self):
        self.schema_cache = None
        self.examples_cache = None
    
    def get_database_schema(self) -> str:
        """Get the complete database schema as a string"""
        if self.schema_cache:
            return self.schema_cache
            
        try:
            inspector = inspect(engine)
            schema_parts = ["# Database Schema\n"]
            
            for table_name in inspector.get_table_names():
                schema_parts.append(f"## Table: {table_name}")
                
                # Get columns
                columns = inspector.get_columns(table_name)
                for column in columns:
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    default = f" DEFAULT {column['default']}" if column.get('default') else ""
                    schema_parts.append(f"- {column['name']}: {column['type']} {nullable}{default}")
                
                # Get primary keys
                pk = inspector.get_pk_constraint(table_name)
                if pk['constrained_columns']:
                    schema_parts.append(f"- Primary Key: {', '.join(pk['constrained_columns'])}")
                
                # Get foreign keys
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    schema_parts.append(f"- Foreign Key: {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
                
                schema_parts.append("")  # Empty line between tables
            
            self.schema_cache = "\n".join(schema_parts)
            return self.schema_cache
            
        except Exception as e:
            return f"# Database Schema\nError retrieving schema: {e}"
    
    def get_example_queries(self) -> str:
        """Get example SQL queries for common operations"""
        if self.examples_cache:
            return self.examples_cache
            
        examples = """# Example SQL Queries

## Customer Queries

### Count total customers:
```sql
SELECT COUNT(*) as total_customers FROM customers;
```

### Get customer with highest order value:
```sql
SELECT c.first_name, c.last_name, SUM(o.total) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 1;
```

### Top 5 customers by total spending:
```sql
SELECT c.first_name, c.last_name, SUM(o.total) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 5;
```

### Customer lifetime value:
```sql
SELECT c.first_name, c.last_name, COUNT(o.id) as order_count, SUM(o.total) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spent DESC;
```

## Product Queries

### Count total products:
```sql
SELECT COUNT(*) as total_products FROM products;
```

### Products by category:
```sql
SELECT c.name as category, COUNT(p.id) as product_count
FROM products p
JOIN categories c ON p.category_id = c.id
GROUP BY c.id, c.name
ORDER BY product_count DESC;
```

### Top selling products:
```sql
SELECT p.name, SUM(oi.quantity) as total_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 10;
```

### Products with low inventory:
```sql
SELECT p.name, i.quantity
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE i.quantity < 10;
```

### Most expensive products:
```sql
SELECT name, price, sku
FROM products
ORDER BY price DESC
LIMIT 5;
```

## Order Queries

### Calculate total revenue:
```sql
SELECT SUM(total) as total_revenue FROM orders;
```

### Get average order value:
```sql
SELECT AVG(total) as average_order_value FROM orders;
```

### Orders by status:
```sql
SELECT status, COUNT(*) as count
FROM orders
GROUP BY status
ORDER BY count DESC;
```

### Recent orders:
```sql
SELECT o.id, c.first_name, c.last_name, o.total, o.status, o.created_at
FROM orders o
JOIN customers c ON o.customer_id = c.id
ORDER BY o.created_at DESC
LIMIT 10;
```

## Revenue and Sales Queries

### Revenue by category:
```sql
SELECT c.name as category, SUM(oi.quantity * oi.price) as revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY c.name
ORDER BY revenue DESC;
```

### Monthly revenue:
```sql
SELECT DATE_TRUNC('month', created_at) as month, SUM(total) as revenue
FROM orders
GROUP BY month
ORDER BY month DESC;
```

## Inventory Queries

### Low stock products:
```sql
SELECT p.name, i.quantity, p.price
FROM inventory i
JOIN products p ON i.product_id = p.id
WHERE i.quantity < 10
ORDER BY i.quantity ASC;
```

### Out of stock products:
```sql
SELECT p.name, p.price
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE i.quantity = 0;
```
"""
        
        self.examples_cache = examples
        return self.examples_cache
    
    def get_business_rules(self) -> str:
        """Get business rules and domain knowledge"""
        rules = """# Business Rules and Domain Knowledge

## E-commerce Business Context
- This is an e-commerce platform with customers, products, orders, and inventory
- Orders can have multiple items (order_items table)
- Products belong to categories and have inventory tracking
- Customers can have multiple addresses (shipping/billing)
- Orders have status tracking (pending, shipped, delivered, etc.)

## Key Relationships
- customers -> orders (one-to-many)
- orders -> order_items (one-to-many)
- products -> order_items (one-to-many)
- products -> inventory (one-to-one)
- customers -> addresses (one-to-many)
- products -> categories (many-to-one)

## Business Metrics
- Revenue = SUM(order_items.quantity * order_items.price)
- Average Order Value = AVG(orders.total)
- Customer Lifetime Value = SUM of all orders per customer
- Product Performance = SUM of quantities sold per product

## Data Quality Rules
- All prices are stored as NUMERIC(10,2) with 2 decimal places
- Order totals are calculated from order_items (quantity * price)
- Customer emails are unique and required
- Product names and prices are required fields
- Order dates use TIMESTAMP with timezone awareness

## Common Business Queries
- Top customers by total spending
- Best selling products by quantity
- Revenue by category or time period
- Inventory levels and low stock alerts
- Customer order frequency and patterns
"""
        return rules
    
    def get_data_insights(self) -> str:
        """Get data insights and common patterns"""
        insights = """# Data Insights and Query Patterns

## Common Aggregation Patterns
- Customer analysis: GROUP BY customer_id, customer_name
- Product analysis: GROUP BY product_id, product_name, category
- Time-based analysis: GROUP BY DATE_TRUNC('month', created_at)
- Revenue analysis: SUM(quantity * price) or SUM(total)

## Join Patterns
- Customer orders: customers JOIN orders ON customer_id
- Order details: orders JOIN order_items ON order_id
- Product info: order_items JOIN products ON product_id
- Category analysis: products JOIN categories ON category_id
- Inventory check: products JOIN inventory ON product_id

## Filtering Best Practices
- Active orders: WHERE status != 'cancelled'
- Recent data: WHERE created_at >= NOW() - INTERVAL '30 days'
- Valid products: WHERE price > 0 AND name IS NOT NULL
- Stocked items: WHERE inventory.quantity > 0

## Sorting Patterns
- Revenue: ORDER BY total_spent DESC
- Recent activity: ORDER BY created_at DESC
- Performance: ORDER BY quantity_sold DESC
- Alphabetical: ORDER BY name ASC

## Common Calculations
- Percentage: (value / total) * 100
- Growth rate: ((current - previous) / previous) * 100
- Running totals: SUM() OVER (ORDER BY date)
- Rankings: ROW_NUMBER() OVER (ORDER BY value DESC)
"""
        return insights
    
    def build_sql_context(self, query: str) -> str:
        """Build comprehensive SQL context for a query"""
        schema = self.get_database_schema()
        examples = self.get_example_queries()
        business_rules = self.get_business_rules()
        data_insights = self.get_data_insights()
        
        context = f"""# SQL Agent Context

{schema}

{business_rules}

{data_insights}

{examples}

# User Query
{query}

# Instructions
Based on the schema, business rules, and examples above, generate the appropriate SQL query to answer the user's question.
Consider the business context and data relationships when crafting your query.
Always use proper SQL syntax and join tables when needed to get complete information.
For aggregations, consider using appropriate functions like SUM(), AVG(), COUNT(), etc.
When dealing with dates, use proper date functions and consider time zones if relevant.
"""
        
        return context
    
    def get_relevant_examples(self, query: str) -> str:
        """Get only relevant examples based on the query"""
        query_lower = query.lower()
        all_examples = self.get_example_queries()
        
        # Extract relevant sections based on keywords
        relevant_sections = []
        
        if any(word in query_lower for word in ['customer', 'customers']):
            relevant_sections.append("## Customer Queries")
        if any(word in query_lower for word in ['product', 'products']):
            relevant_sections.append("## Product Queries")
        if any(word in query_lower for word in ['order', 'orders']):
            relevant_sections.append("## Order Queries")
        if any(word in query_lower for word in ['revenue', 'sales', 'total']):
            relevant_sections.append("## Revenue and Sales Queries")
        if any(word in query_lower for word in ['inventory', 'stock']):
            relevant_sections.append("## Inventory Queries")
        
        # If no specific section matches, return all examples
        if not relevant_sections:
            return all_examples
        
        # Extract the relevant sections from the full examples
        lines = all_examples.split('\n')
        result_lines = []
        include_section = False
        
        for line in lines:
            if line.startswith('## ') and line in relevant_sections:
                include_section = True
                result_lines.append(line)
            elif line.startswith('## ') and line not in relevant_sections:
                include_section = False
            elif include_section:
                result_lines.append(line)
        
        return '\n'.join(result_lines)

# Global instance
_sql_context_builder = None

def get_sql_context_builder() -> SQLContextBuilder:
    """Get the global SQL context builder instance"""
    global _sql_context_builder
    if _sql_context_builder is None:
        _sql_context_builder = SQLContextBuilder()
    return _sql_context_builder 