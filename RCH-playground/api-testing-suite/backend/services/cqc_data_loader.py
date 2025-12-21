"""
CQC Data Loader
Loads and maps care homes data from CQC CSV (cqc_carehomes_master_full_data_rows.csv)

Part of hybrid database approach:
- Primary source: CQC CSV
- Maps CQC fields to DB format
- Normalizes data (boolean, float, dates, ratings)
"""
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Field mappings from CQC CSV to DB format
CQC_SERVICE_BANDS_MAPPING = {
    'serves_older_people': 'service_user_band_older_people',
    'serves_dementia_band': 'service_user_band_dementia',
    'serves_mental_health': 'service_user_band_mental_health',
    'serves_physical_disabilities': 'service_user_band_physical_disability',
    'serves_sensory_impairments': 'service_user_band_sensory_impairment',
    'serves_children': 'service_user_band_children',
    'serves_learning_disabilities': 'service_user_band_learning_disabilities',
    'serves_detained_mha': 'service_user_band_detained_mental_health',
    'serves_substance_misuse': 'service_user_band_drugs_alcohol',
    'serves_eating_disorders': 'service_user_band_eating_disorder',
    'serves_whole_population': 'service_user_band_whole_population',
    'serves_younger_adults': 'service_user_band_younger_adults'
}

CQC_RATINGS_MAPPING = {
    'cqc_rating_overall': 'location_latest_overall_rating',
    'cqc_rating_safe': 'cqc_rating_safe',
    'cqc_rating_effective': 'cqc_rating_effective',
    'cqc_rating_caring': 'cqc_rating_caring',
    'cqc_rating_responsive': 'cqc_rating_responsive',
    'cqc_rating_well_led': 'cqc_rating_well_led'
}

CQC_LOCATION_MAPPING = {
    'latitude': 'location_latitude',
    'longitude': 'location_longitude',
    'postcode': 'location_postal_code',
    'city': 'location_city',
    'local_authority': 'location_local_authority'
}

CQC_CARE_TYPES_MAPPING = {
    'care_nursing': 'service_type_care_home_nursing',
    'care_residential': 'service_type_care_home_without_nursing',
    'care_dementia': 'service_user_band_dementia'  # Proxy
}

# Cache for loaded data
_cqc_homes_cache: Optional[List[Dict[str, Any]]] = None


def normalize_cqc_boolean(value: Optional[str]) -> Optional[bool]:
    """
    Преобразовать 'TRUE'/'FALSE' → True/False.
    
    Args:
        value: Строка из CSV ('TRUE', 'FALSE', '', None)
        
    Returns:
        True, False, или None
    """
    if not value:
        return None
    
    value_str = str(value).strip().upper()
    if value_str in ('TRUE', '1', 'YES', 'T'):
        return True
    elif value_str in ('FALSE', '0', 'NO', 'F'):
        return False
    else:
        return None


def normalize_cqc_rating(value: Optional[str]) -> Optional[str]:
    """
    Нормализовать CQC рейтинг.
    
    Args:
        value: Рейтинг из CSV ('Good', 'Outstanding', 'Requires improvement', 'Inadequate', 'Unknown', '')
        
    Returns:
        Нормализованный рейтинг или None
    """
    if not value:
        return None
    
    value_str = str(value).strip()
    if not value_str or value_str.upper() in ('NULL', 'NONE', 'N/A', 'NA', 'UNKNOWN', ''):
        return None
    
    # Normalize common variations
    value_lower = value_str.lower()
    if 'outstanding' in value_lower:
        return 'Outstanding'
    elif 'good' in value_lower:
        return 'Good'
    elif 'requires improvement' in value_lower or 'requires' in value_lower:
        return 'Requires improvement'
    elif 'inadequate' in value_lower:
        return 'Inadequate'
    else:
        return value_str  # Return as-is if not recognized


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


def clean_text(value: Optional[str]) -> Optional[str]:
    """Очистить текст от лишних пробелов"""
    if not value:
        return None
    cleaned = str(value).strip()
    if cleaned.upper() in ('NULL', 'NONE', 'N/A', 'NA', ''):
        return None
    return cleaned if cleaned else None


def map_cqc_to_db_format(cqc_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Маппинг полей CQC CSV → формат БД.
    
    Args:
        cqc_row: Строка из CQC CSV
        
    Returns:
        Dict с полями в формате БД
    """
    db_home: Dict[str, Any] = {}
    
    # ─────────────────────────────────────────────────────
    # ID и базовые поля
    # ─────────────────────────────────────────────────────
    db_home['id'] = clean_text(cqc_row.get('location_id'))
    db_home['location_id'] = clean_text(cqc_row.get('location_id'))
    db_home['cqc_location_id'] = clean_text(cqc_row.get('location_id'))
    db_home['name'] = clean_text(cqc_row.get('location_name'))
    
    # ─────────────────────────────────────────────────────
    # Service User Bands (12 полей)
    # ─────────────────────────────────────────────────────
    for db_field, cqc_field in CQC_SERVICE_BANDS_MAPPING.items():
        db_home[db_field] = normalize_cqc_boolean(cqc_row.get(cqc_field))
    
    # ─────────────────────────────────────────────────────
    # CQC Ratings (6 полей)
    # ─────────────────────────────────────────────────────
    for db_field, cqc_field in CQC_RATINGS_MAPPING.items():
        db_home[db_field] = normalize_cqc_rating(cqc_row.get(cqc_field))
    
    # ─────────────────────────────────────────────────────
    # Location (5 полей)
    # ─────────────────────────────────────────────────────
    db_home['latitude'] = safe_parse_float(cqc_row.get('location_latitude'))
    db_home['longitude'] = safe_parse_float(cqc_row.get('location_longitude'))
    db_home['postcode'] = clean_text(cqc_row.get('location_postal_code'))
    db_home['city'] = clean_text(cqc_row.get('location_city'))
    db_home['local_authority'] = clean_text(cqc_row.get('location_local_authority'))
    
    # ─────────────────────────────────────────────────────
    # Care Types (3 поля)
    # ─────────────────────────────────────────────────────
    db_home['care_nursing'] = normalize_cqc_boolean(cqc_row.get('service_type_care_home_nursing'))
    db_home['care_residential'] = normalize_cqc_boolean(cqc_row.get('service_type_care_home_without_nursing'))
    # Dementia care is a proxy from service_user_band_dementia
    db_home['care_dementia'] = normalize_cqc_boolean(cqc_row.get('service_user_band_dementia'))
    
    # ─────────────────────────────────────────────────────
    # Regulated Activities (для лицензий)
    # ─────────────────────────────────────────────────────
    db_home['has_nursing_care_license'] = normalize_cqc_boolean(cqc_row.get('service_type_care_home_nursing'))
    db_home['has_personal_care_license'] = normalize_cqc_boolean(cqc_row.get('service_type_care_home_without_nursing'))
    db_home['has_surgical_procedures_license'] = normalize_cqc_boolean(cqc_row.get('regulated_activity_surgical'))
    db_home['has_treatment_license'] = normalize_cqc_boolean(cqc_row.get('regulated_activity_treatment'))
    db_home['has_diagnostic_license'] = normalize_cqc_boolean(cqc_row.get('regulated_activity_diagnostic'))
    
    # ─────────────────────────────────────────────────────
    # Дополнительные поля
    # ─────────────────────────────────────────────────────
    db_home['region'] = clean_text(cqc_row.get('location_region'))
    db_home['provider_id'] = clean_text(cqc_row.get('provider_id'))
    db_home['provider_name'] = clean_text(cqc_row.get('provider_name'))
    db_home['dormant'] = normalize_cqc_boolean(cqc_row.get('dormant'))
    
    # Inspection date
    inspection_date_str = clean_text(cqc_row.get('publication_date'))
    if inspection_date_str:
        # Try to parse date (format: YYYY-MM-DD or similar)
        try:
            # Extract first 10 characters (YYYY-MM-DD)
            if len(inspection_date_str) >= 10:
                db_home['cqc_last_inspection_date'] = inspection_date_str[:10]
            else:
                db_home['cqc_last_inspection_date'] = inspection_date_str
        except Exception:
            db_home['cqc_last_inspection_date'] = inspection_date_str
    else:
        db_home['cqc_last_inspection_date'] = None
    
    # Beds (if available in CQC)
    beds_str = cqc_row.get('care_homes_beds')
    if beds_str:
        db_home['beds_total'] = safe_parse_int(beds_str)
    else:
        db_home['beds_total'] = None
    
    return db_home


def load_cqc_homes(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Загрузить дома из CQC CSV.
    
    Args:
        csv_path: Путь к CSV файлу. Если None, ищет автоматически.
        
    Returns:
        List[Dict]: Список домов с полями в формате БД
    """
    global _cqc_homes_cache
    
    # Use cache if available
    if _cqc_homes_cache is not None:
        return _cqc_homes_cache
    
    # Find CSV file
    if csv_path:
        csv_file = Path(csv_path)
    else:
        # Try multiple possible paths
        _backend_dir = Path(__file__).parent
        _possible_paths = [
            _backend_dir.parent.parent.parent.parent / "documents" / "report-algorithms" / "cqc_carehomes_master_full_data_rows.csv",
            _backend_dir.parent.parent.parent / "documents" / "report-algorithms" / "cqc_carehomes_master_full_data_rows.csv",
            Path("/Users/alexander/Documents/Products/RCH-admin-playground/documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv"),
        ]
        
        csv_file = None
        for path in _possible_paths:
            if path.exists():
                csv_file = path
                break
        
        if not csv_file:
            logger.error(f"CQC CSV file not found. Tried paths: {_possible_paths}")
            return []
    
    if not csv_file.exists():
        logger.error(f"CQC CSV file not found: {csv_file}")
        return []
    
    try:
        homes = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip dormant homes
                if normalize_cqc_boolean(row.get('dormant')):
                    continue
                
                # Map CQC row to DB format
                db_home = map_cqc_to_db_format(row)
                
                # Only add if we have at least location_id
                if db_home.get('location_id'):
                    homes.append(db_home)
        
        _cqc_homes_cache = homes
        logger.info(f"✅ Loaded {len(homes)} care homes from CQC CSV: {csv_file}")
        return homes
    
    except Exception as e:
        logger.error(f"❌ Error loading CQC CSV data: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_cqc_home_by_location_id(location_id: str) -> Optional[Dict[str, Any]]:
    """
    Получить дом по location_id.
    
    Args:
        location_id: CQC location ID (формат: '1-10000302982')
        
    Returns:
        Dict с данными дома или None
    """
    homes = load_cqc_homes()
    for home in homes:
        if home.get('location_id') == location_id:
            return home
    return None

