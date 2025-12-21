"""
Staging Data Loader
Loads and maps care homes data from Staging CSV (carehome_staging_export.csv)

Part of hybrid database approach:
- Auxiliary source: Staging CSV
- Returns list of staging records (not indexed by location_id since it's empty)
- Maps Staging fields to DB format
- Matching is done by care_home_matcher using multiple fields (name, postcode, city, etc.)
"""
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Field mappings from Staging CSV to DB format
STAGING_PRICING_MAPPING = {
    'fee_residential_from': 'parsed_fee_residential_from',
    'fee_nursing_from': 'parsed_fee_nursing_from',  # ✅ ДОБАВЛЕНО: критично для nursing care матчинга
    'fee_dementia_from': 'parsed_fee_dementia_from',
    'fee_respite_from': 'parsed_fee_respite_from'
}

STAGING_REVIEWS_MAPPING = {
    'review_average_score': 'parsed_review_average_score',
    'review_count': 'parsed_review_count'
}

STAGING_AMENITIES_MAPPING = {
    'wheelchair_access': 'parsed_wheelchair_access',
    'wifi_available': 'parsed_wifi_available',
    'parking_onsite': 'parsed_parking_onsite'
}

STAGING_AVAILABILITY_MAPPING = {
    'beds_total': 'parsed_beds_total'
}

STAGING_FUNDING_MAPPING = {
    'accepts_self_funding': 'parsed_accepts_self_funding',
    'accepts_local_authority': 'parsed_accepts_local_authority',
    'accepts_nhs_chc': 'parsed_accepts_nhs_chc'
}

# Cache for loaded staging data (can be list or dict for backward compatibility)
_staging_index_cache: Optional[Any] = None


def safe_parse_float(value: Optional[str]) -> Optional[float]:
    """Безопасно преобразовать строку в float"""
    if not value or value == '':
        return None
    try:
        # Handle comma as decimal separator
        value_clean = str(value).replace(',', '.').strip()
        return float(value_clean)
    except (ValueError, TypeError):
        return None


def safe_parse_int(value: Optional[str]) -> Optional[int]:
    """Безопасно преобразовать строку в int"""
    if not value or value == '':
        return None
    try:
        return int(float(str(value).replace(',', '.').strip()))
    except (ValueError, TypeError):
        return None


def normalize_boolean(value: Optional[Any]) -> Optional[bool]:
    """
    Преобразовать значение в boolean.
    
    Args:
        value: Может быть строкой ('True', 'False'), boolean, или числом
        
    Returns:
        True, False, или None
    """
    if value is None:
        return None
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    value_str = str(value).strip().upper()
    if value_str in ('TRUE', '1', 'YES', 'T', 'Y'):
        return True
    elif value_str in ('FALSE', '0', 'NO', 'F', 'N', ''):
        return False
    else:
        return None


def clean_text(value: Optional[str]) -> Optional[str]:
    """Очистить текст от лишних пробелов"""
    if not value:
        return None
    cleaned = str(value).strip()
    if cleaned.upper() in ('NULL', 'NONE', 'N/A', 'NA', ''):
        return None
    return cleaned if cleaned else None


def map_staging_to_db_format(staging_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Маппинг полей Staging CSV → формат БД.
    
    Args:
        staging_row: Строка из Staging CSV
        
    Returns:
        Dict с полями в формате БД
    """
    db_data: Dict[str, Any] = {}
    
    # ─────────────────────────────────────────────────────
    # Store original staging row for matching
    # (cqc_location_id is empty, so we'll match by other fields)
    # ─────────────────────────────────────────────────────
    db_data['_original_staging_row'] = staging_row
    
    # Try to get cqc_location_id if available (usually empty)
    cqc_location_id = clean_text(staging_row.get('cqc_location_id'))
    if cqc_location_id:
        db_data['cqc_location_id'] = cqc_location_id
    
    # ─────────────────────────────────────────────────────
    # Pricing (4 поля) - Weekly fees from staging
    # ─────────────────────────────────────────────────────
    for db_field, staging_field in STAGING_PRICING_MAPPING.items():
        value = staging_row.get(staging_field)
        db_data[db_field] = safe_parse_float(value)
    
    # ─────────────────────────────────────────────────────
    # Reviews (2 поля)
    # ─────────────────────────────────────────────────────
    for db_field, staging_field in STAGING_REVIEWS_MAPPING.items():
        value = staging_row.get(staging_field)
        if db_field == 'review_average_score':
            db_data[db_field] = safe_parse_float(value)
        elif db_field == 'review_count':
            db_data[db_field] = safe_parse_int(value)
    
    # ─────────────────────────────────────────────────────
    # Amenities (3 поля)
    # ─────────────────────────────────────────────────────
    for db_field, staging_field in STAGING_AMENITIES_MAPPING.items():
        value = staging_row.get(staging_field)
        db_data[db_field] = normalize_boolean(value)
    
    # ─────────────────────────────────────────────────────
    # Availability (1 поле)
    # ─────────────────────────────────────────────────────
    for db_field, staging_field in STAGING_AVAILABILITY_MAPPING.items():
        value = staging_row.get(staging_field)
        db_data[db_field] = safe_parse_int(value)
    
    # ─────────────────────────────────────────────────────
    # Funding (3 поля)
    # ─────────────────────────────────────────────────────
    for db_field, staging_field in STAGING_FUNDING_MAPPING.items():
        value = staging_row.get(staging_field)
        db_data[db_field] = normalize_boolean(value)
    
    return db_data


def load_staging_data(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Загрузить данные из Staging CSV.
    
    NOTE: Returns a LIST, not a dict indexed by location_id, because
    cqc_location_id is empty in staging table. Matching is done by
    care_home_matcher using multiple fields (name, postcode, city, etc.).
    
    Args:
        csv_path: Путь к CSV файлу. Если None, ищет автоматически.
        
    Returns:
        List[Dict]: Список записей из Staging CSV в формате БД
    """
    global _staging_index_cache
    
    # Use cache if available
    if _staging_index_cache is not None:
        # If cache is a list, return it
        if isinstance(_staging_index_cache, list):
            return _staging_index_cache
        # If cache is old dict format, convert to list
        return list(_staging_index_cache.values())
    
    # Find CSV file
    if csv_path:
        csv_file = Path(csv_path)
    else:
        # Try multiple possible paths
        _backend_dir = Path(__file__).parent
        _possible_paths = [
            _backend_dir.parent.parent.parent.parent / "documents" / "report-algorithms" / "carehome_staging_export.csv",
            _backend_dir.parent.parent.parent / "documents" / "report-algorithms" / "carehome_staging_export.csv",
            Path("/Users/alexander/Documents/Products/RCH-admin-playground/documents/report-algorithms/carehome_staging_export.csv"),
        ]
        
        csv_file = None
        for path in _possible_paths:
            if path.exists():
                csv_file = path
                break
        
        if not csv_file:
            logger.warning(f"Staging CSV file not found. Tried paths: {_possible_paths}")
            return []
    
    if not csv_file.exists():
        logger.warning(f"Staging CSV file not found: {csv_file}")
        return []
    
    try:
        staging_list: List[Dict[str, Any]] = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            processed = 0
            skipped_dormant = 0
            added = 0
            
            for row in reader:
                processed += 1
                
                # Skip dormant homes
                if normalize_boolean(row.get('is_dormant')):
                    skipped_dormant += 1
                    continue
                
                # Map Staging row to DB format
                db_data = map_staging_to_db_format(row)
                
                # Add to list (matching will be done by care_home_matcher)
                if db_data:  # Only add if we got some data
                    staging_list.append(db_data)
                    added += 1
        
        logger.info(
            f"Staging CSV processing: {processed} total, "
            f"{added} added, {skipped_dormant} dormant"
        )
        
        _staging_index_cache = staging_list
        logger.info(f"✅ Loaded {len(staging_list)} staging records from CSV: {csv_file}")
        return staging_list
    
    except Exception as e:
        logger.error(f"❌ Error loading Staging CSV data: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_staging_data_by_location_id(location_id: str) -> Optional[Dict[str, Any]]:
    """
    Получить данные Staging по location_id.
    
    NOTE: This function is deprecated since staging table doesn't have location_id.
    Use care_home_matcher.match_cqc_to_staging() instead.
    
    Args:
        location_id: CQC location ID (формат: '1-10000302982')
        
    Returns:
        Dict с данными Staging или None
    """
    staging_list = load_staging_data()
    # Try to find by location_id if it exists
    for staging_data in staging_list:
        if staging_data.get('cqc_location_id') == location_id:
            return staging_data
    return None

