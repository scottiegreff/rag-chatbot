print("=== CHECKING DUMMY DATA CONSISTENCY ===\n")

# Orders from dummy data
orders_data = [
    (1, 1299.98),  # Order 1
    (2, 189.98),   # Order 2  
    (3, 119.98),   # Order 3
    (4, 74.98),    # Order 4
    (5, 199.98),   # Order 5
    (6, 39.99),    # Order 6
    (7, 89.99),    # Order 7
    (8, 159.98),   # Order 8
    (9, 299.99),   # Order 9
    (10, 44.99)    # Order 10
]

# Order items from dummy data
order_items_data = [
    # Order 1: (1, 1, 1, 999.99), (1, 4, 1, 299.99)
    (1, 999.99 + 299.99),  # = 1299.98 ✓
    
    # Order 2: (2, 6, 1, 89.99), (2, 8, 1, 129.99)
    (2, 89.99 + 129.99),   # = 219.98 ✗ (should be 189.98)
    
    # Order 3: (3, 11, 1, 79.99), (3, 15, 1, 39.99)
    (3, 79.99 + 39.99),    # = 119.98 ✓
    
    # Order 4: (4, 16, 1, 12.99), (4, 17, 1, 39.99), (4, 18, 1, 24.99)
    (4, 12.99 + 39.99 + 24.99),  # = 77.97 ✗ (should be 74.98)
    
    # Order 5: (5, 21, 1, 29.99), (5, 25, 1, 79.99), (5, 26, 1, 89.99)
    (5, 29.99 + 79.99 + 89.99),  # = 199.97 ✗ (should be 199.98)
    
    # Order 6: (6, 31, 1, 39.99)
    (6, 39.99),            # = 39.99 ✓
    
    # Order 7: (7, 36, 1, 49.99), (7, 37, 1, 29.99), (7, 38, 1, 89.99)
    (7, 49.99 + 29.99 + 89.99),  # = 169.97 ✗ (should be 89.99)
    
    # Order 8: (8, 1, 1, 999.99), (8, 4, 1, 299.99)
    (8, 999.99 + 299.99),  # = 1299.98 ✗ (should be 159.98)
    
    # Order 9: (9, 6, 1, 89.99), (9, 8, 1, 129.99), (9, 10, 1, 29.99)
    (9, 89.99 + 129.99 + 29.99),  # = 249.97 ✗ (should be 299.99)
    
    # Order 10: (10, 33, 1, 44.99)
    (10, 44.99)            # = 44.99 ✓
]

print("Order-by-order comparison:")
print("Order | Orders.total | Order_Items_Sum | Difference | Status")
print("------|-------------|----------------|------------|--------")

total_orders = 0
total_items = 0

for order_id, order_total in orders_data:
    items_total = next(items_sum for oid, items_sum in order_items_data if oid == order_id)
    difference = order_total - items_total
    status = "✓" if abs(difference) < 0.01 else "✗"
    
    print(f"{order_id:5d} | ${order_total:10.2f} | ${items_total:13.2f} | ${difference:9.2f} | {status}")
    
    total_orders += order_total
    total_items += items_total

print("------|-------------|----------------|------------|--------")
print(f"TOTAL | ${total_orders:10.2f} | ${total_items:13.2f} | ${total_orders - total_items:9.2f} |")

print(f"\n=== ANALYSIS ===")
print(f"Orders total: ${total_orders:.2f}")
print(f"Order items sum: ${total_items:.2f}")
print(f"Difference: ${total_orders - total_items:.2f}")

print(f"\n=== ISSUES FOUND ===")
issues = []
for order_id, order_total in orders_data:
    items_total = next(items_sum for oid, items_sum in order_items_data if oid == order_id)
    if abs(order_total - items_total) > 0.01:
        issues.append((order_id, order_total, items_total, order_total - items_total))

for order_id, order_total, items_total, diff in issues:
    print(f"Order {order_id}: ${order_total:.2f} vs ${items_total:.2f} (diff: ${diff:.2f})")

print(f"\n=== CONCLUSION ===")
print("The dummy data has inconsistencies between orders.total and order_items calculations.")
print("This explains why the chatbot might get different totals depending on which table it queries.")
print("The chatbot should use orders.total as the authoritative source for total sales.") 