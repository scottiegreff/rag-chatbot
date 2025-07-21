#!/usr/bin/env python3
"""
Test script for the new metadata upload UI.
Tests the API endpoints and verifies the modal functionality.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_api_endpoints():
    """Test the API endpoints for categories and locations"""
    print("🧪 Testing API endpoints...")
    
    # Test categories endpoint
    try:
        response = requests.get(f"{API_BASE}/categories")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categories endpoint: {len(data['categories'])} categories found")
            print(f"   Categories: {', '.join(data['categories'])}")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories endpoint error: {e}")
    
    # Test locations endpoint
    try:
        response = requests.get(f"{API_BASE}/locations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Locations endpoint: {len(data['locations'])} locations found")
            print(f"   Locations: {', '.join(data['locations'])}")
        else:
            print(f"❌ Locations endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Locations endpoint error: {e}")
    
    # Test documents endpoint
    try:
        response = requests.get(f"{API_BASE}/documents")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documents endpoint: {data['total_count']} documents found")
        else:
            print(f"❌ Documents endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Documents endpoint error: {e}")

def test_metadata_query():
    """Test the metadata query endpoint"""
    print("\n🔍 Testing metadata query endpoint...")
    
    query_data = {
        "query": "employee handbook",
        "category": "HR",
        "n_results": 3
    }
    
    try:
        response = requests.post(f"{API_BASE}/query/metadata", json=query_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metadata query successful: {data['total_results']} results found")
            for i, result in enumerate(data['results']):
                metadata = result['metadata']
                print(f"   {i+1}. {metadata.get('title', 'Untitled')} ({metadata.get('category', 'Unknown')})")
        else:
            print(f"❌ Metadata query failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Metadata query error: {e}")

def test_ui_elements():
    """Test that the UI elements are present in the HTML"""
    print("\n🎨 Testing UI elements...")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            html = response.text
            
            # Check for modal elements
            checks = [
                ("upload-modal", "Upload modal"),
                ("metadata-upload-form", "Metadata form"),
                ("modal-file-input", "File input"),
                ("modal-title", "Title input"),
                ("modal-category", "Category select"),
                ("modal-location", "Location select"),
                ("modal-tags", "Tags input"),
                ("modal-questions", "Questions textarea"),
                ("modal-description", "Description textarea"),
                ("modal-upload-btn", "Upload button"),
                ("modal-cancel-btn", "Cancel button")
            ]
            
            for element_id, description in checks:
                if element_id in html:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
        else:
            print(f"❌ Failed to load HTML: {response.status_code}")
    except Exception as e:
        print(f"❌ UI test error: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing Metadata Upload UI")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(1)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test metadata query
    test_metadata_query()
    
    # Test UI elements
    test_ui_elements()
    
    print("\n🎉 All tests completed!")
    print("\n📝 Next steps:")
    print("1. Open http://localhost:8000 in your browser")
    print("2. Click the upload button (📤 icon)")
    print("3. Fill out the metadata form")
    print("4. Upload a document and verify it works!")

if __name__ == "__main__":
    main() 