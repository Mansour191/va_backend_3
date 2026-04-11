-- =====================================================
-- Create api_organization table with Google Maps fields
-- Execute this in phpMyAdmin for database: vynilart_2_0
-- =====================================================

-- Create the complete api_organization table
CREATE TABLE `api_organization` (
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

-- Add indexes for performance
CREATE INDEX `org_is_active_idx` ON `api_organization`(`is_active`);
CREATE INDEX `org_base_city_idx` ON `api_organization`(`base_city_id`);
CREATE INDEX `org_created_by_idx` ON `api_organization`(`created_by_id`);
CREATE INDEX `idx_org_latitude` ON `api_organization`(`latitude`);
CREATE INDEX `idx_org_longitude` ON `api_organization`(`longitude`);
CREATE INDEX `idx_org_google_place_id` ON `api_organization`(`google_place_id`);

-- Add constraint for singleton pattern (only one active organization)
ALTER TABLE `api_organization` 
ADD CONSTRAINT `singleton_active_organization` 
UNIQUE (`id`) WHERE `is_active` = TRUE;

-- Insert default organization data
INSERT INTO `api_organization` (
    `name_ar`, `name_en`, `contact_email`, `is_active`,
    `created_at`, `updated_at`
) VALUES (
    'VinylArt', 'VinylArt', 'info@vinylart.dz', TRUE,
    NOW(), NOW()
);

-- Verification
SELECT 'api_organization table created successfully!' as message;
SELECT COUNT(*) as total_organizations FROM `api_organization`;
