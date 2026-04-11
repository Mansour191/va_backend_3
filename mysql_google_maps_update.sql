-- =====================================================
-- Google Maps Integration Update for VinylArt Database
-- =====================================================

-- 1. Add Google Maps fields to api_organization table
ALTER TABLE api_organization 
ADD COLUMN latitude DECIMAL(22, 16) NULL COMMENT 'خط العرض من جوجل مابس',
ADD COLUMN longitude DECIMAL(22, 16) NULL COMMENT 'خط الطول من جوجل مابس',
ADD COLUMN google_place_id VARCHAR(255) NULL COMMENT 'معرف المكان من جوجل',
ADD COLUMN maps_url VARCHAR(500) NULL COMMENT 'رابط خرائط جوجل المباشر';

-- 2. Add Google Maps fields to core_shipping table
ALTER TABLE core_shipping 
ADD COLUMN pickup_latitude DECIMAL(22, 16) NULL COMMENT 'خط عرض نقطة الاستلام',
ADD COLUMN pickup_longitude DECIMAL(22, 16) NULL COMMENT 'خط طول نقطة الاستلام',
ADD COLUMN radius_km INT NULL COMMENT 'نطاق التوصيل بالكيلومتر',
ADD COLUMN maps_url VARCHAR(500) NULL COMMENT 'رابط خرائط جوجل لنقطة الاستلام';

-- 3. Update foreign key relationship if needed
-- Check if base_city column exists and update reference
ALTER TABLE api_organization 
ADD CONSTRAINT fk_org_base_city 
FOREIGN KEY (base_city_id) REFERENCES core_shipping(id) 
ON DELETE SET NULL;

-- 4. Add indexes for better performance
CREATE INDEX idx_org_latitude ON api_organization(latitude);
CREATE INDEX idx_org_longitude ON api_organization(longitude);
CREATE INDEX idx_org_google_place_id ON api_organization(google_place_id);

CREATE INDEX idx_shipping_pickup_lat ON core_shipping(pickup_latitude);
CREATE INDEX idx_shipping_pickup_lng ON core_shipping(pickup_longitude);
CREATE INDEX idx_shipping_radius_km ON core_shipping(radius_km);

-- 5. Verification queries
SELECT 'Google Maps fields added to api_organization' as status;
DESCRIBE api_organization;

SELECT 'Google Maps fields added to core_shipping' as status;
DESCRIBE core_shipping;

-- 6. Sample update for existing organization (optional)
-- UPDATE api_organization 
-- SET latitude = 36.7538, longitude = 3.0588, 
--     google_place_id = 'ChIJR2G7B8N9RxR1qL3Q7n8Q9Q',
--     maps_url = 'https://maps.google.com/?q=36.7538,3.0588'
-- WHERE id = 1;

-- 7. Sample update for existing shipping data (optional)
-- UPDATE core_shipping 
-- SET pickup_latitude = 36.7538, pickup_longitude = 3.0588, 
--     radius_km = 50, maps_url = 'https://maps.google.com/?q=36.7538,3.0588'
-- WHERE wilaya_id = '16';
