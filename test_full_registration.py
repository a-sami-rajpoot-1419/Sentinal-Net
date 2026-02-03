"""Complete end-to-end registration test"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("END-TO-END REGISTRATION TEST")
print("=" * 70)

# Step 1: Check backend is running
print("\n1. Checking if backend is running...")
try:
    response = requests.get(f"{BASE_URL}/agents/list", timeout=5)
    if response.status_code == 200:
        print("   ✓ Backend is running")
    else:
        print(f"   ✗ Backend error: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ✗ Backend is not running: {e}")
    exit(1)

# Step 2: Register a new user
print("\n2. Registering a new user...")
email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
password = "TestPass123!"
full_name = "Test User"

payload = {
    "email": email,
    "password": password,
    "full_name": full_name
}

print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Full Name: {full_name}")

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=payload,
        timeout=30
    )
    
    print(f"\n   Response Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"   ✓ Registration successful!")
        print(f"\n   Response:")
        print(f"   - Access Token: {data.get('access_token', 'N/A')[:50]}...")
        print(f"   - Refresh Token: {data.get('refresh_token', 'N/A')[:30]}...")
        print(f"   - Token Type: {data.get('token_type', 'N/A')}")
        print(f"   - User ID: {data.get('user_id', 'N/A')}")
        print(f"   - User Email: {data.get('email', 'N/A')}")
        print(f"\n   ✓ ALL TESTS PASSED!")
    else:
        print(f"   ✗ Registration failed")
        try:
            error_data = response.json()
            print(f"   Error response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   Response body: {response.text}")
        exit(1)
        
except requests.exceptions.Timeout:
    print("   ✗ Request timed out")
    exit(1)
except requests.exceptions.ConnectionError:
    print("   ✗ Connection error - backend is not running")
    exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
