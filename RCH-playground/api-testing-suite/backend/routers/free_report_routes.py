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
from datetime import datetime

from utils.price_extractor import extract_weekly_price, extract_price_range
from utils.geo import calculate_distance_km, validate_coordinates

router = APIRouter(prefix="/api", tags=["Free Report"])


@router.post("/free-report")
async def generate_free_report(request: Dict[str, Any] = Body(...)):
    """
    Generate free report from simple questionnaire
    
    Accepts basic questionnaire with postcode, budget, care_type
    Returns report with 3 matched care homes using 50-point matching algorithm
    """
    try:
        # Extract questionnaire data
        postcode = request.get('postcode', '')
        budget = request.get('budget', 0.0)
        care_type = request.get('care_type', 'residential')
        chc_probability = request.get('chc_probability', 0.0)
        
        if not postcode:
            raise HTTPException(status_code=400, detail="postcode is required")
        
        # Import services
        from services.async_data_loader import get_async_loader
        from services.database_service import DatabaseService
        from services.mock_care_homes import filter_mock_care_homes
        
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
        
        # Get care homes
        care_homes = []
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
        except Exception as e:
            print(f"⚠️ Database query failed, using mock data: {e}")
        
        # If no homes from database, try mock data
        if not care_homes:
            try:
                loop = asyncio.get_event_loop()
                care_homes = await loop.run_in_executor(
                    None,
                    lambda: filter_mock_care_homes(
                        local_authority=local_authority,
                        care_type=care_type,
                        max_distance_km=30.0,
                        user_lat=user_lat,
                        user_lon=user_lon
                    )
                )
                
                if not care_homes:
                    from services.mock_care_homes import load_mock_care_homes
                    all_homes = await loop.run_in_executor(None, load_mock_care_homes)
                    if care_type:
                        care_homes = [
                            h for h in all_homes
                            if care_type.lower() in [ct.lower() for ct in h.get('care_types', [])]
                        ]
                    else:
                        care_homes = all_homes
                    care_homes = care_homes[:50]
            except Exception as mock_error:
                print(f"⚠️ Mock data also failed: {mock_error}")
                care_homes = []
        
        if not care_homes:
            raise HTTPException(
                status_code=404,
                detail=f"No care homes found for {local_authority or postcode}. Please try a different location."
            )
        
        # Helper function to calculate distance if not already present
        def calculate_distance_if_needed(home: Dict[str, Any], user_lat: Optional[float], user_lon: Optional[float]) -> Optional[float]:
            """Calculate distance using shared geo utility if not already present"""
            # If distance already calculated, use it
            distance = home.get('distance_km') or home.get('distance')
            if distance and isinstance(distance, (int, float)) and distance > 0:
                return float(distance)
            
            # Calculate if we have valid coordinates
            if user_lat and user_lon:
                home_lat = home.get('latitude')
                home_lon = home.get('longitude')
                if home_lat and home_lon:
                    try:
                        if validate_coordinates(float(home_lat), float(home_lon)):
                            return calculate_distance_km(user_lat, user_lon, float(home_lat), float(home_lon))
                    except (ValueError, TypeError):
                        pass
            return None
        
        # Simple matching - select top 3 homes
        # For now, use simple scoring based on CQC rating and distance
        scored_homes = []
        for home in care_homes:
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
            
            # Extract weekly price using helper
            weekly_price = extract_weekly_price(home, care_type)
            
            # Add points for budget match
            if budget > 0 and weekly_price > 0:
                price_diff = abs(weekly_price - budget)
                if price_diff < 50:
                    score += 20
                elif price_diff < 100:
                    score += 15
                elif price_diff < 200:
                    score += 10
            
            # Calculate distance if needed
            distance_km = calculate_distance_if_needed(home, user_lat, user_lon)
            if distance_km:
                home['distance_km'] = distance_km
            elif user_lat and user_lon:
                # Debug: check if home has coordinates
                home_lat = home.get('latitude')
                home_lon = home.get('longitude')
                if not (home_lat and home_lon):
                    print(f"⚠️ Home {home.get('name', 'Unknown')} missing coordinates: lat={home_lat}, lon={home_lon}")
            
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
            if cqc_score >= 3:  # Good or Outstanding
                # Balance score: quality + price fit + distance
                balance_score = cqc_score * 10
                if budget > 0 and weekly_price_val > 0:
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
        
        # Find Best Value (best price/quality ratio)
        best_value = None
        best_value_score = -1
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
        
        # Find Premium (highest quality)
        premium = None
        premium_score = -1
        for scored in top_homes:
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
            
            # Premium: Outstanding rating preferred, or highest quality available
            if cqc_score >= 3:  # Good or Outstanding
                premium_candidate_score = cqc_score * 10
                if cqc_score == 4:  # Outstanding
                    premium_candidate_score += 10
                if weekly_price_val > 0:
                    # Don't penalize high price for premium
                    premium_candidate_score += 2
                
                if premium_candidate_score > premium_score:
                    premium_score = premium_candidate_score
                    premium = scored
        
        # Fallback: if we don't have 3 different homes, use top scored ones
        selected_homes = []
        if safe_bet:
            safe_bet['match_type'] = 'Safe Bet'
            selected_homes.append(safe_bet)
        if best_value:
            best_value['match_type'] = 'Best Value'
            selected_homes.append(best_value)
        if premium:
            premium['match_type'] = 'Premium'
            selected_homes.append(premium)
        
        # If we have less than 3, fill with top scored homes
        remaining_slots = 3 - len(selected_homes)
        if remaining_slots > 0:
            for scored in top_homes:
                if scored not in selected_homes:
                    if not scored.get('match_type'):
                        # Assign based on position
                        if len(selected_homes) == 0:
                            scored['match_type'] = 'Safe Bet'
                        elif len(selected_homes) == 1:
                            scored['match_type'] = 'Best Value'
                        else:
                            scored['match_type'] = 'Premium'
                    selected_homes.append(scored)
                    remaining_slots -= 1
                    if remaining_slots == 0:
                        break
        
        # Ensure we have exactly 3 homes
        top_3_homes = selected_homes[:3]
        
        # Format homes for response
        care_homes_list = []
        for scored in top_3_homes:
            home = scored['home']
            
            # Extract weekly price
            weekly_price = extract_weekly_price(home, care_type)
            
            # Get distance
            distance_km = home.get('distance_km') or home.get('distance')
            if distance_km is None:
                distance_km = calculate_distance_if_needed(home, user_lat, user_lon)
            
            # If still no distance, try to calculate from postcode if we have user coordinates
            if distance_km is None and user_lat and user_lon:
                # Try to get home coordinates from postcode if available
                home_postcode = home.get('postcode')
                if home_postcode:
                    try:
                        home_postcode_info = await loader.resolve_postcode(home_postcode)
                        if home_postcode_info:
                            home_lat = home_postcode_info.get('latitude')
                            home_lon = home_postcode_info.get('longitude')
                            if home_lat and home_lon:
                                if validate_coordinates(float(home_lat), float(home_lon)):
                                    distance_km = calculate_distance_km(user_lat, user_lon, float(home_lat), float(home_lon))
                    except (ValueError, TypeError):
                        pass  # Ignore errors in postcode resolution for distance
            
            # Final fallback: use a default distance if still None (e.g., 5km for same city)
            if distance_km is None:
                # Try to get user city from postcode_info (already resolved earlier)
                user_city = None
                try:
                    if 'postcode_info' in locals() and postcode_info:
                        user_city = postcode_info.get('city')
                except:
                    pass
                home_city = home.get('city')
                if user_city and home_city and user_city.lower() == home_city.lower():
                    distance_km = 5.0  # Same city, estimate 5km
                else:
                    distance_km = 10.0  # Different city, estimate 10km
            
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
            
            # If still no FSA rating, try FSA API (simplified lookup)
            if not fsa_rating:
                home_name = home.get('name', '')
                if home_name:
                    try:
                        from api_clients.fsa_client import FSAAPIClient
                        fsa_client = FSAAPIClient()
                        
                        # Search by business name (simplified - first match)
                        establishments = await fsa_client.search_by_business_name(home_name)
                        
                        if establishments and len(establishments) > 0:
                            # Take first match
                            fsa_establishment = establishments[0]
                            rating_value = fsa_establishment.get('RatingValue')
                            
                            if rating_value is not None:
                                # Convert string rating to int (handle "5", "4", etc.)
                                try:
                                    if isinstance(rating_value, str):
                                        if rating_value.isdigit():
                                            fsa_rating = int(rating_value)
                                        elif rating_value.lower() == 'pass':
                                            fsa_rating = 5  # Scotland uses Pass/Fail
                                    else:
                                        fsa_rating = int(rating_value)
                                    
                                    fsa_rating_date = fsa_establishment.get('RatingDate')
                                    print(f"✅ FSA API: {home_name} -> Rating {fsa_rating}")
                                except (ValueError, TypeError):
                                    pass
                        
                        await fsa_client.close()
                    except Exception as fsa_error:
                        print(f"⚠️ FSA API lookup failed for {home_name}: {fsa_error}")
            
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
                'distance_km': round(distance_km, 2) if distance_km else None,
                'care_types': home.get('care_types', []),
                'photo_url': (
                    home.get('photo') or 
                    home.get('photo_url') or 
                    home.get('image_url') or
                    # Use Unsplash placeholder if no photo available
                    f"https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop&q=80"
                ),
                'location_id': home.get('cqc_location_id') or home.get('location_id'),
                # Match type (strategy)
                'match_type': match_type,
                # FSA Rating fields
                'fsa_rating': float(fsa_rating) if fsa_rating else None,
                'fsa_color': fsa_color,
                'fsa_rating_date': fsa_rating_date,
                'fsa_rating_key': home.get('fsa_rating_key') or (f'fhrs_{int(fsa_rating)}_en-gb' if fsa_rating else None),
            })
        
        # Calculate area profile statistics
        # REUSES: ons_loader for demographics and wellbeing data
        area_profile = None
        area_map = None
        
        try:
            # Count total homes in area
            total_homes_in_area = len(care_homes)
            
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
            
            # Build area map data
            # Use default Birmingham coordinates if postcode resolution failed
            map_user_lat = user_lat or 52.4862  # Birmingham default
            map_user_lon = user_lon or -1.8904
            
            map_homes = []
            for idx, scored in enumerate(top_3_homes):
                home = scored['home']
                home_lat = home.get('latitude')
                home_lon = home.get('longitude')
                distance_km = home.get('distance_km') or 5.0
                
                if home_lat and home_lon:
                    map_homes.append({
                        'id': home.get('cqc_location_id') or home.get('location_id') or str(uuid.uuid4()),
                        'name': home.get('name', 'Unknown'),
                        'lat': float(home_lat),
                        'lng': float(home_lon),
                        'distance_km': round(distance_km, 2),
                        'match_type': scored.get('match_type', 'Safe Bet')
                    })
                else:
                    # Approximate coordinates if not available (spread around user location)
                    offset_lat = (idx - 1) * 0.015  # Spread vertically
                    offset_lon = (idx % 2) * 0.02 - 0.01  # Spread horizontally
                    map_homes.append({
                        'id': home.get('cqc_location_id') or home.get('location_id') or str(uuid.uuid4()),
                        'name': home.get('name', 'Unknown'),
                        'lat': map_user_lat + offset_lat,
                        'lng': map_user_lon + offset_lon,
                        'distance_km': round(distance_km, 2),
                        'match_type': scored.get('match_type', 'Safe Bet')
                    })
            
            area_map = {
                'user_location': {
                    'lat': map_user_lat,
                    'lng': map_user_lon,
                    'postcode': postcode
                },
                'homes': map_homes,
                'amenities': []  # TODO: Add nearby amenities from OpenStreetMap
            }
        except Exception as area_error:
            print(f"⚠️ Area profile generation failed: {area_error}")
            # Continue without area profile
        
        # Get MSIF fair cost
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
            print(f"⚠️ MSIF lookup failed: {e}")
            default_msif = {
                'residential': 700,
                'nursing': 1048,
                'residential_dementia': 800,
                'nursing_dementia': 1048
            }
            msif_lower_bound = float(default_msif.get(care_type, 700))
        
        # Calculate fair cost gap
        # Use average weekly cost from homes if budget not provided, otherwise use budget
        if budget > 0:
            market_price = float(budget)
        elif care_homes_list:
            # Calculate average from top 3 homes
            avg_price = sum(h.get('weekly_cost', 0) for h in care_homes_list) / len(care_homes_list)
            market_price = avg_price if avg_price > 0 else 1200.0
        else:
            market_price = 1200.0
        
        gap_week = max(0.0, market_price - msif_lower_bound)
        gap_year = gap_week * 52
        gap_5year = gap_year * 5
        gap_percent = (gap_week / msif_lower_bound * 100) if msif_lower_bound > 0 else 0.0
        
        # Generate report
        report_id = str(uuid.uuid4())
        
        return {
            'questionnaire': request,
            'care_homes': care_homes_list,
            'fair_cost_gap': {
                'gap_week': round(gap_week, 2),
                'gap_year': round(gap_year, 2),
                'gap_5year': round(gap_5year, 2),
                'gap_percent': round(gap_percent, 2),
                'market_price': round(market_price, 2),
                'msif_lower_bound': round(msif_lower_bound, 2),
                'local_authority': local_authority or 'Unknown',
                'care_type': care_type,
                'gap_text': f"Переплата £{round(gap_year, 0):,.0f} в год = £{round(gap_5year, 0):,.0f} за 5 лет",
                'explanation': f"Market price of £{round(market_price, 0):,.0f}/week exceeds MSIF fair cost of £{round(msif_lower_bound, 0):,.0f}/week by {round(gap_percent, 1)}%",
                'recommendations': [
                    'Use MSIF data to negotiate lower fees',
                    'Consider homes in adjacent local authorities',
                    'Request detailed cost breakdown',
                    'Explore long-term commitment discounts'
                ]
            },
            'area_profile': area_profile,
            'area_map': area_map,
            'generated_at': datetime.now().isoformat(),
            'report_id': report_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Free report generation error: {error_detail}")
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
