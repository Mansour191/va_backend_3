# 🗺️ Google Maps Integration - MySQL Setup Guide

## نظرة عامة
هذا الدليل يشرح كيفية تحديث قاعدة بيانات MySQL لإضافة حقول Google Maps الجديدة.

## 📋 الملفات المطلوبة

### 1. ملف SQL الجاهز
- **mysql_google_maps_update.sql** - ملف SQL جاهز للتنفيذ اليدوي

### 2. سكريبت Python الأوتوماتيكي
- **update_mysql_google_maps.py** - سكريبت Python للتحديث التلقائي

### 3. إعدادات البيئة
- **.env.mysql** - نموذج إعدادات MySQL

## 🚀 طريقة التطبيق

### الطريقة الأولى: استخدام سكريبت Python (موصى به)

```bash
# 1. تثبيت المكتبات المطلوبة
pip install pymysql python-dotenv

# 2. نسخ إعدادات MySQL
cp .env.mysql .env

# 3. تعديل بيانات الاتصال في ملف .env
nano .env

# 4. تشغيل السكريبت
python update_mysql_google_maps.py
```

### الطريقة الثانية: تنفيذ SQL يدوياً

```bash
# 1. الدخول إلى MySQL
mysql -u root -p vynilart

# 2. تنفيذ ملف SQL
source mysql_google_maps_update.sql;
```

## 📊 الحقول الجديدة المضافة

### جدول المؤسسة (api_organization)
| الحقل | النوع | الوصف |
|--------|--------|---------|
| `latitude` | DECIMAL(22,16) | خط العرض من جوجل مابس |
| `longitude` | DECIMAL(22,16) | خط الطول من جوجل مابس |
| `google_place_id` | VARCHAR(255) | معرف المكان من جوجل |
| `maps_url` | VARCHAR(500) | رابط خرائط جوجل المباشر |

### جدول الشحن (core_shipping)
| الحقل | النوع | الوصف |
|--------|--------|---------|
| `pickup_latitude` | DECIMAL(22,16) | خط عرض نقطة الاستلام |
| `pickup_longitude` | DECIMAL(22,16) | خط طول نقطة الاستلام |
| `radius_km` | INT | نطاق التوصيل بالكيلومتر |
| `maps_url` | VARCHAR(500) | رابط خرائط جوجل لنقطة الاستلام |

## 🔗 العلاقات بين الجداول

- `api_organization.base_city_id` ← `core_shipping.id`
- تم تحديث العلاقة لضمان الربط الصحيح

## 📈 الفهارس الجديدة (Indexes)

لتحسين الأداء:
- `idx_org_latitude` على `api_organization.latitude`
- `idx_org_longitude` على `api_organization.longitude`
- `idx_org_google_place_id` على `api_organization.google_place_id`
- `idx_shipping_pickup_lat` على `core_shipping.pickup_latitude`
- `idx_shipping_pickup_lng` على `core_shipping.pickup_longitude`
- `idx_shipping_radius_km` على `core_shipping.radius_km`

## ✅ التحقق من التحديث

بعد التطبيق، تحقق من وجود الحقول:

```sql
-- التحقق من جدول المؤسسة
DESCRIBE api_organization;

-- التحقق من جدول الشحن
DESCRIBE core_shipping;
```

## 🔄 التحديثات اللاحقة

1. **تحديث البيانات الموجودة**:
   ```sql
   UPDATE api_organization 
   SET latitude = 36.7538, longitude = 3.0588
   WHERE id = 1;
   ```

2. **ربط بـ Google Maps API** في الواجهة الأمامية Vue 3

## 🐛 استكشاف الأخطاء

### مشاكل شائعة:
- **Access denied**: تحقق من صلاحيات MySQL
- **Column already exists**: الحقل موجود مسبقاً (طبيعي)
- **Connection failed**: تحقق من بيانات الاتصال في .env

### الحلول:
```bash
# إعطاء صلاحيات للمستخدم
GRANT ALL PRIVILEGES ON vynilart.* TO 'root'@'localhost';

# إعادة تحميل الصلاحيات
FLUSH PRIVILEGES;
```

## 📞 المساعدة

إذا واجهت أي مشاكل:
1. تحقق من نسخة MySQL (5.7+ موصى به)
2. تأكد من وجود قاعدة البيانات `vynilart`
3. تحقق من صلاحيات المستخدم

---
**✨ بعد التطبيق، سيكون النظام جاهزاً للتكامل الكامل مع Google Maps API**
