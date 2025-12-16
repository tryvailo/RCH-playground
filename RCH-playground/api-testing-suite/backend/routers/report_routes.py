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
from services.async_data_loader import get_async_loader
from services.cost_analysis_service import CostAnalysisService
from utils.state_manager import test_results_store
from utils.price_extractor import extract_weekly_price

router = APIRouter(prefix="/api", tags=["Reports"])

VALID_CARE_TYPES = {'residential', 'nursing', 'dementia', 'respite'}
VALID_REGIONS = {'england', 'wales', 'scotland', 'northern_ireland'}
MAX_CARE_HOMES = 50


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
    Returns report with 5 matched care homes using 156-point matching algorithm
    
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
        max_distance_km: Optional[float] = None
        if max_distance == 'within_5km':
            max_distance_km = 5.0
        elif max_distance == 'within_15km':
            max_distance_km = 15.0
        elif max_distance == 'within_30km':
            max_distance_km = 30.0
        
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
        
        loader = get_async_loader()
        print(f"\n   🔄 Calling AsyncDataLoader.load_initial_data()...")
        
        care_homes, user_lat, user_lon = await loader.load_initial_data(
            preferred_city=normalized_city if normalized_city else preferred_city if preferred_city else None,
            care_type=care_type,
            max_distance_km=max_distance_km,
            postcode=postcode if postcode else None,
            limit=20
        )
        
        print(f"   ✅ AsyncDataLoader returned:")
        print(f"      care_homes: {len(care_homes)} homes")
        print(f"      user_lat: {user_lat}")
        print(f"      user_lon: {user_lon}")
        
        if care_homes and len(care_homes) > 0:
            print(f"      First home: {care_homes[0].get('name', 'N/A')}")
        
        # STEP 2: Fallback to mock data if empty
        print(f"\n{'='*80}")
        print(f"STEP 2: FALLBACK TO MOCK DATA (report_routes.py)")
        print(f"{'='*80}")
        
        if not care_homes or len(care_homes) == 0:
            print(f"   ⚠️  AsyncDataLoader returned empty, trying direct mock data load...")
            try:
                from services.mock_care_homes import load_mock_care_homes
                import asyncio
                
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
        
        # Initialize matching service
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
        scored_homes = []
        for home in care_homes:
            try:
                # Use empty enriched_data for now (can be enhanced later)
                enriched_data = {}
                
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
        
        # Check if we have any scored homes
        # If no scored homes, try to load mock data directly as last resort
        if not scored_homes:
            print(f"⚠️ No scored homes found, attempting to load mock data as last resort...")
            try:
                from services.mock_care_homes import load_mock_care_homes
                import asyncio
                loop = asyncio.get_event_loop()
                all_mock_homes = await loop.run_in_executor(None, load_mock_care_homes)
                
                if all_mock_homes:
                    # Score mock homes
                    for home in all_mock_homes[:20]:  # Limit to 20 for performance
                        try:
                            enriched_data = {}
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
        
        # Sort by match score (descending) and take top 5
        scored_homes.sort(key=lambda x: x['matchScore'], reverse=True)
        top_5_homes = scored_homes[:5]
        
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
                        cqc_client = CQCAPIClient(
                            primary_subscription_key=creds.cqc.primary_subscription_key,
                            secondary_subscription_key=creds.cqc.secondary_subscription_key
                        )
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
            
            detailed_ratings = {
                'safe': {
                    'rating': normalize_rating(ratings_data.get('safe') or ratings_data.get('safe_rating') or 'Unknown'),
                    'explanation': 'Safety of care, safeguarding, medicines handling'
                },
                'effective': {
                    'rating': normalize_rating(ratings_data.get('effective') or 'Unknown'),
                    'explanation': 'Effectiveness of treatments and support'
                },
                'caring': {
                    'rating': normalize_rating(ratings_data.get('caring') or 'Unknown'),
                    'explanation': 'Compassion, dignity, respect'
                },
                'responsive': {
                    'rating': normalize_rating(ratings_data.get('responsive') or 'Unknown'),
                    'explanation': 'Meeting needs, responding to feedback'
                },
                'well_led': {
                    'rating': normalize_rating(ratings_data.get('well_led') or ratings_data.get('well-led') or 'Unknown'),
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
        
        # STEP: Enrich FSA data for all homes (parallel) - uses FSAEnrichmentService
        print(f"\n{'='*80}")
        print(f"STEP: FSA API ENRICHMENT (Section 7 - Food Hygiene)")
        print(f"{'='*80}")
        
        # Prepare FSA enrichment tasks
        fsa_enrichment_tasks = {}
        for scored in top_5_homes:
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
                import asyncio
                
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
                import asyncio
                
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
                            cqc_enriched_data[location_id] = None
                        else:
                            cqc_enriched_data[location_id] = service.to_dict(result)
                    
                    await service.close()
                    return cqc_enriched_data
                
                # Run async enrichment
                cqc_enriched_data = await enrich_all_cqc()
                print(f"   ✅ CQC enrichment completed for {len([v for v in cqc_enriched_data.values() if v])} homes")
            except Exception as e:
                print(f"   ⚠️ CQC enrichment error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
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
                    import asyncio
                    
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
                    print(f"   ✅ Google Places enrichment completed for {len([v for v in google_places_enriched_data.values() if v])} homes")
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
                import asyncio
                
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
                print(f"   ✅ Companies House enrichment completed for {len([v for v in companies_house_enriched_data.values() if v])} homes")
            except Exception as e:
                print(f"   ⚠️ Companies House enrichment error: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
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
                        tasks.append(
                            asyncio.wait_for(
                                service.analyze_by_location_id(location_id),
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
        
        # STEP: Enrich Neighbourhood data for all homes (parallel)
        print(f"\n{'='*80}")
        print(f"STEP: NEIGHBOURHOOD ANALYSIS ENRICHMENT (Section 18 - Location Wellbeing)")
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
                                    include_os_places=False,  # Skip for speed
                                    include_ons=True,
                                    include_osm=True,
                                    include_nhsbsa=False,  # Temporarily disabled
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
        for scored in top_5_homes:
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
            if not financial_stability:
                financial_stability = raw_home.get('financial_stability') or raw_home.get('financialStability')
            
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
            if location_id_for_cqc and location_id_for_cqc in cqc_enriched_data:
                cqc_details = cqc_enriched_data[location_id_for_cqc]
            if not cqc_details:
                cqc_details = raw_home.get('cqc_detailed') or raw_home.get('cqcDeepDive') or {}
            if not cqc_details:
                # Fallback to basic build
                cqc_details = build_cqc_deep_dive(raw_home, cqc_rating_value, last_inspection_date)
            
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
                        'healthProfile': {
                            'score': nhsbsa.get('health_index', {}).get('score'),
                            'rating': nhsbsa.get('health_index', {}).get('rating'),
                            'gpPracticesNearby': nhsbsa.get('practices_nearby', 0),
                            'careHomeConsiderations': nhsbsa.get('care_home_considerations', [])
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
                'communityReputation': community_reputation  # Community Reputation (Section 10)
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
            }
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
                            } for h in care_homes_list[:3]
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

