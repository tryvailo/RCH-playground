#!/usr/bin/env python3
"""
Test Matching with Mock Data (if backend unavailable)
Tests all questionnaires using mock matching logic
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import sys

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "free_report_viewer" / "services"))

QUESTIONNAIRES_DIR = project_root / "api-testing-suite" / "frontend" / "public" / "sample_questionnaires"
RESULTS_FILE = Path(__file__).parent / "matching_test_results_mock.json"


def load_questionnaires() -> List[Dict[str, Any]]:
    """Load all questionnaire JSON files"""
    questionnaires = []
    for i in range(1, 7):
        file_path = QUESTIONNAIRES_DIR / f"questionnaire_{i}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_file'] = f"questionnaire_{i}.json"
                questionnaires.append(data)
    return questionnaires


def test_with_mock_matching(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Test questionnaire with mock matching logic"""
    file_name = questionnaire.get('_file', 'unknown')
    postcode = questionnaire.get('postcode', '')
    care_type = questionnaire.get('care_type', 'residential')
    budget = questionnaire.get('budget')
    
    print(f"\n{'='*80}")
    print(f"📋 Testing: {file_name}")
    print(f"   Postcode: {postcode}")
    print(f"   Care Type: {care_type}")
    print(f"   Budget: £{budget}/week" if budget else "   Budget: Not specified")
    print(f"{'='*80}")
    
    # Mock matching - simulate different results based on postcode
    postcode_prefix = postcode.upper().split()[0]
    
    # Generate mock homes based on postcode prefix
    mock_homes = {
        'safe_bet': {
            'name': f'Safe Care Home {postcode_prefix}',
            'postcode': postcode,
            'distance_km': 2.5,
            'weekly_cost': (budget or 1000) * 0.95,
            'rating': 'Good',
            'location_id': f'LOC_{postcode_prefix}_001'
        },
        'best_value': {
            'name': f'Value Care Home {postcode_prefix}',
            'postcode': postcode,
            'distance_km': 3.8,
            'weekly_cost': (budget or 1000) * 0.85,
            'rating': 'Good',
            'location_id': f'LOC_{postcode_prefix}_002'
        },
        'premium': {
            'name': f'Premium Care Home {postcode_prefix}',
            'postcode': postcode,
            'distance_km': 5.2,
            'weekly_cost': (budget or 1000) * 1.15,
            'rating': 'Outstanding',
            'location_id': f'LOC_{postcode_prefix}_003'
        }
    }
    
    print(f"✅ Mock matching: Generated 3 homes for {postcode_prefix}")
    for scenario_name, home in mock_homes.items():
        print(f"   {scenario_name.upper()}: {home['name']} - "
              f"£{home['weekly_cost']:.0f}/week, {home['distance_km']}km")
    
    return {
        'questionnaire': file_name,
        'postcode': postcode,
        'care_type': care_type,
        'budget': budget,
        'success': True,
        'total_homes': 3,
        'scenarios': mock_homes,
        'local_authority': 'Mock Authority'
    }


def main():
    """Run mock tests"""
    print(f"\n🚀 Starting Mock Matching Tests")
    print(f"   Questionnaires directory: {QUESTIONNAIRES_DIR}")
    
    questionnaires = load_questionnaires()
    print(f"\n📚 Loaded {len(questionnaires)} questionnaires")
    
    results = []
    for questionnaire in questionnaires:
        result = test_with_mock_matching(questionnaire)
        results.append(result)
    
    # Generate report
    print(f"\n{'='*100}")
    print("📊 MOCK MATCHING TEST RESULTS - COMPARISON REPORT")
    print("="*100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSummary: {len(results)}/{len(results)} questionnaires tested successfully")
    
    # Check uniqueness
    all_home_ids = set()
    duplicates = {}
    for result in results:
        scenarios = result.get('scenarios', {})
        for scenario_name, home in scenarios.items():
            home_id = home.get('location_id', '')
            if home_id:
                if home_id in all_home_ids:
                    if home_id not in duplicates:
                        duplicates[home_id] = []
                    duplicates[home_id].append(result['questionnaire'])
                else:
                    all_home_ids.add(home_id)
    
    print(f"\nTotal unique care homes: {len(all_home_ids)}")
    if duplicates:
        print(f"⚠️ Found {len(duplicates)} duplicate homes:")
        for home_id, questionnaires in duplicates.items():
            print(f"   {home_id}: {', '.join(questionnaires)}")
    else:
        print("✅ All recommendations are unique!")
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_questionnaires': len(results),
        'successful': len(results),
        'results': results,
        'note': 'Mock data - backend was unavailable'
    }
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()

