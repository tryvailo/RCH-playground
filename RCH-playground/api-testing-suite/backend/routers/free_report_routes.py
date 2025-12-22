"""
Free Report Routes
Handles free report generation endpoint

Uses shared utilities:
- utils.price_extractor for price extraction (shared with Professional Report)
- utils.geo for distance calculations
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
import asyncio
import uuid
import logging
import json
from datetime import datetime

from utils.price_extractor import extract_weekly_price, extract_price_range
from utils.geo import calculate_distance_km, validate_coordinates
from utils.distance_calculator import calculate_home_distance
from models.free_report_models import FreeReportRequest, FreeReportResponse
from services.fair_cost_gap_service import get_fair_cost_gap_service
from utils.logging_utils import GenerationContext, GenerationStep

# Configure logging
logger = logging.getLogger(__name__)

# Import MatchingService and MatchingInputs for improved matching algorithm
try:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent.parent
    matching_service_path = project_root / "RCH-playground" / "src" / "free_report_viewer" / "services"
    if str(matching_service_path) not in sys.path:
        sys.path.insert(0, str(matching_service_path))
    from matching_service import MatchingService
    
    models_path = project_root / "RCH-playground" / "api-testing-suite" / "backend" / "models"
    if str(models_path) not in sys.path:
        sys.path.insert(0, str(models_path))
    from matching_models import MatchingInputs
    
    MATCHING_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MatchingService not available: {e}")
    MATCHING_SERVICE_AVAILABLE = False
    MatchingService = None
    MatchingInputs = None

router = APIRouter(prefix="/api", tags=["Free Report"])


@router.post("/free-report", response_model=FreeReportResponse)
async def generate_free_report(request: FreeReportRequest):
    """
    Generate free report from simple questionnaire
    
    Pydantic automatically validates the request.
    Returns report with 3 matched care homes using 50-point matching algorithm
    """
    # Initialize generation context
    report_id = str(uuid.uuid4())
    context = GenerationContext(report_id, request.postcode, request.care_type)
    
    context.log_step_start(GenerationStep.INITIALIZATION)
    
    # Initialize llm_insights early to ensure it's always in response
    llm_insights = {
        'generated_at': datetime.now().isoformat(),
        'method': 'data_driven_analysis',
        'insights': {
            'overall_explanation': {
                'summary': 'Report generation in progress...',
                'key_findings': [],
                'confidence_level': 'medium'
            },
            'home_insights': []
        }
    }
    
    try:
        # Extract validated questionnaire data (already validated by Pydantic)
        postcode = request.postcode
        budget = request.budget
        care_type = request.care_type  # Already validated enum
        chc_probability = request.chc_probability
        
        # Extract optional fields
        location_postcode = request.location_postcode or postcode
        timeline = request.timeline
        medical_conditions = request.medical_conditions
        max_distance_km = request.max_distance_km
        priority_order = request.priority_order
        priority_weights = request.priority_weights
        
        context.log_step_complete(GenerationStep.INITIALIZATION)
        
        # Import services
        from services.async_data_loader import get_async_loader
        from services.database_service import DatabaseService
        
        # Resolve postcode to local authority
        loader = get_async_loader()
        user_lat, user_lon = None, None
        local_authority = None
        
        try:
            # Try to resolve postcode
            postcode_info = await loader.resolve_postcode(postcode)
            if postcode_info:
                local_authority = postcode_info.get('local_authority') or postcode_info.get('localAuthority')
                user_lat = postcode_info.get('latitude')
                user_lon = postcode_info.get('longitude')
                print(f"✅ Postcode resolved: {postcode} -> LA: {local_authority}, coords: ({user_lat}, {user_lon})")
            else:
                print(f"⚠️ Postcode resolution returned no data for: {postcode}")
        except Exception as e:
            print(f"⚠️ Postcode resolution failed: {e}")
            # Continue without postcode resolution
        
        # Get care homes using hybrid approach (CQC + Staging)
        # Uses: cqc_carehomes_master_full_data_rows.csv (primary) + carehome_staging_export.csv (auxiliary)
        care_homes = []
        try:
            from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
            loop = asyncio.get_event_loop()
            # use_hybrid=True by default - uses CQC + Staging merged data
            care_homes = await loop.run_in_executor(
                None,
                lambda: get_csv_care_homes(
                    local_authority=local_authority,
                    care_type=care_type,
                    max_distance_km=30.0,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    limit=50,
                    use_hybrid=True  # ✅ Explicitly enable hybrid approach (CQC + Staging)
                )
            )
            print(f"✅ Loaded {len(care_homes)} care homes from hybrid database (CQC + Staging)")
        except Exception as e:
            print(f"⚠️ CSV data load failed: {e}")
            # Fallback to database only (no mock data)
            try:
                loop = asyncio.get_event_loop()
                db_service = DatabaseService()
                care_homes = await loop.run_in_executor(
                    None,
                    lambda: db_service.get_care_homes(
                        local_authority=local_authority,
                        care_type=care_type,
                        max_distance_km=30.0,
                        user_lat=user_lat,
                        user_lon=user_lon,
                        limit=50
                    )
                )
                if care_homes:
                    print(f"✅ Loaded {len(care_homes)} care homes from database")
            except Exception as db_error:
                print(f"⚠️ Database query also failed: {db_error}")
                care_homes = []
        
        if not care_homes:
            raise HTTPException(
                status_code=404,
                detail=f"No care homes found for {local_authority or postcode}. Please try a different location."
            )
        
        # Helper function to calculate distance if not already present
        def calculate_distance_if_needed(home: Dict[str, Any], user_lat: Optional[float], user_lon: Optional[float]) -> Optional[float]:
            """Calculate distance using shared geo utility if not already present"""
            # If distance already calculated, use it (0.0 is valid - home might be at same location)
            distance = home.get('distance_km') or home.get('distance')
            if distance is not None and isinstance(distance, (int, float)) and distance >= 0:
                return float(distance)
            
            # Calculate if we have valid coordinates
            if user_lat and user_lon:
                home_lat = home.get('latitude')
                home_lon = home.get('longitude')
                if home_lat and home_lon:
                    try:
                        # Convert all coordinates to float
                        user_lat_float = float(user_lat)
                        user_lon_float = float(user_lon)
                        home_lat_float = float(home_lat)
                        home_lon_float = float(home_lon)
                        
                        if validate_coordinates(user_lat_float, user_lon_float) and validate_coordinates(home_lat_float, home_lon_float):
                            return calculate_distance_km(user_lat_float, user_lon_float, home_lat_float, home_lon_float)
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Error in calculate_distance_if_needed: {e}")
                        pass
            return None
        
        # Apply filters according to FREE Report specification
        # Filter 1: Quality (CQC Good or Outstanding)
        filtered_homes = [
            h for h in care_homes
            if (h.get('rating') or h.get('overall_rating') or h.get('cqc_rating_overall') or '').lower() in ['good', 'outstanding']
        ]
        
        # Filter 2: Budget (remove >£200 above budget)
        if budget > 0:
            budget_weekly = budget / 4.33 if budget > 1000 else budget  # Assume monthly if > 1000
            filtered_homes = [
                h for h in filtered_homes
                if extract_weekly_price(h, care_type) <= (budget_weekly + 200)
            ]
        
        # Filter 3: Location (max_distance_km or default 30km)
        max_distance = max_distance_km if max_distance_km else 30.0
        if user_lat and user_lon:
            location_filtered = []
            for h in filtered_homes:
                h_lat = h.get('latitude')
                h_lon = h.get('longitude')
                if h_lat and h_lon:
                    try:
                        distance = calculate_distance_km(float(user_lat), float(user_lon), float(h_lat), float(h_lon))
                        if distance <= max_distance:
                            h['distance_km'] = distance
                            location_filtered.append(h)
                    except (ValueError, TypeError):
                        pass
                else:
                    # Include homes without coordinates (will be filtered later)
                    location_filtered.append(h)
            filtered_homes = location_filtered
        
        print(f"🔍 After all filters: {len(filtered_homes)} homes available for matching")
        print(f"🔍 Filtered homes with prices > 0: {sum(1 for h in filtered_homes if extract_weekly_price(h, care_type) > 0)}")
        
        # Use improved matching algorithm if available
        if MATCHING_SERVICE_AVAILABLE and MatchingService and MatchingInputs:
            try:
                # Create MatchingInputs
                matching_inputs = MatchingInputs(
                    postcode=postcode,
                    location_postcode=location_postcode,
                    budget=budget / 4.33 if budget > 1000 else budget,  # Convert monthly to weekly if needed
                    care_type=care_type,
                    user_lat=float(user_lat) if user_lat else None,
                    user_lon=float(user_lon) if user_lon else None,
                    max_distance_km=max_distance_km,
                    timeline=timeline,
                    medical_conditions=medical_conditions,
                    priority_order=priority_order,
                    priority_weights=priority_weights
                )
                
                # Use MatchingService with spec_v3 preset
                matching_service = MatchingService.with_preset('spec_v3')
                print(f"🔍 Calling select_3_strategic_homes_simple with {len(filtered_homes)} filtered homes")
                selected_homes_dict = matching_service.select_3_strategic_homes_simple(filtered_homes, matching_inputs)
                
                print(f"🔍 select_3_strategic_homes_simple returned: {list(selected_homes_dict.keys())}")
                for key, home in selected_homes_dict.items():
                    if home:
                        home_name = home.get('name', 'Unknown')
                        price = extract_weekly_price(home, care_type)
                        print(f"   {key}: {home_name} - Price: £{price}/week")
                
                # Convert to expected format (list of dicts with 'home' and 'match_type')
                top_3_homes = []
                if selected_homes_dict.get('safe_bet'):
                    safe_bet = selected_homes_dict['safe_bet']
                    top_3_homes.append({
                        'home': safe_bet,
                        'match_type': 'Safe Bet',
                        'score': safe_bet.get('match_score', 0),
                        'match_reasoning': safe_bet.get('match_reasoning', [])
                    })
                
                if selected_homes_dict.get('best_reputation'):
                    best_reputation = selected_homes_dict['best_reputation']
                    top_3_homes.append({
                        'home': best_reputation,
                        'match_type': 'Best Reputation',
                        'score': best_reputation.get('match_score', 0),
                        'match_reasoning': best_reputation.get('match_reasoning', [])
                    })
                
                if selected_homes_dict.get('smart_value'):
                    smart_value = selected_homes_dict['smart_value']
                    top_3_homes.append({
                        'home': smart_value,
                        'match_type': 'Smart Value',
                        'score': smart_value.get('match_score', 0),
                        'match_reasoning': smart_value.get('match_reasoning', [])
                    })
                
                print(f"✅ Used improved matching algorithm: selected {len(top_3_homes)} homes before price filter")
                use_improved_algorithm = True
                
            except Exception as e:
                print(f"⚠️ Improved matching algorithm failed: {e}")
                import traceback
                traceback.print_exc()
                use_improved_algorithm = False
                # Log the error details for debugging
                print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
                print(f"🔍 filtered_homes count: {len(filtered_homes) if 'filtered_homes' in locals() else 'N/A'}")
        else:
            use_improved_algorithm = False
        
        # Fallback to old matching method if new one not available or failed
        if not use_improved_algorithm:
            # Simple matching - select top 3 homes (legacy method)
            scored_homes = []
            for home in filtered_homes:
                # Skip homes with zero or missing price
                weekly_price = extract_weekly_price(home, care_type)
                if weekly_price <= 0:
                    home_name = home.get('name', 'Unknown')
                    print(f"⚠️ Skipping {home_name} from scoring: price is £{weekly_price} (missing or invalid)")
                    continue
                
                score = 50.0  # Base score
                
                # Add points for CQC rating
                cqc_rating = (
                    home.get('cqc_rating_overall') or 
                    home.get('overall_cqc_rating') or 
                    home.get('rating') or
                    (home.get('cqc_ratings', {}) or {}).get('overall') or 
                    'Unknown'
                )
                if isinstance(cqc_rating, str):
                    if 'outstanding' in cqc_rating.lower():
                        score += 25
                    elif 'good' in cqc_rating.lower():
                        score += 20
                    elif 'requires improvement' in cqc_rating.lower():
                        score += 10
                
                # Weekly price already extracted and validated above
                # Add points for budget match
                if budget > 0:
                    price_diff = abs(weekly_price - budget)
                    if price_diff < 50:
                        score += 20
                    elif price_diff < 100:
                        score += 15
                    elif price_diff < 200:
                        score += 10
                
                # Calculate distance if needed (for scoring)
                # Use helper function to ensure distance_km is set in home dict for later use
                distance_km = calculate_distance_if_needed(home, user_lat, user_lon)
                if distance_km is not None:
                    home['distance_km'] = distance_km
                else:
                    # If helper didn't calculate, try direct calculation (synchronous for scoring phase)
                    if user_lat and user_lon:
                        home_lat = home.get('latitude')
                        home_lon = home.get('longitude')
                        if home_lat and home_lon:
                            try:
                                user_lat_float = float(user_lat)
                                user_lon_float = float(user_lon)
                                home_lat_float = float(home_lat)
                                home_lon_float = float(home_lon)
                                
                                if validate_coordinates(user_lat_float, user_lon_float) and validate_coordinates(home_lat_float, home_lon_float):
                                    calculated_distance = calculate_distance_km(user_lat_float, user_lon_float, home_lat_float, home_lon_float)
                                    home['distance_km'] = calculated_distance
                            except (ValueError, TypeError):
                                pass
                
                scored_homes.append({
                    'home': home,
                    'score': score
                })
        
        # Sort by score and take top 10 for strategy selection
        scored_homes.sort(key=lambda x: x['score'], reverse=True)
        top_homes = scored_homes[:10]  # Take more homes to select best 3 with different strategies
        
        # Assign match types to top 3 homes based on strategy
        # Strategy 1: Safe Bet - Best balance of quality and price (Good CQC, reasonable price)
        # Strategy 2: Best Value - Best price/quality ratio (Lower price, still good quality)
        # Strategy 3: Premium - Highest quality (Outstanding CQC, may be more expensive)
        
        def get_cqc_rating_score(rating_str):
            """Convert CQC rating to numeric score"""
            if not rating_str or not isinstance(rating_str, str):
                return 0
            rating_lower = rating_str.lower()
            if 'outstanding' in rating_lower:
                return 4
            elif 'good' in rating_lower:
                return 3
            elif 'requires improvement' in rating_lower:
                return 2
            elif 'inadequate' in rating_lower:
                return 1
            return 0
        
        def calculate_value_score(home_data, weekly_price_val):
            """Calculate value score (quality/price ratio)"""
            cqc_score = get_cqc_rating_score(
                home_data.get('cqc_rating_overall') or 
                home_data.get('overall_cqc_rating') or 
                home_data.get('rating') or 
                'Unknown'
            )
            if weekly_price_val > 0:
                return cqc_score / (weekly_price_val / 100)  # Higher is better
            return 0
        
        # Find Safe Bet (best overall balance)
        safe_bet = None
        safe_bet_score = -1
        print(f"🔍 Legacy method: Searching for Safe Bet among {len(top_homes)} homes")
        for scored in top_homes:
            home_data = scored['home']
            weekly_price_val = extract_weekly_price(home_data, care_type)
            cqc_score = get_cqc_rating_score(
                home_data.get('cqc_rating_overall') or 
                home_data.get('overall_cqc_rating') or 
                home_data.get('rating') or 
                'Unknown'
            )
            distance_val = home_data.get('distance_km') or 999
            
            # Safe Bet: Good+ rating, reasonable price, close distance
            # MUST have valid price (> 0)
            if cqc_score >= 3 and weekly_price_val > 0:  # Good or Outstanding AND valid price
                # Balance score: quality + price fit + distance
                balance_score = cqc_score * 10
                if budget > 0:
                    price_diff = abs(weekly_price_val - budget)
                    if price_diff < 100:
                        balance_score += 5
                    elif price_diff < 200:
                        balance_score += 3
                if distance_val and distance_val < 15:
                    balance_score += 2
                
                if balance_score > safe_bet_score:
                    safe_bet_score = balance_score
                    safe_bet = scored
                    print(f"✅ Found Safe Bet candidate: {home_data.get('name', 'Unknown')} - Score: {balance_score}, Price: £{weekly_price_val}, CQC: {cqc_score}")
            elif cqc_score >= 3 and weekly_price_val == 0:
                # Log homes with missing prices
                home_name = home_data.get('name', 'Unknown')
                print(f"⚠️ Skipping {home_name} for Safe Bet: price is £0")
            elif cqc_score < 3:
                home_name = home_data.get('name', 'Unknown')
                print(f"⚠️ Skipping {home_name} for Safe Bet: CQC score {cqc_score} < 3 (need Good/Outstanding)")
        
        if safe_bet:
            print(f"✅ Safe Bet selected: {safe_bet.get('home', {}).get('name', 'Unknown')}")
        else:
            print(f"⚠️ No Safe Bet found among {len(top_homes)} homes")
        
        # Find Best Value (best price/quality ratio)
        best_value = None
        best_value_score = -1
        print(f"🔍 Legacy method: Searching for Best Value among {len(top_homes)} homes (excluding Safe Bet)")
        for scored in top_homes:
            home_data = scored['home']
            if scored == safe_bet:
                continue  # Skip if already selected as Safe Bet
            
            weekly_price_val = extract_weekly_price(home_data, care_type)
            value_score = calculate_value_score(home_data, weekly_price_val)
            
            # Best Value: Good quality but lower price
            cqc_score = get_cqc_rating_score(
                home_data.get('cqc_rating_overall') or 
                home_data.get('overall_cqc_rating') or 
                home_data.get('rating') or 
                'Unknown'
            )
            
            if cqc_score >= 2 and weekly_price_val > 0:  # At least Requires Improvement or better
                if value_score > best_value_score:
                    best_value_score = value_score
                    best_value = scored
                    print(f"✅ Found Best Value candidate: {home_data.get('name', 'Unknown')} - Score: {value_score}, Price: £{weekly_price_val}, CQC: {cqc_score}")
            elif weekly_price_val == 0:
                print(f"⚠️ Skipping {home_data.get('name', 'Unknown')} for Best Value: price is £0")
            elif cqc_score < 2:
                print(f"⚠️ Skipping {home_data.get('name', 'Unknown')} for Best Value: CQC score {cqc_score} < 2 (need Requires Improvement+)")
        
        if best_value:
            print(f"✅ Best Value selected: {best_value.get('home', {}).get('name', 'Unknown')}")
        else:
            print(f"⚠️ No Best Value found among {len(top_homes)} homes (excluding Safe Bet)")
        
        # Find Premium (highest quality within reasonable price uplift range)
        # Premium MUST be more expensive than user's budget in ANY case
        # Strategy: Try 5-30% range first, if not found, expand distance and try 5-35%
        premium = None
        premium_score = -1
        safe_bet_price = None
        if safe_bet:
            safe_bet_home = safe_bet.get('home', {})
            safe_bet_price = extract_weekly_price(safe_bet_home, care_type)
        
        # Premium MUST be >= user's budget (critical requirement)
        min_premium_price_from_budget = budget if budget > 0 else None
        
        # Define reasonable price uplift range for Premium
        # Start with 5-30% above Safe Bet
        min_premium_price = None
        max_premium_price = None
        premium_uplift_percent = 0.30  # Start with 30%
        
        if safe_bet_price and safe_bet_price > 0:
            # Minimum: 5% above Safe Bet OR user's budget (whichever is higher)
            min_premium_price = max(safe_bet_price * 1.05, min_premium_price_from_budget or 0)
            
            # Maximum: 30% above Safe Bet OR £300/week more, whichever is lower
            max_premium_percentage = safe_bet_price * (1 + premium_uplift_percent)
            max_premium_absolute = safe_bet_price + 300
            max_premium_price = min(max_premium_percentage, max_premium_absolute)
            
            print(f"💰 Premium price range (initial): £{min_premium_price or 0:.0f} - £{max_premium_price or 0:.0f} (Safe Bet: £{safe_bet_price or 0:.0f}, Budget: £{budget or 0:.0f})")
        else:
            # If no Safe Bet, use budget as reference
            if budget > 0:
                min_premium_price = budget * 1.05
                max_premium_price = min(budget * 1.30, budget + 300)
                print(f"💰 Premium price range (based on budget): £{min_premium_price or 0:.0f} - £{max_premium_price or 0:.0f} (Budget: £{budget or 0:.0f})")
        
        # Helper function to find Premium from a list of homes
        def find_premium_from_homes(homes_to_search, min_price, max_price, search_context=""):
            """Find Premium home from given list with price constraints"""
            nonlocal premium, premium_score
            candidates_checked = 0
            candidates_rejected = []
            
            for scored in homes_to_search:
                home_data = scored['home']
                if scored == safe_bet or scored == best_value:
                    continue  # Skip if already selected
                
                cqc_score = get_cqc_rating_score(
                    home_data.get('cqc_rating_overall') or 
                    home_data.get('overall_cqc_rating') or 
                    home_data.get('rating') or 
                    'Unknown'
                )
                weekly_price_val = extract_weekly_price(home_data, care_type)
                home_name = home_data.get('name', 'Unknown')
                
                # Premium: Outstanding rating preferred, or highest quality available
                # AND must be within reasonable price uplift range
                # MUST have valid price (> 0) AND >= user's budget
                if cqc_score >= 3 and weekly_price_val > 0:  # Good or Outstanding AND valid price
                    # CRITICAL: Premium MUST be >= user's budget
                    if min_premium_price_from_budget and weekly_price_val < min_premium_price_from_budget:
                        continue  # Skip if cheaper than user's budget
                    
                    candidates_checked += 1
                    is_premium_candidate = True
                    rejection_reason = None
                    
                    # Check price range
                    if min_price and max_price:
                        if weekly_price_val < min_price:
                            is_premium_candidate = False
                            rejection_reason = f"Too cheap: £{weekly_price_val} < £{min_price:.0f} (min)"
                        elif weekly_price_val > max_price:
                            is_premium_candidate = False
                            rejection_reason = f"Too expensive: £{weekly_price_val} > £{max_price:.0f} (max)"
                    elif safe_bet_price:
                        # Fallback: at least more expensive than Safe Bet
                        if weekly_price_val <= safe_bet_price:
                            is_premium_candidate = False
                            rejection_reason = f"Not more expensive than Safe Bet: £{weekly_price_val} <= £{safe_bet_price or 0:.0f}"
                    
                    if is_premium_candidate:
                        premium_candidate_score = cqc_score * 10
                        if cqc_score == 4:  # Outstanding
                            premium_candidate_score += 10
                        
                        # Prefer homes closer to max_premium_price (better value in premium range)
                        if max_price and weekly_price_val > 0:
                            # Score based on how close to optimal premium price (80% of max range)
                            optimal_premium_price = min_price + (max_price - min_price) * 0.8
                            price_diff = abs(weekly_price_val - optimal_premium_price)
                            price_score = max(0, 5 - (price_diff / 50))  # Max 5 points for price positioning
                            premium_candidate_score += price_score
                        
                        if premium_candidate_score > premium_score:
                            premium_score = premium_candidate_score
                            premium = scored
                            print(f"✅ Premium candidate {search_context}: {home_name} - £{weekly_price_val}/week (score: {premium_candidate_score or 0:.1f})")
                    else:
                        candidates_rejected.append({
                            'name': home_name,
                            'price': weekly_price_val,
                            'reason': rejection_reason
                        })
            
            if candidates_checked > 0 and not premium:
                print(f"⚠️ Checked {candidates_checked} Premium candidates {search_context}, none selected:")
                for rejected in candidates_rejected[:5]:  # Show first 5
                    print(f"   - {rejected['name']}: £{rejected['price']}/week - {rejected['reason']}")
            
            return premium is not None
        
        # First pass: find Premium within reasonable price range (5-30%)
        find_premium_from_homes(top_homes, min_premium_price, max_premium_price, "(initial search)")
        
        # Second pass: if no Premium found, expand distance and increase price range to 5-35%
        if not premium:
            print(f"⚠️ No Premium found in initial range (£{min_premium_price or 'N/A'} - £{max_premium_price or 'N/A'})")
            print(f"   Expanding search: increasing distance to 50km and price range to 5-35%")
            
            # Expand distance and reload homes
            expanded_max_distance = 100.0  # Increase from 30km to 100km for Premium search
            expanded_care_homes = []
            try:
                from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
                loop = asyncio.get_event_loop()
                # Use hybrid approach (CQC + Staging)
                expanded_care_homes = await loop.run_in_executor(
                    None,
                    lambda: get_csv_care_homes(
                        use_hybrid=True,  # Explicitly enable hybrid approach
                        local_authority=local_authority,
                        care_type=care_type,
                        max_distance_km=expanded_max_distance,
                        user_lat=user_lat,
                        user_lon=user_lon,
                        limit=200  # Increase limit to get more homes
                    )
                )
                print(f"✅ Loaded {len(expanded_care_homes)} care homes with expanded distance ({expanded_max_distance}km)")
            except Exception as e:
                print(f"⚠️ Failed to load expanded care homes: {e}")
                expanded_care_homes = []
            
            # Score expanded homes
            expanded_scored_homes = []
            for home in expanded_care_homes:
                # Skip homes with zero or missing price
                weekly_price = extract_weekly_price(home, care_type)
                if weekly_price <= 0:
                    continue
                
                score = 50.0  # Base score
                
                # Add points for CQC rating
                cqc_rating = (
                    home.get('cqc_rating_overall') or 
                    home.get('overall_cqc_rating') or 
                    home.get('rating') or
                    (home.get('cqc_ratings', {}) or {}).get('overall') or 
                    'Unknown'
                )
                if isinstance(cqc_rating, str):
                    if 'outstanding' in cqc_rating.lower():
                        score += 25
                    elif 'good' in cqc_rating.lower():
                        score += 20
                    elif 'requires improvement' in cqc_rating.lower():
                        score += 10
                
                # Add points for budget match
                if budget > 0:
                    price_diff = abs(weekly_price - budget)
                    if price_diff < 50:
                        score += 20
                    elif price_diff < 100:
                        score += 15
                    elif price_diff < 200:
                        score += 10
                
                # Calculate distance if needed
                distance_km = calculate_distance_if_needed(home, user_lat, user_lon)
                if distance_km is not None:
                    home['distance_km'] = distance_km
                
                expanded_scored_homes.append({
                    'home': home,
                    'score': score
                })
            
            # Sort and take top homes
            expanded_scored_homes.sort(key=lambda x: x['score'], reverse=True)
            expanded_top_homes = expanded_scored_homes[:20]  # Take more homes for expanded search
            
            # Update price range to 5-35%
            if safe_bet_price and safe_bet_price > 0:
                premium_uplift_percent = 0.35  # Increase to 35%
                min_premium_price_expanded = max(safe_bet_price * 1.05, min_premium_price_from_budget or 0)
                max_premium_percentage_expanded = safe_bet_price * (1 + premium_uplift_percent)
                max_premium_absolute_expanded = safe_bet_price + 300
                max_premium_price_expanded = min(max_premium_percentage_expanded, max_premium_absolute_expanded)
                
                print(f"💰 Premium price range (expanded): £{min_premium_price_expanded or 0:.0f} - £{max_premium_price_expanded or 0:.0f} (Safe Bet: £{safe_bet_price or 0:.0f}, Budget: £{budget or 0:.0f})")
                
                # Search in expanded homes
                find_premium_from_homes(expanded_top_homes, min_premium_price_expanded, max_premium_price_expanded, "(expanded search)")
            
            # If still not found, try fallback: highest quality among homes >= budget
            if not premium:
                print(f"⚠️ No Premium found in expanded range, selecting highest quality among homes >= budget (£{budget:.0f})")
                
                fallback_candidates_checked = 0
                fallback_candidates_rejected = []
                
                # Search in expanded homes
                # Track already selected home names to avoid duplicates
                selected_home_names_for_fallback = set()
                if safe_bet:
                    safe_bet_home = safe_bet.get('home', {})
                    selected_home_names_for_fallback.add(safe_bet_home.get('name'))
                if best_value:
                    best_value_home = best_value.get('home', {})
                    selected_home_names_for_fallback.add(best_value_home.get('name'))
                
                for scored in expanded_top_homes:
                    home_data = scored['home']
                    home_name = home_data.get('name', 'Unknown')
                    
                    # Skip if already selected (check by object reference and name)
                    if scored == safe_bet or scored == best_value:
                        continue
                    if home_name in selected_home_names_for_fallback:
                        continue
                    
                    cqc_score = get_cqc_rating_score(
                        home_data.get('cqc_rating_overall') or 
                        home_data.get('overall_cqc_rating') or 
                        home_data.get('rating') or 
                        'Unknown'
                    )
                    weekly_price_val = extract_weekly_price(home_data, care_type)
                    home_name = home_data.get('name', 'Unknown')
                    
                    # Must be Good/Outstanding
                    if cqc_score >= 3 and weekly_price_val > 0:
                        fallback_candidates_checked += 1
                        
                        # Check price requirements (same as final fallback)
                        meets_budget = budget > 0 and weekly_price_val >= budget
                        exceeds_safe_bet = safe_bet_price and weekly_price_val > safe_bet_price
                        at_least_safe_bet = safe_bet_price and weekly_price_val >= safe_bet_price
                        
                        # Accept if meets any price requirement
                        if not (meets_budget or exceeds_safe_bet or at_least_safe_bet):
                            fallback_candidates_rejected.append({
                                'name': home_name,
                                'price': weekly_price_val,
                                'reason': f"Price £{weekly_price_val} < Safe Bet £{safe_bet_price or 0:.0f} and < Budget £{budget or 0:.0f}"
                            })
                            continue
                        
                        premium_candidate_score = cqc_score * 10
                        if cqc_score == 4:  # Outstanding
                            premium_candidate_score += 10
                        
                        # Prefer higher price in fallback
                        if weekly_price_val > 0 and safe_bet_price:
                            price_bonus = min((weekly_price_val - safe_bet_price) / 10, 5)
                            premium_candidate_score += price_bonus
                        
                        if premium_candidate_score > premium_score:
                            premium_score = premium_candidate_score
                            premium = scored
                            print(f"✅ Premium (final fallback): {home_name} - £{weekly_price_val}/week, CQC score: {cqc_score} (total score: {premium_candidate_score or 0:.1f})")
                
                if fallback_candidates_checked > 0 and not premium:
                    print(f"⚠️ Checked {fallback_candidates_checked} final fallback Premium candidates, none selected:")
                    for rejected in fallback_candidates_rejected[:5]:
                        print(f"   - {rejected['name']}: £{rejected['price']}/week - {rejected['reason']}")
                    
                    # Last resort: search in ALL expanded_care_homes (not just top 20)
                    if expanded_care_homes:
                        print(f"🔍 Last resort: searching in ALL {len(expanded_care_homes)} expanded homes for Premium...")
                        last_resort_candidates = []
                        for home in expanded_care_homes:
                            # Skip homes with zero price
                            weekly_price = extract_weekly_price(home, care_type)
                            if weekly_price <= 0:
                                continue
                            
                            home_name = home.get('name', 'Unknown')
                            if home_name in selected_home_names_for_fallback:
                                continue
                            
                            cqc_score = get_cqc_rating_score(
                                home.get('cqc_rating_overall') or 
                                home.get('overall_cqc_rating') or 
                                home.get('rating') or 
                                'Unknown'
                            )
                            
                            if cqc_score >= 3:  # Good/Outstanding
                                # Check price requirements
                                meets_budget = budget > 0 and weekly_price >= budget
                                exceeds_safe_bet = safe_bet_price and weekly_price > safe_bet_price
                                at_least_safe_bet = safe_bet_price and weekly_price >= safe_bet_price
                                
                                if meets_budget or exceeds_safe_bet or at_least_safe_bet:
                                    # Create scored entry for this home
                                    premium_candidate_score = cqc_score * 10
                                    if cqc_score == 4:  # Outstanding
                                        premium_candidate_score += 10
                                    if weekly_price > 0 and safe_bet_price:
                                        price_bonus = min((weekly_price - safe_bet_price) / 10, 5)
                                        premium_candidate_score += price_bonus
                                    
                                    last_resort_candidates.append({
                                        'home': home,
                                        'score': premium_candidate_score,
                                        'price': weekly_price,
                                        'name': home_name
                                    })
                        
                        # Select best candidate (highest score, or highest price if scores equal)
                        if last_resort_candidates:
                            last_resort_candidates.sort(key=lambda x: (x['score'], x['price']), reverse=True)
                            best_candidate = last_resort_candidates[0]
                            premium = {
                                'home': best_candidate['home'],
                                'score': best_candidate['score'],
                                'match_type': 'Premium'
                            }
                            print(f"✅ Premium (last resort from all expanded homes): {best_candidate['name']} - £{best_candidate['price']}/week (score: {best_candidate['score']:.1f})")
                        else:
                            print(f"⚠️ No Premium candidates found in {len(expanded_care_homes)} expanded homes")
        
        # Fallback: if we don't have 3 different homes, use top scored ones
        # BUT ensure price ordering is maintained
        selected_homes = []
        if safe_bet:
            safe_bet['match_type'] = 'Safe Bet'
            selected_homes.append(safe_bet)
            print(f"✅ Legacy: Safe Bet selected: {safe_bet.get('home', {}).get('name', 'Unknown')}")
        if best_value:
            best_value['match_type'] = 'Best Value'
            selected_homes.append(best_value)
            print(f"✅ Legacy: Best Value selected: {best_value.get('home', {}).get('name', 'Unknown')}")
        if premium:
            premium['match_type'] = 'Premium'
            selected_homes.append(premium)
            print(f"✅ Legacy: Premium selected: {premium.get('home', {}).get('name', 'Unknown')}")
        
        print(f"🔍 Legacy method: Found {len(selected_homes)} homes before fallback")
        
        # If we have less than 3, fill with top scored homes
        # IMPORTANT: Maintain price ordering - Premium must be >= Safe Bet
        remaining_slots = 3 - len(selected_homes)
        if remaining_slots > 0:
            # Get Safe Bet price for comparison
            safe_bet_price_for_fallback = None
            if safe_bet:
                safe_bet_home = safe_bet.get('home', {})
                safe_bet_price_for_fallback = extract_weekly_price(safe_bet_home, care_type)
            
            # Use expanded_top_homes if available (from expanded search), otherwise use top_homes
            homes_to_search = expanded_top_homes if 'expanded_top_homes' in locals() and expanded_top_homes else top_homes
            print(f"🔍 Fallback: searching in {len(homes_to_search)} homes for remaining {remaining_slots} slots")
            
            # Track already selected home names to avoid duplicates
            selected_home_names = {scored.get('home', {}).get('name') for scored in selected_homes if scored.get('home', {}).get('name')}
            
            for scored in homes_to_search:
                # Skip if already selected (check by object reference and name)
                if scored in selected_homes:
                    continue
                
                home_data = scored.get('home', {})
                home_name = home_data.get('name')
                if home_name in selected_home_names:
                    continue
                
                weekly_price_val = extract_weekly_price(home_data, care_type)
                
                # Skip homes with zero price
                if weekly_price_val <= 0:
                    continue
                
                if not scored.get('match_type'):
                    # Get CQC score for quality check
                    cqc_score = get_cqc_rating_score(
                        home_data.get('cqc_rating_overall') or 
                        home_data.get('overall_cqc_rating') or 
                        home_data.get('rating') or 
                        'Unknown'
                    )
                    
                    # Assign based on position AND price/quality constraints
                    if len(selected_homes) == 0:
                        # Safe Bet: Good+ rating required
                        if cqc_score >= 3:
                            scored['match_type'] = 'Safe Bet'
                        else:
                            continue  # Skip if quality insufficient
                    elif len(selected_homes) == 1:
                        # Best Value should be <= Safe Bet (if Safe Bet exists) AND at least Requires Improvement
                        if safe_bet_price_for_fallback and weekly_price_val > safe_bet_price_for_fallback:
                            # Too expensive for Best Value, skip this one
                            continue
                        if cqc_score >= 2:  # At least Requires Improvement
                            scored['match_type'] = 'Best Value'
                        else:
                            continue  # Skip if quality insufficient
                    else:
                        # Premium: Good/Outstanding rating required
                        # Price requirements (in order of preference):
                        # 1. >= budget AND > Safe Bet (ideal)
                        # 2. >= budget (acceptable)
                        # 3. > Safe Bet (acceptable if no budget match)
                        # 4. >= Safe Bet (last resort - better than no Premium)
                        
                        if cqc_score < 3:  # Must be Good or Outstanding
                            print(f"⚠️ Skipping {home_data.get('name', 'Unknown')} for Premium fallback: CQC score {cqc_score} < 3 (need Good/Outstanding)")
                            continue
                        
                        # Check price requirements
                        meets_budget = budget > 0 and weekly_price_val >= budget
                        exceeds_safe_bet = safe_bet_price_for_fallback and weekly_price_val > safe_bet_price_for_fallback
                        at_least_safe_bet = safe_bet_price_for_fallback and weekly_price_val >= safe_bet_price_for_fallback
                        
                        # Accept if meets any price requirement
                        if meets_budget or exceeds_safe_bet or at_least_safe_bet:
                            if not meets_budget and not exceeds_safe_bet:
                                # Only warn if it's the last resort (>= Safe Bet but < budget)
                                print(f"⚠️ Accepting {home_data.get('name', 'Unknown')} as Premium (price £{weekly_price_val} >= Safe Bet £{safe_bet_price_for_fallback or 0:.0f} but < Budget £{budget or 0:.0f})")
                            scored['match_type'] = 'Premium'
                        else:
                            # Price too low - skip
                            if safe_bet_price_for_fallback:
                                print(f"⚠️ Skipping {home_data.get('name', 'Unknown')} for Premium fallback: price £{weekly_price_val} < Safe Bet £{safe_bet_price_for_fallback or 0:.0f}")
                            else:
                                print(f"⚠️ Skipping {home_data.get('name', 'Unknown')} for Premium fallback: price £{weekly_price_val} < Budget £{budget:.0f}")
                            continue
                
                selected_homes.append(scored)
                remaining_slots -= 1
                if remaining_slots == 0:
                    break
        
        # Ensure we have exactly 3 homes
        top_3_homes = selected_homes[:3]
        
        # Log selected homes with prices for verification
        print("\n" + "="*80)
        print("SELECTED HOMES FOR FREE REPORT:")
        print("="*80)
        for idx, scored in enumerate(top_3_homes, 1):
            home = scored.get('home', {})
            match_type = scored.get('match_type', 'Unknown')
            name = home.get('name', 'Unknown')
            weekly_price = extract_weekly_price(home, care_type)
            cqc_rating = (
                home.get('cqc_rating_overall') or 
                home.get('overall_cqc_rating') or 
                home.get('rating') or 
                'Unknown'
            )
            print(f"{idx}. {match_type}: {name}")
            print(f"   Price: £{weekly_price}/week | CQC: {cqc_rating}")
        print("="*80 + "\n")
        
        # Verify price ordering: Premium should be >= Safe Bet, Safe Bet should be >= Best Value
        if len(top_3_homes) >= 2:
            safe_bet_home = None
            premium_home = None
            best_value_home = None
            
            for scored in top_3_homes:
                match_type = scored.get('match_type', '')
                if match_type == 'Safe Bet':
                    safe_bet_home = scored.get('home', {})
                elif match_type == 'Premium':
                    premium_home = scored.get('home', {})
                elif match_type == 'Best Value':
                    best_value_home = scored.get('home', {})
            
            if safe_bet_home and premium_home:
                safe_bet_price = extract_weekly_price(safe_bet_home, care_type)
                premium_price = extract_weekly_price(premium_home, care_type)
                if premium_price < safe_bet_price:
                    print(f"⚠️ WARNING: Premium price (£{premium_price}) < Safe Bet price (£{safe_bet_price})")
                else:
                    print(f"✅ Price ordering correct: Premium (£{premium_price}) >= Safe Bet (£{safe_bet_price})")
                
                # CRITICAL: Premium MUST be >= user's budget
                if budget > 0:
                    if premium_price < budget:
                        print(f"❌ CRITICAL ERROR: Premium price (£{premium_price}) < User budget (£{budget})")
                    else:
                        print(f"✅ Premium price (£{premium_price}) >= User budget (£{budget})")
            
            if safe_bet_home and best_value_home:
                safe_bet_price = extract_weekly_price(safe_bet_home, care_type)
                best_value_price = extract_weekly_price(best_value_home, care_type)
                if best_value_price > safe_bet_price:
                    print(f"⚠️ WARNING: Best Value price (£{best_value_price}) > Safe Bet price (£{safe_bet_price})")
                else:
                    print(f"✅ Price ordering correct: Safe Bet (£{safe_bet_price}) >= Best Value (£{best_value_price})")
        
        # Format homes for response
        care_homes_list = []
        print(f"🔍 Formatting {len(top_3_homes)} homes for response...")
        print(f"🔍 Top 3 homes before price filter: {[h.get('match_type', 'Unknown') for h in top_3_homes]}")
        
        homes_skipped_price = 0
        for scored in top_3_homes:
            home = scored['home']
            print(f"🔍 Processing home: {home.get('name', 'Unknown')}, lat={home.get('latitude')}, lon={home.get('longitude')}")
            
            # Extract weekly price
            weekly_price = extract_weekly_price(home, care_type)
            
            # Final validation: skip homes with zero or missing price
            if weekly_price <= 0:
                home_name = home.get('name', 'Unknown')
                match_type = scored.get('match_type', 'Unknown')
                print(f"⚠️ WARNING: Skipping {home_name} ({match_type}) from final list: price is £{weekly_price}")
                homes_skipped_price += 1
                continue
            
            # Calculate distance using reusable method
            distance_km = await calculate_home_distance(
                home=home,
                user_lat=user_lat,
                user_lon=user_lon,
                postcode_loader=loader
            )
            
            if distance_km is not None:
                print(f"✅ Calculated distance for {home.get('name', 'Unknown')}: {distance_km} km")
            else:
                print(f"⚠️ WARNING: Could not calculate distance for {home.get('name', 'Unknown')} - coordinates may be missing")
            
            # Format address
            address = home.get('address', '')
            if not address:
                parts = [home.get('name', ''), home.get('postcode', '')]
                address = ', '.join([p for p in parts if p])
            
            # Extract FSA rating data from database first
            fsa_rating = home.get('fsa_rating') or home.get('food_hygiene_rating')
            fsa_color = home.get('fsa_color')
            fsa_rating_date = home.get('fsa_rating_date') or home.get('food_hygiene_rating_date')
            
            # If no FSA data in DB, try to get from facilities
            if not fsa_rating:
                facilities = home.get('facilities', {})
                if isinstance(facilities, dict):
                    fsa_rating = facilities.get('fsa_rating') or facilities.get('food_hygiene_rating')
            
            # If still no FSA rating, try FSA API (improved lookup with multiple strategies)
            if not fsa_rating:
                home_name = home.get('name', '')
                home_postcode = home.get('postcode', '')
                home_lat = home.get('latitude')
                home_lon = home.get('longitude')
                
                if home_name:
                    try:
                        from api_clients.fsa_client import FSAAPIClient
                        fsa_client = FSAAPIClient()
                        
                        # Strategy 1: Search by business type + name (more accurate for care homes)
                        # Business type 7835 = "Hospitals/Childcare/Caring Premises"
                        establishments = []
                        try:
                            establishments = await fsa_client.search_by_business_type(
                                business_type_id=7835,
                                name=home_name,
                                page_size=10
                            )
                        except Exception as e:
                            print(f"⚠️ FSA business type search failed: {e}")
                        
                        # Strategy 2: If no results, try search by name only
                        if not establishments:
                            try:
                                establishments = await fsa_client.search_by_business_name(home_name)
                            except Exception as e:
                                print(f"⚠️ FSA name search failed: {e}")
                        
                        # Strategy 3: If we have coordinates, try location-based search
                        if not establishments and home_lat and home_lon:
                            try:
                                establishments = await fsa_client.search_by_location(
                                    latitude=float(home_lat),
                                    longitude=float(home_lon),
                                    max_distance=0.5  # 500m radius
                                )
                                # Filter by name similarity
                                if establishments:
                                    name_words = set(home_name.lower().split())
                                    best_match = None
                                    best_score = 0
                                    for est in establishments:
                                        est_name = est.get('BusinessName', '').lower()
                                        est_words = set(est_name.split())
                                        # Calculate word overlap
                                        overlap = len(name_words & est_words)
                                        if overlap > best_score:
                                            best_score = overlap
                                            best_match = est
                                    if best_match and best_score >= 2:  # At least 2 words match
                                        establishments = [best_match]
                                    else:
                                        establishments = []
                            except Exception as e:
                                print(f"⚠️ FSA location search failed: {e}")
                        
                        # Process results
                        if establishments and len(establishments) > 0:
                            # Try to find best match by name similarity and postcode
                            best_match = None
                            best_score = 0
                            
                            for est in establishments:
                                est_name = est.get('BusinessName', '').lower()
                                est_postcode = est.get('PostCode', '').upper().replace(' ', '')
                                home_name_lower = home_name.lower()
                                home_postcode_clean = home_postcode.upper().replace(' ', '') if home_postcode else ''
                                
                                score = 0
                                # Name similarity
                                if home_name_lower in est_name or est_name in home_name_lower:
                                    score += 10
                                # Check for common words
                                home_words = set(home_name_lower.split())
                                est_words = set(est_name.split())
                                common_words = home_words & est_words
                                score += len(common_words) * 2
                                
                                # Postcode match (bonus)
                                if home_postcode_clean and est_postcode:
                                    if home_postcode_clean == est_postcode:
                                        score += 20
                                    elif home_postcode_clean[:4] == est_postcode[:4]:  # First 4 chars match
                                        score += 10
                                
                                if score > best_score:
                                    best_score = score
                                    best_match = est
                            
                            # Use best match or first result if no clear best match
                            fsa_establishment = best_match if best_match and best_score >= 5 else establishments[0]
                            rating_value = fsa_establishment.get('RatingValue')
                            
                            if rating_value is not None:
                                # Convert string rating to int (handle "5", "4", etc.)
                                try:
                                    if isinstance(rating_value, str):
                                        if rating_value.isdigit():
                                            fsa_rating = int(rating_value)
                                        elif rating_value.lower() == 'pass':
                                            fsa_rating = 5  # Scotland uses Pass/Fail
                                        elif rating_value.lower() == 'awaiting inspection':
                                            fsa_rating = None
                                    else:
                                        fsa_rating = int(rating_value)
                                    
                                    if fsa_rating:
                                        fsa_rating_date = fsa_establishment.get('RatingDate')
                                        fsa_rating_key = fsa_establishment.get('RatingKey')
                                        print(f"✅ FSA API: {home_name} -> Rating {fsa_rating} (match score: {best_score})")
                                except (ValueError, TypeError):
                                    pass
                        
                        await fsa_client.close()
                    except Exception as fsa_error:
                        print(f"⚠️ FSA API lookup failed for {home_name}: {fsa_error}")
                        import traceback
                        traceback.print_exc()
            
            # Final fallback: if still no FSA rating, use None (don't derive from CQC)
            # This is more honest than deriving a fake rating
            if fsa_rating is None:
                fsa_rating = None
                fsa_color = None
            else:
                # Determine color from rating
                try:
                    rating_num = float(fsa_rating) if isinstance(fsa_rating, (int, float)) else None
                    if rating_num is not None:
                        if rating_num >= 5:
                            fsa_color = 'green'
                        elif rating_num >= 4:
                            fsa_color = 'green'
                        elif rating_num >= 3:
                            fsa_color = 'yellow'
                        else:
                            fsa_color = 'red'
                except (ValueError, TypeError):
                    fsa_color = None
            
            # Get match_type from scored data
            match_type = scored.get('match_type', 'Safe Bet')
            
            care_homes_list.append({
                'id': home.get('cqc_location_id') or home.get('location_id') or home.get('id') or str(uuid.uuid4()),
                'name': home.get('name', 'Unknown'),
                'address': address,
                'postcode': home.get('postcode', ''),
                'city': home.get('city', ''),
                'weekly_cost': round(weekly_price, 2) if weekly_price > 0 else 0.0,
                'rating': (
                    home.get('cqc_rating_overall') or 
                    home.get('overall_cqc_rating') or 
                    home.get('rating') or
                    (home.get('cqc_ratings', {}) or {}).get('overall') or 
                    'Unknown'
                ),
                'distance_km': round(distance_km, 2) if distance_km is not None else None,
                'care_types': home.get('care_types', []),
                'photo_url': (
                    home.get('photo') or 
                    home.get('photo_url') or 
                    home.get('image_url') or
                    # Use Unsplash placeholder if no photo available (no photos in CSV database)
                    f"https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop&q=80"
                ),
                # Contact information from CSV database
                'contact_phone': (home.get('telephone') or home.get('provider_telephone_number') or '').strip() or None,
                'email': (home.get('email') or '').strip() or None,
                'website': (home.get('website') or '').strip() or None,
                'location_id': home.get('cqc_location_id') or home.get('location_id'),
                # Match type (strategy)
                'match_type': match_type,
                # FSA Rating fields
                'fsa_rating': float(fsa_rating) if fsa_rating else None,
                'fsa_color': fsa_color,
                'fsa_rating_date': fsa_rating_date,
                'fsa_rating_key': home.get('fsa_rating_key') or (f'fhrs_{int(fsa_rating)}_en-gb' if fsa_rating else None),
                # Additional fields for LLM insights
                'beds_available': home.get('beds_available'),
                'google_rating': home.get('google_rating'),
                'review_count': home.get('review_count'),
                # Coordinates for map (extract from home)
                'latitude': home.get('latitude'),
                'longitude': home.get('longitude'),
                '_original_home': home  # Store original for detailed analysis
            })
            print(f"✅ Added {home.get('name', 'Unknown')} to care_homes_list: lat={home.get('latitude')}, lon={home.get('longitude')}")
        
        if homes_skipped_price > 0:
            print(f"⚠️ WARNING: {homes_skipped_price} homes were skipped due to zero/missing price")
            print(f"⚠️ Final care_homes_list count: {len(care_homes_list)} (expected 3)")
        
        # CRITICAL: If we have less than 3 homes, try to fill from filtered_homes
        if len(care_homes_list) < 3:
            print(f"⚠️ CRITICAL: Only {len(care_homes_list)} homes in final list, trying to fill from filtered_homes")
            # Get homes that weren't selected yet
            selected_names = {h.get('name') for h in care_homes_list}
            # Use filtered_homes if available, otherwise try to get from top_homes
            homes_to_fill = filtered_homes if 'filtered_homes' in locals() else (top_homes if 'top_homes' in locals() else [])
            for home in homes_to_fill[:20]:  # Check top 20
                if len(care_homes_list) >= 3:
                    break
                home_name = home.get('name') if isinstance(home, dict) else home.get('home', {}).get('name')
                if not home_name or home_name in selected_names:
                    continue
                # Extract home dict if needed
                home_dict = home if isinstance(home, dict) else home.get('home', {})
                weekly_price = extract_weekly_price(home_dict, care_type)
                if weekly_price > 0:
                    # Add as additional home (simplified format)
                    care_homes_list.append({
                        'id': home_dict.get('cqc_location_id') or home_dict.get('location_id') or home_dict.get('id') or str(uuid.uuid4()),
                        'name': home_name,
                        'match_type': 'Additional' if isinstance(home, dict) else home.get('match_type', 'Additional')
                    })
                    selected_names.add(home_name)
                    print(f"✅ Added additional home: {home_name} (price: £{weekly_price}/week)")
        
        # Build area map data (MUST be after care_homes_list is populated)
        # Separate from area_profile to ensure it's always generated
        try:
            # Build area map data
            # Use the SAME distance_km values from care_homes_list to ensure consistency
            map_homes = []
            valid_home_coords = []
            
            # Use top_3_homes directly to get coordinates (more reliable than care_homes_list which may have serialization issues)
            print(f"🔍 Building area_map: processing {len(top_3_homes)} homes from top_3_homes")
            for idx, scored in enumerate(top_3_homes):
                home = scored['home']
                home_name = home.get('name', 'Unknown')
                # Get coordinates directly from home (from CSV service)
                home_lat = home.get('latitude')
                home_lon = home.get('longitude')
                match_type = scored.get('match_type', 'Safe Bet')
                
                # Get distance_km from care_homes_list using index (they should be in the same order)
                # Fallback to searching by name if index doesn't work
                distance_km = None
                if idx < len(care_homes_list):
                    distance_km = care_homes_list[idx].get('distance_km')
                if distance_km is None:
                    # Fallback: search by name
                    for home_data in care_homes_list:
                        if home_data.get('name') == home_name:
                            distance_km = home_data.get('distance_km')
                            break
                
                print(f"🔍 Processing {home_name} for map: lat={home_lat} (type: {type(home_lat)}), lon={home_lon} (type: {type(home_lon)})")
                
                # Convert to float if they are strings or other types
                if home_lat is not None and home_lon is not None:
                    try:
                        home_lat_float = float(home_lat)
                        home_lon_float = float(home_lon)
                        
                        # Validate coordinates are reasonable (UK is roughly 49-61°N, 2°W-2°E)
                        if 49.0 <= home_lat_float <= 61.0 and -10.0 <= home_lon_float <= 5.0:
                            # Get id from home or care_homes_list
                            home_id = home.get('cqc_location_id') or home.get('location_id') or home.get('id')
                            if not home_id:
                                # Try to get from care_homes_list
                                for home_data in care_homes_list:
                                    if home_data.get('name') == home_name:
                                        home_id = home_data.get('id')
                                        break
                            map_homes.append({
                                'id': home_id or str(uuid.uuid4()),
                                'name': home_name,
                                'lat': home_lat_float,
                                'lng': home_lon_float,
                                'distance_km': round(distance_km, 2) if distance_km is not None else None,
                                'match_type': match_type
                            })
                            valid_home_coords.append((home_lat_float, home_lon_float))
                            print(f"✅ Added {home_name} to map: lat={home_lat_float}, lng={home_lon_float}, distance={distance_km}km")
                        else:
                            print(f"⚠️ Skipping {home_name}: coordinates out of UK range (lat={home_lat_float}, lon={home_lon_float})")
                    except (ValueError, TypeError) as coord_error:
                        print(f"⚠️ Error converting coordinates for {home_name}: {coord_error}")
                else:
                    print(f"⚠️ Skipping {home_name} from map: missing coordinates (lat={home_lat}, lon={home_lon})")
            
            # Determine user location for map:
            # 1. Use resolved postcode coordinates if available
            # 2. Otherwise, calculate center point from homes
            # 3. Fallback to first home's location
            if user_lat and user_lon:
                try:
                    map_user_lat = float(user_lat)
                    map_user_lon = float(user_lon)
                    print(f"✅ Using resolved postcode coordinates: ({map_user_lat}, {map_user_lon})")
                except (ValueError, TypeError):
                    # Fallback to center of homes
                    if valid_home_coords:
                        avg_lat = sum(coord[0] for coord in valid_home_coords) / len(valid_home_coords)
                        avg_lon = sum(coord[1] for coord in valid_home_coords) / len(valid_home_coords)
                        map_user_lat = avg_lat
                        map_user_lon = avg_lon
                        print(f"⚠️ Postcode coordinates invalid, using center of homes: ({map_user_lat}, {map_user_lon})")
                    elif map_homes:
                        map_user_lat = map_homes[0]['lat']
                        map_user_lon = map_homes[0]['lng']
                        print(f"⚠️ Using first home location as user location: ({map_user_lat}, {map_user_lon})")
                    else:
                        map_user_lat = 52.4862
                        map_user_lon = -1.8904
                        print(f"⚠️ Using default Birmingham coordinates: ({map_user_lat}, {map_user_lon})")
            elif valid_home_coords:
                # Calculate center point from all homes
                avg_lat = sum(coord[0] for coord in valid_home_coords) / len(valid_home_coords)
                avg_lon = sum(coord[1] for coord in valid_home_coords) / len(valid_home_coords)
                map_user_lat = avg_lat
                map_user_lon = avg_lon
                print(f"⚠️ Postcode resolution failed, using center of homes: ({map_user_lat}, {map_user_lon})")
            else:
                # Last resort: use first home or default
                if map_homes:
                    map_user_lat = map_homes[0]['lat']
                    map_user_lon = map_homes[0]['lng']
                    print(f"⚠️ Using first home location as user location: ({map_user_lat}, {map_user_lon})")
                else:
                    # Absolute fallback (shouldn't happen)
                    map_user_lat = 52.4862
                    map_user_lon = -1.8904
                    print(f"⚠️ Using default Birmingham coordinates: ({map_user_lat}, {map_user_lon})")
            
            # Calculate optimal zoom level based on distances
            # If all homes are within 10km, use zoom 12-13
            # If homes are spread out, use zoom 11-12
            max_distance = 0
            if map_homes:
                distances = [h.get('distance_km') or 0 for h in map_homes if h.get('distance_km') is not None]
                if distances:
                    max_distance = max(distances)
            if max_distance < 5:
                suggested_zoom = 13
            elif max_distance < 10:
                suggested_zoom = 12
            elif max_distance < 20:
                suggested_zoom = 11
            else:
                suggested_zoom = 10
            
            area_map = {
                'user_location': {
                    'lat': map_user_lat,
                    'lng': map_user_lon,
                    'postcode': postcode
                },
                'homes': map_homes,
                'suggested_zoom': suggested_zoom,  # Add suggested zoom for frontend
                'amenities': []  # TODO: Add nearby amenities from OpenStreetMap
            }
            print(f"✅ Area map generated with {len(map_homes)} homes")
            print(f"🔍 Final area_map.homes count: {len(area_map.get('homes', []))}")
        except Exception as map_error:
            print(f"⚠️ Area map generation failed: {map_error}")
            import traceback
            traceback.print_exc()
            # Create minimal area_map with default values
            area_map = {
                'user_location': {
                    'lat': 52.4862,
                    'lng': -1.8904,
                    'postcode': postcode
                },
                'homes': [],
                'suggested_zoom': 12,
                'amenities': []
            }
        
        # Ensure area_map is initialized
        if 'area_map' not in locals() or area_map is None:
            print("⚠️ WARNING: area_map not initialized, creating default")
            area_map = {
                'user_location': {
                    'lat': 52.4862,
                    'lng': -1.8904,
                    'postcode': postcode
                },
                'homes': [],
                'suggested_zoom': 12,
                'amenities': []
            }
        
        # Final verification before adding to response
        print(f"🔍 Final check: area_map.homes count before response: {len(area_map.get('homes', []))}")
        
        # Calculate area profile statistics
        try:
            # Count total homes in area (ALL homes in local_authority, not filtered)
            # This should represent the total market, not just filtered results
            total_homes_in_area = len(care_homes)  # Will be updated below with actual count
            
            # Get ALL homes in local_authority for accurate area statistics (without filters)
            # Uses hybrid approach (CQC + Staging)
            try:
                from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
                loop = asyncio.get_event_loop()
                all_homes_in_area = await loop.run_in_executor(
                    None,
                    lambda: get_csv_care_homes(
                        local_authority=local_authority,
                        use_hybrid=True,  # Explicitly enable hybrid approach
                        care_type=None,  # No care_type filter for total count
                        max_distance_km=None,  # No distance filter for total count
                        user_lat=None,
                        user_lon=None,
                        limit=None  # No limit - get all homes in area
                    )
                )
                total_homes_in_area = len(all_homes_in_area)
                print(f"✅ Total homes in {local_authority or 'area'}: {total_homes_in_area} (all types, all distances)")
            except Exception as count_error:
                print(f"⚠️ Could not get total homes count: {count_error}")
                # Fallback: use filtered count but note it's approximate
                total_homes_in_area = len(care_homes)
                print(f"⚠️ Using filtered count as approximation: {total_homes_in_area}")
            
            # Calculate average weekly cost
            weekly_costs = [extract_weekly_price(h, care_type) for h in care_homes]
            valid_costs = [c for c in weekly_costs if c > 0]
            avg_weekly_cost = sum(valid_costs) / len(valid_costs) if valid_costs else 1200
            
            # Calculate CQC distribution
            cqc_counts = {'outstanding': 0, 'good': 0, 'requires_improvement': 0, 'inadequate': 0}
            for home in care_homes:
                rating = (home.get('cqc_rating_overall') or home.get('overall_cqc_rating') or 
                         home.get('rating') or 'Unknown')
                if isinstance(rating, str):
                    rating_lower = rating.lower()
                    if 'outstanding' in rating_lower:
                        cqc_counts['outstanding'] += 1
                    elif 'good' in rating_lower:
                        cqc_counts['good'] += 1
                    elif 'requires improvement' in rating_lower:
                        cqc_counts['requires_improvement'] += 1
                    elif 'inadequate' in rating_lower:
                        cqc_counts['inadequate'] += 1
            
            # National average comparison (approximate)
            national_avg = 1100  # Approximate UK national average for care homes
            cost_vs_national = round(((avg_weekly_cost - national_avg) / national_avg) * 100, 1)
            
            # Get area name from postcode_info
            area_name = local_authority or 'Your Area'
            
            # Get ONS data using shared ons_loader (reuses neighbourhood module)
            wellbeing_index = 72  # Default
            population_65_plus = 18  # Default
            average_income = 28000  # Default
            green_spaces = 'medium'  # Default
            
            try:
                from data_integrations.ons_loader import ONSLoader
                ons_loader = ONSLoader()
                ons_profile = await ons_loader.get_full_area_profile(postcode)
                
                if not ons_profile.get('error'):
                    # Extract wellbeing index from ONS data
                    wellbeing_data = ons_profile.get('wellbeing', {})
                    if wellbeing_data.get('social_wellbeing_index', {}).get('score'):
                        wellbeing_index = wellbeing_data['social_wellbeing_index']['score']
                    
                    # Extract demographics from ONS data
                    demographics_data = ons_profile.get('demographics', {})
                    elderly_context = demographics_data.get('elderly_care_context', {})
                    if elderly_context.get('over_65_percent'):
                        population_65_plus = elderly_context['over_65_percent']
                    
                    # Extract economic data
                    economic_data = ons_profile.get('economic', {})
                    indicators = economic_data.get('indicators', {})
                    if indicators.get('median_income', {}).get('value'):
                        average_income = indicators['median_income']['value']
                    
                    print(f"✅ ONS data loaded: wellbeing={wellbeing_index}, 65+={population_65_plus}%")
                
                await ons_loader.close()
            except Exception as ons_error:
                print(f"⚠️ ONS loader not available, using defaults: {ons_error}")
            
            area_profile = {
                'area_name': area_name,
                'total_homes': total_homes_in_area,
                'average_weekly_cost': round(avg_weekly_cost, 0),
                'cost_vs_national': cost_vs_national,
                'cqc_distribution': cqc_counts,
                'wellbeing_index': wellbeing_index,
                'demographics': {
                    'population_65_plus': population_65_plus,
                    'average_income': average_income,
                    'green_spaces': green_spaces
                }
            }
        except Exception as area_error:
            print(f"⚠️ Area profile generation failed: {area_error}")
            import traceback
            traceback.print_exc()
            # Continue without area profile
        
        # Get MSIF fair cost and calculate fair cost gap
        context.log_step_start(GenerationStep.GAP_CALCULATION)
        
        msif_lower_bound = 700.0
        try:
            from pricing_calculator import PricingService, CareType
            pricing_service = PricingService()
            care_type_enum = CareType.RESIDENTIAL
            if care_type == 'nursing':
                care_type_enum = CareType.NURSING
            elif care_type == 'residential_dementia':
                care_type_enum = CareType.RESIDENTIAL_DEMENTIA
            
            if local_authority:
                # Access fair_cost_data directly
                care_type_key = care_type_enum.value
                if local_authority in pricing_service.fair_cost_data:
                    la_data = pricing_service.fair_cost_data[local_authority]
                    result = la_data.get(care_type_key)
                    if result:
                        msif_lower_bound = float(result)
        except Exception as e:
            context.log_warning(GenerationStep.GAP_CALCULATION, f"MSIF lookup failed: {e}")
            default_msif = {
                'residential': 700,
                'nursing': 1048,
                'residential_dementia': 800,
                'nursing_dementia': 1048
            }
            msif_lower_bound = float(default_msif.get(care_type, 700))
        
        # Calculate market price (average from homes or use budget)
        if budget > 0:
            market_price = float(budget)
        elif care_homes_list:
            # Calculate average from top 3 homes
            avg_price = sum(h.get('weekly_cost', 0) for h in care_homes_list) / len(care_homes_list)
            market_price = avg_price if avg_price > 0 else 1200.0
        else:
            market_price = 1200.0
        
        # Use FairCostGapService to calculate gap
        gap_service = get_fair_cost_gap_service()
        fair_cost_gap = gap_service.calculate_gap(
            market_price=market_price,
            msif_lower_bound=msif_lower_bound,
            care_type=care_type
        )
        
        context.log_step_complete(
            GenerationStep.GAP_CALCULATION,
            {
                'gap_week': fair_cost_gap['gap_week'],
                'gap_percent': fair_cost_gap['gap_percent']
            }
        )
        
        # Initialize LLM Insights Service
        try:
            from services.free_report_llm_insights_service import FreeReportLLMInsightsService
            from config_manager import get_credentials
            
            # Get OpenAI API key from credentials
            creds = get_credentials()
            openai_api_key = None
            if creds and hasattr(creds, 'openai') and creds.openai:
                openai_api_key = getattr(creds.openai, 'api_key', None)
            
            # Initialize LLM Insights Service
            llm_insights_service = FreeReportLLMInsightsService(openai_api_key=openai_api_key)
            print(f"✅ LLM Insights Service initialized (OpenAI key: {'present' if openai_api_key else 'not configured'})")
        except Exception as import_error:
            print(f"⚠️ Error importing LLM Insights Service: {import_error}")
            import traceback
            traceback.print_exc()
            # Create a dummy service that will use fallback
            class DummyLLMService:
                async def generate_home_insight(self, *args, **kwargs):
                    return {'home_name': 'Unknown', 'match_type': 'Unknown', 'why_selected': '', 'key_strengths': [], 'considerations': []}
            llm_insights_service = DummyLLMService()
            openai_api_key = None
        
        # Initialize LLM Insights structure
        llm_insights = {
            'generated_at': datetime.now().isoformat(),
            'method': 'openai_llm_analysis' if openai_api_key else 'data_driven_analysis',
            'insights': {
                'overall_explanation': {
                    'summary': f"Based on analysis of {len(care_homes)} care homes in your area, we've selected 3 homes that best match your needs: a Safe Bet for reliability, Best Value for affordability, and Premium for highest quality.",
                    'key_findings': [
                        f"Found {len(care_homes)} homes matching your criteria in {local_authority or 'your area'}",
                        f"Average weekly cost in area: £{area_profile.get('average_weekly_cost', 0) if area_profile else 0}",
                        f"All selected homes have CQC ratings of 'Good' or better",
                        f"Fair Cost Gap analysis shows market prices exceed MSIF fair cost by {round(gap_percent, 1)}%"
                    ],
                    'confidence_level': 'high'
                },
                'home_insights': []
            }
        }
        
        # Generate LLM Insights for each home using OpenAI
        # Prepare user context for LLM
        user_context = {
            'budget': budget,
            'care_type': care_type,
            'postcode': postcode,
            'local_authority': local_authority
        }
        
        # Legacy fallback function (kept for error handling)
        def generate_home_insight_fallback(home_data: Dict[str, Any], match_type: str, budget: float, care_type: str, top_3_homes_ref: List) -> Dict[str, Any]:
            """Generate insight explanation for why this home matches the criteria"""
            name = home_data.get('name', 'Unknown')
            rating = home_data.get('rating', 'Unknown')
            weekly_cost = home_data.get('weekly_cost', 0)
            distance_km = home_data.get('distance_km', 0)
            care_types = home_data.get('care_types', [])
            fsa_rating = home_data.get('fsa_rating')
            beds_available = home_data.get('beds_available')
            
            # Get original home data for additional details
            original_home = home_data.get('_original_home')
            if not original_home:
                # Fallback: try to find in top_3_homes
                for scored in top_3_homes_ref:
                    if scored['home'].get('name') == name:
                        original_home = scored['home']
                        break
            
            # Extract additional data from original home
            cqc_safe = original_home.get('cqc_rating_safe') if original_home else None
            cqc_caring = original_home.get('cqc_rating_caring') if original_home else None
            cqc_effective = original_home.get('cqc_rating_effective') if original_home else None
            google_rating = original_home.get('google_rating') if original_home else None
            review_count = original_home.get('review_count') if original_home else None
            
            # Calculate budget fit
            budget_diff = weekly_cost - budget if budget > 0 else 0
            budget_fit_percent = ((budget - abs(budget_diff)) / budget * 100) if budget > 0 else 0
            
            insight = {
                'home_name': name,
                'match_type': match_type,
                'why_selected': '',
                'key_strengths': [],
                'considerations': []
            }
            
            if match_type == 'Safe Bet':
                # Safe Bet: Good balance of quality, price, and location
                why_parts = []
                strength_parts = []
                
                # CQC Rating analysis
                if rating and 'good' in rating.lower():
                    why_parts.append(f"has a 'Good' CQC rating")
                    strength_parts.append(f"Strong regulatory compliance with 'Good' overall CQC rating")
                elif rating and 'outstanding' in rating.lower():
                    why_parts.append(f"has an 'Outstanding' CQC rating")
                    strength_parts.append(f"Exceptional quality with 'Outstanding' CQC rating")
                
                # Price analysis
                if budget > 0:
                    if abs(budget_diff) < 50:
                        why_parts.append(f"priced at £{weekly_cost}/week, closely matching your budget of £{budget}/week")
                        strength_parts.append(f"Excellent budget fit - within £{abs(budget_diff)} of your budget")
                    elif budget_diff < 100:
                        why_parts.append(f"priced at £{weekly_cost}/week, slightly above your budget but still affordable")
                        strength_parts.append(f"Good budget alignment - only £{abs(budget_diff)} above your budget")
                    elif budget_diff < 0:
                        why_parts.append(f"priced at £{weekly_cost}/week, below your budget of £{budget}/week")
                        strength_parts.append(f"Cost-effective option - £{abs(budget_diff)} below your budget")
                
                # Distance analysis
                if distance_km:
                    if distance_km < 5:
                        why_parts.append(f"located just {distance_km:.1f}km away")
                        strength_parts.append(f"Very convenient location - only {distance_km:.1f}km from your postcode")
                    elif distance_km < 10:
                        why_parts.append(f"located {distance_km:.1f}km away")
                        strength_parts.append(f"Convenient location - {distance_km:.1f}km from your postcode")
                    elif distance_km < 15:
                        why_parts.append(f"located {distance_km:.1f}km away")
                        strength_parts.append(f"Accessible location - {distance_km:.1f}km from your postcode")
                
                # Care type match
                if care_type in care_types:
                    why_parts.append(f"offers {care_type} care")
                    strength_parts.append(f"Provides the {care_type} care you need")
                
                # FSA Rating
                if fsa_rating and fsa_rating >= 4:
                    strength_parts.append(f"Excellent food hygiene rating ({fsa_rating}/5)")
                
                # CQC sub-ratings
                if cqc_safe and 'good' in str(cqc_safe).lower():
                    strength_parts.append("Strong safety record (CQC Safe rating: Good)")
                if cqc_caring and 'good' in str(cqc_caring).lower():
                    strength_parts.append("Compassionate care approach (CQC Caring rating: Good)")
                
                # Google reviews
                if google_rating and google_rating >= 4.0 and review_count and review_count >= 10:
                    strength_parts.append(f"Positive community feedback ({google_rating:.1f}/5 from {int(review_count)} reviews)")
                
                # Availability
                if beds_available and beds_available > 0:
                    strength_parts.append(f"Currently has {int(beds_available)} beds available")
                
                insight['why_selected'] = f"{name} was selected as your Safe Bet because it " + ", ".join(why_parts) + "."
                insight['key_strengths'] = strength_parts
                
                # Considerations
                if budget_diff > 100:
                    insight['considerations'].append(f"Price is £{abs(budget_diff)} above your budget - consider negotiating")
                if distance_km and distance_km > 10:
                    insight['considerations'].append(f"Location is {distance_km:.1f}km away - factor in travel time for visits")
                if not fsa_rating:
                    insight['considerations'].append("Food hygiene rating not available - request this information during visit")
            
            elif match_type == 'Best Value':
                # Best Value: Best price/quality ratio
                why_parts = []
                strength_parts = []
                
                # Price analysis (should be lower or good value)
                if budget > 0:
                    if weekly_cost < budget:
                        why_parts.append(f"priced at £{weekly_cost}/week, significantly below your budget of £{budget}/week")
                        strength_parts.append(f"Excellent value - £{abs(budget_diff)} below your budget")
                    elif abs(budget_diff) < 100:
                        why_parts.append(f"priced at £{weekly_cost}/week, close to your budget")
                        strength_parts.append(f"Good value for money - within budget")
                
                # Quality analysis
                if rating and ('good' in rating.lower() or 'outstanding' in rating.lower()):
                    why_parts.append(f"maintains a '{rating}' CQC rating")
                    strength_parts.append(f"Quality care with '{rating}' CQC rating at competitive pricing")
                
                # Care types
                if len(care_types) > 1:
                    why_parts.append(f"offers multiple care types: {', '.join(care_types)}")
                    strength_parts.append(f"Versatile care options: {', '.join(care_types)}")
                elif care_type in care_types:
                    why_parts.append(f"offers {care_type} care")
                    strength_parts.append(f"Provides the {care_type} care you need")
                
                # Distance
                if distance_km and distance_km < 15:
                    strength_parts.append(f"Convenient location - {distance_km:.1f}km away")
                
                # FSA
                if fsa_rating and fsa_rating >= 4:
                    strength_parts.append(f"Good food hygiene standards ({fsa_rating}/5)")
                
                insight['why_selected'] = f"{name} was selected as Best Value because it " + ", ".join(why_parts) + ", offering the best balance of quality and affordability."
                insight['key_strengths'] = strength_parts
                
                # Considerations
                if rating and 'requires improvement' in rating.lower():
                    insight['considerations'].append("CQC rating is 'Requires Improvement' - review latest inspection report")
                if not beds_available or beds_available == 0:
                    insight['considerations'].append("Check current availability - may have waiting list")
            
            elif match_type == 'Premium':
                # Premium: Highest quality available
                why_parts = []
                strength_parts = []
                
                # CQC Rating (should be Outstanding or Good)
                if rating and 'outstanding' in rating.lower():
                    why_parts.append(f"has an 'Outstanding' CQC rating")
                    strength_parts.append(f"Exceptional quality - 'Outstanding' CQC rating (highest possible)")
                elif rating and 'good' in rating.lower():
                    why_parts.append(f"has a 'Good' CQC rating")
                    strength_parts.append(f"High quality care with 'Good' CQC rating")
                
                # CQC sub-ratings
                if cqc_safe and 'outstanding' in str(cqc_safe).lower():
                    strength_parts.append("Outstanding safety standards (CQC Safe rating: Outstanding)")
                elif cqc_safe and 'good' in str(cqc_safe).lower():
                    strength_parts.append("Strong safety record (CQC Safe rating: Good)")
                
                if cqc_caring and 'outstanding' in str(cqc_caring).lower():
                    strength_parts.append("Exceptional compassionate care (CQC Caring rating: Outstanding)")
                elif cqc_caring and 'good' in str(cqc_caring).lower():
                    strength_parts.append("Compassionate care approach (CQC Caring rating: Good)")
                
                if cqc_effective and 'outstanding' in str(cqc_effective).lower():
                    strength_parts.append("Outstanding care effectiveness (CQC Effective rating: Outstanding)")
                
                # Care types (premium often offers multiple)
                if len(care_types) > 2:
                    why_parts.append(f"offers comprehensive care: {', '.join(care_types)}")
                    strength_parts.append(f"Comprehensive care options: {', '.join(care_types)}")
                elif len(care_types) > 1:
                    why_parts.append(f"offers multiple care types: {', '.join(care_types)}")
                    strength_parts.append(f"Multiple care options: {', '.join(care_types)}")
                
                # Google reviews
                if google_rating and google_rating >= 4.5 and review_count and review_count >= 20:
                    why_parts.append(f"has excellent community reviews ({google_rating:.1f}/5 from {int(review_count)} reviews)")
                    strength_parts.append(f"Excellent community reputation ({google_rating:.1f}/5 from {int(review_count)} reviews)")
                elif google_rating and google_rating >= 4.0:
                    strength_parts.append(f"Positive community feedback ({google_rating:.1f}/5)")
                
                # FSA
                if fsa_rating and fsa_rating == 5:
                    strength_parts.append(f"Perfect food hygiene rating (5/5)")
                elif fsa_rating and fsa_rating >= 4:
                    strength_parts.append(f"Excellent food hygiene standards ({fsa_rating}/5)")
                
                # Distance
                if distance_km and distance_km < 10:
                    strength_parts.append(f"Convenient location - {distance_km:.1f}km away")
                
                insight['why_selected'] = f"{name} was selected as Premium because it " + ", ".join(why_parts) + ", representing the highest quality option available."
                insight['key_strengths'] = strength_parts
                
                # Considerations
                if weekly_cost > budget + 200:
                    insight['considerations'].append(f"Premium pricing at £{weekly_cost}/week - £{abs(budget_diff)} above your budget")
                if not beds_available or beds_available == 0:
                    insight['considerations'].append("Check availability - premium homes often have waiting lists")
            
            return insight
        
        # Generate insight for each home using OpenAI LLM
        try:
            print(f"🔍 Generating LLM insights for {len(care_homes_list)} homes using OpenAI...")
            for home in care_homes_list:
                match_type = home.get('match_type', 'Safe Bet')
                try:
                    # Prepare comprehensive home data for LLM
                    # Merge home data with original home data for full context
                    original_home = home.get('_original_home', {})
                    comprehensive_home_data = {
                        **home,  # Start with formatted home data
                        **original_home,  # Merge original home data (has more fields)
                        # Ensure key fields are present
                        'name': home.get('name'),
                        'rating': home.get('rating'),
                        'weekly_cost': home.get('weekly_cost'),
                        'distance_km': home.get('distance_km'),
                        'care_types': home.get('care_types', []),
                        'fsa_rating': home.get('fsa_rating'),
                        'beds_available': home.get('beds_available'),
                        'cqc_rating_safe': original_home.get('cqc_rating_safe'),
                        'cqc_rating_caring': original_home.get('cqc_rating_caring'),
                        'cqc_rating_effective': original_home.get('cqc_rating_effective'),
                        'cqc_rating_responsive': original_home.get('cqc_rating_responsive'),
                        'cqc_rating_well_led': original_home.get('cqc_rating_well_led'),
                        'google_rating': home.get('google_rating') or original_home.get('google_rating'),
                        'review_count': home.get('review_count') or original_home.get('review_count')
                    }
                    
                    # Call LLM service to generate insight
                    insight = await llm_insights_service.generate_home_insight(
                        home_data=comprehensive_home_data,
                        match_type=match_type,
                        user_context=user_context
                    )
                    
                    llm_insights['insights']['home_insights'].append(insight)
                    print(f"✅ Generated LLM insight for {home.get('name', 'Unknown')} ({match_type})")
                except Exception as insight_error:
                    print(f"⚠️ Error generating LLM insight for {home.get('name', 'Unknown')}: {insight_error}")
                    import traceback
                    traceback.print_exc()
                    # Use fallback function if LLM fails
                    try:
                        insight = generate_home_insight_fallback(home, match_type, budget, care_type, top_3_homes)
                        llm_insights['insights']['home_insights'].append(insight)
                        print(f"✅ Used fallback insight for {home.get('name', 'Unknown')}")
                    except Exception as fallback_error:
                        print(f"⚠️ Fallback insight generation also failed: {fallback_error}")
                        # Add minimal fallback insight
                        llm_insights['insights']['home_insights'].append({
                            'home_name': home.get('name', 'Unknown'),
                            'match_type': match_type,
                            'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                            'key_strengths': ['Selected based on comprehensive data analysis'],
                            'considerations': []
                        })
            print(f"✅ Generated {len(llm_insights['insights']['home_insights'])} insights")
        except Exception as e:
            print(f"⚠️ Error generating LLM insights: {e}")
            import traceback
            traceback.print_exc()
            # If error occurred, generate fallback insights for all homes
            print(f"🔄 Generating fallback insights for all {len(care_homes_list)} homes...")
            llm_insights['insights']['home_insights'] = []  # Clear any partial insights
            for home in care_homes_list:
                match_type = home.get('match_type', 'Safe Bet')
                try:
                    insight = generate_home_insight_fallback(home, match_type, budget, care_type, top_3_homes)
                    llm_insights['insights']['home_insights'].append(insight)
                    print(f"✅ Generated fallback insight for {home.get('name', 'Unknown')}")
                except Exception as fallback_error:
                    print(f"⚠️ Fallback insight generation failed for {home.get('name', 'Unknown')}: {fallback_error}")
                    # Add minimal fallback insight
                    llm_insights['insights']['home_insights'].append({
                        'home_name': home.get('name', 'Unknown'),
                        'match_type': match_type,
                        'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                        'key_strengths': ['Selected based on comprehensive data analysis'],
                        'considerations': []
                    })
            llm_insights['method'] = 'data_driven_analysis'  # Update method to reflect fallback
            print(f"✅ Generated {len(llm_insights['insights']['home_insights'])} fallback insights")
        
        # Ensure llm_insights is always present (fallback if generation failed)
        if 'llm_insights' not in locals() or not llm_insights:
            llm_insights = {
                'generated_at': datetime.now().isoformat(),
                'method': 'data_driven_analysis',
                'insights': {
                    'overall_explanation': {
                        'summary': f"Based on analysis of {len(care_homes)} care homes in your area, we've selected 3 homes that best match your needs.",
                        'key_findings': [
                            f"Found {len(care_homes)} homes matching your criteria",
                            f"All selected homes have been carefully analyzed"
                        ],
                        'confidence_level': 'high'
                    },
                    'home_insights': []
                }
            }
        
        # Generate report
        report_id = str(uuid.uuid4())
        
        # Ensure llm_insights is always present and valid
        if 'llm_insights' not in locals() or not llm_insights:
            llm_insights = {
                'generated_at': datetime.now().isoformat(),
                'method': 'data_driven_analysis',
                'insights': {
                    'overall_explanation': {
                        'summary': f"Based on analysis of {len(care_homes)} care homes in your area, we've selected 3 homes that best match your needs.",
                        'key_findings': [
                            f"Found {len(care_homes)} homes matching your criteria",
                            f"All selected homes have been carefully analyzed"
                        ],
                        'confidence_level': 'high'
                    },
                    'home_insights': []
                }
            }
        
        context.log_step_start(GenerationStep.RESPONSE_ASSEMBLY)
        
        logger.info(f"Returning report with {len(llm_insights.get('insights', {}).get('home_insights', []))} home insights")
        
        response = {
            'questionnaire': request.dict(),
            'care_homes': care_homes_list,
            'fair_cost_gap': fair_cost_gap,  # Use service output directly
            'area_profile': area_profile,
            'area_map': area_map,
            'llm_insights': llm_insights,
            'generated_at': datetime.now().isoformat(),
            'report_id': report_id
        }
        
        context.log_step_complete(GenerationStep.RESPONSE_ASSEMBLY)
        context.log_step_start(GenerationStep.INITIALIZATION)  # Mark final step
        
        # Log generation summary
        summary = context.get_summary()
        logger.info(f"Report generation complete: {json.dumps(summary)}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Free report generation error: {error_detail}")
        # Ensure llm_insights is in error response too
        if 'llm_insights' not in locals():
            llm_insights = {
                'generated_at': datetime.now().isoformat(),
                'method': 'error_fallback',
                'insights': {
                    'overall_explanation': {
                        'summary': 'Error occurred during report generation',
                        'key_findings': [],
                        'confidence_level': 'low'
                    },
                    'home_insights': []
                }
            }
        raise HTTPException(status_code=500, detail=f"Failed to generate free report: {str(e)}")


@router.post("/funding-eligibility")
async def calculate_funding_eligibility(request: Dict[str, Any] = Body(...)):
    """
    Calculate simplified funding eligibility for Free Report
    
    Uses shared FundingOptimizationService (same as Professional Report)
    but returns a simplified response suitable for Free Report display.
    
    Request body:
    {
        "chc_probability": 35.0,  # Optional CHC probability from questionnaire
        "care_type": "residential",  # Optional care type
        "budget": 1200  # Optional weekly budget
    }
    
    Returns:
        Simplified funding eligibility data with CHC, LA, and DPA info
    """
    try:
        chc_probability = request.get('chc_probability', 35.0)
        care_type = request.get('care_type', 'residential')
        budget = request.get('budget', 1200)
        
        # Build minimal questionnaire for FundingOptimizationService
        minimal_questionnaire = {
            'section_2_location_budget': {
                'q7_budget_max': budget
            },
            'section_3_medical_needs': {
                'q8_care_types': [care_type] if care_type else ['residential'],
                'q9_medical_conditions': [],
                'q10_mobility_level': 'needs_assistance',
                'q11_medication_management': 'needs_help',
                'q12_age_range': '75_84'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls'
            },
            'section_5_preferences': {
                'q16_room_preferences': ['single_room']
            }
        }
        
        # Import and use shared FundingOptimizationService
        from services.funding_optimization_service import FundingOptimizationService
        funding_service = FundingOptimizationService()
        
        # Calculate CHC eligibility using shared service
        chc_eligibility = funding_service.calculate_chc_eligibility(minimal_questionnaire)
        
        # Override with provided CHC probability if available
        if chc_probability and chc_probability > 0:
            base_prob = chc_probability / 100.0  # Convert to decimal
        else:
            base_prob = chc_eligibility.get('probability', 0.35)
        
        # Calculate probability ranges
        if base_prob >= 0.75:
            chc_range = '75-90%'
            chc_savings = '£78,000-£130,000/year'
        elif base_prob >= 0.50:
            chc_range = '50-75%'
            chc_savings = '£52,000-£78,000/year'
        elif base_prob >= 0.25:
            chc_range = '25-50%'
            chc_savings = '£26,000-£52,000/year'
        else:
            chc_range = '10-25%'
            chc_savings = '£10,000-£26,000/year'
        
        # LA funding probability (typically 60-80% for most applicants)
        la_prob = min(95, 50 + (base_prob * 100 * 0.4))
        
        # DPA probability (usually high if property owner)
        dpa_prob = 85
        
        return {
            'chc': {
                'probability_range': chc_range,
                'savings_range': chc_savings,
                'explanation': 'NHS Continuing Healthcare covers full care costs if you have a "primary health need"',
                'next_steps': [
                    'Request CHC assessment from local Clinical Commissioning Group',
                    'Gather medical documentation',
                    'Consider professional advocacy support'
                ]
            },
            'la': {
                'probability': f'{int(la_prob)}%',
                'savings_range': '£20,000-£50,000/year',
                'explanation': 'Local Authority funding available if assets below £23,250 threshold',
                'next_steps': [
                    'Complete financial assessment',
                    'Check asset thresholds',
                    'Apply to local council adult social care'
                ]
            },
            'dpa': {
                'probability': f'{dpa_prob}%',
                'cash_flow_relief': '£2,000+/week deferred',
                'explanation': 'Deferred Payment Agreement allows deferring fees against property equity',
                'next_steps': [
                    'Property valuation',
                    'Apply to local authority',
                    'Understand interest rates and terms'
                ]
            },
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Funding eligibility calculation error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate funding eligibility: {str(e)}")
