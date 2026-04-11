#!/usr/bin/env python3
"""
Check SQLite schema for api_organization table
"""

import os
import sqlite3

def check_schema():
    """Check the actual schema of api_organization table"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking api_organization table schema...")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(api_organization)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Columns in api_organization table:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - NOT NULL: {bool(col[3])} - DEFAULT: {col[4]}")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_organization'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print(f"\n✅ Table api_organization exists")
        else:
            print(f"\n❌ Table api_organization does not exist")
        
        # Check social table too
        cursor.execute("PRAGMA table_info(api_social)")
        social_columns = cursor.fetchall()
        
        print(f"\n📋 Columns in api_social table:")
        for col in social_columns:
            print(f"   - {col[1]} ({col[2]}) - NOT NULL: {bool(col[3])} - DEFAULT: {col[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_schema()
