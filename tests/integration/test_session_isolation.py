#!/usr/bin/env python3
"""
Test script to verify session isolation is working properly.
This script will:
1. Create a new session and ask a question
2. Create another new session and ask a related question
3. Verify that the second session doesn't have context from the first
"""

import requests
import json
import time

BASE_URL = "http://localhost:8010"

def test_session_isolation():
    print("🧪 Testing session isolation...")
    
    # Step 1: Create first session and ask a question
    print("\n📝 Step 1: Creating first session...")
    response = requests.post(f"{BASE_URL}/api/session/new")
    if response.status_code != 200:
        print(f"❌ Failed to create first session: {response.status_code}")
        return
    session1 = response.json()
    session1_id = session1['session_id']
    print(f"✅ Created session 1: {session1_id}")
    
    # Ask a question in first session
    print("\n💬 Asking question in session 1...")
    question1 = "My name is Alice. What is your name?"
    response = requests.post(f"{BASE_URL}/api/chat/stream", 
                           json={"message": question1, "session_id": session1_id})
    if response.status_code != 200:
        print(f"❌ Failed to send message to session 1: {response.status_code}")
        return
    
    # Read the streaming response
    content1 = ""
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'delta' in data:
                        content1 += data['delta']
                    if data.get('done'):
                        break
                except json.JSONDecodeError:
                    continue
    
    print(f"✅ Session 1 response: {content1[:200]}...")
    
    # Step 2: Create second session and ask a related question
    print("\n📝 Step 2: Creating second session...")
    response = requests.post(f"{BASE_URL}/api/session/new")
    if response.status_code != 200:
        print(f"❌ Failed to create second session: {response.status_code}")
        return
    session2 = response.json()
    session2_id = session2['session_id']
    print(f"✅ Created session 2: {session2_id}")
    
    # Ask a question that should NOT have context from session 1
    print("\n💬 Asking question in session 2...")
    question2 = "What is my name?"
    response = requests.post(f"{BASE_URL}/api/chat/stream", 
                           json={"message": question2, "session_id": session2_id})
    if response.status_code != 200:
        print(f"❌ Failed to send message to session 2: {response.status_code}")
        return
    
    # Read the streaming response
    content2 = ""
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'delta' in data:
                        content2 += data['delta']
                    if data.get('done'):
                        break
                except json.JSONDecodeError:
                    continue
    
    print(f"✅ Session 2 response: {content2[:200]}...")
    
    # Step 3: Verify isolation
    print("\n🔍 Step 3: Verifying session isolation...")
    
    # Check if session 2 mentions Alice
    alice_mentioned = "alice" in content2.lower()
    
    if alice_mentioned:
        print("❌ FAILED: Session 2 has context from session 1!")
        print(f"   Alice mentioned: {alice_mentioned}")
        print(f"   Full response: {content2}")
        return False
    else:
        print("✅ PASSED: Session 2 is properly isolated from session 1!")
        print(f"   Alice mentioned: {alice_mentioned}")
        return True

if __name__ == "__main__":
    try:
        success = test_session_isolation()
        if success:
            print("\n🎉 Session isolation test PASSED!")
        else:
            print("\n💥 Session isolation test FAILED!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 