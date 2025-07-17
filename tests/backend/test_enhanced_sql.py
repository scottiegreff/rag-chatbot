#!/usr/bin/env python3
"""
Test script for enhanced SQL service
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_sql_context_builder():
    """Test the SQL context builder"""
    print("🧪 Testing SQL Context Builder...")
    
    try:
        from backend.utils.sql_context_builder import get_sql_context_builder
        
        builder = get_sql_context_builder()
        
        # Test schema
        schema = builder.get_database_schema()
        print(f"✅ Schema retrieved ({len(schema)} characters)")
        print(f"📋 Schema preview: {schema[:200]}...")
        
        # Test examples
        examples = builder.get_example_queries()
        print(f"✅ Examples retrieved ({len(examples)} characters)")
        print(f"📋 Examples preview: {examples[:200]}...")
        
        # Test context building
        context = builder.build_sql_context("List the top 5 customers by total spending.")
        print(f"✅ Context built ({len(context)} characters)")
        print(f"📋 Context preview: {context[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Context Builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_database_query():
    """Test direct database query"""
    print("\n🧪 Testing Direct Database Query...")
    
    try:
        from backend.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Test a simple query
            result = conn.execute(text("SELECT COUNT(*) as count FROM customers"))
            count = result.fetchone()[0]
            print(f"✅ Customer count: {count}")
            
            # Test top 5 customers query
            result = conn.execute(text("""
                SELECT c.first_name, c.last_name, SUM(o.total) as total_spent
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id, c.first_name, c.last_name
                ORDER BY total_spent DESC NULLS LAST
                LIMIT 5
            """))
            
            customers = result.fetchall()
            print(f"✅ Top 5 customers query successful")
            print("📋 Results:")
            for i, customer in enumerate(customers, 1):
                total_spent = customer[2] or 0
                print(f"  {i}. {customer[0]} {customer[1]} - ${total_spent:,.2f}")
            
            return True
            
    except Exception as e:
        print(f"❌ Direct database query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sql_service():
    """Test the SQL service"""
    print("\n🧪 Testing SQL Service...")
    
    try:
        from backend.services.langchain_sql_service import LangChainSQLService
        
        service = LangChainSQLService()
        
        # Test the query
        result = service.process_query("List the top 5 customers by total spending.")
        
        print(f"✅ SQL Service result: {result}")
        
        if result and result.get('success'):
            print(f"📋 Response: {result.get('response', 'No response')}")
        else:
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ SQL Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_rag_integration():
    """Test RAG integration"""
    print("\n🧪 Testing RAG Integration...")
    
    try:
        from backend.services.rag_service import RAGService
        
        rag = RAGService()
        result = rag.process_database_query("List the top 5 customers by total spending.")
        
        print(f"✅ RAG Integration result: {result}")
        
        if result and result.get('has_database_results'):
            db_result = result.get('database_results', {})
            if db_result.get('success'):
                print(f"📋 Database Response: {db_result.get('response', 'No response')}")
            else:
                print(f"❌ Database query failed: {db_result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ RAG Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced SQL Service Tests\n")
    
    # Test 1: SQL Context Builder
    context_builder_ok = test_sql_context_builder()
    
    # Test 2: Direct Database Query
    direct_query_ok = test_direct_database_query()
    
    # Test 3: SQL Service
    sql_service_result = test_sql_service()
    
    # Test 4: RAG Integration
    rag_result = test_rag_integration()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"✅ SQL Context Builder: {'PASS' if context_builder_ok else 'FAIL'}")
    print(f"✅ Direct Database Query: {'PASS' if direct_query_ok else 'FAIL'}")
    print(f"✅ SQL Service: {'PASS' if sql_service_result and sql_service_result.get('success') else 'FAIL'}")
    print(f"✅ RAG Integration: {'PASS' if rag_result and rag_result.get('has_database_results') else 'FAIL'}")
    
    if sql_service_result and sql_service_result.get('success'):
        print(f"\n🎉 SUCCESS! The enhanced SQL service is working!")
        print(f"📝 Response: {sql_service_result.get('response', 'No response')}")
    else:
        print(f"\n⚠️  The SQL service needs more work.")
        if sql_service_result:
            print(f"❌ Error: {sql_service_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 