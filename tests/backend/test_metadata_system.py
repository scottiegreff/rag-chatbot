#!/usr/bin/env python3
"""
Test script for the enhanced metadata system.
Tests document upload with metadata and metadata-based queries.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8010"
API_BASE = f"{BASE_URL}/api"

def test_metadata_upload():
    """Test uploading a document with enhanced metadata"""
    print("🧪 Testing metadata-enhanced document upload...")
    
    # Create a test document
    test_content = """
    Employee Handbook 2024
    
    This handbook contains all the policies and procedures for employees.
    
    Time Off Requests:
    - Submit requests through the HR portal
    - Minimum 2 weeks notice for vacation
    - Sick leave requires doctor's note after 3 days
    
    Dress Code:
    - Business casual Monday-Thursday
    - Casual Friday
    - No flip-flops or tank tops
    
    Working Hours:
    - 9:00 AM to 5:00 PM Monday-Friday
    - Flexible hours available with manager approval
    - Remote work options available
    
    Emergency Procedures:
    - In case of fire, use nearest exit
    - Assembly point is the parking lot
    - Call 911 for medical emergencies
    """
    
    # Create test file
    test_file_path = Path("test_handbook.txt")
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    # Prepare metadata
    metadata = {
        "title": "Employee Handbook 2024",
        "category": "HR",
        "location": "All Locations",
        "general_questions": json.dumps([
            "How do I request time off?",
            "What's the dress code?",
            "What are the working hours?",
            "How do I report an incident?",
            "Where is the emergency exit?"
        ]),
        "tags": json.dumps(["policies", "employee", "handbook", "hr"]),
        "description": "Comprehensive employee handbook covering company policies and procedures",
        "uploaded_by": "test@company.com"
    }
    
    try:
        # Upload file with metadata
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_handbook.txt", f, "text/plain")}
            data = metadata
            
            response = requests.post(f"{API_BASE}/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful! Document ID: {result.get('doc_id')}")
                print(f"📄 Metadata: {json.dumps(result.get('metadata'), indent=2)}")
                return result.get('doc_id')
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()

def test_metadata_query():
    """Test querying documents with metadata filters"""
    print("\n🔍 Testing metadata-enhanced queries...")
    
    # Test 1: Query by location
    print("\n📍 Testing location-based query...")
    location_query = {
        "query": "What are the emergency procedures?",
        "location": "All Locations",
        "n_results": 3
    }
    
    response = requests.post(f"{API_BASE}/query/metadata", json=location_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Location query successful! Found {result['total_results']} results")
        for i, doc in enumerate(result['results']):
            print(f"  {i+1}. {doc['metadata'].get('title', 'Untitled')} - {doc['metadata'].get('location', 'Unknown')}")
    else:
        print(f"❌ Location query failed: {response.status_code} - {response.text}")
    
    # Test 2: Query by category
    print("\n📂 Testing category-based query...")
    category_query = {
        "query": "dress code policy",
        "category": "HR",
        "n_results": 3
    }
    
    response = requests.post(f"{API_BASE}/query/metadata", json=category_query)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Category query successful! Found {result['total_results']} results")
        for i, doc in enumerate(result['results']):
            print(f"  {i+1}. {doc['metadata'].get('title', 'Untitled')} - {doc['metadata'].get('category', 'Unknown')}")
    else:
        print(f"❌ Category query failed: {response.status_code} - {response.text}")

def test_document_listing():
    """Test listing documents and metadata"""
    print("\n📋 Testing document listing...")
    
    # List all documents
    response = requests.get(f"{API_BASE}/documents")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total_count']} documents")
        for doc in result['documents']:
            print(f"  📄 {doc['title']} ({doc['category']} - {doc['location']})")
            print(f"     Questions: {', '.join(doc['general_questions'][:3])}...")
    else:
        print(f"❌ Document listing failed: {response.status_code} - {response.text}")
    
    # List categories
    print("\n📂 Testing category listing...")
    response = requests.get(f"{API_BASE}/categories")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total_count']} categories: {', '.join(result['categories'])}")
    else:
        print(f"❌ Category listing failed: {response.status_code} - {response.text}")
    
    # List locations
    print("\n📍 Testing location listing...")
    response = requests.get(f"{API_BASE}/locations")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total_count']} locations: {', '.join(result['locations'])}")
    else:
        print(f"❌ Location listing failed: {response.status_code} - {response.text}")

def main():
    """Run all metadata system tests"""
    print("🚀 Testing Enhanced Metadata System")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test upload with metadata
    doc_id = test_metadata_upload()
    
    if doc_id:
        # Wait a moment for processing
        time.sleep(1)
        
        # Test metadata queries
        test_metadata_query()
        
        # Test document listing
        test_document_listing()
        
        print("\n🎉 All metadata system tests completed!")
    else:
        print("\n❌ Upload failed, skipping query tests")

if __name__ == "__main__":
    main() 