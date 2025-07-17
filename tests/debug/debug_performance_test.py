#!/usr/bin/env python3
"""
Debug Performance Test - Simplified version to identify issues
"""

import subprocess
import time
import json
import requests
import os
import sys
from datetime import datetime

def log(message: str):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_backend_connection():
    """Test basic backend connectivity"""
    log("🔍 Testing backend connectivity...")
    
    # Test 1: Basic health check
    try:
        response = requests.get("http://localhost:8000/test", timeout=5)
        if response.status_code == 200:
            log("✅ Basic health check passed")
            log(f"📄 Response: {response.text}")
        else:
            log(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Health check exception: {e}")
        return False
    
    # Test 2: Chat endpoint
    try:
        log("🔍 Testing chat endpoint...")
        response = requests.post(
            "http://localhost:8000/api/chat/stream",
            json={"message": "Hello", "session_id": "debug-test"},
            timeout=10,
            stream=True
        )
        
        if response.status_code == 200:
            log("✅ Chat endpoint responding")
            
            # Read a few lines to verify streaming works
            line_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    log(f"📄 Line {line_count}: {line_str[:100]}...")
                    line_count += 1
                    if line_count >= 5:  # Just read first 5 lines
                        break
            log("✅ Streaming response working")
            return True
        else:
            log(f"❌ Chat endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Chat endpoint exception: {e}")
        return False

def test_environment_switch():
    """Test environment switching"""
    log("🔄 Testing environment switch...")
    
    # Check current processes
    log("📊 Current processes on port 8000:")
    try:
        result = subprocess.run("lsof -i:8000", shell=True, capture_output=True, text=True)
        log(f"📄 {result.stdout}")
    except Exception as e:
        log(f"❌ Error checking processes: {e}")
    
    # Try switching to local
    log("🚀 Attempting to switch to local environment...")
    try:
        result = subprocess.run(
            "PORT=8000 ./switch-to-local.sh",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Reduced timeout since script should exit quickly
        )
        
        log(f"📄 Switch command return code: {result.returncode}")
        log(f"📄 Switch command stdout: {result.stdout}")
        log(f"📄 Switch command stderr: {result.stderr}")
        
        if result.returncode == 0:
            log("✅ Environment switch successful")
            return True
        else:
            log("❌ Environment switch failed")
            return False
            
    except subprocess.TimeoutExpired:
        log("❌ Environment switch timed out")
        return False
    except Exception as e:
        log(f"❌ Environment switch exception: {e}")
        return False

def main():
    """Main debug function"""
    log("🔍 Starting debug performance test...")
    
    # Test 1: Environment switch
    if not test_environment_switch():
        log("❌ Environment switch test failed")
        return
    
    # Wait for backend to be ready
    log("⏳ Waiting for backend to be ready...")
    time.sleep(5)
    
    # Test 2: Backend connectivity
    if not test_backend_connection():
        log("❌ Backend connectivity test failed")
        return
    
    log("✅ All debug tests passed!")

if __name__ == "__main__":
    main() 