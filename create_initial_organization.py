#!/usr/bin/env python3
"""
Create initial organization record for VinylArt
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vynilart_project.settings')
django.setup()

from api.models.organization import Organization, Social
from django.contrib.auth import get_user_model

User = get_user_model()

def create_initial_organization():
    """Create initial organization record with VinylArt data"""
    
    print("🏢 Creating initial organization record...")
    
    try:
        # Get or create the organization using the manager
        organization = Organization.objects.get_instance()
        
        # Update with VinylArt data
        organization.name_ar = 'فينيل آرت'
        organization.name_en = 'VinylArt'
        organization.slogan_ar = 'فن الديكور العصري'
        organization.slogan_en = 'Modern Decor Art'
        organization.about_ar = 'نحن متخصصون في تقديم حلول الديكور الحديثة بجودة عالية وتصاميم مبتكرة تلبي احتياجاتكم وتحقق أحلامكم.'
        organization.about_en = 'We specialize in providing modern decor solutions with high quality and innovative designs that meet your needs and fulfill your dreams.'
        organization.contact_email = 'info@vinylart.dz'
        organization.phone_1 = '0663140341'
        organization.phone_2 = '0551234567'
        organization.address = 'الجزائر، الجزائر العاصمة، حي المرادية'
        organization.tax_number = 'NIF123456789012345'
        
        # Google Maps coordinates for Algiers (example)
        organization.latitude = '36.7538'
        organization.longitude = '3.0588'
        organization.google_place_id = 'ChIJv2WsK13vRxQRyfbt4e6gA8M'
        organization.maps_url = 'https://maps.google.com/?q=36.7538,3.0588'
        
        # Set as active
        organization.is_active = True
        
        organization.save()
        
        print(f"✅ Organization created/updated: {organization}")
        print(f"   Name (AR): {organization.name_ar}")
        print(f"   Name (EN): {organization.name_en}")
        print(f"   Email: {organization.contact_email}")
        print(f"   Phone: {organization.phone_1}")
        print(f"   Address: {organization.address}")
        print(f"   Coordinates: {organization.latitude}, {organization.longitude}")
        
        # Create social media links
        social_links_data = [
            {
                'platform_name': 'facebook',
                'platform_type': 'public',
                'url': 'https://www.facebook.com/profile.php?id=61588391030740',
                'icon_class': 'fa-brands fa-facebook',
                'order_index': 1
            },
            {
                'platform_name': 'youtube',
                'platform_type': 'public',
                'url': 'https://www.youtube.com/@store_paclos',
                'icon_class': 'fa-brands fa-youtube',
                'order_index': 2
            },
            {
                'platform_name': 'whatsapp',
                'platform_type': 'public',
                'url': 'https://wa.me/213663140341',
                'icon_class': 'fa-brands fa-whatsapp',
                'order_index': 3
            },
            {
                'platform_name': 'instagram',
                'platform_type': 'public',
                'url': 'https://www.instagram.com/vinylartdz',
                'icon_class': 'fa-brands fa-instagram',
                'order_index': 4
            },
            {
                'platform_name': 'tiktok',
                'platform_type': 'public',
                'url': 'https://www.tiktok.com/@mansour.2026',
                'icon_class': 'fa-brands fa-tiktok',
                'order_index': 5
            }
        ]
        
        # Clear existing social links
        Social.objects.filter(organization=organization).delete()
        
        # Create new social links
        for social_data in social_links_data:
            social_link = Social.objects.create(
                organization=organization,
                **social_data
            )
            print(f"✅ Social link created: {social_link.platform_name}")
        
        print("\n🎉 Initial organization setup completed successfully!")
        return organization
        
    except Exception as e:
        print(f"❌ Error creating organization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def check_existing_data():
    """Check existing organization and social data"""
    print("🔍 Checking existing data...")
    
    # Check organizations
    org_count = Organization.objects.count()
    print(f"   Organizations found: {org_count}")
    
    if org_count > 0:
        for org in Organization.objects.all():
            print(f"   - {org.name_ar} ({org.name_en}) - Active: {org.is_active}")
    
    # Check social links
    social_count = Social.objects.count()
    print(f"   Social links found: {social_count}")
    
    if social_count > 0:
        for social in Social.objects.all():
            print(f"   - {social.platform_name}: {social.url}")

if __name__ == '__main__':
    print("=" * 60)
    print("🏢 VINYLART - Initial Organization Setup")
    print("=" * 60)
    
    # Check existing data
    check_existing_data()
    
    print("\n" + "=" * 60)
    
    # Create initial organization
    organization = create_initial_organization()
    
    if organization:
        print("\n✅ Setup completed successfully!")
        print("You can now use the organization data in your frontend application.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
    
    print("=" * 60)
