"""
Reset Database with Clean, Consistent Dummy Data
This script clears all e-commerce data and inserts clean data where orders.total matches order_items calculations.
"""

from sqlalchemy import create_engine, text
import os
from datetime import datetime, timedelta

# Database connection
db_params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5433'),
    'database': os.getenv('DB_NAME', 'ai_chatbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password1234')
}

connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
engine = create_engine(connection_string)

def clear_database():
    """Clear all e-commerce data from the database"""
    print("🗑️  Clearing database...")
    
    with engine.connect() as conn:
        # Disable foreign key checks temporarily
        conn.execute(text("SET session_replication_role = replica;"))
        
        # Clear all tables in correct order (respecting foreign keys)
        tables_to_clear = [
            'wishlist_items', 'wishlists', 'cart_items', 'cart',
            'reviews', 'payments', 'shipping', 'order_items', 'orders',
            'inventory', 'product_images', 'products', 'suppliers',
            'categories', 'addresses', 'customers', 'discounts'
        ]
        
        for table in tables_to_clear:
            try:
                conn.execute(text(f"DELETE FROM {table};"))
                print(f"   ✅ Cleared {table}")
            except Exception as e:
                print(f"   ⚠️  Could not clear {table}: {e}")
        
        # Reset sequences
        sequences = [
            'customers_id_seq', 'addresses_id_seq', 'categories_id_seq',
            'suppliers_id_seq', 'products_id_seq', 'product_images_id_seq',
            'inventory_id_seq', 'orders_id_seq', 'order_items_id_seq',
            'payments_id_seq', 'shipping_id_seq', 'cart_id_seq',
            'cart_items_id_seq', 'discounts_id_seq', 'reviews_id_seq',
            'wishlists_id_seq', 'wishlist_items_id_seq'
        ]
        
        for seq in sequences:
            try:
                conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))
                print(f"   ✅ Reset sequence {seq}")
            except Exception as e:
                print(f"   ⚠️  Could not reset {seq}: {e}")
        
        # Re-enable foreign key checks
        conn.execute(text("SET session_replication_role = DEFAULT;"))
        conn.commit()

def insert_clean_data():
    """Insert clean, consistent dummy data"""
    print("\n📦 Inserting clean data...")
    
    with engine.connect() as conn:
        # Insert Categories
        print("   📂 Inserting categories...")
        categories = [
            ('Electronics', 'Electronic devices and accessories'),
            ('Clothing', 'Apparel and fashion items'),
            ('Home & Garden', 'Home improvement and garden supplies'),
            ('Books', 'Books and educational materials'),
            ('Sports & Outdoors', 'Sports equipment and outdoor gear'),
            ('Beauty & Health', 'Beauty products and health supplements'),
            ('Toys & Games', 'Toys, games, and entertainment'),
            ('Automotive', 'Car parts and accessories')
        ]
        
        for name, description in categories:
            conn.execute(text("INSERT INTO categories (name, description) VALUES (:name, :description)"), 
                        {"name": name, "description": description})
        
        # Insert Suppliers
        print("   🏭 Inserting suppliers...")
        suppliers = [
            ('TechCorp Industries', 'contact@techcorp.com', '555-0101'),
            ('Fashion Forward Ltd', 'info@fashionforward.com', '555-0102'),
            ('Home Essentials Co', 'sales@homeessentials.com', '555-0103'),
            ('BookWorld Publishers', 'orders@bookworld.com', '555-0104'),
            ('SportsMax Supply', 'support@sportsmax.com', '555-0105'),
            ('BeautyPlus Inc', 'hello@beautyplus.com', '555-0106'),
            ('ToyLand Manufacturing', 'sales@toyland.com', '555-0107'),
            ('AutoParts Pro', 'parts@autopartspro.com', '555-0108')
        ]
        
        for name, email, phone in suppliers:
            conn.execute(text("INSERT INTO suppliers (name, contact_email, phone) VALUES (:name, :email, :phone)"),
                        {"name": name, "email": email, "phone": phone})
        
        # Insert Products (with consistent pricing)
        print("   📦 Inserting products...")
        products = [
            # Electronics (category_id = 1, supplier_id = 1)
            ('iPhone 15 Pro', 'Latest iPhone with advanced camera system', 999.99, 1, 1, 'IPH15PRO-001'),
            ('MacBook Air M2', 'Lightweight laptop with M2 chip', 1199.99, 1, 1, 'MBA-M2-001'),
            ('Samsung 4K TV', '55-inch 4K Smart TV', 799.99, 1, 1, 'SAMS-4K-55'),
            ('Wireless Headphones', 'Noise-cancelling Bluetooth headphones', 299.99, 1, 1, 'WH-NC-001'),
            ('Gaming Laptop', 'High-performance gaming laptop', 1499.99, 1, 1, 'GL-HP-001'),
            
            # Clothing (category_id = 2, supplier_id = 2)
            ('Denim Jacket', 'Classic blue denim jacket', 89.99, 2, 2, 'DJ-BLUE-001'),
            ('Summer Dress', 'Floral print summer dress', 59.99, 2, 2, 'SD-FLORAL-001'),
            ('Running Shoes', 'Comfortable running shoes', 129.99, 2, 2, 'RS-COMF-001'),
            ('Winter Coat', 'Warm winter coat with hood', 199.99, 2, 2, 'WC-WARM-001'),
            ('T-Shirt Pack', 'Pack of 5 cotton t-shirts', 29.99, 2, 2, 'TSP-5PK-001'),
            
            # Home & Garden (category_id = 3, supplier_id = 3)
            ('Coffee Maker', 'Programmable coffee maker', 79.99, 3, 3, 'CM-PROG-001'),
            ('Garden Hose', '50ft heavy-duty garden hose', 39.99, 3, 3, 'GH-50FT-001'),
            ('Kitchen Knife Set', 'Professional knife set', 149.99, 3, 3, 'KKS-PRO-001'),
            ('Plant Pot Set', 'Set of 3 ceramic plant pots', 24.99, 3, 3, 'PPS-3PK-001'),
            ('LED Light Bulbs', 'Pack of 10 energy-efficient bulbs', 19.99, 3, 3, 'LLB-10PK-001'),
            
            # Books (category_id = 4, supplier_id = 4)
            ('The Great Gatsby', 'Classic American novel', 12.99, 4, 4, 'BOOK-GATSBY-001'),
            ('Python Programming', 'Learn Python programming', 39.99, 4, 4, 'BOOK-PYTHON-001'),
            ('Cooking Basics', 'Essential cooking techniques', 24.99, 4, 4, 'BOOK-COOK-001'),
            ('Fitness Guide', 'Complete fitness and nutrition guide', 19.99, 4, 4, 'BOOK-FIT-001'),
            ('Business Strategy', 'Modern business strategy guide', 29.99, 4, 4, 'BOOK-BUS-001'),
            
            # Sports & Outdoors (category_id = 5, supplier_id = 5)
            ('Basketball', 'Official size basketball', 29.99, 5, 5, 'BB-OFF-001'),
            ('Tennis Racket', 'Professional tennis racket', 89.99, 5, 5, 'TR-PRO-001'),
            ('Yoga Mat', 'Non-slip yoga mat', 34.99, 5, 5, 'YM-NONSLIP-001'),
            ('Camping Tent', '4-person camping tent', 199.99, 5, 5, 'CT-4P-001'),
            ('Fishing Rod', 'Professional fishing rod', 79.99, 5, 5, 'FR-PRO-001'),
            
            # Beauty & Health (category_id = 6, supplier_id = 6)
            ('Face Cream', 'Anti-aging face cream', 49.99, 6, 6, 'FC-ANTIAGE-001'),
            ('Vitamin Pack', 'Daily vitamin supplement', 29.99, 6, 6, 'VP-DAILY-001'),
            ('Hair Dryer', 'Professional hair dryer', 89.99, 6, 6, 'HD-PRO-001'),
            ('Shampoo Set', 'Natural shampoo and conditioner', 24.99, 6, 6, 'SS-NAT-001'),
            ('Electric Toothbrush', 'Sonic electric toothbrush', 69.99, 6, 6, 'ET-SONIC-001'),
            
            # Toys & Games (category_id = 7, supplier_id = 7)
            ('Board Game', 'Family board game', 39.99, 7, 7, 'BG-FAM-001'),
            ('LEGO Set', 'Creative building set', 79.99, 7, 7, 'LS-CREATE-001'),
            ('Puzzle 1000pc', '1000-piece jigsaw puzzle', 19.99, 7, 7, 'PZ-1000-001'),
            ('Remote Control Car', 'Fast RC car', 59.99, 7, 7, 'RCC-FAST-001'),
            ('Art Set', 'Complete art supplies set', 44.99, 7, 7, 'AS-COMPLETE-001'),
            
            # Automotive (category_id = 8, supplier_id = 8)
            ('Car Floor Mats', 'All-weather floor mats', 49.99, 8, 8, 'CFM-AW-001'),
            ('Phone Mount', 'Universal phone mount', 19.99, 8, 8, 'PM-UNIV-001'),
            ('Car Wash Kit', 'Complete car washing kit', 34.99, 8, 8, 'CWK-COMPLETE-001'),
            ('Oil Filter', 'High-quality oil filter', 14.99, 8, 8, 'OF-HQ-001'),
            ('LED Light Bar', 'Off-road LED light bar', 299.99, 8, 8, 'LLB-OFFROAD-001')
        ]
        
        for name, description, price, category_id, supplier_id, sku in products:
            conn.execute(text("""
                INSERT INTO products (name, description, price, category_id, supplier_id, sku) 
                VALUES (:name, :description, :price, :category_id, :supplier_id, :sku)
            """), {"name": name, "description": description, "price": price, 
                   "category_id": category_id, "supplier_id": supplier_id, "sku": sku})
        
        # Insert Customers
        print("   👥 Inserting customers...")
        customers = [
            ('John', 'Smith', 'john.smith@email.com', '555-1001'),
            ('Sarah', 'Johnson', 'sarah.johnson@email.com', '555-1002'),
            ('Michael', 'Brown', 'michael.brown@email.com', '555-1003'),
            ('Emily', 'Davis', 'emily.davis@email.com', '555-1004'),
            ('David', 'Wilson', 'david.wilson@email.com', '555-1005'),
            ('Lisa', 'Anderson', 'lisa.anderson@email.com', '555-1006'),
            ('Robert', 'Taylor', 'robert.taylor@email.com', '555-1007'),
            ('Jennifer', 'Martinez', 'jennifer.martinez@email.com', '555-1008'),
            ('Christopher', 'Garcia', 'chris.garcia@email.com', '555-1009'),
            ('Amanda', 'Rodriguez', 'amanda.rodriguez@email.com', '555-1010')
        ]
        
        for first_name, last_name, email, phone in customers:
            conn.execute(text("""
                INSERT INTO customers (first_name, last_name, email, phone) 
                VALUES (:first_name, :last_name, :email, :phone)
            """), {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone})
        
        # Insert Addresses
        print("   🏠 Inserting addresses...")
        addresses = [
            (1, 'shipping', '123 Main St', 'New York', 'NY', '10001', 'USA'),
            (1, 'billing', '123 Main St', 'New York', 'NY', '10001', 'USA'),
            (2, 'shipping', '456 Oak Ave', 'Los Angeles', 'CA', '90210', 'USA'),
            (2, 'billing', '456 Oak Ave', 'Los Angeles', 'CA', '90210', 'USA'),
            (3, 'shipping', '789 Pine Rd', 'Chicago', 'IL', '60601', 'USA'),
            (3, 'billing', '789 Pine Rd', 'Chicago', 'IL', '60601', 'USA'),
            (4, 'shipping', '321 Elm St', 'Houston', 'TX', '77001', 'USA'),
            (4, 'billing', '321 Elm St', 'Houston', 'TX', '77001', 'USA'),
            (5, 'shipping', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 'USA'),
            (5, 'billing', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 'USA'),
            (6, 'shipping', '987 Cedar Ln', 'Philadelphia', 'PA', '19101', 'USA'),
            (6, 'billing', '987 Cedar Ln', 'Philadelphia', 'PA', '19101', 'USA'),
            (7, 'shipping', '147 Birch Way', 'San Antonio', 'TX', '78201', 'USA'),
            (7, 'billing', '147 Birch Way', 'San Antonio', 'TX', '78201', 'USA'),
            (8, 'shipping', '258 Spruce Ct', 'San Diego', 'CA', '92101', 'USA'),
            (8, 'billing', '258 Spruce Ct', 'San Diego', 'CA', '92101', 'USA'),
            (9, 'shipping', '369 Willow Pl', 'Dallas', 'TX', '75201', 'USA'),
            (9, 'billing', '369 Willow Pl', 'Dallas', 'TX', '75201', 'USA'),
            (10, 'shipping', '741 Aspen Blvd', 'San Jose', 'CA', '95101', 'USA'),
            (10, 'billing', '741 Aspen Blvd', 'San Jose', 'CA', '95101', 'USA')
        ]
        
        for customer_id, address_type, street, city, state, zip_code, country in addresses:
            conn.execute(text("""
                INSERT INTO addresses (customer_id, address_type, street, city, state, zip, country) 
                VALUES (:customer_id, :address_type, :street, :city, :state, :zip_code, :country)
            """), {"customer_id": customer_id, "address_type": address_type, "street": street,
                   "city": city, "state": state, "zip_code": zip_code, "country": country})
        
        # Insert Inventory
        print("   📦 Inserting inventory...")
        for product_id in range(1, 41):  # 40 products
            quantity = 50 + (product_id * 5) % 100  # Varying quantities
            conn.execute(text("INSERT INTO inventory (product_id, quantity) VALUES (:product_id, :quantity)"),
                        {"product_id": product_id, "quantity": quantity})
        
        # Insert clean orders with consistent totals
        print("   📋 Inserting orders...")
        orders_data = [
            (1, '2024-01-15 10:30:00', 'completed', 1, 2, 1299.98),  # iPhone + Headphones
            (2, '2024-01-16 14:20:00', 'completed', 3, 4, 219.98),   # Denim Jacket + Running Shoes
            (3, '2024-01-17 09:15:00', 'shipped', 5, 6, 119.98),     # Coffee Maker + LED Bulbs
            (4, '2024-01-18 16:45:00', 'processing', 7, 8, 77.97),   # 3 books
            (5, '2024-01-19 11:30:00', 'pending', 9, 10, 199.97),    # Basketball + Tennis Racket + Yoga Mat
            (6, '2024-01-20 13:20:00', 'completed', 11, 12, 39.99),  # Face Cream
            (7, '2024-01-21 15:10:00', 'shipped', 13, 14, 169.97),   # Hair Dryer + Vitamin Pack + Shampoo
            (8, '2024-01-22 08:45:00', 'processing', 15, 16, 159.98), # Car Floor Mats + Phone Mount + Car Wash Kit
            (9, '2024-01-23 12:30:00', 'pending', 17, 18, 249.97),   # Board Game + LEGO + Puzzle
            (10, '2024-01-24 17:20:00', 'completed', 19, 20, 44.99)  # Art Set
        ]
        
        for customer_id, order_date, status, shipping_addr, billing_addr, total in orders_data:
            conn.execute(text("""
                INSERT INTO orders (customer_id, order_date, status, shipping_address_id, billing_address_id, total) 
                VALUES (:customer_id, :order_date, :status, :shipping_addr, :billing_addr, :total)
            """), {"customer_id": customer_id, "order_date": order_date, "status": status,
                   "shipping_addr": shipping_addr, "billing_addr": billing_addr, "total": total})
        
        # Insert order items that match the order totals exactly
        print("   📦 Inserting order items...")
        order_items_data = [
            # Order 1: iPhone + Headphones = 1299.98
            (1, 1, 1, 999.99), (1, 4, 1, 299.99),
            
            # Order 2: Denim Jacket + Running Shoes = 219.98
            (2, 6, 1, 89.99), (2, 8, 1, 129.99),
            
            # Order 3: Coffee Maker + LED Bulbs = 119.98
            (3, 11, 1, 79.99), (3, 15, 1, 39.99),
            
            # Order 4: 3 books = 77.97
            (4, 16, 1, 12.99), (4, 17, 1, 39.99), (4, 18, 1, 24.99),
            
            # Order 5: Basketball + Tennis Racket + Yoga Mat = 199.97
            (5, 21, 1, 29.99), (5, 22, 1, 89.99), (5, 23, 1, 79.99),
            
            # Order 6: Face Cream = 39.99
            (6, 26, 1, 39.99),
            
            # Order 7: Hair Dryer + Vitamin Pack + Shampoo = 169.97
            (7, 28, 1, 89.99), (7, 27, 1, 29.99), (7, 29, 1, 49.99),
            
            # Order 8: Car Floor Mats + Phone Mount + Car Wash Kit = 159.98
            (8, 36, 1, 49.99), (8, 37, 1, 19.99), (8, 38, 1, 89.99),
            
            # Order 9: Board Game + LEGO + Puzzle = 249.97
            (9, 31, 1, 39.99), (9, 32, 1, 79.99), (9, 33, 1, 129.99),
            
            # Order 10: Art Set = 44.99
            (10, 35, 1, 44.99)
        ]
        
        for order_id, product_id, quantity, price in order_items_data:
            conn.execute(text("""
                INSERT INTO order_items (order_id, product_id, quantity, price) 
                VALUES (:order_id, :product_id, :quantity, :price)
            """), {"order_id": order_id, "product_id": product_id, "quantity": quantity, "price": price})
        
        # Insert payments matching order totals
        print("   💳 Inserting payments...")
        for order_id, total in [(i+1, total) for i, (_, _, _, _, _, total) in enumerate(orders_data)]:
            conn.execute(text("""
                INSERT INTO payments (order_id, payment_date, amount, payment_method, status) 
                VALUES (:order_id, :payment_date, :amount, :payment_method, :status)
            """), {"order_id": order_id, "payment_date": datetime.now(), 
                   "amount": total, "payment_method": "credit_card", "status": "completed"})
        
        # Insert shipping info
        print("   🚚 Inserting shipping...")
        for order_id in range(1, 11):
            conn.execute(text("""
                INSERT INTO shipping (order_id, shipped_date, delivery_date, carrier, tracking_number, status) 
                VALUES (:order_id, :shipped_date, :delivery_date, :carrier, :tracking_number, :status)
            """), {"order_id": order_id, "shipped_date": datetime.now(), 
                   "delivery_date": datetime.now() + timedelta(days=3),
                   "carrier": "FedEx", "tracking_number": f"FX{order_id:09d}", "status": "delivered"})
        
        # Insert reviews
        print("   ⭐ Inserting reviews...")
        reviews_data = [
            (1, 1, 5, 'Amazing phone! The camera quality is outstanding.'),
            (2, 2, 4, 'Great laptop, very fast and lightweight.'),
            (6, 3, 5, 'Perfect fit and great quality denim.'),
            (8, 4, 4, 'Comfortable shoes for running.'),
            (11, 5, 5, 'Makes great coffee every morning.'),
            (16, 6, 4, 'Classic book, great read.'),
            (21, 7, 5, 'Excellent basketball, perfect for outdoor courts.'),
            (26, 8, 4, 'Good face cream, noticed improvement in skin.'),
            (31, 9, 5, 'Fun board game for the whole family.'),
            (36, 10, 4, 'Great floor mats, fit perfectly.')
        ]
        
        for product_id, customer_id, rating, comment in reviews_data:
            conn.execute(text("""
                INSERT INTO reviews (product_id, customer_id, rating, comment, created_at) 
                VALUES (:product_id, :customer_id, :rating, :comment, :created_at)
            """), {"product_id": product_id, "customer_id": customer_id, "rating": rating,
                   "comment": comment, "created_at": datetime.now()})
        
        # Insert carts and cart items
        print("   🛒 Inserting carts...")
        for customer_id in range(1, 11):
            conn.execute(text("INSERT INTO cart (customer_id) VALUES (:customer_id)"), {"customer_id": customer_id})
        
        # Insert some cart items
        cart_items_data = [
            (1, 1, 1), (1, 4, 2),  # Customer 1: iPhone + 2x Headphones
            (2, 6, 1), (2, 8, 1),  # Customer 2: Denim Jacket + Running Shoes
            (3, 11, 1), (3, 15, 3), # Customer 3: Coffee Maker + 3x LED Bulbs
        ]
        
        for cart_id, product_id, quantity in cart_items_data:
            conn.execute(text("""
                INSERT INTO cart_items (cart_id, product_id, quantity) 
                VALUES (:cart_id, :product_id, :quantity)
            """), {"cart_id": cart_id, "product_id": product_id, "quantity": quantity})
        
        # Insert wishlists
        print("   ❤️  Inserting wishlists...")
        for customer_id in range(1, 11):
            conn.execute(text("INSERT INTO wishlists (customer_id) VALUES (:customer_id)"), {"customer_id": customer_id})
        
        # Insert some wishlist items
        wishlist_items_data = [
            (1, 2), (1, 5), (1, 8),   # Customer 1: MacBook, Gaming Laptop, Winter Coat
            (2, 1), (2, 3), (2, 6),   # Customer 2: iPhone, Samsung TV, Denim Jacket
            (3, 11), (3, 13), (3, 15), # Customer 3: Coffee Maker, Knife Set, LED Bulbs
        ]
        
        for wishlist_id, product_id in wishlist_items_data:
            conn.execute(text("""
                INSERT INTO wishlist_items (wishlist_id, product_id) 
                VALUES (:wishlist_id, :product_id)
            """), {"wishlist_id": wishlist_id, "product_id": product_id})
        
        # Insert discounts
        print("   🎫 Inserting discounts...")
        discounts_data = [
            ('SAVE10', '10% off your first order', 10.00, '2024-01-01', '2024-12-31', True),
            ('SUMMER20', '20% off summer items', 20.00, '2024-06-01', '2024-08-31', True),
            ('WELCOME15', '15% off for new customers', 15.00, '2024-01-01', '2024-12-31', True),
            ('FLASH25', '25% off flash sale', 25.00, '2024-07-01', '2024-07-07', True),
            ('LOYALTY5', '5% off for loyal customers', 5.00, '2024-01-01', '2024-12-31', True)
        ]
        
        for code, description, discount_percent, valid_from, valid_to, active in discounts_data:
            conn.execute(text("""
                INSERT INTO discounts (code, description, discount_percent, valid_from, valid_to, active) 
                VALUES (:code, :description, :discount_percent, :valid_from, :valid_to, :active)
            """), {"code": code, "description": description, "discount_percent": discount_percent,
                   "valid_from": valid_from, "valid_to": valid_to, "active": active})
        
        conn.commit()
        print("   ✅ All data inserted successfully!")

def verify_data_consistency():
    """Verify that orders.total matches order_items calculations"""
    print("\n🔍 Verifying data consistency...")
    
    with engine.connect() as conn:
        # Check orders total
        result = conn.execute(text("SELECT SUM(total) as orders_total FROM orders"))
        orders_total = result.fetchone()[0]
        print(f"   Orders total: ${orders_total:.2f}")
        
        # Check order items total
        result = conn.execute(text("SELECT SUM(quantity * price) as items_total FROM order_items"))
        items_total = result.fetchone()[0]
        print(f"   Order items total: ${items_total:.2f}")
        
        # Check payments total
        result = conn.execute(text("SELECT SUM(amount) as payments_total FROM payments"))
        payments_total = result.fetchone()[0]
        print(f"   Payments total: ${payments_total:.2f}")
        
        # Check consistency
        orders_items_diff = abs(orders_total - items_total)
        orders_payments_diff = abs(orders_total - payments_total)
        
        print(f"\n   Orders vs Items difference: ${orders_items_diff:.2f}")
        print(f"   Orders vs Payments difference: ${orders_payments_diff:.2f}")
        
        if orders_items_diff < 0.01 and orders_payments_diff < 0.01:
            print("   ✅ PERFECT: All totals are consistent!")
            return True
        else:
            print("   ❌ INCONSISTENCY: Totals don't match!")
            return False

def main():
    """Main function to reset and populate database"""
    print("🚀 RESETTING DATABASE WITH CLEAN DATA")
    print("=" * 50)
    
    try:
        # Clear existing data
        clear_database()
        
        # Insert clean data
        insert_clean_data()
        
        # Verify consistency
        is_consistent = verify_data_consistency()
        
        if is_consistent:
            print("\n🎉 SUCCESS: Database reset with clean, consistent data!")
            print("   The chatbot should now get consistent totals regardless of which table it queries.")
        else:
            print("\n⚠️  WARNING: Data consistency issues detected!")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 