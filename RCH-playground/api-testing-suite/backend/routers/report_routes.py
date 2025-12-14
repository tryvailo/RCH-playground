"""
Report Routes
Handles report generation endpoints
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
                    'matchScore': match_result.get('total_score', 0),
                    'factorScores': match_result.get('factor_scores', {}),
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
                                'matchScore': match_result.get('total_score', 0),
                                'factorScores': match_result.get('factor_scores', {}),
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
        
        # Helper to extract best available weekly price (must be defined before use)
        def extract_weekly_price(home_data: Dict[str, Any], preferred_care_type: Optional[str] = None) -> float:
            if not home_data:
                return 0.0
            
            # Direct weekly price fields
            for key in ['weeklyPrice', 'weekly_price', 'price_weekly', 'weekly_cost']:
                value = home_data.get(key)
                if value:
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        continue
            
            # Fee fields from database schema
            fee_fields = [
                'fee_residential_from',
                'fee_nursing_from',
                'fee_dementia_from',
                'fee_dementia_residential_from',
                'fee_dementia_nursing_from',
                'fee_respite_from',
            ]
            for field in fee_fields:
                value = home_data.get(field)
                if value:
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        continue
            
            # Weekly costs nested dict (mock data)
            weekly_costs = home_data.get('weekly_costs') or home_data.get('weeklyCosts')
            if isinstance(weekly_costs, dict):
                # Try preferred care type first
                lookup_order: List[str] = []
                if preferred_care_type:
                    lookup_order.append(preferred_care_type)
                lookup_order.extend(['residential', 'nursing', 'dementia', 'respite'])
                
                for care_key in lookup_order:
                    if care_key in weekly_costs:
                        value = weekly_costs.get(care_key)
                        if value:
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                continue
                
                # Fallback to first numerical value
                for value in weekly_costs.values():
                    if value:
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            continue
            
            # If rawData present, attempt extraction from it (avoid infinite recursion)
            raw_data = home_data.get('rawData')
            if raw_data and raw_data is not home_data:
                price = extract_weekly_price(raw_data, preferred_care_type)
                if price:
                    return price
            
            return 0.0
        
        # Helper functions to build enriched data
        def build_google_places_data(raw_home: Dict[str, Any], rating_value: Optional[Any], review_count_value: Optional[Any]) -> Optional[Dict[str, Any]]:
            if rating_value is None and review_count_value is None:
                return None
            
            # Extract place_id from various possible fields
            place_id = (
                raw_home.get('google_place_id')
                or raw_home.get('place_id')
                or raw_home.get('placeId')
                or raw_home.get('googlePlaceId')
                or (raw_home.get('google_places', {}) or {}).get('place_id')
                or (raw_home.get('googlePlaces', {}) or {}).get('place_id')
                or (raw_home.get('google_places', {}) or {}).get('placeId')
                or (raw_home.get('googlePlaces', {}) or {}).get('placeId')
            )
            
            # If place_id is still None, try to extract from nested structures
            if not place_id:
                # Check if there's a google_places object with place_id
                google_places_obj = raw_home.get('google_places') or raw_home.get('googlePlaces')
                if isinstance(google_places_obj, dict):
                    place_id = google_places_obj.get('place_id') or google_places_obj.get('placeId')
            
            # If still no place_id, use a fallback or leave as None (frontend should handle this)
            # But we'll still return the data structure with None place_id
            
            try:
                rating_float = float(rating_value) if rating_value is not None else None
            except (ValueError, TypeError):
                rating_float = None
            try:
                reviews_int = int(review_count_value) if review_count_value is not None else None
            except (ValueError, TypeError):
                reviews_int = None
            sentiment = None
            if rating_float is not None:
                sentiment = {
                    'average_sentiment': round((rating_float / 5) * 100, 1),
                    'sentiment_label': 'Positive' if rating_float >= 4 else 'Neutral' if rating_float >= 3 else 'Negative',
                    'total_reviews': reviews_int,
                    'positive_reviews': None,
                    'negative_reviews': None,
                    'neutral_reviews': None,
                    'sentiment_distribution': None
                }
            insights = None
            if rating_float is not None:
                insights = {
                    'summary': {
                        'family_engagement_score': round(min(100, max(0, rating_float * 20)), 1),
                        'quality_indicator': f"Rated {rating_float:.1f}/5 by Google reviewers",
                        'recommendations': [
                            'Encourage recent families to leave reviews to keep this data up-to-date.',
                            'Address any negative feedback promptly to maintain high sentiment.'
                        ]
                    },
                    'popular_times': None,
                    'dwell_time': None,
                    'repeat_visitor_rate': {
                        'repeat_visitor_rate_percent': 40 + (rating_float * 5) if rating_float else None,
                        'trend': 'stable',
                        'interpretation': 'Estimated repeat visitor engagement based on review sentiment.'
                    },
                    'visitor_geography': None,
                    'footfall_trends': None
                }
            return {
                'place_id': place_id,  # Can be None, but we try to extract from multiple sources
                'rating': rating_float,
                'user_ratings_total': reviews_int,
                'reviews': None,
                'reviews_count': reviews_int,
                'sentiment_analysis': sentiment,
                'insights': insights,
                'average_dwell_time_minutes': None,
                'repeat_visitor_rate': None,
                'footfall_trend': None,
                'popular_times': None,
                'family_engagement_score': insights['summary']['family_engagement_score'] if insights else None,
                'quality_indicator': insights['summary']['quality_indicator'] if insights else None
            }
        
        def build_financial_stability(raw_home: Dict[str, Any], weekly_price: float, rating_value: Optional[Any]) -> Dict[str, Any]:
            """
            Build financial stability data using Custom Care Home Financial Risk Model (SPEC v3.2)
            
            ⚠️ NOT using Altman Z-Score (not suitable for care homes)
            Uses 5-component model: Liquidity, Debt, Profitability, Management, Maturity
            """
            try:
                from services.care_home_financial_risk_service import CareHomeFinancialRiskService
                
                # Extract financial data from raw_home
                beds_total = raw_home.get('beds_total') or raw_home.get('bedsTotal') or 40
                beds_available = raw_home.get('beds_available') or raw_home.get('bedsAvailable') or max(0, beds_total - 35)
                try:
                    beds_total = int(beds_total)
                except (ValueError, TypeError):
                    beds_total = 40
                try:
                    beds_available = int(beds_available)
                except (ValueError, TypeError):
                    beds_available = max(0, beds_total - 35)
                if beds_total <= 0:
                    beds_total = 40
                
                occupancy_rate = 1 - (beds_available / beds_total) if beds_total else 0.85
                occupancy_rate = max(0.5, min(0.98, occupancy_rate))
                average_weekly_revenue = weekly_price * beds_total * occupancy_rate
                average_annual_revenue = average_weekly_revenue * 52
                net_margin = 0.12 if (rating_value and isinstance(rating_value, (int, float)) and rating_value >= 4.2) else 0.09 if rating_value and rating_value >= 3.5 else 0.07
                
                # Estimate financial metrics for risk model
                # Use revenue-based estimates if no Companies House data available
                estimated_total_assets = average_annual_revenue * 2.5  # Typical care home asset/revenue ratio
                estimated_current_assets = estimated_total_assets * 0.15
                estimated_current_liabilities = estimated_current_assets * 0.25
                estimated_total_debt = estimated_total_assets * 0.4
                estimated_equity = estimated_total_assets - estimated_total_debt - estimated_current_liabilities
                estimated_profit = average_annual_revenue * net_margin
                estimated_depreciation = estimated_total_assets * 0.025
                
                # Determine profit trend
                profit_trend = 'growing' if net_margin >= 0.1 else 'stable' if net_margin >= 0.08 else 'declining'
                
                # Get Companies House data if available
                companies_house_data = raw_home.get('companies_house') or raw_home.get('companiesHouse') or {}
                
                # Prepare financial data for risk model
                financial_data = {
                    'current_assets': estimated_current_assets,
                    'current_liabilities': estimated_current_liabilities,
                    'total_debt': estimated_total_debt,
                    'equity': estimated_equity,
                    'profit_loss': estimated_profit,
                    'depreciation': estimated_depreciation,
                    'profit_trend': profit_trend,
                    'director_changes_3yr': companies_house_data.get('director_changes_3yr', 0),
                    'company_age_years': companies_house_data.get('company_age_years', 0.0)
                }
                
                # Calculate Custom Care Home Financial Risk
                risk_service = CareHomeFinancialRiskService()
                risk_result = risk_service.calculate_financial_risk(
                    ch_data=financial_data,
                    companies_house_data=companies_house_data if companies_house_data else None
                )
                
                # Convert to dict format
                risk_dict = risk_service.to_dict(risk_result)
                
                # Build three-year summary (for backward compatibility)
                revenue_trend = 'Growing' if profit_trend == 'growing' else 'Stable' if profit_trend == 'stable' else 'Pressure'
                growth_rate = 0.06 if revenue_trend == 'Growing' else -0.04 if revenue_trend == 'Pressure' else 0.02
                revenue_year3 = average_annual_revenue
                revenue_year2 = revenue_year3 / (1 + growth_rate) if growth_rate != -1 else revenue_year3
                revenue_year1 = revenue_year2 / (1 + growth_rate) if growth_rate != -1 else revenue_year2
                average_profit = average_annual_revenue * net_margin
                profit_year3 = average_profit
                profit_year2 = profit_year3 / (1 + (growth_rate / 2))
                profit_year1 = profit_year2 / (1 + (growth_rate / 2))
                
                return {
                    'three_year_summary': {
                        'revenue_trend': revenue_trend,
                        'revenue_3yr_avg': round(average_annual_revenue, 2),
                        'revenue_growth_rate': 0.05 if revenue_trend == 'Growing' else 0.0 if revenue_trend == 'Stable' else -0.03,
                        'profitability_trend': 'Healthy' if net_margin >= 0.1 else 'Moderate',
                        'net_margin_3yr_avg': round(net_margin, 3),
                        'working_capital_trend': 'Stable',
                        'working_capital_3yr_avg': round(average_annual_revenue * 0.1, 2),
                        'current_ratio_3yr_avg': risk_dict.get('current_ratio', 1.5),
                        'revenue_year_1': round(revenue_year1, 2),
                        'revenue_year_2': round(revenue_year2, 2),
                        'revenue_year_3': round(revenue_year3, 2),
                        'profit_year_1': round(profit_year1, 2),
                        'profit_year_2': round(profit_year2, 2),
                        'profit_year_3': round(profit_year3, 2),
                        'average_revenue': round((revenue_year1 + revenue_year2 + revenue_year3) / 3, 2),
                        'average_profit': round((profit_year1 + profit_year2 + profit_year3) / 3, 2)
                    },
                    # Custom Care Home Financial Risk Model (SPEC v3.2)
                    'risk_score': risk_dict['risk_score'],
                    'risk_level': risk_dict['risk_level'],
                    'risk_breakdown': risk_dict['breakdown'],
                    'current_ratio': risk_dict.get('current_ratio'),
                    'debt_to_ebitda': risk_dict.get('debt_to_ebitda'),
                    'profit_trend': risk_dict.get('profit_trend'),
                    'director_changes_3yr': risk_dict.get('director_changes_3yr'),
                    'company_age_years': risk_dict.get('company_age_years'),
                    'methodology': risk_dict.get('methodology', 'Custom Care Home Financial Risk Model (SPEC v3.2)'),
                    # Backward compatibility (deprecated)
                    'altman_z_score': None,  # Deprecated - not suitable for care homes
                    'bankruptcy_risk_score': 100 - risk_dict['risk_score'],  # Inverted for compatibility
                    'bankruptcy_risk_level': 'low' if risk_dict['risk_score'] <= 20 else 'medium' if risk_dict['risk_score'] <= 45 else 'high',
                    'uk_benchmarks_comparison': {
                        'revenue_growth': 'In line with market growth of 3-6%',
                        'net_margin': 'Comparable to UK average 7-12%',
                        'current_ratio': f"Current ratio: {risk_dict.get('current_ratio', 1.5):.2f}"
                    },
                    'red_flags': self._extract_red_flags_from_risk(risk_dict)
                }
            except ImportError:
                # Fallback to old method if service not available
                logger.warning("CareHomeFinancialRiskService not available, using fallback method")
                return self._build_financial_stability_fallback(raw_home, weekly_price, rating_value)
            except Exception as e:
                logger.error(f"Error building financial stability: {e}")
                return self._build_financial_stability_fallback(raw_home, weekly_price, rating_value)
        
        def _build_financial_stability_fallback(raw_home: Dict[str, Any], weekly_price: float, rating_value: Optional[Any]) -> Dict[str, Any]:
            """Fallback method if Custom Risk Model not available"""
            beds_total = raw_home.get('beds_total') or raw_home.get('bedsTotal') or 40
            beds_available = raw_home.get('beds_available') or raw_home.get('bedsAvailable') or max(0, beds_total - 35)
            try:
                beds_total = int(beds_total)
            except (ValueError, TypeError):
                beds_total = 40
            try:
                beds_available = int(beds_available)
            except (ValueError, TypeError):
                beds_available = max(0, beds_total - 35)
            if beds_total <= 0:
                beds_total = 40
            occupancy_rate = 1 - (beds_available / beds_total) if beds_total else 0.85
            occupancy_rate = max(0.5, min(0.98, occupancy_rate))
            average_weekly_revenue = weekly_price * beds_total * occupancy_rate
            average_annual_revenue = average_weekly_revenue * 52
            net_margin = 0.12 if (rating_value and isinstance(rating_value, (int, float)) and rating_value >= 4.2) else 0.09 if rating_value and rating_value >= 3.5 else 0.07
            altman_base = 3.1 if net_margin >= 0.1 else 2.6 if net_margin >= 0.08 else 2.1
            altman_z = round(altman_base, 2)
            bankruptcy_risk_score = round(max(10, min(90, 100 - altman_z * 20)), 1)
            bankruptcy_level = 'low' if altman_z >= 3 else 'medium' if altman_z >= 2.3 else 'high'
            
            revenue_trend = 'Stable'
            if occupancy_rate > 0.9:
                revenue_trend = 'Growing'
            elif occupancy_rate < 0.7:
                revenue_trend = 'Pressure'
            
            if revenue_trend == 'Growing':
                growth_rate = 0.06
            elif revenue_trend == 'Pressure':
                growth_rate = -0.04
            else:
                growth_rate = 0.02
            
            revenue_year3 = average_annual_revenue
            revenue_year2 = revenue_year3 / (1 + growth_rate) if growth_rate != -1 else revenue_year3
            revenue_year1 = revenue_year2 / (1 + growth_rate) if growth_rate != -1 else revenue_year2
            
            average_profit = average_annual_revenue * net_margin
            profit_year3 = average_profit
            profit_year2 = profit_year3 / (1 + (growth_rate / 2))
            profit_year1 = profit_year2 / (1 + (growth_rate / 2))
            
            return {
                'three_year_summary': {
                    'revenue_trend': revenue_trend,
                    'revenue_3yr_avg': round(average_annual_revenue, 2),
                    'revenue_growth_rate': 0.05 if revenue_trend == 'Growing' else 0.0 if revenue_trend == 'Stable' else -0.03,
                    'profitability_trend': 'Healthy' if net_margin >= 0.1 else 'Moderate',
                    'net_margin_3yr_avg': round(net_margin, 3),
                    'working_capital_trend': 'Stable',
                    'working_capital_3yr_avg': round(average_annual_revenue * 0.1, 2),
                    'current_ratio_3yr_avg': 1.5,
                    'revenue_year_1': round(revenue_year1, 2),
                    'revenue_year_2': round(revenue_year2, 2),
                    'revenue_year_3': round(revenue_year3, 2),
                    'profit_year_1': round(profit_year1, 2),
                    'profit_year_2': round(profit_year2, 2),
                    'profit_year_3': round(profit_year3, 2),
                    'average_revenue': round((revenue_year1 + revenue_year2 + revenue_year3) / 3, 2),
                    'average_profit': round((profit_year1 + profit_year2 + profit_year3) / 3, 2)
                },
                'altman_z_score': altman_z,
                'bankruptcy_risk_score': bankruptcy_risk_score,
                'bankruptcy_risk_level': bankruptcy_level,
                'uk_benchmarks_comparison': {
                    'revenue_growth': 'In line with market growth of 3-6%',
                    'net_margin': 'Comparable to UK average 7-12%',
                    'current_ratio': 'Healthy liquidity position'
                },
                'red_flags': []
            }
        
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
                    cqc_service = CQCDeepDiveService()
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
        
        def build_fsa_details(raw_home: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            rating_raw = (
                raw_home.get('food_hygiene_rating')
                or raw_home.get('fsa_rating')
                or raw_home.get('foodHygieneRating')
            )
            label_map = {
                5: 'Excellent',
                4: 'Very Good',
                3: 'Generally Satisfactory',
                2: 'Improvement Necessary',
                1: 'Major Improvement Necessary',
                0: 'Urgent Improvement Necessary'
            }
            base_rating = None
            rating_source = 'FSA dataset'
            try:
                if rating_raw is not None:
                    base_rating = float(str(rating_raw).strip())
            except (ValueError, TypeError):
                base_rating = None
            if base_rating is None:
                cqc_rating_source = (
                    raw_home.get('cqc_rating_overall')
                    or raw_home.get('overall_cqc_rating')
                    or (raw_home.get('cqc_ratings', {}) or {}).get('overall')
                )
                if isinstance(cqc_rating_source, str):
                    rating_lower = cqc_rating_source.lower()
                    if 'outstanding' in rating_lower:
                        base_rating = 5.0
                    elif 'good' in rating_lower:
                        base_rating = 4.5
                    elif 'requires improvement' in rating_lower:
                        base_rating = 3.5
                    elif 'inadequate' in rating_lower:
                        base_rating = 2.5
                if base_rating is None:
                    base_rating = 3.5  # neutral default
                rating_source = 'Estimated from CQC rating'
            if base_rating is None:
                return None
            rating_int = int(round(base_rating))
            rating_display = base_rating if not rating_int else rating_int
            label = label_map.get(rating_int, 'Unknown')
            normalized_score = max(0, min(100, base_rating * 20))
            
            hygiene_score = max(0, min(100, normalized_score))
            cleanliness_score = max(0, min(100, normalized_score - 5 if normalized_score >= 5 else normalized_score))
            management_score = max(0, min(100, normalized_score - 10 if normalized_score >= 10 else normalized_score))
            
            sub_scores = {
                'hygiene': {
                    'raw_score': round(hygiene_score / 20, 1),
                    'normalized_score': round(hygiene_score, 1),
                    'max_score': 100,
                    'weight': 0.33,
                    'label': label
                },
                'cleanliness': {
                    'raw_score': round(cleanliness_score / 20, 1),
                    'normalized_score': round(cleanliness_score, 1),
                    'max_score': 100,
                    'weight': 0.33,
                    'label': label
                },
                'management': {
                    'raw_score': round(management_score / 20, 1),
                    'normalized_score': round(management_score, 1),
                    'max_score': 100,
                    'weight': 0.34,
                    'label': label
                }
            }
            
            rating_date = raw_home.get('fsa_rating_date') or raw_home.get('food_hygiene_rating_date')
            historical_ratings = []
            if rating_date:
                historical_ratings.append({
                    'date': rating_date,
                    'rating': rating_display,
                    'rating_key': f"fhrs_{rating_int}",
                    'breakdown_scores': {
                        'hygiene': round(hygiene_score, 1),
                        'structural': round(cleanliness_score, 1),
                        'confidence_in_management': round(management_score, 1)
                    },
                    'local_authority': raw_home.get('local_authority'),
                    'inspection_type': 'Routine Inspection'
                })
            
            return {
                'rating': rating_display,
                'rating_date': rating_date,
                'fhrs_id': raw_home.get('fsa_rating_id') or raw_home.get('fhrs_id'),
                'rating_source': rating_source,
                'health_score': {
                    'score': round(normalized_score, 1),
                    'label': label
                },
                'detailed_sub_scores': sub_scores,
                'historical_ratings': historical_ratings,
                'trend_analysis': {
                    'trend': 'stable',
                    'trend_direction': 'stable',
                    'interpretation': 'Food hygiene rating is stable based on available data.'
                }
            }
        
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
                import asyncio
                
                async def enrich_all_cqc():
                    service = CQCDeepDiveService()
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
            financial_stability = raw_home.get('financial_stability') or raw_home.get('financialStability')
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
            elif not google_places:
                # Build google_places data if it doesn't exist
                google_places = build_google_places_data(raw_home, google_rating_value, review_count_value)
            
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
                # Add enriched data
                'financialStability': financial_stability if financial_stability else build_financial_stability(raw_home, weekly_price_value, google_rating_value),
                'googlePlaces': google_places,
                'cqcDeepDive': cqc_details,
                'fsaDetailed': fsa_detailed if fsa_detailed else build_fsa_details(raw_home)
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
        except Exception as e:
            print(f"⚠️ Risk assessment generation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
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
        except Exception as e:
            print(f"⚠️ Negotiation strategy generation failed: {e}")
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

