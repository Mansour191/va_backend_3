-- =====================================================
-- Google Maps Integration for VinylArt Database
-- Execute this in phpMyAdmin for database: vynilart_2_0
-- =====================================================

-- 1. Add Google Maps fields to api_organization table
ALTER TABLE `api_organization` 
ADD COLUMN `latitude` DECIMAL(22,16) NULL DEFAULT NULL COMMENT 'خط العرض من جوجل مابس',
ADD COLUMN `longitude` DECIMAL(22,16) NULL DEFAULT NULL COMMENT 'خط الطول من جوجل مابس',
ADD COLUMN `google_place_id` VARCHAR(255) NULL DEFAULT NULL COMMENT 'معرف المكان من جوجل',
ADD COLUMN `maps_url` VARCHAR(500) NULL DEFAULT NULL COMMENT 'رابط خرائط جوجل المباشر';

-- 2. Add Google Maps fields to core_shipping table
ALTER TABLE `core_shipping` 
ADD COLUMN `pickup_latitude` DECIMAL(22,16) NULL DEFAULT NULL COMMENT 'خط عرض نقطة الاستلام',
ADD COLUMN `pickup_longitude` DECIMAL(22,16) NULL DEFAULT NULL COMMENT 'خط طول نقطة الاستلام',
ADD COLUMN `radius_km` INT NULL DEFAULT NULL COMMENT 'نطاق التوصيل بالكيلومتر',
ADD COLUMN `maps_url` VARCHAR(500) NULL DEFAULT NULL COMMENT 'رابط خرائط جوجل لنقطة الاستلام';

-- 3. Add performance indexes
CREATE INDEX `idx_org_latitude` ON `api_organization`(`latitude`);
CREATE INDEX `idx_org_longitude` ON `api_organization`(`longitude`);
CREATE INDEX `idx_org_google_place_id` ON `api_organization`(`google_place_id`);

CREATE INDEX `idx_shipping_pickup_lat` ON `core_shipping`(`pickup_latitude`);
CREATE INDEX `idx_shipping_pickup_lng` ON `core_shipping`(`pickup_longitude`);
CREATE INDEX `idx_shipping_radius_km` ON `core_shipping`(`radius_km`);

-- 4. Verification queries
SELECT 'Google Maps fields added successfully!' as message;

-- Show updated table structures
SHOW COLUMNS FROM `api_organization`;
SHOW COLUMNS FROM `core_shipping`;
