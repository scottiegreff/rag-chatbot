#!/usr/bin/env python3
"""
Test script to verify the upload endpoint is receiving form data correctly.
This script tests the /api/upload endpoint with metadata fields.
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload"

def create_test_file():
    """Create a test file for uploading."""
    test_content = """
This is a test document for the FCIAS Chatbot.

Key Information:
- Document Type: Test Policy
- Category: HR
- Location: All Locations
- Tags: test, policy, hr

This document contains important information about testing procedures.
    """
    
    test_file_path = "test_upload_document.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    return test_file_path

def test_upload_with_metadata():
    """Test the upload endpoint with complete metadata."""
    print("🧪 Testing Upload Endpoint with Metadata")
    print("=" * 50)
    
    # Create test file
    test_file_path = create_test_file()
    
    try:
        # Prepare form data - exactly like the frontend does
        with open(test_file_path, "rb") as f:
            files = {
                'file': ('test_upload_document.txt', f, 'text/plain')
            }
            
            # Handle general questions like the frontend does
            questions_text = """What is this document about?
How do I use this policy?
Who should I contact for questions?"""
            
            questions_array = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            data = {
                'title': 'Test HR Policy Document',
                'category': 'HR',
                'location': 'All Locations',
                'tags': json.dumps(['test', 'policy', 'hr', 'procedures']),  # JSON array string
                'description': 'A test document for verifying upload functionality',
                'uploaded_by': 'test@company.com',
                'general_questions': json.dumps(questions_array)  # JSON string like frontend
            }
            
            print("📤 Sending upload request with data:")
            print(f"  File: {test_file_path}")
            print(f"  Title: {data['title']}")
            print(f"  Category: {data['category']}")
            print(f"  Location: {data['location']}")
            print(f"  Tags: {data['tags']}")
            print(f"  Description: {data['description']}")
            print(f"  Uploaded By: {data['uploaded_by']}")
            print(f"  Questions JSON: {data['general_questions']}")
            print()
            
            # Send request
            print("🔄 Sending request to:", UPLOAD_ENDPOINT)
            response = requests.post(UPLOAD_ENDPOINT, files=files, data=data)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload Successful!")
                print("📋 Response Data:")
                print(json.dumps(result, indent=2))
                
                # Verify metadata was received correctly
                if 'metadata' in result:
                    metadata = result['metadata']
                    print("\n🔍 Metadata Verification:")
                    print(f"  ✅ Title: {metadata.get('title')}")
                    print(f"  ✅ Category: {metadata.get('category')}")
                    print(f"  ✅ Location: {metadata.get('location')}")
                    print(f"  ✅ Tags: {metadata.get('tags')}")
                    print(f"  ✅ Description: {metadata.get('description')}")
                    print(f"  ✅ Uploaded By: {metadata.get('uploaded_by')}")
                    print(f"  ✅ General Questions: {metadata.get('general_questions')}")
                else:
                    print("⚠️  No metadata in response")
                    
            else:
                print("❌ Upload Failed!")
                print(f"Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"🧹 Cleaned up test file: {test_file_path}")

def test_upload_validation():
    """Test upload validation by sending incomplete data."""
    print("\n🧪 Testing Upload Validation")
    print("=" * 50)
    
    test_file_path = create_test_file()
    
    try:
        with open(test_file_path, "rb") as f:
            files = {
                'file': ('test_upload_document.txt', f, 'text/plain')
            }
            
            # Test with missing required fields
            data = {
                'title': '',  # Missing title
                'category': '',  # Missing category
                'location': 'All Locations',
                'general_questions': '[]',  # Empty questions array
            }
            
            print("📤 Testing with missing required fields:")
            print(f"  Title: '{data['title']}' (empty)")
            print(f"  Category: '{data['category']}' (empty)")
            print(f"  Location: {data['location']}")
            print(f"  Questions: {data['general_questions']}")
            print()
            
            response = requests.post(UPLOAD_ENDPOINT, files=files, data=data)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 422:  # Validation error
                print("✅ Validation working correctly!")
                try:
                    error_data = response.json()
                    print("📋 Validation Errors:")
                    print(json.dumps(error_data, indent=2))
                except:
                    print("📋 Error Response:", response.text)
            else:
                print("⚠️  Unexpected response for validation test")
                print("Response:", response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_categories_endpoint():
    """Test the categories endpoint."""
    print("\n🧪 Testing Categories Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Categories Retrieved Successfully!")
            print("📋 Categories:", data.get('categories', []))
        else:
            print("❌ Failed to get categories")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_locations_endpoint():
    """Test the locations endpoint."""
    print("\n🧪 Testing Locations Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/locations")
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Locations Retrieved Successfully!")
            print("📋 Locations:", data.get('locations', []))
        else:
            print("❌ Failed to get locations")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Upload Endpoint Tests")
    print("=" * 60)
    
    # Test basic endpoints first
    test_categories_endpoint()
    test_locations_endpoint()
    
    # Test upload functionality
    test_upload_with_metadata()
    test_upload_validation()
    
    print("\n🎉 Test Suite Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main() 