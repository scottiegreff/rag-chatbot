from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.services import ecommerce_service
from backend.models.ecommerce import Customer, Product, Order, Category, Address, Wishlist, Review, ProductImage, Inventory, OrderItem, Shipping, Payment, Cart, CartItem, WishlistItem
from backend.services.ecommerce_service import (
    check_stock_availability, update_inventory, calculate_order_total,
    ensure_customer_cart, add_item_to_cart_with_checks, create_order_with_validation,
    add_item_to_order_with_validation, update_order_status, get_cart_total
)

router = APIRouter()

# Pydantic models for request/response validation
class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    phone: Optional[str]
    created_at: Optional[datetime]

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    sku: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    sku: Optional[str] = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    price: float
    category_id: Optional[int]
    supplier_id: Optional[int]
    sku: Optional[str]
    created_at: Optional[datetime]

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    customer_id: int
    order_date: Optional[datetime]
    status: Optional[str]
    shipping_address_id: Optional[int]
    billing_address_id: Optional[int]
    total: Optional[float]

class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    customer_id: int
    address_type: Optional[str]
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    country: Optional[str]

class WishlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    customer_id: int
    created_at: Optional[datetime]

class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    customer_id: Optional[int]
    rating: Optional[int]
    comment: Optional[str]
    created_at: Optional[datetime]

class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    image_url: Optional[str]

class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    quantity: int

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float

class ShippingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    shipped_date: Optional[datetime]
    delivery_date: Optional[datetime]
    carrier: Optional[str]
    tracking_number: Optional[str]
    status: Optional[str]

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    payment_date: Optional[datetime]
    amount: float
    payment_method: Optional[str]
    status: Optional[str]

class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    customer_id: int
    created_at: Optional[datetime]

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    cart_id: int
    product_id: int
    quantity: int

# Customer endpoints
@router.get("/customers", response_model=List[CustomerResponse])
def list_customers():
    """Get all customers"""
    return ecommerce_service.get_customers()

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    """Get a specific customer by ID"""
    customer = ecommerce_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/customers", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate):
    """Create a new customer"""
    return ecommerce_service.create_customer(customer)

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerUpdate):
    """Update a customer"""
    updated_customer = ecommerce_service.update_customer(customer_id, customer)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer

@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    """Delete a customer"""
    success = ecommerce_service.delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# Product endpoints
@router.get("/products", response_model=List[ProductResponse])
def list_products():
    """Get all products"""
    return ecommerce_service.get_products()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    """Get a specific product by ID"""
    product = ecommerce_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories/{category_id}/products", response_model=List[ProductResponse])
def get_products_by_category(category_id: int):
    """Get products by category"""
    return ecommerce_service.get_products_by_category(category_id)

@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate):
    """Create a new product"""
    return ecommerce_service.create_product(product)

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    """Update a product"""
    updated_product = ecommerce_service.update_product(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    """Delete a product"""
    success = ecommerce_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Category endpoints
@router.get("/categories", response_model=List[CategoryResponse])
def list_categories():
    """Get all categories"""
    return ecommerce_service.get_categories()

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int):
    """Get a specific category by ID"""
    category = ecommerce_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Order endpoints
@router.get("/orders", response_model=List[OrderResponse])
def list_orders():
    """Get all orders"""
    return ecommerce_service.get_orders()

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    """Get a specific order by ID"""
    order = ecommerce_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/customers/{customer_id}/orders", response_model=List[OrderResponse])
def get_customer_orders(customer_id: int):
    """Get orders for a specific customer"""
    return ecommerce_service.get_customer_orders(customer_id)

# Customer address endpoints
@router.get("/customers/{customer_id}/addresses", response_model=List[AddressResponse])
def get_customer_addresses(customer_id: int):
    """Get addresses for a specific customer"""
    return ecommerce_service.get_customer_addresses(customer_id)

# Customer wishlist endpoints
@router.get("/customers/{customer_id}/wishlists", response_model=List[WishlistResponse])
def get_customer_wishlists(customer_id: int):
    """Get wishlists for a specific customer"""
    return ecommerce_service.get_customer_wishlists(customer_id)

# Customer review endpoints
@router.get("/customers/{customer_id}/reviews", response_model=List[ReviewResponse])
def get_customer_reviews(customer_id: int):
    """Get reviews by a specific customer"""
    return ecommerce_service.get_customer_reviews(customer_id)

# Product review endpoints
@router.get("/products/{product_id}/reviews", response_model=List[ReviewResponse])
def get_product_reviews(product_id: int):
    """Get reviews for a specific product"""
    return ecommerce_service.get_product_reviews(product_id)

# Product inventory endpoints
@router.get("/products/{product_id}/inventory", response_model=InventoryResponse)
def get_product_inventory(product_id: int):
    """Get inventory for a specific product"""
    inventory = ecommerce_service.get_product_inventory(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

# Product image endpoints
@router.get("/products/{product_id}/images", response_model=List[ProductImageResponse])
def get_product_images(product_id: int):
    """Get images for a specific product"""
    return ecommerce_service.get_product_images(product_id)

# Order endpoints
@router.post("/customers/{customer_id}/orders", response_model=OrderResponse)
def create_order_for_customer(customer_id: int, order: Dict[str, Any]):
    """Create an order for a specific customer"""
    return ecommerce_service.create_customer_order(customer_id, order)

@router.post("/orders/{order_id}/items", response_model=OrderItemResponse)
def add_item_to_order(order_id: int, item: OrderItemCreate):
    """Add an item to an order"""
    return ecommerce_service.add_order_item(order_id, item)

# Shipping endpoints
@router.get("/orders/{order_id}/shipping", response_model=ShippingResponse)
def get_order_shipping(order_id: int):
    """Get shipping information for an order"""
    shipping = ecommerce_service.get_order_shipping(order_id)
    if not shipping:
        raise HTTPException(status_code=404, detail="Shipping information not found")
    return shipping

# Payment endpoints
@router.get("/orders/{order_id}/payments", response_model=List[PaymentResponse])
def get_order_payments(order_id: int):
    """Get payments for an order"""
    return ecommerce_service.get_order_payments(order_id)

# Cart endpoints
@router.get("/customers/{customer_id}/cart", response_model=CartResponse)
def get_customer_cart(customer_id: int):
    """Get cart for a specific customer"""
    cart = ecommerce_service.get_customer_cart(customer_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.post("/customers/{customer_id}/cart/items", response_model=CartItemResponse)
def add_item_to_cart(customer_id: int, item: CartItemCreate):
    """Add an item to a customer's cart"""
    return ecommerce_service.add_cart_item(customer_id, item)

@router.delete("/customers/{customer_id}/cart/items/{item_id}")
def remove_item_from_cart(customer_id: int, item_id: int):
    """Remove an item from a customer's cart"""
    success = ecommerce_service.remove_cart_item(customer_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Cart item removed successfully"}

# Business Logic Endpoints

class StockCheckRequest(BaseModel):
    product_id: int
    quantity: int

class StockCheckResponse(BaseModel):
    available: bool
    message: str

@router.post("/stock/check", response_model=StockCheckResponse)
def check_stock(request: StockCheckRequest):
    """Check if product has sufficient stock"""
    available = check_stock_availability(request.product_id, request.quantity)
    message = "Stock available" if available else "Insufficient stock"
    return StockCheckResponse(available=available, message=message)

class InventoryUpdateRequest(BaseModel):
    product_id: int
    quantity_change: int  # Positive for restock, negative for sale

class InventoryUpdateResponse(BaseModel):
    success: bool
    message: str
    new_quantity: Optional[int] = None

@router.post("/inventory/update", response_model=InventoryUpdateResponse)
def update_inventory_endpoint(request: InventoryUpdateRequest):
    """Update product inventory"""
    success = update_inventory(request.product_id, request.quantity_change)
    if success:
        # Get updated quantity
        from backend.database import SessionLocal
        db = SessionLocal()
        try:
            inventory = db.query(Inventory).filter(Inventory.product_id == request.product_id).first()
            new_quantity = inventory.quantity if inventory else None
        finally:
            db.close()
        
        message = "Inventory updated successfully"
        return InventoryUpdateResponse(success=True, message=message, new_quantity=new_quantity)
    else:
        return InventoryUpdateResponse(success=False, message="Failed to update inventory")

class OrderTotalResponse(BaseModel):
    subtotal: float
    tax: float
    shipping: float
    discount: float
    total: float

@router.get("/orders/{order_id}/total", response_model=OrderTotalResponse)
def get_order_total(order_id: int):
    """Calculate order total including tax, shipping, and discounts"""
    total_info = calculate_order_total(order_id)
    if "error" in total_info:
        raise HTTPException(status_code=404, detail=total_info["error"])
    return OrderTotalResponse(**total_info)

class CartItemAddRequest(BaseModel):
    customer_id: int
    product_id: int
    quantity: int

class CartItemAddResponse(BaseModel):
    success: bool
    message: str
    action: Optional[str] = None
    item_id: Optional[int] = None

@router.post("/cart/add-item", response_model=CartItemAddResponse)
def add_item_to_cart(request: CartItemAddRequest):
    """Add item to cart with stock and duplicate checks"""
    result = add_item_to_cart_with_checks(
        request.customer_id, 
        request.product_id, 
        request.quantity
    )
    
    if result["success"]:
        return CartItemAddResponse(
            success=True,
            message=f"Item {result['action']} to cart successfully",
            action=result["action"],
            item_id=result["item"].id
        )
    else:
        return CartItemAddResponse(success=False, message=result["error"])

class CartTotalResponse(BaseModel):
    subtotal: float
    discount: float
    total: float

@router.get("/cart/{customer_id}/total", response_model=CartTotalResponse)
def get_customer_cart_total(customer_id: int):
    """Get cart total for customer"""
    total_info = get_cart_total(customer_id)
    return CartTotalResponse(**total_info)

class OrderCreateRequest(BaseModel):
    customer_id: int
    status: str = "pending"

class OrderCreateResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[int] = None

@router.post("/orders/create", response_model=OrderCreateResponse)
def create_order(request: OrderCreateRequest):
    """Create new order with validation"""
    order_data = {
        "status": request.status,
        "total": 0.0  # Will be calculated when items are added
    }
    
    result = create_order_with_validation(request.customer_id, order_data)
    
    if result["success"]:
        return OrderCreateResponse(
            success=True,
            message="Order created successfully",
            order_id=result["order"].id
        )
    else:
        return OrderCreateResponse(success=False, message=result["error"])

class OrderItemAddRequest(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: float

class OrderItemAddResponse(BaseModel):
    success: bool
    message: str
    item_id: Optional[int] = None
    order_total: Optional[Dict[str, float]] = None

@router.post("/orders/add-item", response_model=OrderItemAddResponse)
def add_item_to_order(request: OrderItemAddRequest):
    """Add item to order with stock validation and inventory update"""
    result = add_item_to_order_with_validation(
        request.order_id,
        request.product_id,
        request.quantity,
        request.price
    )
    
    if result["success"]:
        return OrderItemAddResponse(
            success=True,
            message="Item added to order successfully",
            item_id=result["item_id"],
            order_total=result["order_total"]
        )
    else:
        return OrderItemAddResponse(success=False, message=result["error"])

class OrderStatusUpdateRequest(BaseModel):
    new_status: str

class OrderStatusUpdateResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[int] = None
    new_status: Optional[str] = None

@router.put("/orders/{order_id}/status", response_model=OrderStatusUpdateResponse)
def update_order_status_endpoint(order_id: int, request: OrderStatusUpdateRequest):
    """Update order status with validation"""
    result = update_order_status(order_id, request.new_status)
    
    if result["success"]:
        return OrderStatusUpdateResponse(
            success=True,
            message="Order status updated successfully",
            order_id=order_id,
            new_status=request.new_status
        )
    else:
        return OrderStatusUpdateResponse(success=False, message=result["error"]) 