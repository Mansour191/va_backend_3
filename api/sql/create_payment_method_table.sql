-- =====================================================
-- Create Payment Method Table
-- =====================================================
-- This SQL creates the api_payment_method table for storing
-- configurable payment methods with multilingual support

-- Create the table
CREATE TABLE IF NOT EXISTS api_payment_method (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Basic Information (Bilingual)
    name_ar VARCHAR(100) NOT NULL COMMENT 'الاسم بالعربية',
    name_en VARCHAR(100) NOT NULL COMMENT 'الاسم بالإنجليزية',
    
    -- Payment Type and Gateway
    payment_type ENUM('cash', 'bank_transfer', 'wallet', 'card', 'other') DEFAULT 'cash' COMMENT 'نوع الدفع',
    gateway_provider VARCHAR(50) NULL COMMENT 'مزود بوابة الدفع',
    
    -- Account Information (Sensitive Data)
    account_name VARCHAR(200) NULL COMMENT 'اسم الحساب',
    account_number VARCHAR(100) NULL COMMENT 'رقم الحساب/الحساب البريدي الجاري',
    iban VARCHAR(34) NULL COMMENT 'IBAN',
    
    -- Instructions (Bilingual)
    instructions_ar TEXT NULL COMMENT 'التعليمات بالعربية',
    instructions_en TEXT NULL COMMENT 'التعليمات بالإنجليزية',
    
    -- Visual Elements
    icon VARCHAR(100) NULL COMMENT 'كود أيقونة Font Awesome',
    logo VARCHAR(255) NULL COMMENT 'مسار الشعار',
    
    -- Display and Control
    order_index INT DEFAULT 0 COMMENT 'ترتيب الظهور',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'نشط',
    is_default BOOLEAN DEFAULT FALSE COMMENT 'افتراضي',
    
    -- Additional Configuration
    max_amount DECIMAL(12,2) NULL COMMENT 'الحد الأقصى للمبلغ',
    fee_percentage DECIMAL(5,2) DEFAULT 0 COMMENT 'نسبة الرسوم',
    fee_fixed DECIMAL(10,2) DEFAULT 0 COMMENT 'رسوم ثابتة',
    
    -- Audit Fields
    created_by INT NULL COMMENT 'المستخدم الذي أنشأ السجل',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'تاريخ الإنشاء',
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'تاريخ التحديث'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='طرق الدفع القابلة للتكوين';

-- =====================================================
-- Create Indexes for Performance
-- =====================================================
CREATE INDEX IF NOT EXISTS payment_method_is_active_idx ON api_payment_method(is_active);
CREATE INDEX IF NOT EXISTS payment_method_type_idx ON api_payment_method(payment_type);
CREATE INDEX IF NOT EXISTS payment_method_order_idx ON api_payment_method(order_index);
CREATE INDEX IF NOT EXISTS payment_method_default_idx ON api_payment_method(is_default);

-- =====================================================
-- Create Constraint for Single Default Method
-- =====================================================
-- Note: MySQL doesn't support CHECK constraints with subqueries
-- This will be handled at application level

-- =====================================================
-- Insert Default Payment Methods
-- =====================================================
INSERT IGNORE INTO api_payment_method (
    name_ar, name_en, payment_type, 
    instructions_ar, instructions_en, 
    icon, order_index, is_active, is_default
) VALUES
(
    'الدفع عند الاستلام', 
    'Cash on Delivery', 
    'cash', 
    'يمكنك الدفع نقداً عند استلام المنتجات من الساعي.', 
    'You can pay cash when courier delivers your products.', 
    'fas fa-hand-holding-usd', 
    1, 
    TRUE, 
    TRUE
),
(
    'تحويل بنكي - CCP', 
    'Bank Transfer - CCP', 
    'bank_transfer',
    'قم بتحويل المبلغ إلى الحساب البريدي الجاري (CCP) المحدد. يرجى إرسال إيصال التحويل عبر الواتساب.',
    'Transfer amount to the specified CCP account. Please send transfer receipt via WhatsApp.',
    'fas fa-university', 
    2, 
    TRUE, 
    FALSE
),
(
    'BaridiMob', 
    'BaridiMob', 
    'wallet',
    'افتح تطبيق BaridiMob وقم بتحويل المبلغ إلى الرقم المحدد.',
    'Open BaridiMob app and transfer amount to the specified number.',
    'fas fa-mobile-alt', 
    3, 
    TRUE, 
    FALSE
);

-- =====================================================
-- Add Foreign Key for created_by (if auth_user table exists)
-- =====================================================
-- ALTER TABLE api_payment_method 
-- ADD CONSTRAINT fk_payment_method_created_by 
-- FOREIGN KEY (created_by) REFERENCES auth_user(id) 
-- ON DELETE SET NULL;

-- =====================================================
-- Success Message
-- =====================================================
SELECT '✅ Table api_payment_method created successfully with default payment methods' AS message;
