"""Test login endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("LOGIN TEST")
print("=" * 70)

# Test data - use the registered email from earlier
email = "testuser_cc7736de@example.com"  # Change this to a registered email
password = "TestPass123!"

payload = {
    "email": email,
    "password": password
}

print(f"\nTesting login for: {email}")
print(f"Password: {password}")

try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=payload,
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Login successful!")
        print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
        print(f"Refresh Token: {data.get('refresh_token', 'N/A')[:30]}...")
        print(f"User ID: {data.get('user', {}).get('id', 'N/A')}")
        print(f"User Email: {data.get('user', {}).get('email', 'N/A')}")
    else:
        print(f"\n✗ Login failed")
        try:
            error_data = response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Response: {response.text}")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
