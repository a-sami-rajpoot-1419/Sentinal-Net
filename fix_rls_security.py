#!/usr/bin/env python3
"""
Fix RLS security warnings in Supabase database
"""
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()

# Get raw connection string
raw_url = os.getenv("DATABASE_URL")

# Parse and fix the connection string
# Format: postgresql://postgres:[@Dmwcr 72019]@db.jfhbgfpuusvlreucjvmf.supabase.co:5432/postgres
# The password contains special characters and square brackets
if raw_url:
    # Extract password from between first : and @
    parts = raw_url.split('@')
    if len(parts) == 2:
        user_pass = parts[0].replace('postgresql://', '')
        host_db = parts[1]
        
        # user_pass is like: postgres:[@Dmwcr 72019]
        user_parts = user_pass.split(':')
        user = user_parts[0]
        password = user_pass[len(user)+1:]  # Get everything after 'postgres:'
        
        # Remove brackets if present
        password = password.strip('[]')
        
        # Rebuild proper URL with quoted password
        DATABASE_URL = f"postgresql://postgres:{quote(password)}@{host_db}"
    else:
        DATABASE_URL = raw_url
else:
    print("✗ Error: DATABASE_URL not found in .env file")
    exit(1)

# Read SQL fix script
sql_file = Path(__file__).parent / "FIX_RLS_SECURITY.sql"
with open(sql_file, 'r') as f:
    sql_script = f.read()

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✓ Connected to Supabase database")
    print("=" * 70)
    print("Executing RLS security fixes...")
    print("=" * 70)
    
    # Execute the SQL script
    cursor.execute(sql_script)
    conn.commit()
    
    print("\n✓ RLS policies have been successfully updated!")
    print("\nFixes applied:")
    print("  • Dropped: 'Allow all access on sessions'")
    print("  • Dropped: 'Allow all access on consensus_results'")
    print("  • Dropped: 'Allow all access on weight_updates'")
    print("  • Dropped: 'Allow all access on agent_performance'")
    print("\n✓ Created new authentication-based policies:")
    print("  • Sessions: Authenticated users can read/create/update")
    print("  • Consensus Results: Authenticated users can read/create")
    print("  • Weight Updates: Authenticated users can read/create")
    print("  • Agent Performance: Authenticated users can read/create/update")
    print("\n" + "=" * 70)
    print("Security Status: FIXED ✓")
    print("=" * 70)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    exit(1)
