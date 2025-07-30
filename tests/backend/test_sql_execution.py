#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine
from sqlalchemy import text

def test_sql_execution():
    """Test SQL execution and result formatting"""
    sql_query = "SELECT COUNT(*) as total_products FROM products"
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            
            print(f"SQL execution returned {len(rows)} rows with columns: {list(columns)}")
            
            if rows:
                # Format the results
                result_text = f"\n\n**Query Results:**\n"
                result_text += f"| {' | '.join(columns)} |\n"
                result_text += f"| {' | '.join(['---'] * len(columns))} |\n"
                
                for row in rows[:10]:  # Limit to 10 rows
                    result_text += f"| {' | '.join(str(cell) for cell in row)} |\n"
                
                if len(rows) > 10:
                    result_text += f"\n*Showing first 10 of {len(rows)} results*\n"
                
                print("Formatted result:")
                print(result_text)
            else:
                print("No data found for SQL query")
        
    except Exception as e:
        print(f"Error executing SQL: {e}")

if __name__ == "__main__":
    test_sql_execution() 