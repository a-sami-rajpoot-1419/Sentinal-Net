"""Test Supabase API key validity"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.getenv("SUPABASE_PROJECT_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("=" * 60)
print("SUPABASE API KEY TEST")
print("=" * 60)

print(f"\n✓ SUPABASE_PROJECT_URL: {url}")
print(f"✓ SUPABASE_ANON_KEY: {anon_key[:50]}..." if anon_key else "✗ ANON_KEY missing")
print(f"✓ SUPABASE_SERVICE_ROLE_KEY: {service_key[:30]}..." if service_key else "✗ SERVICE_KEY missing")

# Test creating Supabase client
try:
    from supabase import create_client
    
    print("\n" + "=" * 60)
    print("Testing Supabase Connection...")
    print("=" * 60)
    
    # Test anon client (for auth operations)
    print("\n1. Testing ANON_KEY (for user auth)...")
    try:
        anon_client = create_client(url, anon_key)
        print("   ✓ ANON client created successfully")
        
        # Test a simple query
        response = anon_client.table("users").select("*").limit(1).execute()
        print(f"   ✓ Query successful (accessed users table)")
    except Exception as e:
        print(f"   ✗ ANON client error: {e}")
    
    # Test service role client (for admin operations)
    print("\n2. Testing SERVICE_ROLE_KEY (for admin operations)...")
    try:
        service_client = create_client(url, service_key)
        print("   ✓ Service client created successfully")
        
        # Test a simple query
        response = service_client.table("users").select("*").limit(1).execute()
        print(f"   ✓ Query successful (accessed users table)")
    except Exception as e:
        print(f"   ✗ Service client error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
