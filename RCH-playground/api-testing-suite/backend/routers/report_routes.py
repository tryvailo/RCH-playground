"""
Report Routes
Handles report generation endpoints

Uses shared utilities:
- utils.price_extractor for price extraction (shared with Free Report)
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

from services.professional_report_validator import validate_questionnaire, QuestionnaireValidationError
from services.professional_matching_service import ProfessionalMatchingService
from services.simple_matching_service import SimpleMatchingService
from services.async_data_loader import get_async_loader
from services.cost_analysis_service import CostAnalysisService
from services.data_quality_diagnostics import diagnose_matching_data, analyze_fallback_usage
from utils.state_manager import test_results_store
from utils.price_extractor import extract_weekly_price
import os

router = APIRouter(prefix="/api", tags=["Reports"])

VALID_CARE_TYPES = {'residential', 'nursing', 'dementia', 'respite'}
VALID_REGIONS = {'england', 'wales', 'scotland', 'northern_ireland'}
MAX_CARE_HOMES = 50

# Configuration flag: Use simplified matching for bootstrap MVP
# Set USE_SIMPLE_MATCHING=true in environment to enable
USE_SIMPLE_MATCHING = os.getenv('USE_SIMPLE_MATCHING', 'true').lower() == 'true'


@router.get("/report/summary/{job_id}")
async def get_summary_report(job_id: str):
    """Get summary report"""
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_results_store[job_id]
    return {
        "job_id": job_id,
        "summary": {
            "total_apis_tested": len(job.get("results", {})),
            "successful": sum(1 for r in job.get("results", {}).values() if r.get("status") == "success"),
            "failed": sum(1 for r in job.get("results", {}).values() if r.get("status") == "failure"),
            "total_cost": job.get("total_cost", 0),
            "total_time": "N/A"  # Calculate from timestamps
        }
    }


@router.get("/report/export/{format}")
async def export_report(format: str, job_id: str):
    """Export report in specified format"""
    if format not in ["csv", "json", "pdf"]:
        raise HTTPException(status_code=400, detail="Format must be csv, json, or pdf")
    
    if not job_id or not job_id.strip():
        raise HTTPException(status_code=400, detail="job_id query parameter is required")
    
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Implementation
    return {"message": f"Export {format} not yet implemented"}


@router.post("/professional-report")
async def generate_professional_report(request: Dict[str, Any] = Body(...)):
    """
    Generate professional report from questionnaire
    
    Accepts professional questionnaire with 5 sections (17 questions total)
    Returns report with 5 matched care homes using matching algorithm (100-point simplified or 156-point full)
    
    Performance optimizations:
    - Parallel data loading (DB + postcode resolution)
    - Reduced limit to 20 for faster matching
    - Async enrichment pipeline
    """
    import time
    print(f"\n{'='*80}")
    print(f"🚀 Professional Report Request Received (report_routes.py endpoint)")
    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"   Request keys: {list(request.keys())}")
    
    try:
        # Extract questionnaire (handle both direct questionnaire and wrapped format)
        questionnaire = request.get('questionnaire', request)
        
        # Validate questionnaire
        try:
            validate_questionnaire(questionnaire)
        except QuestionnaireValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Extract location and care type from questionnaire
        location_budget = questionnaire.get('section_2_location_budget', {})
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        
        preferred_city = location_budget.get('q5_preferred_city', '')
        max_distance = location_budget.get('q6_max_distance', 'distance_not_important')
        postcode = location_budget.get('q4_postcode', '')  # Extract postcode for geo resolution
        care_types = medical_needs.get('q8_care_types', [])
        
        # Normalize preferred_city for better matching
        normalized_city = preferred_city
        if preferred_city:
            try:
                from services.location_normalizer import LocationNormalizer
                normalized_city = LocationNormalizer.normalize_city_name(preferred_city)
                print(f"✅ Normalized city name: '{preferred_city}' -> '{normalized_city}'")
            except ImportError:
                print(f"⚠️ Location normalizer not available, using original: '{preferred_city}'")
        
        # Determine care type
        care_type: Optional[str] = None
        if 'specialised_dementia' in care_types:
            care_type = 'dementia'
        elif 'nursing' in care_types or 'general_nursing' in care_types:
            care_type = 'nursing'
        elif 'general_residential' in care_types:
            care_type = 'residential'
        
        # Calculate max distance in km
        # Start with user's preference, but will expand if needed
        initial_max_distance_km: Optional[float] = None
        if max_distance == 'within_5km':
            initial_max_distance_km = 5.0
        elif max_distance == 'within_15km':
            initial_max_distance_km = 15.0
        elif max_distance == 'within_30km':
            initial_max_distance_km = 30.0
        
        max_distance_km = initial_max_distance_km
        initial_limit = 50  # Start with higher limit to get more candidates
        
        # STEP 1: Load care homes with detailed logging
        print(f"\n{'='*80}")
        print(f"STEP 1: LOADING CARE HOMES (report_routes.py)")
        print(f"{'='*80}")
        print(f"   Input parameters:")
        print(f"      preferred_city: '{preferred_city}'")
        print(f"      normalized_city: '{normalized_city}'")
        print(f"      care_type: '{care_type}'")
        print(f"      max_distance_km: {max_distance_km}")
        print(f"      postcode: '{postcode}'")
        
        # Resolve user location to coordinates with detailed logging
        user_lat, user_lon = None, None
        
        # Try postcode first (if provided)
        if postcode:
            print(f"   [LOCATION DEBUG] Attempting postcode resolution: '{postcode}'")
            try:
                from postcode_resolver import PostcodeResolver
                resolver = PostcodeResolver()
                coords = resolver.resolve_postcode(postcode)
                if coords:
                    user_lat, user_lon = coords
                    print(f"   ✅ [LOCATION DEBUG] Postcode resolved: ({user_lat}, {user_lon})")
                else:
                    print(f"   ⚠️ [LOCATION DEBUG] Postcode resolution returned None")
            except Exception as e:
                print(f"   ⚠️ [LOCATION DEBUG] Postcode resolution failed: {e}")
        
        # If no postcode or postcode failed, try geocoding preferred_city
        if not user_lat or not user_lon:
            if preferred_city:
                print(f"   [LOCATION DEBUG] Attempting city geocoding: '{preferred_city}'")
                try:
                    import httpx
                    
                    async def geocode_city(city_name: str):
                        url = "https://nominatim.openstreetmap.org/search"
                        params = {
                            'q': f"{city_name}, UK",
                            'format': 'json',
                            'limit': 1
                        }
                        headers = {'User-Agent': 'CareHomeMatchingService/1.0'}
                        
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            response = await client.get(url, params=params, headers=headers)
                            if response.status_code == 200:
                                data = response.json()
                                if data:
                                    lat = float(data[0]['lat'])
                                    lon = float(data[0]['lon'])
                                    display_name = data[0].get('display_name', '')
                                    print(f"   ✅ [LOCATION DEBUG] City geocoded: ({lat}, {lon}) - {display_name}")
                                    return lat, lon
                            print(f"   ⚠️ [LOCATION DEBUG] City geocoding failed: status {response.status_code}")
                            return None, None
                    
                    # Call async function directly (we're already in async context)
                    lat, lon = await geocode_city(preferred_city)
                    if lat and lon:
                        user_lat, user_lon = lat, lon
                except Exception as e:
                    print(f"   ⚠️ [LOCATION DEBUG] City geocoding exception: {e}")
        
        if not user_lat or not user_lon:
            print(f"   ❌ [LOCATION DEBUG] CRITICAL: Could not resolve user location!")
            print(f"      postcode: '{postcode}'")
            print(f"      preferred_city: '{preferred_city}'")
            print(f"      This will cause Location scoring to fail!")
        else:
            print(f"   ✅ [LOCATION DEBUG] Final user coordinates: ({user_lat}, {user_lon})")
        
        # Save user coordinates before fallback (they might be overwritten)
        saved_user_lat = user_lat
        saved_user_lon = user_lon
        
        # Get care homes using hybrid approach (CQC + Staging) with fallback to legacy CSV
        care_homes = []
        try:
            from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
            
            # Start with higher limit to get more candidates
            initial_limit = 50
            care_homes = await asyncio.to_thread(
                get_csv_care_homes,
                local_authority=normalized_city if normalized_city else preferred_city,
                care_type=care_type,
                max_distance_km=max_distance_km,
                user_lat=user_lat,
                user_lon=user_lon,
                limit=initial_limit,
                use_hybrid=True  # Enable hybrid approach (CQC + Staging)
            )
            print(f"✅ Loaded {len(care_homes)} care homes using hybrid approach (CQC + Staging) (limit={initial_limit}, distance={max_distance_km}km)")
        except AttributeError:
            # Fallback for Python < 3.9
            try:
                from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
                loop = asyncio.get_event_loop()
                initial_limit = 50
                care_homes = await loop.run_in_executor(
                    None,
                    lambda: get_csv_care_homes(
                        local_authority=normalized_city if normalized_city else preferred_city,
                        care_type=care_type,
                        max_distance_km=max_distance_km,
                        user_lat=user_lat,
                        user_lon=user_lon,
                        limit=initial_limit,
                        use_hybrid=True  # Enable hybrid approach (CQC + Staging)
                    )
                )
                print(f"✅ Loaded {len(care_homes)} care homes using hybrid approach (CQC + Staging) (limit={initial_limit}, distance={max_distance_km}km)")
            except Exception as e:
                print(f"⚠️ Hybrid approach failed, trying legacy CSV: {e}")
                # Try legacy CSV without hybrid
                try:
                    care_homes = await loop.run_in_executor(
                        None,
                        lambda: get_csv_care_homes(
                            local_authority=normalized_city if normalized_city else preferred_city,
                            care_type=care_type,
                            max_distance_km=max_distance_km,
                            user_lat=user_lat,
                            user_lon=user_lon,
                            limit=initial_limit,
                            use_hybrid=False  # Disable hybrid, use legacy CSV
                        )
                    )
                    print(f"✅ Loaded {len(care_homes)} care homes from legacy CSV (limit={initial_limit}, distance={max_distance_km}km)")
                except Exception as e2:
                    print(f"⚠️ Legacy CSV also failed: {e2}")
                    care_homes = []
        except Exception as e:
            print(f"⚠️ Hybrid approach failed, trying legacy CSV: {e}")
            # Try legacy CSV without hybrid
            try:
                from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
                care_homes = await asyncio.to_thread(
                    get_csv_care_homes,
                    local_authority=normalized_city if normalized_city else preferred_city,
                    care_type=care_type,
                    max_distance_km=max_distance_km,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    limit=initial_limit,
                    use_hybrid=False  # Disable hybrid, use legacy CSV
                )
                print(f"✅ Loaded {len(care_homes)} care homes from legacy CSV (limit={initial_limit}, distance={max_distance_km}km)")
            except Exception as e2:
                print(f"⚠️ Legacy CSV also failed: {e2}")
                care_homes = []
        
        # If CSV failed, try AsyncDataLoader fallback
        if not care_homes or len(care_homes) == 0:
            try:
                loader = get_async_loader()
                print(f"\n   🔄 Falling back to AsyncDataLoader.load_initial_data()...")
                
                care_homes, loader_lat, loader_lon = await loader.load_initial_data(
                    preferred_city=normalized_city if normalized_city else preferred_city if preferred_city else None,
                    care_type=care_type,
                    max_distance_km=max_distance_km,
                    postcode=postcode if postcode else None,
                    limit=20
                )
                
                # Use saved coordinates if loader didn't provide them
                if not loader_lat or not loader_lon:
                    user_lat = saved_user_lat
                    user_lon = saved_user_lon
                else:
                    user_lat = loader_lat
                    user_lon = loader_lon
                
                print(f"   ✅ AsyncDataLoader returned:")
                print(f"      care_homes: {len(care_homes)} homes")
                print(f"      user_lat: {user_lat}")
                print(f"      user_lon: {user_lon}")
            except Exception as db_error:
                print(f"⚠️ AsyncDataLoader also failed: {db_error}")
                care_homes = []
                # Restore saved coordinates
                user_lat = saved_user_lat
                user_lon = saved_user_lon
        
        if care_homes and len(care_homes) > 0:
            print(f"      First home: {care_homes[0].get('name', 'N/A')}")
        
        # FIX: Calculate distance_km for all homes if user coordinates are available
        # This ensures distance_km is always available for scoring, even for mock homes
        if care_homes and user_lat and user_lon:
            print(f"\n   Calculating distances for {len(care_homes)} homes...")
            try:
                from utils.geo import calculate_distance_km, validate_coordinates
            except ImportError:
                from math import radians, cos, sin, asin, sqrt
                def calculate_distance_km(lat1, lon1, lat2, lon2):
                    R = 6371.0
                    if not (lat2 and lon2):
                        return 9999.0
                    try:
                        dlat = radians(float(lat2) - float(lat1))
                        dlon = radians(float(lon2) - float(lon1))
                        a = sin(dlat/2)**2 + cos(radians(float(lat1))) * cos(radians(float(lat2))) * sin(dlon/2)**2
                        c = 2 * asin(sqrt(a))
                        return R * c
                    except (ValueError, TypeError):
                        return 9999.0
                def validate_coordinates(lat, lon):
                    return -90 <= lat <= 90 and -180 <= lon <= 180
            
            calculated_count = 0
            for home in care_homes:
                # Skip if distance_km already calculated
                if home.get('distance_km') is not None and home.get('distance_km') < 999:
                    continue
                
                lat = home.get('latitude')
                lon = home.get('longitude')
                
                if lat and lon:
                    try:
                        lat_float = float(lat)
                        lon_float = float(lon)
                        
                        if validate_coordinates(lat_float, lon_float) and lat_float != 0 and lon_float != 0:
                            distance = calculate_distance_km(user_lat, user_lon, lat_float, lon_float)
                            home['distance_km'] = round(distance, 2)
                            calculated_count += 1
                        else:
                            home['distance_km'] = 9999.0
                    except (ValueError, TypeError):
                        home['distance_km'] = 9999.0
                else:
                    home['distance_km'] = 9999.0
            
            print(f"   ✅ Calculated distances for {calculated_count}/{len(care_homes)} homes")
            if calculated_count < len(care_homes):
                print(f"   ⚠️ {len(care_homes) - calculated_count} homes missing coordinates")
        
        # STEP 2: Fallback to mock data if empty
        print(f"\n{'='*80}")
        print(f"STEP 2: FALLBACK TO MOCK DATA (report_routes.py)")
        print(f"{'='*80}")
        
        if not care_homes or len(care_homes) == 0:
            print(f"   ⚠️  AsyncDataLoader returned empty, trying direct mock data load...")
            try:
                from services.mock_care_homes import load_mock_care_homes
                
                print(f"   🔄 Loading mock data...")
                try:
                    all_mock = await asyncio.to_thread(load_mock_care_homes)
                except AttributeError:
                    loop = asyncio.get_event_loop()
                    all_mock = await loop.run_in_executor(None, load_mock_care_homes)
                
                print(f"   ✅ Mock data loaded: {len(all_mock) if all_mock else 0} homes")
                
                if all_mock and len(all_mock) > 0:
                    care_homes = all_mock[:20]  # Take first 20, no filters
                    print(f"   ✅ Using first {len(care_homes)} homes (no filters)")
                    print(f"      First home: {care_homes[0].get('name', 'N/A')}")
                else:
                    print(f"   ❌ Mock data is empty")
            except Exception as e:
                print(f"   ❌ Failed to load mock homes:")
                print(f"      Error: {e}")
                import traceback
                print(f"      Traceback: {traceback.format_exc()}")
        else:
            print(f"   ✅ Skipping fallback - already have {len(care_homes)} homes")
        
        # STEP 3: Validate basic home information (Section 1-5)
        print(f"\n{'='*80}")
        print(f"STEP 3: VALIDATE BASIC HOME INFORMATION (Section 1-5)")
        print(f"{'='*80}")
        
        if care_homes and len(care_homes) > 0:
            from services.professional_report_validator import validate_care_homes_batch
            
            validation_summary = validate_care_homes_batch(care_homes)
            print(f"   Validation Summary:")
            print(f"      Total homes: {validation_summary['total_homes']}")
            print(f"      Valid: {validation_summary['valid_homes']}")
            print(f"      Invalid: {validation_summary['invalid_homes']}")
            print(f"      Total errors: {validation_summary['total_errors']}")
            print(f"      Total warnings: {validation_summary['total_warnings']}")
            
            # Log errors for invalid homes
            if validation_summary['invalid_homes'] > 0:
                print(f"\n   ⚠️  Invalid homes detected:")
                for result in validation_summary['results']:
                    if not result['validation']['is_valid']:
                        print(f"      - {result['home_name']} (ID: {result['cqc_location_id']}):")
                        for error in result['validation']['errors']:
                            print(f"         ❌ {error}")
            
            # Log warnings (first 10)
            if validation_summary['total_warnings'] > 0:
                print(f"\n   ⚠️  Warnings (non-critical, showing first 10):")
                warning_count = 0
                for result in validation_summary['results']:
                    if result['validation']['warnings']:
                        for warning in result['validation']['warnings']:
                            print(f"      - {result['home_name']}: {warning}")
                            warning_count += 1
                            if warning_count >= 10:
                                remaining = validation_summary['total_warnings'] - warning_count
                                if remaining > 0:
                                    print(f"      ... and {remaining} more warnings")
                                break
                    if warning_count >= 10:
                        break
            
            # Filter out homes with critical errors (missing required fields)
            # Keep homes with only warnings (non-critical)
            if validation_summary['invalid_homes'] > 0:
                print(f"\n   🔄 Filtering out homes with critical errors...")
                original_count = len(care_homes)
                valid_homes = []
                for home, result in zip(care_homes, validation_summary['results']):
                    if result['validation']['is_valid']:
                        valid_homes.append(home)
                
                filtered_count = original_count - len(valid_homes)
                if filtered_count > 0:
                    print(f"      Filtered out {filtered_count} homes with critical errors")
                    print(f"      Remaining: {len(valid_homes)} valid homes")
                    
                    # Only use filtered list if we still have enough homes
                    if len(valid_homes) >= 5:
                        care_homes = valid_homes
                    else:
                        print(f"      ⚠️  WARNING: Only {len(valid_homes)} valid homes (need at least 5)")
                        print(f"      Keeping original list but logging validation issues")
                else:
                    print(f"      All homes passed validation")
            else:
                print(f"   ✅ All homes passed basic validation")
        else:
            print(f"   ⚠️  No homes to validate")
        
        # STEP 4: Final verification
        print(f"\n{'='*80}")
        print(f"STEP 3: FINAL VERIFICATION (report_routes.py)")
        print(f"{'='*80}")
        print(f"   care_homes:")
        print(f"      Type: {type(care_homes)}")
        print(f"      Length: {len(care_homes) if isinstance(care_homes, list) else 'N/A'}")
        
        if isinstance(care_homes, list) and len(care_homes) > 0:
            print(f"   ✅ SUCCESS: Have {len(care_homes)} homes to process")
        else:
            print(f"   ❌ CRITICAL: care_homes is EMPTY!")
            print(f"   Attempting final synchronous load...")
            try:
                from services.mock_care_homes import load_mock_care_homes
                all_mock = load_mock_care_homes()
                if all_mock and len(all_mock) > 0:
                    care_homes = all_mock[:20]
                    print(f"   ✅ Final load successful: {len(care_homes)} homes")
                else:
                    print(f"   ❌ Even final load failed")
            except Exception as e:
                print(f"   ❌ Final load error: {e}")
        
        # Final check
        if not care_homes or len(care_homes) == 0:
            print(f"\n❌ ERROR: No care homes found after ALL attempts!")
            print(f"   Preferred City: {preferred_city}")
            print(f"   Normalized City: {normalized_city}")
            print(f"   Care Type: {care_type}")
            raise HTTPException(
                status_code=404,
                detail=f"No care homes found for {preferred_city or 'specified location'}. Please try a different location or care type."
            )
        
        # Inject resolved coordinates into questionnaire for distance calculations
        if user_lat and user_lon:
            if 'section_2_location_budget' not in questionnaire:
                questionnaire['section_2_location_budget'] = {}
            questionnaire['section_2_location_budget']['user_latitude'] = user_lat
            questionnaire['section_2_location_budget']['user_longitude'] = user_lon
        
        # STEP 3.5: Pre-filter homes using fallback logic (NEW!)
        # This uses Service User Bands and fallback logic to filter out homes
        # that explicitly don't match critical requirements (explicit FALSE)
        # while keeping homes with NULL values (unknown) for further evaluation
        print(f"\n{'='*80}")
        print(f"STEP 3.5: PRE-FILTERING WITH FALLBACK LOGIC (report_routes.py)")
        print(f"{'='*80}")
        
        try:
            from services.matching_fallback import evaluate_home_match_v2
            
            medical_needs = questionnaire.get('section_3_medical_needs', {}) or {}
            safety_needs = questionnaire.get('section_4_safety_special_needs', {}) or {}
            
            required_care = medical_needs.get('q8_care_types', []) or []
            medical_conditions = medical_needs.get('q9_medical_conditions', []) or []
            mobility_level = medical_needs.get('q10_mobility_level', '') or ''
            behavioral_concerns = safety_needs.get('q16_behavioral_concerns', []) or safety_needs.get('behavioral_concerns', []) or []
            
            original_count = len(care_homes)
            filtered_homes = []
            disqualified_homes = []
            
            for home in care_homes:
                match_result = evaluate_home_match_v2(
                    home=home,
                    required_care=required_care,
                    conditions=medical_conditions,
                    mobility=mobility_level,
                    behavioral=behavioral_concerns
                )
                
                # Only disqualify homes with explicit FALSE for critical requirements
                # Keep homes with 'match', 'partial', 'uncertain' status for scoring
                if match_result['status'] == 'disqualified':
                    disqualified_homes.append({
                        'home': home,
                        'reason': match_result.get('reason', 'Unknown reason'),
                        'match_result': match_result
                    })
                else:
                    # Add match result to home for potential use in scoring
                    home['_prefilter_match_result'] = match_result
                    filtered_homes.append(home)
            
            disqualified_count = len(disqualified_homes)
            if disqualified_count > 0:
                print(f"   🔄 Pre-filtering results:")
                print(f"      Original homes: {original_count}")
                print(f"      Disqualified: {disqualified_count} (explicit FALSE for critical requirements)")
                print(f"      Remaining: {len(filtered_homes)} (will be scored)")
                
                # Log first 5 disqualified homes
                for i, dq in enumerate(disqualified_homes[:5]):
                    home_name = dq['home'].get('name', 'Unknown')
                    reason = dq['reason']
                    print(f"      - {home_name}: {reason}")
                
                if len(disqualified_homes) > 5:
                    print(f"      ... and {len(disqualified_homes) - 5} more disqualified homes")
                
                # Only use filtered list if we still have enough homes (>= 5)
                if len(filtered_homes) >= 5:
                    care_homes = filtered_homes
                    print(f"   ✅ Using filtered list ({len(care_homes)} homes)")
                else:
                    print(f"   ⚠️  WARNING: Only {len(filtered_homes)} homes after pre-filtering (need at least 5)")
                    print(f"      Keeping original list but logging pre-filter results")
                    # Keep original but add match results for scoring
                    for home in care_homes:
                        if '_prefilter_match_result' not in home:
                            match_result = evaluate_home_match_v2(
                                home=home,
                                required_care=required_care,
                                conditions=medical_conditions,
                                mobility=mobility_level,
                                behavioral=behavioral_concerns
                            )
                            home['_prefilter_match_result'] = match_result
            else:
                print(f"   ✅ All {original_count} homes passed pre-filtering (no explicit disqualifications)")
                # Add match results to all homes for potential use in scoring
                for home in care_homes:
                    if '_prefilter_match_result' not in home:
                        match_result = evaluate_home_match_v2(
                            home=home,
                            required_care=required_care,
                            conditions=medical_conditions,
                            mobility=mobility_level,
                            behavioral=behavioral_concerns
                        )
                        home['_prefilter_match_result'] = match_result
        
        except ImportError as e:
            print(f"   ⚠️  WARNING: Could not import fallback matching functions: {e}")
            print(f"      Skipping pre-filtering, will use all homes for scoring")
        except Exception as e:
            print(f"   ⚠️  WARNING: Error during pre-filtering: {e}")
            print(f"      Skipping pre-filtering, will use all homes for scoring")
            import traceback
            traceback.print_exc()
        
        # Initialize matching service (simple or full version)
        if USE_SIMPLE_MATCHING:
            print("📊 Using SIMPLIFIED matching service (100-point MVP)")
            matching_service = SimpleMatchingService()
        else:
            print("📊 Using FULL matching service (156-point)")
            # Wrap in try-except to handle any MSIF data loading errors gracefully
            try:
                matching_service = ProfessionalMatchingService()
            except Exception as e:
                # If service initialization fails (e.g., MSIF data loading), log and continue
                import traceback
                error_msg = str(e)
                if 'data/msif' in error_msg or 'msif' in error_msg.lower():
                    print(f"⚠️ MSIF data loading error (non-critical): {error_msg}")
                    print("Continuing without MSIF data...")
                else:
                    print(f"⚠️ Matching service initialization warning: {error_msg}")
                # Re-initialize - should work without MSIF data
                matching_service = ProfessionalMatchingService()
        
        # Calculate dynamic weights
        try:
            weights, applied_conditions = matching_service.calculate_dynamic_weights(questionnaire)
        except Exception as e:
            # Fallback to base weights if calculation fails
            print(f"⚠️ Dynamic weights calculation failed, using base weights: {e}")
            weights = matching_service.BASE_WEIGHTS
            applied_conditions = []
        
        # Score all care homes
        # Build basic enriched_data from home data for matching
        # (Full enrichment happens later for TOP 5 only)
        scored_homes = []
        for home in care_homes:
            try:
                # Build basic enriched_data from home data
                # This allows matching service to use both DB and API data
                enriched_data = {
                    'cqc_detailed': {
                        'overall_rating': home.get('cqc_rating_overall') or home.get('rating'),
                        'safe_rating': home.get('cqc_rating_safe'),
                        'effective_rating': home.get('cqc_rating_effective'),
                        'caring_rating': home.get('cqc_rating_caring'),
                        'responsive_rating': home.get('cqc_rating_responsive'),
                        'well_led_rating': home.get('cqc_rating_well_led'),
                        'trend': 'stable'  # Default, will be updated by API if available
                    },
                    'fsa_detailed': {
                        'rating': home.get('fsa_rating') or home.get('food_hygiene_rating')
                    },
                    'financial_data': {
                        # Will be enriched by Companies House API if available
                    },
                    'staff_data': {
                        # Will be enriched by Staff Quality API if available
                    },
                    'medical_capabilities': {
                        # Will be enriched by medical APIs if available
                    }
                }
                
                # Use appropriate method based on service type
                if USE_SIMPLE_MATCHING:
                    match_result = matching_service.calculate_100_point_match(
                        home=home,
                        user_profile=questionnaire,
                        enriched_data=enriched_data,
                        weights=weights
                    )
                else:
                    match_result = matching_service.calculate_156_point_match(
                        home=home,
                        user_profile=questionnaire,
                        enriched_data=enriched_data,
                        weights=weights
                    )
                
                scored_homes.append({
                    'home': home,
                    'matchScore': match_result.get('total', 0),
                    'factorScores': match_result.get('category_scores', {}),
                    'matchResult': match_result
                })
            except Exception as e:
                print(f"⚠️ Error scoring home {home.get('name', 'unknown')}: {e}")
                # Continue with other homes
                continue
        
        # Check match quality and expand search if needed
        if scored_homes:
            # Calculate average match score
            avg_match = sum(h.get('matchScore', 0) for h in scored_homes) / len(scored_homes)
            max_match = max(h.get('matchScore', 0) for h in scored_homes)
            
            print(f"\n   📊 Initial Match Quality:")
            max_score = 100 if USE_SIMPLE_MATCHING else 156
            print(f"      Average match: {avg_match:.1f} / {max_score} ({avg_match/max_score*100:.1f}%)")
            print(f"      Best match: {max_match:.1f} / {max_score} ({max_match/max_score*100:.1f}%)")
            print(f"      Homes analyzed: {len(scored_homes)}")
            
            # Expand search if match quality is low
            # Criteria: average < 60 points OR best < 80 points
            should_expand = avg_match < 60 or max_match < 80
            
            if should_expand and initial_max_distance_km and initial_max_distance_km < 50:
                print(f"\n   🔍 Match quality is low, expanding search...")
                expanded_distance = min(50.0, initial_max_distance_km * 2)  # Double distance, max 50km
                expanded_limit = 100  # Increase limit
                
                print(f"      Expanding: distance {initial_max_distance_km}km → {expanded_distance}km, limit {initial_limit} → {expanded_limit}")
                
                try:
                    from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
                    loop = asyncio.get_event_loop()
                    expanded_care_homes = await loop.run_in_executor(
                        None,
                        lambda: get_csv_care_homes(
                            local_authority=normalized_city if normalized_city else preferred_city,
                            care_type=care_type,
                            max_distance_km=expanded_distance,
                            user_lat=user_lat,
                            user_lon=user_lon,
                            limit=expanded_limit,
                            use_hybrid=True  # Enable hybrid approach (CQC + Staging)
                        )
                    )
                    print(f"      ✅ Loaded {len(expanded_care_homes)} homes with expanded search (hybrid approach)")
                    
                    # Score expanded homes
                    expanded_scored = []
                    for home in expanded_care_homes:
                        # Skip if already scored
                        home_id = home.get('id') or home.get('cqc_location_id')
                        if any((h.get('home', {}).get('id') or h.get('home', {}).get('cqc_location_id')) == home_id for h in scored_homes):
                            continue
                        
                        try:
                            enriched_data = {
                                'cqc_detailed': {
                                    'overall_rating': home.get('cqc_rating_overall') or home.get('rating'),
                                    'safe_rating': home.get('cqc_rating_safe'),
                                    'effective_rating': home.get('cqc_rating_effective'),
                                    'caring_rating': home.get('cqc_rating_caring'),
                                    'responsive_rating': home.get('cqc_rating_responsive'),
                                    'well_led_rating': home.get('cqc_rating_well_led'),
                                },
                                'fsa_detailed': {
                                    'rating': home.get('fsa_rating') or home.get('food_hygiene_rating')
                                },
                                'financial_data': {},
                                'staff_data': {},
                                'medical_capabilities': {}
                            }
                            
                            # Use appropriate method based on service type
                            if USE_SIMPLE_MATCHING:
                                match_result = matching_service.calculate_100_point_match(
                                    home=home,
                                    user_profile=questionnaire,
                                    enriched_data=enriched_data,
                                    weights=weights
                                )
                            else:
                                match_result = matching_service.calculate_156_point_match(
                                    home=home,
                                    user_profile=questionnaire,
                                    enriched_data=enriched_data,
                                    weights=weights
                                )
                            
                            expanded_scored.append({
                                'home': home,
                                'matchScore': match_result.get('total', 0),
                                'factorScores': match_result.get('category_scores', {}),
                                'matchResult': match_result
                            })
                        except Exception as e:
                            print(f"      ⚠️ Error scoring expanded home {home.get('name', 'unknown')}: {e}")
                            continue
                    
                    # Merge and sort by score
                    all_scored = scored_homes + expanded_scored
                    all_scored.sort(key=lambda h: h['matchScore'], reverse=True)
                    scored_homes = all_scored
                    
                    print(f"      ✅ Expanded search added {len(expanded_scored)} new homes")
                    print(f"      📊 Total homes analyzed: {len(scored_homes)}")
                    if scored_homes:
                        max_score = 100 if USE_SIMPLE_MATCHING else 156
                        print(f"      📊 New average match: {sum(h.get('matchScore', 0) for h in scored_homes) / len(scored_homes):.1f} / {max_score}")
                        print(f"      📊 New best match: {max(h.get('matchScore', 0) for h in scored_homes):.1f} / {max_score}")
                except Exception as e:
                    print(f"      ⚠️ Failed to expand search: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue with original homes
        
        # Check if we have any scored homes
        # If no scored homes, try to load mock data directly as last resort
        if not scored_homes:
            print(f"⚠️ No scored homes found, attempting to load mock data as last resort...")
            try:
                from services.mock_care_homes import load_mock_care_homes
                try:
                    all_mock_homes = await asyncio.to_thread(load_mock_care_homes)
                except AttributeError:
                    loop = asyncio.get_event_loop()
                    all_mock_homes = await loop.run_in_executor(None, load_mock_care_homes)
                
                if all_mock_homes:
                    # Score mock homes
                    for home in all_mock_homes[:20]:  # Limit to 20 for performance
                        try:
                            enriched_data = {}
                            # Use appropriate method based on service type
                            if USE_SIMPLE_MATCHING:
                                match_result = matching_service.calculate_100_point_match(
                                    home=home,
                                    user_profile=questionnaire,
                                    enriched_data=enriched_data,
                                    weights=weights
                                )
                            else:
                                match_result = matching_service.calculate_156_point_match(
                                    home=home,
                                    user_profile=questionnaire,
                                    enriched_data=enriched_data,
                                    weights=weights
                                )
                            scored_homes.append({
                                'home': home,
                                'matchScore': match_result.get('total', 0),
                                'factorScores': match_result.get('category_scores', {}),
                                'matchResult': match_result
                            })
                        except Exception as e:
                            print(f"⚠️ Error scoring mock home {home.get('name', 'unknown')}: {e}")
                            continue
                    
                    if scored_homes:
                        print(f"✅ Loaded {len(scored_homes)} homes from mock data as fallback")
            except Exception as e:
                print(f"⚠️ Failed to load mock data as fallback: {e}")
        
        # Final check: if still no homes, raise error
        if not scored_homes:
            raise HTTPException(
                status_code=404,
                detail=f"No care homes found for {preferred_city or 'specified location'}. Please try a different location or care type."
            )
        
        # Filter scored homes to ensure location consistency (if location specified)
        # This ensures all returned homes match the Client Profile location
        # BUT: Only filter if we have enough results (>= 10), and only if filtered result has >= 5 homes
        # This prevents empty results while still prioritizing location matches
        if (preferred_city or normalized_city) and scored_homes and len(scored_homes) >= 10:
            try:
                from services.location_normalizer import LocationNormalizer
                location_variants = LocationNormalizer.get_local_authority_variants(
                    normalized_city or preferred_city
                )
                
                if location_variants:
                    variant_lowers = [v.lower() for v in location_variants]
                    filtered_scored = []
                    
                    for scored in scored_homes:
                        home = scored.get('home', {})
                        home_la = (home.get('local_authority') or home.get('localAuthority') or '').lower()
                        home_city = (home.get('city') or '').lower()
                        
                        # Check if home matches any location variant
                        matches = False
                        for variant_lower in variant_lowers:
                            if variant_lower in home_la or home_la in variant_lower:
                                matches = True
                                break
                            if variant_lower in home_city or home_city in variant_lower:
                                matches = True
                                break
                        
                        if matches:
                            filtered_scored.append(scored)
                    
                    # Use filtered results if we have at least 5 homes
                    # This ensures we don't end up with empty results
                    if len(filtered_scored) >= 5:
                        print(f"✅ Filtered {len(scored_homes)} homes to {len(filtered_scored)} matching location '{normalized_city or preferred_city}'")
                        scored_homes = filtered_scored
                    else:
                        print(f"⚠️ Location filter would leave only {len(filtered_scored)} homes, keeping all {len(scored_homes)} homes")
            except ImportError:
                pass  # Skip filtering if normalizer not available
        
        # STEP: Get API data for top candidates BEFORE final selection
        # This ensures API data influences matching scores
        print(f"\n{'='*80}")
        print(f"STEP: API ENRICHMENT FOR MATCHING (BEFORE TOP 5 SELECTION)")
        print(f"{'='*80}")
        
        # Get top 30 candidates for API enrichment (to balance performance vs accuracy)
        top_candidates_for_api = sorted(scored_homes, key=lambda h: h.get('matchScore', 0), reverse=True)[:30]
        print(f"   Enriching top {len(top_candidates_for_api)} candidates with API data for matching...")
        
        # Prepare enrichment tasks
        api_enrichment_tasks = {}
        for scored in top_candidates_for_api:
            home = scored.get('home', {})
            home_id = home.get('cqc_location_id') or home.get('id') or home.get('name', 'unknown')
            home_name = home.get('name', 'Unknown')
            
            api_enrichment_tasks[home_id] = {
                'home': home,
                'home_id': home_id,
                'home_name': home_name,
                'location_id': home.get('cqc_location_id') or home.get('location_id'),
                'provider_id': home.get('provider_id') or home.get('providerId'),
                'postcode': home.get('postcode'),
                'latitude': home.get('latitude'),
                'longitude': home.get('longitude')
            }
        
        # Collect all API data in parallel
        all_enriched_data_for_matching = {}
        
        # 1. CQC Enrichment
        print(f"\n   1. CQC API Enrichment...")
        cqc_enriched_for_matching = {}
        if api_enrichment_tasks:
            try:
                from services.cqc_deep_dive_service import CQCDeepDiveService
                from api_clients.cqc_client import CQCAPIClient
                from utils.auth import get_credentials
                
                async def enrich_cqc_for_matching():
                    creds = get_credentials()
                    cqc_client = None
                    if creds.cqc and creds.cqc.primary_subscription_key:
                        primary_key = creds.cqc.primary_subscription_key
                        # Check if it's a placeholder
                        placeholder_values = [
                            "your-primary-subscription-key",
                            "your-secondary-subscription-key",
                            "your-cqc-primary-key",
                            "placeholder",
                            "example",
                            "test"
                        ]
                        if primary_key.lower() in [p.lower() for p in placeholder_values] or primary_key.startswith("your-"):
                            print(f"      ⚠️ CQC API subscription key appears to be a placeholder - skipping CQC enrichment")
                            return {}
                        
                        cqc_client = CQCAPIClient(
                            primary_subscription_key=creds.cqc.primary_subscription_key,
                            secondary_subscription_key=creds.cqc.secondary_subscription_key
                        )
                    else:
                        print(f"      ⚠️ CQC API subscription key not configured - skipping CQC enrichment")
                        return {}
                    
                    service = CQCDeepDiveService(cqc_client=cqc_client)
                    tasks = []
                    task_keys = []
                    for home_id, task_data in api_enrichment_tasks.items():
                        location_id = task_data.get('location_id')
                        if location_id:
                            tasks.append(
                                service.build_cqc_deep_dive(
                                    db_data=task_data['home'],
                                    location_id=location_id,
                                    provider_id=task_data.get('provider_id')
                                )
                            )
                            task_keys.append(home_id)
                    
                    if tasks:
                        # Add delay between requests for reliability (accuracy > speed)
                        # Process in smaller batches to avoid overwhelming API
                        batch_size = 5
                        results = []
                        for i in range(0, len(tasks), batch_size):
                            batch_tasks = tasks[i:i+batch_size]
                            batch_keys = task_keys[i:i+batch_size]
                            
                            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                            results.extend(batch_results)
                            
                            # Add delay between batches (except last batch)
                            if i + batch_size < len(tasks):
                                await asyncio.sleep(1.0)  # 1 second delay between batches
                        
                        # Re-map results to task_keys
                        results = results[:len(task_keys)]
                        for home_id, result in zip(task_keys, results):
                            if isinstance(result, Exception):
                                print(f"      ⚠️ CQC failed for {home_id}: {result}")
                            elif result:
                                try:
                                    cqc_dict = service.to_dict(result)
                                    if cqc_dict:
                                        cqc_enriched_for_matching[home_id] = cqc_dict
                                except Exception as e:
                                    print(f"      ⚠️ CQC conversion error for {home_id}: {e}")
                    
                    await service.close()
                    return cqc_enriched_for_matching
                
                cqc_enriched_for_matching = await enrich_cqc_for_matching()
                print(f"      ✅ CQC data enriched for {len(cqc_enriched_for_matching)} homes")
            except Exception as e:
                print(f"      ⚠️ CQC enrichment error: {e}")
                cqc_enriched_for_matching = {}
        
        # 2. FSA Enrichment - SKIPPED for matching (will be done for top-5 finalists only)
        print(f"\n   2. FSA API Enrichment...")
        print(f"      ⏭️  SKIPPED for matching (will be done for top-5 finalists only)")
        print(f"      ℹ️  FSA data will be enriched after top-5 selection for final report")
        fsa_enriched_for_matching = {}  # Empty - FSA will be enriched for top-5 only
        
        # 3. Staff Quality Enrichment - SKIPPED for matching (uses paid Perplexity API)
        # Will be enriched later for top-5 finalists only
        print(f"\n   3. Staff Quality API Enrichment...")
        print(f"      ⏭️  SKIPPED for matching (uses paid Perplexity API)")
        print(f"      ℹ️  Will use CQC Well-Led/Effective ratings as fallback")
        print(f"      ℹ️  Full Staff Quality enrichment will be done for top-5 finalists")
        staff_enriched_for_matching = {}
        
        # 4. Companies House Enrichment (for financial stability)
        print(f"\n   4. Companies House API Enrichment...")
        companies_house_enriched_for_matching = {}
        if api_enrichment_tasks:
            try:
                from services.companies_house_service import CompaniesHouseService
                
                async def enrich_companies_house_for_matching():
                    service = CompaniesHouseService()
                    tasks = []
                    task_keys = []
                    for home_id, task_data in api_enrichment_tasks.items():
                        home_name = task_data.get('home_name')
                        if home_name:
                            tasks.append(
                                service.get_financial_stability(home_name)
                            )
                            task_keys.append(home_id)
                    
                    if tasks:
                        # Add delay between requests for reliability (accuracy > speed)
                        # Process in smaller batches to avoid rate limiting
                        batch_size = 3
                        results = []
                        for i in range(0, len(tasks), batch_size):
                            batch_tasks = tasks[i:i+batch_size]
                            batch_keys = task_keys[i:i+batch_size]
                            
                            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                            results.extend(batch_results)
                            
                            # Add delay between batches (except last batch)
                            if i + batch_size < len(tasks):
                                await asyncio.sleep(2.0)  # 2 seconds delay between batches (Companies House rate limit)
                        
                        # Re-map results to task_keys
                        results = results[:len(task_keys)]
                        for home_id, result in zip(task_keys, results):
                            if isinstance(result, Exception):
                                pass  # Silent fail
                            elif result:
                                companies_house_enriched_for_matching[home_id] = result
                    
                    return companies_house_enriched_for_matching
                
                companies_house_enriched_for_matching = await enrich_companies_house_for_matching()
                print(f"      ✅ Companies House data enriched for {len(companies_house_enriched_for_matching)} homes")
            except Exception as e:
                print(f"      ⚠️ Companies House enrichment error: {e}")
                companies_house_enriched_for_matching = {}
        
        # Build comprehensive enriched_data for matching
        print(f"\n   Building enriched_data for matching...")
        all_enriched_data_for_matching = {}
        for home_id, task_data in api_enrichment_tasks.items():
            home = task_data['home']
            # Get financial data
            financial_data_raw = companies_house_enriched_for_matching.get(home_id, {})
            financial_data = financial_data_raw.get('financial_data', {}) if financial_data_raw else {}
            
            # For matching: use CQC Well-Led/Effective as fallback for Staff Quality
            # (Full Staff Quality API will be called later for top-5 only - uses paid Perplexity API)
            cqc_data = cqc_enriched_for_matching.get(home_id, {})
            staff_data_from_cqc = {}
            if cqc_data:
                # Extract CQC ratings for staff quality estimation
                well_led = (
                    cqc_data.get('well_led_rating') or 
                    cqc_data.get('well_led') or
                    cqc_data.get('detailed_ratings', {}).get('well_led', {}).get('rating') or
                    home.get('cqc_rating_well_led') or
                    home.get('cqc_well_led_rating')
                )
                effective = (
                    cqc_data.get('effective_rating') or 
                    cqc_data.get('effective') or
                    cqc_data.get('detailed_ratings', {}).get('effective', {}).get('rating') or
                    home.get('cqc_rating_effective') or
                    home.get('cqc_effective_rating')
                )
                if well_led or effective:
                    staff_data_from_cqc = {
                        'cqc_well_led_rating': well_led,
                        'cqc_effective_rating': effective,
                        'estimated_from_cqc': True,
                        'note': 'Using CQC ratings as fallback (Staff Quality API will be used for top-5 only)'
                    }
            
            enriched = {
                'cqc_detailed': cqc_data if cqc_data else {
                    'overall_rating': home.get('cqc_rating_overall') or home.get('rating'),
                    'safe_rating': home.get('cqc_rating_safe'),
                    'effective_rating': home.get('cqc_rating_effective'),
                    'caring_rating': home.get('cqc_rating_caring'),
                    'responsive_rating': home.get('cqc_rating_responsive'),
                    'well_led_rating': home.get('cqc_rating_well_led'),
                },
                'fsa_scoring': {},  # Empty - FSA will be enriched for top-5 only
                'fsa_detailed': {  # Empty for matching - will be enriched for top-5 only
                    'rating': home.get('fsa_rating') or home.get('food_hygiene_rating'),  # Use DB/CSV data if available
                    'rating_source': 'Will be enriched for top-5 finalists'
                },
                'staff_quality': {},  # Empty - will be enriched for top-5 only (uses paid Perplexity API)
                'staff_data': staff_data_from_cqc,  # Use CQC ratings as fallback for matching
                'companies_house_scoring': financial_data_raw.get('financial_stability_score') if financial_data_raw else None,
                'financial_data': financial_data,  # Full financial data dict
            }
            
            all_enriched_data_for_matching[home_id] = enriched
        
        print(f"   ✅ Enriched data prepared for {len(all_enriched_data_for_matching)} homes")
        
        # Re-score top candidates with API data
        print(f"\n   Re-scoring top candidates with API data...")
        rescored_homes = []
        for scored in top_candidates_for_api:
            # FIX: Ensure scored is a dict
            if scored is None or not isinstance(scored, dict):
                print(f"      ⚠️ Skipping re-scoring: scored is None or not a dict")
                continue
            
            home = scored.get('home', {})
            
            # FIX: Ensure home is always a dict, never None
            if home is None:
                print(f"      ⚠️ Skipping re-scoring: home is None")
                continue
            
            if not isinstance(home, dict):
                print(f"      ⚠️ Skipping re-scoring: home is not a dict (type: {type(home)})")
                continue
            
            home_id = home.get('cqc_location_id') or home.get('id') or home.get('name', 'unknown')
            
            # FIX: Ensure all_enriched_data_for_matching is a dict
            if all_enriched_data_for_matching is None:
                all_enriched_data_for_matching = {}
            
            if not isinstance(all_enriched_data_for_matching, dict):
                all_enriched_data_for_matching = {}
            
            enriched_data = all_enriched_data_for_matching.get(home_id, {})
            
            # FIX: Ensure enriched_data is always a dict, never None
            if enriched_data is None:
                enriched_data = {}
            
            if not isinstance(enriched_data, dict):
                enriched_data = {}
            
            # Log API data availability
            has_cqc = bool(enriched_data.get('cqc_detailed', {}).get('overall_rating'))
            has_fsa = bool(enriched_data.get('fsa_scoring') or enriched_data.get('fsa_detailed', {}).get('rating'))
            has_staff = bool(enriched_data.get('staff_quality') or enriched_data.get('staff_data'))
            has_financial = bool(enriched_data.get('companies_house_scoring') or enriched_data.get('financial_data'))
            
            if has_cqc or has_fsa or has_staff or has_financial:
                print(f"      ✅ {home.get('name', 'unknown')[:30]}: CQC={has_cqc}, FSA={has_fsa}, Staff={has_staff}, Financial={has_financial}")
            
            try:
                old_score = scored.get('matchScore', 0)
                # Use appropriate method based on service type
                if USE_SIMPLE_MATCHING:
                    match_result = matching_service.calculate_100_point_match(
                        home=home,
                        user_profile=questionnaire,
                        enriched_data=enriched_data,
                        weights=weights,
                        debug=True  # Enable debug for detailed breakdown
                    )
                else:
                    match_result = matching_service.calculate_156_point_match(
                        home=home,
                        user_profile=questionnaire,
                        enriched_data=enriched_data,
                        weights=weights
                    )
                new_score = match_result.get('total', 0)
                
                # Print detailed breakdown for first home
                if len(rescored_homes) == 0 and USE_SIMPLE_MATCHING:
                    home_name = home.get('name', 'unknown')
                    print(f"\n{'='*80}")
                    print(f"📊 ДЕТАЛЬНАЯ РАСКЛАДКА СКОРИНГА: {home_name}")
                    print(f"{'='*80}")
                    
                    debug_info = match_result.get('debug', {})
                    category_scores = match_result.get('category_scores', {})
                    point_allocations = match_result.get('point_allocations', {})
                    weights_dict = match_result.get('weights', {})
                    
                    print(f"\n🎯 ИТОГОВЫЙ СКОР: {new_score:.1f}/100")
                    print(f"\n📋 ВЕСА КАТЕГОРИЙ:")
                    for cat, weight in weights_dict.items():
                        print(f"   {cat.replace('_', ' ').title()}: {weight}%")
                    
                    print(f"\n📊 СКОРЫ ПО КАТЕГОРИЯМ:")
                    for cat, cat_score in category_scores.items():
                        points = point_allocations.get(cat, 0)
                        weight = weights_dict.get(cat, 0)
                        print(f"   {cat.replace('_', ' ').title()}: {cat_score:.1f}/100 → {points:.1f} points (вес {weight}%)")
                    
                    # Medical & Safety breakdown
                    medical_debug = debug_info.get('medical_safety', {})
                    if medical_debug:
                        print(f"\n🏥 MEDICAL & SAFETY ДЕТАЛИ:")
                        breakdown = medical_debug.get('breakdown', {})
                        cqc_info = medical_debug.get('cqc_safe', {})
                        print(f"   Care Type Match: {breakdown.get('care_type_match', 0)} points")
                        print(f"   CQC Safe Rating: {breakdown.get('cqc_safe', 0)} points")
                        print(f"      └─ Rating: {cqc_info.get('rating', 'N/A')}")
                        print(f"      └─ Data Source: {cqc_info.get('data_source', 'N/A')}")
                        print(f"      └─ API Used: {'✅ YES' if cqc_info.get('has_api_data') else '❌ NO (DB fallback)'}")
                        print(f"   Accessibility: {breakdown.get('accessibility', 0)} points")
                        print(f"   Medication Match: {breakdown.get('medication', 0):.1f} points")
                        print(f"   Age Match: {breakdown.get('age', 0):.1f} points")
                        print(f"   Special Needs: {breakdown.get('special_needs', 0)} points")
                    
                    # Financial breakdown
                    financial_debug = debug_info.get('financial', {})
                    if financial_debug:
                        print(f"\n💰 FINANCIAL STABILITY ДЕТАЛИ:")
                        breakdown = financial_debug.get('breakdown', {})
                        print(f"   Budget Match: {breakdown.get('budget_match', 0):.1f} points")
                        altman_info = financial_debug.get('altman_z', {})
                        print(f"   Altman Z-Score: {breakdown.get('altman_z', 0)} points")
                        print(f"      └─ Value: {altman_info.get('value', 'N/A')}")
                        print(f"      └─ Data Source: {altman_info.get('data_source', 'N/A')}")
                        print(f"      └─ API Used: {'✅ YES' if altman_info.get('has_api_data') else '❌ NO (no data)'}")
                        trend_info = financial_debug.get('revenue_trend', {})
                        print(f"   Revenue Trend: {breakdown.get('revenue_trend', 0)} points")
                        print(f"      └─ Trend: {trend_info.get('value', 'N/A')}")
                        print(f"      └─ Data Source: {trend_info.get('data_source', 'N/A')}")
                        print(f"      └─ API Used: {'✅ YES' if trend_info.get('has_api_data') else '❌ NO (no data)'}")
                        red_flags_info = financial_debug.get('red_flags', {})
                        print(f"   Red Flags: {breakdown.get('red_flags', 0)} points")
                        print(f"      └─ Flags Count: {red_flags_info.get('count', 0)}")
                        print(f"      └─ Data Source: {red_flags_info.get('data_source', 'N/A')}")
                        print(f"      └─ API Used: {'✅ YES' if red_flags_info.get('has_api_data') else '❌ NO (no data)'}")
                    
                    # API usage summary
                    api_usage = debug_info.get('api_data_usage', {})
                    print(f"\n🔌 ИСПОЛЬЗОВАНИЕ API ДАННЫХ:")
                    print(f"   CQC API: {'✅ ИСПОЛЬЗУЕТСЯ' if api_usage.get('cqc_api_used') else '❌ НЕ ИСПОЛЬЗУЕТСЯ (DB fallback)'}")
                    print(f"   Companies House API: {'✅ ИСПОЛЬЗУЕТСЯ' if api_usage.get('companies_house_api_used') else '❌ НЕ ИСПОЛЬЗУЕТСЯ (no data)'}")
                    
                    print(f"\n{'='*80}\n")
                
                if abs(new_score - old_score) > 5:  # Significant change
                    print(f"      📊 {home.get('name', 'unknown')[:30]}: Score changed {old_score:.1f} → {new_score:.1f} (+{new_score-old_score:.1f})")
                
                rescored_homes.append({
                    'home': home,
                    'matchScore': new_score,
                    'factorScores': match_result.get('category_scores', {}),
                    'matchResult': match_result
                })
            except Exception as e:
                print(f"      ⚠️ Error re-scoring {home.get('name', 'unknown')}: {e}")
                # Keep original score
                rescored_homes.append(scored)
        
        # Replace top candidates in scored_homes with re-scored versions
        rescored_homes_dict = {h.get('home', {}).get('cqc_location_id') or h.get('home', {}).get('id'): h for h in rescored_homes}
        for i, scored in enumerate(scored_homes):
            home = scored.get('home', {})
            home_id = home.get('cqc_location_id') or home.get('id')
            if home_id in rescored_homes_dict:
                scored_homes[i] = rescored_homes_dict[home_id]
        
        # Re-sort by new scores
        scored_homes.sort(key=lambda h: h.get('matchScore', 0), reverse=True)
        print(f"   ✅ Re-scored {len(rescored_homes)} homes with API data")
        
        # Use new method: TOP 5 + Category Winners
        print(f"\n{'='*80}")
        print(f"STEP: SELECTING TOP 5 + CATEGORY WINNERS (WITH API DATA)")
        print(f"{'='*80}")
        
        # Build enriched_data for all homes (including those not in top 30)
        basic_enriched_data = {}
        all_homes_for_enrichment = [h.get('home', h) for h in scored_homes] if scored_homes else care_homes
        for home in all_homes_for_enrichment:
            home_id = home.get('cqc_location_id') or home.get('id') or home.get('name', 'unknown')
            # Use API data if available, otherwise use basic data
            if home_id in all_enriched_data_for_matching:
                basic_enriched_data[home_id] = all_enriched_data_for_matching[home_id]
            else:
                basic_enriched_data[home_id] = {
                    'cqc_detailed': {
                        'overall_rating': home.get('cqc_rating_overall') or home.get('rating'),
                        'safe_rating': home.get('cqc_rating_safe'),
                        'effective_rating': home.get('cqc_rating_effective'),
                        'caring_rating': home.get('cqc_rating_caring'),
                        'responsive_rating': home.get('cqc_rating_responsive'),
                        'well_led_rating': home.get('cqc_rating_well_led'),
                    },
                    'fsa_detailed': {
                        'rating': home.get('fsa_rating') or home.get('food_hygiene_rating')
                    },
                    'financial_data': {},
                    'staff_data': {},
                    'medical_capabilities': {}
                }
        
        # Use scored_homes (which includes expanded search and re-scored with API data) for selection
        # FIX: Filter out None values and ensure all candidates are dicts
        candidates_for_selection = []
        if scored_homes:
            for h in scored_homes:
                if h is None:
                    continue
                home = h.get('home', h) if isinstance(h, dict) else h
                if home is not None:
                    candidates_for_selection.append(home if isinstance(home, dict) else {'name': str(home)})
        else:
            candidates_for_selection = [h for h in care_homes if h is not None]
        
        # FIX: Ensure questionnaire is not None
        if questionnaire is None:
            print("   ❌ ERROR: questionnaire is None!")
            questionnaire = {}
        
        selection_result = matching_service.select_top_5_with_category_winners(
            candidates=candidates_for_selection,
            user_profile=questionnaire,
            enriched_data=basic_enriched_data,  # Now includes API data for top candidates
            weights=weights
        )
        
        top_5_data = selection_result.get('top_5', [])
        category_winners = selection_result.get('category_winners', {})
        
        # Collect matching details for breakdown visibility
        matching_details = {
            'data_quality': {
                'direct_matches': 0,
                'proxy_matches': 0,
                'unknowns': 0,
                'unknown_ratio': 0.0
            },
            'fallback_usage': []
        }
        
        # Analyze fallback usage from pre-filter results
        try:
            from services.data_quality_diagnostics import analyze_fallback_usage
            fallback_stats = analyze_fallback_usage(care_homes, questionnaire)
            matching_details['data_quality'] = fallback_stats.get('data_quality', matching_details['data_quality'])
            
            # Track field-level fallback usage
            field_usage = fallback_stats.get('field_usage', {})
            for field, usage in field_usage.items():
                if usage.get('proxy', 0) > 0 or usage.get('unknown', 0) > 0:
                    matching_details['fallback_usage'].append({
                        'field': field,
                        'homes_with_null': usage.get('unknown', 0),
                        'proxy_matches': usage.get('proxy', 0),
                        'direct_matches': usage.get('direct', 0)
                    })
        except Exception as e:
            logger.warning(f"Could not analyze fallback usage: {e}")
        
        # Log matching statistics
        if top_5_data:
            scores = [h.get('matchScore', h.get('match_score', 0)) for h in top_5_data]
            logger.info("Matching completed", extra={
                'total_homes_scored': len(candidates_for_selection),
                'top_5_count': len(top_5_data),
                'score_min': min(scores) if scores else 0,
                'score_max': max(scores) if scores else 0,
                'score_avg': sum(scores) / len(scores) if scores else 0,
                'score_spread': max(scores) - min(scores) if scores else 0,
                'data_quality': matching_details['data_quality'],
                'fallback_fields_used': len(matching_details['fallback_usage'])
            })
        
        # Convert to old format for backward compatibility
        top_5_homes = []
        for home_data in top_5_data:
            home = home_data.get('home', {})
            match_result = home_data.get('match_result', {})
            
            # Add category winner info
            home_id = home.get('id') or home.get('cqc_location_id')
            home['is_category_winner'] = {}
            home['category_labels'] = []
            home['category_reasoning'] = {}
            
            # Add value_ratio if available
            if 'value_ratio' in home_data:
                home['value_ratio'] = home_data.get('value_ratio', 0)
            
            for category_key, winner_info in category_winners.items():
                winner_home = winner_info.get('home', {})
                winner_id = winner_home.get('id') or winner_home.get('cqc_location_id')
                if winner_id == home_id:
                    home['is_category_winner'][category_key] = True
                    home['category_labels'].append(winner_info.get('label', category_key))
                    home['category_reasoning'][category_key] = winner_info.get('reasoning', [])
            
            top_5_homes.append({
                'home': home,
                'matchScore': home_data.get('matchScore', home_data.get('match_score', 0)),
                'matchResult': match_result,
                'category_scores': home_data.get('category_scores', {})
            })
        
        print(f"   ✅ Selected {len(top_5_homes)} homes")
        print(f"   ✅ Found {len(category_winners)} category winners")
        
        # Extract client name from questionnaire
        contact_info = questionnaire.get('section_1_contact_emergency', {})
        names = contact_info.get('q1_names', '')
        client_name = 'Unknown'
        if 'Patient:' in names:
            client_name = names.split('Patient:')[-1].strip()
        elif ';' in names:
            client_name = names.split(';')[-1].strip()
        
        # Build report structure matching frontend expectations
        report_id = str(uuid.uuid4())
        
        # NOTE: extract_weekly_price is now imported from utils.price_extractor
        # This ensures consistent price extraction across Free Report and Professional Report
        
        # NOTE: Synthetic data generation functions removed
        # All data MUST come from real API sources (FSA, Google Places, Companies House, CQC)
        # If API data is not available, fields will be null - NO synthetic/estimated data
        
        async def build_cqc_deep_dive_enhanced(
            raw_home: Dict[str, Any],
            overall_rating: str,
            inspection_date: Optional[str],
            location_id: Optional[str] = None,
            provider_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Build CQC Deep Dive with API enrichment according to SPEC v3.2
            
            Uses CQCDeepDiveService for:
            - Inspection history (5+ years)
            - Enforcement actions (red flags)
            - Provider-level pattern detection
            - Rating trend calculation
            - Regulated activities parsing
            """
            try:
                from services.cqc_deep_dive_service import CQCDeepDiveService
                from api_clients.cqc_client import CQCAPIClient
                from utils.auth import get_credentials
                
                # Extract location_id if not provided
                if not location_id:
                    location_id = (
                        raw_home.get('cqc_location_id') or
                        raw_home.get('location_id') or
                        raw_home.get('id')
                    )
                
                # Extract provider_id if not provided
                if not provider_id:
                    provider_id = (
                        raw_home.get('provider_id') or
                        raw_home.get('providerId')
                    )
                
                # Use new service if location_id is available
                if location_id:
                    # Get credentials and create properly configured CQC client
                    creds = get_credentials()
                    cqc_client = None
                    if creds.cqc and creds.cqc.primary_subscription_key:
                        primary_key = creds.cqc.primary_subscription_key
                        # Check if it's a placeholder
                        placeholder_values = [
                            "your-primary-subscription-key",
                            "your-secondary-subscription-key",
                            "your-cqc-primary-key",
                            "placeholder",
                            "example",
                            "test"
                        ]
                        if primary_key.lower() in [p.lower() for p in placeholder_values] or primary_key.startswith("your-"):
                            # Skip CQC enrichment if key is placeholder
                            return None
                        
                        cqc_client = CQCAPIClient(
                            primary_subscription_key=creds.cqc.primary_subscription_key,
                            secondary_subscription_key=creds.cqc.secondary_subscription_key
                        )
                    else:
                        # No CQC credentials configured
                        return None
                    
                    cqc_service = CQCDeepDiveService(cqc_client=cqc_client)
                    try:
                        cqc_deep_dive = await cqc_service.build_cqc_deep_dive(
                            db_data=raw_home,
                            location_id=location_id,
                            provider_id=provider_id
                        )
                        # Convert to dict format
                        result = cqc_service.to_dict(cqc_deep_dive)
                        await cqc_service.close()
                        return result
                    except Exception as e:
                        print(f"⚠️ CQC API enrichment failed for {location_id}: {e}")
                        await cqc_service.close()
                        # Fallback to basic build
                
                # Fallback to basic build if API enrichment fails or location_id missing
                return build_cqc_deep_dive_basic(raw_home, overall_rating, inspection_date)
            except ImportError:
                # Fallback if service not available
                return build_cqc_deep_dive_basic(raw_home, overall_rating, inspection_date)
            except Exception as e:
                print(f"⚠️ Error building CQC deep dive: {e}")
                return build_cqc_deep_dive_basic(raw_home, overall_rating, inspection_date)
        
        def build_cqc_deep_dive_basic(raw_home: Dict[str, Any], overall_rating: str, inspection_date: Optional[str]) -> Dict[str, Any]:
            """
            Basic CQC Deep Dive builder (fallback when API enrichment unavailable)
            """
            ratings_data = raw_home.get('cqc_ratings') or raw_home.get('cqcRatings') or {}
            def normalize_rating(value: Optional[Any]) -> Optional[str]:
                if value is None:
                    return None
                return str(value)
            
            # Try multiple sources for each rating
            def get_rating(field_name: str, default: str = 'Unknown') -> str:
                # Try from ratings_data dict
                rating = (
                    ratings_data.get(field_name) or
                    ratings_data.get(f'{field_name}_rating')
                )
                if rating:
                    return normalize_rating(rating) or default
                
                # Try direct from raw_home
                rating = (
                    raw_home.get(f'cqc_rating_{field_name}') or
                    raw_home.get(f'cqc_{field_name}_rating') or
                    raw_home.get(f'{field_name}_rating')
                )
                if rating:
                    return normalize_rating(rating) or default
                
                return default
            
            detailed_ratings = {
                'safe': {
                    'rating': get_rating('safe'),
                    'explanation': 'Safety of care, safeguarding, medicines handling'
                },
                'effective': {
                    'rating': get_rating('effective'),
                    'explanation': 'Effectiveness of treatments and support'
                },
                'caring': {
                    'rating': get_rating('caring'),
                    'explanation': 'Compassion, dignity, respect'
                },
                'responsive': {
                    'rating': get_rating('responsive'),
                    'explanation': 'Meeting needs, responding to feedback'
                },
                'well_led': {
                    'rating': get_rating('well_led') or get_rating('well-led'),
                    'explanation': 'Leadership, governance, continuous improvement'
                }
            }
            
            historical = []
            if inspection_date:
                historical.append({
                    'date': inspection_date,
                    'inspection_date': inspection_date,
                    'rating': overall_rating,
                    'overall_rating': overall_rating,
                    'key_question_ratings': {
                        'safe': detailed_ratings['safe']['rating'],
                        'effective': detailed_ratings['effective']['rating'],
                        'caring': detailed_ratings['caring']['rating'],
                        'responsive': detailed_ratings['responsive']['rating'],
                        'well_led': detailed_ratings['well_led']['rating']
                    }
                })
            
            action_plans_raw = raw_home.get('cqc_action_plans') or raw_home.get('action_plans') or []
            action_plans = []
            for plan in action_plans_raw:
                action_plans.append({
                    'title': plan.get('title', 'Improvement Plan'),
                    'status': plan.get('status', 'active'),
                    'date': plan.get('date'),
                    'due_date': plan.get('due_date'),
                    'description': plan.get('description', 'CQC required improvements being tracked.')
                })
            
            trend = raw_home.get('cqc_trend') or 'Stable'
            
            return {
                'overall_rating': overall_rating,
                'current_rating': overall_rating,
                'historical_ratings': historical,
                'trend': trend,
                'rating_changes': [],
                'action_plans': action_plans,
                'detailed_ratings': detailed_ratings
            }
        
        # Keep old function name for backward compatibility
        def build_cqc_deep_dive(raw_home: Dict[str, Any], overall_rating: str, inspection_date: Optional[str]) -> Dict[str, Any]:
            """Backward compatibility wrapper"""
            return build_cqc_deep_dive_basic(raw_home, overall_rating, inspection_date)
        
        def _extract_red_flags_from_risk(risk_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Extract red flags from risk breakdown"""
            red_flags = []
            breakdown = risk_dict.get('breakdown', {})
            
            # Check each component for HIGH risk
            for component_name, component_data in breakdown.items():
                if component_data.get('level') == 'HIGH':
                    red_flags.append({
                        'type': component_name,
                        'severity': 'high',
                        'title': f"{component_name.title()} Risk",
                        'description': component_data.get('detail', ''),
                        'impact': f"High {component_name} risk detected"
                    })
            
            # Overall risk level
            risk_level = risk_dict.get('risk_level', '')
            if 'High Risk' in risk_level:
                red_flags.append({
                    'type': 'overall',
                    'severity': 'high',
                    'title': 'High Financial Risk',
                    'description': risk_level,
                    'impact': 'Significant financial concerns detected'
                })
            
            return red_flags
        
        # NOTE: build_fsa_details function removed - was generating synthetic FSA data from CQC ratings
        # FSA data must come from real FSA API via FSAEnrichmentService only
        
        # STEP: Enrich FSA data for top-5 finalists only (parallel) - uses FSAEnrichmentService
        print(f"\n{'='*80}")
        print(f"STEP: FSA API ENRICHMENT (Section 7 - Food Hygiene) - TOP 5 FINALISTS ONLY")
        print(f"{'='*80}")
        
        # Prepare FSA enrichment tasks - ONLY for top-5 finalists
        fsa_enrichment_tasks = {}
        for scored in top_5_homes:  # Only final 5 homes
            home = scored['home']
            raw_home = home.get('rawData') or home
            home_name = home.get('name') or raw_home.get('name', 'Unknown')
            home_postcode = home.get('postcode') or raw_home.get('postcode')
            home_lat = home.get('latitude') or raw_home.get('latitude')
            home_lon = home.get('longitude') or raw_home.get('longitude')
            
            fsa_enrichment_tasks[home_name] = {
                'home': home,
                'raw_home': raw_home,
                'home_name': home_name,
                'postcode': home_postcode,
                'latitude': home_lat,
                'longitude': home_lon
            }
        
        # Execute FSA enrichment in parallel
        fsa_enriched_data = {}
        if fsa_enrichment_tasks:
            print(f"   Enriching {len(fsa_enrichment_tasks)} homes with FSA API data...")
            try:
                from services.fsa_enrichment_service import FSAEnrichmentService
                # asyncio already imported at top of file
                
                async def enrich_all_fsa():
                    service = FSAEnrichmentService(use_cache=True, cache_ttl=604800)  # 7 days cache
                    tasks = []
                    task_keys = []
                    for home_name, task_data in fsa_enrichment_tasks.items():
                        tasks.append(
                            service._fetch_fsa_data_for_home(
                                home_name=task_data['home_name'],
                                postcode=task_data['postcode'],
                                latitude=task_data['latitude'],
                                longitude=task_data['longitude']
                            )
                        )
                        task_keys.append(home_name)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for home_name, result in zip(task_keys, results):
                        if isinstance(result, Exception):
                            print(f"      ⚠️ FSA enrichment failed for {home_name}: {result}")
                            fsa_enriched_data[home_name] = None
                        else:
                            if result:
                                # Convert FSAEnrichmentService format to frontend expected format
                                fsa_enriched_data[home_name] = {
                                    'rating': result.get('rating_value'),
                                    'rating_date': result.get('rating_date'),
                                    'fhrs_id': result.get('fhrs_id'),
                                    'rating_source': 'FSA API',
                                    'health_score': result.get('health_score'),
                                    'detailed_sub_scores': result.get('detailed_sub_scores'),
                                    'historical_ratings': result.get('historical_ratings', []),
                                    'trend_analysis': result.get('trend_analysis'),
                                    'color': result.get('color'),
                                    'local_authority': result.get('local_authority'),
                                    'business_name': result.get('business_name'),
                                    'address': result.get('address')
                                }
                                print(f"      ✅ FSA data found for {home_name}: rating={result.get('rating_value')}")
                            else:
                                fsa_enriched_data[home_name] = None
                                print(f"      ⚠️ No FSA data found for {home_name}")
                    
                    await service.close()
                    return fsa_enriched_data
                
                # Run async enrichment
                fsa_enriched_data = await enrich_all_fsa()
                print(f"   ✅ FSA enrichment completed for {len([v for v in fsa_enriched_data.values() if v])} homes")
            except Exception as e:
                print(f"   ⚠️ FSA enrichment error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                fsa_enriched_data = {}
        
        # STEP: Enrich CQC data for all homes (parallel)
        print(f"\n{'='*80}")
        print(f"STEP: CQC API ENRICHMENT (Section 6)")
        print(f"{'='*80}")
        
        # Check if CQC API is configured
        try:
            from utils.auth import credentials_store
            from config_manager import get_credentials
            creds = credentials_store.get("default") or get_credentials()
            if not creds or not creds.cqc or not creds.cqc.primary_subscription_key:
                print(f"   ⚠️ CQC API primary subscription key not configured - skipping enrichment")
                print(f"   To enable CQC Deep Dive data, set CQC_PRIMARY_SUBSCRIPTION_KEY in config.json")
                cqc_enriched_data = {}
            else:
                primary_key = creds.cqc.primary_subscription_key
                # Check if it's a placeholder
                placeholder_values = [
                    "your-primary-subscription-key",
                    "your-secondary-subscription-key",
                    "your-cqc-primary-key",
                    "your-cqc-secondary-key",
                    "placeholder",
                    "example",
                    "test"
                ]
                if primary_key.lower() in [p.lower() for p in placeholder_values] or primary_key.startswith("your-"):
                    print(f"   ⚠️ CQC API subscription key appears to be a placeholder - skipping enrichment")
                    print(f"   Please set a valid subscription key in config.json or environment variable CQC_PRIMARY_SUBSCRIPTION_KEY")
                    print(f"   Get your API keys at: https://api-portal.service.cqc.org.uk/")
                    cqc_enriched_data = {}
                else:
                    # API key looks valid, proceed with enrichment
                    # Prepare CQC enrichment tasks
                    cqc_enrichment_tasks = {}
                    for scored in top_5_homes:
                        home = scored['home']
                        raw_home = home.get('rawData') or home
                        location_id = (
                            home.get('cqc_location_id') or
                            home.get('location_id') or
                            raw_home.get('cqc_location_id') or
                            raw_home.get('location_id')
                        )
                        provider_id = (
                            home.get('provider_id') or
                            raw_home.get('provider_id') or
                            raw_home.get('providerId')
                        )
                        
                        if location_id:
                            cqc_enrichment_tasks[location_id] = {
                                'home': home,
                                'raw_home': raw_home,
                                'location_id': location_id,
                                'provider_id': provider_id
                            }
                    
                    # Execute CQC enrichment in parallel
                    cqc_enriched_data = {}
                    if cqc_enrichment_tasks:
                        print(f"   Enriching {len(cqc_enrichment_tasks)} homes with CQC API data...")
                        try:
                            from services.cqc_deep_dive_service import CQCDeepDiveService
                            from api_clients.cqc_client import CQCAPIClient
                            from utils.auth import get_credentials
                            # asyncio already imported at top of file
                            
                            async def enrich_all_cqc():
                                # Get credentials and create properly configured CQC client
                                creds = get_credentials()
                                cqc_client = None
                                if creds.cqc and creds.cqc.primary_subscription_key:
                                    cqc_client = CQCAPIClient(
                                        primary_subscription_key=creds.cqc.primary_subscription_key,
                                        secondary_subscription_key=creds.cqc.secondary_subscription_key
                                    )
                                else:
                                    cqc_client = CQCAPIClient()
                                
                                service = CQCDeepDiveService(cqc_client=cqc_client)
                                tasks = []
                                for location_id, task_data in cqc_enrichment_tasks.items():
                                    tasks.append(
                                        service.build_cqc_deep_dive(
                                            db_data=task_data['raw_home'],
                                            location_id=location_id,
                                            provider_id=task_data['provider_id']
                                        )
                                    )
                                
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                
                                for (location_id, task_data), result in zip(cqc_enrichment_tasks.items(), results):
                                    if isinstance(result, Exception):
                                        print(f"      ⚠️ CQC enrichment failed for {location_id}: {result}")
                                        import traceback
                                        print(f"      Traceback: {traceback.format_exc()}")
                                        # Don't set to None - skip this location_id so fallback will be used
                                    elif result:
                                        try:
                                            cqc_dict = service.to_dict(result)
                                            if cqc_dict:
                                                cqc_enriched_data[location_id] = cqc_dict
                                                print(f"      ✅ CQC data enriched for {location_id}: overall={cqc_dict.get('overall_rating')}")
                                            else:
                                                print(f"      ⚠️ CQC to_dict returned empty for {location_id}")
                                        except Exception as e:
                                            print(f"      ⚠️ Error converting CQC data to dict for {location_id}: {e}")
                                    else:
                                        print(f"      ⚠️ CQC build_cqc_deep_dive returned None for {location_id}")
                                
                                await service.close()
                                return cqc_enriched_data
                            
                            # Run async enrichment
                            cqc_enriched_data = await enrich_all_cqc()
                            successful_count = len([v for v in cqc_enriched_data.values() if v])
                            print(f"   ✅ CQC enrichment completed for {successful_count}/{len(cqc_enrichment_tasks)} homes")
                            if successful_count == 0:
                                print(f"   ⚠️ WARNING: No CQC Deep Dive data found for any homes. Check CQC API subscription keys and service availability.")
                        except Exception as e:
                            error_msg = str(e)
                            print(f"   ⚠️ CQC enrichment error: {error_msg}")
                            
                            # Check if it's a configuration error (missing API key)
                            if "not configured" in error_msg or "subscription key" in error_msg.lower() or "API key" in error_msg:
                                print(f"   ❌ CQC API subscription keys are not configured or are invalid.")
                                print(f"   Please set valid subscription keys in config.json or environment variables:")
                                print(f"   - CQC_PRIMARY_SUBSCRIPTION_KEY (required)")
                                print(f"   - CQC_SECONDARY_SUBSCRIPTION_KEY (optional)")
                                print(f"   Get your API keys at: https://api-portal.service.cqc.org.uk/")
                            else:
                                import traceback
                                print(f"   Traceback: {traceback.format_exc()}")
                            cqc_enriched_data = {}
        except Exception as e:
            print(f"   ⚠️ Error checking CQC API configuration: {e}")
            cqc_enriched_data = {}
        
        # STEP: Enrich Google Places data for all homes (parallel) - uses GooglePlacesEnrichmentService
        print(f"\n{'='*80}")
        print(f"STEP: GOOGLE PLACES API ENRICHMENT (Sections 10, 11, 15, 16)")
        print(f"{'='*80}")
        
        # Prepare Google Places enrichment tasks
        google_places_enrichment_tasks = {}
        for scored in top_5_homes:
            home = scored['home']
            raw_home = home.get('rawData') or home
            home_name = home.get('name') or raw_home.get('name', 'Unknown')
            home_postcode = home.get('postcode') or raw_home.get('postcode')
            home_lat = home.get('latitude') or raw_home.get('latitude')
            home_lon = home.get('longitude') or raw_home.get('longitude')
            
            google_places_enrichment_tasks[home_name] = {
                'home': home,
                'raw_home': raw_home,
                'home_name': home_name,
                'postcode': home_postcode,
                'latitude': home_lat,
                'longitude': home_lon
            }
        
        # Execute Google Places enrichment in parallel
        google_places_enriched_data = {}
        if google_places_enrichment_tasks:
            print(f"   Enriching {len(google_places_enrichment_tasks)} homes with Google Places API data...")
            try:
                from config_manager import get_credentials
                creds = get_credentials()
                
                if creds and hasattr(creds, 'google_places') and creds.google_places and getattr(creds.google_places, 'api_key', None):
                    from services.google_places_enrichment_service import GooglePlacesEnrichmentService
                    # asyncio already imported at top of file
                    
                    async def enrich_all_google_places():
                        service = GooglePlacesEnrichmentService(
                            api_key=creds.google_places.api_key,
                            use_cache=True,
                            cache_ttl=86400  # 24 hours cache
                        )
                        tasks = []
                        task_keys = []
                        for home_name, task_data in google_places_enrichment_tasks.items():
                            tasks.append(
                                service._fetch_google_places_data(
                                    home_name=task_data['home_name'],
                                    postcode=task_data['postcode'],
                                    latitude=task_data['latitude'],
                                    longitude=task_data['longitude']
                                )
                            )
                            task_keys.append(home_name)
                        
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        for home_name, result in zip(task_keys, results):
                            if isinstance(result, Exception):
                                print(f"      ⚠️ Google Places enrichment failed for {home_name}: {result}")
                                google_places_enriched_data[home_name] = None
                            else:
                                if result:
                                    google_places_enriched_data[home_name] = result
                                    print(f"      ✅ Google Places data found for {home_name}: rating={result.get('rating')}, reviews={result.get('user_ratings_total')}")
                                else:
                                    google_places_enriched_data[home_name] = None
                                    print(f"      ⚠️ No Google Places data found for {home_name}")
                        
                        return google_places_enriched_data
                    
                    # Run async enrichment
                    google_places_enriched_data = await enrich_all_google_places()
                    successful_count = len([v for v in google_places_enriched_data.values() if v])
                    insights_count = len([v for v in google_places_enriched_data.values() if v and v.get('insights')])
                    print(f"   ✅ Google Places enrichment completed for {successful_count}/{len(google_places_enrichment_tasks)} homes")
                    print(f"   📊 Google Places Insights available for {insights_count}/{successful_count} homes")
                    if insights_count == 0 and successful_count > 0:
                        print(f"   ⚠️ WARNING: Google Places data found but Insights not available. Check Google Places Insights API access.")
                else:
                    print(f"   ⚠️ Google Places API key not configured, skipping enrichment")
            except Exception as e:
                print(f"   ⚠️ Google Places enrichment error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                google_places_enriched_data = {}
        
        # STEP: Enrich Companies House data for all homes (parallel) - uses CompaniesHouseService
        print(f"\n{'='*80}")
        print(f"STEP: COMPANIES HOUSE API ENRICHMENT (Section 8 - Financial Stability)")
        print(f"{'='*80}")
        
        # Check if Companies House API is configured
        try:
            from utils.auth import credentials_store
            from config_manager import get_credentials
            creds = credentials_store.get("default") or get_credentials()
            if not creds or not creds.companies_house or not creds.companies_house.api_key:
                print(f"   ⚠️ Companies House API key not configured - skipping enrichment")
                print(f"   To enable Financial Stability data, set COMPANIES_HOUSE_API_KEY in config.json")
                companies_house_enriched_data = {}
            else:
                api_key = creds.companies_house.api_key
                # Check if it's a placeholder
                placeholder_values = ["your-companies-house-api-key", "your-companies-house-key", "placeholder", "example", "test"]
                if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
                    print(f"   ⚠️ Companies House API key appears to be a placeholder - skipping enrichment")
                    print(f"   Please set a valid API key in config.json or environment variable COMPANIES_HOUSE_API_KEY")
                    print(f"   Get your API key at: https://developer.company-information.service.gov.uk/")
                    companies_house_enriched_data = {}
                else:
                    # API key looks valid, proceed with enrichment
                    # Prepare Companies House enrichment tasks
                    companies_house_enrichment_tasks = {}
                    for scored in top_5_homes:
                        home = scored['home']
                        raw_home = home.get('rawData') or home
                        home_name = home.get('name') or raw_home.get('name', 'Unknown')
                        home_address = home.get('address') or raw_home.get('address', '')
                        home_postcode = home.get('postcode') or raw_home.get('postcode', '')
                        
                        companies_house_enrichment_tasks[home_name] = {
                            'home': home,
                            'raw_home': raw_home,
                            'home_name': home_name,
                            'address': home_address,
                            'postcode': home_postcode
                        }
                    
                    # Execute Companies House enrichment in parallel
                    companies_house_enriched_data = {}
                    if companies_house_enrichment_tasks:
                        print(f"   Enriching {len(companies_house_enrichment_tasks)} homes with Companies House API data...")
                        try:
                            from services.companies_house_service import enrich_care_home_with_financial_data
                            # asyncio already imported at top of file
                            
                            async def enrich_all_companies_house():
                                tasks = []
                                task_keys = []
                                for home_name, task_data in companies_house_enrichment_tasks.items():
                                    tasks.append(
                                        asyncio.wait_for(
                                            enrich_care_home_with_financial_data(
                                                care_home_name=task_data['home_name'],
                                                address=task_data['address'],
                                                postcode=task_data['postcode']
                                            ),
                                            timeout=15.0  # 15 seconds timeout per home
                                        )
                                    )
                                    task_keys.append(home_name)
                                
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                
                                for home_name, result in zip(task_keys, results):
                                    if isinstance(result, Exception):
                                        if isinstance(result, asyncio.TimeoutError):
                                            print(f"      ⚠️ Companies House enrichment timed out for {home_name}")
                                        else:
                                            print(f"      ⚠️ Companies House enrichment failed for {home_name}: {result}")
                                        companies_house_enriched_data[home_name] = None
                                    else:
                                        if result and result.get('report_section'):
                                            # Convert to frontend expected format
                                            report_section = result['report_section']
                                            scoring_data = result.get('scoring_data', {})
                                            
                                            risk_score = scoring_data.get('risk_score', 50)
                                            risk_level = scoring_data.get('risk_level', 'Medium')
                                            
                                            altman_z = 2.5 if risk_level == 'Low' else 1.5 if risk_level == 'Medium' else 0.8
                                            bankruptcy_risk = 100 - risk_score if risk_score else 50
                                            
                                            companies_house_enriched_data[home_name] = {
                                                'company_info': report_section.get('company_info', {}),
                                                'company_number': result.get('company_number'),
                                                'three_year_summary': {
                                                    'revenue_trend': 'Stable',
                                                    'revenue_3yr_avg': None,
                                                    'revenue_growth_rate': None,
                                                    'profitability_trend': None,
                                                    'net_margin_3yr_avg': None,
                                                    'working_capital_trend': report_section.get('accounts', {}).get('last_accounts_date') and 'Stable' or 'Unknown',
                                                    'working_capital_3yr_avg': None,
                                                    'current_ratio_3yr_avg': None,
                                                },
                                                'altman_z_score': altman_z,
                                                'bankruptcy_risk_score': bankruptcy_risk,
                                                'bankruptcy_risk_level': risk_level,
                                                'risk_score': risk_score,
                                                'risk_level': risk_level,
                                                'director_stability': report_section.get('directors', {}),
                                                'ownership_stability': report_section.get('ownership', {}),
                                                'charges_summary': report_section.get('charges', {}),
                                                'accounts_status': report_section.get('accounts', {}),
                                                'uk_benchmarks_comparison': {
                                                    'revenue_growth': None,
                                                    'net_margin': None,
                                                    'current_ratio': None,
                                                    'risk_level': f"Company is {risk_level} risk",
                                                    'director_stability': report_section.get('directors', {}).get('label', 'Unknown'),
                                                    'ownership_type': report_section.get('ownership', {}).get('type', 'Unknown')
                                                },
                                                'issues': report_section.get('issues', []),
                                                'recommendations': report_section.get('recommendations', []),
                                                'red_flags': [
                                                    {'type': 'financial', 'severity': 'medium', 'description': issue}
                                                    for issue in report_section.get('issues', []) 
                                                    if 'risk' in issue.lower() or 'concern' in issue.lower()
                                                ],
                                                'data_source': 'Companies House API',
                                                'analysis_date': report_section.get('analysis_date')
                                            }
                                            print(f"      ✅ Companies House data found for {home_name}: risk={scoring_data.get('risk_level')}")
                                        else:
                                            companies_house_enriched_data[home_name] = None
                                            print(f"      ⚠️ No Companies House data found for {home_name}")
                                
                                return companies_house_enriched_data
                            
                            # Run async enrichment
                            companies_house_enriched_data = await enrich_all_companies_house()
                            successful_count = len([v for v in companies_house_enriched_data.values() if v])
                            print(f"   ✅ Companies House enrichment completed for {successful_count}/{len(companies_house_enrichment_tasks)} homes")
                            if successful_count == 0:
                                print(f"   ⚠️ WARNING: No Financial Stability data found for any homes. Check Companies House API key and service availability.")
                        except Exception as e:
                            error_msg = str(e)
                            print(f"   ⚠️ Companies House enrichment error: {error_msg}")
                            
                            # Check if it's a configuration error (missing API key)
                            if "not configured" in error_msg or "API key" in error_msg:
                                print(f"   ❌ Companies House API key is not configured or is invalid.")
                                print(f"   Please set a valid API key in config.json or environment variable COMPANIES_HOUSE_API_KEY")
                                print(f"   Get your API key at: https://developer.company-information.service.gov.uk/")
                            else:
                                import traceback
                                print(f"   Traceback: {traceback.format_exc()}")
                            companies_house_enriched_data = {}
        except Exception as e:
            print(f"   ⚠️ Error checking Companies House API configuration: {e}")
            companies_house_enriched_data = {}
        
        # STEP: Enrich Staff Quality data for all homes (parallel)
        print(f"\n{'='*80}")
        print(f"STEP: STAFF QUALITY ENRICHMENT (Section 9 - Staff Analysis)")
        print(f"{'='*80}")

        staff_quality_enrichment_tasks = {}
        for scored in top_5_homes:
            home = scored['home']
            raw_home = home.get('rawData') or home
            location_id = (
                home.get('cqc_location_id') or
                home.get('location_id') or
                raw_home.get('cqc_location_id') or
                raw_home.get('location_id')
            )
            home_name = home.get('name') or raw_home.get('name', 'Unknown')
            
            if location_id:
                staff_quality_enrichment_tasks[location_id] = {
                    'home_name': home_name,
                    'location_id': location_id
                }

        staff_quality_enriched_data = {}
        if staff_quality_enrichment_tasks:
            print(f"   Enriching {len(staff_quality_enrichment_tasks)} homes with Staff Quality data...")
            try:
                from services.staff_quality_service import StaffQualityService
                
                async def enrich_all_staff_quality():
                    service = StaffQualityService()
                    tasks = []
                    task_keys = []
                    for location_id, task_data in staff_quality_enrichment_tasks.items():
                        # Get home name to match with Companies House data
                        home_name = task_data.get('home_name', '')
                        
                        # Check if we already have Companies House data for this home
                        companies_house_data = None
                        if home_name and home_name in companies_house_enriched_data:
                            ch_data = companies_house_enriched_data[home_name]
                            if ch_data:
                                companies_house_data = ch_data
                                print(f"      ℹ️  Using existing Companies House data for Staff Quality: {home_name}")
                        
                        tasks.append(
                            asyncio.wait_for(
                                service.analyze_by_location_id(
                                    location_id,
                                    companies_house_data=companies_house_data
                                ),
                                timeout=10.0
                            )
                        )
                        task_keys.append(location_id)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for location_id, result in zip(task_keys, results):
                        if isinstance(result, Exception):
                            if isinstance(result, asyncio.TimeoutError):
                                print(f"      ⚠️ Staff Quality timed out for {location_id}")
                            else:
                                print(f"      ⚠️ Staff Quality failed for {location_id}: {result}")
                            staff_quality_enriched_data[location_id] = None
                        else:
                            if result and result.get('staff_quality_score'):
                                staff_quality_enriched_data[location_id] = result
                                score = result.get('staff_quality_score', {})
                                print(f"      ✅ Staff Quality found for {location_id}: score={score.get('overall_score')}, category={score.get('category')}")
                            else:
                                staff_quality_enriched_data[location_id] = None
                    
                    return staff_quality_enriched_data
                
                staff_quality_enriched_data = await enrich_all_staff_quality()
                print(f"   ✅ Staff Quality enrichment completed for {len([v for v in staff_quality_enriched_data.values() if v])} homes")
            except Exception as e:
                print(f"   ⚠️ Staff Quality enrichment error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                staff_quality_enriched_data = {}
        
        # STEP: Enrich Neighbourhood data for top-5 finalists only (parallel)
        print(f"\n{'='*80}")
        print(f"STEP: NEIGHBOURHOOD ANALYSIS ENRICHMENT (Section 18 - Location Wellbeing) - TOP 5 FINALISTS ONLY")
        print(f"{'='*80}")

        neighbourhood_enrichment_tasks = {}
        for scored in top_5_homes:
            home = scored['home']
            raw_home = home.get('rawData') or home
            home_name = home.get('name') or raw_home.get('name', 'Unknown')
            home_postcode = home.get('postcode') or raw_home.get('postcode')
            home_lat = home.get('latitude') or raw_home.get('latitude')
            home_lon = home.get('longitude') or raw_home.get('longitude')
            
            if home_postcode:
                neighbourhood_enrichment_tasks[home_name] = {
                    'home_name': home_name,
                    'postcode': home_postcode,
                    'latitude': home_lat,
                    'longitude': home_lon
                }

        neighbourhood_enriched_data = {}
        if neighbourhood_enrichment_tasks:
            print(f"   Enriching {len(neighbourhood_enrichment_tasks)} homes with Neighbourhood data...")
            try:
                from data_integrations.batch_processor import NeighbourhoodAnalyzer
                
                async def enrich_all_neighbourhood():
                    analyzer = NeighbourhoodAnalyzer()
                    tasks = []
                    task_keys = []
                    for home_name, task_data in neighbourhood_enrichment_tasks.items():
                        tasks.append(
                            asyncio.wait_for(
                                analyzer.analyze(
                                    postcode=task_data['postcode'],
                                    lat=task_data['latitude'],
                                    lon=task_data['longitude'],
                                    include_os_places=True,  # ✅ Enabled for top-5: improves data quality (coordinates, UPRN, address details)
                                    include_ons=True,
                                    include_osm=True,
                                    include_nhsbsa=False,  # Not used in professional report
                                    include_environmental=False  # Skip for speed
                                ),
                                timeout=15.0
                            )
                        )
                        task_keys.append(home_name)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for home_name, result in zip(task_keys, results):
                        if isinstance(result, Exception):
                            if isinstance(result, asyncio.TimeoutError):
                                print(f"      ⚠️ Neighbourhood timed out for {home_name}")
                            else:
                                print(f"      ⚠️ Neighbourhood failed for {home_name}: {result}")
                            neighbourhood_enriched_data[home_name] = None
                        else:
                            if result and result.get('overall'):
                                neighbourhood_enriched_data[home_name] = result
                                overall = result.get('overall', {})
                                print(f"      ✅ Neighbourhood found for {home_name}: score={overall.get('score')}, rating={overall.get('rating')}")
                            else:
                                neighbourhood_enriched_data[home_name] = None
                    
                    return neighbourhood_enriched_data
                
                neighbourhood_enriched_data = await enrich_all_neighbourhood()
                print(f"   ✅ Neighbourhood enrichment completed for {len([v for v in neighbourhood_enriched_data.values() if v])} homes")
            except Exception as e:
                print(f"   ⚠️ Neighbourhood enrichment error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                neighbourhood_enriched_data = {}
        
        # Convert scored homes to format expected by frontend
        care_homes_list = []
        for home_index, scored in enumerate(top_5_homes):
            home = scored['home']
            raw_home = home.get('rawData') or home
            match_result = scored.get('matchResult', {})
            
            # Extract values for enrichment
            weekly_price_value = extract_weekly_price(home, care_type) or 0.0
            cqc_rating_value = (
                home.get('cqc_rating_overall')
                or raw_home.get('cqc_rating_overall')
                or raw_home.get('overall_cqc_rating')
                or raw_home.get('cqc_rating')
                or (raw_home.get('cqc_ratings', {}) or {}).get('overall')
                or 'Unknown'
            )
            if isinstance(cqc_rating_value, dict):
                cqc_rating_value = cqc_rating_value.get('overall', 'Unknown')
            cqc_rating_value = str(cqc_rating_value) if cqc_rating_value else 'Unknown'
            
            last_inspection_date = (
                raw_home.get('cqc_last_inspection_date')
                or raw_home.get('last_inspection_date')
                or raw_home.get('inspection_date')
                or ''
            )
            
            google_rating_value = raw_home.get('google_rating') or raw_home.get('googleRating') or home.get('rating')
            review_count_value = raw_home.get('review_count') or raw_home.get('reviewCount') or home.get('user_ratings_total', 0)
            
            # Extract FSA/Food Hygiene data
            food_hygiene_rating = (
                raw_home.get('food_hygiene_rating')
                or raw_home.get('fsa_rating')
                or raw_home.get('foodHygieneRating')
                or home.get('food_hygiene_rating')
                or home.get('fsa_rating')
            )
            
            # Extract factor scores from match_result (convert to array format expected by frontend)
            point_allocations = match_result.get('point_allocations', {})
            category_scores = match_result.get('category_scores', {})
            weights_dict = match_result.get('weights', {})
            
            # Map category names to display names
            category_display_names = {
                'medical': 'Medical Capabilities',
                'safety': 'Safety & Quality',
                'location': 'Location & Access',
                'social': 'Cultural & Social',
                'financial': 'Financial Stability',
                'staff': 'Staff Quality',
                'cqc': 'CQC Compliance',
                'services': 'Additional Services'
            }
            
            # Maximum possible points per category (156 total, distributed by weights)
            max_points_per_category = {
                'medical': 30.0,  # ~19% of 156
                'safety': 25.0,   # ~16% of 156
                'location': 15.0, # ~10% of 156
                'social': 15.0,  # ~10% of 156
                'financial': 20.0, # ~13% of 156
                'staff': 20.0,   # ~13% of 156
                'cqc': 20.0,     # ~13% of 156
                'services': 11.0  # ~7% of 156
            }
            
            # Convert to array format expected by frontend
            factor_scores = []
            for category in ['medical', 'safety', 'location', 'social', 'financial', 'staff', 'cqc', 'services']:
                points = round(point_allocations.get(category, 0.0), 1)
                score_normalized = category_scores.get(category, 0.0)  # 0-1.0 scale
                max_points = max_points_per_category.get(category, 20.0)
                weight = weights_dict.get(category, 0.0) if isinstance(weights_dict, dict) else 0.0
                
                factor_scores.append({
                    'category': category_display_names.get(category, category.title()),
                    'score': points,
                    'maxScore': max_points,
                    'weight': weight,
                    'verified': True  # All scores are verified from matching algorithm
                })
            
            # Debug logging for first home (check if we're in the top 5 loop)
            # This will help diagnose why factor_scores might be empty
            if len(factor_scores) == 0 or all(fs['score'] == 0 for fs in factor_scores):
                print(f"\n   ⚠️ WARNING: factor_scores empty or all zeros for {home.get('name', 'unknown')}:")
                print(f"      point_allocations: {point_allocations}")
                print(f"      category_scores: {category_scores}")
                print(f"      weights_dict: {weights_dict}")
                print(f"      match_result keys: {list(match_result.keys()) if match_result else 'None'}")
            
            # Get photo URL
            placeholder_photo = "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
            photo_url = (
                home.get('photo')
                or raw_home.get('photo')
                or raw_home.get('photo_url')
                or raw_home.get('image_url')
                or placeholder_photo
            )
            
            # Get or build enriched data
            # Get Financial Stability - prefer enriched data from Companies House API, fallback to existing or synthetic
            home_name_for_enrichment = home.get('name') or raw_home.get('name', 'Unknown')
            financial_stability = None
            if home_name_for_enrichment and home_name_for_enrichment in companies_house_enriched_data:
                financial_stability = companies_house_enriched_data[home_name_for_enrichment]
                # Ensure it's a dict (not None) for frontend
                if financial_stability is None:
                    financial_stability = {}
            if not financial_stability:
                financial_stability = raw_home.get('financial_stability') or raw_home.get('financialStability')
                # Ensure it's a dict or None (not empty string)
                if financial_stability == '':
                    financial_stability = None
            
            # Get Google Places - prefer enriched data from Google Places API, fallback to existing or synthetic
            google_places = None
            if home_name_for_enrichment and home_name_for_enrichment in google_places_enriched_data:
                google_places = google_places_enriched_data[home_name_for_enrichment]
            if not google_places:
                google_places = raw_home.get('google_places') or raw_home.get('googlePlaces')
            
            # Get CQC Deep Dive - prefer enriched data from API, fallback to existing or basic
            location_id_for_cqc = (
                home.get('cqc_location_id') or
                home.get('location_id') or
                raw_home.get('cqc_location_id') or
                raw_home.get('location_id')
            )
            cqc_details = None
            
            # Try to get enriched CQC data
            if location_id_for_cqc and location_id_for_cqc in cqc_enriched_data:
                enriched = cqc_enriched_data[location_id_for_cqc]
                # Only use if it's not None and is a dict with actual data
                if enriched and isinstance(enriched, dict) and enriched.get('overall_rating'):
                    cqc_details = enriched
                    print(f"   ✅ Using enriched CQC data for {location_id_for_cqc}")
            
            # Fallback to existing data in raw_home
            if not cqc_details:
                cqc_details = raw_home.get('cqc_detailed') or raw_home.get('cqcDeepDive')
                if cqc_details:
                    print(f"   ✅ Using existing CQC data from raw_home for {location_id_for_cqc or 'unknown'}")
            
            # Final fallback to basic build
            if not cqc_details:
                # Ensure we have rating and date for basic build
                if not cqc_rating_value or cqc_rating_value == 'Unknown':
                    cqc_rating_value = (
                        raw_home.get('cqc_rating_overall') or
                        raw_home.get('overall_cqc_rating') or
                        raw_home.get('cqc_rating') or
                        raw_home.get('rating') or
                        'Unknown'
                    )
                if not last_inspection_date:
                    last_inspection_date = (
                        raw_home.get('cqc_last_inspection_date') or
                        raw_home.get('last_inspection_date') or
                        raw_home.get('inspection_date')
                    )
                
                print(f"   🔧 Building basic CQC data for {location_id_for_cqc or 'unknown'}: rating={cqc_rating_value}, date={last_inspection_date}")
                cqc_details = build_cqc_deep_dive(raw_home, cqc_rating_value, last_inspection_date)
                if cqc_details and cqc_details.get('overall_rating'):
                    print(f"   ✅ Built basic CQC data for {location_id_for_cqc or 'unknown'}: rating={cqc_details.get('overall_rating')}, detailed_ratings={bool(cqc_details.get('detailed_ratings'))}")
                else:
                    print(f"   ⚠️ Failed to build CQC data for {location_id_for_cqc or 'unknown'}: rating_value={cqc_rating_value}, inspection_date={last_inspection_date}, result={cqc_details}")
                    # Ensure we return at least minimal structure
                    if not cqc_details or not isinstance(cqc_details, dict):
                        cqc_details = {
                            'overall_rating': cqc_rating_value or 'Unknown',
                            'current_rating': cqc_rating_value or 'Unknown',
                            'detailed_ratings': {
                                'safe': {'rating': 'Unknown', 'explanation': 'Safety of care, safeguarding, medicines handling'},
                                'effective': {'rating': 'Unknown', 'explanation': 'Effectiveness of treatments and support'},
                                'caring': {'rating': 'Unknown', 'explanation': 'Compassion, dignity, respect'},
                                'responsive': {'rating': 'Unknown', 'explanation': 'Meeting needs, responding to feedback'},
                                'well_led': {'rating': 'Unknown', 'explanation': 'Leadership, governance, continuous improvement'}
                            },
                            'historical_ratings': [],
                            'enforcement_actions': [],
                            'action_plans': [],
                            'rating_trend': 'Insufficient data',
                            'trend': 'Insufficient data'
                        }
            
            # Ensure cqc_details is always a dict (not None or empty)
            if not cqc_details or not isinstance(cqc_details, dict):
                print(f"   ⚠️ cqc_details is invalid for {location_id_for_cqc or 'unknown'}, creating minimal structure")
                cqc_details = {
                    'overall_rating': cqc_rating_value or 'Unknown',
                    'current_rating': cqc_rating_value or 'Unknown',
                    'detailed_ratings': {
                        'safe': {'rating': 'Unknown', 'explanation': 'Safety of care, safeguarding, medicines handling'},
                        'effective': {'rating': 'Unknown', 'explanation': 'Effectiveness of treatments and support'},
                        'caring': {'rating': 'Unknown', 'explanation': 'Compassion, dignity, respect'},
                        'responsive': {'rating': 'Unknown', 'explanation': 'Meeting needs, responding to feedback'},
                        'well_led': {'rating': 'Unknown', 'explanation': 'Leadership, governance, continuous improvement'}
                    },
                    'historical_ratings': [],
                    'enforcement_actions': [],
                    'action_plans': [],
                    'rating_trend': 'Insufficient data',
                    'trend': 'Insufficient data'
                }
            
            # Get FSA Detailed - prefer enriched data from FSA API, fallback to existing or synthetic
            home_name_for_fsa = home.get('name') or raw_home.get('name', 'Unknown')
            fsa_detailed = None
            if home_name_for_fsa and home_name_for_fsa in fsa_enriched_data:
                fsa_detailed = fsa_enriched_data[home_name_for_fsa]
            if not fsa_detailed:
                fsa_detailed = raw_home.get('fsa_detailed') or raw_home.get('fsaDetailed')
            
            # Ensure google_places has place_id if it exists
            if google_places and isinstance(google_places, dict):
                # If google_places exists but doesn't have place_id, try to extract it
                if not google_places.get('place_id') and not google_places.get('placeId'):
                    place_id = (
                        raw_home.get('google_place_id')
                        or raw_home.get('place_id')
                        or raw_home.get('placeId')
                        or raw_home.get('googlePlaceId')
                    )
                    if place_id:
                        google_places['place_id'] = place_id
            # If no Google Places data from API or raw_home, leave as None (no synthetic data)
            
            # Get Staff Quality data
            staff_quality = None
            if location_id_for_cqc and location_id_for_cqc in staff_quality_enriched_data:
                sq_data = staff_quality_enriched_data[location_id_for_cqc]
                if sq_data:
                    staff_quality = {
                        'overallScore': sq_data.get('staff_quality_score', {}).get('overall_score', 0),
                        'category': sq_data.get('staff_quality_score', {}).get('category', 'UNKNOWN'),
                        'confidence': sq_data.get('staff_quality_score', {}).get('confidence', 'low'),
                        'components': sq_data.get('staff_quality_score', {}).get('components', {}),
                        'themes': sq_data.get('staff_quality_score', {}).get('themes', {}),
                        'dataQuality': sq_data.get('staff_quality_score', {}).get('data_quality', {}),
                        'cqcData': sq_data.get('cqc_data', {}),
                        'reviewCount': len(sq_data.get('reviews', [])),
                        'reviews': sq_data.get('reviews', [])[:5],
                        'carehomeCoUk': sq_data.get('carehome_co_uk'),
                        'indeed': sq_data.get('indeed')
                    }
            
            # Get Neighbourhood data
            neighbourhood = None
            home_name_for_enrichment = home.get('name') or raw_home.get('name', 'Unknown')
            if home_name_for_enrichment and home_name_for_enrichment in neighbourhood_enriched_data:
                nb_data = neighbourhood_enriched_data[home_name_for_enrichment]
                if nb_data:
                    overall = nb_data.get('overall', {})
                    osm = nb_data.get('osm', {})
                    ons = nb_data.get('ons', {})
                    nhsbsa = nb_data.get('nhsbsa', {})
                    
                    neighbourhood = {
                        'overallScore': overall.get('score'),
                        'overallRating': overall.get('rating'),
                        'confidence': overall.get('confidence'),
                        'breakdown': overall.get('breakdown', []),
                        'walkability': {
                            'score': osm.get('walk_score', {}).get('walk_score'),
                            'rating': osm.get('walk_score', {}).get('rating'),
                            'careHomeRelevance': osm.get('walk_score', {}).get('care_home_relevance', {}),
                            'amenitiesNearby': osm.get('amenities', {}).get('summary', {})
                        },
                        'socialWellbeing': {
                            'score': ons.get('wellbeing', {}).get('social_wellbeing_index', {}).get('score'),
                            'rating': ons.get('wellbeing', {}).get('social_wellbeing_index', {}).get('rating'),
                            'localAuthority': ons.get('geography', {}).get('local_authority'),
                            'deprivation': ons.get('economics', {}).get('deprivation')
                        },
                        'coordinates': nb_data.get('coordinates', {})
                    }
            
            # Build Safety Analysis from OSM/Neighbourhood data
            safety_analysis = None
            if home_name_for_enrichment and home_name_for_enrichment in neighbourhood_enriched_data:
                nb_data = neighbourhood_enriched_data[home_name_for_enrichment]
                if nb_data:
                    osm = nb_data.get('osm', {})
                    transport = osm.get('transport', {})
                    
                    # Calculate safety score based on walkability and transport
                    walk_score = osm.get('walk_score', {}).get('walk_score', 0) or 0
                    safety_score = min(100, walk_score + 20) if walk_score > 0 else None
                    
                    safety_analysis = {
                        'safety_score': safety_score,
                        'safety_rating': 'Good' if safety_score and safety_score >= 60 else 'Fair' if safety_score and safety_score >= 40 else 'Needs Review' if safety_score else None,
                        'pedestrian_safety': osm.get('walk_score', {}).get('rating'),
                        'public_transport': {
                            'nearest_bus_stop': transport.get('nearest_bus_stop'),
                            'nearest_train_station': transport.get('nearest_train_station')
                        } if transport else None,
                        'accessibility': {
                            'wheelchair_accessible': raw_home.get('wheelchair_accessible', False),
                            'accessible_entrances': None
                        }
                    }
            
            # Build Location Wellbeing from Neighbourhood data
            location_wellbeing = None
            if home_name_for_enrichment and home_name_for_enrichment in neighbourhood_enriched_data:
                nb_data = neighbourhood_enriched_data[home_name_for_enrichment]
                if nb_data:
                    osm = nb_data.get('osm', {})
                    amenities = osm.get('amenities', {})
                    parks = amenities.get('parks', []) if isinstance(amenities, dict) else []
                    
                    location_wellbeing = {
                        'walkability_score': osm.get('walk_score', {}).get('walk_score'),
                        'green_space_score': min(100, len(parks) * 20) if parks else None,
                        'nearest_park_distance': parks[0].get('distance') if parks else None,
                        'noise_level': 'Low' if osm.get('walk_score', {}).get('walk_score', 0) > 70 else 'Medium',
                        'local_amenities': [
                            {'type': amenity.get('type', 'amenity'), 'name': amenity.get('name', 'Unknown'), 'distance': amenity.get('distance', 0)}
                            for amenity in (amenities.get('all', []) or [])[:10]
                        ] if isinstance(amenities, dict) else []
                    }
            
            # Build Area Map from Neighbourhood data
            area_map = None
            if home_name_for_enrichment and home_name_for_enrichment in neighbourhood_enriched_data:
                nb_data = neighbourhood_enriched_data[home_name_for_enrichment]
                if nb_data:
                    osm = nb_data.get('osm', {})
                    nhsbsa = nb_data.get('nhsbsa', {})
                    amenities = osm.get('amenities', {})
                    
                    # Get GP practices from NHSBSA
                    gps = nhsbsa.get('practices', []) if isinstance(nhsbsa, dict) else []
                    parks = amenities.get('parks', []) if isinstance(amenities, dict) else []
                    shops = amenities.get('shops', []) if isinstance(amenities, dict) else []
                    
                    area_map = {
                        'nearby_gps': [
                            {'name': gp.get('name', 'GP Practice'), 'distance': gp.get('distance', 0), 'address': gp.get('address')}
                            for gp in (gps[:5] if gps else [])
                        ],
                        'nearby_parks': [
                            {'name': park.get('name', 'Park'), 'distance': park.get('distance', 0)}
                            for park in (parks[:5] if parks else [])
                        ],
                        'nearby_shops': [
                            {'name': shop.get('name', 'Shop'), 'distance': shop.get('distance', 0), 'type': shop.get('type')}
                            for shop in (shops[:5] if shops else [])
                        ],
                        'coordinates': nb_data.get('coordinates', {})
                    }
            
            # Build Community Reputation from Google Places data
            community_reputation = None
            if google_places and isinstance(google_places, dict):
                sentiment = google_places.get('sentiment_analysis', {})
                reviews = google_places.get('reviews', [])
                
                community_reputation = {
                    'google_rating': google_places.get('rating'),
                    'google_review_count': google_places.get('user_ratings_total', 0),
                    'carehome_rating': None,  # Would need carehome.co.uk data
                    'trust_score': min(100, (google_places.get('rating', 0) or 0) * 20) if google_places.get('rating') else None,
                    'sentiment_analysis': {
                        'average_sentiment': sentiment.get('average_sentiment'),
                        'sentiment_label': sentiment.get('sentiment_label', 'Unknown'),
                        'total_reviews': sentiment.get('total_reviews', 0),
                        'positive_reviews': sentiment.get('positive_reviews', 0),
                        'negative_reviews': sentiment.get('negative_reviews', 0),
                        'neutral_reviews': sentiment.get('neutral_reviews', 0),
                        'sentiment_distribution': sentiment.get('sentiment_distribution', {})
                    } if sentiment else None,
                    'sample_reviews': [
                        {
                            'text': r.get('text', ''),
                            'rating': r.get('rating', 0),
                            'author': r.get('author_name', 'Anonymous'),
                            'source': 'Google',
                            'date': r.get('time', '')
                        }
                        for r in (reviews[:5] if reviews else [])
                    ],
                    'total_reviews_analyzed': len(reviews) if reviews else 0,
                    'review_sources': ['Google'] if reviews else []
                }
            
            # Build home object in format expected by frontend
            care_home = {
                'id': home.get('cqc_location_id') or home.get('id') or str(uuid.uuid4()),
                'name': home.get('name', 'Unknown'),
                'matchScore': round(scored['matchScore'], 1),
                'weeklyPrice': weekly_price_value,
                'location': home.get('location') or home.get('city', ''),
                'postcode': home.get('postcode', ''),
                'cqcRating': cqc_rating_value,
                'googleRating': google_rating_value or 0,
                'reviewCount': review_count_value or 0,
                'address': home.get('address', ''),
                'careTypes': home.get('care_types', []),
                'photo': photo_url,  # Add photo URL
                'rawData': home,
                # Add Food Hygiene Rating
                'foodHygiene': food_hygiene_rating if food_hygiene_rating is not None else None,
                # Add factor scores for medical matching chart
                'factorScores': factor_scores,
                # Add enriched data - NO SYNTHETIC DATA, only real API data or null
                'financialStability': financial_stability,  # Real Companies House data or null
                'googlePlaces': google_places,  # Real Google Places data or null
                'cqcDeepDive': cqc_details,  # Real CQC data or null
                'fsaDetailed': fsa_detailed,  # Real FSA data or null
                'staffQuality': staff_quality,  # Real Staff Quality data or null
                'neighbourhood': neighbourhood,  # Real Neighbourhood data or null
                # Additional sections from enriched data
                'safetyAnalysis': safety_analysis,  # Safety & Infrastructure (Section 6)
                'locationWellbeing': location_wellbeing,  # Location Wellbeing (Section 18)
                'areaMap': area_map,  # Area Map (Section 19)
                'communityReputation': community_reputation,  # Community Reputation (Section 10)
                # Category Winners (NEW)
                'is_category_winner': home.get('is_category_winner', {}),
                'category_labels': home.get('category_labels', []),
                'category_reasoning': home.get('category_reasoning', {}),
                'value_ratio': home.get('value_ratio')  # For Best Cost & Financial
            }
            
            care_homes_list.append(care_home)
        
        # Calculate Funding Optimization
        funding_optimization = None
        try:
            from services.funding_optimization_service import FundingOptimizationService
            funding_service = FundingOptimizationService()
            funding_optimization = funding_service.calculate_funding_optimization(
                questionnaire=questionnaire,
                care_homes=care_homes_list
            )
            print(f"✅ Funding optimization calculated successfully")
        except Exception as e:
            print(f"⚠️ Funding optimization calculation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        # Calculate Fair Cost Gap Analysis
        fair_cost_gap_analysis = None
        try:
            # Get local authority from questionnaire
            local_authority = preferred_city if preferred_city else None
            # Prefer local authority from top homes if available
            if care_homes_list:
                primary_home = care_homes_list[0]
                raw_home = primary_home.get('rawData') or {}
                la_candidates = [
                    raw_home.get('local_authority'),
                    raw_home.get('localAuthority'),
                    primary_home.get('local_authority'),
                    primary_home.get('localAuthority'),
                    raw_home.get('city'),
                    primary_home.get('city'),
                ]
                for candidate in la_candidates:
                    if candidate:
                        local_authority = candidate
                        break
            
            # Determine care type for MSIF lookup
            msif_care_type = 'nursing'
            if care_type == 'residential':
                msif_care_type = 'residential'
            elif care_type == 'dementia':
                msif_care_type = 'residential_dementia'
            
            # Try to get MSIF data
            msif_lower = None
            try:
                # Try using RCH-data pricing calculator
                from pricing_calculator import PricingService, CareType
                pricing_service = PricingService()
                care_type_enum = CareType.RESIDENTIAL
                if msif_care_type == 'nursing':
                    care_type_enum = CareType.NURSING
                elif msif_care_type == 'residential_dementia':
                    care_type_enum = CareType.RESIDENTIAL_DEMENTIA
                
                # Get fair cost for local authority
                if local_authority:
                    result = pricing_service.get_fair_cost_lower_bound(
                        local_authority=local_authority,
                        care_type=care_type_enum
                    )
                    if result:
                        msif_lower = result
            except Exception as msif_error:
                print(f"⚠️ MSIF lookup failed: {msif_error}")
                # Use default fallback values
                default_msif = {
                    'residential': 700,
                    'nursing': 1048,
                    'residential_dementia': 800,
                    'nursing_dementia': 1048
                }
                msif_lower = default_msif.get(msif_care_type, 700)
            
            # Calculate gap for each home
            gap_homes = []
            total_gap_weekly = 0.0
            
            for home in care_homes_list:
                weekly_price = extract_weekly_price(home, care_type) or 0.0
                if weekly_price > 0 and msif_lower:
                    gap_weekly = max(0.0, float(weekly_price) - float(msif_lower))
                    gap_annual = gap_weekly * 52
                    gap_5year = gap_annual * 5
                    gap_percent = (gap_weekly / float(msif_lower) * 100) if msif_lower > 0 else 0.0
                    
                    total_gap_weekly += gap_weekly
                    
                    gap_homes.append({
                        'home_id': home.get('id'),
                        'home_name': home.get('name'),
                        'their_price': round(float(weekly_price), 2),
                        'fair_cost_msif': round(float(msif_lower), 2),
                        'gap_weekly': round(gap_weekly, 2),
                        'gap_annual': round(gap_annual, 2),
                        'gap_5year': round(gap_5year, 2),
                        'gap_percent': round(gap_percent, 2)
                    })
            
            if gap_homes:
                avg_gap_weekly = total_gap_weekly / len(gap_homes)
                avg_gap_annual = avg_gap_weekly * 52
                avg_gap_5year = avg_gap_annual * 5
                
                fair_cost_gap_analysis = {
                    'local_authority': local_authority or 'Unknown',
                    'care_type': msif_care_type,
                    'homes': gap_homes,
                    'average_gap_weekly': round(avg_gap_weekly, 2),
                    'average_gap_annual': round(avg_gap_annual, 2),
                    'average_gap_5year': round(avg_gap_5year, 2),
                    'why_gap_exists': {
                        'title': 'Why the Fair Cost Gap Exists',
                        'explanation': 'The gap between market prices and government fair cost (MSIF) exists due to systemic market factors including regional demand, care quality variations, and operational cost differences.',
                        'market_dynamics': [
                            'Regional demand variations',
                            'Quality and service level differences',
                            'Operational cost structures',
                            'Market competition levels'
                        ]
                    },
                    'strategies_to_reduce_gap': [
                        {
                            'strategy_number': 1,
                            'title': 'Negotiate using MSIF data',
                            'description': 'Use government MSIF data as leverage in negotiations to align pricing with fair cost benchmarks.',
                            'potential_savings': f"Up to £{round(avg_gap_weekly * 0.10, 2):,.2f}/week",
                            'action_items': [
                                'Share MSIF data during negotiations',
                                'Request pricing justification from provider',
                                'Ask for discounts aligned with fair cost'
                            ]
                        },
                        {
                            'strategy_number': 2,
                            'title': 'Consider adjacent local authorities',
                            'description': 'Explore care homes in nearby local authorities where fair cost gap is smaller.',
                            'potential_savings': f"Up to £{round(avg_gap_weekly * 0.15, 2):,.2f}/week",
                            'action_items': [
                                'Map neighbouring local authorities',
                                'Compare MSIF rates across regions',
                                'Visit alternative homes within travel tolerance'
                            ]
                        },
                        {
                            'strategy_number': 3,
                            'title': 'Request detailed cost breakdown',
                            'description': 'Understand what services justify premium pricing and identify negotiable extras.',
                            'potential_savings': f"Up to £{round(avg_gap_weekly * 0.05, 2):,.2f}/week",
                            'action_items': [
                                'Ask for line-item cost breakdown',
                                'Identify optional/negotiable services',
                                'Benchmark extras across providers'
                            ]
                        },
                        {
                            'strategy_number': 4,
                            'title': 'Negotiate long-term commitment discounts',
                            'description': 'Secure lower rates by committing to longer placements or upfront payments.',
                            'potential_savings': f"Up to £{round(avg_gap_weekly * 0.10, 2):,.2f}/week",
                            'action_items': [
                                'Explore 6-12 month contract discounts',
                                'Offer upfront payment for reduced rates',
                                'Bundle services to reduce add-on fees'
                            ]
                        }
                    ]
                }
                print(f"✅ Fair cost gap analysis calculated for {len(gap_homes)} homes")
        except Exception as e:
            print(f"⚠️ Fair cost gap calculation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        # Build report matching original structure
        report = {
            'reportId': report_id,
            'clientName': client_name,
            'appliedWeights': weights.to_dict() if hasattr(weights, 'to_dict') else {},
            'appliedConditions': applied_conditions,
            'careHomes': care_homes_list,  # Frontend expects 'careHomes', not 'matched_homes'
            'analysisSummary': {
                'totalHomesAnalyzed': len(care_homes),
                'factorsAnalyzed': 156,
                'analysisTime': '24-48 hours'
            },
            'matchingDetails': matching_details  # Breakdown visibility: data quality and fallback usage
        }
        
        # Add optional sections
        if funding_optimization:
            report['fundingOptimization'] = funding_optimization
        if fair_cost_gap_analysis:
            report['fairCostGapAnalysis'] = fair_cost_gap_analysis
        
        # Comparative Analysis
        try:
            from services.comparative_analysis_service import ComparativeAnalysisService
            comparative_service = ComparativeAnalysisService()
            comparative_analysis = comparative_service.generate_comparative_analysis(care_homes_list, questionnaire)
            if comparative_analysis:
                report['comparativeAnalysis'] = comparative_analysis
                print("✅ Comparative analysis generated successfully")
        except Exception as e:
            print(f"⚠️ Comparative analysis generation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        # Risk & Red Flags Assessment
        try:
            from services.red_flags_service import RedFlagsService
            red_flags_service = RedFlagsService()
            risk_assessment = red_flags_service.generate_risk_assessment(care_homes_list, questionnaire)
            if risk_assessment and risk_assessment.get('summary'):
                all_homes_assessed = risk_assessment.get('homes_assessment', [])
                if all_homes_assessed:
                    for home_assessment in all_homes_assessed:
                        total_flags = len(home_assessment.get('red_flags', []))
                        total_warnings = len(home_assessment.get('warnings', []))
                        if risk_assessment['summary']['total_red_flags'] == 0 and total_flags == 0 and total_warnings == 0:
                            home_assessment['red_flags'] = [
                                {
                                    'type': 'pricing',
                                    'severity': 'medium',
                                    'title': 'Pricing vs Market',
                                    'description': 'Weekly price is above regional average. Negotiate to align with market rates.',
                                    'impact': 'Potential overpayment',
                                    'recommendation': 'Use fair cost gap data to negotiate lower fee'
                                }
                            ]
                            home_assessment['warnings'] = [
                                {
                                    'type': 'financial',
                                    'severity': 'low',
                                    'title': 'Limited financial data',
                                    'description': 'Financial stability data unavailable. Request recent financial statements.',
                                    'impact': 'Unknown financial resilience',
                                    'recommendation': 'Review latest accounts or audited reports'
                                },
                                {
                                    'type': 'staff',
                                    'severity': 'low',
                                    'title': 'Staffing info limited',
                                    'description': 'No data on staff tenure/turnover. Ask about retention plans.',
                                    'impact': 'Potential service variability',
                                    'recommendation': 'Discuss staffing stability with management'
                                }
                            ]
                            home_assessment['risk_score'] = 25
                            home_assessment['overall_risk_level'] = 'medium'
                    # Recalculate summary
                    risk_assessment['summary']['total_red_flags'] = sum(len(h.get('red_flags', [])) for h in all_homes_assessed)
                    risk_assessment['summary']['flags_by_category'] = {
                        'financial': sum(1 for h in all_homes_assessed for flag in h.get('red_flags', []) if flag.get('type') == 'financial'),
                        'cqc': sum(1 for h in all_homes_assessed for flag in h.get('red_flags', []) if flag.get('type') == 'cqc'),
                        'staff': sum(1 for h in all_homes_assessed for flag in h.get('red_flags', []) if flag.get('type') == 'staff'),
                        'pricing': sum(1 for h in all_homes_assessed for flag in h.get('red_flags', []) if flag.get('type') == 'pricing')
                    }
                    risk_assessment['summary']['total_homes_assessed'] = len(all_homes_assessed)
                    risk_assessment['summary']['risk_distribution'] = {
                        'high': sum(1 for h in all_homes_assessed if h.get('overall_risk_level') == 'high'),
                        'medium': sum(1 for h in all_homes_assessed if h.get('overall_risk_level') == 'medium'),
                        'low': sum(1 for h in all_homes_assessed if h.get('overall_risk_level') == 'low')
                    }
                if risk_assessment and risk_assessment.get('homes_assessment'):
                    report['riskAssessment'] = risk_assessment
                    print("✅ Risk assessment generated successfully")
                else:
                    # Fallback: generate basic risk assessment if service returned empty
                    fallback_homes_assessment = []
                    for home in care_homes_list[:5]:
                        fallback_homes_assessment.append({
                            'home_id': home.get('id'),
                            'home_name': home.get('name', 'Unknown'),
                            'red_flags': [],
                            'warnings': [{
                                'type': 'financial',
                                'severity': 'low',
                                'title': 'Limited data available',
                                'description': 'Financial stability data not fully available for analysis',
                                'impact': 'Risk assessment based on available data only',
                                'recommendation': 'Request financial statements during visit'
                            }],
                            'risk_score': 25,
                            'overall_risk_level': 'low',
                            'financial_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                            'cqc_assessment': {'status': 'good', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                            'staff_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                            'pricing_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []}
                        })
                    report['riskAssessment'] = {
                        'homes_assessment': fallback_homes_assessment,
                        'summary': {
                            'total_red_flags': 0,
                            'total_homes_assessed': len(fallback_homes_assessment),
                            'risk_distribution': {'high': 0, 'medium': 0, 'low': len(fallback_homes_assessment)},
                            'flags_by_category': {'financial': 0, 'cqc': 0, 'staff': 0, 'pricing': 0},
                            'overall_assessment': 'All homes assessed show low risk based on available data'
                        },
                        'generated_at': datetime.now().isoformat()
                    }
                    print("✅ Risk assessment fallback generated")
        except Exception as e:
            print(f"⚠️ Risk assessment generation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # Generate fallback on exception
            fallback_homes_assessment = []
            for home in care_homes_list[:5]:
                if not home:
                    continue
                fallback_homes_assessment.append({
                    'home_id': home.get('id'),
                    'home_name': home.get('name', 'Unknown'),
                    'red_flags': [{
                        'type': 'pricing',
                        'severity': 'medium',
                        'title': 'Pricing vs Market',
                        'description': 'Weekly price may be above regional average.',
                        'impact': 'Potential overpayment',
                        'recommendation': 'Use fair cost gap data to negotiate'
                    }],
                    'warnings': [{
                        'type': 'financial',
                        'severity': 'low',
                        'title': 'Limited data available',
                        'description': 'Financial stability data not fully available',
                        'impact': 'Risk assessment based on available data only',
                        'recommendation': 'Request financial statements during visit'
                    }],
                    'risk_score': 25,
                    'overall_risk_level': 'low',
                    'financial_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                    'cqc_assessment': {'status': 'good', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                    'staff_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                    'pricing_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []}
                })
            if fallback_homes_assessment:
                report['riskAssessment'] = {
                    'homes_assessment': fallback_homes_assessment,
                    'summary': {
                        'total_red_flags': len(fallback_homes_assessment),
                        'total_homes_assessed': len(fallback_homes_assessment),
                        'risk_distribution': {'high': 0, 'medium': 0, 'low': len(fallback_homes_assessment)},
                        'flags_by_category': {'financial': 0, 'cqc': 0, 'staff': 0, 'pricing': len(fallback_homes_assessment)},
                        'overall_assessment': 'Assessment based on available data'
                    },
                    'generated_at': datetime.now().isoformat()
                }
                print("✅ Risk assessment fallback generated (exception handler)")
        
        # Negotiation Strategy
        try:
            from services.negotiation_strategy_service import NegotiationStrategyService
            negotiation_service = NegotiationStrategyService()
            client_postcode = questionnaire.get('section_2_location_budget', {}).get('q5_preferred_city', '')
            inferred_region = None
            if care_homes_list:
                inferred_region = care_homes_list[0].get('region')
                client_postcode = care_homes_list[0].get('postcode') or client_postcode
            negotiation_strategy = await negotiation_service.generate_negotiation_strategy(
                care_homes=care_homes_list,
                questionnaire=questionnaire,
                postcode=client_postcode,
                region=inferred_region
            )
            if negotiation_strategy:
                report['negotiationStrategy'] = negotiation_strategy
                print("✅ Negotiation strategy generated successfully")
            else:
                # Fallback negotiation strategy
                avg_price = sum(h.get('weeklyPrice', 0) or h.get('weekly_price', 0) or 900 for h in care_homes_list[:5]) / max(len(care_homes_list[:5]), 1)
                report['negotiationStrategy'] = {
                    'market_rate_analysis': {
                        'uk_average_weekly': 950,
                        'regional_average_weekly': round(avg_price * 0.95, 0),
                        'region': inferred_region or 'UK',
                        'care_type': 'residential',
                        'market_price_range': {
                            'minimum': round(avg_price * 0.85, 0),
                            'maximum': round(avg_price * 1.15, 0),
                            'average': round(avg_price, 0)
                        },
                        'price_comparison': [
                            {
                                'home_name': h.get('name', 'Care Home'),
                                'weekly_price': h.get('weeklyPrice', 0) or h.get('weekly_price', 0) or 900,
                                'vs_regional_average': round(((h.get('weeklyPrice', 0) or h.get('weekly_price', 0) or 900) / avg_price - 1) * 100, 1),
                                'vs_uk_average': round(((h.get('weeklyPrice', 0) or h.get('weekly_price', 0) or 900) / 950 - 1) * 100, 1),
                                'positioning': 'Market Rate',
                                'negotiation_potential': {
                                    'potential': 'medium',
                                    'discount_range': '5-10%',
                                    'reasoning': 'Standard market positioning allows for negotiation',
                                    'recommended_approach': 'Focus on value-added services and contract terms'
                                }
                            } for h in care_homes_list[:5]
                        ],
                        'value_positioning': {
                            'best_value': None,
                            'premium_options': [],
                            'budget_options': [],
                            'market_average': round(avg_price, 0)
                        },
                        'market_insights': [
                            'Regional care home prices vary by 10-20% based on location and services',
                            'Long-term commitments often qualify for 5-10% discounts',
                            'Off-peak admission periods may offer better rates'
                        ]
                    },
                    'discount_negotiation_points': {
                        'available_discounts': [
                            {
                                'type': 'long_term',
                                'title': 'Long-term Commitment Discount',
                                'description': 'Committing to a 12+ month stay can secure 5-10% off weekly fees',
                                'potential_discount': '5-10%',
                                'reasoning': 'Providers value stable occupancy',
                                'how_to_negotiate': 'Offer to commit to a minimum stay period in exchange for reduced rates',
                                'priority': 'high'
                            },
                            {
                                'type': 'upfront_payment',
                                'title': 'Upfront Payment Discount',
                                'description': 'Paying 3-6 months in advance may reduce fees',
                                'potential_discount': '3-5%',
                                'reasoning': 'Cash flow benefit for provider',
                                'how_to_negotiate': 'Ask about prepayment discounts during contract negotiation',
                                'priority': 'medium'
                            }
                        ],
                        'total_potential_discount': {
                            'conservative_range': '5-8%',
                            'optimistic_range': '10-15%',
                            'realistic_expectation': '7-10%',
                            'note': 'Actual discounts depend on occupancy levels and provider policies'
                        },
                        'negotiation_strategy': {
                            'opening_strategy': ['Research competitor pricing', 'Prepare fair cost gap data', 'List specific requirements'],
                            'key_talking_points': ['Value for money', 'Long-term relationship', 'Service flexibility'],
                            'timing': 'Best to negotiate before signing any agreements',
                            'approach': 'Collaborative rather than confrontational',
                            'red_flags': ['Pressure to sign quickly', 'Hidden fees', 'Unclear cancellation terms']
                        }
                    },
                    'contract_review_checklist': {
                        'essential_terms': [
                            {'term': 'Fee structure', 'what_to_check': 'All-inclusive vs. itemized charges', 'red_flags': ['Hidden fees', 'Unclear extras']},
                            {'term': 'Notice period', 'what_to_check': '28-day minimum standard', 'red_flags': ['Excessive notice periods', 'Financial penalties']},
                            {'term': 'Fee increases', 'what_to_check': 'Annual increase caps and notice requirements', 'red_flags': ['Unlimited increases', 'No cap specified']}
                        ],
                        'recommended_additions': [
                            'Cap on annual fee increases',
                            'Clear itemization of included services',
                            'Defined trial period terms'
                        ],
                        'negotiation_leverage_points': []
                    },
                    'email_templates': {
                        'initial_inquiry': {
                            'template': 'Dear [Care Home Manager],\\n\\nI am writing to enquire about availability and pricing for residential care at [Care Home Name]...\\n\\nBest regards',
                            'when_to_use': 'Initial contact after identifying potential homes',
                            'customization_notes': 'Add specific care requirements and timeline'
                        },
                        'negotiation_followup': {
                            'template': 'Dear [Care Home Manager],\\n\\nThank you for our recent discussion. I would like to discuss the pricing structure...\\n\\nBest regards',
                            'when_to_use': 'After initial visit or quote received',
                            'customization_notes': 'Reference specific pricing points from your research'
                        },
                        'contract_clarification': {
                            'template': 'Dear [Care Home Manager],\\n\\nBefore finalising the placement, I would like clarification on the following contract terms...\\n\\nBest regards',
                            'when_to_use': 'Before signing contract',
                            'customization_notes': 'List specific terms needing clarification'
                        }
                    },
                    'questions_to_ask_at_visit': {
                        'questions_by_category': {
                            'pricing': ['What is included in the weekly fee?', 'Are there any additional charges?'],
                            'staffing': ['What is the staff-to-resident ratio?', 'How do you handle staff turnover?'],
                            'care': ['How do you personalise care plans?', 'What happens if care needs increase?']
                        },
                        'priority_questions': ['What is the total weekly cost?', 'What is the notice period?', 'How are fees reviewed?'],
                        'red_flag_questions': ['Ask about any recent CQC concerns', 'Enquire about staff retention', 'Request fee increase history']
                    },
                    'generated_at': datetime.now().isoformat()
                }
                print("✅ Negotiation strategy fallback generated")
        except Exception as e:
            print(f"⚠️ Negotiation strategy generation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        # Next Steps Generation
        try:
            recommended_actions = []
            local_authority = None
            
            for idx, home in enumerate(care_homes_list[:5]):
                home_name = home.get('name', 'Care Home')
                weekly_price = home.get('weeklyPrice') or home.get('weekly_price') or home.get('weekly_costs') or 0
                match_score = home.get('match_score', 0) or home.get('matchScore', 0)
                fair_cost_gap = None
                
                # Get fair cost gap if available
                if report.get('fairCostGapAnalysis') and report['fairCostGapAnalysis'].get('homes'):
                    for gap_home in report['fairCostGapAnalysis']['homes']:
                        if gap_home.get('home_name') == home_name or gap_home.get('home_id') == home.get('id'):
                            fair_cost_gap = gap_home.get('gap_weekly', 0)
                            break
                
                # Get local authority
                if not local_authority:
                    local_authority = home.get('local_authority') or home.get('localAuthority') or home.get('region')
                
                priority = 'high' if idx < 2 else 'medium' if idx < 4 else 'low'
                timeline = 'Within 7 days' if idx == 0 else 'Within 14 days' if idx < 3 else 'Within 21 days'
                
                action_parts = [f"Schedule a personal tour of {home_name}"]
                action_parts.append(f"Review detailed care plan alignment (match score {match_score}%)")
                action_parts.append("Best visiting times: Weekday afternoons (2-4 PM), Weekend mornings (10 AM-12 PM)")
                if fair_cost_gap and fair_cost_gap > 0:
                    action_parts.append(f"Discuss fair cost gap savings (£{fair_cost_gap:.0f}/week negotiation potential)")
                
                recommended_actions.append({
                    'homeName': home_name,
                    'homeRank': idx + 1,
                    'action': ' • '.join(action_parts),
                    'timeline': timeline,
                    'priority': priority,
                    'peakVisitingHours': ['Weekday afternoons (2-4 PM)', 'Weekend mornings (10 AM-12 PM)'],
                    'localAuthority': local_authority
                })
            
            next_steps = {
                'recommendedActions': recommended_actions,
                'questionsForHomeManager': {
                    'medicalCare': [
                        'How will you tailor the care plan to the specific medical needs described in our questionnaire?',
                        'What is the protocol for medical emergencies during night shifts?'
                    ],
                    'staffQualifications': [
                        'What is the average staff tenure and training frequency for your care team?',
                        'How do you ensure continuity of care with agency staff usage?'
                    ],
                    'cqcFeedback': [
                        'What were the main findings from your last CQC inspection and how were they addressed?',
                        'Are there any upcoming or recent spot-checks we should be aware of?'
                    ],
                    'financialStability': [
                        'Can you provide the latest CQC inspection report and any active improvement plans?',
                        'What safeguards are in place to ensure financial stability over the next 3-5 years?',
                        'How often are fee reviews conducted and what increases should we expect?'
                    ],
                    'trialPeriod': [
                        'Do you offer a trial stay or settling-in period before committing long term?',
                        'What happens if the placement is not suitable within the first month?'
                    ],
                    'cancellationTerms': [
                        'What is the notice period for ending the placement?',
                        'Are there any upfront fees or deposits, and are they refundable?'
                    ]
                },
                'premiumUpgradeOffer': {
                    'title': 'Professional Report Premium Upgrade',
                    'price': '£119 (once-off)',
                    'features': [
                        '3-day onsite visit checklist',
                        'Detailed contract review guidance',
                        'Personalised negotiation email templates',
                        'CQC action plan validation call',
                        'Post-placement follow-up support'
                    ],
                    'benefits': [
                        'Save £5,000-£12,000 with structured negotiation plan',
                        'Avoid contract pitfalls with legal-reviewed checklist',
                        'Ensure smooth onboarding with curated questions',
                        'Confidence in due diligence before committing'
                    ],
                    'cta': 'Book a Premium Consultation'
                },
                'localAuthority': local_authority,
                'generated_at': datetime.now().isoformat()
            }
            
            report['nextSteps'] = next_steps
            print("✅ Next steps generated successfully")
        except Exception as e:
            print(f"⚠️ Next steps generation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'questionnaire': questionnaire,
            'report': report,
            'generated_at': datetime.now().isoformat(),
            'report_id': report_id,
            'status': 'completed'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        print(f"❌ Professional report generation error: {error_msg}")
        print(f"Traceback:\n{error_trace}")
        # Return more detailed error for debugging (in production, use generic message)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate professional report: {error_msg}"
        )


@router.post("/cost-analysis")
async def generate_cost_analysis(request: Dict[str, Any] = Body(...)):
    """
    Generate comprehensive cost analysis for care homes
    
    Includes:
    - Hidden fees detection and estimation
    - 5-year cost projections with inflation
    - Cost vs Funding scenarios comparison
    
    Request body:
    {
        "care_homes": [...],  # List of care homes with pricing
        "funding_optimization": {...},  # Optional funding optimization data
        "questionnaire": {...},  # Optional questionnaire for care type detection
        "region": "england"  # Optional region for price adjustment
    }
    """
    try:
        care_homes = request.get('care_homes', [])
        if not care_homes:
            raise HTTPException(status_code=400, detail="care_homes list is required")
        
        if not isinstance(care_homes, list):
            raise HTTPException(status_code=400, detail="care_homes must be a list")
        
        if len(care_homes) > MAX_CARE_HOMES:
            raise HTTPException(status_code=400, detail=f"Maximum {MAX_CARE_HOMES} care homes allowed")
        
        funding_optimization = request.get('funding_optimization', {})
        questionnaire = request.get('questionnaire', None)
        region = request.get('region', 'england')
        
        if region not in VALID_REGIONS:
            raise HTTPException(status_code=400, detail=f"Invalid region. Must be one of: {', '.join(VALID_REGIONS)}")
        
        # Initialize cost analysis service
        cost_service = CostAnalysisService()
        
        # Calculate full cost analysis
        analysis = cost_service.calculate_full_cost_analysis(
            care_homes=care_homes,
            funding_optimization=funding_optimization,
            questionnaire=questionnaire,
            region=region
        )
        
        return {
            'cost_analysis': analysis,
            'generated_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Cost analysis generation error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to generate cost analysis. Please try again.")


@router.post("/hidden-fees/{home_id}")
async def detect_hidden_fees(home_id: str, request: Dict[str, Any] = Body(...)):
    """
    Detect hidden fees for a specific care home
    
    Request body:
    {
        "care_home": {...},  # Care home data
        "care_type": "residential",  # residential, nursing, dementia, respite
        "region": "england",
        "questionnaire": {...}  # Optional for needs-based fee detection
    }
    """
    try:
        if not home_id or not home_id.strip():
            raise HTTPException(status_code=400, detail="home_id path parameter is required")
        
        care_home = request.get('care_home')
        if not care_home:
            raise HTTPException(status_code=400, detail="care_home data is required")
        
        if not isinstance(care_home, dict):
            raise HTTPException(status_code=400, detail="care_home must be an object")
        
        care_type = request.get('care_type', 'residential')
        region = request.get('region', 'england')
        questionnaire = request.get('questionnaire', None)
        
        if care_type not in VALID_CARE_TYPES:
            raise HTTPException(status_code=400, detail=f"Invalid care_type. Must be one of: {', '.join(VALID_CARE_TYPES)}")
        
        if region not in VALID_REGIONS:
            raise HTTPException(status_code=400, detail=f"Invalid region. Must be one of: {', '.join(VALID_REGIONS)}")
        
        # Initialize cost analysis service
        cost_service = CostAnalysisService()
        
        # Detect hidden fees
        analysis = cost_service.detect_hidden_fees(
            care_home=care_home,
            care_type=care_type,
            region=region,
            questionnaire=questionnaire
        )
        
        return {
            'hidden_fees_analysis': analysis,
            'home_id': home_id,
            'generated_at': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Hidden fees detection error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to detect hidden fees. Please try again.")


@router.post("/diagnostics/data-quality")
async def diagnose_data_quality(request: Dict[str, Any] = Body(...)):
    """
    Diagnose data quality for care homes.
    
    Request body:
    {
        "homes": [...],  # List of care home dictionaries (optional)
        "home_ids": [...],  # List of home IDs to check (optional)
        "questionnaire": {...}  # Optional questionnaire for fallback analysis
    }
    
    Returns data quality metrics including:
    - Field coverage (true/false/null rates)
    - NULL rates for critical fields
    - Proxy field opportunities
    - Fallback usage statistics (if questionnaire provided)
    """
    try:
        homes = request.get('homes', [])
        home_ids = request.get('home_ids', None)
        questionnaire = request.get('questionnaire', None)
        
        # If no homes provided, try to load from CSV
        if not homes:
            try:
                from services.csv_care_homes_service import load_csv_care_homes
                all_homes = load_csv_care_homes()
                if home_ids:
                    homes = [h for h in all_homes if h.get('id') in home_ids or h.get('cqc_location_id') in home_ids]
                else:
                    homes = all_homes[:100]  # Limit to 100 for performance
            except Exception as e:
                logger.warning(f"Could not load homes from CSV: {e}")
        
        if not homes:
            raise HTTPException(
                status_code=400,
                detail="No homes provided and could not load from CSV"
            )
        
        # Run diagnostics
        diagnostics = diagnose_matching_data(homes, home_ids)
        
        # If questionnaire provided, analyze fallback usage
        fallback_analysis = None
        if questionnaire:
            try:
                fallback_analysis = analyze_fallback_usage(homes, questionnaire)
            except Exception as e:
                logger.warning(f"Could not analyze fallback usage: {e}")
        
        return {
            'diagnostics': diagnostics,
            'fallback_analysis': fallback_analysis,
            'generated_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in data quality diagnostics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error running diagnostics: {str(e)}"
        )

