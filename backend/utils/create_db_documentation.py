#!/usr/bin/env python3
"""
Create comprehensive database documentation for RAG ingestion
This generates detailed schema information that can be used by the RAG system
to better understand database structure and relationships.
"""

import sys
import os
from pathlib import Path
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.database import engine, SessionLocal

def create_database_documentation():
    """Create comprehensive database documentation for RAG ingestion"""
    
    print("📚 Creating database documentation for RAG ingestion...")
    
    documentation = []
    
    try:
        # Get database inspector
        inspector = inspect(engine)
        
        # Get all table names
        table_names = inspector.get_table_names()
        
        # Create table documentation
        for table_name in table_names:
            print(f"📋 Documenting table: {table_name}")
            
            # Get table columns
            columns = inspector.get_columns(table_name)
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            
            # Create table documentation
            table_doc = f"""
# Table: {table_name}

## Description
This table stores {table_name.replace('_', ' ')} data in the e-commerce system.

## Columns:
"""
            
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                table_doc += f"- **{column['name']}**: {column['type']} ({nullable})\n"
            
            if foreign_keys:
                table_doc += "\n## Foreign Key Relationships:\n"
                for fk in foreign_keys:
                    table_doc += f"- **{fk['constrained_columns']}** → **{fk['referred_table']}.{fk['referred_columns']}**\n"
            
            if indexes:
                table_doc += "\n## Indexes:\n"
                for idx in indexes:
                    table_doc += f"- **{idx['name']}**: {idx['column_names']}\n"
            
            # Add sample queries for this table
            table_doc += f"""
## Common Queries for {table_name}:

### Count records:
```sql
SELECT COUNT(*) FROM {table_name};
```

### Get all records (limited):
```sql
SELECT * FROM {table_name} LIMIT 10;
```

### Get recent records:
```sql
SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT 5;
```
"""
            
            documentation.append(table_doc)
        
        # Create relationship documentation
        relationships_doc = """
# Database Relationships

## Key Relationships in the E-commerce System:

### Customer Relationships:
- **customers** → **addresses** (one-to-many): Customers can have multiple addresses
- **customers** → **orders** (one-to-many): Customers can place multiple orders
- **customers** → **cart** (one-to-one): Each customer has one shopping cart
- **customers** → **wishlists** (one-to-one): Each customer has one wishlist
- **customers** → **reviews** (one-to-many): Customers can write multiple reviews

### Product Relationships:
- **products** → **categories** (many-to-one): Products belong to categories
- **products** → **suppliers** (many-to-one): Products are supplied by suppliers
- **products** → **inventory** (one-to-one): Each product has inventory information
- **products** → **product_images** (one-to-many): Products can have multiple images
- **products** → **order_items** (one-to-many): Products can be in multiple orders
- **products** → **cart_items** (one-to-many): Products can be in multiple carts
- **products** → **wishlist_items** (one-to-many): Products can be in multiple wishlists
- **products** → **reviews** (one-to-many): Products can have multiple reviews

### Order Relationships:
- **orders** → **customers** (many-to-one): Orders belong to customers
- **orders** → **addresses** (many-to-one): Orders have shipping and billing addresses
- **orders** → **order_items** (one-to-many): Orders contain multiple items
- **orders** → **payments** (one-to-many): Orders can have multiple payments
- **orders** → **shipping** (one-to-one): Orders have shipping information

### Shopping Cart Relationships:
- **cart** → **customers** (many-to-one): Carts belong to customers
- **cart** → **cart_items** (one-to-many): Carts contain multiple items
- **cart_items** → **products** (many-to-one): Cart items reference products

### Wishlist Relationships:
- **wishlists** → **customers** (many-to-one): Wishlists belong to customers
- **wishlists** → **wishlist_items** (one-to-many): Wishlists contain multiple items
- **wishlist_items** → **products** (many-to-one): Wishlist items reference products

## Business Logic Relationships:

### Inventory Management:
- Products are linked to inventory to track stock levels
- Order items reduce inventory when orders are placed
- Low inventory can trigger restocking alerts

### Customer Analytics:
- Customer orders are linked to customer profiles
- Order history helps with customer segmentation
- Customer reviews provide product feedback

### Product Management:
- Products are categorized for better organization
- Supplier information helps with procurement
- Product images enhance the shopping experience

### Order Processing:
- Orders go through multiple stages: pending → paid → shipped → delivered
- Payments are tracked separately from orders
- Shipping information includes tracking and delivery dates
"""
        
        documentation.append(relationships_doc)
        
        # Create query examples documentation
        query_examples_doc = """
# Common Database Query Examples

## Customer Queries:

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

### Get customers from specific state:
```sql
SELECT c.first_name, c.last_name, a.city, a.state
FROM customers c
JOIN addresses a ON c.id = a.customer_id
WHERE a.state = 'CA';
```

## Product Queries:

### Get products by category:
```sql
SELECT p.name, p.price, c.name as category
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE c.name = 'Electronics';
```

### Find products with low inventory:
```sql
SELECT p.name, i.quantity
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE i.quantity < 10;
```

### Get most expensive products:
```sql
SELECT name, price, sku
FROM products
ORDER BY price DESC
LIMIT 5;
```

## Order Queries:

### Calculate total revenue:
```sql
SELECT SUM(total) as total_revenue FROM orders;
```

### Get average order value:
```sql
SELECT AVG(total) as average_order_value FROM orders;
```

### Find recent orders:
```sql
SELECT o.id, o.total, o.order_date, c.first_name, c.last_name
FROM orders o
JOIN customers c ON o.customer_id = c.id
ORDER BY o.order_date DESC
LIMIT 10;
```

### Get orders by status:
```sql
SELECT COUNT(*) as order_count, status
FROM orders
GROUP BY status;
```

## Sales Analytics:

### Revenue by category:
```sql
SELECT c.name as category, SUM(oi.quantity * oi.price) as revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY c.name
ORDER BY revenue DESC;
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

### Customer lifetime value:
```sql
SELECT c.first_name, c.last_name, COUNT(o.id) as order_count, SUM(o.total) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
HAVING COUNT(o.id) > 1
ORDER BY total_spent DESC;
```

## Inventory Management:

### Products out of stock:
```sql
SELECT p.name, i.quantity
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE i.quantity = 0;
```

### Low stock alerts:
```sql
SELECT p.name, i.quantity, p.price
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE i.quantity < 5;
```

## Shopping Cart Analysis:

### Abandoned carts:
```sql
SELECT c.id, c.created_at, COUNT(ci.id) as items_in_cart
FROM cart c
JOIN cart_items ci ON c.id = ci.cart_id
WHERE c.created_at < NOW() - INTERVAL '7 days'
GROUP BY c.id, c.created_at;
```

### Cart value analysis:
```sql
SELECT AVG(cart_total) as average_cart_value
FROM (
    SELECT c.id, SUM(ci.quantity * p.price) as cart_total
    FROM cart c
    JOIN cart_items ci ON c.id = ci.cart_id
    JOIN products p ON ci.product_id = p.id
    GROUP BY c.id
) as cart_totals;
```
"""
        
        documentation.append(query_examples_doc)
        
        # Create business rules documentation
        business_rules_doc = """
# Business Rules and Constraints

## Data Integrity Rules:

### Customer Rules:
- Each customer must have a unique email address
- Customer phone numbers are optional
- Customers are created with a timestamp

### Product Rules:
- All products must have a name and price
- Products must belong to a category
- Products must have a unique SKU
- Product prices cannot be negative

### Order Rules:
- Orders must be associated with a customer
- Orders have a status: pending, paid, shipped, delivered
- Order totals are calculated from order items
- Orders can have separate shipping and billing addresses

### Inventory Rules:
- Inventory quantities cannot be negative
- Each product has exactly one inventory record
- Low inventory (quantity < 5) should trigger alerts

### Payment Rules:
- Payments are associated with orders
- Payment amounts should match order totals
- Payment status: pending, completed, failed

### Shipping Rules:
- Shipping is associated with orders
- Tracking numbers are optional
- Delivery dates are estimated

## Business Logic:

### Order Processing:
1. Customer adds items to cart
2. Customer places order (cart becomes order)
3. Payment is processed
4. Order is shipped
5. Order is delivered

### Inventory Management:
- Inventory is reduced when orders are placed
- Low stock triggers restocking alerts
- Products can be discontinued (set quantity to 0)

### Customer Management:
- New customers are created when they first place an order
- Customer addresses are stored for shipping/billing
- Customer preferences are tracked through wishlists

### Product Management:
- Products are organized by categories
- Products have multiple images
- Products are supplied by suppliers
- Product reviews help with quality assessment

## Common Business Questions:

### Revenue Analysis:
- What is our total revenue?
- What is our revenue by category?
- What is our average order value?
- What is our revenue growth over time?

### Customer Analysis:
- How many customers do we have?
- Who are our top customers?
- What is customer lifetime value?
- Where are our customers located?

### Product Analysis:
- What are our best-selling products?
- What products are out of stock?
- What is our inventory value?
- What products have the highest margins?

### Operational Analysis:
- How many orders do we process?
- What is our order fulfillment rate?
- How long does shipping take?
- What is our customer satisfaction rate?
"""
        
        documentation.append(business_rules_doc)
        
        # Save documentation to file
        output_file = Path(__file__).parent.parent.parent / "database_documentation.txt"
        with open(output_file, 'w') as f:
            f.write('\n\n'.join(documentation))
        
        print(f"✅ Database documentation created: {output_file}")
        print(f"📄 Total documentation size: {len('\n\n'.join(documentation))} characters")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error creating database documentation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_database_documentation() 