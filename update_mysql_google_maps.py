#!/usr/bin/env python3
"""
MySQL Google Maps Integration Update Script
Updates MySQL database with new Google Maps fields
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_mysql():
    """Connect to MySQL database"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'vynilart'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Connected to MySQL successfully")
        return connection
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def update_organization_table(cursor):
    """Add Google Maps fields to api_organization table"""
    print("\n🏢 Updating api_organization table...")
    
    queries = [
        # Add latitude field
        """
        ALTER TABLE api_organization 
        ADD COLUMN latitude DECIMAL(22, 16) NULL 
        COMMENT 'خط العرض من جوجل مابس'
        """,
        
        # Add longitude field
        """
        ALTER TABLE api_organization 
        ADD COLUMN longitude DECIMAL(22, 16) NULL 
        COMMENT 'خط الطول من جوجل مابس'
        """,
        
        # Add google_place_id field
        """
        ALTER TABLE api_organization 
        ADD COLUMN google_place_id VARCHAR(255) NULL 
        COMMENT 'معرف المكان من جوجل'
        """,
        
        # Add maps_url field
        """
        ALTER TABLE api_organization 
        ADD COLUMN maps_url VARCHAR(500) NULL 
        COMMENT 'رابط خرائط جوجل المباشر'
        """
    ]
    
    for i, query in enumerate(queries, 1):
        try:
            cursor.execute(query)
            print(f"   ✅ Field {i} added successfully")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print(f"   ⚠️  Field {i} already exists")
            else:
                print(f"   ❌ Error adding field {i}: {e}")

def update_shipping_table(cursor):
    """Add Google Maps fields to core_shipping table"""
    print("\n🚚 Updating core_shipping table...")
    
    queries = [
        # Add pickup_latitude field
        """
        ALTER TABLE core_shipping 
        ADD COLUMN pickup_latitude DECIMAL(22, 16) NULL 
        COMMENT 'خط عرض نقطة الاستلام'
        """,
        
        # Add pickup_longitude field
        """
        ALTER TABLE core_shipping 
        ADD COLUMN pickup_longitude DECIMAL(22, 16) NULL 
        COMMENT 'خط طول نقطة الاستلام'
        """,
        
        # Add radius_km field
        """
        ALTER TABLE core_shipping 
        ADD COLUMN radius_km INT NULL 
        COMMENT 'نطاق التوصيل بالكيلومتر'
        """,
        
        # Add maps_url field
        """
        ALTER TABLE core_shipping 
        ADD COLUMN maps_url VARCHAR(500) NULL 
        COMMENT 'رابط خرائط جوجل لنقطة الاستلام'
        """
    ]
    
    for i, query in enumerate(queries, 1):
        try:
            cursor.execute(query)
            print(f"   ✅ Field {i} added successfully")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print(f"   ⚠️  Field {i} already exists")
            else:
                print(f"   ❌ Error adding field {i}: {e}")

def add_indexes(cursor):
    """Add performance indexes"""
    print("\n📊 Adding performance indexes...")
    
    indexes = [
        ("idx_org_latitude", "api_organization", "latitude"),
        ("idx_org_longitude", "api_organization", "longitude"),
        ("idx_org_google_place_id", "api_organization", "google_place_id"),
        ("idx_shipping_pickup_lat", "core_shipping", "pickup_latitude"),
        ("idx_shipping_pickup_lng", "core_shipping", "pickup_longitude"),
        ("idx_shipping_radius_km", "core_shipping", "radius_km"),
    ]
    
    for index_name, table, column in indexes:
        try:
            cursor.execute(f"CREATE INDEX {index_name} ON {table}({column})")
            print(f"   ✅ Index {index_name} created")
        except pymysql.Error as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print(f"   ⚠️  Index {index_name} already exists")
            else:
                print(f"   ❌ Error creating index {index_name}: {e}")

def verify_updates(cursor):
    """Verify the updates"""
    print("\n🔍 Verifying updates...")
    
    # Check api_organization
    cursor.execute("DESCRIBE api_organization")
    org_columns = [row['Field'] for row in cursor.fetchall()]
    org_fields = ['latitude', 'longitude', 'google_place_id', 'maps_url']
    
    print("\n🏢 api_organization table:")
    for field in org_fields:
        status = "✅" if field in org_columns else "❌"
        print(f"   {status} {field}")
    
    # Check core_shipping
    cursor.execute("DESCRIBE core_shipping")
    shipping_columns = [row['Field'] for row in cursor.fetchall()]
    shipping_fields = ['pickup_latitude', 'pickup_longitude', 'radius_km', 'maps_url']
    
    print("\n🚚 core_shipping table:")
    for field in shipping_fields:
        status = "✅" if field in shipping_columns else "❌"
        print(f"   {status} {field}")

def main():
    """Main execution function"""
    print("🗺️  MySQL Google Maps Integration Update")
    print("=" * 50)
    
    connection = connect_mysql()
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            # Update tables
            update_organization_table(cursor)
            update_shipping_table(cursor)
            
            # Add indexes
            add_indexes(cursor)
            
            # Verify updates
            verify_updates(cursor)
            
            # Commit changes
            connection.commit()
            print("\n✅ All updates completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Error during update: {e}")
        connection.rollback()
    finally:
        connection.close()
        print("\n🔌 Connection closed")

if __name__ == "__main__":
    main()
