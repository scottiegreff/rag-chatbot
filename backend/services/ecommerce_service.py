from backend.models.ecommerce import Customer, Product, Order, Category, Address, Wishlist, Review, ProductImage, Inventory, OrderItem, Shipping, Payment, Cart, CartItem, WishlistItem, Discount
from backend.database import SessionLocal
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

# Pydantic models for service functions
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

# Customer CRUD operations
def get_customers() -> List[Customer]:
    """Get all customers"""
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        return customers
    finally:
        db.close()

def get_customer(customer_id: int) -> Optional[Customer]:
    """Get a specific customer by ID"""
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        return customer
    finally:
        db.close()

def create_customer(customer_data: Dict[str, Any]) -> Customer:
    """Create a new customer"""
    db = SessionLocal()
    try:
        customer = Customer(**customer_data)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    finally:
        db.close()

def update_customer(customer_id: int, customer_data: Dict[str, Any]) -> Optional[Customer]:
    """Update an existing customer"""
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        for key, value in customer_data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        
        db.commit()
        db.refresh(customer)
        return customer
    finally:
        db.close()

def delete_customer(customer_id: int) -> bool:
    """Delete a customer"""
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False
        
        db.delete(customer)
        db.commit()
        return True
    finally:
        db.close()

# Product CRUD operations
def get_products() -> List[Product]:
    """Get all products"""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return products
    finally:
        db.close()

def get_product(product_id: int) -> Optional[Product]:
    """Get a specific product by ID"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        return product
    finally:
        db.close()

def get_products_by_category(category_id: int) -> List[Product]:
    """Get products by category"""
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.category_id == category_id).all()
        return products
    finally:
        db.close()

def create_product(product_data: Dict[str, Any]) -> Product:
    """Create a new product"""
    db = SessionLocal()
    try:
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    finally:
        db.close()

def update_product(product_id: int, product_data: Dict[str, Any]) -> Optional[Product]:
    """Update an existing product"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product
    finally:
        db.close()

def delete_product(product_id: int) -> bool:
    """Delete a product"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True
    finally:
        db.close()

# Category CRUD operations
def get_categories() -> List[Category]:
    """Get all categories"""
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return categories
    finally:
        db.close()

def get_category(category_id: int) -> Optional[Category]:
    """Get a specific category by ID"""
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        return category
    finally:
        db.close()

# Order CRUD operations
def get_orders() -> List[Order]:
    """Get all orders"""
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        return orders
    finally:
        db.close()

def get_order(order_id: int) -> Optional[Order]:
    """Get a specific order by ID"""
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        return order
    finally:
        db.close()

def get_customer_orders(customer_id: int) -> List[Order]:
    """Get all orders for a specific customer"""
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.customer_id == customer_id).all()
        return orders
    finally:
        db.close()

def get_customer_addresses(customer_id: int) -> List[Address]:
    db = SessionLocal()
    try:
        addresses = db.query(Address).filter(Address.customer_id == customer_id).all()
        return addresses
    finally:
        db.close()

def get_customer_wishlists(customer_id: int) -> List[Wishlist]:
    db = SessionLocal()
    try:
        wishlists = db.query(Wishlist).filter(Wishlist.customer_id == customer_id).all()
        return wishlists
    finally:
        db.close()

def get_customer_reviews(customer_id: int) -> List[Review]:
    db = SessionLocal()
    try:
        reviews = db.query(Review).filter(Review.customer_id == customer_id).all()
        return reviews
    finally:
        db.close()

def get_product_reviews(product_id: int) -> List[Review]:
    db = SessionLocal()
    try:
        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        return reviews
    finally:
        db.close()

def get_all_inventory() -> List[Inventory]:
    """Get all inventory items"""
    db = SessionLocal()
    try:
        inventory = db.query(Inventory).all()
        return inventory
    finally:
        db.close()

def get_product_inventory(product_id: int) -> Optional[Inventory]:
    db = SessionLocal()
    try:
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        return inventory
    finally:
        db.close()

def get_product_images(product_id: int) -> List[ProductImage]:
    db = SessionLocal()
    try:
        images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
        return images
    finally:
        db.close()

def create_order_for_customer(customer_id: int, order_data: Dict[str, Any]) -> Order:
    db = SessionLocal()
    try:
        order = Order(customer_id=customer_id, **order_data)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    finally:
        db.close()

def add_item_to_order(order_id: int, item_data: Dict[str, Any]) -> OrderItem:
    db = SessionLocal()
    try:
        item = OrderItem(order_id=order_id, **item_data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()

def get_order_shipping(order_id: int) -> Optional[Shipping]:
    """Get shipping information for an order"""
    db = SessionLocal()
    try:
        return db.query(Shipping).filter(Shipping.order_id == order_id).first()
    finally:
        db.close()

def get_order_payments(order_id: int) -> List[Payment]:
    """Get payments for an order"""
    db = SessionLocal()
    try:
        return db.query(Payment).filter(Payment.order_id == order_id).all()
    finally:
        db.close()

def get_customer_cart(customer_id: int) -> Optional[Cart]:
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        return cart
    finally:
        db.close()

def add_item_to_cart(cart_id: int, item_data: Dict[str, Any]) -> CartItem:
    db = SessionLocal()
    try:
        item = CartItem(cart_id=cart_id, **item_data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()

def remove_item_from_cart(cart_id: int, item_id: int) -> bool:
    db = SessionLocal()
    try:
        item = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.id == item_id).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
    finally:
        db.close()

# Business Logic Functions

def check_stock_availability(product_id: int, quantity: int) -> bool:
    """Check if product has sufficient stock"""
    db = SessionLocal()
    try:
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            return False
        return inventory.quantity >= quantity
    finally:
        db.close()

def update_inventory(product_id: int, quantity_change: int) -> bool:
    """Update inventory (positive for restock, negative for sale)"""
    db = SessionLocal()
    try:
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            return False
        
        new_quantity = inventory.quantity + quantity_change
        if new_quantity < 0:
            return False  # Prevent negative inventory
        
        inventory.quantity = new_quantity
        db.commit()
        return True
    finally:
        db.close()

def calculate_order_total(order_id: int) -> Dict[str, float]:
    """Calculate order total including subtotal, tax, shipping, and discounts"""
    db = SessionLocal()
    try:
        # Get order items
        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"error": "Order not found"}
        
        # Calculate subtotal
        subtotal = sum(Decimal(str(item.price)) * item.quantity for item in items)
        
        # Calculate tax (simplified - 8.5% tax rate)
        tax_rate = Decimal('0.085')
        tax = subtotal * tax_rate
        
        # Calculate shipping (simplified - $10 flat rate for orders under $100)
        shipping = Decimal('0.0') if subtotal >= Decimal('100.0') else Decimal('10.0')
        
        # Apply discounts if any
        discount_amount = Decimal('0.0')
        discount = db.query(Discount).filter(Discount.active == True).first()
        if discount and discount.discount_percent:
            discount_amount = subtotal * (Decimal(str(discount.discount_percent)) / Decimal('100'))
        
        # Calculate final total
        total = subtotal + tax + shipping - discount_amount
        
        return {
            "subtotal": float(subtotal),
            "tax": float(tax),
            "shipping": float(shipping),
            "discount": float(discount_amount),
            "total": float(total)
        }
    finally:
        db.close()

def ensure_customer_cart(customer_id: int) -> Cart:
    """Ensure customer has a cart, create if doesn't exist"""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart:
            cart = Cart(customer_id=customer_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart
    finally:
        db.close()

def add_item_to_cart_with_checks(customer_id: int, product_id: int, quantity: int) -> Dict[str, Any]:
    """Add item to cart with stock and duplicate checks"""
    db = SessionLocal()
    try:
        # Check stock availability
        if not check_stock_availability(product_id, quantity):
            return {"success": False, "error": "Insufficient stock"}
        
        # Ensure customer has a cart
        cart = ensure_customer_cart(customer_id)
        
        # Check for existing item in cart
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        
        if existing_item:
            # Update quantity if item already exists
            new_quantity = existing_item.quantity + quantity
            if not check_stock_availability(product_id, new_quantity):
                return {"success": False, "error": "Insufficient stock for updated quantity"}
            existing_item.quantity = new_quantity
            db.commit()
            db.refresh(existing_item)
            return {"success": True, "item": existing_item, "action": "updated"}
        else:
            # Add new item
            item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.add(item)
            db.commit()
            db.refresh(item)
            return {"success": True, "item": item, "action": "added"}
    finally:
        db.close()

def create_order_with_validation(customer_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create order with stock validation and total calculation"""
    db = SessionLocal()
    try:
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        # Create order
        order = Order(customer_id=customer_id, **order_data)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return {"success": True, "order": order}
    finally:
        db.close()

def add_item_to_order_with_validation(order_id: int, product_id: int, quantity: int, price: float) -> Dict[str, Any]:
    """Add item to order with stock validation"""
    db = SessionLocal()
    try:
        # Check stock availability
        if not check_stock_availability(product_id, quantity):
            return {"success": False, "error": "Insufficient stock"}
        
        # Check if order exists
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"success": False, "error": "Order not found"}
        
        # Add item to order
        item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        db.add(item)
        
        # Update inventory
        if not update_inventory(product_id, -quantity):
            db.rollback()
            return {"success": False, "error": "Failed to update inventory"}
        
        db.commit()
        db.refresh(item)
        
        # Recalculate order total
        total_info = calculate_order_total(order_id)
        order.total = total_info["total"]
        db.commit()
        
        # Get the item ID before closing the session
        item_id = item.id
        
        return {"success": True, "item_id": item_id, "order_total": total_info}
    finally:
        db.close()

def update_order_status(order_id: int, new_status: str) -> Dict[str, Any]:
    """Update order status with validation"""
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    
    if new_status not in valid_statuses:
        return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
    
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"success": False, "error": "Order not found"}
        
        # Update status
        order.status = new_status
        
        # Update shipping info if status is "shipped"
        if new_status == "shipped":
            shipping = db.query(Shipping).filter(Shipping.order_id == order_id).first()
            if shipping:
                shipping.shipped_date = datetime.utcnow()
                shipping.status = "in_transit"
        
        # Update shipping info if status is "delivered"
        if new_status == "delivered":
            shipping = db.query(Shipping).filter(Shipping.order_id == order_id).first()
            if shipping:
                shipping.delivery_date = datetime.utcnow()
                shipping.status = "delivered"
        
        db.commit()
        return {"success": True, "order": order}
    finally:
        db.close()

def get_cart_total(customer_id: int) -> Dict[str, float]:
    """Calculate cart total"""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart:
            return {"subtotal": 0.0, "total": 0.0}
        
        # Get cart items with product prices
        items = db.query(CartItem, Product).join(Product).filter(CartItem.cart_id == cart.id).all()
        
        subtotal = sum(item.CartItem.quantity * item.Product.price for item in items)
        
        # Apply discount if available
        discount = db.query(Discount).filter(Discount.active == True).first()
        discount_amount = 0.0
        if discount and discount.discount_percent:
            discount_amount = subtotal * (discount.discount_percent / 100)
        
        total = subtotal - discount_amount
        
        return {
            "subtotal": float(subtotal),
            "discount": float(discount_amount),
            "total": float(total)
        }
    finally:
        db.close()

def create_customer_order(customer_id: int, order_data: Dict[str, Any]) -> Order:
    """Create an order for a specific customer"""
    db = SessionLocal()
    try:
        order = Order(customer_id=customer_id, **order_data)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    finally:
        db.close()

def add_order_item(order_id: int, item: OrderItemCreate) -> OrderItem:
    """Add an item to an order"""
    db = SessionLocal()
    try:
        order_item = OrderItem(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)
        db.commit()
        db.refresh(order_item)
        return order_item
    finally:
        db.close()

def add_cart_item(customer_id: int, item: CartItemCreate) -> CartItem:
    """Add an item to a customer's cart"""
    db = SessionLocal()
    try:
        # Ensure customer has a cart
        cart = ensure_customer_cart(customer_id)
        
        # Check if item already exists in cart
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += item.quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Add new item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item
    finally:
        db.close()

def remove_cart_item(customer_id: int, item_id: int) -> bool:
    """Remove an item from a customer's cart"""
    db = SessionLocal()
    try:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart:
            return False
        
        cart_item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        ).first()
        
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        return True
    finally:
        db.close() 