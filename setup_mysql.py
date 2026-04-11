#!/usr/bin/env python
"""
Setup MySQL database and populate with sample data
"""
import os
import sys
import django
from django.conf import settings
import pymysql
import decimal

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vynilart_project.settings')
django.setup()

def create_mysql_database():
    """Create MySQL database if it doesn't exist"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS vynilart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        connection.commit()
        cursor.close()
        connection.close()
        print("✅ MySQL database 'vynilart_db' created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating MySQL database: {e}")
        return False

def populate_data():
    """Populate database with sample data"""
    try:
        from core.models import (
            User, Category, Material, Product, ProductImage, 
            ProductVariant, Shipping, UserProfile, DesignCategory, 
            Design, BlogCategory, BlogPost, PricingEngine
        )
        
        print("🔄 Populating database with sample data...")
        
        # Create sample users
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@vynilart.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customer123',
            first_name='Customer',
            last_name='User'
        )
        
        # Create user profiles
        UserProfile.objects.create(
            user=admin_user,
            phone='+213 555 010 001',
            address='Algiers, Algeria',
            bio='System administrator'
        )
        
        UserProfile.objects.create(
            user=customer_user,
            phone='+213 555 010 002',
            address='Oran, Algeria',
            bio='Regular customer'
        )
        
        # Create categories
        vinyl_category = Category.objects.create(
            name_ar='فينيل',
            name_en='Vinyl',
            slug='vinyl',
            icon='vinyl-icon',
            waste_percent=decimal.Decimal('10.00'),
            description='Vinyl products for decoration'
        )
        
        wallpaper_category = Category.objects.create(
            name_ar='ورق جدران',
            name_en='Wallpaper',
            slug='wallpaper',
            icon='wallpaper-icon',
            waste_percent=decimal.Decimal('15.00'),
            description='Wallpaper for home decoration'
        )
        
        # Create materials
        vinyl_premium = Material.objects.create(
            name_ar='فينيل ممتاز',
            name_en='Premium Vinyl',
            description='High quality vinyl material',
            price_per_m2=decimal.Decimal('1200.00'),
            is_premium=True,
            properties={'thickness': '3mm', 'durability': 'high'}
        )
        
        vinyl_standard = Material.objects.create(
            name_ar='فينيل عادي',
            name_en='Standard Vinyl',
            description='Standard quality vinyl material',
            price_per_m2=decimal.Decimal('800.00'),
            is_premium=False,
            properties={'thickness': '2mm', 'durability': 'medium'}
        )
        
        wallpaper_premium = Material.objects.create(
            name_ar='ورق جدران ممتاز',
            name_en='Premium Wallpaper',
            description='High quality wallpaper material',
            price_per_m2=decimal.Decimal('1500.00'),
            is_premium=True,
            properties={'thickness': '0.5mm', 'pattern': 'custom'}
        )
        
        # Create products
        product1 = Product.objects.create(
            name_ar='فينيل زخرفة إسلامية',
            name_en='Islamic Pattern Vinyl',
            slug='islamic-pattern-vinyl',
            description_ar='فينيل بزخارف إسلامية تقليدية',
            description_en='Vinyl with traditional Islamic patterns',
            base_price=decimal.Decimal('5000.00'),
            cost=decimal.Decimal('3000.00'),
            category=vinyl_category,
            is_featured=True,
            is_new=True,
            stock=50,
            weight=decimal.Decimal('2.5'),
            dimensions='100x100 cm',
            tags=['islamic', 'traditional', 'premium'],
            seo_title='Islamic Pattern Vinyl - VynilArt',
            seo_description='High quality vinyl with Islamic patterns'
        )
        
        product2 = Product.objects.create(
            name_ar='ورق جدران زهور',
            name_en='Floral Wallpaper',
            slug='floral-wallpaper',
            description_ar='ورق جدران بتصاميم زهور جميلة',
            description_en='Beautiful floral wallpaper designs',
            base_price=decimal.Decimal('3500.00'),
            cost=decimal.Decimal('2000.00'),
            category=wallpaper_category,
            on_sale=True,
            discount_percent=20,
            stock=30,
            weight=decimal.Decimal('1.5'),
            dimensions='100x100 cm',
            tags=['floral', 'modern', 'sale'],
            seo_title='Floral Wallpaper - VynilArt',
            seo_description='Beautiful floral wallpaper for your home'
        )
        
        product3 = Product.objects.create(
            name_ar='فينيل هندسي',
            name_en='Geometric Vinyl',
            slug='geometric-vinyl',
            description_ar='فينيل بتصاميم هندسية عصرية',
            description_en='Modern geometric vinyl designs',
            base_price=decimal.Decimal('4500.00'),
            cost=decimal.Decimal('2800.00'),
            category=vinyl_category,
            is_featured=True,
            stock=25,
            weight=decimal.Decimal('2.0'),
            dimensions='100x100 cm',
            tags=['geometric', 'modern', 'contemporary'],
            seo_title='Geometric Vinyl - VynilArt',
            seo_description='Modern geometric vinyl designs'
        )
        
        # Create product images
        ProductImage.objects.create(
            product=product1,
            image_url='/media/products/islamic-vinyl-1.jpg',
            alt_text='Islamic Pattern Vinyl - Main Image',
            is_main=True,
            sort_order=1
        )
        
        ProductImage.objects.create(
            product=product2,
            image_url='/media/products/floral-wallpaper-1.jpg',
            alt_text='Floral Wallpaper - Main Image',
            is_main=True,
            sort_order=1
        )
        
        ProductImage.objects.create(
            product=product3,
            image_url='/media/products/geometric-vinyl-1.jpg',
            alt_text='Geometric Vinyl - Main Image',
            is_main=True,
            sort_order=1
        )
        
        # Create product variants
        ProductVariant.objects.create(
            product=product1,
            name='حجم صغير',
            sku='VIN-001-S',
            price=decimal.Decimal('2500.00'),
            stock=20,
            attributes={'size': '50x50 cm', 'color': 'gold'}
        )
        
        ProductVariant.objects.create(
            product=product1,
            name='حجم كبير',
            sku='VIN-001-L',
            price=decimal.Decimal('5000.00'),
            stock=15,
            attributes={'size': '100x100 cm', 'color': 'gold'}
        )
        
        # Create shipping locations (Algerian Wilayas)
        shipping_data = [
            ('16', 'الجزائر', 'Alger'),
            ('01', 'أدرار', 'Adrar'),
            ('02', 'شلف', 'Chlef'),
            ('03', 'أغواط', 'Laghouat'),
            ('04', 'أم البواقي', 'Oum El Bouaghi'),
            ('05', 'باتنة', 'Batna'),
            ('06', 'بجاية', 'Bejaia'),
            ('07', 'بسكرة', 'Biskra'),
            ('08', 'بشار', 'Bechar'),
            ('09', 'البليدة', 'Blida')
        ]
        
        for wilaya_id, name_ar, name_fr in shipping_data:
            Shipping.objects.create(
                wilaya_id=wilaya_id,
                name_ar=name_ar,
                name_fr=name_fr,
                stop_desk_price=decimal.Decimal('400.00'),
                home_delivery_price=decimal.Decimal('700.00')
            )
        
        # Create design categories
        design_cat1 = DesignCategory.objects.create(
            name_ar='زخارف إسلامية',
            name_en='Islamic Patterns',
            slug='islamic-patterns',
            description='Traditional Islamic design patterns',
            is_active=True
        )
        
        design_cat2 = DesignCategory.objects.create(
            name_ar='تصاميم حديثة',
            name_en='Modern Designs',
            slug='modern-designs',
            description='Contemporary design patterns',
            is_active=True
        )
        
        # Create designs
        Design.objects.create(
            name='Islamic Geometric Pattern 1',
            description='Beautiful Islamic geometric pattern with traditional colors',
            category=design_cat1,
            user=admin_user,
            is_featured=True,
            is_active=True,
            likes=25,
            downloads=15,
            tags=['islamic', 'geometric', 'traditional'],
            status='approved'
        )
        
        Design.objects.create(
            name='Modern Abstract Pattern',
            description='Contemporary abstract design for modern spaces',
            category=design_cat2,
            user=admin_user,
            is_active=True,
            likes=18,
            downloads=8,
            tags=['modern', 'abstract', 'contemporary'],
            status='approved'
        )
        
        # Create blog categories
        blog_cat1 = BlogCategory.objects.create(
            name_ar='ديكور',
            name_en='Decoration',
            slug='decoration',
            description='Tips and ideas for home decoration'
        )
        
        blog_cat2 = BlogCategory.objects.create(
            name_ar='تصاميم',
            name_en='Designs',
            slug='designs',
            description='Latest design trends and ideas'
        )
        
        # Create blog posts
        BlogPost.objects.create(
            title_ar='أفكار ديكور لغرفة المعيشة',
            title_en='Living Room Decoration Ideas',
            slug='living-room-decoration-ideas',
            content_ar='هنا تكتب أفكار ديكور رائعة لغرفة المعيشة...',
            content_en='Here you write great decoration ideas for the living room...',
            summary_ar='أفضل أفكار ديكور لغرفة المعيشة',
            summary_en='Best living room decoration ideas',
            category=blog_cat1,
            author=admin_user,
            views=150,
            is_published=True,
            tags=['living room', 'decoration', 'ideas']
        )
        
        BlogPost.objects.create(
            title_ar='أحدث اتجاهات التصميم الداخلي',
            title_en='Latest Interior Design Trends',
            slug='latest-interior-design-trends',
            content_ar='أحدث اتجاهات التصميم الداخلي لعام 2024...',
            content_en='Latest interior design trends for 2024...',
            summary_ar='تعرف على أحدث اتجاهات التصميم',
            summary_en='Discover the latest design trends',
            category=blog_cat2,
            author=admin_user,
            views=200,
            is_published=True,
            tags=['trends', 'interior', 'modern']
        )
        
        # Create pricing engine configuration
        PricingEngine.objects.create(
            raw_material_cost=decimal.Decimal('500.00'),
            labor_cost=decimal.Decimal('300.00'),
            international_shipping=decimal.Decimal('200.00')
        )
        
        print("✅ Database populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Setting up MySQL database for VynilArt...")
    
    # Step 1: Create database
    if not create_mysql_database():
        print("❌ Failed to create database. Please check MySQL connection.")
        return False
    
    # Step 2: Run migrations
    print("🔄 Running migrations...")
    os.system("python manage.py migrate")
    
    # Step 3: Populate data
    if populate_data():
        print("\n🎉 MySQL database setup completed successfully!")
        print("\n📊 Database Summary:")
        print("   - Users: 2 (admin, customer)")
        print("   - Categories: 2 (Vinyl, Wallpaper)")
        print("   - Materials: 3 (Premium Vinyl, Standard Vinyl, Premium Wallpaper)")
        print("   - Products: 3 (Islamic Vinyl, Floral Wallpaper, Geometric Vinyl)")
        print("   - Shipping: 10 Algerian Wilayas")
        print("   - Designs: 2")
        print("   - Blog Posts: 2")
        print("\n🔐 Login Credentials:")
        print("   - Admin: admin / admin123")
        print("   - Customer: customer / customer123")
        return True
    else:
        print("❌ Failed to populate database.")
        return False

if __name__ == '__main__':
    main()
