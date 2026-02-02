"""Debug Supabase auth flow"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing auth client creation...")
print("=" * 60)

try:
    from supabase import create_client
    
    url = os.getenv("SUPABASE_PROJECT_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"URL: {url}")
    print(f"ANON_KEY: {anon_key[:50]}...")
    print()
    
    # Create client with anon key
    print("Creating auth client...")
    auth_client = create_client(url, anon_key)
    print("✓ Auth client created")
    
    # Try to sign up
    print("\nAttempting to sign up test user...")
    print("Email: testuser123@example.com")
    print("Password: TestPass123!")
    
    response = auth_client.auth.sign_up({
        "email": "testuser123@example.com",
        "password": "TestPass123!"
    })
    
    print(f"✓ Sign up response: {response}")
    if response.user:
        print(f"✓ User ID: {response.user.id}")
        print(f"✓ User Email: {response.user.email}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
