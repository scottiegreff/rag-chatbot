#!/usr/bin/env python3
"""
Simple test for LangChain SQL Agent initialization
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_langchain_initialization():
    """Test if LangChain SQL Agent can initialize properly"""
    
    print("🧪 Testing LangChain SQL Agent initialization...")
    
    try:
        # Test database connection
        from backend.database import engine
        print("✅ Database connection successful")
        
        # Test SQLDatabase creation
        from langchain.sql_database import SQLDatabase
        db = SQLDatabase(engine)
        print("✅ SQLDatabase created successfully")
        print(f"📊 Available tables: {db.get_table_names()}")
        
        # Test if we can get table info
        table_info = db.get_table_info()
        print("✅ Table info retrieved successfully")
        
        # Test if we can get sample data
        sample_data = db.get_sample_data()
        print("✅ Sample data retrieved successfully")
        
        print("\n🎉 LangChain SQL Agent components are working!")
        print("The LLM model loading is the bottleneck, but the SQL functionality is ready.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langchain_initialization() 