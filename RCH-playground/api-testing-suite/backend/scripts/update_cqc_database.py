#!/usr/bin/env python3
"""
CQC Database Update Script

Обновляет CQC базу данных через API, заполняя пустые или неправильные поля.

Использование:
    python3 update_cqc_database.py [--dry-run] [--limit N] [--fields field1,field2]
    
Опции:
    --dry-run: Только анализ, без обновления
    --limit N: Обновить только первые N домов (для тестирования)
    --fields: Список полей для обновления (по умолчанию все)
    --output: Путь к выходному CSV файлу (по умолчанию обновляет исходный)
"""
import asyncio
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set, Union
from datetime import datetime
import argparse
import logging

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from api_clients.cqc_client import CQCAPIClient
from services.cqc_data_loader import load_cqc_homes, map_cqc_to_db_format, CQC_SERVICE_BANDS_MAPPING, CQC_RATINGS_MAPPING
from config_manager import get_credentials

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cqc_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Fields that can be updated from CQC API
UPDATABLE_FIELDS = {
    # CQC Ratings
    'cqc_rating_overall',
    'cqc_rating_safe',
    'cqc_rating_effective',
    'cqc_rating_caring',
    'cqc_rating_responsive',
    'cqc_rating_well_led',
    # Regulated Activities
    'regulated_activity_nursing_care',
    'regulated_activity_personal_care',
    'regulated_activity_surgical',
    'regulated_activity_diagnostic',
    'regulated_activity_treatment',
    
    # Location
    'latitude',
    'longitude',
    'postcode',
    'city',
    'local_authority',
    
    # Service User Bands
    'serves_older_people',
    'serves_dementia_band',
    'serves_mental_health',
    'serves_physical_disabilities',
    'serves_sensory_impairments',
    'serves_children',
    'serves_learning_disabilities',
    'serves_detained_mha',
    'serves_substance_misuse',
    'serves_eating_disorders',
    'serves_whole_population',
    'serves_younger_adults',
    
    # Care Types
    'care_nursing',
    'care_residential',
    'care_dementia',
    
    # Inspection Date
    'cqc_last_inspection_date',
    
    # Beds
    'beds_total',
    
    # Facilities (may not be available in CQC API - will remain empty if not in API)
    'wheelchair_access',
    'parking_onsite',
    'ensuite_rooms',
    'secure_garden',
    'wifi_available',
    
    # Financial (may not be available in CQC API - will remain empty if not in API)
    'fee_residential_from',
    'fee_nursing_from',
    'fee_dementia_from',
    'accepts_self_funding',
    'accepts_local_authority',
    'accepts_nhs_chc',
}


def extract_ratings_from_api(api_data: Dict) -> Dict[str, Optional[str]]:
    """Extract CQC ratings from API response"""
    ratings = {}
    
    # Try multiple paths for overall rating
    overall_raw = (
        api_data.get('latestOverallRating') or
        api_data.get('overallRating') or
        api_data.get('ratings', {}).get('overall') or
        api_data.get('currentRatings', {}).get('overall')
    )
    
    # Extract rating string from dict if needed
    if overall_raw:
        if isinstance(overall_raw, dict):
            # API returns dict with 'rating' field
            overall = overall_raw.get('rating')
        else:
            # Already a string
            overall = str(overall_raw)
    else:
        overall = None
    
    # Get individual ratings from inspectionAreas
    inspection_areas = api_data.get('inspectionAreas', [])
    for area in inspection_areas:
        area_name = area.get('name', '').lower()
        rating = area.get('rating') or area.get('currentRating')
        
        if area_name == 'safe':
            ratings['cqc_rating_safe'] = rating
        elif area_name == 'effective':
            ratings['cqc_rating_effective'] = rating
        elif area_name == 'caring':
            ratings['cqc_rating_caring'] = rating
        elif area_name == 'responsive':
            ratings['cqc_rating_responsive'] = rating
        elif area_name == 'well-led':
            ratings['cqc_rating_well_led'] = rating
    
    # Also try to get ratings from latestOverallRating.keyQuestionRatings
    if overall_raw and isinstance(overall_raw, dict):
        key_question_ratings = overall_raw.get('keyQuestionRatings', [])
        for kq_rating in key_question_ratings:
            name = kq_rating.get('name', '').lower()
            rating_value = kq_rating.get('rating')
            
            if name == 'safe' and not ratings.get('cqc_rating_safe'):
                ratings['cqc_rating_safe'] = rating_value
            elif name == 'effective' and not ratings.get('cqc_rating_effective'):
                ratings['cqc_rating_effective'] = rating_value
            elif name == 'caring' and not ratings.get('cqc_rating_caring'):
                ratings['cqc_rating_caring'] = rating_value
            elif name == 'responsive' and not ratings.get('cqc_rating_responsive'):
                ratings['cqc_rating_responsive'] = rating_value
            elif name == 'well-led' and not ratings.get('cqc_rating_well_led'):
                ratings['cqc_rating_well_led'] = rating_value
    
    ratings['cqc_rating_overall'] = overall
    return ratings


def extract_service_user_bands_from_api(api_data: Dict) -> Dict[str, bool]:
    """Extract Service User Bands from API response"""
    bands = {}
    
    # Try multiple paths
    gac_service_types = api_data.get('gacServiceTypes', [])
    specialisms = api_data.get('specialisms', [])
    
    # Map specialisms to service user bands (improved matching)
    # API returns names like "Caring for adults over 65 yrs", "Caring for people whose rights are restricted under the Mental Health Act", etc.
    for specialism in specialisms:
        specialism_name = specialism.get('name', '').lower()
        
        # Match by keywords in specialism name
        if 'over 65' in specialism_name or 'older people' in specialism_name or 'adults over' in specialism_name:
            bands['serves_older_people'] = True
        elif 'dementia' in specialism_name:
            bands['serves_dementia_band'] = True
        elif 'mental health' in specialism_name or 'mha' in specialism_name:
            if 'detained' in specialism_name or 'rights are restricted' in specialism_name:
                bands['serves_detained_mha'] = True
            else:
                bands['serves_mental_health'] = True
        elif 'physical disabilit' in specialism_name:
            bands['serves_physical_disabilities'] = True
        elif 'sensory impair' in specialism_name:
            bands['serves_sensory_impairments'] = True
        elif 'learning disabilit' in specialism_name:
            bands['serves_learning_disabilities'] = True
        elif 'children' in specialism_name or '0-18' in specialism_name:
            bands['serves_children'] = True
        elif 'younger adults' in specialism_name or '18-65' in specialism_name:
            bands['serves_younger_adults'] = True
        elif 'substance' in specialism_name or 'drugs' in specialism_name or 'alcohol' in specialism_name:
            bands['serves_substance_misuse'] = True
        elif 'eating disord' in specialism_name:
            bands['serves_eating_disorders'] = True
        elif 'whole population' in specialism_name or 'all ages' in specialism_name:
            bands['serves_whole_population'] = True
    
    # Also check gacServiceTypes for additional information
    for gac_type in gac_service_types:
        gac_name = gac_type.get('name', '').lower()
        gac_desc = gac_type.get('description', '').lower()
        
        # Check if it's a whole population service
        if 'all ages' in gac_name or 'all ages' in gac_desc:
            bands['serves_whole_population'] = True
    
    return bands


def extract_location_from_api(api_data: Dict) -> Dict[str, Optional[any]]:
    """Extract location data from API response"""
    location = {}
    
    # Try multiple paths
    location_data = api_data.get('location', {}) or api_data
    
    location['latitude'] = (
        location_data.get('latitude') or
        location_data.get('locationLatitude') or
        location_data.get('geoLocation', {}).get('latitude')
    )
    
    location['longitude'] = (
        location_data.get('longitude') or
        location_data.get('locationLongitude') or
        location_data.get('geoLocation', {}).get('longitude')
    )
    
    location['postcode'] = (
        location_data.get('postalCode') or
        location_data.get('postcode') or
        location_data.get('locationPostalCode')
    )
    
    location['city'] = (
        location_data.get('city') or
        location_data.get('locationCity') or
        location_data.get('town')
    )
    
    location['local_authority'] = (
        location_data.get('localAuthority') or
        location_data.get('localAuthorityName') or
        location_data.get('locationLocalAuthority')
    )
    
    return location


def extract_care_types_from_api(api_data: Dict) -> Dict[str, bool]:
    """Extract care types from API response"""
    care_types = {}
    
    # Check serviceTypes
    service_types = api_data.get('serviceTypes', [])
    for service_type in service_types:
        service_name = service_type.get('name', '').lower()
        if 'nursing' in service_name:
            care_types['care_nursing'] = True
        if 'without nursing' in service_name or 'residential' in service_name:
            care_types['care_residential'] = True
    
    # Check regulatedActivities
    regulated_activities = api_data.get('regulatedActivities', [])
    for activity in regulated_activities:
        activity_name = activity.get('name', '').lower()
        if 'nursing care' in activity_name:
            care_types['care_nursing'] = True
        if 'personal care' in activity_name:
            care_types['care_residential'] = True
    
    # Dementia is a proxy from service user bands
    specialisms = api_data.get('specialisms', [])
    for specialism in specialisms:
        if 'dementia' in specialism.get('name', '').lower():
            care_types['care_dementia'] = True
            break
    
    return care_types


def extract_regulated_activities_from_api(api_data: Dict) -> Dict[str, bool]:
    """Extract regulated activities from API response"""
    activities = {}
    
    # Check regulatedActivities
    regulated_activities = api_data.get('regulatedActivities', [])
    for activity in regulated_activities:
        activity_name = activity.get('name', '').lower()
        activity_code = activity.get('code', '').upper()
        
        # Map to CSV fields
        if 'nursing care' in activity_name or activity_code == 'RA1':
            activities['regulated_activity_nursing_care'] = True
        if 'personal care' in activity_name or activity_code == 'RA2':
            activities['regulated_activity_personal_care'] = True
        if 'surgical' in activity_name or activity_code == 'RA3':
            activities['regulated_activity_surgical'] = True
        if 'diagnostic' in activity_name or activity_code == 'RA4':
            activities['regulated_activity_diagnostic'] = True
        if 'treatment' in activity_name or activity_code == 'RA5':
            activities['regulated_activity_treatment'] = True
        if 'accommodation' in activity_name and 'nursing' in activity_name:
            # "Accommodation for persons who require nursing or personal care" - это RA2
            activities['regulated_activity_personal_care'] = True
            # Также может быть nursing care, если указано явно
            if 'nursing' in activity_name and 'personal' not in activity_name:
                activities['regulated_activity_nursing_care'] = True
    
    return activities


def extract_inspection_date_from_api(api_data: Dict) -> Optional[str]:
    """Extract last inspection date from API response"""
    # Try multiple paths
    inspection_date = (
        api_data.get('lastInspectionDate') or
        api_data.get('publicationDate') or
        api_data.get('latestInspectionDate') or
        api_data.get('inspectionDate')
    )
    
    if inspection_date:
        # Normalize date format (YYYY-MM-DD)
        if isinstance(inspection_date, str):
            # Extract first 10 characters (YYYY-MM-DD)
            if len(inspection_date) >= 10:
                return inspection_date[:10]
            return inspection_date
    
    return None


def extract_facilities_from_api(api_data: Dict) -> Dict[str, Optional[bool]]:
    """
    Extract facilities from API response.
    
    NOTE: CQC API typically does NOT contain facilities data.
    This function attempts to extract if available, but will return empty dict.
    If no data in API, fields will remain empty in CQC table.
    Staging table is used separately for other purposes.
    """
    facilities = {}
    
    # CQC API does not typically contain facilities data
    # But we check for any potential fields that might exist
    # These are unlikely to be present, but we try anyway
    
    # Check if there's any facilities-related data in the API response
    # (This is a placeholder - CQC API doesn't provide facilities)
    
    # If in the future CQC API adds facilities, we can extract them here
    # For now, return empty dict (no facilities data from CQC API)
    
    return facilities


def extract_financial_from_api(api_data: Dict) -> Dict[str, Optional[Union[float, bool]]]:
    """
    Extract financial data from API response.
    
    NOTE: CQC API does NOT contain pricing/fees data (see documentation).
    This function attempts to extract if available, but will return empty dict.
    If no data in API, fields will remain empty in CQC table.
    Staging table is used separately for other purposes.
    """
    financial = {}
    
    # CQC API does not contain pricing/fees data (see CQC-fields-api-analysis.md)
    # Documentation states: "Pricing/fees: ❌ НЕТ в CQC - нужен provider portal"
    
    # Check if there's any financial-related data in the API response
    # (This is a placeholder - CQC API doesn't provide financial data)
    
    # If in the future CQC API adds financial data, we can extract them here
    # For now, return empty dict (no financial data from CQC API)
    
    return financial


def extract_beds_from_api(api_data: Dict) -> Optional[int]:
    """Extract beds total from API response"""
    beds = (
        api_data.get('beds') or
        api_data.get('totalBeds') or
        api_data.get('numberOfBeds') or
        api_data.get('careHomesBeds')
    )
    
    if beds:
        try:
            return int(beds)
        except (ValueError, TypeError):
            return None
    
    return None


def save_homes_to_csv(
    homes: List[Dict],
    output_path: Path,
    original_csv_path: Path,
    original_csv_rows: Optional[Dict[str, Dict]] = None
) -> None:
    """
    Save updated homes to CSV file.
    
    Maps DB format back to CQC CSV format.
    Preserves all original CSV fields and updates only changed fields.
    
    Args:
        homes: List of updated homes in DB format
        output_path: Path to output CSV file
        original_csv_path: Path to original CSV (for reference structure)
        original_csv_rows: Optional dict of {location_id: original_csv_row} to preserve all fields
    """
    # Read original CSV to get column order and structure
    original_columns = []
    try:
        with open(original_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            original_columns = reader.fieldnames or []
    except Exception as e:
        logger.warning(f"Could not read original CSV structure: {e}")
        # Use default columns if can't read original
        original_columns = [
            'location_id', 'location_name', 'location_latitude', 'location_longitude',
            'location_postal_code', 'location_city', 'location_local_authority',
            'service_user_band_older_people', 'service_user_band_dementia',
            'cqc_rating_overall', 'cqc_rating_safe', 'service_type_care_home_nursing',
            'service_type_care_home_without_nursing', 'publication_date', 'care_homes_beds'
        ]
    
    # If original_csv_rows provided, use it to preserve all fields
    if original_csv_rows is None:
        original_csv_rows = {}
    
    # Reverse mappings (DB field → CQC CSV field)
    REVERSE_SERVICE_BANDS = {v: k for k, v in CQC_SERVICE_BANDS_MAPPING.items()}
    # Note: For ratings, we use direct mapping (CQC_RATINGS_MAPPING) not reverse
    # because db_field is the key, not the value
    
    # Write updated CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        if original_columns:
            writer = csv.DictWriter(f, fieldnames=original_columns, extrasaction='ignore')
        else:
            # If no original columns, use all possible fields from homes
            all_fields = set()
            for home in homes:
                all_fields.update(home.keys())
            writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
        
        writer.writeheader()
        
        for home in homes:
            # Get location_id for lookup
            location_id = home.get('location_id') or home.get('cqc_location_id', '')
            
            # Start with original CSV row if available (preserves all fields)
            if location_id in original_csv_rows:
                csv_row = original_csv_rows[location_id].copy()
            else:
                csv_row = {}
            
            # Map updated fields from DB format back to CSV format
            for db_field, value in home.items():
                # ID fields
                if db_field == 'location_id' or db_field == 'cqc_location_id':
                    csv_row['location_id'] = value
                elif db_field == 'name':
                    csv_row['location_name'] = value
                
                # Location fields
                elif db_field == 'latitude':
                    csv_row['location_latitude'] = value
                elif db_field == 'longitude':
                    csv_row['location_longitude'] = value
                elif db_field == 'postcode':
                    csv_row['location_postal_code'] = value
                elif db_field == 'city':
                    csv_row['location_city'] = value
                elif db_field == 'local_authority':
                    csv_row['location_local_authority'] = value
                
                # Service User Bands (reverse mapping)
                elif db_field in REVERSE_SERVICE_BANDS:
                    cqc_field = REVERSE_SERVICE_BANDS[db_field]
                    csv_row[cqc_field] = 'TRUE' if value else 'FALSE' if value is False else ''
                
                # CQC Ratings (direct mapping - FIXED)
                # db_field is the key in CQC_RATINGS_MAPPING, not the value
                elif db_field in CQC_RATINGS_MAPPING:
                    cqc_field = CQC_RATINGS_MAPPING[db_field]
                    csv_row[cqc_field] = value if value else ''
                
                # Regulated Activities (direct mapping)
                elif db_field.startswith('regulated_activity_'):
                    # Map directly: regulated_activity_nursing_care -> regulated_activity_nursing_care
                    # Convert boolean to CSV format: True -> 'TRUE', False -> 'FALSE', None -> ''
                    if value is True:
                        csv_row[db_field] = 'TRUE'
                    elif value is False:
                        csv_row[db_field] = 'FALSE'
                    else:
                        csv_row[db_field] = ''
                
                # Care Types
                elif db_field == 'care_nursing':
                    csv_row['service_type_care_home_nursing'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'care_residential':
                    csv_row['service_type_care_home_without_nursing'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'care_dementia':
                    # Dementia is mapped from service_user_band_dementia
                    csv_row['service_user_band_dementia'] = 'TRUE' if value else 'FALSE' if value is False else ''
                
                # Inspection Date
                elif db_field == 'cqc_last_inspection_date':
                    csv_row['publication_date'] = value if value else ''
                
                # Beds
                elif db_field == 'beds_total':
                    csv_row['care_homes_beds'] = str(value) if value else ''
                
                # Facilities (direct mapping - may not be in CSV, but we save for future use)
                elif db_field == 'wheelchair_access':
                    csv_row['wheelchair_access'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'parking_onsite':
                    csv_row['parking_onsite'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'ensuite_rooms':
                    csv_row['ensuite_rooms'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'secure_garden':
                    csv_row['secure_garden'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'wifi_available':
                    csv_row['wifi_available'] = 'TRUE' if value else 'FALSE' if value is False else ''
                
                # Financial (direct mapping - may not be in CSV, but we save for future use)
                elif db_field == 'fee_residential_from':
                    csv_row['fee_residential_from'] = str(value) if value else ''
                elif db_field == 'fee_nursing_from':
                    csv_row['fee_nursing_from'] = str(value) if value else ''
                elif db_field == 'fee_dementia_from':
                    csv_row['fee_dementia_from'] = str(value) if value else ''
                elif db_field == 'accepts_self_funding':
                    csv_row['accepts_self_funding'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'accepts_local_authority':
                    csv_row['accepts_local_authority'] = 'TRUE' if value else 'FALSE' if value is False else ''
                elif db_field == 'accepts_nhs_chc':
                    csv_row['accepts_nhs_chc'] = 'TRUE' if value else 'FALSE' if value is False else ''
                
                # Provider fields
                elif db_field == 'provider_id':
                    csv_row['provider_id'] = value if value else ''
                elif db_field == 'provider_name':
                    csv_row['provider_name'] = value if value else ''
            
            writer.writerow(csv_row)
    
    logger.info(f"✅ Saved {len(homes)} homes to {output_path}")


async def update_home_from_api(
    home: Dict,
    cqc_client: CQCAPIClient,
    fields_to_update: Set[str],
    dry_run: bool = False
) -> Dict[str, any]:
    """
    Update a single home from CQC API.
    
    Returns:
        Dict with update statistics: {
            'updated_fields': [...],
            'api_success': bool,
            'api_error': Optional[str]
        }
    """
    location_id = home.get('location_id') or home.get('cqc_location_id')
    
    if not location_id:
        return {
            'updated_fields': [],
            'api_success': False,
            'api_error': 'No location_id'
        }
    
    try:
        # Get location data from API
        api_data = await cqc_client.get_location(location_id)
        
        updated_fields = []
        updates = {}
        
        # Extract and update fields
        if any(f.startswith('cqc_rating_') for f in fields_to_update):
            ratings = extract_ratings_from_api(api_data)
            for field, value in ratings.items():
                if field in fields_to_update:
                    # Check if field is empty or None
                    current_value = home.get(field)
                    is_empty = (
                        current_value is None or 
                        current_value == '' or 
                        str(current_value).strip().upper() in ['NONE', 'NULL', 'N/A', 'NA']
                    )
                    
                    # Update if empty and API has value
                    if is_empty and value:
                        updates[field] = value
                        updated_fields.append(field)
                    elif not is_empty and value and value != current_value:
                        # Also update if value changed (optional - for re-sync)
                        updates[field] = value
                        updated_fields.append(field)
        
        if any(f in ['latitude', 'longitude', 'postcode', 'city', 'local_authority'] for f in fields_to_update):
            location = extract_location_from_api(api_data)
            for field, value in location.items():
                if field in fields_to_update and (not home.get(field) or home.get(field) == ''):
                    updates[field] = value
                    updated_fields.append(field)
        
        if any(f.startswith('serves_') for f in fields_to_update):
            service_bands = extract_service_user_bands_from_api(api_data)
            for field, value in service_bands.items():
                if field in fields_to_update and (not home.get(field) or home.get(field) is None):
                    updates[field] = value
                    updated_fields.append(field)
        
        # Extract and update regulated activities
        if any(f.startswith('regulated_activity_') for f in fields_to_update):
            regulated_activities = extract_regulated_activities_from_api(api_data)
            for field, value in regulated_activities.items():
                if field in fields_to_update:
                    # For regulated activities, update if current value is FALSE or empty
                    current_value = home.get(field)
                    is_false_or_empty = (
                        current_value is None or 
                        current_value == '' or 
                        str(current_value).strip().upper() in ['FALSE', 'F', '0', 'NONE', 'NULL', 'N/A', 'NA']
                    )
                    
                    # Update if FALSE/empty and API says TRUE
                    if is_false_or_empty and value:
                        updates[field] = 'TRUE' if value else 'FALSE'
                        updated_fields.append(field)
                    elif not is_false_or_empty and value and str(current_value).upper() != 'TRUE':
                        # Also update if was FALSE but should be TRUE
                        updates[field] = 'TRUE'
                        updated_fields.append(field)
        
        if any(f.startswith('care_') for f in fields_to_update):
            care_types = extract_care_types_from_api(api_data)
            for field, value in care_types.items():
                if field in fields_to_update and (not home.get(field) or home.get(field) is None):
                    updates[field] = value
                    updated_fields.append(field)
        
        if 'cqc_last_inspection_date' in fields_to_update:
            inspection_date = extract_inspection_date_from_api(api_data)
            if inspection_date and (not home.get('cqc_last_inspection_date') or home.get('cqc_last_inspection_date') == ''):
                updates['cqc_last_inspection_date'] = inspection_date
                updated_fields.append('cqc_last_inspection_date')
        
        if 'beds_total' in fields_to_update:
            beds = extract_beds_from_api(api_data)
            if beds and (not home.get('beds_total') or home.get('beds_total') == 0):
                updates['beds_total'] = beds
                updated_fields.append('beds_total')
        
        # Extract and update facilities (if available in API)
        facilities_fields = ['wheelchair_access', 'parking_onsite', 'ensuite_rooms', 'secure_garden', 'wifi_available']
        if any(f in fields_to_update for f in facilities_fields):
            facilities = extract_facilities_from_api(api_data)
            for field, value in facilities.items():
                if field in fields_to_update and value is not None:
                    # Only update if field is empty and API has value
                    current_value = home.get(field)
                    is_empty = (
                        current_value is None or 
                        current_value == '' or 
                        str(current_value).strip().upper() in ['FALSE', 'F', '0', 'NONE', 'NULL', 'N/A', 'NA']
                    )
                    if is_empty and value:
                        updates[field] = value
                        updated_fields.append(field)
        
        # Extract and update financial data (if available in API)
        financial_fields = ['fee_residential_from', 'fee_nursing_from', 'fee_dementia_from', 
                           'accepts_self_funding', 'accepts_local_authority', 'accepts_nhs_chc']
        if any(f in fields_to_update for f in financial_fields):
            financial = extract_financial_from_api(api_data)
            for field, value in financial.items():
                if field in fields_to_update and value is not None:
                    # Only update if field is empty and API has value
                    current_value = home.get(field)
                    is_empty = (
                        current_value is None or 
                        current_value == '' or 
                        (isinstance(current_value, (int, float)) and current_value == 0)
                    )
                    if is_empty and value:
                        updates[field] = value
                        updated_fields.append(field)
        
        # Apply updates
        if not dry_run and updates:
            home.update(updates)
        
        return {
            'updated_fields': updated_fields,
            'api_success': True,
            'api_error': None
        }
    
    except Exception as e:
        logger.error(f"Error updating home {location_id}: {e}")
        return {
            'updated_fields': [],
            'api_success': False,
            'api_error': str(e)
        }


async def update_cqc_database(
    csv_path: Path,
    fields_to_update: Set[str],
    limit: Optional[int] = None,
    dry_run: bool = False,
    output_path: Optional[Path] = None,
    batch_size: int = 30,
    delay_between_batches: float = 1.0
) -> Dict[str, any]:
    """
    Update CQC database from API.
    
    IMPORTANT: This function now updates the ORIGINAL file in place.
    - Loads ALL homes from original CSV
    - Updates only homes that need updates (based on limit if specified)
    - Saves ALL homes back to original file
    - Creates backup before updating
    
    Args:
        csv_path: Path to CQC CSV file
        fields_to_update: Set of field names to update
        limit: Maximum number of homes to UPDATE via API (None = all). Note: ALL homes are saved.
        dry_run: If True, only analyze without updating
        output_path: Path to output CSV (None = update original file in place)
        batch_size: Number of homes to process in parallel
        delay_between_batches: Delay between batches (seconds)
    
    Returns:
        Dict with statistics
    """
    logger.info("=" * 80)
    logger.info("CQC DATABASE UPDATE SCRIPT")
    logger.info("=" * 80)
    logger.info(f"CSV Path: {csv_path}")
    logger.info(f"Fields to update: {', '.join(sorted(fields_to_update))}")
    logger.info(f"Limit: {limit or 'All homes will be updated via API'}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("=" * 80)
    
    # Load ALL CQC homes from original CSV
    logger.info("Loading ALL homes from original CSV...")
    all_homes = load_cqc_homes(str(csv_path))
    logger.info(f"Loaded {len(all_homes)} total homes from CSV")
    
    # Also load original CSV rows to preserve all fields
    logger.info("Loading original CSV structure...")
    original_csv_rows = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                location_id = row.get('location_id', '').strip()
                if location_id:
                    original_csv_rows[location_id] = row
        logger.info(f"Loaded {len(original_csv_rows)} original CSV rows")
    except Exception as e:
        logger.warning(f"Could not load original CSV rows: {e}")
        original_csv_rows = {}
    
    # Determine which homes to update via API
    # If limit is specified, prioritize homes with empty fields
    homes_to_update = all_homes.copy()  # Start with all homes
    
    if limit:
        # Separate homes with empty fields and homes with data
        empty_homes = []
        filled_homes = []
        
        for home in all_homes:
            has_empty_field = False
            for field in fields_to_update:
                current_value = home.get(field)
                is_empty = (
                    current_value is None or 
                    current_value == '' or 
                    str(current_value).strip().upper() in ['NONE', 'NULL', 'N/A', 'NA', 'FALSE', 'F', '0']
                )
                if is_empty:
                    has_empty_field = True
                    break
            
            if has_empty_field:
                empty_homes.append(home)
            else:
                filled_homes.append(home)
        
        # Prioritize empty homes, then fill with filled homes if needed
        homes_to_update = (empty_homes + filled_homes)[:limit]
        logger.info(f"Selected {len(empty_homes)} homes with empty fields, {len(filled_homes)} homes with data")
        logger.info(f"Will update {len(homes_to_update)} homes via API (out of {len(all_homes)} total)")
    else:
        logger.info(f"Will update ALL {len(homes_to_update)} homes via API")
    
    # Create a mapping of location_id to home for quick lookup
    homes_by_id = {home.get('location_id') or home.get('cqc_location_id'): home for home in all_homes}
    homes_to_update_ids = {home.get('location_id') or home.get('cqc_location_id') for home in homes_to_update}
    
    # Load API credentials
    logger.info("Loading API credentials...")
    try:
        credentials = get_credentials()
        cqc_primary = credentials.cqc.primary_subscription_key if credentials.cqc else None
        cqc_secondary = credentials.cqc.secondary_subscription_key if credentials.cqc else None
    except Exception as e:
        logger.warning(f"Could not load API credentials: {e}")
        cqc_primary = None
        cqc_secondary = None
    
    # Initialize CQC client
    cqc_client = CQCAPIClient(
        primary_subscription_key=cqc_primary,
        secondary_subscription_key=cqc_secondary
    )
    
    # Statistics
    stats = {
        'total_homes': len(all_homes),
        'homes_to_update': len(homes_to_update),
        'processed': 0,
        'updated': 0,
        'api_success': 0,
        'api_errors': 0,
        'fields_updated': {},
        'errors': []
    }
    
    # Process homes in batches
    logger.info(f"\nProcessing {len(homes_to_update)} homes via API in batches of {batch_size}...")
    
    for i in range(0, len(homes_to_update), batch_size):
        batch = homes_to_update[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(homes_to_update) + batch_size - 1) // batch_size
        
        logger.info(f"\nBatch {batch_num}/{total_batches} ({len(batch)} homes)...")
        
        # Process batch in parallel
        tasks = [
            update_home_from_api(home, cqc_client, fields_to_update, dry_run)
            for home in batch
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and update homes in all_homes list
        for home, result in zip(batch, results):
            stats['processed'] += 1
            
            # Get location_id for lookup
            location_id = home.get('location_id') or home.get('cqc_location_id')
            
            if isinstance(result, Exception):
                stats['api_errors'] += 1
                stats['errors'].append({
                    'location_id': location_id,
                    'error': str(result)
                })
                logger.error(f"Error processing {location_id}: {result}")
                continue
            
            if result['api_success']:
                stats['api_success'] += 1
            
            if result['updated_fields']:
                stats['updated'] += 1
                for field in result['updated_fields']:
                    stats['fields_updated'][field] = stats['fields_updated'].get(field, 0) + 1
                logger.info(f"  ✅ {location_id}: Updated {len(result['updated_fields'])} fields")
                
                # Update the home in all_homes list (home is already updated in-place by update_home_from_api)
                # But we need to make sure the update is reflected in all_homes
                if location_id in homes_by_id:
                    # The home object is already updated in-place, so all_homes is already updated
                    pass
            else:
                logger.debug(f"  ⏭️  {location_id}: No updates needed")
        
        # Delay between batches (rate limiting)
        if i + batch_size < len(homes_to_update):
            await asyncio.sleep(delay_between_batches)
    
    # Close client
    await cqc_client.close()
    
    # Save updated CSV if not dry run
    if not dry_run:
        # Determine output path
        if output_path:
            # User specified output path
            output_file = Path(output_path)
        else:
            # Update original file in place
            output_file = csv_path
        
        # Create backup before updating
        if output_file == csv_path:
            from datetime import datetime
            import shutil
            
            csv_dir = csv_path.parent
            csv_stem = csv_path.stem
            csv_suffix = csv_path.suffix
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = csv_dir / f"{csv_stem}_BACKUP_{timestamp}{csv_suffix}"
            
            logger.info(f"\nCreating backup: {backup_file}...")
            try:
                shutil.copy2(csv_path, backup_file)
                logger.info(f"✅ Backup created: {backup_file}")
            except Exception as e:
                logger.error(f"❌ Failed to create backup: {e}")
                logger.warning("Continuing without backup...")
        
        logger.info(f"\nSaving updated CSV to {output_file}...")
        logger.info(f"Original CSV: {csv_path}")
        logger.info(f"Output CSV: {output_file}")
        logger.info(f"Total homes to save: {len(all_homes)}")
        logger.info(f"Homes updated via API: {stats['updated']}")
        
        # Save ALL homes to CSV (not just updated ones)
        try:
            save_homes_to_csv(all_homes, output_file, csv_path, original_csv_rows)
            logger.info(f"✅ Successfully saved {len(all_homes)} homes to {output_file}")
            if output_file == csv_path:
                logger.info(f"✅ Original file updated in place")
        except Exception as e:
            logger.error(f"❌ Failed to save CSV: {e}")
            import traceback
            traceback.print_exc()
            logger.warning("Updates are in memory only - CSV not saved")
    
    # Print statistics
    logger.info("\n" + "=" * 80)
    logger.info("UPDATE STATISTICS")
    logger.info("=" * 80)
    logger.info(f"Total homes in CSV: {stats['total_homes']}")
    logger.info(f"Homes updated via API: {stats['homes_to_update']}")
    logger.info(f"Processed: {stats['processed']}")
    logger.info(f"Updated: {stats['updated']}")
    logger.info(f"API success: {stats['api_success']}")
    logger.info(f"API errors: {stats['api_errors']}")
    logger.info(f"\nFields updated:")
    for field, count in sorted(stats['fields_updated'].items()):
        logger.info(f"  {field}: {count}")
    
    if stats['errors']:
        logger.warning(f"\nErrors ({len(stats['errors'])}):")
        for error in stats['errors'][:10]:  # Show first 10
            logger.warning(f"  {error['location_id']}: {error['error']}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Update complete!")
    if not dry_run:
        logger.info(f"All {stats['total_homes']} homes saved to CSV")
    logger.info("=" * 80)
    
    return stats


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Update CQC database from API'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only analyze, do not update'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Update only first N homes (for testing)'
    )
    parser.add_argument(
        '--fields',
        type=str,
        help='Comma-separated list of fields to update (default: all)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV path (default: update in place)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=30,
        help='Batch size for parallel processing (default: 30)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between batches in seconds (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    # Determine fields to update
    if args.fields:
        fields_to_update = set(f.strip() for f in args.fields.split(','))
        # Validate fields
        invalid_fields = fields_to_update - UPDATABLE_FIELDS
        if invalid_fields:
            logger.error(f"Invalid fields: {invalid_fields}")
            logger.error(f"Valid fields: {', '.join(sorted(UPDATABLE_FIELDS))}")
            sys.exit(1)
    else:
        fields_to_update = UPDATABLE_FIELDS
    
    # Find CSV file
    backend_dir = Path(__file__).parent.parent
    possible_paths = [
        backend_dir.parent.parent.parent.parent / "documents" / "report-algorithms" / "cqc_carehomes_master_full_data_rows.csv",
        backend_dir.parent.parent.parent / "documents" / "report-algorithms" / "cqc_carehomes_master_full_data_rows.csv",
        Path("/Users/alexander/Documents/Products/RCH-admin-playground/documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv"),
    ]
    
    csv_path = None
    for path in possible_paths:
        if path.exists():
            csv_path = path
            break
    
    if not csv_path:
        logger.error("CQC CSV file not found!")
        logger.error(f"Tried paths: {possible_paths}")
        sys.exit(1)
    
    # Output path
    if args.output:
        # User specified output path
        output_path = Path(args.output)
        # If relative path, make it relative to original CSV directory
        if not output_path.is_absolute():
            output_path = csv_path.parent / output_path
    else:
        # Default: update original file in place
        output_path = None  # Will update original file in update_cqc_database function
    
    # Run update
    try:
        stats = await update_cqc_database(
            csv_path=csv_path,
            fields_to_update=fields_to_update,
            limit=args.limit,
            dry_run=args.dry_run,
            output_path=output_path,
            batch_size=args.batch_size,
            delay_between_batches=args.delay
        )
        
        logger.info("\n✅ Update completed successfully!")
        sys.exit(0)
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

