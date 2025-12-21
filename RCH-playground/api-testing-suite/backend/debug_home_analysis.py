#!/usr/bin/env python3
"""
Debug script to analyze a single care home's matching calculation
"""
import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.professional_matching_service import ProfessionalMatchingService, ScoringWeights
from services.csv_care_homes_service import CSVCareHomesService
from routers.report_routes import generate_professional_report

async def analyze_single_home(questionnaire_path: str, home_index: int = 0):
    """Load questionnaire, generate report, and analyze first home in detail"""
    
    print("="*80)
    print("DETAILED HOME ANALYSIS")
    print("="*80)
    
    # Load questionnaire
    with open(questionnaire_path, 'r') as f:
        questionnaire = json.load(f)
    
    print(f"\n📋 Questionnaire: {questionnaire_path}")
    print(f"   Client: {questionnaire.get('client_name', 'Unknown')}")
    
    # Generate report
    print("\n🔄 Generating professional report...")
    request_data = {
        "questionnaire": questionnaire
    }
    
    try:
        response = await generate_professional_report(request_data)
        report_data = response if isinstance(response, dict) else json.loads(response.body) if hasattr(response, 'body') else response
        
        if not report_data or 'careHomes' not in report_data:
            print("❌ Error: No care homes in response")
            return
        
        care_homes = report_data.get('careHomes', [])
        if len(care_homes) == 0:
            print("❌ Error: No care homes found")
            return
        
        print(f"\n✅ Found {len(care_homes)} care homes")
        
        # Get first home
        if home_index >= len(care_homes):
            print(f"⚠️ Home index {home_index} out of range, using first home")
            home_index = 0
        
        home = care_homes[home_index]
        
        print("\n" + "="*80)
        print(f"HOME #{home_index + 1} DETAILED ANALYSIS")
        print("="*80)
        print(f"\n🏠 Home: {home.get('name', 'Unknown')}")
        print(f"   ID: {home.get('id', 'Unknown')}")
        print(f"   Match Score: {home.get('matchScore', 0)}%")
        
        # Analyze factorScores
        print("\n" + "-"*80)
        print("FACTOR SCORES (from 156-point algorithm)")
        print("-"*80)
        factor_scores = home.get('factorScores', [])
        if factor_scores:
            total_points = 0
            total_max = 0
            for factor in factor_scores:
                category = factor.get('category', 'Unknown')
                score = factor.get('score', 0)
                max_score = factor.get('maxScore', 0)
                weight = factor.get('weight', 0)
                percentage = (score / max_score * 100) if max_score > 0 else 0
                total_points += score
                total_max += max_score
                print(f"   {category:30s} | Points: {score:6.1f}/{max_score:6.1f} | {percentage:5.1f}% | Weight: {weight:.2f}")
            print(f"\n   TOTAL: {total_points:.1f}/{total_max:.1f} points ({total_points/total_max*100:.1f}%)")
        else:
            print("   ❌ No factorScores found!")
        
        # Analyze matchResult
        print("\n" + "-"*80)
        print("MATCH RESULT (category_scores)")
        print("-"*80)
        match_result = home.get('matchResult', {})
        category_scores = match_result.get('category_scores', {})
        if category_scores:
            for category, score in category_scores.items():
                print(f"   {category:30s} | Score: {score:.4f} (0-1 scale)")
        else:
            print("   ❌ No category_scores found!")
        
        # Analyze CQC Deep Dive
        print("\n" + "-"*80)
        print("CQC DEEP DIVE")
        print("-"*80)
        cqc_deep_dive = home.get('cqcDeepDive', {})
        if cqc_deep_dive:
            print(f"   Overall Rating: {cqc_deep_dive.get('overall_rating', 'N/A')}")
            print(f"   Current Rating: {cqc_deep_dive.get('current_rating', 'N/A')}")
            print(f"   Rating Trend: {cqc_deep_dive.get('rating_trend', 'N/A')}")
            
            detailed_ratings = cqc_deep_dive.get('detailed_ratings', {})
            if detailed_ratings:
                print("\n   Detailed Ratings:")
                for key, value in detailed_ratings.items():
                    if isinstance(value, dict):
                        rating = value.get('rating', 'N/A')
                        print(f"      {key:15s}: {rating}")
                    else:
                        print(f"      {key:15s}: {value}")
            else:
                print("   ⚠️ No detailed_ratings found")
            
            historical = cqc_deep_dive.get('historical_ratings', [])
            print(f"\n   Historical Ratings: {len(historical)} entries")
            
            enforcement = cqc_deep_dive.get('enforcement_actions', [])
            print(f"   Enforcement Actions: {len(enforcement)} entries")
        else:
            print("   ❌ No cqcDeepDive data found!")
        
        # Analyze Financial Stability
        print("\n" + "-"*80)
        print("FINANCIAL STABILITY")
        print("-"*80)
        financial = home.get('financialStability', {})
        if financial:
            print(f"   Data available: {bool(financial)}")
            print(f"   Keys: {list(financial.keys())[:10]}")
        else:
            print("   ❌ No financialStability data found!")
        
        # Analyze Staff Quality
        print("\n" + "-"*80)
        print("STAFF QUALITY")
        print("-"*80)
        staff = home.get('staffQuality', {})
        if staff:
            print(f"   Data available: {bool(staff)}")
            print(f"   Keys: {list(staff.keys())[:10]}")
        else:
            print("   ❌ No staffQuality data found!")
        
        # Analyze Google Places
        print("\n" + "-"*80)
        print("GOOGLE PLACES")
        print("-"*80)
        google = home.get('googlePlaces', {})
        if google:
            print(f"   Data available: {bool(google)}")
            print(f"   Keys: {list(google.keys())[:10]}")
        else:
            print("   ❌ No googlePlaces data found!")
        
        # Analyze Priorities Match
        print("\n" + "-"*80)
        print("PRIORITIES MATCH ANALYSIS")
        print("-"*80)
        
        # Extract priorities from questionnaire
        priorities = questionnaire.get('section_6_priorities', {})
        if priorities:
            priority_order = priorities.get('priority_order', [])
            priority_weights = priorities.get('priority_weights', {})
            print(f"\n   User Priorities:")
            for i, priority_id in enumerate(priority_order[:4], 1):
                weight = priority_weights.get(priority_id, 0)
                label_map = {
                    'quality_reputation': 'Quality & Reputation',
                    'cost_financial': 'Cost & Financial',
                    'location_social': 'Location & Social',
                    'comfort_amenities': 'Comfort & Amenities'
                }
                label = label_map.get(priority_id, priority_id)
                print(f"      {i}. {label} (weight: {weight})")
        else:
            print("   ⚠️ No section_6_priorities found in questionnaire")
        
        # Map priorities to algorithm categories
        priority_category_map = {
            'quality_reputation': ['cqc', 'staff'],
            'cost_financial': ['financial'],
            'location_social': ['location', 'social'],
            'comfort_amenities': ['services']
        }
        
        print(f"\n   Category Scores for Priorities:")
        if category_scores:
            for priority_id in priority_order[:4]:
                categories = priority_category_map.get(priority_id, [])
                scores = [category_scores.get(cat, 0) for cat in categories]
                avg_score = sum(scores) / len(scores) if scores else 0
                percentage = avg_score * 100
                label_map = {
                    'quality_reputation': 'Quality & Reputation',
                    'cost_financial': 'Cost & Financial',
                    'location_social': 'Location & Social',
                    'comfort_amenities': 'Comfort & Amenities'
                }
                label = label_map.get(priority_id, priority_id)
                print(f"      {label:30s}: {percentage:5.1f}% (from {categories})")
        else:
            print("      ❌ Cannot calculate - no category_scores available")
        
        # Full home data dump
        print("\n" + "="*80)
        print("FULL HOME DATA (first 50 keys)")
        print("="*80)
        home_keys = list(home.keys())[:50]
        for key in home_keys:
            value = home.get(key)
            if isinstance(value, (dict, list)):
                print(f"   {key:30s}: {type(value).__name__} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")
            else:
                print(f"   {key:30s}: {value}")
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Default to first questionnaire
    questionnaire_path = sys.argv[1] if len(sys.argv) > 1 else \
        "RCH-playground/RCH-playground/api-testing-suite/frontend/public/sample_questionnaires/professional_questionnaire_1_dementia.json"
    
    home_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    asyncio.run(analyze_single_home(questionnaire_path, home_index))

