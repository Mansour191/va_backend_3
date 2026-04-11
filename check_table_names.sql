-- =====================================================
-- Check existing tables in vynilart_2_0 database
-- Execute this in phpMyAdmin to see all table names
-- =====================================================

-- Show all tables in the database
SHOW TABLES;

-- Check if organization table exists (it should be api_organization)
SHOW TABLES LIKE '%organization%';

-- Check if shipping table exists (it should be core_shipping)
SHOW TABLES LIKE '%shipping%';

-- Show structure of api_organization if it exists
DESCRIBE `api_organization`;

-- Show structure of core_shipping if it exists  
DESCRIBE `core_shipping`;
