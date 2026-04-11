-- =====================================================
-- VINYLART - COMPLETE ORGANIZATION SETUP FOR MYSQL
-- =====================================================
-- This script creates the organization record and social links
-- with all the initial data for VinylArt

-- Insert Organization Record
INSERT INTO `api_organization` (
    `name_ar`, `name_en`, `slogan_ar`, `slogan_en`, 
    `about_ar`, `about_en`, `contact_email`, `phone_1`, `phone_2`,
    `address`, `tax_number`, `latitude`, `longitude`, 
    `google_place_id`, `maps_url`, `is_active`,
    `created_at`, `updated_at`
) VALUES (
    'فينيل آرت',
    'VinylArt',
    'فن الديكور العصري',
    'Modern Decor Art',
    'نحن متخصصون في تقديم حلول الديكور الحديثة بجودة عالية وتصاميم مبتكرة تلبي احتياجاتكم وتحقق أحلامكم.',
    'We specialize in providing modern decor solutions with high quality and innovative designs that meet your needs and fulfill your dreams.',
    'info@vinylart.dz',
    '0663140341',
    '0551234567',
    'الجزائر، الجزائر العاصمة، حي المرادية',
    'NIF123456789012345',
    '36.7538',
    '3.0588',
    'ChIJv2WsK13vRxQRyfbt4e6gA8M',
    'https://maps.google.com/?q=36.7538,3.0588',
    1,
    NOW(),
    NOW()
);

-- Get the organization ID (assuming it's the first record)
SET @org_id = (SELECT id FROM `api_organization` WHERE `name_ar` = 'فينيل آرت' LIMIT 1);

-- Insert Social Media Links
INSERT INTO `api_social` (
    `organization_id`, `platform_name`, `platform_type`, `url`, 
    `icon_class`, `order_index`, `is_active`,
    `created_at`, `updated_at`
) VALUES
-- Facebook
(@org_id, 'facebook', 'public', 'https://www.facebook.com/profile.php?id=61588391030740', 'fa-brands fa-facebook', 1, 1, NOW(), NOW()),

-- YouTube
(@org_id, 'youtube', 'public', 'https://www.youtube.com/@store_paclos', 'fa-brands fa-youtube', 2, 1, NOW(), NOW()),

-- WhatsApp
(@org_id, 'whatsapp', 'public', 'https://wa.me/213663140341', 'fa-brands fa-whatsapp', 3, 1, NOW(), NOW()),

-- Instagram
(@org_id, 'instagram', 'public', 'https://www.instagram.com/vinylartdz', 'fa-brands fa-instagram', 4, 1, NOW(), NOW()),

-- TikTok
(@org_id, 'tiktok', 'public', 'https://www.tiktok.com/@mansour.2026', 'fa-brands fa-tiktok', 5, 1, NOW(), NOW());

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify Organization Insert
SELECT 
    id, name_ar, name_en, contact_email, phone_1, address,
    latitude, longitude, is_active, created_at
FROM `api_organization` 
WHERE name_ar = 'فينيل آرت';

-- Verify Social Links Insert
SELECT 
    s.id, s.platform_name, s.platform_type, s.url, s.icon_class, 
    s.order_index, s.is_active, o.name_ar as organization_name
FROM `api_social` s
JOIN `api_organization` o ON s.organization_id = o.id
WHERE o.name_ar = 'فينيل آرت'
ORDER BY s.order_index;

-- =====================================================
-- SAMPLE DATA SUMMARY
-- =====================================================

-- Organization Summary:
-- - Name: فينيل آرت / VinylArt
-- - Email: info@vinylart.dz
-- - Phone: 0663140341
-- - Address: الجزائر، الجزائر العاصمة، حي المرادية
-- - Coordinates: 36.7538, 3.0588 (Algiers)
-- - Tax Number: NIF123456789012345
-- - Social Links: Facebook, YouTube, WhatsApp, Instagram, TikTok

-- =====================================================
-- NOTES FOR DEPLOYMENT
-- =====================================================
-- 1. Run this script after creating the tables structure
-- 2. Verify that the organization record is created correctly
-- 3. Check that all social links are properly linked
-- 4. Update coordinates if needed for actual business location
-- 5. Modify social media URLs if they change
-- 6. The organization is set as active (is_active = 1)

-- =====================================================
-- END OF SCRIPT
-- =====================================================
