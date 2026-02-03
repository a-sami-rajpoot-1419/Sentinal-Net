"""Test the new HTTP-based Supabase client"""
import sys
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Set path
sys.path.insert(0, r'c:\Sami\Sentinal-net')

print("=" * 70)
print("TESTING HTTP-BASED SUPABASE CLIENT")
print("=" * 70)

try:
    from backend.db.supabase_client import get_supabase_client
    import uuid
    
    client = get_supabase_client()
    print("\n✓ Supabase HTTP client initialized")
    
    # Test 1: Check if user exists
    test_email = f"httptest_{uuid.uuid4().hex[:8]}@example.com"
    print(f"\n1. Testing user_exists for: {test_email}")
    exists = client.user_exists(test_email)
    print(f"   ✓ user_exists returned: {exists}")
    
    # Test 2: Create user in database
    print(f"\n2. Creating user profile...")
    auth_id = str(uuid.uuid4())
    user_data = client.create_user(
        auth_id=auth_id,
        email=test_email,
        full_name="Test User",
        role="user"
    )
    print(f"   ✓ User created: {user_data}")
    
    # Test 3: Retrieve user by email
    print(f"\n3. Retrieving user by email...")
    retrieved_user = client.get_user_by_email(test_email)
    print(f"   ✓ User retrieved: {retrieved_user}")
    
    # Test 4: Retrieve user by auth_id
    print(f"\n4. Retrieving user by auth_id...")
    retrieved_by_id = client.get_user_by_id(auth_id)
    print(f"   ✓ User retrieved: {retrieved_by_id}")
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
