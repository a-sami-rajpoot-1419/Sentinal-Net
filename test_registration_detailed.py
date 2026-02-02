"""Detailed registration test to debug the issue"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("DETAILED REGISTRATION TEST")
print("=" * 70)

# Test 1: Check agents endpoint works
print("\n1. Testing /agents/list endpoint...")
try:
    response = requests.get(f"{BASE_URL}/agents/list", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Agents endpoint is working")
    else:
        print(f"   ✗ Agents endpoint failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Register a new user with detailed error handling
print("\n2. Testing /auth/register endpoint...")
payload = {
    "email": "testuser456@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
}

print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=payload,
        timeout=30
    )
    
    print(f"\n   Response Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    print(f"   Response Body: {response.text}")
    
    try:
        data = response.json()
        print(f"\n   Parsed JSON:")
        print(json.dumps(data, indent=2))
        
        if response.status_code == 201:
            print("\n   ✓ Registration successful!")
            if 'access_token' in data:
                print(f"   ✓ Access token received: {data['access_token'][:50]}...")
        elif response.status_code == 500:
            print("\n   ✗ Server error (500)")
            if 'detail' in data:
                print(f"   Error detail: {data['detail']}")
        elif response.status_code == 409:
            print("\n   ✗ Email already registered")
        else:
            print(f"\n   ✗ Unexpected status code: {response.status_code}")
    except json.JSONDecodeError:
        print("\n   ✗ Response is not valid JSON")
        
except requests.exceptions.Timeout:
    print("   ✗ Request timed out (30s)")
except requests.exceptions.ConnectionError:
    print("   ✗ Connection error - is backend running?")
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
