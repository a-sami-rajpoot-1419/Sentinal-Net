"""Test full registration and login flow"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("FULL REGISTRATION AND LOGIN TEST")
print("=" * 70)

# Step 1: Register a new user
email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
password = "TestPass123!"
full_name = "Test User"

print(f"\n1. REGISTERING NEW USER")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Full Name: {full_name}")

reg_payload = {
    "email": email,
    "password": password,
    "full_name": full_name
}

try:
    reg_response = requests.post(
        f"{BASE_URL}/auth/register",
        json=reg_payload,
        timeout=30
    )
    
    print(f"\n   Response Status: {reg_response.status_code}")
    
    if reg_response.status_code == 201:
        reg_data = reg_response.json()
        print(f"   ✓ Registration successful!")
        print(f"   Access Token: {reg_data.get('access_token', 'N/A')[:50]}...")
        print(f"   User ID: {reg_data.get('user', {}).get('id', 'N/A')}")
    else:
        print(f"   ✗ Registration failed")
        try:
            error_data = reg_response.json()
            print(f"   Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   Response: {reg_response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Login with the same credentials
print(f"\n2. LOGGING IN WITH REGISTERED USER")
print(f"   Email: {email}")
print(f"   Password: {password}")

login_payload = {
    "email": email,
    "password": password
}

try:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_payload,
        timeout=30
    )
    
    print(f"\n   Response Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"   ✓ Login successful!")
        print(f"   Access Token: {login_data.get('access_token', 'N/A')[:50]}...")
        print(f"   Refresh Token: {login_data.get('refresh_token', 'N/A')[:30]}...")
        print(f"   User ID: {login_data.get('user', {}).get('id', 'N/A')}")
        print(f"   User Email: {login_data.get('user', {}).get('email', 'N/A')}")
        print(f"\n✓ ALL TESTS PASSED!")
    else:
        print(f"   ✗ Login failed")
        try:
            error_data = login_response.json()
            print(f"   Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   Response: {login_response.text}")
        exit(1)
            
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
