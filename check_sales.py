from sqlalchemy import create_engine, text
import os

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

with engine.connect() as conn:
    # Check total sales from orders table
    result = conn.execute(text('SELECT SUM(total) as total_sales FROM orders'))
    total_sales = result.fetchone()[0]
    print(f'Total sales from orders table: ${total_sales:.2f}')
    
    # Check individual orders
    result = conn.execute(text('SELECT id, customer_id, total FROM orders ORDER BY id'))
    print('\nIndividual orders:')
    for row in result:
        print(f'Order {row[0]}: Customer {row[1]}, Total: ${row[2]:.2f}')
    
    # Check what the customer analysis query is actually returning
    result = conn.execute(text('''
        SELECT 
            c.id, c.first_name, c.last_name,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(o.total), 0) as total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.first_name, c.last_name
        ORDER BY total_spent DESC
        LIMIT 5
    '''))
    
    print('\nTop 5 customers by spending:')
    for row in result:
        print(f'{row[1]} {row[2]}: ${row[4]:.2f} ({row[3]} orders)')
    
    # Sum up customer spending
    result = conn.execute(text('''
        SELECT COALESCE(SUM(o.total), 0) as total_customer_spending
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
    '''))
    total_customer_spending = result.fetchone()[0]
    print(f'\nTotal customer spending: ${total_customer_spending:.2f}')
    
    # Check if there's any duplication in the test query
    result = conn.execute(text('''
        SELECT 
            c.id, c.first_name, c.last_name,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(o.total), 0) as total_spent,
            COUNT(o.id) as raw_order_count
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.first_name, c.last_name
        ORDER BY total_spent DESC
        LIMIT 3
    '''))
    
    print('\nDetailed analysis (including raw order count):')
    for row in result:
        print(f'{row[1]} {row[2]}: ${row[4]:.2f} (distinct orders: {row[3]}, raw count: {row[5]})') 