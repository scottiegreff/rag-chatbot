"""
Test revenue calculation in Docker container
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from backend.database import engine

def test_docker_revenue():
    """Test revenue calculation"""
    try:
        with engine.connect() as conn:
            # Test the exact same query as the fallback
            result = conn.execute(text("SELECT SUM(total) as total FROM orders"))
            total = result.fetchone()[0] or 0
            print(f"Fallback query result: ${total:,.2f}")
            
            # Also test the exact query from our test
            result = conn.execute(text("SELECT SUM(total) FROM orders"))
            total2 = result.fetchone()[0] or 0
            print(f"Test query result: ${total2:,.2f}")
            
            # Check if they match
            print(f"Match: {abs(total - total2) < 0.01}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_docker_revenue() 