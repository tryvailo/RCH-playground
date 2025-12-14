"""
Database utilities for Free Report Viewer
Functions for accessing MSIF fees data

Fair Cost Gap = разница между рыночной ценой (Lottie average или scraped) 
и MSIF fair cost lower bound (из БД msif_fees_2025)
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path for msif_loader
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Try to import msif_loader (preferred method)
try:
    from msif_loader import get_fair_cost_lower_bound as msif_get_fair_cost
    MSIF_LOADER_AVAILABLE = True
except ImportError:
    MSIF_LOADER_AVAILABLE = False


def get_db_connection():
    """Get database connection from environment variable"""
    if not PSYCOPG2_AVAILABLE:
        return None
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    
    try:
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def get_msif_fee(
    local_authority: str,
    care_type: str
) -> Optional[Dict[str, float]]:
    """
    Get MSIF fair cost lower bound from msif_loader (preferred) or database
    
    Priority:
    1. msif_loader.py (downloads from gov.uk)
    2. Database (msif_fees_2025 table)
    3. Mock data (fallback)
    
    Args:
        local_authority: Local authority name
        care_type: 'residential', 'nursing', 'residential_dementia', 'nursing_dementia'
        
    Returns:
        Dict with 'msif_lower_bound' value, or None if not found
    """
    # Try msif_loader first (preferred method)
    if MSIF_LOADER_AVAILABLE:
        try:
            msif_lower = msif_get_fair_cost(local_authority, care_type)
            if msif_lower is not None:
                return {
                    'msif_lower_bound': float(msif_lower),
                    'local_authority': local_authority,
                    'source': 'msif_loader'
                }
        except Exception as e:
            print(f"Error using msif_loader: {e}")
    
    # Fallback to database
    conn = get_db_connection()
    if not conn:
        # Fallback to mock data if DB not available
        return _get_mock_msif_fee(local_authority, care_type)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            column_name = "nursing_median" if care_type == "nursing" else "residential_median"
            
            query = f"""
                SELECT {column_name} as msif_lower_bound
                FROM msif_fees_2025
                WHERE local_authority = %s
                LIMIT 1
            """
            
            cur.execute(query, (local_authority,))
            result = cur.fetchone()
            
            if result and result.get('msif_lower_bound'):
                return {
                    'msif_lower_bound': float(result['msif_lower_bound']),
                    'local_authority': local_authority,
                    'source': 'database'
                }
            else:
                # Fallback to mock if not found
                return _get_mock_msif_fee(local_authority, care_type)
                
    except Exception as e:
        print(f"Error querying MSIF fees: {e}")
        return _get_mock_msif_fee(local_authority, care_type)
    finally:
        conn.close()


def _get_mock_msif_fee(local_authority: str, care_type: str) -> Dict[str, float]:
    """
    Mock MSIF fee data (fallback when DB not available)
    
    Typical MSIF lower bounds:
    - Residential: £600-900/week
    - Nursing: £800-1200/week
    """
    # Mock data based on care type
    if care_type == "nursing":
        msif_lower = 850.0  # Typical nursing lower bound
    elif care_type == "dementia":
        msif_lower = 950.0  # Dementia care typically higher
    else:  # residential
        msif_lower = 700.0  # Typical residential lower bound
    
    return {
        'msif_lower_bound': msif_lower,
        'local_authority': local_authority
    }


def get_local_authority_from_postcode(postcode: str) -> Optional[str]:
    """
    Get local authority from postcode
    
    This is a simplified version. In production, you would:
    1. Use a postcode lookup API (e.g., postcodes.io)
    2. Query CQC API for care homes in that postcode
    3. Use a postcode database
    
    For now, returns mock data based on postcode patterns
    """
    # Simplified mapping (in production, use proper postcode lookup)
    postcode_upper = postcode.upper().strip()
    
    # London postcodes
    if postcode_upper.startswith(('SW', 'SE', 'NW', 'NE', 'E', 'W', 'N', 'WC', 'EC')):
        return "Westminster"  # Default London LA
    
    # Manchester
    if postcode_upper.startswith('M'):
        return "Manchester"
    
    # Birmingham
    if postcode_upper.startswith('B'):
        return "Birmingham"
    
    # Default fallback
    return "Unknown Local Authority"

