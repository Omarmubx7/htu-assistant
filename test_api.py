#!/usr/bin/env python3
"""
Test script to verify API accessibility and functionality
"""

import requests
import json
import sys

def test_api_endpoints():
    """Test the API endpoints to ensure they're accessible."""
    
    # Base URL - change this to your deployed URL
    base_url = "https://omarmubaidin.pythonanywhere.com"
    
    print("🔍 Testing HTU Assistant API endpoints...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"   Data loaded: {data.get('data_loaded', {})}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {str(e)}")
    
    print()
    
    # Test 2: Chat API
    print("2. Testing Chat API...")
    try:
        test_message = {
            "message": "Hello, can you help me find information about CS101?"
        }
        response = requests.post(
            f"{base_url}/api/chat", 
            json=test_message, 
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat API: Response received")
            print(f"   Response length: {len(data.get('response', ''))} characters")
        else:
            print(f"❌ Chat API failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat API error: {str(e)}")
    
    print()
    
    # Test 3: Professor Search
    print("3. Testing Professor Search...")
    try:
        test_message = {
            "message": "Ahmed Bataineh"
        }
        response = requests.post(
            f"{base_url}/api/chat", 
            json=test_message, 
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Professor Search: Response received")
            if 'professor' in data:
                print(f"   Professor found: {data['professor'].get('name', 'Unknown')}")
            else:
                print(f"   No professor data in response")
        else:
            print(f"❌ Professor Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Professor Search error: {str(e)}")
    
    print()
    print("🏁 API testing completed!")

if __name__ == "__main__":
    test_api_endpoints() 