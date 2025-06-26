"""
Database Query Service for PostgreSQL Integration with RAG
Enables the chatbot to query and understand database content
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from backend.database import SessionLocal, engine
from backend.models.ecommerce import Customer, Product, Order, Category, Address, Wishlist, Review, ProductImage, Inventory, OrderItem, Shipping, Payment, Cart, CartItem, WishlistItem, Discount

logger = logging.getLogger(__name__)

class DatabaseQueryService:
    """Service for safely querying the PostgreSQL database"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.inspector = inspect(engine)
    
    def get_table_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            tables = {}
            for table_name in self.inspector.get_table_names():
                columns = []
                for column in self.inspector.get_columns(table_name):
                    columns.append({
                        'name': column['name'],
                        'type': str(column['type']),
                        'nullable': column['nullable']
                    })
                tables[table_name] = columns
            return tables
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return {}
    
    def get_table_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all tables"""
        try:
            summary = {}
            for table_name in self.inspector.get_table_names():
                count_query = text(f"SELECT COUNT(*) as count FROM {table_name}")
                result = self.db.execute(count_query).fetchone()
                summary[table_name] = result.count if result else 0
            return summary
        except Exception as e:
            logger.error(f"Error getting table summary: {e}")
            return {}
    
    def safe_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a safe SQL query with restrictions"""
        try:
            # Basic security checks
            query_lower = query.lower().strip()
            
            # Only allow SELECT queries
            if not query_lower.startswith('select'):
                return {
                    'success': False,
                    'error': 'Only SELECT queries are allowed for security reasons'
                }
            
            # Prevent potentially dangerous operations
            dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 'truncate']
            for keyword in dangerous_keywords:
                if keyword in query_lower:
                    return {
                        'success': False,
                        'error': f'Query contains forbidden keyword: {keyword}'
                    }
            
            # Add LIMIT if not present
            if 'limit' not in query_lower:
                query += f" LIMIT {limit}"
            
            # Execute query
            result = self.db.execute(text(query))
            
            # Convert to list of dictionaries
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            
            return {
                'success': True,
                'data': rows,
                'count': len(rows),
                'query': query
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database query error: {e}")
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def get_customer_info(self, customer_id: int) -> Dict[str, Any]:
        """Get detailed customer information"""
        try:
            customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return {'success': False, 'error': 'Customer not found'}
            
            # Get customer orders
            orders = self.db.query(Order).filter(Order.customer_id == customer_id).all()
            
            # Get customer cart
            cart = self.db.query(Cart).filter(Cart.customer_id == customer_id).first()
            
            return {
                'success': True,
                'customer': {
                    'id': customer.id,
                    'name': f"{customer.first_name} {customer.last_name}",
                    'email': customer.email,
                    'phone': customer.phone,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None
                },
                'orders_count': len(orders),
                'has_cart': cart is not None
            }
        except Exception as e:
            logger.error(f"Error getting customer info: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_order_details(self, order_id: int) -> Dict[str, Any]:
        """Get detailed order information"""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {'success': False, 'error': 'Order not found'}
            
            # Get order items
            items = self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            # Get customer info
            customer = self.db.query(Customer).filter(Customer.id == order.customer_id).first()
            
            return {
                'success': True,
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'total': float(order.total) if order.total else 0.0,
                    'order_date': order.order_date.isoformat() if order.order_date else None
                },
                'customer': {
                    'id': customer.id,
                    'name': f"{customer.first_name} {customer.last_name}",
                    'email': customer.email
                } if customer else None,
                'items_count': len(items),
                'items': [
                    {
                        'product_id': item.product_id,
                        'quantity': item.quantity,
                        'price': float(item.price)
                    } for item in items
                ]
            }
        except Exception as e:
            logger.error(f"Error getting order details: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_product_info(self, product_id: int) -> Dict[str, Any]:
        """Get detailed product information"""
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {'success': False, 'error': 'Product not found'}
            
            # Get inventory
            inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
            
            # Get category
            category = self.db.query(Category).filter(Category.id == product.category_id).first()
            
            return {
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price),
                    'sku': product.sku,
                    'created_at': product.created_at.isoformat() if product.created_at else None
                },
                'category': category.name if category else None,
                'inventory': inventory.quantity if inventory else 0
            }
        except Exception as e:
            logger.error(f"Error getting product info: {e}")
            return {'success': False, 'error': str(e)}
    
    def search_products(self, search_term: str, limit: int = 10) -> Dict[str, Any]:
        """Search products by name or description"""
        try:
            query = self.db.query(Product).filter(
                Product.name.ilike(f'%{search_term}%') |
                Product.description.ilike(f'%{search_term}%')
            ).limit(limit)
            
            products = query.all()
            
            return {
                'success': True,
                'products': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'description': p.description,
                        'price': float(p.price),
                        'sku': p.sku
                    } for p in products
                ],
                'count': len(products)
            }
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_sales_summary(self) -> Dict[str, Any]:
        """Get sales summary statistics"""
        try:
            # Total orders
            total_orders = self.db.query(Order).count()
            
            # Total revenue
            revenue_query = text("SELECT COALESCE(SUM(total), 0) as total_revenue FROM orders WHERE total IS NOT NULL")
            revenue_result = self.db.execute(revenue_query).fetchone()
            total_revenue = float(revenue_result.total_revenue) if revenue_result else 0.0
            
            # Orders by status
            status_query = text("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
            status_results = self.db.execute(status_query).fetchall()
            orders_by_status = {row.status: row.count for row in status_results}
            
            return {
                'success': True,
                'summary': {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'orders_by_status': orders_by_status
                }
            }
        except Exception as e:
            logger.error(f"Error getting sales summary: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_latest_order(self) -> Dict[str, Any]:
        """Get the most recent order with customer information"""
        try:
            # Get the most recent order
            latest_order = self.db.query(Order).order_by(Order.order_date.desc()).first()
            if not latest_order:
                return {'success': False, 'error': 'No orders found'}
            
            # Get customer info
            customer = self.db.query(Customer).filter(Customer.id == latest_order.customer_id).first()
            
            # Get order items
            items = self.db.query(OrderItem).filter(OrderItem.order_id == latest_order.id).all()
            
            return {
                'success': True,
                'order': {
                    'id': latest_order.id,
                    'status': latest_order.status,
                    'total': float(latest_order.total) if latest_order.total else 0.0,
                    'order_date': latest_order.order_date.isoformat() if latest_order.order_date else None
                },
                'customer': {
                    'id': customer.id,
                    'name': f"{customer.first_name} {customer.last_name}",
                    'email': customer.email
                } if customer else None,
                'items_count': len(items),
                'items': [
                    {
                        'product_id': item.product_id,
                        'quantity': item.quantity,
                        'price': float(item.price)
                    } for item in items
                ]
            }
        except Exception as e:
            logger.error(f"Error getting latest order: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and attempt to extract database information.
        
        Args:
            query: Natural language query
            
        Returns:
            Dict containing processed results or None if not a database query
        """
        try:
            query_lower = query.lower().strip()
            
            # Check for customer-related queries
            if any(word in query_lower for word in ['customer', 'customers', 'client', 'clients']):
                if 'count' in query_lower or 'how many' in query_lower:
                    return self.safe_query("SELECT COUNT(*) as customer_count FROM customers")
                elif 'list' in query_lower or 'show' in query_lower:
                    return self.safe_query("SELECT id, first_name, last_name, email FROM customers ORDER BY id LIMIT 10")
                else:
                    return self.safe_query("SELECT id, first_name, last_name, email, created_at FROM customers ORDER BY created_at DESC LIMIT 5")
            
            # Check for product-related queries
            elif any(word in query_lower for word in ['product', 'products', 'item', 'items']):
                if 'count' in query_lower or 'how many' in query_lower:
                    return self.safe_query("SELECT COUNT(*) as product_count FROM products")
                elif 'list' in query_lower or 'show' in query_lower:
                    return self.safe_query("SELECT id, name, price, sku FROM products ORDER BY id LIMIT 10")
                else:
                    return self.safe_query("SELECT id, name, description, price, sku FROM products ORDER BY created_at DESC LIMIT 5")
            
            # Check for order-related queries
            elif any(word in query_lower for word in ['order', 'orders', 'purchase', 'purchases']):
                if 'count' in query_lower or 'how many' in query_lower:
                    return self.safe_query("SELECT COUNT(*) as order_count FROM orders")
                elif 'latest' in query_lower or 'recent' in query_lower:
                    return self.safe_query("SELECT o.id, o.status, o.total, o.order_date, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.order_date DESC LIMIT 5")
                else:
                    return self.safe_query("SELECT id, status, total, order_date FROM orders ORDER BY order_date DESC LIMIT 10")
            
            # Check for sales/revenue queries
            elif any(word in query_lower for word in ['sales', 'revenue', 'total', 'amount', 'money']):
                return self.safe_query("SELECT SUM(total) as total_revenue, COUNT(*) as total_orders FROM orders WHERE status = 'completed'")
            
            # Check for inventory queries
            elif any(word in query_lower for word in ['inventory', 'stock', 'quantity']):
                return self.safe_query("SELECT p.name, i.quantity FROM inventory i JOIN products p ON i.product_id = p.id ORDER BY i.quantity ASC LIMIT 10")
            
            # Check for category queries
            elif any(word in query_lower for word in ['category', 'categories']):
                return self.safe_query("SELECT c.name, COUNT(p.id) as product_count FROM categories c LEFT JOIN products p ON c.id = p.category_id GROUP BY c.id, c.name ORDER BY product_count DESC")
            
            # If no specific pattern matches, return None to indicate this isn't a database query
            return None
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

# Global instance
db_query_service = DatabaseQueryService() 