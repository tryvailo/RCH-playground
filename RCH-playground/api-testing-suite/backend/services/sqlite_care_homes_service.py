"""
SQLite Care Homes Data Service
Loads care homes data from SQLite database (care_homes.db)

This is the ONLY data source for Free Report matching.
SQLite provides:
- Fast queries
- In-memory caching
- Reliable indexing
- No timeout issues
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Path to SQLite database
_possible_db_paths = [
    Path(__file__).parent.parent / "care_homes.db",  # Direct
    Path(__file__).parent.parent.parent.parent / "care_homes.db",  # RCH-playground root
    Path("/Users/alexander/Documents/Products/RCH-admin-playground/RCH-playground/RCH-playground/api-testing-suite/backend/care_homes.db"),  # Absolute
]

DB_PATH = None
for path in _possible_db_paths:
    if path.exists():
        DB_PATH = path
        logger.info(f"✅ Found SQLite database at: {DB_PATH}")
        break

if not DB_PATH:
    logger.warning(f"⚠️ SQLite database not found. Searched paths: {_possible_db_paths}")


def _get_connection() -> Optional[sqlite3.Connection]:
    """Get SQLite database connection with optimized settings"""
    if not DB_PATH or not DB_PATH.exists():
        logger.error(f"Database file not found: {DB_PATH}")
        return None
    
    try:
        # OPTIMIZATION: Use WAL mode and optimized settings for better performance
        conn = sqlite3.connect(str(DB_PATH), timeout=5.0)  # Reduced timeout to 5s
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        
        # Enable WAL mode for better concurrency (if not already enabled)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except:
            pass  # WAL might not be supported, continue anyway
        
        # Optimize for read performance
        conn.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, still safe
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to SQLite: {e}")
        return None


def get_care_homes(
    local_authority: Optional[str] = None,
    care_type: Optional[str] = None,
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    limit: Optional[int] = 50,
    apply_quality_filter: bool = True  # ✅ REFACTOR: Allow disabling quality filter for professional report
) -> List[Dict[str, Any]]:
    """
    Get care homes from SQLite database
    
    Args:
        local_authority: Filter by local authority
        care_type: Filter by care type (residential, nursing, dementia, respite)
        max_distance_km: Maximum distance in km (requires user_lat, user_lon)
        user_lat: User latitude for distance calculation
        user_lon: User longitude for distance calculation
        limit: Maximum number of results (default 50, None = no limit)
        apply_quality_filter: If True, only return Good/Outstanding CQC ratings (default True)
                             If False, return all homes (for professional report matching)
    
    Returns:
        List of care home dicts
    """
    conn = _get_connection()
    if not conn:
        logger.error("Cannot connect to database")
        return []
    
    try:
        cursor = conn.cursor()
        
        # Build base query - select all available columns from SQLite schema
        query = """
            SELECT 
                id, location_id as cqc_location_id, name, address, postcode, local_authority,
                latitude, longitude,
                rating as cqc_rating_overall,
                cqc_rating_safe, cqc_rating_caring, cqc_rating_effective,
                cqc_rating_responsive, cqc_rating_well_led,
                phone as telephone, website,
                beds,
                care_types,
                data_json
            FROM care_homes
            WHERE 1=1
        """
        
        params = []
        
        # Local authority filter
        if local_authority and local_authority != "Unknown":
            query += " AND LOWER(local_authority) = LOWER(?)"
            params.append(local_authority)
        
        # Care type filter - care_types may be empty in current database
        # TODO: Implement once care_types is populated
        # if care_type:
        #     care_type_lower = care_type.lower()
        #     query += f" AND (care_types LIKE ? OR care_types LIKE ?)"
        #     params.append(f'%{care_type_lower}%')
        #     params.append(f'%"{care_type_lower}"%')  # JSON format
        
        # ✅ REFACTOR: Quality filter is optional - only apply if requested
        # For professional report, we want ALL homes to match against questionnaire
        # Quality filtering happens during matching, not during initial load
        if apply_quality_filter:
            query += " AND (cqc_rating_overall = 'Good' OR cqc_rating_overall = 'Outstanding')"
        
        # ✅ REFACTOR: Handle limit - if None, load all matching homes
        limit_clause = ""
        if limit is not None:
            # For initial load, we might want more results for better matching
            # Use limit * 2 to get more candidates, then filter by distance
            limit_clause = f" LIMIT {limit * 2}"
        else:
            # No limit - load all matching homes (for professional report)
            limit_clause = ""
        
        # Execute query with initial results
        logger.debug(f"Executing query with params: {params}, quality_filter={apply_quality_filter}, limit={limit}")
        cursor.execute(query + f" ORDER BY cqc_rating_overall DESC{limit_clause}", params)
        rows = cursor.fetchall()
        
        logger.info(f"Found {len(rows)} care homes in database")
        
        # Convert rows to dicts and calculate distances if needed
        # OPTIMIZATION: Only calculate distances if we have user coordinates AND need to filter by distance
        # If max_distance_km is None, skip distance calculation to save time
        homes = []
        calculate_distances = user_lat and user_lon and max_distance_km is not None
        
        for row in rows:
            home = dict(row)
            
            # ✅ FIX: Parse data_json to extract services, amenities, and additional_services
            if home.get('data_json'):
                try:
                    import json
                    data_json = json.loads(home['data_json']) if isinstance(home['data_json'], str) else home['data_json']
                    
                    # Extract services/amenities from data_json
                    if isinstance(data_json, dict):
                        # Check for services in various possible locations
                        services = (
                            data_json.get('services') or
                            data_json.get('additional_services') or
                            data_json.get('amenities') or
                            []
                        )
                        if services:
                            home['services'] = services
                            home['additional_services'] = services
                            home['amenities'] = services
                        
                        # Also check facilities JSONB field
                        facilities = data_json.get('facilities')
                        if isinstance(facilities, dict):
                            # Extract amenities from facilities
                            general_amenities = facilities.get('general_amenities', [])
                            if general_amenities:
                                if not home.get('amenities'):
                                    home['amenities'] = general_amenities
                                if not home.get('services'):
                                    home['services'] = general_amenities
                            
                            # Extract additional services from facilities
                            additional_services = facilities.get('additional_services', [])
                            if additional_services:
                                home['additional_services'] = additional_services
                                if not home.get('services'):
                                    home['services'] = additional_services
                        
                        # ✅ DEBUG: Log if services were found (for first few homes only)
                        if home.get('services') or home.get('amenities') or home.get('additional_services'):
                            logger.debug(f"✅ Extracted services for {home.get('name')}: services={len(home.get('services', []))}, amenities={len(home.get('amenities', []))}")
                except Exception as e:
                    logger.debug(f"Failed to parse data_json for {home.get('name')}: {e}")
            
            # ✅ FIX: Ensure CQC ratings are properly set (handle None values)
            if not home.get('cqc_rating_safe') or home.get('cqc_rating_safe') == 'None':
                home['cqc_rating_safe'] = 'Unknown'
            if not home.get('cqc_rating_overall') or home.get('cqc_rating_overall') == 'None':
                home['cqc_rating_overall'] = 'Unknown'
            
            # ✅ FIX: Calculate distance only if needed for filtering
            if calculate_distances and home.get('latitude') and home.get('longitude'):
                try:
                    from utils.geo import calculate_distance_km
                    distance = calculate_distance_km(
                        float(user_lat), float(user_lon),
                        float(home['latitude']), float(home['longitude'])
                    )
                    home['distance_km'] = distance
                    
                    # Filter by max_distance_km if specified
                    if distance > max_distance_km:
                        continue
                except Exception as e:
                    logger.warning(f"Distance calculation failed: {e}")
                    home['distance_km'] = 0.0  # Use 0.0 instead of None
            elif user_lat and user_lon and home.get('latitude') and home.get('longitude'):
                # Calculate distance but don't filter (for later use)
                try:
                    from utils.geo import calculate_distance_km
                    distance = calculate_distance_km(
                        float(user_lat), float(user_lon),
                        float(home['latitude']), float(home['longitude'])
                    )
                    home['distance_km'] = distance
                except Exception as e:
                    logger.debug(f"Distance calculation skipped: {e}")
                    home['distance_km'] = 0.0  # Use 0.0 instead of None
            else:
                # ✅ FIX: Set default distance_km if not calculated
                if 'distance_km' not in home or home.get('distance_km') is None:
                    home['distance_km'] = 0.0
            
            # Enrich with staging data if available (for prices)
            # NOTE: This is done per-home, which may be slow. Consider batch enrichment instead.
            try:
                from services.staging_data_loader import load_staging_data
                from services.care_home_matcher import build_staging_index_with_keys, match_cqc_to_staging
                
                # Load staging data (cached, so fast on subsequent calls)
                staging_list = load_staging_data()
                
                if staging_list:
                    # Build staging index for matching
                    staging_index = build_staging_index_with_keys(staging_list)
                    
                    # Try to match this home with staging data
                    matched_staging = match_cqc_to_staging(home, staging_index)
                    
                    if matched_staging:
                        # Enrich with pricing data from staging
                        # matched_staging is already in DB format from map_staging_to_db_format
                        for db_field in ['fee_residential_from', 'fee_nursing_from', 'fee_dementia_from', 'fee_respite_from']:
                            if db_field in matched_staging:
                                value = matched_staging[db_field]
                                if value is not None and value > 0:
                                    home[db_field] = value
            except Exception as e:
                # Silently fail - staging enrichment is optional
                logger.debug(f"Staging enrichment failed for {home.get('name')}: {e}")
            
            homes.append(home)
        
        # Sort by distance (closest first) if available, else by rating
        if user_lat and user_lon:
            homes.sort(key=lambda h: (h.get('distance_km') or 999999, h.get('cqc_rating_overall') != 'Outstanding'))
        
        # ✅ REFACTOR: Apply limit only if specified
        # For professional report, we want ALL homes that match non-strict filters
        if limit is not None:
            homes = homes[:limit]
        
        logger.info(f"Returning {len(homes)} care homes to frontend (distances calculated: {calculate_distances})")
        
        return homes
        
    except Exception as e:
        logger.error(f"Database query error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []
    finally:
        conn.close()


class SQLiteCareHomesService:
    """
    Class wrapper for SQLite care homes service
    Provides same interface as other service classes
    """
    def __init__(self, db_path: str):
        """Initialize service with database path"""
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            logger.warning(f"Database file not found: {self.db_path}")
    
    def get_care_homes(
        self,
        local_authority: Optional[str] = None,
        care_type: Optional[str] = None,
        max_distance_km: Optional[float] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        postcode: Optional[str] = None,  # Ignored - kept for backward compatibility
        limit: Optional[int] = 50,
        apply_quality_filter: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get care homes from SQLite database
        
        Args:
            local_authority: Filter by local authority
            care_type: Filter by care type
            max_distance_km: Maximum distance in km
            user_lat: User latitude
            user_lon: User longitude
            postcode: Postcode (ignored, kept for compatibility)
            limit: Maximum number of results (None = no limit)
            apply_quality_filter: If True, filter by CQC rating
        
        Returns:
            List of care home dicts
        """
        # Use the global function
        return get_care_homes(
            local_authority=local_authority,
            care_type=care_type,
            max_distance_km=max_distance_km,
            user_lat=user_lat,
            user_lon=user_lon,
            limit=limit,
            apply_quality_filter=apply_quality_filter
        )
    
    def close(self):
        """Close service (no-op for this service, kept for compatibility)"""
        pass
