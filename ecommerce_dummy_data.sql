-- E-commerce Dummy Data Insertion Script
-- Run this after creating the tables

-- Insert Categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Home & Garden', 'Home improvement and garden supplies'),
('Books', 'Books and educational materials'),
('Sports & Outdoors', 'Sports equipment and outdoor gear'),
('Beauty & Health', 'Beauty products and health supplements'),
('Toys & Games', 'Toys, games, and entertainment'),
('Automotive', 'Car parts and accessories');

-- Insert Suppliers
INSERT INTO suppliers (name, contact_email, phone) VALUES
('TechCorp Industries', 'contact@techcorp.com', '555-0101'),
('Fashion Forward Ltd', 'info@fashionforward.com', '555-0102'),
('Home Essentials Co', 'sales@homeessentials.com', '555-0103'),
('BookWorld Publishers', 'orders@bookworld.com', '555-0104'),
('SportsMax Supply', 'support@sportsmax.com', '555-0105'),
('BeautyPlus Inc', 'hello@beautyplus.com', '555-0106'),
('ToyLand Manufacturing', 'sales@toyland.com', '555-0107'),
('AutoParts Pro', 'parts@autopartspro.com', '555-0108');

-- Insert Products
INSERT INTO products (name, description, price, category_id, supplier_id, sku) VALUES
-- Electronics
('iPhone 15 Pro', 'Latest iPhone with advanced camera system', 999.99, 1, 1, 'IPH15PRO-001'),
('MacBook Air M2', 'Lightweight laptop with M2 chip', 1199.99, 1, 1, 'MBA-M2-001'),
('Samsung 4K TV', '55-inch 4K Smart TV', 799.99, 1, 1, 'SAMS-4K-55'),
('Wireless Headphones', 'Noise-cancelling Bluetooth headphones', 299.99, 1, 1, 'WH-NC-001'),
('Gaming Laptop', 'High-performance gaming laptop', 1499.99, 1, 1, 'GL-HP-001'),

-- Clothing
('Denim Jacket', 'Classic blue denim jacket', 89.99, 2, 2, 'DJ-BLUE-001'),
('Summer Dress', 'Floral print summer dress', 59.99, 2, 2, 'SD-FLORAL-001'),
('Running Shoes', 'Comfortable running shoes', 129.99, 2, 2, 'RS-COMF-001'),
('Winter Coat', 'Warm winter coat with hood', 199.99, 2, 2, 'WC-WARM-001'),
('T-Shirt Pack', 'Pack of 5 cotton t-shirts', 29.99, 2, 2, 'TSP-5PK-001'),

-- Home & Garden
('Coffee Maker', 'Programmable coffee maker', 79.99, 3, 3, 'CM-PROG-001'),
('Garden Hose', '50ft heavy-duty garden hose', 39.99, 3, 3, 'GH-50FT-001'),
('Kitchen Knife Set', 'Professional knife set', 149.99, 3, 3, 'KKS-PRO-001'),
('Plant Pot Set', 'Set of 3 ceramic plant pots', 24.99, 3, 3, 'PPS-3PK-001'),
('LED Light Bulbs', 'Pack of 10 energy-efficient bulbs', 19.99, 3, 3, 'LLB-10PK-001'),

-- Books
('The Great Gatsby', 'Classic American novel', 12.99, 4, 4, 'BOOK-GATSBY-001'),
('Python Programming', 'Learn Python programming', 39.99, 4, 4, 'BOOK-PYTHON-001'),
('Cooking Basics', 'Essential cooking techniques', 24.99, 4, 4, 'BOOK-COOK-001'),
('Fitness Guide', 'Complete fitness and nutrition guide', 19.99, 4, 4, 'BOOK-FIT-001'),
('Business Strategy', 'Modern business strategy guide', 29.99, 4, 4, 'BOOK-BUS-001'),

-- Sports & Outdoors
('Basketball', 'Official size basketball', 29.99, 5, 5, 'BB-OFF-001'),
('Tennis Racket', 'Professional tennis racket', 89.99, 5, 5, 'TR-PRO-001'),
('Yoga Mat', 'Non-slip yoga mat', 34.99, 5, 5, 'YM-NONSLIP-001'),
('Camping Tent', '4-person camping tent', 199.99, 5, 5, 'CT-4P-001'),
('Fishing Rod', 'Professional fishing rod', 79.99, 5, 5, 'FR-PRO-001'),

-- Beauty & Health
('Face Cream', 'Anti-aging face cream', 49.99, 6, 6, 'FC-ANTIAGE-001'),
('Vitamin Pack', 'Daily vitamin supplement', 29.99, 6, 6, 'VP-DAILY-001'),
('Hair Dryer', 'Professional hair dryer', 89.99, 6, 6, 'HD-PRO-001'),
('Shampoo Set', 'Natural shampoo and conditioner', 24.99, 6, 6, 'SS-NAT-001'),
('Electric Toothbrush', 'Sonic electric toothbrush', 69.99, 6, 6, 'ET-SONIC-001'),

-- Toys & Games
('Board Game', 'Family board game', 39.99, 7, 7, 'BG-FAM-001'),
('LEGO Set', 'Creative building set', 79.99, 7, 7, 'LS-CREATE-001'),
('Puzzle 1000pc', '1000-piece jigsaw puzzle', 19.99, 7, 7, 'PZ-1000-001'),
('Remote Control Car', 'Fast RC car', 59.99, 7, 7, 'RCC-FAST-001'),
('Art Set', 'Complete art supplies set', 44.99, 7, 7, 'AS-COMPLETE-001'),

-- Automotive
('Car Floor Mats', 'All-weather floor mats', 49.99, 8, 8, 'CFM-AW-001'),
('Phone Mount', 'Universal phone mount', 19.99, 8, 8, 'PM-UNIV-001'),
('Car Wash Kit', 'Complete car washing kit', 34.99, 8, 8, 'CWK-COMPLETE-001'),
('Oil Filter', 'High-quality oil filter', 14.99, 8, 8, 'OF-HQ-001'),
('LED Light Bar', 'Off-road LED light bar', 299.99, 8, 8, 'LLB-OFFROAD-001');

-- Insert Customers
INSERT INTO customers (first_name, last_name, email, phone) VALUES
('John', 'Smith', 'john.smith@email.com', '555-1001'),
('Sarah', 'Johnson', 'sarah.johnson@email.com', '555-1002'),
('Michael', 'Brown', 'michael.brown@email.com', '555-1003'),
('Emily', 'Davis', 'emily.davis@email.com', '555-1004'),
('David', 'Wilson', 'david.wilson@email.com', '555-1005'),
('Lisa', 'Anderson', 'lisa.anderson@email.com', '555-1006'),
('Robert', 'Taylor', 'robert.taylor@email.com', '555-1007'),
('Jennifer', 'Martinez', 'jennifer.martinez@email.com', '555-1008'),
('Christopher', 'Garcia', 'chris.garcia@email.com', '555-1009'),
('Amanda', 'Rodriguez', 'amanda.rodriguez@email.com', '555-1010'),
('James', 'Miller', 'james.miller@email.com', '555-1011'),
('Jessica', 'Moore', 'jessica.moore@email.com', '555-1012'),
('Daniel', 'Jackson', 'daniel.jackson@email.com', '555-1013'),
('Ashley', 'Martin', 'ashley.martin@email.com', '555-1014'),
('Matthew', 'Lee', 'matthew.lee@email.com', '555-1015');

-- Insert Addresses
INSERT INTO addresses (customer_id, address_type, street, city, state, zip, country) VALUES
-- John Smith addresses
(1, 'shipping', '123 Main St', 'New York', 'NY', '10001', 'USA'),
(1, 'billing', '123 Main St', 'New York', 'NY', '10001', 'USA'),

-- Sarah Johnson addresses
(2, 'shipping', '456 Oak Ave', 'Los Angeles', 'CA', '90210', 'USA'),
(2, 'billing', '456 Oak Ave', 'Los Angeles', 'CA', '90210', 'USA'),

-- Michael Brown addresses
(3, 'shipping', '789 Pine Rd', 'Chicago', 'IL', '60601', 'USA'),
(3, 'billing', '789 Pine Rd', 'Chicago', 'IL', '60601', 'USA'),

-- Emily Davis addresses
(4, 'shipping', '321 Elm St', 'Houston', 'TX', '77001', 'USA'),
(4, 'billing', '321 Elm St', 'Houston', 'TX', '77001', 'USA'),

-- David Wilson addresses
(5, 'shipping', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 'USA'),
(5, 'billing', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 'USA'),

-- Lisa Anderson addresses
(6, 'shipping', '987 Cedar Ln', 'Philadelphia', 'PA', '19101', 'USA'),
(6, 'billing', '987 Cedar Ln', 'Philadelphia', 'PA', '19101', 'USA'),

-- Robert Taylor addresses
(7, 'shipping', '147 Birch Way', 'San Antonio', 'TX', '78201', 'USA'),
(7, 'billing', '147 Birch Way', 'San Antonio', 'TX', '78201', 'USA'),

-- Jennifer Martinez addresses
(8, 'shipping', '258 Spruce Ct', 'San Diego', 'CA', '92101', 'USA'),
(8, 'billing', '258 Spruce Ct', 'San Diego', 'CA', '92101', 'USA'),

-- Christopher Garcia addresses
(9, 'shipping', '369 Willow Pl', 'Dallas', 'TX', '75201', 'USA'),
(9, 'billing', '369 Willow Pl', 'Dallas', 'TX', '75201', 'USA'),

-- Amanda Rodriguez addresses
(10, 'shipping', '741 Aspen Blvd', 'San Jose', 'CA', '95101', 'USA'),
(10, 'billing', '741 Aspen Blvd', 'San Jose', 'CA', '95101', 'USA');

-- Insert Inventory
INSERT INTO inventory (product_id, quantity) VALUES
(1, 50), (2, 30), (3, 25), (4, 100), (5, 20),
(6, 75), (7, 60), (8, 45), (9, 35), (10, 200),
(11, 40), (12, 80), (13, 25), (14, 150), (15, 300),
(16, 100), (17, 50), (18, 75), (19, 60), (20, 40),
(21, 30), (22, 25), (23, 50), (24, 20), (25, 35),
(26, 80), (27, 45), (28, 100), (29, 30), (30, 25),
(31, 60), (32, 40), (33, 75), (34, 50), (35, 30),
(36, 25), (37, 40), (38, 60), (39, 100), (40, 20);

-- Insert Product Images
INSERT INTO product_images (product_id, image_url) VALUES
(1, 'https://example.com/images/iphone15pro.jpg'),
(2, 'https://example.com/images/macbook-air-m2.jpg'),
(3, 'https://example.com/images/samsung-4k-tv.jpg'),
(4, 'https://example.com/images/wireless-headphones.jpg'),
(5, 'https://example.com/images/gaming-laptop.jpg'),
(6, 'https://example.com/images/denim-jacket.jpg'),
(7, 'https://example.com/images/summer-dress.jpg'),
(8, 'https://example.com/images/running-shoes.jpg'),
(9, 'https://example.com/images/winter-coat.jpg'),
(10, 'https://example.com/images/tshirt-pack.jpg');

-- Insert Carts
INSERT INTO cart (customer_id) VALUES
(1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- Insert Cart Items
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES
(1, 1, 1), (1, 4, 2),
(2, 6, 1), (2, 8, 1),
(3, 11, 1), (3, 15, 3),
(4, 16, 2), (4, 17, 1),
(5, 21, 1), (5, 25, 1),
(6, 26, 1), (6, 28, 2),
(7, 31, 1), (7, 33, 1),
(8, 36, 1), (8, 38, 1),
(9, 1, 1), (9, 2, 1),
(10, 6, 2), (10, 7, 1);

-- Insert Wishlists
INSERT INTO wishlists (customer_id) VALUES
(1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- Insert Wishlist Items
INSERT INTO wishlist_items (wishlist_id, product_id) VALUES
(1, 2), (1, 5), (1, 8),
(2, 1), (2, 3), (2, 6),
(3, 11), (3, 13), (3, 15),
(4, 16), (4, 18), (4, 20),
(5, 21), (5, 23), (5, 25),
(6, 26), (6, 28), (6, 30),
(7, 31), (7, 33), (7, 35),
(8, 36), (8, 38), (8, 40),
(9, 1), (9, 4), (9, 7),
(10, 11), (10, 14), (10, 17);

-- Insert Discounts
INSERT INTO discounts (code, description, discount_percent, valid_from, valid_to, active) VALUES
('SAVE10', '10% off your first order', 10.00, '2024-01-01', '2024-12-31', true),
('SUMMER20', '20% off summer items', 20.00, '2024-06-01', '2024-08-31', true),
('WELCOME15', '15% off for new customers', 15.00, '2024-01-01', '2024-12-31', true),
('FLASH25', '25% off flash sale', 25.00, '2024-07-01', '2024-07-07', true),
('LOYALTY5', '5% off for loyal customers', 5.00, '2024-01-01', '2024-12-31', true);

-- Insert Orders
INSERT INTO orders (customer_id, order_date, status, shipping_address_id, billing_address_id, total) VALUES
(1, '2024-01-15 10:30:00', 'completed', 1, 2, 1299.98),
(2, '2024-01-16 14:20:00', 'completed', 3, 4, 189.98),
(3, '2024-01-17 09:15:00', 'shipped', 5, 6, 119.98),
(4, '2024-01-18 16:45:00', 'processing', 7, 8, 74.98),
(5, '2024-01-19 11:30:00', 'pending', 9, 10, 199.98),
(6, '2024-01-20 13:20:00', 'completed', 11, 12, 39.99),
(7, '2024-01-21 15:10:00', 'shipped', 13, 14, 89.99),
(8, '2024-01-22 08:45:00', 'processing', 15, 16, 159.98),
(9, '2024-01-23 12:30:00', 'pending', 17, 18, 299.99),
(10, '2024-01-24 17:20:00', 'completed', 19, 20, 44.99);

-- Insert Order Items
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 999.99), (1, 4, 1, 299.99),
(2, 6, 1, 89.99), (2, 8, 1, 129.99),
(3, 11, 1, 79.99), (3, 15, 1, 39.99),
(4, 16, 1, 12.99), (4, 17, 1, 39.99), (4, 18, 1, 24.99),
(5, 21, 1, 29.99), (5, 25, 1, 79.99), (5, 26, 1, 89.99),
(6, 31, 1, 39.99),
(7, 36, 1, 49.99), (7, 37, 1, 29.99), (7, 38, 1, 89.99),
(8, 1, 1, 999.99), (8, 4, 1, 299.99),
(9, 6, 1, 89.99), (9, 8, 1, 129.99), (9, 10, 1, 29.99),
(10, 33, 1, 44.99);

-- Insert Payments
INSERT INTO payments (order_id, payment_date, amount, payment_method, status) VALUES
(1, '2024-01-15 10:35:00', 1299.98, 'credit_card', 'completed'),
(2, '2024-01-16 14:25:00', 189.98, 'paypal', 'completed'),
(3, '2024-01-17 09:20:00', 119.98, 'credit_card', 'completed'),
(4, '2024-01-18 16:50:00', 74.98, 'credit_card', 'processing'),
(5, '2024-01-19 11:35:00', 199.98, 'paypal', 'pending'),
(6, '2024-01-20 13:25:00', 39.99, 'credit_card', 'completed'),
(7, '2024-01-21 15:15:00', 89.99, 'credit_card', 'completed'),
(8, '2024-01-22 08:50:00', 159.98, 'paypal', 'processing'),
(9, '2024-01-23 12:35:00', 299.99, 'credit_card', 'pending'),
(10, '2024-01-24 17:25:00', 44.99, 'credit_card', 'completed');

-- Insert Shipping
INSERT INTO shipping (order_id, shipped_date, delivery_date, carrier, tracking_number, status) VALUES
(1, '2024-01-16 09:00:00', '2024-01-18 14:30:00', 'FedEx', 'FX123456789', 'delivered'),
(2, '2024-01-17 10:00:00', '2024-01-19 16:45:00', 'UPS', 'UP987654321', 'delivered'),
(3, '2024-01-18 08:30:00', NULL, 'USPS', 'US456789123', 'in_transit'),
(4, NULL, NULL, 'FedEx', NULL, 'pending'),
(5, NULL, NULL, 'UPS', NULL, 'pending'),
(6, '2024-01-21 11:00:00', '2024-01-23 13:20:00', 'USPS', 'US789123456', 'delivered'),
(7, '2024-01-22 14:00:00', NULL, 'FedEx', 'FX321654987', 'in_transit'),
(8, NULL, NULL, 'UPS', NULL, 'pending'),
(9, NULL, NULL, 'FedEx', NULL, 'pending'),
(10, '2024-01-25 09:00:00', '2024-01-27 15:30:00', 'USPS', 'US147258369', 'delivered');

-- Insert Reviews
INSERT INTO reviews (product_id, customer_id, rating, comment, created_at) VALUES
(1, 1, 5, 'Amazing phone! The camera quality is outstanding.', '2024-01-20 10:00:00'),
(2, 2, 4, 'Great laptop, very fast and lightweight.', '2024-01-21 14:30:00'),
(6, 3, 5, 'Perfect fit and great quality denim.', '2024-01-22 09:15:00'),
(8, 4, 4, 'Comfortable shoes for running.', '2024-01-23 16:45:00'),
(11, 5, 5, 'Makes great coffee every morning.', '2024-01-24 11:30:00'),
(16, 6, 4, 'Classic book, great read.', '2024-01-25 13:20:00'),
(21, 7, 5, 'Excellent basketball, perfect for outdoor courts.', '2024-01-26 15:10:00'),
(26, 8, 4, 'Good face cream, noticed improvement in skin.', '2024-01-27 08:45:00'),
(31, 9, 5, 'Fun board game for the whole family.', '2024-01-28 12:30:00'),
(36, 10, 4, 'Great floor mats, fit perfectly.', '2024-01-29 17:20:00');

-- Update product supplier_id references
UPDATE products SET supplier_id = 1 WHERE category_id = 1;
UPDATE products SET supplier_id = 2 WHERE category_id = 2;
UPDATE products SET supplier_id = 3 WHERE category_id = 3;
UPDATE products SET supplier_id = 4 WHERE category_id = 4;
UPDATE products SET supplier_id = 5 WHERE category_id = 5;
UPDATE products SET supplier_id = 6 WHERE category_id = 6;
UPDATE products SET supplier_id = 7 WHERE category_id = 7;
UPDATE products SET supplier_id = 8 WHERE category_id = 8; 