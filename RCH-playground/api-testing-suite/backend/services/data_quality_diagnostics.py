"""
Data Quality Diagnostics Service

Provides diagnostics for matching data quality, including:
- Field coverage analysis
- NULL rates for critical fields
- Proxy field usage statistics
- Service User Bands availability
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict


# Critical fields for matching
CRITICAL_FIELDS = {
    'service_user_bands': [
        'serves_dementia_band',
        'serves_older_people',
        'serves_mental_health',
        'serves_physical_disabilities',
        'serves_sensory_impairments',
        'serves_learning_disabilities',
        'serves_younger_adults',
        'serves_whole_population'
    ],
    'cqc_ratings': [
        'cqc_rating_overall',
        'cqc_rating_safe',
        'cqc_rating_caring',
        'cqc_rating_effective',
        'cqc_rating_responsive',
        'cqc_rating_well_led',
        'last_inspection_date'
    ],
    'amenities': [
        'wheelchair_access',
        'secure_garden',
        'ensuite_rooms',
        'parking_onsite'
    ],
    'care_types': [
        'care_dementia',
        'care_nursing',
        'care_residential',
        'care_respite'
    ],
    'licenses': [
        'has_nursing_care_license',
        'has_personal_care_license'
    ]
}


def diagnose_matching_data(
    homes: List[Dict[str, Any]],
    home_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Diagnose data quality for care homes used in matching.
    
    Args:
        homes: List of care home dictionaries
        home_ids: Optional list of specific home IDs to check
        
    Returns:
        Dictionary with data quality metrics
    """
    if home_ids:
        # Filter homes by IDs if provided
        homes = [h for h in homes if h.get('id') in home_ids or h.get('cqc_location_id') in home_ids]
    
    if not homes:
        return {
            'error': 'No homes provided',
            'homes_checked': 0
        }
    
    total_homes = len(homes)
    results = {
        'homes_checked': total_homes,
        'field_coverage': {},
        'null_rates': {},
        'category_summary': {},
        'proxy_opportunities': {}
    }
    
    # Analyze each category of fields
    for category, fields in CRITICAL_FIELDS.items():
        category_stats = {
            'total_fields': len(fields),
            'fields_analyzed': 0,
            'avg_null_rate': 0.0,
            'fields': {}
        }
        
        null_rates = []
        
        for field in fields:
            values = [home.get(field) for home in homes]
            
            true_count = sum(1 for v in values if v is True)
            false_count = sum(1 for v in values if v is False)
            null_count = sum(1 for v in values if v is None)
            other_count = total_homes - (true_count + false_count + null_count)
            
            null_rate = round(null_count / total_homes * 100, 1) if total_homes > 0 else 0.0
            null_rates.append(null_rate)
            
            field_stats = {
                'true': true_count,
                'false': false_count,
                'null': null_count,
                'other': other_count,
                'null_rate': null_rate,
                'coverage': round((true_count + false_count) / total_homes * 100, 1) if total_homes > 0 else 0.0
            }
            
            category_stats['fields'][field] = field_stats
            category_stats['fields_analyzed'] += 1
            
            # Store in main results
            results['field_coverage'][field] = field_stats
            results['null_rates'][field] = null_rate
        
        category_stats['avg_null_rate'] = round(sum(null_rates) / len(null_rates), 1) if null_rates else 0.0
        results['category_summary'][category] = category_stats
    
    # Identify proxy opportunities (fields with high NULL rates that have proxies)
    from .matching_fallback_config import FIELD_PROXY_CONFIG
    
    proxy_opportunities = []
    for field, null_rate in results['null_rates'].items():
        if null_rate > 50.0:  # More than 50% NULL
            config = FIELD_PROXY_CONFIG.get(field, {})
            proxies = config.get('proxies', [])
            if proxies:
                proxy_opportunities.append({
                    'field': field,
                    'null_rate': null_rate,
                    'available_proxies': [p['field'] for p in proxies],
                    'proxy_count': len(proxies)
                })
    
    results['proxy_opportunities'] = proxy_opportunities
    
    # Overall data quality score
    all_null_rates = list(results['null_rates'].values())
    avg_null_rate = sum(all_null_rates) / len(all_null_rates) if all_null_rates else 0.0
    data_quality_score = max(0, 100 - avg_null_rate)  # Inverse: lower NULL = higher quality
    
    results['overall'] = {
        'data_quality_score': round(data_quality_score, 1),
        'avg_null_rate': round(avg_null_rate, 1),
        'total_fields_analyzed': len(results['field_coverage']),
        'high_null_fields': len([r for r in all_null_rates if r > 50.0])
    }
    
    return results


def analyze_fallback_usage(
    homes: List[Dict[str, Any]],
    questionnaire: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze fallback logic usage for a set of homes and questionnaire.
    
    Args:
        homes: List of care home dictionaries
        questionnaire: Professional questionnaire
        
    Returns:
        Dictionary with fallback usage statistics
    """
    from .matching_fallback import evaluate_home_match_v2
    
    medical_needs = questionnaire.get('section_3_medical_needs', {}) or {}
    safety_needs = questionnaire.get('section_4_safety_special_needs', {}) or {}
    
    required_care = medical_needs.get('q8_care_types', []) or []
    medical_conditions = medical_needs.get('q9_medical_conditions', []) or []
    mobility_level = medical_needs.get('q10_mobility_level', '') or ''
    behavioral_concerns = safety_needs.get('q16_behavioral_concerns', []) or []
    
    results = {
        'total_homes': len(homes),
        'match_results': {
            'match': 0,
            'partial': 0,
            'uncertain': 0,
            'disqualified': 0
        },
        'data_quality': {
            'direct_matches': 0,
            'proxy_matches': 0,
            'unknowns': 0
        },
        'field_usage': defaultdict(lambda: {'direct': 0, 'proxy': 0, 'unknown': 0})
    }
    
    for home in homes:
        match_result = evaluate_home_match_v2(
            home=home,
            required_care=required_care,
            conditions=medical_conditions,
            mobility=mobility_level,
            behavioral=behavioral_concerns
        )
        
        status = match_result.get('status', 'unknown')
        results['match_results'][status] = results['match_results'].get(status, 0) + 1
        
        # Aggregate data quality
        dq = match_result.get('data_quality', {})
        results['data_quality']['direct_matches'] += dq.get('direct_matches', 0)
        results['data_quality']['proxy_matches'] += dq.get('proxy_matches', 0)
        results['data_quality']['unknowns'] += dq.get('unknowns', 0)
        
        # Track field usage from checks
        checks = match_result.get('checks', [])
        for check in checks:
            if isinstance(check, dict):
                field = check.get('field', 'unknown')
                result_type = check.get('result', 'unknown')
                
                if result_type == 'match':
                    results['field_usage'][field]['direct'] += 1
                elif result_type in ['proxy_match', 'proxy_likely']:
                    results['field_usage'][field]['proxy'] += 1
                elif result_type == 'unknown':
                    results['field_usage'][field]['unknown'] += 1
    
    # Calculate ratios
    total_checks = (
        results['data_quality']['direct_matches'] +
        results['data_quality']['proxy_matches'] +
        results['data_quality']['unknowns']
    )
    
    if total_checks > 0:
        results['data_quality']['unknown_ratio'] = round(
            results['data_quality']['unknowns'] / total_checks, 2
        )
        results['data_quality']['proxy_ratio'] = round(
            results['data_quality']['proxy_matches'] / total_checks, 2
        )
    else:
        results['data_quality']['unknown_ratio'] = 0.0
        results['data_quality']['proxy_ratio'] = 0.0
    
    # Convert defaultdict to regular dict
    results['field_usage'] = dict(results['field_usage'])
    
    return results

