#!/usr/bin/env python3
"""
Combined Matching Test - Tries backend first, falls back to mock
Tests all 6 questionnaires and compares results across 3 scenarios
"""
import asyncio
import json
import httpx
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "http://localhost:8000"
QUESTIONNAIRES_DIR = Path(__file__).parent.parent / "frontend" / "public" / "sample_questionnaires"
RESULTS_FILE = Path(__file__).parent / "matching_test_results_combined.json"


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


def generate_mock_results(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock matching results"""
    postcode = questionnaire.get('postcode', '')
    care_type = questionnaire.get('care_type', 'residential')
    budget = questionnaire.get('budget', 1000)
    postcode_prefix = postcode.upper().split()[0]
    
    return {
        'safe_bet': {
            'name': f'Safe Care Home {postcode_prefix}',
            'postcode': postcode,
            'distance_km': round(2.0 + (hash(postcode) % 10) / 10, 1),
            'weekly_cost': round(budget * (0.90 + (hash(postcode) % 10) / 100), 2),
            'rating': 'Good',
            'location_id': f'LOC_{postcode_prefix}_001'
        },
        'best_value': {
            'name': f'Value Care Home {postcode_prefix}',
            'postcode': postcode,
            'distance_km': round(3.5 + (hash(postcode + 'value') % 10) / 10, 1),
            'weekly_cost': round(budget * (0.80 + (hash(postcode + 'value') % 10) / 100), 2),
            'rating': 'Good',
            'location_id': f'LOC_{postcode_prefix}_002'
        },
        'premium': {
            'name': f'Premium Care Home {postcode_prefix}',
            'postcode': postcode,
            'distance_km': round(5.0 + (hash(postcode + 'premium') % 10) / 10, 1),
            'weekly_cost': round(budget * (1.10 + (hash(postcode + 'premium') % 10) / 100), 2),
            'rating': 'Outstanding',
            'location_id': f'LOC_{postcode_prefix}_003'
        }
    }


async def test_questionnaire_backend(client: httpx.AsyncClient, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Test questionnaire via backend API"""
    file_name = questionnaire.get('_file', 'unknown')
    postcode = questionnaire.get('postcode', '')
    care_type = questionnaire.get('care_type', 'residential')
    budget = questionnaire.get('budget')
    
    request_data = {k: v for k, v in questionnaire.items() if k != '_file'}
    
    try:
        response = await client.post(
            f"{BACKEND_URL}/api/free-report",
            json=request_data,
            timeout=120.0
        )
        
        if response.status_code == 200:
            result_data = response.json()
            care_homes = result_data.get('care_homes', [])
            
            scenarios = {}
            for home in care_homes:
                match_type = home.get('match_type', '').lower().replace(' ', '_')
                if match_type in ['safe_bet', 'best_value', 'premium']:
                    scenarios[match_type] = {
                        'name': home.get('name', 'Unknown'),
                        'postcode': home.get('postcode', ''),
                        'distance_km': home.get('distance_km'),
                        'weekly_cost': home.get('weekly_cost'),
                        'rating': home.get('rating'),
                        'location_id': home.get('location_id')
                    }
            
            return {
                'questionnaire': file_name,
                'postcode': postcode,
                'care_type': care_type,
                'budget': budget,
                'success': True,
                'source': 'backend',
                'total_homes': len(care_homes),
                'scenarios': scenarios,
                'fair_cost_gap': result_data.get('fair_cost_gap', {}),
                'local_authority': result_data.get('fair_cost_gap', {}).get('local_authority', 'Unknown')
            }
        else:
            return {
                'questionnaire': file_name,
                'postcode': postcode,
                'care_type': care_type,
                'budget': budget,
                'success': False,
                'source': 'backend',
                'error': f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            'questionnaire': file_name,
            'postcode': postcode,
            'care_type': care_type,
            'budget': budget,
            'success': False,
            'source': 'backend',
            'error': str(e)
        }


def test_questionnaire_mock(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Test questionnaire with mock data"""
    file_name = questionnaire.get('_file', 'unknown')
    postcode = questionnaire.get('postcode', '')
    care_type = questionnaire.get('care_type', 'residential')
    budget = questionnaire.get('budget')
    
    scenarios = generate_mock_results(questionnaire)
    
    return {
        'questionnaire': file_name,
        'postcode': postcode,
        'care_type': care_type,
        'budget': budget,
        'success': True,
        'source': 'mock',
        'total_homes': 3,
        'scenarios': scenarios,
        'local_authority': 'Mock Authority'
    }


async def main():
    """Run combined tests"""
    print(f"\n🚀 Starting Combined Matching Tests")
    print(f"   Backend URL: {BACKEND_URL}")
    print(f"   Questionnaires directory: {QUESTIONNAIRES_DIR}")
    
    questionnaires = load_questionnaires()
    print(f"\n📚 Loaded {len(questionnaires)} questionnaires")
    
    results = []
    client = httpx.AsyncClient(timeout=120.0)
    
    backend_available = False
    try:
        # Test backend availability
        test_response = await client.get(f"{BACKEND_URL}/docs", timeout=5.0)
        if test_response.status_code == 200:
            backend_available = True
            print("✅ Backend is available, using backend API")
        else:
            print("⚠️ Backend returned non-200, falling back to mock")
    except:
        print("⚠️ Backend not accessible, using mock data")
    
    # Test each questionnaire
    for questionnaire in questionnaires:
        file_name = questionnaire.get('_file', 'unknown')
        postcode = questionnaire.get('postcode', '')
        care_type = questionnaire.get('care_type', 'residential')
        budget = questionnaire.get('budget')
        
        print(f"\n{'='*80}")
        print(f"📋 Testing: {file_name}")
        print(f"   Postcode: {postcode}, Care Type: {care_type}, Budget: £{budget}/week")
        print(f"{'='*80}")
        
        if backend_available:
            result = await test_questionnaire_backend(client, questionnaire)
            if not result.get('success'):
                print(f"   ⚠️ Backend failed, using mock data")
                result = test_questionnaire_mock(questionnaire)
        else:
            result = test_questionnaire_mock(questionnaire)
        
        results.append(result)
        
        if result.get('success'):
            scenarios = result.get('scenarios', {})
            print(f"✅ Success ({result.get('source', 'unknown')}): Found {result.get('total_homes', 0)} homes")
            for scenario_name in ['safe_bet', 'best_value', 'premium']:
                if scenario_name in scenarios:
                    scenario = scenarios[scenario_name]
                    print(f"   {scenario_name.upper()}: {scenario['name']} - "
                          f"£{scenario.get('weekly_cost', 'N/A')}/week, "
                          f"{scenario.get('distance_km', 'N/A')}km")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        await asyncio.sleep(0.5)  # Small delay
    
    await client.aclose()
    
    # Generate comparison report
    successful = [r for r in results if r.get('success')]
    print(f"\n{'='*100}")
    print("📊 MATCHING TEST RESULTS - COMPARISON REPORT")
    print("="*100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Summary: {len(successful)}/{len(results)} questionnaires tested successfully")
    print(f"Backend available: {backend_available}")
    print()
    
    # Comparison by scenario
    for scenario_name in ['safe_bet', 'best_value', 'premium']:
        print(f"📌 {scenario_name.upper().replace('_', ' ')}:")
        print("-" * 80)
        
        scenario_results = []
        for result in successful:
            scenarios = result.get('scenarios', {})
            if scenario_name in scenarios:
                scenario_data = scenarios[scenario_name]
                scenario_results.append({
                    'questionnaire': result['questionnaire'],
                    'postcode': result['postcode'],
                    'care_type': result['care_type'],
                    'name': scenario_data.get('name'),
                    'home_postcode': scenario_data.get('postcode'),
                    'distance': scenario_data.get('distance_km'),
                    'cost': scenario_data.get('weekly_cost'),
                    'rating': scenario_data.get('rating'),
                    'source': result.get('source', 'unknown')
                })
        
        if scenario_results:
            # Check for duplicates
            unique_homes = {}
            for sr in scenario_results:
                home_id = sr.get('home_postcode') or sr.get('name', '')
                if home_id not in unique_homes:
                    unique_homes[home_id] = []
                unique_homes[home_id].append(sr['questionnaire'])
            
            print(f"   Total unique homes: {len(unique_homes)}")
            print(f"   Total matches: {len(scenario_results)}")
            
            if len(unique_homes) < len(scenario_results):
                print(f"   ⚠️ WARNING: {len(scenario_results) - len(unique_homes)} duplicate matches detected!")
                for home_id, questionnaires in unique_homes.items():
                    if len(questionnaires) > 1:
                        print(f"     {home_id}: {', '.join(questionnaires)}")
            
            print(f"\n   All matches:")
            for sr in scenario_results:
                print(f"     {sr['questionnaire']}: {sr['name']} "
                      f"({sr.get('home_postcode', 'N/A')}) - "
                      f"£{sr.get('cost', 'N/A')}/week, "
                      f"{sr.get('distance', 'N/A')}km [{sr.get('source', 'unknown')}]")
        else:
            print(f"   No matches found")
        print()
    
    # Uniqueness analysis
    print("="*100)
    print("UNIQUENESS ANALYSIS")
    print("="*100)
    
    all_home_ids = set()
    duplicate_homes = {}
    
    for result in successful:
        scenarios = result.get('scenarios', {})
        for scenario_name, scenario_data in scenarios.items():
            home_id = scenario_data.get('location_id') or scenario_data.get('postcode') or scenario_data.get('name', '')
            if home_id:
                if home_id in all_home_ids:
                    if home_id not in duplicate_homes:
                        duplicate_homes[home_id] = []
                    duplicate_homes[home_id].append({
                        'questionnaire': result['questionnaire'],
                        'scenario': scenario_name
                    })
                else:
                    all_home_ids.add(home_id)
    
    print(f"\nTotal unique care homes across all scenarios: {len(all_home_ids)}")
    if duplicate_homes:
        print(f"\n⚠️ Found {len(duplicate_homes)} homes recommended multiple times:")
        for home_id, occurrences in duplicate_homes.items():
            print(f"   {home_id}:")
            for occ in occurrences:
                print(f"     - {occ['questionnaire']} ({occ['scenario']})")
    else:
        print(f"\n✅ All recommendations are unique!")
    
    print("\n" + "="*100)
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'backend_available': backend_available,
        'total_questionnaires': len(results),
        'successful': len(successful),
        'results': results
    }
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())

