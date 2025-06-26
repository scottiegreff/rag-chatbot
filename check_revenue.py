"""
Quick script to check actual revenue values in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from backend.database import engine

def check_revenue():
    """Check the actual revenue values in the database"""
    try:
        with engine.connect() as conn:
            # Get total revenue
            result = conn.execute(text("SELECT SUM(total) FROM orders"))
            total_revenue = result.fetchone()[0] or 0
            print(f"Total Revenue: ${total_revenue:,.2f}")
            
            # Get individual order amounts
            result = conn.execute(text("SELECT id, total FROM orders ORDER BY id"))
            orders = result.fetchall()
            print(f"\nIndividual Orders:")
            for order_id, amount in orders:
                print(f"  Order {order_id}: ${amount:,.2f}")
            
            # Verify the sum
            calculated_sum = sum(amount for _, amount in orders)
            print(f"\nCalculated Sum: ${calculated_sum:,.2f}")
            print(f"Database SUM(): ${total_revenue:,.2f}")
            print(f"Match: {abs(calculated_sum - total_revenue) < 0.01}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_revenue() 