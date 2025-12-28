"""
Free Report Routes
Handles free report generation endpoint

Uses shared utilities:
- utils.price_extractor for price extraction (shared with Professional Report)
- utils.geo for distance calculations
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List, AsyncGenerator
import asyncio
import uuid
import logging
import json
import time as time_module
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


async def _send_progress(progress_callback: Optional[callable], step: str, progress: int, data: Optional[Dict] = None):
    """Helper function to send progress updates"""
    if progress_callback:
        try:
            await progress_callback({
                'step': step,
                'progress': progress,
                'data': data or {},
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.warning(f"Failed to send progress update: {e}")


@router.post("/free-report-stream")
async def generate_free_report_stream(request: FreeReportRequest):
    """
    Generate free report with Server-Sent Events (SSE) for real-time progress
    Streams progress updates as report is being generated
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for report generation progress"""
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'step': 'connected', 'progress': 0, 'message': 'Starting report generation...'})}\n\n"
            
            # Step 1: Initialization (5%)
            yield f"data: {json.dumps({'step': 'initialization', 'progress': 5, 'message': 'Initializing...'})}\n\n"
            
            report_id = str(uuid.uuid4())
            context = GenerationContext(report_id, request.postcode, request.care_type)
            context.log_step_start(GenerationStep.INITIALIZATION)
            
            postcode = request.postcode
            budget = request.budget
            care_type = request.care_type
            chc_probability = request.chc_probability
            location_postcode = request.location_postcode or postcode
            timeline = request.timeline
            medical_conditions = request.medical_conditions
            max_distance_km = request.max_distance_km
            priority_order = request.priority_order
            priority_weights = request.priority_weights
            
            context.log_step_complete(GenerationStep.INITIALIZATION)
            
            # Step 2: Loading homes (10-20%)
            yield f"data: {json.dumps({'step': 'loading_homes', 'progress': 10, 'message': 'Loading care homes from database...'})}\n\n"
            
            from services.async_data_loader import get_async_loader
            loader = get_async_loader()
            user_lat, user_lon = None, None
            local_authority = None
            
            try:
                postcode_info = await loader.resolve_postcode(postcode)
                if postcode_info:
                    local_authority = postcode_info.get('local_authority') or postcode_info.get('localAuthority')
                    user_lat = postcode_info.get('latitude')
                    user_lon = postcode_info.get('longitude')
            except Exception as e:
                logger.warning(f"Postcode resolution failed: {e}")
            
            from services.sqlite_care_homes_service import get_care_homes as get_sqlite_care_homes
            loop = asyncio.get_event_loop()
            care_homes = await loop.run_in_executor(
                None,
                lambda: get_sqlite_care_homes(
                    local_authority=local_authority,
                    care_type=care_type,
                    max_distance_km=30.0,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    limit=50
                )
            )
            
            yield f"data: {json.dumps({'step': 'homes_loaded', 'progress': 20, 'message': f'Loaded {len(care_homes)} care homes', 'count': len(care_homes)})}\n\n"
            
            if not care_homes:
                yield f"data: {json.dumps({'step': 'error', 'progress': 0, 'message': f'No care homes found for {local_authority or postcode}'})}\n\n"
                return
            
            # Step 3: Filtering (25-35%)
            yield f"data: {json.dumps({'step': 'filtering', 'progress': 25, 'message': 'Filtering homes by quality...'})}\n\n"
            
            # Apply filters (simplified - reuse existing logic)
            filtered_homes = [
                h for h in care_homes
                if (h.get('rating') or h.get('overall_rating') or h.get('cqc_rating_overall') or '').lower() in ['good', 'outstanding']
            ]
            
            yield f"data: {json.dumps({'step': 'filtering_price', 'progress': 30, 'message': 'Filtering by budget...'})}\n\n"
            
            if budget > 0:
                budget_max = budget * 1.3
                filtered_homes = [
                    h for h in filtered_homes
                    if extract_weekly_price(h, care_type) <= budget_max
                ]
            
            yield f"data: {json.dumps({'step': 'filtering_location', 'progress': 35, 'message': 'Filtering by location...'})}\n\n"
            
            # Step 4: Matching (40-50%)
            yield f"data: {json.dumps({'step': 'matching', 'progress': 40, 'message': 'Matching homes to your needs...'})}\n\n"
            
            # Use existing matching logic (simplified for streaming)
            # In production, you'd call the actual matching service
            from services.free_report_matching_service import get_free_report_matching_service
            matching_service = get_free_report_matching_service()
            
            matched = matching_service.select_top_3_homes(
                homes=filtered_homes,
                budget=budget,
                care_type=care_type,
                user_lat=user_lat,
                user_lon=user_lon,
                max_distance_km=max_distance_km or 30.0
            )
            
            # Format matched homes (same as main endpoint)
            care_homes_list = []
            match_types = ['safe_bet', 'best_value', 'premium']
            match_type_labels = {'safe_bet': 'Safe Bet', 'best_value': 'Best Value', 'premium': 'Premium'}
            
            for match_key in match_types:
                if matched.get(match_key):
                    home = matched[match_key]
                    match_type = match_type_labels.get(match_key, 'Safe Bet')
                    
                    # Extract weekly cost - ensure it's always a number
                    # Import extract_weekly_price at the top level (already imported)
                    extracted_price = extract_weekly_price(home, care_type)
                    weekly_cost_value = extracted_price if extracted_price and extracted_price > 0 else 0.0
                    
                    # Format home data (same as main endpoint)
                    formatted_home = {
                        'name': home.get('name', 'Unknown'),
                        'address': home.get('address', ''),
                        'postcode': home.get('postcode', ''),
                        'city': home.get('city', ''),
                        'weekly_cost': weekly_cost_value,  # Ensure it's always a number, never None
                        'care_types': home.get('care_types', []),
                        'rating': home.get('rating') or home.get('cqc_rating_overall') or home.get('overall_rating'),
                        'cqc_rating_overall': home.get('cqc_rating_overall') or home.get('rating') or home.get('overall_rating'),
                        'distance_km': home.get('distance_km', 0),
                        'features': home.get('features', []),
                        'contact_phone': home.get('contact_phone'),
                        'website': home.get('website'),
                        'band': 1,  # Default band
                        'photo_url': home.get('photo_url') or home.get('photo'),
                        'fsa_color': home.get('fsa_color'),
                        'fsa_rating': home.get('fsa_rating'),
                        'fsa_rating_key': home.get('fsa_rating_key'),
                        'fsa_rating_date': home.get('fsa_rating_date'),
                        'fsa_health_score': home.get('fsa_health_score'),
                        'google_rating': home.get('google_rating'),
                        'review_count': home.get('review_count'),
                        'match_type': match_type,
                        'enriched_data': home.get('enriched_data', {}),
                        '_original_home': home  # Store original for LLM insights
                    }
                    care_homes_list.append(formatted_home)
            
            yield f"data: {json.dumps({'step': 'matched', 'progress': 50, 'message': f'Selected {len(care_homes_list)} homes', 'homes': [{'name': h.get('name'), 'match_type': h.get('match_type'), 'weekly_cost': h.get('weekly_cost')} for h in care_homes_list]})}\n\n"
            
            # Step 5: Enrichment (55-75%)
            yield f"data: {json.dumps({'step': 'enriching', 'progress': 55, 'message': 'Enriching home data...'})}\n\n"
            
            # Enrich homes with additional data (same as main endpoint)
            if care_homes_list:
                try:
                    from services.enrichment_orchestrator import EnrichmentOrchestrator, EnrichmentConfig
                    
                    orchestrator = EnrichmentOrchestrator()
                    config = EnrichmentConfig(
                        enabled_sources=['fsa', 'google'],
                        parallel_limit=3,
                        timeout_per_source=15,
                        cache_results=True
                    )
                    
                    # Extract homes for enrichment
                    homes_to_enrich = [h.get('_original_home', h) for h in care_homes_list]
                    
                    enriched_results = await orchestrator.enrich_homes_batch(
                        homes_to_enrich,
                        config,
                        context={'questionnaire': {'postcode': postcode, 'care_type': care_type}},
                        progress_callback=None
                    )
                    
                    # Update care_homes_list with enriched data
                    enriched_homes_dict = {}
                    for result in enriched_results:
                        home = result.get('home', {})
                        home_name = home.get('name')
                        if home_name:
                            enriched_homes_dict[home_name] = {
                                'home': home,
                                'enrichments': result.get('enrichments', {})
                            }
                    
                    # Merge enriched data into formatted homes
                    for formatted_home in care_homes_list:
                        home_name = formatted_home.get('name')
                        if home_name and home_name in enriched_homes_dict:
                            enriched_result = enriched_homes_dict[home_name]
                            enriched_home = enriched_result['home']
                            enrichments = enriched_result['enrichments']
                            
                            # Update formatted home with enriched data
                            formatted_home.update({
                                'fsa_rating': enriched_home.get('fsa_rating') or formatted_home.get('fsa_rating'),
                                'fsa_color': enriched_home.get('fsa_color') or formatted_home.get('fsa_color'),
                                'google_rating': enriched_home.get('google_rating') or formatted_home.get('google_rating'),
                                'review_count': enriched_home.get('review_count') or formatted_home.get('review_count'),
                            })
                            
                            # Add enriched_data
                            if 'enriched_data' not in formatted_home:
                                formatted_home['enriched_data'] = {}
                            
                            # Add CQC data
                            cqc_overall = formatted_home.get('rating') or formatted_home.get('cqc_rating_overall')
                            if cqc_overall:
                                formatted_home['enriched_data']['cqc_detailed'] = {
                                    'overall_rating': cqc_overall,
                                    'safe_rating': formatted_home.get('cqc_rating_safe') or cqc_overall,
                                    'caring_rating': formatted_home.get('cqc_rating_caring') or cqc_overall,
                                }
                            
                            # Add FSA data
                            if formatted_home.get('fsa_rating') is not None or formatted_home.get('fsa_color'):
                                formatted_home['enriched_data']['fsa_detailed'] = {
                                    'rating': formatted_home.get('fsa_rating'),
                                    'color': formatted_home.get('fsa_color'),
                                }
                            
                            # Add Google Places data
                            if formatted_home.get('google_rating') is not None:
                                formatted_home['enriched_data']['google_places'] = {
                                    'rating': formatted_home.get('google_rating'),
                                    'review_count': formatted_home.get('review_count'),
                                }
                    
                except Exception as e:
                    logger.warning(f"Enrichment failed in streaming: {e}")
                    # Continue without enrichment
            
            yield f"data: {json.dumps({'step': 'enriching', 'progress': 75, 'message': 'Data enrichment complete'})}\n\n"
            
            # Step 6: LLM Insights (80-90%)
            yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 80, 'message': 'Generating AI insights (parallel)...'})}\n\n"
            
            # LLM insights generation (parallel, with timeout)
            llm_insights = {
                'generated_at': datetime.now().isoformat(),
                'method': 'data_driven_analysis',
                'insights': {
                    'overall_explanation': {
                        'summary': f"Based on analysis of {len(care_homes)} care homes, we've selected 3 homes that best match your needs.",
                        'key_findings': [],
                        'confidence_level': 'high'
                    },
                    'home_insights': []
                }
            }
            
            # Generate insights using parallel LLM calls (same logic as main endpoint)
            # Check if LLM Insights are enabled (same flag as main endpoint)
            ENABLE_DATA_ENRICHMENT = True  # LLM Insights enabled
            
            if ENABLE_DATA_ENRICHMENT:
                try:
                    from services.free_report_llm_insights_service import FreeReportLLMInsightsService
                    # Get OpenAI API key from credentials (same as main endpoint)
                    try:
                        from config_manager import get_credentials
                        creds = get_credentials()
                        openai_api_key = None
                        if creds and hasattr(creds, 'openai') and creds.openai:
                            openai_api_key = getattr(creds.openai, 'api_key', None)
                    except Exception:
                        # Fallback to environment variable
                        import os
                        openai_api_key = os.getenv('OPENAI_API_KEY')
                    
                    llm_insights_service = FreeReportLLMInsightsService(openai_api_key=openai_api_key) if openai_api_key else None
                    logger.info(f"✅ LLM Insights Service initialized (OpenAI key: {'present' if openai_api_key else 'not configured'})")
                except Exception as e:
                    logger.warning(f"Failed to initialize LLM Insights service: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    llm_insights_service = None
            else:
                llm_insights_service = None
            
            if ENABLE_DATA_ENRICHMENT and llm_insights_service and llm_insights_service.client:
                # Prepare user context
                user_context = {
                    'budget': budget,
                    'care_type': care_type,
                    'postcode': postcode,
                    'local_authority': local_authority
                }
                
                # Generate insights in parallel (same comprehensive data as main endpoint)
                async def generate_single_insight(home, match_type):
                    try:
                        original_home = home.get('_original_home', {})
                        # Use same comprehensive data structure as main endpoint
                        comprehensive_home_data = {
                            **home,
                            **original_home,
                            'name': home.get('name'),
                            'rating': home.get('rating'),
                            'weekly_cost': home.get('weekly_cost'),
                            'distance_km': home.get('distance_km'),
                            'care_types': home.get('care_types', []),
                            'fsa_rating': home.get('fsa_rating'),
                            'beds_available': home.get('beds_available'),
                            'cqc_rating_safe': original_home.get('cqc_rating_safe') or home.get('cqc_rating_safe'),
                            'cqc_rating_caring': original_home.get('cqc_rating_caring') or home.get('cqc_rating_caring'),
                            'cqc_rating_effective': original_home.get('cqc_rating_effective') or home.get('cqc_rating_effective'),
                            'cqc_rating_responsive': original_home.get('cqc_rating_responsive') or home.get('cqc_rating_responsive'),
                            'cqc_rating_well_led': original_home.get('cqc_rating_well_led') or home.get('cqc_rating_well_led'),
                            'google_rating': home.get('google_rating') or original_home.get('google_rating'),
                            'review_count': home.get('review_count') or original_home.get('review_count'),
                            'fsa_color': home.get('fsa_color'),
                            'fsa_health_score': home.get('fsa_health_score'),
                            'enriched_data': home.get('enriched_data', {})
                        }
                        insight = await asyncio.wait_for(
                            llm_insights_service.generate_home_insight(
                                home_data=comprehensive_home_data,
                                match_type=match_type,
                                user_context=user_context
                            ),
                            timeout=30.0
                        )
                        return insight
                    except Exception as e:
                        logger.warning(f"Failed to generate LLM insight for {home.get('name')}: {e}")
                        # Fallback will be generated below
                        return None
                
                # Create tasks for parallel execution
                insight_tasks = [
                    generate_single_insight(home, home.get('match_type', 'Safe Bet'))
                    for home in care_homes_list
                ]
                
                # Execute in parallel with progress updates
                try:
                    yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 82, 'message': 'Generating insights for 3 homes in parallel...'})}\n\n"
                    insights_results = await asyncio.wait_for(
                        asyncio.gather(*insight_tasks, return_exceptions=True),
                        timeout=35.0
                    )
                    
                    # Process results
                    for i, result in enumerate(insights_results):
                        if isinstance(result, Exception) or result is None:
                            # Use fallback
                            home = care_homes_list[i] if i < len(care_homes_list) else {}
                            match_type = home.get('match_type', 'Safe Bet')
                            insight = {
                                'home_name': home.get('name', 'Unknown'),
                                'match_type': match_type,
                                'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                                'key_strengths': ['Selected based on comprehensive data analysis'],
                                'considerations': []
                            }
                            llm_insights['insights']['home_insights'].append(insight)
                        else:
                            llm_insights['insights']['home_insights'].append(result)
                    
                    insights_count = len(llm_insights["insights"]["home_insights"])
                    yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 90, 'message': f'Generated {insights_count} insights'})}\n\n"
                except asyncio.TimeoutError:
                    # Fallback for all homes
                    yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 88, 'message': 'LLM timeout - using fallback insights'})}\n\n"
                    for home in care_homes_list:
                        match_type = home.get('match_type', 'Safe Bet')
                        insight = {
                            'home_name': home.get('name', 'Unknown'),
                            'match_type': match_type,
                            'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                            'key_strengths': ['Selected based on comprehensive data analysis'],
                            'considerations': []
                        }
                        llm_insights['insights']['home_insights'].append(insight)
                    yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 90, 'message': 'Fallback insights generated'})}\n\n"
            else:
                # Use fallback insights
                yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 85, 'message': 'Using data-driven insights (LLM not configured)'})}\n\n"
                for home in care_homes_list:
                    match_type = home.get('match_type', 'Safe Bet')
                    insight = {
                        'home_name': home.get('name', 'Unknown'),
                        'match_type': match_type,
                        'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                        'key_strengths': ['Selected based on comprehensive data analysis'],
                        'considerations': []
                    }
                    llm_insights['insights']['home_insights'].append(insight)
                yield f"data: {json.dumps({'step': 'generating_insights', 'progress': 90, 'message': 'Data-driven insights generated'})}\n\n"
            
            # Step 7: Final assembly (95-100%)
            yield f"data: {json.dumps({'step': 'assembling', 'progress': 95, 'message': 'Assembling final report...'})}\n\n"
            
            # Calculate fair cost gap
            fair_cost_gap_service = get_fair_cost_gap_service()
            # Get market price
            market_price = sum(extract_weekly_price(h, care_type) for h in care_homes_list[:3]) / min(3, len(care_homes_list)) if care_homes_list else 1000
            # Get MSIF lower bound
            try:
                import sys
                from pathlib import Path
                # Add src directory to path
                project_root = Path(__file__).parent.parent.parent.parent
                src_path = project_root / "src"  # Fixed: removed extra "RCH-playground"
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                from msif_loader import get_fair_cost_lower_bound
                msif_lower_bound = get_fair_cost_lower_bound(
                    local_authority or 'Birmingham',
                    care_type
                ) or 700  # Fallback to 700 if not found
            except ImportError as e:
                # Handle import errors (missing module, wrong path, etc.)
                logger.warning(f"⚠️ Failed to import msif_loader: {e}. Using fallback MSIF value.")
                msif_lower_bound = 700  # Default fallback
            except Exception as e:
                # Handle other errors (function call failures, etc.)
                logger.warning(f"⚠️ Failed to get MSIF lower bound: {e}. Using fallback MSIF value.")
                import traceback
                logger.debug(traceback.format_exc())
                msif_lower_bound = 700  # Default fallback
            # Calculate gap using correct method
            fair_cost_gap = fair_cost_gap_service.calculate_gap(
                market_price=market_price,
                msif_lower_bound=msif_lower_bound,
                care_type=care_type
            )
            
            # Final response
            response = {
                'questionnaire': request.dict(),
                'care_homes': care_homes_list,
                'fair_cost_gap': fair_cost_gap,
                'area_profile': None,
                'area_map': None,
                'llm_insights': llm_insights,
                'generated_at': datetime.now().isoformat(),
                'report_id': report_id
            }
            
            yield f"data: {json.dumps({'step': 'complete', 'progress': 100, 'message': 'Report generated successfully', 'report': response})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in report generation stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'step': 'error', 'progress': 0, 'message': f'Error generating report: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/free-report", response_model=FreeReportResponse)
async def generate_free_report(request: FreeReportRequest):
    """
    Generate free report from simple questionnaire
    
    Pydantic automatically validates the request.
    Returns report with 3 matched care homes using 50-point matching algorithm
    """
    # Use time_module from global scope
    
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
        # CRITICAL FIX: Add timeout to prevent hanging on slow API
        postcode_resolution_start = time_module.time()
        loader = get_async_loader()
        user_lat, user_lon = None, None
        local_authority = None
        
        try:
            # Try to resolve postcode with timeout (3 seconds max)
            print(f"📥 Resolving postcode: {postcode}")
            try:
                postcode_info = await asyncio.wait_for(
                    loader.resolve_postcode(postcode),
                    timeout=3.0  # 3 second timeout to prevent hanging
                )
                postcode_resolution_time = time_module.time() - postcode_resolution_start
                print(f"   ⏱️  Postcode resolution took {postcode_resolution_time:.3f}s")
                
                if postcode_info:
                    local_authority = postcode_info.get('local_authority') or postcode_info.get('localAuthority')
                    user_lat = postcode_info.get('latitude')
                    user_lon = postcode_info.get('longitude')
                    print(f"✅ Postcode resolved: {postcode} -> LA: {local_authority}, coords: ({user_lat}, {user_lon})")
                else:
                    print(f"⚠️ Postcode resolution returned no data for: {postcode}")
            except asyncio.TimeoutError:
                postcode_resolution_time = time_module.time() - postcode_resolution_start
                print(f"❌ Postcode resolution TIMEOUT after {postcode_resolution_time:.3f}s for {postcode}")
                print(f"   ⚠️  Continuing without postcode resolution (will use fallback)")
                postcode_info = None
        except Exception as e:
            postcode_resolution_time = time_module.time() - postcode_resolution_start
            print(f"⚠️ Postcode resolution failed after {postcode_resolution_time:.3f}s: {e}")
            # Continue without postcode resolution
            postcode_info = None
        
        # Get care homes from SQLite database (only source of truth)
        start_time = time_module.time()
        care_homes = []
        try:
            from services.sqlite_care_homes_service import get_care_homes as get_sqlite_care_homes
            
            # OPTIMIZATION: SQLite queries are fast (<100ms), use executor with timeout
            # to avoid blocking event loop and prevent hanging
            print(f"📥 Loading care homes from SQLite database...")
            print(f"   Parameters: LA={local_authority}, care_type={care_type}, limit=50")
            
            # Use executor with explicit timeout to prevent hanging
            loop = asyncio.get_event_loop()
            try:
                care_homes = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,  # Use default executor
                        lambda: get_sqlite_care_homes(
                            local_authority=local_authority,
                            care_type=care_type,
                            max_distance_km=30.0,  # SQLite will filter by distance and calculate it
                            user_lat=user_lat,
                            user_lon=user_lon,
                            limit=50
                        )
                    ),
                    timeout=5.0  # 5 second timeout for SQLite query
                )
            except asyncio.TimeoutError:
                print(f"❌ SQLite query timed out after 5 seconds!")
                logger.error("SQLite query timeout - database may be locked or slow")
                raise HTTPException(
                    status_code=500,
                    detail="Database query timeout. The database may be busy. Please try again in a moment."
                )
            
            db_load_time = time_module.time() - start_time
            print(f"✅ Loaded {len(care_homes)} care homes from SQLite database in {db_load_time:.3f}s")
            print(f"📊 STEP 1 - Initial load: {len(care_homes)} homes")
            # Log sample of homes for debugging
            if care_homes:
                sample = care_homes[0]
                print(f"   Sample home: {sample.get('name', 'Unknown')} | Rating: {sample.get('rating') or sample.get('cqc_rating_overall', 'N/A')} | Price: {extract_weekly_price(sample, care_type)} | Distance: {sample.get('distance_km', 'N/A')}km")
        except HTTPException:
            raise
        except Exception as e:
            print(f"⚠️ SQLite data load failed: {e}")
            import traceback
            traceback.print_exc()
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
        print(f"\n{'='*80}")
        print(f"📊 STEP 2 - Quality Filter (CQC Good or Outstanding)")
        print(f"{'='*80}")
        print(f"   Input: {len(care_homes)} homes")
        
        # Count homes by rating before filter
        rating_counts = {}
        for h in care_homes:
            rating = (h.get('rating') or h.get('overall_rating') or h.get('cqc_rating_overall') or 'Unknown').lower()
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        print(f"   Rating distribution: {rating_counts}")
        
        filtered_homes = [
            h for h in care_homes
            if (h.get('rating') or h.get('overall_rating') or h.get('cqc_rating_overall') or '').lower() in ['good', 'outstanding']
        ]
        print(f"   Output: {len(filtered_homes)} homes (removed {len(care_homes) - len(filtered_homes)} homes)")
        
        # Filter 2: Budget (remove >£200 above budget)
        # NOTE: In free report, budget is always in weekly format (not monthly)
        print(f"\n📊 STEP 3 - Budget Filter (budget + £200)")
        print(f"   Input: {len(filtered_homes)} homes")
        print(f"   Budget: £{budget}/week")
        
        if budget > 0:
            # Budget is already in weekly format for free report
            budget_weekly = budget
            # FIX #3: Add tolerance parameter (default 30%)
            tolerance_pct = 30  # Can be configured: 30-50%
            budget_max = budget_weekly * (1 + tolerance_pct / 100)
            print(f"   Max price: £{budget_max:.0f}/week (budget + {tolerance_pct}%)")
            
            # Count homes by price before filter
            price_stats = {'with_price': 0, 'no_price': 0, 'within_budget': 0, 'over_budget': 0}
            for h in filtered_homes:
                price = extract_weekly_price(h, care_type)
                if price > 0:
                    price_stats['with_price'] += 1
                    if price <= budget_max:
                        price_stats['within_budget'] += 1
                    else:
                        price_stats['over_budget'] += 1
                else:
                    price_stats['no_price'] += 1
            print(f"   Price stats: {price_stats}")
            
            homes_before_budget_filter = len(filtered_homes)
            filtered_homes = [
                h for h in filtered_homes
                if extract_weekly_price(h, care_type) <= budget_max
            ]
            print(f"   Output: {len(filtered_homes)} homes (removed {homes_before_budget_filter - len(filtered_homes)} homes)")
        else:
            print(f"   No budget filter (budget = 0)")
        
        # Filter 3: Location (max_distance_km or default 30km)
        # OPTIMIZATION: SQLite already calculated distances, so reuse them instead of recalculating
        location_filter_start = time_module.time()
        print(f"\n📊 STEP 4 - Location Filter (max {max_distance_km or 30.0}km)")
        print(f"   Input: {len(filtered_homes)} homes")
        print(f"   User location: ({user_lat}, {user_lon})")
        
        max_distance = max_distance_km if max_distance_km else 30.0
        if user_lat and user_lon:
            location_filtered = []
            homes_with_coords = 0
            homes_without_coords = 0
            homes_too_far = 0
            homes_distance_already_calculated = 0
            for h in filtered_homes:
                # OPTIMIZATION: Use already calculated distance from SQLite if available
                distance = h.get('distance_km')
                if distance is not None and isinstance(distance, (int, float)) and distance >= 0:
                    # Distance already calculated by SQLite - reuse it!
                    homes_distance_already_calculated += 1
                    if distance <= max_distance:
                        location_filtered.append(h)
                    else:
                        homes_too_far += 1
                else:
                    # Distance not calculated - need to calculate it
                    h_lat = h.get('latitude')
                    h_lon = h.get('longitude')
                    if h_lat and h_lon:
                        homes_with_coords += 1
                        try:
                            distance = calculate_distance_km(float(user_lat), float(user_lon), float(h_lat), float(h_lon))
                            h['distance_km'] = distance
                            if distance <= max_distance:
                                location_filtered.append(h)
                            else:
                                homes_too_far += 1
                        except (ValueError, TypeError):
                            # Include homes with invalid coordinates (will be filtered later)
                            location_filtered.append(h)
                    else:
                        homes_without_coords += 1
                        # Include homes without coordinates (will be filtered later)
                        location_filtered.append(h)
            location_filter_time = time_module.time() - location_filter_start
            print(f"   Homes with coordinates: {homes_with_coords}")
            print(f"   Homes without coordinates: {homes_without_coords}")
            print(f"   Homes too far (> {max_distance}km): {homes_too_far}")
            print(f"   ✅ Reused {homes_distance_already_calculated} pre-calculated distances (saved time)")
            print(f"   ⏱️  Location filter took {location_filter_time:.3f}s")
            filtered_homes = location_filtered
            print(f"   Output: {len(filtered_homes)} homes")
        else:
            print(f"   No location filter (no user coordinates)")
        
        print(f"\n{'='*80}")
        print(f"📊 SUMMARY - After all filters: {len(filtered_homes)} homes available for matching")
        print(f"   Homes with prices > 0: {sum(1 for h in filtered_homes if extract_weekly_price(h, care_type) > 0)}")
        print(f"{'='*80}\n")
        
        # OPTIMIZATION: Limit candidates for matching to prevent timeout
        # If we have too many candidates, take top ones by rating/price/distance
        MAX_MATCHING_CANDIDATES = 30  # Limit to 30 homes for matching to prevent timeout
        if len(filtered_homes) > MAX_MATCHING_CANDIDATES:
            print(f"⚠️  Too many candidates ({len(filtered_homes)}) for matching, limiting to top {MAX_MATCHING_CANDIDATES}")
            # Sort by: has price > 0, then by rating, then by distance
            filtered_homes.sort(key=lambda h: (
                extract_weekly_price(h, care_type) <= 0,  # Homes with price first
                h.get('cqc_rating_overall') != 'Outstanding',  # Outstanding first
                h.get('distance_km') or 999999  # Closest first
            ))
            filtered_homes = filtered_homes[:MAX_MATCHING_CANDIDATES]
            print(f"   ✅ Selected top {len(filtered_homes)} candidates for matching")
        
        # Use improved matching algorithm if available
        matching_start = time_module.time()
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
                print(f"   ⏱️  Starting matching at {datetime.now().strftime('%H:%M:%S')}")
                selected_homes_dict = matching_service.select_3_strategic_homes_simple(filtered_homes, matching_inputs)
                matching_time = time_module.time() - matching_start
                print(f"   ✅ Matching completed in {matching_time:.2f}s")
                
                print(f"🔍 select_3_strategic_homes_simple returned: {list(selected_homes_dict.keys())}")
                for key, home in selected_homes_dict.items():
                    if home:
                        home_name = home.get('name', 'Unknown')
                        price = extract_weekly_price(home, care_type)
                        print(f"   {key}: {home_name} - Price: £{price}/week")
                
                # Convert to expected format (list of dicts with 'home' and 'match_type')
                # Map improved matching keys to legacy format
                top_3_homes = []
                if selected_homes_dict.get('safe_bet'):
                    safe_bet = selected_homes_dict['safe_bet']
                    top_3_homes.append({
                        'home': safe_bet,
                        'match_type': 'Safe Bet',
                        'score': safe_bet.get('match_score', 0),
                        'match_reasoning': safe_bet.get('match_reasoning', [])
                    })
                
                # Map 'best_reputation' or 'best_value' to 'Best Value'
                best_value_home = selected_homes_dict.get('best_reputation') or selected_homes_dict.get('best_value')
                if best_value_home:
                    top_3_homes.append({
                        'home': best_value_home,
                        'match_type': 'Best Value',
                        'score': best_value_home.get('match_score', 0),
                        'match_reasoning': best_value_home.get('match_reasoning', [])
                    })
                
                # Map 'smart_value' or 'premium' to 'Premium'
                premium_home = selected_homes_dict.get('smart_value') or selected_homes_dict.get('premium')
                if premium_home:
                    top_3_homes.append({
                        'home': premium_home,
                        'match_type': 'Premium',
                        'score': premium_home.get('match_score', 0),
                        'match_reasoning': premium_home.get('match_reasoning', [])
                    })
                
                print(f"\n{'='*80}")
                print(f"📊 STEP 5 - Improved Matching Algorithm")
                print(f"{'='*80}")
                print(f"   Input: {len(filtered_homes)} filtered homes")
                print(f"   Selected homes dict keys: {list(selected_homes_dict.keys())}")
                print(f"   Selected homes: {len(top_3_homes)}")
                if len(top_3_homes) == 0:
                    print(f"   ⚠️ WARNING: No homes selected by improved matching!")
                    print(f"   Available keys in result: {list(selected_homes_dict.keys())}")
                    for key, value in selected_homes_dict.items():
                        if value:
                            print(f"      {key}: {value.get('name', 'Unknown') if isinstance(value, dict) else 'Present'}")
                        else:
                            print(f"      {key}: None")
                else:
                    for idx, home_dict in enumerate(top_3_homes, 1):
                        home = home_dict.get('home', {})
                        match_type = home_dict.get('match_type', 'Unknown')
                        name = home.get('name', 'Unknown')
                        price = extract_weekly_price(home, care_type)
                        rating = home.get('rating') or home.get('cqc_rating_overall', 'N/A')
                        print(f"   {idx}. {match_type}: {name} | Price: £{price} | Rating: {rating}")
                print(f"{'='*80}\n")
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
            print(f"\n{'='*80}")
            print(f"📊 STEP 5 - Legacy Matching Algorithm")
            print(f"{'='*80}")
            print(f"   Input: {len(filtered_homes)} filtered homes")
            # Simple matching - select top 3 homes (legacy method)
            scored_homes = []
            homes_skipped_no_price = 0
            for home in filtered_homes:
                # Skip homes with zero or missing price
                weekly_price = extract_weekly_price(home, care_type)
                if weekly_price <= 0:
                    homes_skipped_no_price += 1
                    if homes_skipped_no_price <= 5:  # Log first 5 only
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
                # FIX #4: Reweight to 40-40-20 (quality-price-distance)
                balance_score = 0
                
                # Quality score (40 points max)
                quality_score = 40 if cqc_score == 4 else 30 if cqc_score >= 3 else 0
                balance_score += quality_score
                
                # Price score (40 points max)
                price_score = 0
                if budget > 0:
                    price_diff = abs(weekly_price_val - budget)
                    if price_diff < 50:
                        price_score = 40
                    elif price_diff < 100:
                        price_score = 30
                    elif price_diff < 200:
                        price_score = 20
                    else:
                        price_score = 0
                else:
                    price_score = 20  # Default if no budget
                
                # Distance score (20 points max)
                distance_score = 0
                if isinstance(distance_val, (int, float)) and distance_val < 999:
                    if distance_val < 5:
                        distance_score = 20
                    elif distance_val < 10:
                        distance_score = 15
                    elif distance_val < 15:
                        distance_score = 10
                    else:
                        distance_score = 0
                
                balance_score = quality_score + price_score + distance_score
                
                if balance_score > safe_bet_score:
                    safe_bet_score = balance_score
                    safe_bet = home_data
                    print(f"   ✅ New Safe Bet candidate: {home_data.get('name', 'Unknown')} | Balance: {balance_score} (Q:{quality_score} P:{price_score} D:{distance_score})")
        
        # Find Best Value (best price/quality ratio)
        best_value = None
        best_value_score = -1
        print(f"🔍 Legacy method: Searching for Best Value among {len(top_homes)} homes")
        for scored in top_homes:
            home_data = scored['home']
            weekly_price_val = extract_weekly_price(home_data, care_type)
            cqc_score = get_cqc_rating_score(
                home_data.get('cqc_rating_overall') or 
                home_data.get('overall_cqc_rating') or 
                home_data.get('rating') or 
                'Unknown'
            )
            
            # FIX #1: Best Value requires CQC >= 3 (Good or Outstanding)
            if cqc_score >= 3 and weekly_price_val > 0:  # Good/Outstanding AND valid price
                # FIX #1: Add bounds check (50-130% of budget)
                if budget > 0:
                    if weekly_price_val < (budget * 0.5) or weekly_price_val > (budget * 1.3):
                        continue  # Skip homes outside reasonable price range
                
                value_score = calculate_value_score(home_data, weekly_price_val)
                if value_score > best_value_score:
                    best_value_score = value_score
                    best_value = home_data
                    print(f"   ✅ New Best Value candidate: {home_data.get('name', 'Unknown')} | Value: {value_score:.2f} (CQC:{cqc_score} Price:£{weekly_price_val})")
        
        # Find Premium (highest quality, max price for same quality)
        premium = None
        print(f"🔍 Legacy method: Searching for Premium among {len(top_homes)} homes")
        # FIX #2: Collect candidates first, then select max price
        outstanding_candidates = []
        good_candidates = []
        
        for scored in top_homes:
            home_data = scored['home']
            weekly_price_val = extract_weekly_price(home_data, care_type)
            cqc_score = get_cqc_rating_score(
                home_data.get('cqc_rating_overall') or 
                home_data.get('overall_cqc_rating') or 
                home_data.get('rating') or 
                'Unknown'
            )
            
            if weekly_price_val > 0:  # Must have valid price
                if cqc_score == 4:  # Outstanding
                    outstanding_candidates.append((home_data, weekly_price_val))
                elif cqc_score == 3:  # Good
                    good_candidates.append((home_data, weekly_price_val))
        
        # FIX #2: Select max price from candidates
        if outstanding_candidates:
            premium = max(outstanding_candidates, key=lambda x: x[1])[0]  # Max price
            print(f"   ✅ Premium selected (Outstanding): {premium.get('name', 'Unknown')} | Price: £{extract_weekly_price(premium, care_type)}")
        elif good_candidates:
            premium = max(good_candidates, key=lambda x: x[1])[0]  # Max price
            print(f"   ✅ Premium selected (Good): {premium.get('name', 'Unknown')} | Price: £{extract_weekly_price(premium, care_type)}")
        
        # Build top_3_homes list from selected homes
        top_3_homes = []
        if safe_bet:
            top_3_homes.append({
                'home': safe_bet,
                'match_type': 'Safe Bet',
                'score': safe_bet_score
            })
        if best_value:
            top_3_homes.append({
                'home': best_value,
                'match_type': 'Best Value',
                'score': best_value_score
            })
        if premium:
            top_3_homes.append({
                'home': premium,
                'match_type': 'Premium',
                'score': get_cqc_rating_score(premium.get('rating') or premium.get('cqc_rating_overall') or 'Unknown')
            })
        
        # Ensure we have exactly 3 homes (fill with top scored if needed)
        while len(top_3_homes) < 3 and len(scored_homes) > len(top_3_homes):
            # Find next best home that's not already selected
            for scored in scored_homes:
                home_data = scored['home']
                home_name = home_data.get('name')
                # Check if this home is already in top_3_homes
                already_selected = any(
                    h['home'].get('name') == home_name 
                    for h in top_3_homes
                )
                if not already_selected:
                    match_type = 'Recommended' if len(top_3_homes) == 0 else ('Alternative' if len(top_3_homes) == 1 else 'Additional')
                    top_3_homes.append({
                        'home': home_data,
                        'match_type': match_type,
                        'score': scored['score']
                    })
                    break
        
        print(f"\n{'='*80}")
        print(f"📊 FINAL SELECTION - Top 3 Homes")
        print(f"{'='*80}")
        for idx, home_dict in enumerate(top_3_homes, 1):
            home = home_dict.get('home', {})
            match_type = home_dict.get('match_type', 'Unknown')
            name = home.get('name', 'Unknown')
            price = extract_weekly_price(home, care_type)
            rating = home.get('rating') or home.get('cqc_rating_overall', 'N/A')
            distance = home.get('distance_km', 'N/A')
            print(f"   {idx}. {match_type}: {name} | Price: £{price}/week | Rating: {rating} | Distance: {distance}km")
        print(f"{'='*80}\n")
        
        context.log_step_complete(GenerationStep.MATCHING)
        
        # ============================================================================
        # STEP 6: Enrich selected homes with additional data (CQC, FSA, Google Places)
        # ============================================================================
        print(f"\n{'='*80}")
        print(f"📊 STEP 6 - Data Enrichment")
        print(f"{'='*80}")
        print(f"   Enriching {len(top_3_homes)} selected homes with additional data...")
        
        # Extract homes from top_3_homes for enrichment
        homes_to_enrich = [home_dict.get('home', {}) for home_dict in top_3_homes if home_dict.get('home')]
        
        if homes_to_enrich:
            try:
                from services.enrichment_orchestrator import EnrichmentOrchestrator, EnrichmentConfig
                
                print(f"   Starting enrichment for {len(homes_to_enrich)} homes...")
                enrichment_start = time_module.time()
                
                # Initialize enrichment orchestrator
                orchestrator = EnrichmentOrchestrator()
                
                # Configure enrichment - enable CQC, FSA, Google Places
                # Disable Financial and Staff for free report (performance)
                config = EnrichmentConfig(
                    enabled_sources=['fsa', 'google'],  # CQC data already in SQLite, so focus on FSA and Google
                    parallel_limit=3,  # Enrich 3 homes in parallel
                    timeout_per_source=15,  # 15 seconds per source
                    cache_results=True  # Use cache for performance
                )
                
                # Enrich homes using orchestrator (makes real API calls)
                enriched_results = await orchestrator.enrich_homes_batch(
                    homes_to_enrich,
                    config,
                    context={'questionnaire': {'postcode': postcode, 'care_type': care_type}},
                    progress_callback=None
                )
                
                enrichment_time = time_module.time() - enrichment_start
                print(f"   ✅ Enrichment completed in {enrichment_time:.2f}s")
                
                # Update homes in top_3_homes with enriched data
                # enriched_results is a list of dicts with 'home' and 'enrichments' keys
                enriched_homes_dict = {}
                for result in enriched_results:
                    home = result.get('home', {})
                    home_name = home.get('name')
                    enrichments = result.get('enrichments', {})
                    
                    if home_name:
                        enriched_homes_dict[home_name] = {
                            'home': home,
                            'enrichments': enrichments
                        }
                
                # Merge enriched data into original homes
                for home_dict in top_3_homes:
                    home = home_dict.get('home', {})
                    home_name = home.get('name')
                    if home_name and home_name in enriched_homes_dict:
                        enriched_result = enriched_homes_dict[home_name]
                        enriched_home = enriched_result['home']
                        enrichments = enriched_result['enrichments']
                        
                        # Merge enriched home data
                        home.update(enriched_home)
                        
                        # Add enrichments to enriched_data
                        # Note: FSA and Google services add data directly to home, but we also create enriched_data structure
                        if 'enriched_data' not in home:
                            home['enriched_data'] = {}
                        
                        # Add CQC data to enriched_data (CQC data comes from SQLite, extract from home)
                        cqc_overall = home.get('rating') or home.get('cqc_rating_overall') or home.get('overall_rating')
                        cqc_safe = home.get('cqc_rating_safe')
                        cqc_effective = home.get('cqc_rating_effective')
                        cqc_caring = home.get('cqc_rating_caring')
                        cqc_responsive = home.get('cqc_rating_responsive')
                        cqc_well_led = home.get('cqc_rating_well_led')
                        cqc_trend = home.get('cqc_trend')
                        safeguarding = home.get('safeguarding_incidents')
                        
                        # Add CQC detailed data if we have at least one rating
                        if cqc_overall or cqc_safe or cqc_effective or cqc_caring or cqc_responsive or cqc_well_led:
                            home['enriched_data']['cqc_detailed'] = {
                                'overall_rating': cqc_overall,
                                'safe_rating': cqc_safe or cqc_overall,
                                'effective_rating': cqc_effective or cqc_overall,
                                'caring_rating': cqc_caring or cqc_overall,
                                'responsive_rating': cqc_responsive or cqc_overall,
                                'well_led_rating': cqc_well_led or cqc_overall,
                                'trend': cqc_trend,
                                'safeguarding_incidents': safeguarding
                            }
                            # Also ensure cqc_rating_overall is set for backward compatibility
                            if not home.get('cqc_rating_overall') and cqc_overall:
                                home['cqc_rating_overall'] = cqc_overall
                        
                        # Add FSA data to enriched_data (FSA service adds it directly to home, so we extract from there)
                        if home.get('fsa_rating') is not None or home.get('fsa_color'):
                            home['enriched_data']['fsa_detailed'] = {
                                'rating': home.get('fsa_rating'),
                                'rating_key': home.get('fsa_rating_key'),
                                'rating_date': home.get('fsa_rating_date'),
                                'color': home.get('fsa_color'),
                                'health_score': home.get('fsa_health_score'),
                                'breakdown_scores': home.get('fsa_breakdown'),
                                'fhrs_id': home.get('fsa_fhrs_id')
                            }
                            # Also check if enrichments has FSA data (might be in different format)
                            if enrichments.get('fsa') and isinstance(enrichments['fsa'], dict) and enrichments['fsa']:
                                fsa_data = enrichments['fsa']
                                # Merge enrichments data if available
                                if fsa_data.get('rating_value'):
                                    home['enriched_data']['fsa_detailed']['rating'] = fsa_data.get('rating_value')
                                if fsa_data.get('color'):
                                    home['enriched_data']['fsa_detailed']['color'] = fsa_data.get('color')
                        
                        # Add Google Places data to enriched_data
                        if home.get('google_rating') is not None or home.get('review_count'):
                            home['enriched_data']['google_places'] = {
                                'rating': home.get('google_rating'),
                                'review_count': home.get('review_count'),
                                'place_id': home.get('google_place_id'),
                                'address': home.get('google_formatted_address')
                            }
                            # Also check if enrichments has Google data
                            if enrichments.get('google') and isinstance(enrichments['google'], dict) and enrichments['google']:
                                google_data = enrichments['google']
                                if google_data.get('rating'):
                                    home['enriched_data']['google_places']['rating'] = google_data.get('rating')
                                if google_data.get('review_count'):
                                    home['enriched_data']['google_places']['review_count'] = google_data.get('review_count')
                
                # Log enrichment results
                for home_dict in top_3_homes:
                    home = home_dict.get('home', {})
                    home_name = home.get('name', 'Unknown')
                    enriched_data = home.get('enriched_data', {})
                    sources = list(enriched_data.keys()) if enriched_data else []
                    fsa_rating = home.get('fsa_rating')
                    google_rating = home.get('google_rating')
                    print(f"   {home_name}: enriched with {len(sources)} sources - {sources}")
                    if fsa_rating:
                        print(f"      FSA Rating: {fsa_rating}")
                    if google_rating:
                        print(f"      Google Rating: {google_rating}")
                
            except Exception as e:
                print(f"⚠️ Enrichment failed: {e}")
                import traceback
                traceback.print_exc()
                # Continue without enrichment - homes will still be returned
                print(f"   ⚠️ Continuing without enrichment data")
        else:
            print(f"   ⚠️ No homes to enrich")
        
        print(f"{'='*80}\n")
        
        # Format matched homes for response
        care_homes_list = []
        for home_dict in top_3_homes:
            home = home_dict.get('home', {})
            match_type = home_dict.get('match_type', 'Safe Bet')
            
            # Calculate distance if not present
            distance_km = calculate_distance_if_needed(home, user_lat, user_lon)
            if distance_km is not None:
                home['distance_km'] = distance_km
            
            # Format home data
            # Extract weekly cost - ensure it's never None (use 0 as fallback)
            extracted_price = extract_weekly_price(home, care_type)
            weekly_cost_value = extracted_price if extracted_price and extracted_price > 0 else 0.0
            
            # Extract CQC rating (ensure it's set correctly)
            cqc_overall_rating = (
                home.get('cqc_rating_overall') or 
                home.get('rating') or 
                home.get('overall_rating') or
                (home.get('enriched_data', {}).get('cqc_detailed', {}).get('overall_rating'))
            )
            
            formatted_home = {
                'name': home.get('name', 'Unknown'),
                'address': home.get('address', ''),
                'postcode': home.get('postcode', ''),
                'city': home.get('city', ''),
                'weekly_cost': weekly_cost_value,  # Ensure it's always a number, never None
                'care_types': home.get('care_types', []),
                'rating': cqc_overall_rating,  # CQC Overall rating
                'cqc_rating_overall': cqc_overall_rating,  # Explicitly set for consistency
                'cqc_rating_safe': home.get('cqc_rating_safe') or (home.get('enriched_data', {}).get('cqc_detailed', {}).get('safe_rating')),
                'cqc_rating_effective': home.get('cqc_rating_effective') or (home.get('enriched_data', {}).get('cqc_detailed', {}).get('effective_rating')),
                'cqc_rating_caring': home.get('cqc_rating_caring') or (home.get('enriched_data', {}).get('cqc_detailed', {}).get('caring_rating')),
                'cqc_rating_responsive': home.get('cqc_rating_responsive') or (home.get('enriched_data', {}).get('cqc_detailed', {}).get('responsive_rating')),
                'cqc_rating_well_led': home.get('cqc_rating_well_led') or (home.get('enriched_data', {}).get('cqc_detailed', {}).get('well_led_rating')),
                'distance_km': home.get('distance_km') or distance_km or 0,
                'features': home.get('features', []),
                'contact_phone': home.get('contact_phone'),
                'website': home.get('website'),
                'band': home_dict.get('band', 1),
                'photo_url': home.get('photo_url') or home.get('photo'),
                'fsa_color': home.get('fsa_color'),
                'fsa_rating': home.get('fsa_rating'),
                'fsa_rating_key': home.get('fsa_rating_key'),
                'fsa_rating_date': home.get('fsa_rating_date'),
                'fsa_health_score': home.get('fsa_health_score'),
                'google_rating': home.get('google_rating'),
                'review_count': home.get('review_count'),
                'match_type': match_type,
                'enriched_data': home.get('enriched_data', {}),  # Include enriched data in response
                '_original_home': home  # Store original for LLM insights
            }
            
            # Debug logging if price is 0 but we expected it
            if weekly_cost_value == 0:
                print(f"⚠️ Warning: Home '{home.get('name')}' has weekly_cost = 0. Original data keys: {list(home.keys())[:10]}")
            care_homes_list.append(formatted_home)
        
        # Calculate Fair Cost Gap
        context.log_step_start(GenerationStep.GAP_CALCULATION)
        
        fair_cost_gap_service = get_fair_cost_gap_service()
        try:
            # Calculate average market price from selected homes
            market_price = 0
            if care_homes_list:
                prices = [h['weekly_cost'] for h in care_homes_list if h['weekly_cost'] > 0]
                if prices:
                    market_price = sum(prices) / len(prices)
                else:
                    market_price = budget or 1000  # Fallback
            
            # Get MSIF lower bound
            try:
                import sys
                from pathlib import Path
                # Add src directory to path
                project_root = Path(__file__).parent.parent.parent.parent
                src_path = project_root / "src"  # Fixed: removed extra "RCH-playground"
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                from msif_loader import get_fair_cost_lower_bound
                msif_lower_bound = get_fair_cost_lower_bound(
                    local_authority or 'Birmingham',
                    care_type
                ) or 700  # Fallback to 700 if not found
            except ImportError as e:
                # Handle import errors (missing module, wrong path, etc.)
                logger.warning(f"⚠️ Failed to import msif_loader: {e}. Using fallback MSIF value.")
                msif_lower_bound = 700  # Default fallback
            except Exception as e:
                # Handle other errors (function call failures, etc.)
                logger.warning(f"⚠️ Failed to get MSIF lower bound: {e}. Using fallback MSIF value.")
                import traceback
                logger.debug(traceback.format_exc())
                msif_lower_bound = 700  # Default fallback
            # Calculate gap using correct method
            fair_cost_gap = fair_cost_gap_service.calculate_gap(
                market_price=market_price,
                msif_lower_bound=msif_lower_bound,
                care_type=care_type
            )
            context.log_step_complete(
                GenerationStep.GAP_CALCULATION,
                {"gap_week": fair_cost_gap.get("gap_week")}
            )
        except Exception as e:
            print(f"⚠️ Fair cost gap calculation failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback fair cost gap
            fair_cost_gap = {
                'gap_week': 0,
                'gap_year': 0,
                'gap_5year': 0,
                'market_price': market_price if 'market_price' in locals() else (budget or 1000),
                'msif_lower_bound': 700,
                'local_authority': local_authority or 'Birmingham',
                'care_type': care_type,
                'explanation': 'Fair cost gap calculation unavailable',
                'gap_text': 'Unable to calculate',
                'recommendations': [],
                'gap_percent': 0
            }
        
        # Generate Area Profile (optional)
        area_profile = None
        try:
            # Calculate basic area profile from loaded homes
            if care_homes:
                total_homes = len(care_homes)
                prices_with_data = [extract_weekly_price(h, care_type) for h in care_homes if extract_weekly_price(h, care_type) > 0]
                avg_weekly_cost = sum(prices_with_data) / len(prices_with_data) if prices_with_data else 0
                
                # Count CQC ratings
                cqc_distribution = {
                    'outstanding': sum(1 for h in care_homes if (h.get('rating') or h.get('cqc_rating_overall') or '').lower() == 'outstanding'),
                    'good': sum(1 for h in care_homes if (h.get('rating') or h.get('cqc_rating_overall') or '').lower() == 'good'),
                    'requires_improvement': sum(1 for h in care_homes if (h.get('rating') or h.get('cqc_rating_overall') or '').lower() == 'requires improvement'),
                    'inadequate': sum(1 for h in care_homes if (h.get('rating') or h.get('cqc_rating_overall') or '').lower() == 'inadequate')
                }
                
                area_profile = {
                    'area_name': local_authority or postcode,
                    'total_homes': total_homes,
                    'average_weekly_cost': avg_weekly_cost,
                    'cost_vs_national': 0,  # Would need national average data
                    'cqc_distribution': cqc_distribution,
                    'wellbeing_index': None,
                    'demographics': None
                }
        except Exception as e:
            print(f"⚠️ Area profile generation failed: {e}")
            area_profile = None
        
        # Generate Area Map (optional)
        area_map = None
        try:
            if user_lat and user_lon:
                area_map = {
                    'user_location': {
                        'lat': float(user_lat),
                        'lng': float(user_lon),
                        'postcode': postcode
                    },
                    'homes': [
                        {
                            'id': str(i),
                            'name': h.get('name', 'Unknown'),
                            'lat': float(h.get('latitude', 0)),
                            'lng': float(h.get('longitude', 0)),
                            'distance_km': h.get('distance_km', 0),
                            'match_type': h.get('match_type', 'Recommended')
                        }
                        for i, h in enumerate(care_homes_list)
                        if h.get('latitude') and h.get('longitude')
                    ],
                    'amenities': []
                }
        except Exception as e:
            print(f"⚠️ Area map generation failed: {e}")
            area_map = None
        
        # ============================================================================
        # Data Enrichment (LLM Insights) - ENABLED
        # ============================================================================
        # LLM Insights generation for selected homes
        # Note: This can take 30-35 seconds, but provides valuable insights
        ENABLE_DATA_ENRICHMENT = True  # LLM Insights enabled
        
        if ENABLE_DATA_ENRICHMENT:
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
        else:
            print("⏭️  Data enrichment (LLM Insights) is TEMPORARILY DISABLED - skipping enrichment step")
            llm_insights_service = None
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
                        f"Fair Cost Gap analysis shows market prices exceed MSIF fair cost by {fair_cost_gap.get('gap_percent', 0)}%"
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
                # Add FSA warning for poor food hygiene rating (FSA <= 3)
                if fsa_rating is not None:
                    try:
                        fsa_int = int(fsa_rating) if isinstance(fsa_rating, (int, float, str)) else None
                        if fsa_int is not None and fsa_int <= 3:
                            insight['considerations'].append("⚠️ This home has a food hygiene rating that requires improvement. See detailed safety analysis in Professional Report.")
                    except (ValueError, TypeError):
                        pass
            
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
                # Add FSA warning for poor food hygiene rating (FSA <= 3)
                if fsa_rating is not None:
                    try:
                        fsa_int = int(fsa_rating) if isinstance(fsa_rating, (int, float, str)) else None
                        if fsa_int is not None and fsa_int <= 3:
                            insight['considerations'].append("⚠️ This home has a food hygiene rating that requires improvement. See detailed safety analysis in Professional Report.")
                    except (ValueError, TypeError):
                        pass
            
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
                    strength_parts.append(f"Excellent community reputation ({google_rating:.1f}/5 from {int(review_count)} reviews)")
                
                # FSA
                if fsa_rating and fsa_rating >= 4:
                    strength_parts.append(f"Excellent food hygiene standards ({fsa_rating}/5)")
                
                insight['why_selected'] = f"{name} was selected as Premium because it " + ", ".join(why_parts) + ", representing the highest quality option available."
                insight['key_strengths'] = strength_parts
                
                # Considerations
                if budget > 0 and weekly_cost > budget:
                    insight['considerations'].append(f"Premium pricing - £{abs(budget_diff)} above your budget, but offers exceptional quality")
                if not beds_available or beds_available == 0:
                    insight['considerations'].append("Check availability - premium homes often have waiting lists")
                # Add FSA warning for poor food hygiene rating (FSA <= 3)
                if fsa_rating is not None:
                    try:
                        fsa_int = int(fsa_rating) if isinstance(fsa_rating, (int, float, str)) else None
                        if fsa_int is not None and fsa_int <= 3:
                            insight['considerations'].append("⚠️ This home has a food hygiene rating that requires improvement. See detailed safety analysis in Professional Report.")
                    except (ValueError, TypeError):
                        pass
            
            return insight
        
        # Generate insight for each home using OpenAI LLM (PARALLEL execution)
        # Generate LLM Insights for selected homes (if enabled and service available)
        if ENABLE_DATA_ENRICHMENT and llm_insights_service and llm_insights_service.client:
            try:
                print(f"🔍 Generating LLM insights for {len(care_homes_list)} homes using OpenAI (parallel)...")
                
                # Prepare all home data for parallel LLM calls
                async def generate_single_insight(home, match_type):
                    """Generate insight for a single home with fallback and timeout"""
                    try:
                        original_home = home.get('_original_home', {})
                        comprehensive_home_data = {
                            **home,
                            **original_home,
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
                        
                        # Add timeout to each LLM call (30 seconds max per home)
                        insight = await asyncio.wait_for(
                            llm_insights_service.generate_home_insight(
                                home_data=comprehensive_home_data,
                                match_type=match_type,
                                user_context=user_context
                            ),
                            timeout=30.0  # 30 seconds max per home
                        )
                        print(f"✅ Generated LLM insight for {home.get('name', 'Unknown')} ({match_type})")
                        return insight
                    except (asyncio.TimeoutError, Exception) as insight_error:
                        error_type = 'timeout' if isinstance(insight_error, asyncio.TimeoutError) else 'error'
                        print(f"⚠️ LLM insight {error_type} for {home.get('name', 'Unknown')}: {insight_error}")
                        try:
                            insight = generate_home_insight_fallback(home, match_type, budget, care_type, top_3_homes)
                            print(f"✅ Used fallback insight for {home.get('name', 'Unknown')}")
                            return insight
                        except Exception:
                            return {
                                'home_name': home.get('name', 'Unknown'),
                                'match_type': match_type,
                                'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                                'key_strengths': ['Selected based on comprehensive data analysis'],
                                'considerations': []
                            }
                
                # Create tasks for parallel execution
                insight_tasks = [
                    generate_single_insight(home, home.get('match_type', 'Safe Bet'))
                    for home in care_homes_list
                ]
                
                # Execute all LLM calls in parallel with overall timeout (35 seconds for all 3)
                # This ensures we don't wait forever if one call hangs
                try:
                    insights_results = await asyncio.wait_for(
                        asyncio.gather(*insight_tasks, return_exceptions=True),
                        timeout=35.0  # 35 seconds total for all 3 parallel calls
                    )
                except asyncio.TimeoutError:
                    print(f"⏱️ Overall LLM insights timeout - generating fallback insights")
                    # If timeout, generate fallback for all homes
                    insights_results = []
                    for home in care_homes_list:
                        match_type = home.get('match_type', 'Safe Bet')
                        try:
                            insight = generate_home_insight_fallback(home, match_type, budget, care_type, top_3_homes)
                            insights_results.append(insight)
                        except Exception:
                            insights_results.append({
                                'home_name': home.get('name', 'Unknown'),
                                'match_type': match_type,
                                'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                                'key_strengths': ['Selected based on comprehensive data analysis'],
                                'considerations': []
                            })
                
                # Process results
                for i, result in enumerate(insights_results):
                    if isinstance(result, Exception):
                        home = care_homes_list[i] if i < len(care_homes_list) else {}
                        llm_insights['insights']['home_insights'].append({
                            'home_name': home.get('name', 'Unknown'),
                            'match_type': home.get('match_type', 'Unknown'),
                            'why_selected': f"{home.get('name', 'Unknown')} was selected based on quality, location, and pricing analysis.",
                            'key_strengths': ['Selected based on comprehensive data analysis'],
                            'considerations': []
                        })
                    else:
                        llm_insights['insights']['home_insights'].append(result)
                
                print(f"✅ Generated {len(llm_insights['insights']['home_insights'])} insights (parallel execution)")
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
        else:
            # Enrichment disabled - use minimal fallback insights
            print(f"⏭️  Skipping LLM enrichment - using minimal fallback insights")
            llm_insights['insights']['home_insights'] = []
            for home in care_homes_list:
                match_type = home.get('match_type', 'Safe Bet')
                llm_insights['insights']['home_insights'].append({
                    'home_name': home.get('name', 'Unknown'),
                    'match_type': match_type,
                    'why_selected': f"{home.get('name', 'Unknown')} was selected as {match_type} based on quality, location, and pricing analysis.",
                    'key_strengths': ['Selected based on comprehensive data analysis'],
                    'considerations': []
                })
            llm_insights['method'] = 'data_driven_analysis'
            print(f"✅ Generated {len(llm_insights['insights']['home_insights'])} minimal fallback insights (enrichment disabled)")
        
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
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)
        import traceback
        full_traceback = traceback.format_exc()
        
        # Log detailed error information
        logger.error(f"❌ Free report generation error: {error_type}: {error_detail}")
        logger.error(f"Full traceback:\n{full_traceback}")
        
        # Print to console for immediate visibility
        print(f"❌ ERROR TYPE: {error_type}")
        print(f"❌ ERROR MESSAGE: {error_detail}")
        print(f"❌ FULL TRACEBACK:\n{full_traceback}")
        
        # Ensure llm_insights is in error response too
        if 'llm_insights' not in locals():
            llm_insights = {
                'generated_at': datetime.now().isoformat(),
                'method': 'data_driven_analysis',
                'insights': {
                    'overall_explanation': {
                        'summary': 'Report generation encountered an error',
                        'key_findings': [],
                        'confidence_level': 'low'
                    },
                    'home_insights': []
                }
            }
        
        # Provide more helpful error message
        error_message = f"Failed to generate free report: {error_detail}"
        if error_type == "ModuleNotFoundError":
            error_message += " (Missing required module. Check backend dependencies.)"
        elif error_type == "ImportError":
            error_message += " (Import error. Check module paths and dependencies.)"
        elif error_type == "FileNotFoundError":
            error_message += " (File not found. Check database and data files.)"
        
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/free-report/funding-eligibility")
async def calculate_funding_eligibility_simplified(request: FreeReportRequest):
    """
    Calculate simplified funding eligibility for Free Report
    This is a simplified version of the professional report funding eligibility
    but returns a simplified response suitable for Free Report display.
    """
    # Simplified funding eligibility calculation
    chc_prob = request.chc_probability or 35
    
    # CHC probability range
    if chc_prob >= 75:
        chc_range = '75-90%'
        chc_savings = '£78,000-£130,000/year'
    elif chc_prob >= 50:
        chc_range = '50-75%'
        chc_savings = '£52,000-£78,000/year'
    elif chc_prob >= 25:
        chc_range = '25-50%'
        chc_savings = '£26,000-£52,000/year'
    else:
        chc_range = '10-25%'
        chc_savings = '£10,000-£26,000/year'
    
    # LA probability
    la_prob = min(95, 50 + (chc_prob * 0.4))
    
    return {
        'chc': {
            'probability_range': chc_range,
            'savings_range': chc_savings,
        },
        'la': {
            'probability': f'{int(la_prob)}%',
            'savings_range': '£20,000-£50,000/year',
        },
        'dpa': {
            'probability': '85%',
            'cash_flow_relief': '£2,000+/week deferred',
        }
    }
