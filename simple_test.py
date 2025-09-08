#!/usr/bin/env python3
"""
Simple test to check API functionality
"""

import requests
import json

def test_single_api():
    """Test a single API call to see the actual error"""
    try:
        print("Testing API call...")
        response = requests.post("http://localhost:8000/api/chat", 
                               json={
                                   "message": "tell me a cat fact",
                                   "tenant_id": "test",
                                   "agent_type": "api_exec"
                               }, 
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success: {data.get('response', 'No response')}")
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server is not running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
        return True
    except:
        print("❌ Server is not running")
        return False

if __name__ == "__main__":
    print("🔍 Checking server status...")
    if check_server_status():
        print("\n🧪 Testing API call...")
        test_single_api()
    else:
        print("Please start the server first with: python app.py")
