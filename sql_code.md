
-- ============================================
-- VinylArt Production Database Schema
-- MySQL 8.0+ Optimized
-- ============================================

-- Drop database if exists (CAREFUL: removes all data)
-- DROP DATABASE IF EXISTS vinylart;
-- CREATE DATABASE vinylart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE vinylart;

-- ============================================
-- 1. CORE DJANGO TABLES (Required by Django)
-- ============================================

-- Content Types (Django built-in)
CREATE TABLE IF NOT EXISTS django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model_76bd3d3b_uniq (app_label, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migrations (Django built-in)
CREATE TABLE IF NOT EXISTS django_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions (Django built-in)
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME(6) NOT NULL,
    INDEX django_session_expire_date_a5c62663 (expire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. AUTHENTICATION TABLES (Django Auth)
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6),
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    date_joined DATETIME(6) NOT NULL,
    INDEX auth_user_username_6821ab7c_like (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Groups
CREATE TABLE IF NOT EXISTS auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    INDEX auth_group_name_a6ea08ec_like (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Permissions
CREATE TABLE IF NOT EXISTS auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    UNIQUE KEY auth_permission_content_type_id_codename_01ab375a_uniq (content_type_id, codename),
    INDEX auth_permission_codename_01ab375a_like (codename),
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User groups (many-to-many)
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY auth_user_groups_user_id_group_id_94350c0c_uniq (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User permissions (many-to-many)
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_user_user_permissions_user_id_permission_id_14a6b632_uniq (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Group permissions
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_group_permissions_group_id_permission_id_0cd325b0_uniq (group_id, permission_id),
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. USER PROFILE (Extended user info)
-- ============================================

CREATE TABLE IF NOT EXISTS api_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    bio TEXT,
    avatar VARCHAR(255),
    preferences JSON,
    settings JSON,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. CATALOG TABLES
-- ============================================

-- Categories
CREATE TABLE IF NOT EXISTS api_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    icon VARCHAR(100),
    waste_percent DECIMAL(5,2) DEFAULT 10.00,
    is_active TINYINT(1) DEFAULT 1,
    image VARCHAR(500),
    description TEXT,
    parent_id INT,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX api_category_slug_like (slug),
    FOREIGN KEY (parent_id) REFERENCES api_category(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Materials
CREATE TABLE IF NOT EXISTS api_material (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    description TEXT,
    price_per_m2 DECIMAL(10,2) DEFAULT 0,
    is_premium TINYINT(1) DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    image VARCHAR(500),
    properties JSON,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Products
CREATE TABLE IF NOT EXISTS api_product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description_ar TEXT,
    description_en TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) DEFAULT 0,
    category_id INT,
    on_sale TINYINT(1) DEFAULT 0,
    discount_percent INT DEFAULT 0,
    is_featured TINYINT(1) DEFAULT 0,
    is_new TINYINT(1) DEFAULT 1,
    is_active TINYINT(1) DEFAULT 1,
    stock INT DEFAULT 0,
    weight DECIMAL(10,2),
    dimensions VARCHAR(100),
    tags JSON,
    seo_title VARCHAR(255),
    seo_description TEXT,
    sync_status VARCHAR(20) DEFAULT 'pending',
    erpnext_item_code VARCHAR(100),
    sync_error TEXT,
    last_synced_at DATETIME(6),
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX api_product_slug_like (slug),
    FOREIGN KEY (category_id) REFERENCES api_category(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Product Images
CREATE TABLE IF NOT EXISTS api_productimage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_main TINYINT(1) DEFAULT 0,
    sort_order INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Product Variants
CREATE TABLE IF NOT EXISTS api_productvariant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    attributes JSON,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Product-Material relationship (many-to-many)
CREATE TABLE IF NOT EXISTS api_product_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    material_id INT NOT NULL,
    UNIQUE KEY api_product_materials_product_id_material_id_uniq (product_id, material_id),
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES api_material(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. ORDER TABLES
-- ============================================

-- Shipping (Wilayas)
CREATE TABLE IF NOT EXISTS api_shipping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    wilaya_id VARCHAR(10) NOT NULL UNIQUE,
    name_ar VARCHAR(100) NOT NULL,
    name_fr VARCHAR(100) NOT NULL,
    stop_desk_price DECIMAL(10,2) DEFAULT 400,
    home_delivery_price DECIMAL(10,2) DEFAULT 700,
    is_active TINYINT(1) DEFAULT 1,
    regions JSON,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Shipping Methods
CREATE TABLE IF NOT EXISTS api_shipping_method (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id INT NOT NULL, -- الربط مع المؤسسة (مثل Paclos)
    name VARCHAR(100) NOT NULL,
    provider_name VARCHAR(100), 
    base_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    estimated_days VARCHAR(50),
    is_active TINYINT(1) DEFAULT 1,
    description TEXT,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    
    -- الفهارس والمفاتيح الأجنبية
    INDEX shipping_active_idx (is_active),
    INDEX shipping_org_idx (organization_id),
    CONSTRAINT fk_shipping_organization 
        FOREIGN KEY (organization_id) 
        REFERENCES api_organization(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Orders Table (Updated with Shipping Method FK)
CREATE TABLE IF NOT EXISTS api_order (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    user_id INT,
    customer_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(254),
    shipping_address TEXT NOT NULL,
    wilaya_id VARCHAR(10),
    
    -- إضافة الحقل هنا ليكون ضمن بنية الجدول
    shipping_method_id INT NULL, 
    
    subtotal DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20) DEFAULT 'cod',
    payment_status TINYINT(1) DEFAULT 0,
    notes TEXT,
    sync_status VARCHAR(20) DEFAULT 'pending',
    erpnext_sales_order_id VARCHAR(100),
    sync_error TEXT,
    last_synced_at DATETIME(6),
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,

    -- الفهارس (Indexes)
    INDEX api_order_order_number_like (order_number),
    INDEX api_order_status_idx (status),
    INDEX api_order_shipping_method_idx (shipping_method_id),

    -- جميع المفاتيح الأجنبية (Foreign Keys)
    CONSTRAINT fk_order_user 
        FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE SET NULL,
        
    CONSTRAINT fk_order_wilaya 
        FOREIGN KEY (wilaya_id) REFERENCES api_shipping(wilaya_id) ON DELETE SET NULL,
        
    CONSTRAINT fk_order_shipping_method 
        FOREIGN KEY (shipping_method_id) REFERENCES api_shipping_method(id) ON DELETE SET NULL
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order Items
CREATE TABLE IF NOT EXISTS api_orderitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    material_id INT,
    width DECIMAL(10,2) NOT NULL,
    height DECIMAL(10,2) NOT NULL,
    dimension_unit VARCHAR(10) DEFAULT 'cm',
    marble_texture VARCHAR(100),
    custom_design TEXT,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES api_order(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES api_material(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order Timeline
CREATE TABLE IF NOT EXISTS api_ordertimeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    note TEXT,
    user_id INT,
    timestamp DATETIME(6) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES api_order(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payments
CREATE TABLE IF NOT EXISTS api_payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    gateway_response JSON,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX api_payment_transaction_id_like (transaction_id),
    FOREIGN KEY (order_id) REFERENCES api_order(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Coupons
CREATE TABLE IF NOT EXISTS api_coupon (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    discount_type VARCHAR(20) DEFAULT 'percentage',
    discount_value DECIMAL(10,2) NOT NULL,
    min_amount DECIMAL(10,2) DEFAULT 0,
    max_discount DECIMAL(10,2),
    usage_limit INT,
    used_count INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    valid_from DATETIME(6),
    valid_to DATETIME(6),
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX api_coupon_code_like (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 6. CART & WISHLIST
-- ============================================

-- Cart Items
CREATE TABLE IF NOT EXISTS api_cartitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    material_id INT,
    quantity INT NOT NULL DEFAULT 1,
    options JSON,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES api_material(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Wishlist
CREATE TABLE IF NOT EXISTS api_wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at DATETIME(6) NOT NULL,
    UNIQUE KEY api_wishlist_user_id_product_id_uniq (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 7. REVIEWS & DESIGNS
-- ============================================

-- Reviews
CREATE TABLE IF NOT EXISTS api_review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    is_verified TINYINT(1) DEFAULT 0,
    helpful_count INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Review Reports
CREATE TABLE IF NOT EXISTS api_reviewreport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (review_id) REFERENCES api_review(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Design Categories
CREATE TABLE IF NOT EXISTS api_designcategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    image VARCHAR(500),
    is_active TINYINT(1) DEFAULT 1,
    design_count INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Designs
CREATE TABLE IF NOT EXISTS api_design (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image VARCHAR(500),
    category_id INT,
    user_id INT,
    is_featured TINYINT(1) DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    likes INT DEFAULT 0,
    downloads INT DEFAULT 0,
    tags JSON,
    status VARCHAR(20) DEFAULT 'pending',
    generated_at DATETIME(6),
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES api_designcategory(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 8. NOTIFICATIONS & ALERTS
-- ============================================

-- Notifications
CREATE TABLE IF NOT EXISTS api_notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read TINYINT(1) DEFAULT 0,
    data JSON,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alerts
CREATE TABLE IF NOT EXISTS api_alert (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    conditions JSON,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 9. ERPNext INTEGRATION
-- ============================================

-- ERPNext Sync Logs
CREATE TABLE IF NOT EXISTS api_erpnextsynclog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',
    message TEXT,
    records_synced INT DEFAULT 0,
    error_message TEXT,
    timestamp DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 10. AI & ANALYTICS
-- ============================================

-- Behavior Tracking
CREATE TABLE IF NOT EXISTS api_behaviortracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id INT,
    duration INT DEFAULT 0,
    metadata JSON,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    INDEX api_behaviortracking_session_id_idx (session_id),
    INDEX api_behaviortracking_action_idx (action),
    INDEX api_behaviortracking_created_at_idx (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Forecasts
CREATE TABLE IF NOT EXISTS api_forecast (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    forecast_type VARCHAR(50) NOT NULL,
    period VARCHAR(20) NOT NULL,
    predicted_demand INT,
    actual_demand INT,
    error_margin DECIMAL(5,2),
    algorithm_used VARCHAR(100),
    confidence DECIMAL(5,2),
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES api_product(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customer Segments
CREATE TABLE IF NOT EXISTS api_customersegment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    criteria JSON,
    is_active TINYINT(1) DEFAULT 1,
    priority INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX api_customersegment_is_active_idx (is_active),
    INDEX api_customersegment_priority_idx (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customer Segment Users (many-to-many)
CREATE TABLE IF NOT EXISTS api_customersegment_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customersegment_id INT NOT NULL,
    user_id INT NOT NULL,
    UNIQUE KEY api_customersegment_users_segment_id_user_id_uniq (customersegment_id, user_id),
    FOREIGN KEY (customersegment_id) REFERENCES api_customersegment(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pricing Engine
CREATE TABLE IF NOT EXISTS api_pricingengine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    raw_material_cost DECIMAL(10,2) DEFAULT 500,
    labor_cost DECIMAL(10,2) DEFAULT 300,
    international_shipping DECIMAL(10,2) DEFAULT 200
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 11. BLOG
-- ============================================

-- Blog Categories
CREATE TABLE IF NOT EXISTS api_blogcategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Blog Posts
CREATE TABLE IF NOT EXISTS api_blogpost (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title_ar VARCHAR(255) NOT NULL,
    title_en VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    content_ar LONGTEXT,
    content_en LONGTEXT,
    summary_ar TEXT,
    summary_en TEXT,
    category_id INT,
    author_id INT,
    featured_image VARCHAR(500),
    tags JSON,
    views INT DEFAULT 0,
    is_published TINYINT(1) DEFAULT 0,
    published_at DATETIME(6),
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES api_blogcategory(id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES auth_user(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 12. CONVERSATIONS (AI Chat)
-- ============================================

-- Conversation History
CREATE TABLE IF NOT EXISTS api_conversationhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(50) DEFAULT 'user',
    confidence DECIMAL(5,2),
    metadata JSON,
    created_at DATETIME(6) NOT NULL,
    INDEX api_conversationhistory_session_id_8d0f3e0c (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 13. DASHBOARD & SETTINGS
-- ============================================

-- Dashboard Settings
CREATE TABLE IF NOT EXISTS api_dashboardsettings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    widgets JSON,
    layout JSON,
    preferences JSON,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Wishlist Settings
CREATE TABLE IF NOT EXISTS api_wishlistsettings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    auto_add TINYINT(1) DEFAULT 1,
    max_items INT DEFAULT 100,
    email_reminders TINYINT(1) DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 14. INDEXES FOR PERFORMANCE
-- ============================================

-- Additional indexes for better query performance
CREATE INDEX idx_product_slug ON api_product(slug);
CREATE INDEX idx_product_category ON api_product(category_id);
CREATE INDEX idx_product_is_active ON api_product(is_active);
CREATE INDEX idx_product_created_at ON api_product(created_at);

CREATE INDEX idx_order_user ON api_order(user_id);
CREATE INDEX idx_order_status ON api_order(status);
CREATE INDEX idx_order_created_at ON api_order(created_at);

CREATE INDEX idx_orderitem_order ON api_orderitem(order_id);
CREATE INDEX idx_orderitem_product ON api_orderitem(product_id);

CREATE INDEX idx_cartitem_user ON api_cartitem(user_id);
CREATE INDEX idx_wishlist_user ON api_wishlist(user_id);

CREATE INDEX idx_review_product ON api_review(product_id);
CREATE INDEX idx_review_user ON api_review(user_id);

CREATE INDEX idx_notification_user ON api_notification(user_id);
CREATE INDEX idx_notification_is_read ON api_notification(is_read);

-- ============================================
-- 15. TRIGGERS FOR AUTO-UPDATES
-- ============================================

-- Update updated_at timestamp automatically
DELIMITER //
CREATE TRIGGER api_product_before_update 
BEFORE UPDATE ON api_product
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER api_category_before_update 
BEFORE UPDATE ON api_category
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER api_order_before_update 
BEFORE UPDATE ON api_order
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//

CREATE TRIGGER api_userprofile_before_update 
BEFORE UPDATE ON api_userprofile
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END//
DELIMITER ;

-- ============================================
-- 16. INITIAL DATA (Optional)
-- ============================================

-- Insert default pricing engine
INSERT INTO api_pricingengine (id, raw_material_cost, labor_cost, international_shipping) 
VALUES (1, 500, 300, 200)
ON DUPLICATE KEY UPDATE 
    raw_material_cost = VALUES(raw_material_cost),
    labor_cost = VALUES(labor_cost),
    international_shipping = VALUES(international_shipping);

-- ============================================
-- 17. VERIFICATION QUERIES
-- ============================================

-- Check all tables created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'vinylart' ORDER BY table_name;

-- Show table counts
-- SELECT 
--     table_name,
--     table_rows
-- FROM information_schema.tables 
-- WHERE table_schema = 'vinylart' 
-- ORDER BY table_name;

-- ============================================
-- 18. ORGANIZATION MODELS (Additional)
-- ============================================

-- Organization
CREATE TABLE IF NOT EXISTS api_organization (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    logo VARCHAR(255),
    slogan_ar VARCHAR(500),
    slogan_en VARCHAR(500),
    about_ar TEXT,
    about_en TEXT,
    contact_email VARCHAR(255) NOT NULL,
    phone_1 VARCHAR(20) NOT NULL,
    phone_2 VARCHAR(20),
    address TEXT,
    latitude DECIMAL(22, 16),
    longitude DECIMAL(22, 16),
    google_place_id VARCHAR(255),
    maps_url VARCHAR(500),
    tax_number VARCHAR(100),
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    base_city_id INT,
    created_by_id INT,
    INDEX api_organization_is_active_idx (is_active),
    INDEX api_organization_base_city_idx (base_city_id),
    INDEX api_organization_created_by_idx (created_by_id),
    CONSTRAINT singleton_active_organization UNIQUE (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Social Media Links
CREATE TABLE IF NOT EXISTS api_social (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id INT NOT NULL,
    platform_name VARCHAR(50) NOT NULL,
    platform_type VARCHAR(20) DEFAULT 'public',
    url VARCHAR(500) NOT NULL,
    icon_class VARCHAR(100),
    order_index INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    INDEX social_platform_name_idx (platform_name),
    INDEX social_is_active_idx (is_active),
    INDEX social_org_active_idx (organization_id, is_active),
    INDEX social_platform_type_idx (platform_type),
    INDEX social_order_idx (order_index),
    UNIQUE KEY api_social_organization_platform_name_uniq (organization_id, platform_name),
    FOREIGN KEY (organization_id) REFERENCES api_organization(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 19. ALTER TABLE COMMANDS FOR EXISTING TABLES
-- ============================================

-- Add new fields to existing api_customersegment table
ALTER TABLE api_customersegment 
ADD COLUMN is_active TINYINT(1) DEFAULT 1,
ADD COLUMN priority INT DEFAULT 0;

-- Add indexes for new fields
CREATE INDEX api_customersegment_is_active_idx ON api_customersegment(is_active);
CREATE INDEX api_customersegment_priority_idx ON api_customersegment(priority);

-- ============================================
-- 20. VERIFICATION QUERIES
-- ============================================

-- Check all tables created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'vinylart' ORDER BY table_name;

-- Show table counts
-- SELECT 
--     table_name,
--     table_rows
-- FROM information_schema.tables 
-- WHERE table_schema = 'vinylart' 
-- ORDER BY table_name;

