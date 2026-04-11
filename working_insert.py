#!/usr/bin/env python3
"""
Working insert for organization data - insert by column names
"""

import os
import sqlite3
from datetime import datetime

def insert_data():
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute("DELETE FROM api_social")
        cursor.execute("DELETE FROM api_organization")
        print("🗑️ Cleared existing data")
        
        # Insert organization using named parameters approach
        org_data = {
            'name_ar': 'فينيل آرت',
            'name_en': 'VinylArt',
            'logo': '/org/logo/vinylart_default.png',  # Provide a default logo path
            'slogan_ar': 'فن الديكور العصري',
            'slogan_en': 'Modern Decor Art',
            'about_ar': 'نحن متخصصون في تقديم حلول الديكور الحديثة بجودة عالية وتصاميم مبتكرة تلبي احتياجاتكم وتحقق أحلامكم.',
            'about_en': 'We specialize in providing modern decor solutions with high quality and innovative designs that meet your needs and fulfill your dreams.',
            'contact_email': 'info@vinylart.dz',
            'phone_1': '0663140341',
            'phone_2': '0551234567',
            'address': 'الجزائر، الجزائر العاصمة، حي المرادية',
            'tax_number': 'NIF123456789012345',
            'is_active': 1,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'base_city_id': None,
            'created_by_id': None,
            'google_place_id': 'ChIJv2WsK13vRxQRyfbt4e6gA8M',
            'latitude': '36.7538',
            'longitude': '3.0588',
            'maps_url': 'https://maps.google.com/?q=36.7538,3.0588'
        }
        
        # Build INSERT statement dynamically
        columns = list(org_data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = list(org_data.values())
        
        sql = f"INSERT INTO api_organization ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        
        org_id = cursor.lastrowid
        print(f"✅ Organization inserted with ID: {org_id}")
        
        # Insert social links
        social_links = [
            (org_id, 'facebook', 'public', 'https://www.facebook.com/profile.php?id=61588391030740', 'fa-brands fa-facebook', 1, 1, datetime.now(), datetime.now()),
            (org_id, 'youtube', 'public', 'https://www.youtube.com/@store_paclos', 'fa-brands fa-youtube', 2, 1, datetime.now(), datetime.now()),
            (org_id, 'whatsapp', 'public', 'https://wa.me/213663140341', 'fa-brands fa-whatsapp', 3, 1, datetime.now(), datetime.now()),
            (org_id, 'instagram', 'public', 'https://www.instagram.com/vinylartdz', 'fa-brands fa-instagram', 4, 1, datetime.now(), datetime.now()),
            (org_id, 'tiktok', 'public', 'https://www.tiktok.com/@mansour.2026', 'fa-brands fa-tiktok', 5, 1, datetime.now(), datetime.now())
        ]
        
        cursor.executemany('''
            INSERT INTO api_social (
                organization_id, platform_name, platform_type, url, icon_class,
                order_index, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', social_links)
        
        conn.commit()
        print("✅ Social links inserted")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM api_organization")
        org_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM api_social")
        social_count = cursor.fetchone()[0]
        
        print(f"\n📊 Summary:")
        print(f"   Organizations: {org_count}")
        print(f"   Social links: {social_count}")
        
        # Show inserted data
        cursor.execute("SELECT name_ar, name_en, contact_email FROM api_organization LIMIT 1")
        org = cursor.fetchone()
        print(f"\n🏢 Organization Data:")
        print(f"   Name AR: {org[0]}")
        print(f"   Name EN: {org[1]}")
        print(f"   Email: {org[2]}")
        
        print("\n🎉 SQLite data insertion completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    insert_data()
