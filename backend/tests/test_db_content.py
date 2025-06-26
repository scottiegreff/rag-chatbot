#!/usr/bin/env python3
"""
Test script to check database content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.database_query_service import db_query_service

def test_db_content():
    """Check what's in the database"""
    
    print("Checking database content...")
    
    # Get table summary
    print("\n1. Table Summary:")
    summary = db_query_service.get_table_summary()
    for table, count in summary.items():
        print(f"   {table}: {count} records")
    
    # Get latest order
    print("\n2. Latest Order:")
    latest_order = db_query_service.get_latest_order()
    if latest_order.get('success'):
        order = latest_order['order']
        customer = latest_order['customer']
        print(f"   Order ID: {order['id']}")
        print(f"   Status: {order['status']}")
        print(f"   Total: ${order['total']}")
        print(f"   Date: {order['order_date']}")
        if customer:
            print(f"   Customer: {customer['name']} ({customer['email']})")
        print(f"   Items: {latest_order['items_count']}")
    else:
        print(f"   Error: {latest_order.get('error', 'Unknown error')}")
    
    # Get all orders
    print("\n3. All Orders:")
    orders_result = db_query_service.safe_query("SELECT id, customer_id, status, total, order_date FROM orders ORDER BY order_date DESC LIMIT 5")
    if orders_result.get('success'):
        for order in orders_result['data']:
            print(f"   Order {order['id']}: ${order['total']} - {order['status']} - {order['order_date']}")
    else:
        print(f"   Error: {orders_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_db_content() 