#!/usr/bin/env python3
"""
PostgreSQL Database Setup Utility

This script helps set up the PostgreSQL database for the FCI Chatbot.
It will create the database if it doesn't exist and initialize the tables.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from sqlalchemy import text

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, engine
from backend.models.chat import ChatSession, ChatMessage

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    load_dotenv()
    
    # Get database configuration
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "fci_chatbot")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    # Connect to PostgreSQL server (not to a specific database)
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nPlease make sure:")
        print("1. PostgreSQL is installed and running")
        print("2. Your .env file has the correct database credentials")
        print("3. The PostgreSQL user has permission to create databases")
        return False
    
    return True

def test_connection():
    """Test the database connection"""
    try:
        # Test the connection using SQLAlchemy
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"Successfully connected to PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False

def main():
    """Main setup function"""
    print("PostgreSQL Database Setup for FCI Chatbot")
    print("=" * 50)
    
    # Step 1: Create database if it doesn't exist
    if not create_database_if_not_exists():
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection():
        print("Failed to connect to the database.")
        sys.exit(1)
    
    # Step 3: Initialize tables
    print("Initializing database tables...")
    try:
        init_db()
        print("Database tables initialized successfully!")
    except Exception as e:
        print(f"Error initializing tables: {e}")
        sys.exit(1)
    
    print("\nPostgreSQL database setup completed successfully!")
    print("You can now start the chatbot server.")

if __name__ == "__main__":
    main() 