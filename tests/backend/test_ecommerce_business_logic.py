#!/usr/bin/env python3
"""
Test script for e-commerce business logic features
Tests stock checks, order total calculation, cart management, and order status updates
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/ecommerce"

def test_stock_checks():
    """Test stock availability checks"""
    print("\n=== Testing Stock Checks ===")
    
    # Test checking stock for product 1
    stock_check = {
        "product_id": 1,
        "quantity": 5
    }
    
    response = requests.post(f"{BASE_URL}/stock/check", json=stock_check)
    print(f"Stock check response: {response.json()}")
    
    # Test checking stock for product that doesn't exist
    stock_check_invalid = {
        "product_id": 999,
        "quantity": 1
    }
    
    response = requests.post(f"{BASE_URL}/stock/check", json=stock_check_invalid)
    print(f"Invalid stock check response: {response.json()}")

def test_inventory_updates():
    """Test inventory updates"""
    print("\n=== Testing Inventory Updates ===")
    
    # Test restocking product 1
    restock = {
        "product_id": 1,
        "quantity_change": 10
    }
    
    response = requests.post(f"{BASE_URL}/inventory/update", json=restock)
    print(f"Restock response: {response.json()}")
    
    # Test selling product 1
    sale = {
        "product_id": 1,
        "quantity_change": -3
    }
    
    response = requests.post(f"{BASE_URL}/inventory/update", json=sale)
    print(f"Sale response: {response.json()}")

def test_cart_management():
    """Test cart management with business logic"""
    print("\n=== Testing Cart Management ===")
    
    # Add item to cart for customer 1
    cart_item = {
        "customer_id": 1,
        "product_id": 1,
        "quantity": 2
    }
    
    response = requests.post(f"{BASE_URL}/cart/add-item", json=cart_item)
    print(f"Add to cart response: {response.json()}")
    
    # Try to add same item again (should update quantity)
    response = requests.post(f"{BASE_URL}/cart/add-item", json=cart_item)
    print(f"Add duplicate item response: {response.json()}")
    
    # Get cart total
    response = requests.get(f"{BASE_URL}/cart/1/total")
    print(f"Cart total response: {response.json()}")
    
    # Try to add more than available stock
    overstock_item = {
        "customer_id": 1,
        "product_id": 1,
        "quantity": 100
    }
    
    response = requests.post(f"{BASE_URL}/cart/add-item", json=overstock_item)
    print(f"Overstock attempt response: {response.json()}")

def test_order_creation_and_management():
    """Test order creation and management"""
    print("\n=== Testing Order Creation and Management ===")
    
    # Create new order
    order_data = {
        "customer_id": 1,
        "status": "pending",
        "notes": "Test order with business logic"
    }
    
    response = requests.post(f"{BASE_URL}/orders/create", json=order_data)
    print(f"Create order response: {response.json()}")
    
    if response.json()["success"]:
        order_id = response.json()["order_id"]
        
        # Add item to order
        order_item = {
            "order_id": order_id,
            "product_id": 1,
            "quantity": 2,
            "price": 29.99
        }
        
        response = requests.post(f"{BASE_URL}/orders/add-item", json=order_item)
        print(f"Add item to order response: {response.json()}")
        
        # Get order total
        response = requests.get(f"{BASE_URL}/orders/{order_id}/total")
        print(f"Order total response: {response.json()}")
        
        # Update order status
        status_update = {
            "new_status": "processing"
        }
        
        response = requests.put(f"{BASE_URL}/orders/{order_id}/status", json=status_update)
        print(f"Update status response: {response.json()}")
        
        # Try invalid status
        invalid_status = {
            "new_status": "invalid_status"
        }
        
        response = requests.put(f"{BASE_URL}/orders/{order_id}/status", json=invalid_status)
        print(f"Invalid status response: {response.json()}")

def test_order_status_transitions():
    """Test order status transitions"""
    print("\n=== Testing Order Status Transitions ===")
    
    # Create another order for status testing
    order_data = {
        "customer_id": 2,
        "status": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/orders/create", json=order_data)
    print(f"Create test order response: {response.json()}")
    
    if response.json()["success"]:
        order_id = response.json()["order_id"]
        
        # Test status transitions
        statuses = ["processing", "shipped", "delivered"]
        
        for status in statuses:
            status_update = {"new_status": status}
            response = requests.put(f"{BASE_URL}/orders/{order_id}/status", json=status_update)
            print(f"Status update to '{status}': {response.json()}")

def test_integrated_workflow():
    """Test a complete e-commerce workflow"""
    print("\n=== Testing Integrated Workflow ===")
    
    # 1. Check stock
    stock_check = {"product_id": 2, "quantity": 3}
    response = requests.post(f"{BASE_URL}/stock/check", json=stock_check)
    print(f"1. Stock check: {response.json()}")
    
    # 2. Add to cart
    cart_item = {"customer_id": 3, "product_id": 2, "quantity": 3}
    response = requests.post(f"{BASE_URL}/cart/add-item", json=cart_item)
    print(f"2. Add to cart: {response.json()}")
    
    # 3. Get cart total
    response = requests.get(f"{BASE_URL}/cart/3/total")
    print(f"3. Cart total: {response.json()}")
    
    # 4. Create order
    order_data = {"customer_id": 3, "status": "pending"}
    response = requests.post(f"{BASE_URL}/orders/create", json=order_data)
    print(f"4. Create order: {response.json()}")
    
    if response.json()["success"]:
        order_id = response.json()["order_id"]
        
        # 5. Add item to order
        order_item = {"order_id": order_id, "product_id": 2, "quantity": 3, "price": 49.99}
        response = requests.post(f"{BASE_URL}/orders/add-item", json=order_item)
        print(f"5. Add to order: {response.json()}")
        
        # 6. Get order total
        response = requests.get(f"{BASE_URL}/orders/{order_id}/total")
        print(f"6. Order total: {response.json()}")
        
        # 7. Update status
        status_update = {"new_status": "processing"}
        response = requests.put(f"{BASE_URL}/orders/{order_id}/status", json=status_update)
        print(f"7. Update status: {response.json()}")

def main():
    """Run all business logic tests"""
    print("Testing E-commerce Business Logic Features")
    print("=" * 50)
    
    try:
        test_stock_checks()
        test_inventory_updates()
        test_cart_management()
        test_order_creation_and_management()
        test_order_status_transitions()
        test_integrated_workflow()
        
        print("\n" + "=" * 50)
        print("All business logic tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main() 