"""
Test script to verify each step of professional report generation
"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("PROFESSIONAL REPORT - STEP BY STEP VERIFICATION")
print("=" * 80)

# Load questionnaire
questionnaire_path = Path(__file__).parent.parent / "frontend" / "public" / "sample_questionnaires" / "professional_questionnaire_1_dementia.json"

if not questionnaire_path.exists():
    print(f"❌ Questionnaire not found: {questionnaire_path}")
    sys.exit(1)

with open(questionnaire_path, 'r') as f:
    questionnaire = json.load(f)

print("\n" + "=" * 80)
print("STEP 1: EXTRACT DATA FROM QUESTIONNAIRE")
print("=" * 80)

location_budget = questionnaire.get('section_2_location_budget', {})
medical_needs = questionnaire.get('section_3_medical_needs', {})

preferred_city = location_budget.get('q5_preferred_city', '')
max_distance = location_budget.get('q6_max_distance', 'distance_not_important')
care_types = medical_needs.get('q8_care_types', [])

print(f"✅ Extracted:")
print(f"   preferred_city: '{preferred_city}'")
print(f"   care_types: {care_types}")

care_type = None
if 'specialised_dementia' in care_types:
    care_type = 'dementia'
elif 'nursing' in care_types or 'general_nursing' in care_types:
    care_type = 'nursing'
elif 'general_residential' in care_types:
    care_type = 'residential'

print(f"   care_type (determined): '{care_type}'")

max_distance_km = None
if max_distance == 'within_5km':
    max_distance_km = 5.0
elif max_distance == 'within_15km':
    max_distance_km = 15.0
elif max_distance == 'within_30km':
    max_distance_km = 30.0

print(f"   max_distance_km: {max_distance_km}")

# Normalize city
normalized_city = preferred_city
if preferred_city:
    try:
        from services.location_normalizer import LocationNormalizer
        normalized_city = LocationNormalizer.normalize_city_name(preferred_city)
        print(f"   normalized_city: '{normalized_city}'")
    except ImportError:
        print(f"   ⚠️  Location normalizer not available")

print("\n" + "=" * 80)
print("STEP 2: CHECK MOCK DATA DIRECTLY")
print("=" * 80)

from services.mock_care_homes import load_mock_care_homes, filter_mock_care_homes

all_mock = load_mock_care_homes()
print(f"✅ Total mock homes: {len(all_mock)}")

# Check Birmingham
birmingham_homes = [h for h in all_mock if 'birmingham' in h.get('city', '').lower() or 'birmingham' in h.get('local_authority', '').lower()]
print(f"✅ Birmingham homes: {len(birmingham_homes)}")

# Check dementia
dementia_homes = [h for h in all_mock if 'dementia' in [ct.lower() for ct in h.get('care_types', [])]]
print(f"✅ Dementia homes: {len(dementia_homes)}")

# Check Birmingham + Dementia
birmingham_dementia = [h for h in birmingham_homes if 'dementia' in [ct.lower() for ct in h.get('care_types', [])]]
print(f"✅ Birmingham + Dementia: {len(birmingham_dementia)}")

if birmingham_dementia:
    print(f"   Sample:")
    for i, h in enumerate(birmingham_dementia[:3], 1):
        print(f"      {i}. {h.get('name')} - {h.get('city')} - {h.get('care_types')}")

# Test filter function
print(f"\n✅ Testing filter_mock_care_homes('Birmingham', 'dementia'):")
filtered = filter_mock_care_homes(
    local_authority='Birmingham',
    care_type='dementia'
)
print(f"   Result: {len(filtered)} homes")

print("\n" + "=" * 80)
print("STEP 3: TEST ASYNCDATALOADER")
print("=" * 80)

async def test_async_loader():
    from services.async_data_loader import get_async_loader
    
    loader = get_async_loader()
    print(f"   Calling load_initial_data with:")
    print(f"      preferred_city: '{normalized_city if normalized_city else preferred_city}'")
    print(f"      care_type: '{care_type}'")
    print(f"      max_distance_km: {max_distance_km}")
    
    care_homes, user_lat, user_lon = await loader.load_initial_data(
        preferred_city=normalized_city if normalized_city else preferred_city if preferred_city else None,
        care_type=care_type,
        max_distance_km=max_distance_km,
        postcode=None,
        limit=50
    )
    
    print(f"\n   ✅ AsyncDataLoader returned:")
    print(f"      care_homes: {len(care_homes)} homes")
    print(f"      user_lat: {user_lat}")
    print(f"      user_lon: {user_lon}")
    print(f"      Type: {type(care_homes)}")
    
    if care_homes and len(care_homes) > 0:
        print(f"      First home: {care_homes[0].get('name', 'N/A')}")
        print(f"      First home city: {care_homes[0].get('city', 'N/A')}")
        return True, care_homes
    else:
        print(f"      ❌ PROBLEM: AsyncDataLoader returned EMPTY list!")
        return False, []

success, care_homes = asyncio.run(test_async_loader())

print("\n" + "=" * 80)
print("STEP 4: FINAL VERIFICATION")
print("=" * 80)

if not success or not care_homes:
    print(f"❌ PROBLEM FOUND: AsyncDataLoader returns empty list")
    print(f"   This is the root cause!")
    print(f"\n   Let's check why...")
    
    # Check what _load_mock_care_homes_async does
    print(f"\n   Testing _load_mock_care_homes_async directly...")
    async def test_mock_loader():
        from services.async_data_loader import get_async_loader
        loader = get_async_loader()
        
        # Call the internal method
        mock_homes = await loader._load_mock_care_homes_async(
            local_authority=normalized_city if normalized_city else preferred_city,
            care_type=care_type,
            max_distance_km=max_distance_km,
            user_lat=None,
            user_lon=None
        )
        print(f"      _load_mock_care_homes_async returned: {len(mock_homes)} homes")
        return mock_homes
    
    mock_homes = asyncio.run(test_mock_loader())
    if not mock_homes:
        print(f"   ❌ _load_mock_care_homes_async also returns empty!")
        print(f"   This means the problem is in the filtering logic")
else:
    print(f"✅ SUCCESS: Have {len(care_homes)} homes")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)

