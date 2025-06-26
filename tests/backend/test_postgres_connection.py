#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection and basic functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import engine, SessionLocal
from backend.models.chat import ChatSession, ChatMessage
from sqlalchemy import text

def test_database_connection():
    """Test basic database connection"""
    print("Testing PostgreSQL connection...")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Successfully connected to PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False

def test_table_creation():
    """Test table creation and basic operations"""
    print("\nTesting table operations...")
    
    try:
        # Create tables
        from backend.database import init_db
        init_db()
        print("✅ Tables created successfully")
        
        # Test basic CRUD operations
        db = SessionLocal()
        
        # Create a test session
        test_session = ChatSession(
            session_id="test-session-123",
            title="Test Session"
        )
        db.add(test_session)
        db.commit()
        db.refresh(test_session)
        print(f"✅ Created test session: {test_session.session_id}")
        
        # Create a test message
        test_message = ChatMessage(
            session_id=test_session.id,
            role="user",
            content="Hello, this is a test message"
        )
        db.add(test_message)
        db.commit()
        print("✅ Created test message")
        
        # Query the session
        session = db.query(ChatSession).filter_by(session_id="test-session-123").first()
        if session:
            print(f"✅ Retrieved session: {session.title}")
            messages = db.query(ChatMessage).filter_by(session_id=session.id).all()
            print(f"✅ Retrieved {len(messages)} messages")
        
        # Clean up
        db.query(ChatMessage).filter_by(session_id=test_session.id).delete()
        db.query(ChatSession).filter_by(session_id="test-session-123").delete()
        db.commit()
        print("✅ Cleaned up test data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to test table operations: {e}")
        return False

def main():
    """Main test function"""
    print("PostgreSQL Database Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Test connection
    if not test_database_connection():
        print("\n❌ Database connection failed. Please check your .env configuration.")
        sys.exit(1)
    
    # Test table operations
    if not test_table_creation():
        print("\n❌ Table operations failed.")
        sys.exit(1)
    
    print("\n✅ All PostgreSQL tests passed!")
    print("Your PostgreSQL database is working correctly.")

if __name__ == "__main__":
    main() 