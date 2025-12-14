"""
Database Service
Service для работы с базой данных care_homes_db
"""
from typing import List, Dict, Optional, Any
import sys
from pathlib import Path
import os

# Import geo utilities
try:
    from utils.geo import calculate_distance_km
except ImportError:
    # Fallback if utils.geo not available
    import math
    def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        return round(R * c, 2)

# Add src to path for db_utils
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src" / "free_report_viewer"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from db_utils import get_db_connection
except ImportError:
    # Fallback: try psycopg2 directly
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    def get_db_connection():
        """Fallback database connection"""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return None
        try:
            return psycopg2.connect(database_url)
        except Exception as e:
            print(f"Database connection error: {e}")
            return None


class DatabaseService:
    """Service для работы с базой данных care_homes_db"""
    
    def __init__(self):
        """Initialize database service"""
        self.conn = None
    
    def _get_connection(self):
        """Get database connection"""
        if self.conn is None or self.conn.closed:
            self.conn = get_db_connection()
        return self.conn
    
    def get_care_homes(
        self,
        postcode: Optional[str] = None,
        local_authority: Optional[str] = None,
        care_type: Optional[str] = None,
        max_distance_km: Optional[float] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        max_budget: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get care homes from database
        
        Args:
            postcode: Filter by postcode prefix
            local_authority: Filter by local authority
            care_type: Filter by care type (residential, nursing, dementia, respite)
            max_distance_km: Maximum distance in km (requires user_lat, user_lon)
            user_lat: User latitude for distance calculation
            user_lon: User longitude for distance calculation
            max_budget: Maximum weekly budget
            limit: Maximum number of results
        
        Returns:
            List of care home dicts
        """
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT 
                    id, cqc_location_id, name, city, postcode,
                    latitude, longitude, region, local_authority,
                    beds_total, beds_available, has_availability, availability_status,
                    care_residential, care_nursing, care_dementia, care_respite,
                    fee_residential_from, fee_nursing_from, fee_dementia_from, fee_respite_from,
                    cqc_rating_overall, cqc_rating_safe, cqc_rating_effective,
                    cqc_rating_caring, cqc_rating_responsive, cqc_rating_well_led,
                    cqc_last_inspection_date,
                    google_rating, review_count,
                    wheelchair_access, ensuite_rooms, secure_garden,
                    wifi_available, parking_onsite,
                    telephone, website, email
                FROM care_homes
                WHERE 1=1
            """
            
            params = []
            param_count = 0
            
            # Postcode filter
            if postcode:
                postcode_prefix = postcode.upper().split()[0]
                param_count += 1
                query += f" AND postcode LIKE %s"
                params.append(f"{postcode_prefix}%")
            
            # Local authority filter - try both local_authority and city fields with normalization
            if local_authority and local_authority != "Unknown":
                try:
                    from services.location_normalizer import normalize_location_for_search
                    location_data = normalize_location_for_search(local_authority)
                    
                    if location_data['query_fragment'] and location_data['params']:
                        # Use normalized variants for better matching
                        query += location_data['query_fragment']
                        params.extend(location_data['params'])
                    else:
                        # Fallback to simple matching
                        query += f" AND (LOWER(local_authority) = LOWER(%s) OR LOWER(city) = LOWER(%s))"
                        params.append(local_authority)
                        params.append(local_authority)
                except ImportError:
                    # Fallback if normalizer not available
                    query += f" AND (LOWER(local_authority) = LOWER(%s) OR LOWER(city) = LOWER(%s))"
                    params.append(local_authority)
                    params.append(local_authority)
            
            # Care type filter
            if care_type:
                care_type_lower = care_type.lower()
                if care_type_lower == 'residential':
                    query += " AND care_residential = TRUE"
                elif care_type_lower == 'nursing':
                    query += " AND care_nursing = TRUE"
                elif care_type_lower == 'dementia':
                    query += " AND (care_dementia = TRUE OR care_residential = TRUE)"
                elif care_type_lower == 'respite':
                    query += " AND care_respite = TRUE"
            
            # Budget filter
            if max_budget:
                query += """
                    AND (
                        (fee_residential_from IS NOT NULL AND fee_residential_from <= %s)
                        OR (fee_nursing_from IS NOT NULL AND fee_nursing_from <= %s)
                        OR (fee_dementia_from IS NOT NULL AND fee_dementia_from <= %s)
                        OR (fee_respite_from IS NOT NULL AND fee_respite_from <= %s)
                    )
                """
                params.extend([max_budget, max_budget, max_budget, max_budget])
            
            # Distance filter (simple calculation, not PostGIS)
            # Note: For PostGIS, would use ST_DWithin
            if user_lat and user_lon and max_distance_km:
                import math
                # Simple bounding box filter first
                # 1 degree latitude ≈ 111 km
                lat_delta = max_distance_km / 111.0
                lon_delta = max_distance_km / (111.0 * abs(math.cos(math.radians(user_lat))))
                
                query += " AND latitude BETWEEN %s AND %s"
                params.append(user_lat - lat_delta)
                params.append(user_lat + lat_delta)
                
                query += " AND longitude BETWEEN %s AND %s"
                params.append(user_lon - lon_delta)
                params.append(user_lon + lon_delta)
            
            query += f" ORDER BY cqc_rating_overall DESC, google_rating DESC NULLS LAST LIMIT {limit}"
            
            # Execute query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Transform to dict format
            homes = []
            for row in rows:
                # Calculate distance if coordinates available
                distance_km = None
                if user_lat and user_lon and row[6] and row[7]:  # latitude, longitude
                    import math
                    distance_km = self._calculate_distance_km(
                        user_lat, user_lon,
                        float(row[6]), float(row[7])
                    )
                
                # Filter by distance if specified
                if max_distance_km and distance_km and distance_km > max_distance_km:
                    continue
                
                # Extract care types
                care_types = []
                if row[13]:  # care_residential
                    care_types.append('residential')
                if row[14]:  # care_nursing
                    care_types.append('nursing')
                if row[15]:  # care_dementia
                    care_types.append('dementia')
                if row[16]:  # care_respite
                    care_types.append('respite')
                
                # Get weekly cost based on care type
                weekly_cost = None
                if care_type:
                    care_type_lower = care_type.lower()
                    if care_type_lower == 'residential' and row[17]:  # fee_residential_from
                        weekly_cost = float(row[17])
                    elif care_type_lower == 'nursing' and row[18]:  # fee_nursing_from
                        weekly_cost = float(row[18])
                    elif care_type_lower == 'dementia' and row[19]:  # fee_dementia_from
                        weekly_cost = float(row[19])
                    elif care_type_lower == 'respite' and row[20]:  # fee_respite_from
                        weekly_cost = float(row[20])
                
                # Fallback to first available price
                if weekly_cost is None:
                    for price in [row[17], row[18], row[19], row[20]]:
                        if price:
                            weekly_cost = float(price)
                            break
                
                home = {
                    'id': row[0],
                    'location_id': row[1],
                    'cqc_location_id': row[1],
                    'name': row[2],
                    'city': row[3],
                    'postcode': row[4],
                    'latitude': float(row[5]) if row[5] else None,
                    'longitude': float(row[6]) if row[6] else None,
                    'region': row[7],
                    'local_authority': row[8],
                    'beds_total': row[9],
                    'beds_available': row[10],
                    'has_availability': row[11],
                    'availability_status': row[12],
                    'care_types': care_types,
                    'weekly_cost': weekly_cost,
                    'fee_residential_from': float(row[17]) if row[17] else None,
                    'fee_nursing_from': float(row[18]) if row[18] else None,
                    'fee_dementia_from': float(row[19]) if row[19] else None,
                    'fee_respite_from': float(row[20]) if row[20] else None,
                    'rating': row[21],  # cqc_rating_overall
                    'overall_rating': row[21],
                    'cqc_rating_overall': row[21],
                    'cqc_rating_safe': row[22],
                    'cqc_rating_effective': row[23],
                    'cqc_rating_caring': row[24],
                    'cqc_rating_responsive': row[25],
                    'cqc_rating_well_led': row[26],
                    'cqc_last_inspection_date': row[27].isoformat() if row[27] else None,
                    'google_rating': float(row[28]) if row[28] else None,
                    'review_count': row[29],
                    'user_ratings_total': row[29],
                    'facilities': {
                        'wheelchair_access': row[30],
                        'ensuite_rooms': row[31],
                        'secure_garden': row[32],
                        'wifi_available': row[33],
                        'parking_onsite': row[34]
                    },
                    'contact_phone': row[35],
                    'website': row[36],
                    'email': row[37],
                    'distance_km': distance_km,
                    'address': f"{row[2]}, {row[4]}"  # Simple address
                }
                homes.append(home)
            
            cursor.close()
            return homes
            
        except Exception as e:
            print(f"Database query error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _calculate_distance_km(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance in km using Haversine formula (delegates to geo utility)"""
        return calculate_distance_km(lat1, lon1, lat2, lon2)
    
    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None

