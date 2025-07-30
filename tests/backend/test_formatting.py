#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.langchain_sql_service import LangChainSQLService

def test_formatting():
    """Test the cell formatting function"""
    
    sql_service = LangChainSQLService()
    
    # Test cases
    test_cases = [
        # (cell_value, columns, column_index, expected)
        (1299.98, ['category_name', 'category_revenue', 'revenue_percentage'], 1, '$1299.98'),
        (100.0, ['category_name', 'category_revenue', 'revenue_percentage'], 2, '100.00%'),
        (2582.78, ['total_revenue'], 0, '$2582.78'),
        (42, ['count'], 0, '42'),
        (3.14159, ['pi'], 0, '3.1416'),
        (None, ['name'], 0, 'NULL'),
    ]
    
    print("Testing cell formatting:")
    for cell_value, columns, column_index, expected in test_cases:
        result = sql_service._format_cell_value(cell_value, columns, column_index)
        status = "✅" if result == expected else "❌"
        print(f"{status} {cell_value} -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_formatting() 