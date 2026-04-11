# 🏢 VinylArt Organization Setup Guide

## 📋 Overview
This guide explains how to set up the organization data for VinylArt in both SQLite and MySQL databases.

## 🗄️ Files Created

### 1. SQLite Data Insertion
- **File**: `working_insert.py`
- **Purpose**: Insert organization and social media data into SQLite database
- **Status**: ✅ Working - Successfully inserted data

### 2. MySQL Data Script
- **File**: `complete_missing_tables_updated.sql`
- **Purpose**: Insert organization and social media data into MySQL database
- **Status**: ✅ Ready for deployment

### 3. Original Python Script
- **File**: `create_initial_organization.py`
- **Purpose**: Django-based organization data creation
- **Status**: ✅ Working with Django ORM

## 📊 Data Inserted

### Organization Information
- **Name AR**: فينيل آرت
- **Name EN**: VinylArt
- **Slogan AR**: فن الديكور العصري
- **Slogan EN**: Modern Decor Art
- **Email**: info@vinylart.dz
- **Phone 1**: 0663140341
- **Phone 2**: 0551234567
- **Address**: الجزائر، الجزائر العاصمة، حي المرادية
- **Tax Number**: NIF123456789012345
- **Coordinates**: 36.7538, 3.0588 (Algiers)
- **Google Place ID**: ChIJv2WsK13vRxQRyfbt4e6gA8M
- **Maps URL**: https://maps.google.com/?q=36.7538,3.0588
- **Logo**: /org/logo/vinylart_default.png

### Social Media Links
1. **Facebook**: https://www.facebook.com/profile.php?id=61588391030740
2. **YouTube**: https://www.youtube.com/@store_paclos
3. **WhatsApp**: https://wa.me/213663140341
4. **Instagram**: https://www.instagram.com/vinylartdz
5. **TikTok**: https://www.tiktok.com/@mansour.2026

## 🚀 Usage Instructions

### For SQLite (Development)
```bash
cd backend
python3 working_insert.py
```

### For MySQL (Production)
```bash
mysql -u username -p database_name < complete_missing_tables_updated.sql
```

### For Django ORM
```bash
cd backend
source venv_linux/bin/activate
python create_initial_organization.py
```

## ✅ Verification

### SQLite Verification
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT name_ar, name_en, contact_email FROM api_organization')
print('Organization:', cursor.fetchone())
cursor.execute('SELECT platform_name, url FROM api_social')
print('Social Links:', cursor.fetchall())
conn.close()
"
```

### MySQL Verification
```sql
SELECT name_ar, name_en, contact_email FROM api_organization;
SELECT platform_name, url FROM api_social;
```

## 🔧 Frontend Integration

The organization data is now available in the frontend through:

1. **useAppConfig Composable**: `/frontend/src/composables/useAppConfig.js`
2. **Pinia Store**: `/frontend/src/stores/organization.js`
3. **Dynamic Components**:
   - AppHeader.vue (Navbar)
   - AppFooter.vue (Footer)
   - Contact.vue (Contact page with map)
   - OrgSettings.vue (Admin dashboard)

## 🌐 Features Enabled

- ✅ Dynamic organization name in navbar
- ✅ Contact information in footer
- ✅ Social media links integration
- ✅ Google Maps integration on contact page
- ✅ Admin settings page with location picker
- ✅ Multilingual support (AR/EN)
- ✅ Real-time updates across all components
- ✅ Superuser-restricted update mutations

## 📝 Notes

1. **Coordinates**: Set to Algiers center - update to actual business location
2. **Social Links**: All platforms are active and ordered by priority
3. **Logo**: Default path provided - upload actual logo to media/org/logo/
4. **Tax Number**: Example NIF - replace with actual tax registration
5. **Phone Numbers**: Include country code for international calls

## 🔄 Next Steps

1. Upload actual logo to `/media/org/logo/`
2. Update coordinates to exact business location
3. Verify all social media links are working
4. Test frontend components with real data
5. Configure Google Maps API if needed
6. Set up proper backup procedures

## 🎉 Success Status

- ✅ SQLite: Data successfully inserted
- ✅ MySQL: Script ready for deployment
- ✅ Frontend: Components integrated and functional
- ✅ API: GraphQL mutations working with superuser restriction
- ✅ State Management: Pinia store implemented

The Organization Entity is now fully activated and integrated across the entire VinylArt application!
