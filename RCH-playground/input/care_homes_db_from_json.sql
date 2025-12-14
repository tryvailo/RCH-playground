
-- Создание таблицы care_homes
CREATE TABLE IF NOT EXISTS care_homes (
    id SERIAL PRIMARY KEY,
    cqc_location_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    city VARCHAR(200),
    postcode VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    region VARCHAR(100),
    local_authority VARCHAR(200),
    telephone VARCHAR(50),
    website VARCHAR(500),
    beds_total INTEGER,
    beds_available INTEGER,
    has_availability BOOLEAN DEFAULT FALSE,
    availability_status VARCHAR(50),
    care_residential BOOLEAN DEFAULT FALSE,
    care_nursing BOOLEAN DEFAULT FALSE,
    care_dementia BOOLEAN DEFAULT FALSE,
    care_respite BOOLEAN DEFAULT FALSE,
    fee_residential_from DECIMAL(10, 2),
    fee_nursing_from DECIMAL(10, 2),
    fee_dementia_from DECIMAL(10, 2),
    fee_respite_from DECIMAL(10, 2),
    cqc_rating_overall VARCHAR(50),
    cqc_rating_safe VARCHAR(50),
    cqc_rating_effective VARCHAR(50),
    cqc_rating_caring VARCHAR(50),
    cqc_rating_responsive VARCHAR(50),
    cqc_rating_well_led VARCHAR(50),
    cqc_last_inspection_date DATE,
    google_rating DECIMAL(2, 1),
    review_count INTEGER,
    wheelchair_access BOOLEAN DEFAULT FALSE,
    ensuite_rooms BOOLEAN DEFAULT FALSE,
    secure_garden BOOLEAN DEFAULT FALSE,
    wifi_available BOOLEAN DEFAULT FALSE,
    parking_onsite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_care_homes_postcode ON care_homes(postcode);
CREATE INDEX IF NOT EXISTS idx_care_homes_local_authority ON care_homes(local_authority);
CREATE INDEX IF NOT EXISTS idx_care_homes_cqc_rating ON care_homes(cqc_rating_overall);
CREATE INDEX IF NOT EXISTS idx_care_homes_beds_available ON care_homes(beds_available) WHERE beds_available > 0;


-- Вставка тестовых данных

INSERT INTO care_homes (

    cqc_location_id, name, city, postcode, latitude, longitude,

    region, local_authority, telephone, website,

    beds_total, beds_available, has_availability, availability_status,

    care_residential, care_nursing, care_dementia, care_respite,

    fee_residential_from, fee_nursing_from, fee_dementia_from, fee_respite_from,

    cqc_rating_overall, cqc_rating_safe, cqc_rating_effective, cqc_rating_caring,

    cqc_rating_responsive, cqc_rating_well_led, cqc_last_inspection_date,

    google_rating, review_count,

    wheelchair_access, ensuite_rooms, secure_garden, wifi_available, parking_onsite

) VALUES

('1-10016894058', 'Respite Breaks - Epwell rd.', 'Birmingham', 'B44 8DD', 52.533398, NULL, 'West Midlands', 'Birmingham', '1212740588', NULL, 2, 1, TRUE, 'Available', TRUE, FALSE, FALSE, FALSE, 948, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2022-04-26', 3.7, 46, FALSE, TRUE, FALSE, FALSE, TRUE),
('1-1004508435', 'Meadow Rose Nursing Home', 'Birmingham', 'B31 2TX', 52.399843, -1.989241, 'West Midlands', 'Birmingham', '1214769808', 'www.macccare.com', 56, 1, TRUE, 'Available', FALSE, TRUE, TRUE, FALSE, NULL, 1187, 1051, NULL, 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2020-10-01', 4.3, 122, FALSE, FALSE, TRUE, FALSE, FALSE),
('1-10646798947', 'Petersfield Care Home', 'Birmingham', 'B20 3RP', 52.508024, -1.912955, 'West Midlands', 'Birmingham', '1215151654', NULL, 5, 0, FALSE, 'Full', TRUE, FALSE, FALSE, FALSE, 1178, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2023-01-20', 4.1, 76, TRUE, FALSE, TRUE, FALSE, FALSE),
('1-109100588', 'Beech Hill Grange', 'Sutton Coldfield', 'B72 1DU', 52.539648, -1.822084, 'West Midlands', 'Birmingham', '1213730200', 'www.beechhillgrange.co.uk', 74, 22, TRUE, 'Waiting list', FALSE, TRUE, TRUE, FALSE, NULL, 1233, 1399, NULL, 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2024-09-13', 4.3, 16, FALSE, FALSE, FALSE, TRUE, TRUE),
('1-109925813', 'Sycamore House', 'Birmingham', 'B11 3RG', 52.452689, -1.848759, 'West Midlands', 'Birmingham', '1217074622', NULL, 28, 3, TRUE, 'Waiting list', TRUE, FALSE, FALSE, FALSE, 887, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-04-05', 4.0, 140, TRUE, TRUE, FALSE, TRUE, TRUE),
('1-110294199', 'Bryony House', 'Birmingham', 'B29 4BX', 52.430879, -1.958186, 'West Midlands', 'Birmingham', '1214752965', NULL, 35, 12, TRUE, 'Waiting list', TRUE, FALSE, FALSE, FALSE, 1076, NULL, NULL, NULL, 'Inadequate', 'Inadequate', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Inadequate', '2025-08-01', 4.1, 103, FALSE, FALSE, FALSE, FALSE, FALSE),
('1-11058464513', 'Sutton Park Grange', 'Sutton Coldfield', 'B72 1LY', 52.551945, -1.827226, 'West Midlands', 'Birmingham', '1212691235', NULL, 64, 22, TRUE, 'Limited availability', TRUE, FALSE, TRUE, FALSE, 1199, NULL, 1022, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2023-08-05', 4.6, 41, TRUE, FALSE, TRUE, TRUE, TRUE),
('1-111397200', 'Orchard House Nursing Home', 'Sutton Coldfield', 'B75 6DS', 52.572186, -1.802137, 'West Midlands', 'Birmingham', '1213780272', 'www.orchardhousenursinghome.co.uk', 31, 2, TRUE, 'Waiting list', FALSE, TRUE, FALSE, FALSE, NULL, 1455, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-05-21', 4.7, 21, TRUE, FALSE, TRUE, TRUE, FALSE),
('1-11242868692', 'Blackmoor', 'Birmingham', 'B33 0PE', 52.477568, -1.767402, 'West Midlands', 'Birmingham', '1218243200', 'www.exemplarhc.com', 30, 9, TRUE, 'Available', FALSE, TRUE, TRUE, FALSE, NULL, 893, 1127, NULL, 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', 'Requires Improvement', '2023-01-12', 4.3, 66, FALSE, FALSE, TRUE, FALSE, FALSE),
('1-112440307', 'Arden Lodge Residential Care Home for Elder Adults', 'Birmingham', 'B27 6QG', 52.450593, -1.830015, 'West Midlands', 'Birmingham', '1217067958', 'www.lindale-homes.co.uk', 47, 10, TRUE, 'Waiting list', TRUE, FALSE, TRUE, FALSE, 856, NULL, 1356, NULL, 'Good', 'Good', 'Good', 'Good', 'Outstanding', 'Good', '2019-04-18', 3.8, 77, TRUE, TRUE, TRUE, TRUE, FALSE),
('1-112476088', 'Chesterberry', 'Birmingham', 'B24 0EA', 52.531978, -1.826862, 'West Midlands', 'Birmingham', '1213862290', 'www.bid.org.uk', 7, 2, TRUE, 'Limited availability', TRUE, FALSE, FALSE, FALSE, 788, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-02-01', 4.1, 119, FALSE, FALSE, FALSE, FALSE, TRUE),
('1-112566759', 'Berwood Court Care Home', 'Birmingham', 'B35 7EW', 52.514099, -1.789386, 'West Midlands', 'Birmingham', '1217497887', 'www.dukerieshealthcare.co.uk', 74, 29, TRUE, 'Limited availability', TRUE, TRUE, TRUE, FALSE, 671, 1436, 1375, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2021-10-20', 3.7, 26, FALSE, TRUE, TRUE, TRUE, FALSE),
('1-112566829', 'The Ridings Care Home', 'Birmingham', 'B35 7NR', 52.520246, -1.778318, 'West Midlands', 'Birmingham', '1217488770', 'www.dukerieshealthcare.co.uk', 83, 27, TRUE, 'Available', TRUE, TRUE, TRUE, FALSE, 1155, 957, 1052, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2025-08-14', 3.8, 129, FALSE, TRUE, TRUE, FALSE, TRUE),
('1-112835025', 'Roxton Nursing Home', 'Sutton Coldfield', 'B72 1LY', 52.551945, -1.827226, 'West Midlands', 'Birmingham', '1213542621', 'www.roxton.biz', 45, 12, TRUE, 'Limited availability', FALSE, TRUE, TRUE, FALSE, NULL, 1298, 1105, NULL, 'Good', 'Good', 'Good', 'Requires Improvement', 'Requires Improvement', 'Good', '2019-04-17', 3.6, 88, TRUE, FALSE, FALSE, FALSE, FALSE),
('1-1128510414', 'Hampton Road', 'Birmingham', 'B23 7JJ', 52.52257, -1.860349, 'West Midlands', 'Birmingham', '1212265800', 'www.reachthecharity.org.uk', 4, 2, TRUE, 'Available', TRUE, FALSE, FALSE, FALSE, 656, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2018-12-25', 4.0, 121, FALSE, FALSE, TRUE, FALSE, FALSE),
('1-112953271', 'Tulip Gardens', 'Birmingham', 'B29 5BW', 52.429822, -1.973777, 'West Midlands', 'Birmingham', '1214783505', 'www.newoutlookha.org', 8, 1, TRUE, 'Available', TRUE, FALSE, FALSE, FALSE, 815, NULL, NULL, NULL, 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Good', 'Requires Improvement', '2022-11-18', 4.3, 112, TRUE, FALSE, FALSE, FALSE, FALSE),
('1-112953306', 'Silver Birch', 'Birmingham', 'B24 0AR', 52.531207, -1.828988, 'West Midlands', 'Birmingham', '1212502067', 'www.newoutlookha.org', 7, 3, TRUE, 'Waiting list', TRUE, FALSE, FALSE, FALSE, 715, NULL, NULL, NULL, 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Good', 'Requires Improvement', '2022-03-03', 4.3, 114, TRUE, TRUE, FALSE, FALSE, TRUE),
('1-112963886', 'Oakwood Care Home', 'Birmingham', 'B24 8QJ', 52.514781, -1.847206, 'West Midlands', 'Birmingham', '1213738476', 'www.oakwoodresthome.co.uk', 37, 10, TRUE, 'Limited availability', TRUE, FALSE, TRUE, FALSE, 1147, NULL, 995, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2023-03-28', 4.2, 27, TRUE, FALSE, TRUE, FALSE, FALSE),
('1-113524621', 'Keo Lodge', 'Birmingham', 'B13 8DS', 52.452609, -1.894665, 'West Midlands', 'Birmingham', '1214495589', NULL, 11, 1, TRUE, 'Waiting list', TRUE, FALSE, FALSE, FALSE, 1185, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2020-01-01', 3.6, 28, TRUE, FALSE, TRUE, TRUE, TRUE),
('1-113533340', 'Coney Green Residential Home', 'Birmingham', 'B31 4DT', 52.401225, -1.973632, 'West Midlands', 'Birmingham', '1214781076', NULL, 9, 4, TRUE, 'Available', TRUE, FALSE, FALSE, FALSE, 924, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2021-08-26', 3.8, 107, FALSE, TRUE, FALSE, TRUE, FALSE),
('1-114103397', 'Stratford Court', 'Birmingham', 'B28 0EU', 52.427771, NULL, 'West Midlands', 'Birmingham', '1217783366', NULL, 30, 14, TRUE, 'Available', TRUE, FALSE, FALSE, FALSE, 1102, NULL, NULL, NULL, 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2022-12-23', 4.5, 116, FALSE, TRUE, TRUE, TRUE, FALSE),
('1-114155375', 'Homecroft Residential Home', 'Sutton Coldfield', 'B74 4BL', 52.591815, -1.834037, 'West Midlands', 'Birmingham', '1213086367', 'www.homecroft-ltd.co.uk', 23, 6, TRUE, 'Limited availability', TRUE, FALSE, TRUE, FALSE, 637, NULL, 1354, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2022-01-21', 3.6, 33, TRUE, TRUE, TRUE, FALSE, TRUE),
('1-114155392', 'Wyndley Grange Nursing Home', 'Sutton Coldfield', 'B73 6JA', 52.558453, -1.833484, 'West Midlands', 'Birmingham', '1213541619', 'www.homecroft-ltd.co.uk', 64, 2, TRUE, 'Waiting list', FALSE, TRUE, TRUE, FALSE, NULL, 1219, 1077, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2018-01-12', 4.0, 139, TRUE, TRUE, TRUE, TRUE, TRUE),
('1-114314574', 'Care Home for Special Needs', 'Birmingham', 'B16 0LR', 52.481361, -1.945328, 'West Midlands', 'Birmingham', '1214558269', NULL, 4, 1, TRUE, 'Available', TRUE, FALSE, TRUE, FALSE, 1086, NULL, 1292, NULL, 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Good', 'Requires Improvement', '2025-06-17', 4.0, 103, FALSE, TRUE, FALSE, FALSE, FALSE),
('1-114658627', 'Barkat House Residential Home', 'Birmingham', 'B13 8EY', 52.444904, -1.889672, 'West Midlands', 'Birmingham', '1214490584', NULL, 27, 8, TRUE, 'Available', TRUE, FALSE, TRUE, FALSE, 876, NULL, 1180, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2021-07-30', 4.6, 18, FALSE, FALSE, TRUE, FALSE, FALSE),
('1-115853341', 'Cotteridge House', 'Birmingham', 'B30 1AB', 52.41482, -1.934148, 'West Midlands', 'Birmingham', '1216240506', NULL, 11, 1, TRUE, 'Limited availability', TRUE, FALSE, FALSE, FALSE, 949, NULL, NULL, NULL, 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Good', 'Good', 'Requires Improvement', '2023-01-18', 4.1, 109, FALSE, TRUE, TRUE, TRUE, FALSE),
('1-11597234926', 'Selly Wood House Nursing Home', 'Birmingham', 'B30 1TJ', 52.431546, -1.942566, 'West Midlands', 'Birmingham', '1214723721', 'www.avatarcaregroup.co.uk', 48, 5, TRUE, 'Waiting list', FALSE, TRUE, TRUE, FALSE, NULL, 1281, 1312, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-11-28', 3.7, 128, TRUE, TRUE, FALSE, TRUE, FALSE),
('1-11600679815', 'Highbury Nursing Home', 'Birmingham', 'B13 8PX', 52.443172, NULL, 'West Midlands', 'Birmingham', '1214424885', 'www.highburynursinghome.co.uk', 38, 5, TRUE, 'Waiting list', FALSE, TRUE, TRUE, FALSE, NULL, 1432, 1310, NULL, 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', 'Requires Improvement', '2023-06-20', 3.6, 124, TRUE, FALSE, TRUE, FALSE, TRUE),
('1-116439860', 'Queen Alexandra College', 'Birmingham', 'B17 9TG', 52.460242, -1.965458, 'West Midlands', 'Birmingham', '1214285025', 'www.qac.ac.uk', 51, 13, TRUE, 'Waiting list', TRUE, FALSE, FALSE, FALSE, 895, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', '2019-05-23', 4.6, 50, FALSE, FALSE, TRUE, TRUE, TRUE),
('1-116640703', 'Bournville Grange Limited', 'Birmingham', 'B30 1TX', 52.430592, -1.939993, 'West Midlands', 'Birmingham', '1214722213', NULL, 28, 7, TRUE, 'Waiting list', TRUE, FALSE, FALSE, FALSE, 1048, NULL, NULL, NULL, 'Good', 'Good', 'Good', 'Good', 'Good', 'Requires Improvement', '2019-04-03', 4.6, 89, TRUE, FALSE, TRUE, TRUE, FALSE)
;


-- Статистика
SELECT 
    COUNT(*) as total_homes,
    COUNT(*) FILTER (WHERE has_availability = TRUE) as homes_with_availability,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Outstanding') as outstanding_homes,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Good') as good_homes,
    AVG(google_rating) as avg_google_rating
FROM care_homes;
