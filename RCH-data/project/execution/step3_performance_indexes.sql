-- ============================================================================
-- Performance Indexes for Professional Report Queries
-- Run after step1_schema_create.sql and step2_run_migration.sql
-- ============================================================================

-- =============================================================================
-- COMPOSITE INDEXES for get_care_homes queries
-- These indexes optimize the most common query patterns in DatabaseService
-- =============================================================================

-- 1. Main query pattern: local_authority + care_type + rating
-- Used by: get_care_homes(local_authority=X, care_type='residential')
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_la_residential 
ON care_homes(local_authority, cqc_rating_overall, google_rating) 
WHERE care_residential = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_la_nursing 
ON care_homes(local_authority, cqc_rating_overall, google_rating) 
WHERE care_nursing = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_la_dementia 
ON care_homes(local_authority, cqc_rating_overall, google_rating) 
WHERE care_dementia = TRUE OR care_residential = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_la_respite 
ON care_homes(local_authority, cqc_rating_overall, google_rating) 
WHERE care_respite = TRUE;

-- 2. Geospatial bounding box queries
-- Used by: distance filtering with lat/lon ranges
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_geo_box 
ON care_homes(latitude, longitude) 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- 3. Budget filtering pattern
-- Used by: max_budget filter
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_fees 
ON care_homes(fee_residential_from, fee_nursing_from, fee_dementia_from, fee_respite_from);

-- 4. Combined search pattern: all care types with ratings
-- Used by: sorting by cqc_rating_overall DESC, google_rating DESC
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_rating_sort 
ON care_homes(cqc_rating_overall DESC NULLS LAST, google_rating DESC NULLS LAST);

-- 5. Postcode prefix search
-- Used by: postcode LIKE 'XX%'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_postcode_prefix 
ON care_homes(upper(substring(postcode from 1 for 3)));

-- 6. Full care type composite for complex queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_care_homes_all_care_types 
ON care_homes(care_residential, care_nursing, care_dementia, care_respite, local_authority);

-- =============================================================================
-- ANALYZE to update statistics for query planner
-- =============================================================================
ANALYZE care_homes;

-- =============================================================================
-- Verification query - run to confirm indexes exist
-- =============================================================================
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'care_homes' 
-- AND indexname LIKE 'idx_care_homes_%'
-- ORDER BY indexname;
