#!/usr/bin/env python3
"""
Simple insert for organization data
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
        
        # Insert organization with explicit column order
        cursor.execute('''
            INSERT INTO api_organization (
                name_ar, name_en, slogan_ar, slogan_en, about_ar, about_en,
                contact_email, phone_1, phone_2, address, tax_number,
                is_active, created_at, updated_at, base_city_id, created_by_id,
                latitude, longitude, google_place_id, maps_url, logo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'فينيل آرت', 'VinylArt',
            'فن الديكور العصري', 'Modern Decor Art',
            'نحن متخصصون في تقديم حلول الديكور الحديثة بجودة عالية وتصاميم مبتكرة تلبي احتياجاتكم وتحقق أحلامكم.',
            'We specialize in providing modern decor solutions with high quality and innovative designs that meet your needs and fulfill your dreams.',
            'info@vinylart.dz', '0663140341', '0551234567',
            'الجزائر، الجزائر العاصمة، حي المرادية', 'NIF123456789012345',
            1, datetime.now(), datetime.now(), None, None,
            '36.7538', '3.0588', 'ChIJv2WsK13vRxQRyfbt4e6gA8M',
            'https://maps.google.com/?q=36.7538,3.0588', None
        ))
        
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
        
        cursor.execute('''
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    insert_data()
