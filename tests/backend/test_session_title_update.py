#!/usr/bin/env python3
"""
Test script to verify session title update functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_session_title_update():
    print("🧪 Testing session title update...")
    
    # Step 1: Create a new session
    print("\n📝 Step 1: Creating new session...")
    response = requests.post(f"{BASE_URL}/api/session/new")
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        return False
    session = response.json()
    session_id = session['session_id']
    original_title = session['title']
    print(f"✅ Created session: {session_id}")
    print(f"   Original title: {original_title}")
    
    # Step 2: Update the title
    print("\n✏️  Step 2: Updating session title...")
    new_title = "Test Updated Title"
    response = requests.put(f"{BASE_URL}/api/session/{session_id}/title?title={new_title}")
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Title updated successfully to: {new_title}")
        
        # Step 3: Verify the title was updated
        print("\n🔍 Step 3: Verifying title update...")
        response = requests.get(f"{BASE_URL}/api/sessions")
        if response.status_code == 200:
            sessions = response.json()
            updated_session = next((s for s in sessions if s['session_id'] == session_id), None)
            if updated_session and updated_session['title'] == new_title:
                print(f"✅ Title verification successful: {updated_session['title']}")
                return True
            else:
                print(f"❌ Title verification failed. Expected: {new_title}, Got: {updated_session['title'] if updated_session else 'None'}")
                return False
        else:
            print(f"❌ Failed to get sessions: {response.status_code}")
            return False
    else:
        print(f"❌ Failed to update title: {response.status_code}")
        try:
            error_text = response.text
            print(f"   Error response: {error_text}")
        except:
            pass
        return False

if __name__ == "__main__":
    try:
        success = test_session_title_update()
        if success:
            print("\n🎉 Session title update test PASSED!")
        else:
            print("\n💥 Session title update test FAILED!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 