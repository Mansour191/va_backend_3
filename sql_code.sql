-- ============================================
-- VinylArt Dashboard Settings Enhancement Migration
-- MySQL 8.0+ Compatible
-- ============================================

-- Add new UI customization fields to api_dashboardsettings table
ALTER TABLE api_dashboardsettings 
ADD COLUMN IF NOT EXISTS layout_json JSON COMMENT 'Advanced layout configuration for dashboard widgets',
ADD COLUMN IF NOT EXISTS refresh_interval INT DEFAULT 30 COMMENT 'Auto-refresh interval in seconds',
ADD COLUMN IF NOT EXISTS show_notifications TINYINT(1) DEFAULT 1 COMMENT 'Enable/disable dashboard notifications',
ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#3B82F6' COMMENT 'Primary theme color in hex format',
ADD COLUMN IF NOT EXISTS default_chart_type VARCHAR(20) DEFAULT 'line' COMMENT 'Default chart type for analytics';

-- Add indexes for new dashboard settings fields
CREATE INDEX IF NOT EXISTS api_dashboardsettings_refresh_interval_idx ON api_dashboardsettings(refresh_interval);
CREATE INDEX IF NOT EXISTS api_dashboardsettings_show_notifications_idx ON api_dashboardsettings(show_notifications);

-- ============================================
-- VinylArt Professional Blog Enhancement Migration
-- MySQL 8.0+ Compatible
-- ============================================

-- Add new professional blogging fields to existing api_blogpost table
ALTER TABLE api_blogpost 
ADD COLUMN excerpt TEXT,
ADD COLUMN featured_image_url VARCHAR(500),
ADD COLUMN view_count INT DEFAULT 0,
ADD COLUMN scheduled_at DATETIME(6),
ADD COLUMN read_time_minutes INT DEFAULT 0;

-- Update is_published field with help text (if supported)
ALTER TABLE api_blogpost 
MODIFY COLUMN is_published TINYINT(1) DEFAULT 0 COMMENT 'Whether this post is published';

-- Add indexes for new blog post fields for performance
CREATE INDEX api_blogpos_schedul_93e380_idx ON api_blogpost(scheduled_at);
CREATE INDEX api_blogpos_view_co_a38f40_idx ON api_blogpost(view_count);
CREATE INDEX api_blogpos_read_ti_7f4b2e_idx ON api_blogpost(read_time_minutes);
CREATE INDEX api_blogpos_excerpt_8c3d5f_idx ON api_blogpost(excerpt(255));
CREATE INDEX api_blogpos_featured_4e2a9c_idx ON api_blogpost(featured_image_url(255));

-- Add new fields to existing api_blogcategory table (if not already added)
ALTER TABLE api_blogcategory 
ADD COLUMN IF NOT EXISTS description_ar TEXT,
ADD COLUMN IF NOT EXISTS icon_class VARCHAR(100),
ADD COLUMN IF NOT EXISTS order_priority INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS is_featured TINYINT(1) DEFAULT 0,
ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255);

-- Add indexes for blog category fields (if not already exists)
CREATE INDEX IF NOT EXISTS api_blogcategory_order_priority_idx ON api_blogcategory(order_priority);
CREATE INDEX IF NOT EXISTS api_blogcategory_is_featured_idx ON api_blogcategory(is_featured);

-- Update existing blog posts with default values (optional)
UPDATE api_blogpost 
SET 
    excerpt = COALESCE(excerpt, LEFT(COALESCE(content_en, content_ar, ''), 300)),
    view_count = COALESCE(view_count, views, 0),
    read_time_minutes = COALESCE(read_time_minutes, 
        CASE 
            WHEN LENGTH(COALESCE(content_en, content_ar, '')) > 0 
            THEN GREATEST(1, ROUND(LENGTH(COALESCE(content_en, content_ar, '')) / 1000))
            ELSE 1 
        END
    )
WHERE 
    excerpt IS NULL OR view_count IS NULL OR read_time_minutes IS NULL;

-- Update existing categories with default values (optional)
UPDATE api_blogcategory 
SET 
    order_priority = COALESCE(order_priority, id),  -- Use ID as initial priority
    is_featured = COALESCE(is_featured, 0),
    meta_title = COALESCE(meta_title, CONCAT(name_en, ' - VinylArt Blog'))
WHERE 
    order_priority IS NULL OR order_priority = 0;

-- Verification query for blog post table
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    column_comment
FROM information_schema.columns 
WHERE table_name = 'api_blogpost' 
    AND table_schema = DATABASE()
    AND column_name IN ('excerpt', 'featured_image_url', 'view_count', 'scheduled_at', 'read_time_minutes', 'is_published')
ORDER BY ordinal_position;

-- Verification query for blog category table
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'api_blogcategory' 
    AND table_schema = DATABASE()
ORDER BY ordinal_position;

-- ============================================
-- VinylArt Wishlist Settings Marketing Enhancement Migration
-- MySQL 8.0+ Compatible
-- ============================================

-- Add new marketing and sharing fields to api_wishlistsettings table
ALTER TABLE api_wishlistsettings 
ADD COLUMN IF NOT EXISTS items_per_page INT DEFAULT 20 COMMENT 'Number of items to display per page',
ADD COLUMN IF NOT EXISTS sort_by VARCHAR(20) DEFAULT 'created_at' COMMENT 'Default sort order',
ADD COLUMN IF NOT EXISTS sort_order VARCHAR(4) DEFAULT 'desc' COMMENT 'Sort direction',
ADD COLUMN IF NOT EXISTS email_notifications TINYINT(1) DEFAULT 1 COMMENT 'Enable email notifications',
ADD COLUMN IF NOT EXISTS push_notifications TINYINT(1) DEFAULT 1 COMMENT 'Enable push notifications',
ADD COLUMN IF NOT EXISTS notify_on_price_drop TINYINT(1) DEFAULT 1 COMMENT 'Notify when wishlist item price drops',
ADD COLUMN IF NOT EXISTS alert_on_low_stock TINYINT(1) DEFAULT 1 COMMENT 'Alert when wishlist items have low stock',
ADD COLUMN IF NOT EXISTS auto_remove_out_of_stock TINYINT(1) DEFAULT 0 COMMENT 'Automatically remove out-of-stock items',
ADD COLUMN IF NOT EXISTS auto_remove_discontinued TINYINT(1) DEFAULT 1 COMMENT 'Automatically remove discontinued products',
ADD COLUMN IF NOT EXISTS make_public TINYINT(1) DEFAULT 0 COMMENT 'Make wishlist publicly visible',
ADD COLUMN IF NOT EXISTS privacy_level VARCHAR(10) DEFAULT 'private' COMMENT 'Privacy level for wishlist visibility',
ADD COLUMN IF NOT EXISTS share_token VARCHAR(64) UNIQUE COMMENT 'Unique token for sharing wishlist',
ADD COLUMN IF NOT EXISTS max_items_allowed INT DEFAULT 100 COMMENT 'Maximum number of items allowed in wishlist';

-- Add indexes for new wishlist settings fields for performance
CREATE INDEX IF NOT EXISTS api_wishlistsettings_share_token_idx ON api_wishlistsettings(share_token);
CREATE INDEX IF NOT EXISTS api_wishlistsettings_privacy_level_idx ON api_wishlistsettings(privacy_level);

-- Update existing records with default values for new fields
UPDATE api_wishlistsettings 
SET 
    items_per_page = COALESCE(items_per_page, 20),
    sort_by = COALESCE(sort_by, 'created_at'),
    sort_order = COALESCE(sort_order, 'desc'),
    email_notifications = COALESCE(email_notifications, 1),
    push_notifications = COALESCE(push_notifications, 1),
    notify_on_price_drop = COALESCE(notify_on_price_drop, 1),
    alert_on_low_stock = COALESCE(alert_on_low_stock, 1),
    auto_remove_out_of_stock = COALESCE(auto_remove_out_of_stock, 0),
    auto_remove_discontinued = COALESCE(auto_remove_discontinued, 1),
    make_public = COALESCE(make_public, 0),
    privacy_level = COALESCE(privacy_level, 'private'),
    max_items_allowed = COALESCE(max_items_allowed, 100)
WHERE 
    items_per_page IS NULL OR sort_by IS NULL OR sort_order IS NULL OR 
    email_notifications IS NULL OR push_notifications IS NULL OR 
    notify_on_price_drop IS NULL OR alert_on_low_stock IS NULL OR 
    auto_remove_out_of_stock IS NULL OR auto_remove_discontinued IS NULL OR 
    make_public IS NULL OR privacy_level IS NULL OR max_items_allowed IS NULL;

-- Verification query for wishlist settings table
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    column_comment
FROM information_schema.columns 
WHERE table_name = 'api_wishlistsettings' 
    AND table_schema = DATABASE()
    AND column_name IN (
        'items_per_page', 'sort_by', 'sort_order', 'email_notifications', 
        'push_notifications', 'notify_on_price_drop', 'alert_on_low_stock',
        'auto_remove_out_of_stock', 'auto_remove_discontinued', 'make_public',
        'privacy_level', 'share_token', 'max_items_allowed'
    )
ORDER BY ordinal_position;

-- ============================================
-- VinylArt User Profile Audit Trail Enhancement
-- MySQL 8.0+ Compatible
-- ============================================

-- Create UserProfileBeforeUpdate table for audit trail
CREATE TABLE IF NOT EXISTS api_userprofile_before_update (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_profile_id INT NOT NULL,
    phone VARCHAR(20) NULL,
    address TEXT NULL,
    bio TEXT NULL,
    avatar VARCHAR(255) NULL,
    preferences JSON NULL,
    settings JSON NULL,
    update_reason TEXT NULL COMMENT 'Reason for the profile update',
    updated_by_id INT NULL COMMENT 'User who made the update',
    device_info VARCHAR(500) NULL COMMENT 'Device/browser information',
    change_type VARCHAR(50) NULL COMMENT 'Type of change: profile_update, settings_change, etc.',
    snapshot_date DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'When this snapshot was created',
    original_created_at DATETIME(6) NOT NULL COMMENT 'Original created_at from profile',
    original_updated_at DATETIME(6) NOT NULL COMMENT 'Original updated_at from profile',
    
    -- Foreign Keys
    FOREIGN KEY (user_profile_id) REFERENCES api_userprofile(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    
    -- Indexes for performance (optimized for 4GB RAM)
    INDEX idx_api_userprofile_before_update_user_profile (user_profile_id),
    INDEX idx_api_userprofile_before_update_snapshot_date (snapshot_date),
    INDEX idx_api_userprofile_before_update_updated_by (updated_by_id),
    INDEX idx_api_userprofile_before_update_change_type (change_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Audit trail for user profile changes';

-- Verification query for UserProfileBeforeUpdate table
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    column_comment
FROM information_schema.columns 
WHERE table_name = 'api_userprofile_before_update' 
    AND table_schema = DATABASE()
ORDER BY ordinal_position;
