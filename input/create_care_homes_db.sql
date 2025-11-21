-- =====================================================
-- Тестовая база данных для домов престарелых
-- Создаёт таблицу и заполняет 30 тестовыми записями
-- =====================================================

-- Создание таблицы care_homes
CREATE TABLE IF NOT EXISTS care_homes (
    -- Identifiers
    id SERIAL PRIMARY KEY,
    cqc_location_id VARCHAR(50) UNIQUE NOT NULL,
    location_ods_code VARCHAR(20),
    
    -- Basic Info
    name VARCHAR(500) NOT NULL,
    name_normalized VARCHAR(500),
    provider_name VARCHAR(500),
    provider_id VARCHAR(50),
    brand_name VARCHAR(200),
    
    -- Address
    city VARCHAR(200),
    county VARCHAR(200),
    postcode VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    
    -- Geographic
    region VARCHAR(100),
    local_authority VARCHAR(200),
    
    -- Contact
    telephone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(500),
    
    -- Operational
    beds_total INTEGER,
    beds_available INTEGER,
    has_availability BOOLEAN DEFAULT FALSE,
    availability_status VARCHAR(50),
    availability_last_checked DATE,
    
    -- Care Types (as JSONB for flexibility)
    care_residential BOOLEAN DEFAULT FALSE,
    care_nursing BOOLEAN DEFAULT FALSE,
    care_dementia BOOLEAN DEFAULT FALSE,
    care_respite BOOLEAN DEFAULT FALSE,
    
    -- Pricing (weekly GBP)
    fee_residential_from DECIMAL(10, 2),
    fee_nursing_from DECIMAL(10, 2),
    fee_dementia_from DECIMAL(10, 2),
    fee_respite_from DECIMAL(10, 2),
    
    -- CQC Ratings
    cqc_rating_overall VARCHAR(50),
    cqc_rating_safe VARCHAR(50),
    cqc_rating_effective VARCHAR(50),
    cqc_rating_caring VARCHAR(50),
    cqc_rating_responsive VARCHAR(50),
    cqc_rating_well_led VARCHAR(50),
    cqc_last_inspection_date DATE,
    
    -- Google Places Data
    google_rating DECIMAL(2, 1),
    review_count INTEGER,
    review_average_score DECIMAL(3, 1),
    
    -- Facilities
    wheelchair_access BOOLEAN DEFAULT FALSE,
    ensuite_rooms BOOLEAN DEFAULT FALSE,
    secure_garden BOOLEAN DEFAULT FALSE,
    wifi_available BOOLEAN DEFAULT FALSE,
    parking_onsite BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped_at TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_care_homes_postcode ON care_homes(postcode);
CREATE INDEX IF NOT EXISTS idx_care_homes_city ON care_homes(city);
CREATE INDEX IF NOT EXISTS idx_care_homes_local_authority ON care_homes(local_authority);
CREATE INDEX IF NOT EXISTS idx_care_homes_region ON care_homes(region);
CREATE INDEX IF NOT EXISTS idx_care_homes_cqc_rating ON care_homes(cqc_rating_overall);
CREATE INDEX IF NOT EXISTS idx_care_homes_location ON care_homes(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_care_homes_beds_available ON care_homes(beds_available) WHERE beds_available > 0;
CREATE INDEX IF NOT EXISTS idx_care_homes_has_availability ON care_homes(has_availability) WHERE has_availability = TRUE;

-- GIST индекс для географических запросов (если PostGIS установлен)
-- CREATE INDEX IF NOT EXISTS idx_care_homes_geography ON care_homes USING GIST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));

-- =====================================================
-- Вставка тестовых данных (30 домов)
-- =====================================================

INSERT INTO care_homes (
    cqc_location_id, location_ods_code, name, name_normalized, city, postcode,
    latitude, longitude, region, local_authority,
    telephone, website,
    beds_total, beds_available, has_availability, availability_status,
    care_residential, care_nursing, care_dementia, care_respite,
    fee_residential_from, fee_nursing_from, fee_dementia_from, fee_respite_from,
    cqc_rating_overall, cqc_rating_safe, cqc_rating_effective, cqc_rating_caring,
    cqc_rating_responsive, cqc_rating_well_led, cqc_last_inspection_date,
    google_rating, review_count, review_average_score,
    wheelchair_access, ensuite_rooms, secure_garden, wifi_available, parking_onsite
) VALUES
-- Home 1
('1-10016894058', 'VNH55', 'Respite Breaks - Epwell rd.', 'respite breaks - epwell rd.', 'Birmingham', 'B44 8DD', 
 52.533398, NULL, 'West Midlands', 'Birmingham',
 '1212740588', NULL,
 2, 1, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 948, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2022-04-26',
 3.7, 46, 3.7,
 FALSE, TRUE, FALSE, FALSE, TRUE),

-- Home 2
('1-1004508435', 'VM4G9', 'Meadow Rose Nursing Home', 'meadow rose', 'Birmingham', 'B31 2TX',
 52.399843, -1.989241, 'West Midlands', 'Birmingham',
 '1214769808', 'www.macccare.com',
 56, 1, TRUE, 'Available',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1187, 1051, NULL,
 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2020-10-01',
 4.3, 122, 4.3,
 FALSE, FALSE, TRUE, FALSE, FALSE),

-- Home 3
('1-10646798947', 'VNJCX', 'Petersfield Care Home', 'petersfield', 'Birmingham', 'B20 3RP',
 52.508024, -1.912955, 'West Midlands', 'Birmingham',
 '1215151654', NULL,
 5, 0, FALSE, 'Full',
 TRUE, FALSE, FALSE, FALSE,
 1178, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2023-01-20',
 4.1, 76, 4.1,
 TRUE, FALSE, TRUE, FALSE, FALSE),

-- Home 4
('1-109100588', 'VLM9A', 'Beech Hill Grange', 'beech hill grange', 'Sutton Coldfield', 'B72 1DU',
 52.539648, -1.822084, 'West Midlands', 'Birmingham',
 '1213730200', 'www.beechhillgrange.co.uk',
 74, 22, TRUE, 'Waiting list',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1233, 1399, NULL,
 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2024-09-13',
 4.3, 16, 4.3,
 FALSE, FALSE, FALSE, TRUE, TRUE),

-- Home 5
('1-109925813', 'VL951', 'Sycamore House', 'sycamore house', 'Birmingham', 'B11 3RG',
 52.452689, -1.848759, 'West Midlands', 'Birmingham',
 '1217074622', NULL,
 28, 5, TRUE, 'Limited availability',
 TRUE, FALSE, FALSE, FALSE,
 1120, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-04-05',
 4.5, 89, 4.5,
 TRUE, TRUE, FALSE, TRUE, FALSE),

-- Home 6
('1-110294199', 'VLM9E', 'Bryony House', 'bryony house', 'Birmingham', 'B29 4BX',
 52.430879, -1.958186, 'West Midlands', 'Birmingham',
 '1214752965', NULL,
 35, 0, FALSE, 'Full',
 TRUE, FALSE, FALSE, FALSE,
 980, NULL, NULL, NULL,
 'Inadequate', 'Inadequate', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Inadequate', '2025-08-01',
 2.8, 12, 2.8,
 FALSE, FALSE, FALSE, FALSE, FALSE),

-- Home 7
('1-11058464513', 'VNJN6', 'Sutton Park Grange', 'sutton park grange', 'Sutton Coldfield', 'B72 1LY',
 52.551945, -1.827226, 'West Midlands', 'Birmingham',
 '1212691235', NULL,
 64, 8, TRUE, 'Available',
 TRUE, FALSE, TRUE, FALSE,
 1250, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2023-08-05',
 4.6, 145, 4.6,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 8
('1-111397200', 'VLMAN', 'Orchard House Nursing Home', 'orchard house', 'Sutton Coldfield', 'B75 6DS',
 52.572186, -1.802137, 'West Midlands', 'Birmingham',
 '1213780272', 'www.orchardhousenursinghome.co.uk',
 31, 2, TRUE, 'Limited availability',
 FALSE, TRUE, FALSE, FALSE,
 NULL, 1100, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-05-21',
 4.2, 67, 4.2,
 TRUE, FALSE, TRUE, TRUE, TRUE),

-- Home 9
('1-11242868692', 'VNJWW', 'Blackmoor', 'blackmoor', 'Birmingham', 'B33 0PE',
 52.477568, -1.767402, 'West Midlands', 'Birmingham',
 '1218243200', 'www.exemplarhc.com',
 30, 3, TRUE, 'Available',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1150, 1200, NULL,
 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', 'Requires Improvement', '2023-01-12',
 3.9, 34, 3.9,
 TRUE, TRUE, FALSE, TRUE, FALSE),

-- Home 10
('1-112440307', 'VLRVG', 'Arden Lodge Residential Care Home for Elder Adults', 'arden lodge residential care home for elder adults', 'Birmingham', 'B27 6QG',
 52.450593, -1.830015, 'West Midlands', 'Birmingham',
 '1217067958', 'www.lindale-homes.co.uk',
 47, 6, TRUE, 'Available',
 TRUE, FALSE, TRUE, FALSE,
 1080, NULL, 1180, NULL,
 'Good', 'Good', 'Good', 'Good', 'Outstanding', 'Good', '2019-04-18',
 4.4, 98, 4.4,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 11
('1-112476088', 'VL8X4', 'Chesterberry', 'chesterberry', 'Birmingham', 'B24 0EA',
 52.531978, -1.826862, 'West Midlands', 'Birmingham',
 '1213862290', 'www.bid.org.uk',
 7, 1, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 950, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-02-01',
 4.0, 23, 4.0,
 TRUE, FALSE, FALSE, TRUE, FALSE),

-- Home 12
('1-112566759', 'VLM9C', 'Berwood Court Care Home', 'berwood court', 'Birmingham', 'B35 7EW',
 52.514099, -1.789386, 'West Midlands', 'Birmingham',
 '1217497887', 'www.dukerieshealthcare.co.uk',
 74, 12, TRUE, 'Available',
 TRUE, TRUE, TRUE, FALSE,
 1020, 1280, 1350, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2021-10-20',
 4.5, 156, 4.5,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 13
('1-112566829', 'VLMAW', 'The Ridings Care Home', 'ridings', 'Birmingham', 'B35 7NR',
 52.520246, -1.778318, 'West Midlands', 'Birmingham',
 '1217488770', 'www.dukerieshealthcare.co.uk',
 83, 15, TRUE, 'Available',
 TRUE, TRUE, TRUE, FALSE,
 1050, 1300, 1400, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2025-08-14',
 4.7, 178, 4.7,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 14
('1-112835025', 'VLVW8', 'Roxton Nursing Home', 'roxton', 'Sutton Coldfield', 'B72 1LY',
 52.551945, -1.827226, 'West Midlands', 'Birmingham',
 '1213542621', 'www.roxton.biz',
 45, 4, TRUE, 'Limited availability',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1200, 1250, NULL,
 'Good', 'Good', 'Good', 'Requires Improvement', 'Requires Improvement', 'Good', '2019-04-17',
 3.8, 45, 3.8,
 TRUE, FALSE, TRUE, TRUE, TRUE),

-- Home 15
('1-1128510414', 'VM4KC', 'Hampton Road', 'hampton road', 'Birmingham', 'B23 7JJ',
 52.522570, -1.860349, 'West Midlands', 'Birmingham',
 '1212265800', 'www.reachthecharity.org.uk',
 4, 0, FALSE, 'Full',
 TRUE, FALSE, FALSE, FALSE,
 920, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2018-12-25',
 4.1, 18, 4.1,
 FALSE, FALSE, FALSE, TRUE, FALSE),

-- Home 16
('1-112953271', 'VL91X', 'Tulip Gardens', 'tulip gardens', 'Birmingham', 'B29 5BW',
 52.429822, -1.973777, 'West Midlands', 'Birmingham',
 '1214783505', 'www.newoutlookha.org',
 8, 2, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 1000, NULL, NULL, NULL,
 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Good', 'Requires Improvement', '2022-11-18',
 3.6, 29, 3.6,
 TRUE, TRUE, FALSE, TRUE, FALSE),

-- Home 17
('1-112953306', 'VL94H', 'Silver Birch', 'silver birch', 'Birmingham', 'B24 0AR',
 52.531207, -1.828988, 'West Midlands', 'Birmingham',
 '1212502067', 'www.newoutlookha.org',
 7, 1, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 980, NULL, NULL, NULL,
 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Good', 'Requires Improvement', '2022-03-03',
 3.7, 31, 3.7,
 TRUE, FALSE, TRUE, TRUE, FALSE),

-- Home 18
('1-112963886', 'VL8XP', 'Oakwood Care Home', 'oakwood', 'Birmingham', 'B24 8QJ',
 52.514781, -1.847206, 'West Midlands', 'Birmingham',
 '1213738476', 'www.oakwoodresthome.co.uk',
 37, 5, TRUE, 'Available',
 TRUE, FALSE, TRUE, FALSE,
 1040, NULL, 1140, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2023-03-28',
 4.2, 72, 4.2,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 19
('1-113524621', 'VL90Q', 'Keo Lodge', 'keo lodge', 'Birmingham', 'B13 8DS',
 52.452609, -1.894665, 'West Midlands', 'Birmingham',
 '1214495589', NULL,
 11, 2, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 960, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2020-01-01',
 3.9, 41, 3.9,
 FALSE, TRUE, FALSE, TRUE, FALSE),

-- Home 20
('1-113533340', 'VLR69', 'Coney Green Residential Home', 'coney green', 'Birmingham', 'B31 4DT',
 52.401225, -1.973632, 'West Midlands', 'Birmingham',
 '1214781076', NULL,
 9, 1, TRUE, 'Limited availability',
 TRUE, FALSE, FALSE, FALSE,
 940, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2021-08-26',
 4.0, 38, 4.0,
 TRUE, FALSE, TRUE, FALSE, TRUE),

-- Home 21
('1-114103397', 'VL94W', 'Stratford Court', 'stratford court', 'Birmingham', 'B28 0EU',
 52.427771, NULL, 'West Midlands', 'Birmingham',
 '1217783366', NULL,
 30, 3, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 990, NULL, NULL, NULL,
 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2022-12-23',
 3.5, 52, 3.5,
 TRUE, TRUE, FALSE, TRUE, FALSE),

-- Home 22
('1-114155375', 'VL90D', 'Homecroft Residential Home', 'homecroft', 'Sutton Coldfield', 'B74 4BL',
 52.591815, -1.834037, 'West Midlands', 'Birmingham',
 '1213086367', 'www.homecroft-ltd.co.uk',
 23, 4, TRUE, 'Available',
 TRUE, FALSE, TRUE, FALSE,
 1120, NULL, 1220, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2022-01-21',
 4.3, 64, 4.3,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 23
('1-114155392', 'VLVD6', 'Wyndley Grange Nursing Home', 'wyndley grange', 'Sutton Coldfield', 'B73 6JA',
 52.558453, -1.833484, 'West Midlands', 'Birmingham',
 '1213541619', 'www.homecroft-ltd.co.uk',
 64, 10, TRUE, 'Available',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1250, 1350, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2018-01-12',
 4.4, 112, 4.4,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 24
('1-114314574', 'VL93X', 'Care Home for Special Needs', 'care home for special needs', 'Birmingham', 'B16 0LR',
 52.481361, -1.945328, 'West Midlands', 'Birmingham',
 '1214558269', NULL,
 4, 1, TRUE, 'Available',
 TRUE, FALSE, TRUE, FALSE,
 1100, NULL, 1200, NULL,
 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Good', 'Requires Improvement', '2025-06-17',
 3.8, 19, 3.8,
 TRUE, FALSE, TRUE, FALSE, FALSE),

-- Home 25
('1-114658627', 'VL8WD', 'Barkat House Residential Home', 'barkat house', 'Birmingham', 'B13 8EY',
 52.444904, -1.889672, 'West Midlands', 'Birmingham',
 '1214490584', NULL,
 27, 3, TRUE, 'Available',
 TRUE, FALSE, TRUE, FALSE,
 1060, NULL, 1160, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2021-07-30',
 4.1, 55, 4.1,
 TRUE, TRUE, FALSE, TRUE, TRUE),

-- Home 26
('1-115853341', 'VL90H', 'Cotteridge House', 'cotteridge house', 'Birmingham', 'B30 1AB',
 52.414820, -1.934148, 'West Midlands', 'Birmingham',
 '1216240506', NULL,
 11, 2, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 970, NULL, NULL, NULL,
 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2023-01-18',
 3.6, 27, 3.6,
 TRUE, FALSE, TRUE, TRUE, FALSE),

-- Home 27
('1-11597234926', 'VNKN1', 'Selly Wood House Nursing Home', 'selly wood house', 'Birmingham', 'B30 1TJ',
 52.431546, -1.942566, 'West Midlands', 'Birmingham',
 '1214723721', 'www.avatarcaregroup.co.uk',
 48, 7, TRUE, 'Available',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1220, 1320, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-11-28',
 4.5, 134, 4.5,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 28
('1-11600679815', 'VNKYV', 'Highbury Nursing Home', 'highbury', 'Birmingham', 'B13 8PX',
 52.443172, NULL, 'West Midlands', 'Birmingham',
 '1214424885', 'www.highburynursinghome.co.uk',
 38, 4, TRUE, 'Limited availability',
 FALSE, TRUE, TRUE, FALSE,
 NULL, 1180, 1280, NULL,
 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', '2023-06-20',
 3.4, 43, 3.4,
 TRUE, TRUE, FALSE, TRUE, TRUE),

-- Home 29
('1-116439860', 'VL92H', 'Queen Alexandra College', 'queen alexandra college', 'Birmingham', 'B17 9TG',
 52.460242, -1.965458, 'West Midlands', 'Birmingham',
 '1214285025', 'www.qac.ac.uk',
 51, 8, TRUE, 'Available',
 TRUE, FALSE, FALSE, FALSE,
 1030, NULL, NULL, NULL,
 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-05-23',
 4.2, 87, 4.2,
 TRUE, TRUE, TRUE, TRUE, TRUE),

-- Home 30
('1-116500000', 'VLTEST', 'Test Care Home Outstanding', 'test care home outstanding', 'Birmingham', 'B1 1AA',
 52.4862, -1.8904, 'West Midlands', 'Birmingham',
 '1210000000', 'www.testcarehome.co.uk',
 50, 10, TRUE, 'Available',
 TRUE, TRUE, TRUE, TRUE,
 1200, 1400, 1300, 1100,
 'Outstanding', 'Outstanding', 'Outstanding', 'Outstanding', 'Outstanding', 'Outstanding', '2024-01-15',
 4.8, 200, 4.8,
 TRUE, TRUE, TRUE, TRUE, TRUE);

-- Обновление updated_at для всех записей
UPDATE care_homes SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL;

-- Статистика
SELECT 
    COUNT(*) as total_homes,
    COUNT(*) FILTER (WHERE has_availability = TRUE) as homes_with_availability,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Outstanding') as outstanding_homes,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Good') as good_homes,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Requires Improvement') as requires_improvement_homes,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Inadequate') as inadequate_homes,
    AVG(google_rating) as avg_google_rating,
    SUM(beds_available) as total_beds_available
FROM care_homes;

-- Вывод сообщения об успешном создании
DO $$
BEGIN
    RAISE NOTICE '✅ База данных успешно создана!';
    RAISE NOTICE '📊 Загружено 30 домов престарелых';
    RAISE NOTICE '📍 Регион: West Midlands (Birmingham)';
    RAISE NOTICE '💾 Используйте SELECT * FROM care_homes; для просмотра данных';
END $$;

