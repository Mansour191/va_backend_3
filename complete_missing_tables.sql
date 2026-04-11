-- =====================================================
-- Complete Missing Tables for VinylArt Database
-- Execute this in phpMyAdmin for database: vynilart_2_0
-- =====================================================

-- 1. Create api_organization table with Google Maps fields
CREATE TABLE IF NOT EXISTS `api_organization` (
    `id` bigint AUTO_INCREMENT PRIMARY KEY,
    `name_ar` varchar(255) NOT NULL,
    `name_en` varchar(255) NOT NULL,
    `logo` varchar(255) NOT NULL,
    `slogan_ar` varchar(500) NOT NULL,
    `slogan_en` varchar(500) NOT NULL,
    `about_ar` longtext NOT NULL,
    `about_en` longtext NOT NULL,
    `contact_email` varchar(255) NOT NULL,
    `phone_1` varchar(20) NOT NULL,
    `phone_2` varchar(20) NULL DEFAULT NULL,
    `address` longtext NOT NULL,
    `tax_number` varchar(100) NULL DEFAULT NULL,
    `created_by_id` bigint NULL DEFAULT NULL,
    `base_city_id` bigint NULL DEFAULT NULL,
    `is_active` bool NOT NULL DEFAULT TRUE,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    
    -- Google Maps Integration Fields
    `latitude` decimal(22,16) NULL DEFAULT NULL COMMENT 'خط العرض من جوجل مابس',
    `longitude` decimal(22,16) NULL DEFAULT NULL COMMENT 'خط الطول من جوجل مابس',
    `google_place_id` varchar(255) NULL DEFAULT NULL COMMENT 'معرف المكان من جوجل',
    `maps_url` varchar(500) NULL DEFAULT NULL COMMENT 'رابط خرائط جوجل المباشر'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Create api_social table
CREATE TABLE IF NOT EXISTS `api_social` (
    `id` bigint AUTO_INCREMENT PRIMARY KEY,
    `organization_id` bigint NOT NULL,
    `platform_name` varchar(50) NOT NULL,
    `platform_type` varchar(20) NOT NULL DEFAULT 'public',
    `url` varchar(500) NOT NULL,
    `icon_class` varchar(100) NOT NULL,
    `order_index` int NOT NULL DEFAULT 0,
    `is_active` bool NOT NULL DEFAULT TRUE,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    
    CONSTRAINT `fk_social_organization` FOREIGN KEY (`organization_id`) REFERENCES `api_organization`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Update core_shipping table with Google Maps fields (if table exists but missing fields)
ALTER TABLE `core_shipping` 
ADD COLUMN IF NOT EXISTS `pickup_latitude` decimal(22,16) NULL DEFAULT NULL COMMENT 'خط عرض نقطة الاستلام',
ADD COLUMN IF NOT EXISTS `pickup_longitude` decimal(22,16) NULL DEFAULT NULL COMMENT 'خط طول نقطة الاستلام',
ADD COLUMN IF NOT EXISTS `radius_km` int NULL DEFAULT NULL COMMENT 'نطاق التوصيل بالكيلومتر',
ADD COLUMN IF NOT EXISTS `maps_url` varchar(500) NULL DEFAULT NULL COMMENT 'رابط خرائط جوجل لنقطة الاستلام';

-- 4. Add indexes for api_organization
CREATE INDEX IF NOT EXISTS `org_is_active_idx` ON `api_organization`(`is_active`);
CREATE INDEX IF NOT EXISTS `org_base_city_idx` ON `api_organization`(`base_city_id`);
CREATE INDEX IF NOT EXISTS `org_created_by_idx` ON `api_organization`(`created_by_id`);
CREATE INDEX IF NOT EXISTS `idx_org_latitude` ON `api_organization`(`latitude`);
CREATE INDEX IF NOT EXISTS `idx_org_longitude` ON `api_organization`(`longitude`);
CREATE INDEX IF NOT EXISTS `idx_org_google_place_id` ON `api_organization`(`google_place_id`);

-- 5. Add indexes for api_social
CREATE INDEX IF NOT EXISTS `social_platform_name_idx` ON `api_social`(`platform_name`);
CREATE INDEX IF NOT EXISTS `social_is_active_idx` ON `api_social`(`is_active`);
CREATE INDEX IF NOT EXISTS `social_org_active_idx` ON `api_social`(`organization_id`, `is_active`);
CREATE INDEX IF NOT EXISTS `social_platform_type_idx` ON `api_social`(`platform_type`);
CREATE INDEX IF NOT EXISTS `social_order_idx` ON `api_social`(`order_index`);

-- 6. Add indexes for core_shipping
CREATE INDEX IF NOT EXISTS `idx_shipping_pickup_lat` ON `core_shipping`(`pickup_latitude`);
CREATE INDEX IF NOT EXISTS `idx_shipping_pickup_lng` ON `core_shipping`(`pickup_longitude`);
CREATE INDEX IF NOT EXISTS `idx_shipping_radius_km` ON `core_shipping`(`radius_km`);

-- 7. Add foreign key constraint for organization base_city
ALTER TABLE `api_organization` 
ADD CONSTRAINT IF NOT EXISTS `fk_org_base_city` 
FOREIGN KEY (`base_city_id`) REFERENCES `core_shipping`(`id`) ON DELETE SET NULL;

-- 8. Insert default organization data
INSERT IGNORE INTO `api_organization` (
    `name_ar`, `name_en`, `contact_email`, `is_active`,
    `created_at`, `updated_at`
) VALUES (
    'VinylArt', 'VinylArt', 'info@vinylart.dz', TRUE,
    NOW(), NOW()
);

-- 9. Verification queries
SELECT 'All missing tables created successfully!' as message;

-- Show final table count
SELECT COUNT(*) as total_tables FROM information_schema.tables 
WHERE table_schema = 'vynilart_2_0';

-- Show the new tables
SHOW TABLES LIKE 'api_%';
SHOW COLUMNS FROM `api_organization`;
SHOW COLUMNS FROM `api_social`;
