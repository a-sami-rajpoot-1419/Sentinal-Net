"""Test Supabase auth directly via HTTP"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_PROJECT_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")

print("=" * 70)
print("TESTING SUPABASE AUTH DIRECTLY VIA HTTP")
print("=" * 70)

print(f"\nProject URL: {url}")
print(f"ANON_KEY: {anon_key[:50]}...")

# Supabase auth endpoint
auth_url = f"{url}/auth/v1/signup"

headers = {
    "Content-Type": "application/json",
    "apikey": anon_key
}

payload = {
    "email": "httptest@example.com",
    "password": "TestPass123!"
}

print(f"\nAuth URL: {auth_url}")
print(f"Headers: {headers}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(auth_url, json=payload, headers=headers, timeout=10)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:\n{response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Auth successful!")
        print(f"User ID: {data.get('user', {}).get('id', 'N/A')}")
    else:
        print(f"\n✗ Auth failed")
        try:
            error_data = response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error (raw): {response.text}")
            
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
