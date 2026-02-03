"""Test Supabase auth token endpoint directly"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_PROJECT_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")

print("=" * 70)
print("TESTING SUPABASE AUTH TOKEN ENDPOINT")
print("=" * 70)

# Use the email that was just registered
email = "testuser_fce4f22c@example.com"
password = "TestPass123!"

auth_url = f"{url}/auth/v1/token?grant_type=password"
headers = {
    "Content-Type": "application/json",
    "apikey": anon_key
}

payload = {
    "email": email,
    "password": password
}

print(f"\nAuth URL: {auth_url}")
print(f"Email: {email}")
print(f"Password: {password}")

try:
    response = requests.post(auth_url, json=payload, headers=headers, timeout=10)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:\n{response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Auth successful!")
        print(f"User ID: {data.get('user', {}).get('id')}")
    else:
        print(f"\n✗ Auth failed")
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2)}")
        except:
            pass
            
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
