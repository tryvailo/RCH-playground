"""
Performance Analysis for Matching Algorithm

Analyzes:
- Time complexity
- Actual execution time
- Best and worst case scenarios
- Code quality metrics
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Any
import statistics

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from services.simple_matching_service import SimpleMatchingService
from services.matching_fallback import evaluate_home_match_v2, check_field_with_fallback


def create_mock_home(index: int, has_full_data: bool = True) -> Dict[str, Any]:
    """Create a mock care home for testing"""
    home = {
        'id': f'home_{index}',
        'name': f'Test Care Home {index}',
        'latitude': 52.4862 + (index * 0.01),
        'longitude': -1.8904 + (index * 0.01),
        'distance_km': index * 2.0,
        'beds_total': 40 + (index % 20),
        'fee_residential_from': 500 + (index * 10),
        'fee_nursing_from': 800 + (index * 10),
        'wheelchair_access': index % 2 == 0,
        'care_residential': True,
        'care_nursing': index % 3 == 0,
        'care_dementia': index % 4 == 0,
        'cqc_rating_overall': ['Outstanding', 'Good', 'Requires improvement'][index % 3],
        'cqc_rating_safe': ['Outstanding', 'Good'][index % 2],
        'cqc_rating_caring': 'Good',
        'cqc_rating_effective': 'Good',
        'cqc_rating_responsive': 'Good',
        'cqc_rating_well_led': 'Good',
    }
    
    if has_full_data:
        home.update({
            'serves_dementia_band': index % 2 == 0,
            'serves_mental_health': index % 3 == 0,
            'serves_physical_disabilities': index % 2 == 0,
            'secure_garden': index % 2 == 0,
            'last_inspection_date': '2023-01-01',
        })
    else:
        # Sparse data (many NULLs)
        home.update({
            'serves_dementia_band': None if index % 3 == 0 else (index % 2 == 0),
            'serves_mental_health': None if index % 4 == 0 else (index % 3 == 0),
            'serves_physical_disabilities': None,
            'secure_garden': None,
            'last_inspection_date': None,
        })
    
    return home


def create_mock_questionnaire(complexity: str = 'medium') -> Dict[str, Any]:
    """Create a mock questionnaire with varying complexity"""
    base = {
        'section_1_contact_emergency': {
            'q1_names': 'Test Client',
            'q2_email': 'test@example.com',
            'q3_phone': '+44 123 456789'
        },
        'section_2_location_budget': {
            'q5_preferred_city': 'Birmingham',
            'q6_max_distance': 'within_15km',
            'q7_budget': '5000_7000_local',
            'user_latitude': 52.4862,
            'user_longitude': -1.8904
        },
        'section_3_medical_needs': {
            'q8_care_types': ['specialised_dementia'],
            'q9_medical_conditions': ['dementia_alzheimers'],
            'q10_mobility_level': 'uses_walking_aid',
            'q11_medication_management': 'simple_routine',
            'q12_special_equipment': ['no_special_equipment'],
            'q13_age_range': '85_94'
        },
        'section_4_safety_special_needs': {
            'q13_fall_history': '1_2_no_serious_injuries',
            'q14_allergies': ['no_allergies'],
            'q15_dietary_requirements': ['no_special_requirements'],
            'q16_behavioral_concerns': []
        },
        'section_5_timeline': {
            'q17_placement_timeline': 'next_month'
        }
    }
    
    if complexity == 'simple':
        # Minimal requirements
        base['section_3_medical_needs']['q9_medical_conditions'] = ['no_serious_medical']
        base['section_3_medical_needs']['q8_care_types'] = ['general_residential']
    elif complexity == 'complex':
        # Many requirements
        base['section_3_medical_needs']['q9_medical_conditions'] = [
            'dementia_alzheimers',
            'parkinsons',
            'mobility_problems',
            'visual_impairment'
        ]
        base['section_4_safety_special_needs']['q16_behavioral_concerns'] = [
            'wandering_risk',
            'anxiety'
        ]
        base['section_3_medical_needs']['q10_mobility_level'] = 'wheelchair_user'
        base['section_3_medical_needs']['q12_special_equipment'] = ['hospital_bed', 'hoist_lift']
    
    return base


def benchmark_prefiltering(homes: List[Dict], questionnaire: Dict) -> Dict[str, Any]:
    """Benchmark pre-filtering performance"""
    times = []
    disqualified_count = 0
    
    for home in homes:
        start = time.perf_counter()
        
        medical_needs = questionnaire.get('section_3_medical_needs', {}) or {}
        safety_needs = questionnaire.get('section_4_safety_special_needs', {}) or {}
        
        required_care = medical_needs.get('q8_care_types', []) or []
        medical_conditions = medical_needs.get('q9_medical_conditions', []) or []
        mobility_level = medical_needs.get('q10_mobility_level', '') or ''
        behavioral_concerns = safety_needs.get('q16_behavioral_concerns', []) or []
        
        result = evaluate_home_match_v2(
            home=home,
            required_care=required_care,
            conditions=medical_conditions,
            mobility=mobility_level,
            behavioral=behavioral_concerns
        )
        
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        
        if result['status'] == 'disqualified':
            disqualified_count += 1
    
    return {
        'total_homes': len(homes),
        'disqualified': disqualified_count,
        'avg_time_ms': statistics.mean(times) * 1000,
        'min_time_ms': min(times) * 1000,
        'max_time_ms': max(times) * 1000,
        'total_time_ms': sum(times) * 1000,
        'median_time_ms': statistics.median(times) * 1000
    }


def benchmark_scoring(homes: List[Dict], questionnaire: Dict) -> Dict[str, Any]:
    """Benchmark scoring performance"""
    service = SimpleMatchingService()
    weights, _ = service.calculate_dynamic_weights(questionnaire)
    
    times = []
    
    for home in homes:
        start = time.perf_counter()
        
        enriched_data = {
            'cqc_detailed': {
                'overall_rating': home.get('cqc_rating_overall'),
                'safe_rating': home.get('cqc_rating_safe'),
                'caring_rating': home.get('cqc_rating_caring'),
                'effective_rating': home.get('cqc_rating_effective'),
                'responsive_rating': home.get('cqc_rating_responsive'),
                'well_led_rating': home.get('cqc_rating_well_led'),
            }
        }
        
        result = service.calculate_100_point_match(
            home=home,
            user_profile=questionnaire,
            enriched_data=enriched_data,
            weights=weights
        )
        
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        'total_homes': len(homes),
        'avg_time_ms': statistics.mean(times) * 1000,
        'min_time_ms': min(times) * 1000,
        'max_time_ms': max(times) * 1000,
        'total_time_ms': sum(times) * 1000,
        'median_time_ms': statistics.median(times) * 1000
    }


def benchmark_top5_selection(scored_homes: List[Dict]) -> Dict[str, Any]:
    """Benchmark top 5 selection"""
    start = time.perf_counter()
    
    # Sort by match score
    scored_homes.sort(key=lambda x: x.get('matchScore', 0), reverse=True)
    top_5 = scored_homes[:5]
    
    elapsed = time.perf_counter() - start
    
    return {
        'total_homes': len(scored_homes),
        'top_5_count': len(top_5),
        'time_ms': elapsed * 1000
    }


def run_performance_analysis():
    """Run complete performance analysis"""
    print("=" * 80)
    print("PERFORMANCE ANALYSIS: Matching Algorithm")
    print("=" * 80)
    
    scenarios = [
        ('best_case', 20, True, 'simple'),
        ('average_case', 50, True, 'medium'),
        ('worst_case', 100, False, 'complex'),
    ]
    
    results = {}
    
    for scenario_name, num_homes, has_full_data, complexity in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario_name.upper()}")
        print(f"  Homes: {num_homes}")
        print(f"  Data completeness: {'Full' if has_full_data else 'Sparse (many NULLs)'}")
        print(f"  Complexity: {complexity}")
        print(f"{'='*80}")
        
        # Create test data
        homes = [create_mock_home(i, has_full_data) for i in range(num_homes)]
        questionnaire = create_mock_questionnaire(complexity)
        
        # Benchmark pre-filtering
        print("\n1. PRE-FILTERING (evaluate_home_match_v2)")
        prefilter_results = benchmark_prefiltering(homes, questionnaire)
        print(f"   Total homes: {prefilter_results['total_homes']}")
        print(f"   Disqualified: {prefilter_results['disqualified']}")
        print(f"   Avg time per home: {prefilter_results['avg_time_ms']:.2f} ms")
        print(f"   Total time: {prefilter_results['total_time_ms']:.2f} ms ({prefilter_results['total_time_ms']/1000:.3f} s)")
        
        # Filter homes (simulate pre-filtering)
        filtered_homes = [h for h in homes if h.get('_prefilter_match_result', {}).get('status') != 'disqualified']
        if not filtered_homes:
            filtered_homes = homes  # Keep all if none disqualified
        
        # Benchmark scoring
        print("\n2. SCORING (calculate_100_point_match)")
        scoring_results = benchmark_scoring(filtered_homes, questionnaire)
        print(f"   Total homes scored: {scoring_results['total_homes']}")
        print(f"   Avg time per home: {scoring_results['avg_time_ms']:.2f} ms")
        print(f"   Total time: {scoring_results['total_time_ms']:.2f} ms ({scoring_results['total_time_ms']/1000:.3f} s)")
        
        # Create scored homes list
        scored_homes = [
            {
                'home': home,
                'matchScore': 50 + (i % 50),  # Mock scores
            }
            for i, home in enumerate(filtered_homes)
        ]
        
        # Benchmark top 5 selection
        print("\n3. TOP 5 SELECTION")
        top5_results = benchmark_top5_selection(scored_homes)
        print(f"   Total homes: {top5_results['total_homes']}")
        print(f"   Time: {top5_results['time_ms']:.2f} ms")
        
        # Total time
        total_time_ms = (
            prefilter_results['total_time_ms'] +
            scoring_results['total_time_ms'] +
            top5_results['time_ms']
        )
        
        print(f"\n📊 TOTAL TIME: {total_time_ms:.2f} ms ({total_time_ms/1000:.3f} s)")
        
        results[scenario_name] = {
            'prefilter': prefilter_results,
            'scoring': scoring_results,
            'top5': top5_results,
            'total_time_ms': total_time_ms,
            'total_time_s': total_time_ms / 1000
        }
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"{'Scenario':<20} {'Homes':<10} {'Total Time (s)':<15} {'Time per Home (ms)':<20}")
    print("-" * 80)
    
    for scenario_name, result in results.items():
        num_homes = result['prefilter']['total_homes']
        total_time_s = result['total_time_s']
        time_per_home = result['total_time_ms'] / num_homes
        
        print(f"{scenario_name:<20} {num_homes:<10} {total_time_s:<15.3f} {time_per_home:<20.2f}")
    
    return results


if __name__ == '__main__':
    results = run_performance_analysis()

