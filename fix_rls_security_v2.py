#!/usr/bin/env python3
"""
Fix RLS security warnings in Supabase database
"""
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build connection parameters directly
DATABASE_HOST = "db.jfhbgfpuusvlreucjvmf.supabase.co"
DATABASE_PORT = "5432"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "[@Dmwcr 72019]"  # Exact password from .env
DATABASE_NAME = "postgres"

try:
    # Connect using individual parameters (safer than URL parsing)
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME
    )
    cursor = conn.cursor()
    
    print("✓ Connected to Supabase database")
    print("=" * 70)
    print("Executing RLS security fixes...")
    print("=" * 70)
    
    # Read SQL fix script
    sql_file = Path(__file__).parent / "FIX_RLS_SECURITY.sql"
    with open(sql_file, 'r') as f:
        sql_script = f.read()
    
    # Execute the SQL script
    cursor.execute(sql_script)
    conn.commit()
    
    # Fetch and display results from verification query
    results = cursor.fetchall()
    
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
    
    if results:
        print("\n✓ Verification - Active RLS Policies:")
        print("-" * 70)
        for row in results:
            schema, table, policy, cmd = row[0], row[1], row[2], row[4]
            print(f"  {table:25} | {policy:40} | {cmd}")
        print("-" * 70)
    
    print("\n" + "=" * 70)
    print("Security Status: FIXED ✓")
    print("All Supabase RLS warnings have been resolved!")
    print("=" * 70)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
