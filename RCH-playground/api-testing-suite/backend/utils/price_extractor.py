"""
Price Extractor Utilities
Common functions for extracting weekly prices from care home data
Shared between Free Report and Professional Report
"""
from typing import Any, Dict, List, Optional


def extract_weekly_price(
    home_data: Dict[str, Any],
    preferred_care_type: Optional[str] = None
) -> float:
    """
    Extract weekly price from care home data, checking multiple field names and care types
    
    This function handles various data sources:
    - Direct price fields (weeklyPrice, weekly_price, etc.)
    - Care-type specific fields (fee_residential_from, fee_nursing_from, etc.)
    - Nested weekly_costs dictionaries (from mock data)
    
    Args:
        home_data: Dictionary containing care home data
        preferred_care_type: Optional preferred care type for price lookup
            ('residential', 'nursing', 'dementia', 'respite')
    
    Returns:
        Weekly price as float, or 0.0 if not found
    
    Example:
        >>> home = {'name': 'Test Home', 'weekly_price': 1200}
        >>> extract_weekly_price(home)
        1200.0
        
        >>> home = {'fee_nursing_from': 1400}
        >>> extract_weekly_price(home, 'nursing')
        1400.0
    """
    if not home_data or not isinstance(home_data, dict):
        return 0.0
    
    # Try direct price fields first (most common)
    direct_fields = [
        'weeklyPrice',
        'weekly_price', 
        'price_weekly',
        'weekly_cost',
    ]
    
    for field in direct_fields:
        value = home_data.get(field)
        if value is not None:
            try:
                price = float(value)
                if price > 0:
                    return price
            except (ValueError, TypeError):
                continue
    
    # Try care-type specific fields (from database schema)
    if preferred_care_type:
        care_type_lower = preferred_care_type.lower()
        care_type_fields = _get_care_type_fields(care_type_lower)
        
        for field in care_type_fields:
            value = home_data.get(field)
            if value is not None:
                try:
                    price = float(value)
                    if price > 0:
                        return price
                except (ValueError, TypeError):
                    continue
    
    # Try all fee fields as fallback
    all_fee_fields = [
        'fee_residential_from',
        'fee_nursing_from',
        'fee_dementia_from',
        'fee_dementia_residential_from',
        'fee_dementia_nursing_from',
        'fee_respite_from',
    ]
    
    for field in all_fee_fields:
        value = home_data.get(field)
        if value is not None:
            try:
                price = float(value)
                if price > 0:
                    return price
            except (ValueError, TypeError):
                continue
    
    # Try weekly_costs nested dict (from mock data)
    weekly_costs = home_data.get('weekly_costs') or home_data.get('weeklyCosts')
    if isinstance(weekly_costs, dict):
        # Build lookup order
        lookup_order: List[str] = []
        if preferred_care_type:
            lookup_order.append(preferred_care_type.lower())
        lookup_order.extend(['residential', 'nursing', 'dementia', 'respite'])
        
        for care_key in lookup_order:
            if care_key in weekly_costs:
                value = weekly_costs.get(care_key)
                if value is not None:
                    try:
                        price = float(value)
                        if price > 0:
                            return price
                    except (ValueError, TypeError):
                        continue
    
    # If rawData present, attempt extraction from it (for Professional Report frontend format)
    raw_data = home_data.get('rawData')
    if raw_data and isinstance(raw_data, dict) and raw_data is not home_data:
        price = extract_weekly_price(raw_data, preferred_care_type)
        if price > 0:
            return price
    
    # Try data_json field (from SQLite database) - may contain staging CSV prices
    data_json = home_data.get('data_json')
    if data_json:
        # If data_json is a string, parse it
        if isinstance(data_json, str):
            try:
                import json
                data_json = json.loads(data_json)
            except (json.JSONDecodeError, TypeError):
                data_json = None
        
        # If data_json is a dict, extract prices from it
        if isinstance(data_json, dict):
            # Try staging CSV fields first (parsed_fee_*)
            staging_fields = {
                'residential': 'parsed_fee_residential_from',
                'nursing': 'parsed_fee_nursing_from',
                'dementia': 'parsed_fee_dementia_from',
                'respite': 'parsed_fee_respite_from',
            }
            
            # Try preferred care type first
            if preferred_care_type:
                care_type_lower = preferred_care_type.lower()
                staging_field = staging_fields.get(care_type_lower)
                if staging_field and staging_field in data_json:
                    value = data_json[staging_field]
                    if value is not None and str(value) != 'nan' and str(value) != 'None':
                        try:
                            price = float(value)
                            if price > 0:
                                return price
                        except (ValueError, TypeError):
                            pass
            
            # Try all staging fields as fallback
            for staging_field in staging_fields.values():
                if staging_field in data_json:
                    value = data_json[staging_field]
                    if value is not None and str(value) != 'nan' and str(value) != 'None':
                        try:
                            price = float(value)
                            if price > 0:
                                return price
                        except (ValueError, TypeError):
                            continue
            
            # Also try standard fee fields in data_json (in case they're stored there)
            fee_fields_in_json = [
                'fee_residential_from',
                'fee_nursing_from',
                'fee_dementia_from',
                'fee_respite_from',
            ]
            
            if preferred_care_type:
                care_type_lower = preferred_care_type.lower()
                if care_type_lower == 'residential' and 'fee_residential_from' in data_json:
                    value = data_json['fee_residential_from']
                elif care_type_lower == 'nursing' and 'fee_nursing_from' in data_json:
                    value = data_json['fee_nursing_from']
                elif care_type_lower == 'dementia' and 'fee_dementia_from' in data_json:
                    value = data_json['fee_dementia_from']
                elif care_type_lower == 'respite' and 'fee_respite_from' in data_json:
                    value = data_json['fee_respite_from']
                else:
                    value = None
                
                if value is not None and str(value) != 'nan' and str(value) != 'None':
                    try:
                        price = float(value)
                        if price > 0:
                            return price
                    except (ValueError, TypeError):
                        pass
            
            # Try all fee fields in data_json as fallback
            for field in fee_fields_in_json:
                if field in data_json:
                    value = data_json[field]
                    if value is not None and str(value) != 'nan' and str(value) != 'None':
                        try:
                            price = float(value)
                            if price > 0:
                                return price
                        except (ValueError, TypeError):
                            continue
    
    return 0.0


def _get_care_type_fields(care_type: str) -> List[str]:
    """
    Get database field names for a specific care type
    
    Args:
        care_type: Care type string (lowercase)
    
    Returns:
        List of field names to check for this care type
    """
    care_type_mapping = {
        'residential': [
            'fee_residential_from',
            'weekly_cost_residential',
        ],
        'nursing': [
            'fee_nursing_from',
            'weekly_cost_nursing',
        ],
        'dementia': [
            'fee_dementia_from',
            'fee_dementia_residential_from',
            'fee_dementia_nursing_from',
            'weekly_cost_dementia',
        ],
        'respite': [
            'fee_respite_from',
            'weekly_cost_respite',
        ],
    }
    
    return care_type_mapping.get(care_type, [])


def extract_price_range(
    home_data: Dict[str, Any],
    preferred_care_type: Optional[str] = None
) -> Dict[str, float]:
    """
    Extract price range (min/max) from care home data
    
    Args:
        home_data: Dictionary containing care home data
        preferred_care_type: Optional preferred care type
    
    Returns:
        Dictionary with 'min' and 'max' keys
    """
    base_price = extract_weekly_price(home_data, preferred_care_type)
    
    if base_price <= 0:
        return {'min': 0.0, 'max': 0.0}
    
    # Check for explicit range fields
    price_min = home_data.get('price_min') or home_data.get('weekly_price_min')
    price_max = home_data.get('price_max') or home_data.get('weekly_price_max')
    
    if price_min and price_max:
        try:
            return {
                'min': float(price_min),
                'max': float(price_max),
            }
        except (ValueError, TypeError):
            pass
    
    # Default: estimate range as ±10% of base price
    return {
        'min': round(base_price * 0.9, 2),
        'max': round(base_price * 1.1, 2),
    }
