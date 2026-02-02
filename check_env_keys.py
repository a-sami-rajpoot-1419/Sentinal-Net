"""Check what the backend is loading for API keys"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.getenv("SUPABASE_PROJECT_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("Keys loaded by Python:")
print("=" * 70)
print(f"SUPABASE_PROJECT_URL:")
print(f"  {url}")
print(f"\nSUPABASE_ANON_KEY:")
print(f"  {anon_key}")
print(f"\nSUPABASE_SERVICE_ROLE_KEY:")
print(f"  {service_key}")
print("=" * 70)

# Verify the exact key you provided
expected_anon = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmaGJnZnB1dXN2bHJldWNqdm1mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NTIwMjMsImV4cCI6MjA4NTIyODAyM30.06_G8T9I1trEXprrd44wvCgikUuhxm1g425QA6Zatrk"

print(f"\nExpected ANON_KEY matches: {anon_key == expected_anon}")
if anon_key != expected_anon:
    print(f"\nExpected: {expected_anon}")
    print(f"Got:      {anon_key}")
    
    # Find the difference
    for i, (e, g) in enumerate(zip(expected_anon, anon_key)):
        if e != g:
            print(f"\nFirst difference at position {i}:")
            print(f"  Expected: {e}")
            print(f"  Got: {g}")
            break
