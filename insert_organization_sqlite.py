#!/usr/bin/env python3
"""
Insert organization data into SQLite database
"""

import os
import sys
import sqlite3
from datetime import datetime

def insert_organization_data():
    """Insert organization and social links data into SQLite"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🏢 Inserting organization data into SQLite...")
        
        # Insert organization data
        org_data = (
            'فينيل آرت',  # name_ar
            'VinylArt',   # name_en
            'فن الديكور العصري',  # slogan_ar
            'Modern Decor Art',     # slogan_en
            'نحن متخصصون في تقديم حلول الديكور الحديثة بجودة عالية وتصاميم مبتكرة تلبي احتياجاتكم وتحقق أحلامكم.',  # about_ar
            'We specialize in providing modern decor solutions with high quality and innovative designs that meet your needs and fulfill your dreams.',  # about_en
            'info@vinylart.dz',   # contact_email
            '0663140341',         # phone_1
            '0551234567',          # phone_2
            'الجزائر، الجزائر العاصمة، حي المرادية',  # address
            'NIF123456789012345',  # tax_number
            1,                      # is_active
            datetime.now(),          # created_at
            datetime.now(),          # updated_at
            None,                   # base_city_id
            None,                   # created_by_id
            '36.7538',             # latitude
            '3.0588',              # longitude
            'ChIJv2WsK13vRxQRyfbt4e6gA8M',  # google_place_id
            'https://maps.google.com/?q=36.7538,3.0588'   # maps_url
        )
        
        cursor.execute('''
            INSERT INTO api_organization (
                name_ar, name_en, slogan_ar, slogan_en, about_ar, about_en,
                contact_email, phone_1, phone_2, address, tax_number,
                is_active, created_at, updated_at, base_city_id, created_by_id,
                latitude, longitude, google_place_id, maps_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', org_data)
        
        org_id = cursor.lastrowid
        print(f"✅ Organization inserted with ID: {org_id}")
        
        # Social media links data
        social_links = [
            (org_id, 'facebook', 'public', 'https://www.facebook.com/profile.php?id=61588391030740', 'fa-brands fa-facebook', 1, 1, datetime.now(), datetime.now()),
            (org_id, 'youtube', 'public', 'https://www.youtube.com/@store_paclos', 'fa-brands fa-youtube', 2, 1, datetime.now(), datetime.now()),
            (org_id, 'whatsapp', 'public', 'https://wa.me/213663140341', 'fa-brands fa-whatsapp', 3, 1, datetime.now(), datetime.now()),
            (org_id, 'instagram', 'public', 'https://www.instagram.com/vinylartdz', 'fa-brands fa-instagram', 4, 1, datetime.now(), datetime.now()),
            (org_id, 'tiktok', 'public', 'https://www.tiktok.com/@mansour.2026', 'fa-brands fa-tiktok', 5, 1, datetime.now(), datetime.now())
        ]
        
        # Clear existing social links
        cursor.execute("DELETE FROM api_social WHERE organization_id = ?", (org_id,))
        
        # Insert social links
        for social_data in social_links:
            cursor.execute('''
                INSERT INTO api_social (
                    organization_id, platform_name, platform_type, url, icon_class,
                    order_index, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', social_data)
            print(f"✅ Social link inserted: {social_data[2]}")
        
        # Commit changes
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM api_organization")
        org_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM api_social")
        social_count = cursor.fetchone()[0]
        
        print(f"\n📊 Verification:")
        print(f"   Organizations: {org_count}")
        print(f"   Social links: {social_count}")
        
        conn.close()
        print("\n🎉 Organization data successfully inserted into SQLite!")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🏢 VINYLART - SQLite Data Insertion")
    print("=" * 60)
    
    success = insert_organization_data()
    
    if success:
        print("\n✅ Data insertion completed successfully!")
        print("You can now run the application with the organization data.")
    else:
        print("\n❌ Data insertion failed. Please check error messages above.")
    
    print("=" * 60)
