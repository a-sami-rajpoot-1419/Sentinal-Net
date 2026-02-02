"""Diagnostic test for registration"""
import sys
import os

# Set environment variables directly (since we can't use .env in this context)
os.environ["SUPABASE_PROJECT_URL"] = "https://qzzcpwdloxsxmjhslqup.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6emNwd2Rsb3hzeG1qaHNscXVwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODMxNzg3MCwiZXhwIjoxNzUzODY5ODcwfQ.L6gm4RLrPjzJXgBZzPVMHBp-DxdAhqCEGvqKN8v5KCc"
os.environ["SUPABASE_ANON_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6emNwd2Rsb3hzeG1qaHNscXVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgzMTc4NzAsImV4cCI6MTc1Mzg2OTg3MH0.PbMl0vbOAg7SvNhCqF4JKMI0Xvj5Ou7v_bSmyPFXr7Q"

sys.path.insert(0, r'c:\Sami\Sentinal-net')

from backend.db.supabase_client import SupabaseClient

print("Testing Supabase client connection...")

try:
    client = SupabaseClient()
    print("✓ Supabase client initialized")
    
    # Step 1: Check if user exists
    email = "testuser@example.com"
    exists = client.user_exists(email)
    print(f"✓ user_exists returned: {exists}")
    
    # Step 2: Try to auth sign up
    try:
        auth_response = client.auth_client.auth.sign_up({
            "email": email,
            "password": "TestPass123!",
        })
        auth_id = auth_response.user.id
        print(f"✓ Auth user created with ID: {auth_id}")
    except Exception as auth_error:
        print(f"✗ Auth error: {auth_error}")
        exit(1)
    
    # Step 3: Create user profile
    try:
        profile = client.create_user(
            auth_id=auth_id,
            email=email,
            full_name="Test User",
            role="user"
        )
        print(f"✓ User profile created: {profile}")
    except Exception as profile_error:
        print(f"✗ Profile error: {profile_error}")
        exit(1)
        
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
