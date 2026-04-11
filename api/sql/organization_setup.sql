-- VinylArt Organization Database Setup
-- Ensures utf8mb4 encoding for Arabic and emoji support

-- Create database with utf8mb4 encoding (if creating new database)
-- CREATE DATABASE vinylart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Set default character set for tables
ALTER DATABASE vinylart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create Organization table with utf8mb4 support
CREATE TABLE IF NOT EXISTS `api_organization` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name_ar` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `name_en` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `logo` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    `slogan_ar` VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `slogan_en` VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `about_ar` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `about_en` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `contact_email` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `phone_1` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `phone_2` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    `address` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `tax_number` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `singleton_active_organization` CHECK (
        `is_active` = FALSE OR 
        `id` = (SELECT MIN(`id`) FROM `api_organization` WHERE `is_active` = TRUE)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Create Social table with utf8mb4 support
CREATE TABLE IF NOT EXISTS `api_social` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `organization_id` BIGINT NOT NULL,
    `platform_name` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `url` VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `icon_class` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `order_index` INT UNSIGNED NOT NULL DEFAULT 0,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`organization_id`) REFERENCES `api_organization`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_org_platform` (`organization_id`, `platform_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS `org_is_active_idx` ON `api_organization` (`is_active`);
CREATE INDEX IF NOT EXISTS `social_platform_name_idx` ON `api_social` (`platform_name`);
CREATE INDEX IF NOT EXISTS `social_is_active_idx` ON `api_social` (`is_active`);
CREATE INDEX IF NOT EXISTS `social_org_active_idx` ON `api_social` (`organization_id`, `is_active`);
CREATE INDEX IF NOT EXISTS `social_order_idx` ON `api_social` (`order_index`);

-- Insert default organization data (if table is empty)
INSERT IGNORE INTO `api_organization` (
    `name_ar`, `name_en`, `slogan_ar`, `slogan_en`, 
    `about_ar`, `about_en`, `contact_email`, `phone_1`, 
    `address`, `is_active`
) VALUES (
    'VinylArt', 'VinylArt', 
    'الفن يلتقي بالجودة', 'Art Meets Quality',
    'VinylArt هي شركة رائدة في مجال الطباعة والتصميم، نقدم حلولاً مبتكرة لجميع احتياجات الطباعة عالية الجودة.',
    'VinylArt is a leading company in printing and design, offering innovative solutions for all high-quality printing needs.',
    'info@vinylart.dz', '+213 555 123 456',
    'شارع القدس، الجزائر العاصمة، الجزائر',
    TRUE
);

-- Get the organization ID for social links insertion
SET @org_id = (SELECT `id` FROM `api_organization` WHERE `is_active` = TRUE LIMIT 1);

-- Insert default social media links
INSERT IGNORE INTO `api_social` (
    `organization_id`, `platform_name`, `url`, `icon_class`, `order_index`, `is_active`
) VALUES 
(@org_id, 'Facebook', 'https://facebook.com/vinylart', 'fa-brands fa-facebook', 1, TRUE),
(@org_id, 'Instagram', 'https://instagram.com/vinylart', 'fa-brands fa-instagram', 2, TRUE),
(@org_id, 'TikTok', 'https://tiktok.com/@vinylart', 'fa-brands fa-tiktok', 3, TRUE),
(@org_id, 'YouTube', 'https://youtube.com/vinylart', 'fa-brands fa-youtube', 4, TRUE),
(@org_id, 'LinkedIn', 'https://linkedin.com/company/vinylart', 'fa-brands fa-linkedin', 5, TRUE);

-- Create triggers for automatic timestamp updates
DELIMITER //

CREATE TRIGGER IF NOT EXISTS `api_organization_updated_at` 
BEFORE UPDATE ON `api_organization`
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

CREATE TRIGGER IF NOT EXISTS `api_social_updated_at` 
BEFORE UPDATE ON `api_social`
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

DELIMITER ;

-- Create view for active organization with social links
CREATE OR REPLACE VIEW `v_active_organization` AS
SELECT 
    o.id,
    o.name_ar,
    o.name_en,
    o.logo,
    o.slogan_ar,
    o.slogan_en,
    o.about_ar,
    o.about_en,
    o.contact_email,
    o.phone_1,
    o.phone_2,
    o.address,
    o.tax_number,
    o.created_at,
    o.updated_at,
    (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'id', s.id,
                'platform_name', s.platform_name,
                'url', s.url,
                'icon_class', s.icon_class,
                'order_index', s.order_index
            )
        )
        FROM api_social s
        WHERE s.organization_id = o.id AND s.is_active = TRUE
        ORDER BY s.order_index ASC
    ) as social_links
FROM api_organization o
WHERE o.is_active = TRUE;

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON vinylart_db.* TO 'vinylart_user'@'localhost';

-- Final setup verification
SELECT 'Organization and Social tables created successfully with utf8mb4 encoding' as status;
