#!/usr/bin/env python3
"""
Test Matching for All 6 Questionnaires
Tests all questionnaires and compares results across 3 scenarios (Safe Bet, Best Value, Premium)
"""
import asyncio
import json
import httpx
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import sys

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
BACKEND_URL = "http://localhost:8000"  # Adjust if needed
QUESTIONNAIRES_DIR = project_root / "frontend" / "public" / "sample_questionnaires"
RESULTS_FILE = project_root / "backend" / "matching_test_results.json"


class MatchingTester:
    """Test matching for all questionnaires"""
    
    def __init__(self, backend_url: str = BACKEND_URL):
        self.backend_url = backend_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results = []
    
    async def load_questionnaires(self) -> List[Dict[str, Any]]:
        """Load all questionnaire JSON files"""
        questionnaires = []
        for i in range(1, 7):
            file_path = QUESTIONNAIRES_DIR / f"questionnaire_{i}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_file'] = f"questionnaire_{i}.json"
                    questionnaires.append(data)
            else:
                print(f"⚠️ Warning: {file_path} not found")
        return questionnaires
    
    async def test_questionnaire(self, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single questionnaire"""
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
        
        try:
            # Make request to backend
            # Remove _file key before sending
            request_data = {k: v for k, v in questionnaire.items() if k != '_file'}
            
            response = await self.client.post(
                f"{self.backend_url}/api/free-report",
                json=request_data,
                timeout=120.0  # Increase timeout for complex queries
            )
            
            if response.status_code != 200:
                try:
                    error_detail = response.json()
                    detail_text = error_detail.get('detail', str(error_detail))
                    error_msg = f"HTTP {response.status_code}: {detail_text[:1000]}"
                    print(f"❌ Error: {error_msg}")
                    if len(detail_text) > 1000:
                        print(f"   ... (truncated, full error in JSON file)")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text[:1000]}"
                    print(f"❌ Error: {error_msg}")
                    if len(response.text) > 1000:
                        print(f"   ... (truncated, full error in JSON file)")
                return {
                    'questionnaire': file_name,
                    'postcode': postcode,
                    'care_type': care_type,
                    'budget': budget,
                    'error': error_msg,
                    'success': False
                }
            
            result_data = response.json()
            care_homes = result_data.get('care_homes', [])
            
            # Extract 3 scenarios
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
            
            print(f"✅ Success: Found {len(care_homes)} care homes")
            for scenario_name, scenario_data in scenarios.items():
                print(f"   {scenario_name.upper()}: {scenario_data['name']} "
                      f"({scenario_data.get('postcode', 'N/A')}) - "
                      f"£{scenario_data.get('weekly_cost', 'N/A')}/week, "
                      f"{scenario_data.get('distance_km', 'N/A')}km")
            
            return {
                'questionnaire': file_name,
                'postcode': postcode,
                'care_type': care_type,
                'budget': budget,
                'success': True,
                'total_homes': len(care_homes),
                'scenarios': scenarios,
                'fair_cost_gap': result_data.get('fair_cost_gap', {}),
                'local_authority': result_data.get('fair_cost_gap', {}).get('local_authority', 'Unknown')
            }
            
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Error: {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                'questionnaire': file_name,
                'postcode': postcode,
                'care_type': care_type,
                'budget': budget,
                'error': error_msg,
                'success': False
            }
    
    async def run_all_tests(self):
        """Run tests for all questionnaires"""
        print(f"\n🚀 Starting Matching Tests")
        print(f"   Backend URL: {self.backend_url}")
        print(f"   Questionnaires directory: {QUESTIONNAIRES_DIR}")
        
        questionnaires = await self.load_questionnaires()
        print(f"\n📚 Loaded {len(questionnaires)} questionnaires")
        
        # Test each questionnaire
        for questionnaire in questionnaires:
            result = await self.test_questionnaire(questionnaire)
            self.results.append(result)
            # Small delay between requests
            await asyncio.sleep(1)
        
        await self.client.aclose()
    
    def generate_comparison_report(self) -> str:
        """Generate comparison report"""
        report_lines = []
        report_lines.append("\n" + "="*100)
        report_lines.append("📊 MATCHING TEST RESULTS - COMPARISON REPORT")
        report_lines.append("="*100)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        successful = sum(1 for r in self.results if r.get('success'))
        total = len(self.results)
        report_lines.append(f"Summary: {successful}/{total} questionnaires tested successfully")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("="*100)
        report_lines.append("DETAILED RESULTS BY QUESTIONNAIRE")
        report_lines.append("="*100)
        
        for result in self.results:
            if not result.get('success'):
                report_lines.append(f"\n❌ {result['questionnaire']}: FAILED")
                report_lines.append(f"   Error: {result.get('error', 'Unknown error')}")
                continue
            
            report_lines.append(f"\n✅ {result['questionnaire']}")
            report_lines.append(f"   Postcode: {result['postcode']}")
            report_lines.append(f"   Care Type: {result['care_type']}")
            report_lines.append(f"   Budget: £{result.get('budget', 'N/A')}/week")
            report_lines.append(f"   Local Authority: {result.get('local_authority', 'Unknown')}")
            report_lines.append(f"   Total Homes Found: {result.get('total_homes', 0)}")
            
            scenarios = result.get('scenarios', {})
            if scenarios:
                report_lines.append(f"\n   SCENARIOS:")
                for scenario_name in ['safe_bet', 'best_value', 'premium']:
                    if scenario_name in scenarios:
                        scenario = scenarios[scenario_name]
                        report_lines.append(f"     {scenario_name.upper().replace('_', ' ')}:")
                        report_lines.append(f"       Name: {scenario.get('name', 'N/A')}")
                        report_lines.append(f"       Postcode: {scenario.get('postcode', 'N/A')}")
                        report_lines.append(f"       Distance: {scenario.get('distance_km', 'N/A')} km")
                        report_lines.append(f"       Cost: £{scenario.get('weekly_cost', 'N/A')}/week")
                        report_lines.append(f"       Rating: {scenario.get('rating', 'N/A')}")
        
        # Comparison by scenario
        report_lines.append("\n" + "="*100)
        report_lines.append("COMPARISON BY SCENARIO")
        report_lines.append("="*100)
        
        for scenario_name in ['safe_bet', 'best_value', 'premium']:
            report_lines.append(f"\n📌 {scenario_name.upper().replace('_', ' ')}:")
            report_lines.append("-" * 80)
            
            scenario_results = []
            for result in self.results:
                if result.get('success'):
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
                            'rating': scenario_data.get('rating')
                        })
            
            if scenario_results:
                # Check for duplicates
                unique_homes = {}
                for sr in scenario_results:
                    home_id = sr.get('home_postcode') or sr.get('name', '')
                    if home_id not in unique_homes:
                        unique_homes[home_id] = []
                    unique_homes[home_id].append(sr['questionnaire'])
                
                report_lines.append(f"   Total unique homes: {len(unique_homes)}")
                report_lines.append(f"   Total matches: {len(scenario_results)}")
                
                if len(unique_homes) < len(scenario_results):
                    report_lines.append(f"   ⚠️ WARNING: {len(scenario_results) - len(unique_homes)} duplicate matches detected!")
                    report_lines.append(f"   Duplicate homes:")
                    for home_id, questionnaires in unique_homes.items():
                        if len(questionnaires) > 1:
                            report_lines.append(f"     {home_id}: {', '.join(questionnaires)}")
                
                # Show all matches
                report_lines.append(f"\n   All matches:")
                for sr in scenario_results:
                    report_lines.append(f"     {sr['questionnaire']}: {sr['name']} "
                                      f"({sr.get('home_postcode', 'N/A')}) - "
                                      f"£{sr.get('cost', 'N/A')}/week, "
                                      f"{sr.get('distance', 'N/A')}km")
            else:
                report_lines.append(f"   No matches found for this scenario")
        
        # Uniqueness analysis
        report_lines.append("\n" + "="*100)
        report_lines.append("UNIQUENESS ANALYSIS")
        report_lines.append("="*100)
        
        all_home_ids = set()
        duplicate_homes = {}
        
        for result in self.results:
            if result.get('success'):
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
        
        report_lines.append(f"\nTotal unique care homes across all scenarios: {len(all_home_ids)}")
        if duplicate_homes:
            report_lines.append(f"\n⚠️ Found {len(duplicate_homes)} homes recommended multiple times:")
            for home_id, occurrences in duplicate_homes.items():
                report_lines.append(f"   {home_id}:")
                for occ in occurrences:
                    report_lines.append(f"     - {occ['questionnaire']} ({occ['scenario']})")
        else:
            report_lines.append(f"\n✅ All recommendations are unique!")
        
        report_lines.append("\n" + "="*100)
        
        return "\n".join(report_lines)
    
    def save_results(self):
        """Save results to JSON file"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_questionnaires': len(self.results),
            'successful': sum(1 for r in self.results if r.get('success')),
            'results': self.results
        }
        
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {RESULTS_FILE}")


async def main():
    """Main test function"""
    tester = MatchingTester()
    
    try:
        await tester.run_all_tests()
        
        # Generate and print report
        report = tester.generate_comparison_report()
        print(report)
        
        # Save results
        tester.save_results()
        
        # Save report to file
        report_file = RESULTS_FILE.parent / "matching_test_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

