"""
Neighbourhood Analysis API Routes
Unified endpoints combining all data sources
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging

from data_integrations.batch_processor import BatchProcessor, NeighbourhoodAnalyzer
from data_integrations.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/neighbourhood", tags=["Neighbourhood Analysis"])


# Request/Response Models
class CareHomeInput(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    postcode: str = Field(..., description="UK postcode")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BatchRequest(BaseModel):
    care_homes: List[CareHomeInput] = Field(..., max_items=100)
    include_os_places: bool = True
    include_ons: bool = True
    include_osm: bool = True
    include_nhsbsa: bool = True


class BatchJobResponse(BaseModel):
    job_id: str
    status: str
    total_homes: int
    message: str


# In-memory job storage (would use Redis in production)
_batch_jobs = {}


@router.get("/status")
async def get_neighbourhood_status():
    """Check Neighbourhood Analysis integration status"""
    cache = get_cache_manager()
    stats = cache.get_stats()
    
    return {
        "service": "Neighbourhood Analysis",
        "status": "available",
        "description": "Unified neighbourhood analysis combining OS Places, ONS, OSM, and NHSBSA",
        "cache": {
            "total_entries": stats.get('total_entries', 0),
            "size_mb": stats.get('db_size_mb', 0)
        },
        "endpoints": {
            "analyze": "/api/neighbourhood/analyze/{postcode}",
            "batch": "/api/neighbourhood/batch",
            "batch_status": "/api/neighbourhood/batch/{job_id}",
            "compare": "/api/neighbourhood/compare"
        },
        "data_sources": [
            "OS Places (coordinates, UPRN)",
            "ONS (wellbeing, economics, demographics)",
            "OpenStreetMap (walk score, amenities)",
            "NHSBSA (health profile, GP access)"
        ]
    }


@router.get("/analyze/{postcode}")
async def analyze_neighbourhood(
    postcode: str,
    include_os_places: bool = Query(default=True, description="Include OS Places data"),
    include_ons: bool = Query(default=True, description="Include ONS data"),
    include_osm: bool = Query(default=True, description="Include OpenStreetMap data"),
    include_nhsbsa: bool = Query(default=True, description="Include NHSBSA data"),
    include_environmental: bool = Query(default=False, description="Include Environmental data (noise only)"),
    lat: Optional[float] = Query(default=None, description="Optional: Latitude (if provided, skips postcode resolution)"),
    lon: Optional[float] = Query(default=None, description="Optional: Longitude (if provided, skips postcode resolution)"),
    address_name: Optional[str] = Query(default=None, description="Optional: Address name (e.g., care home name) for OS Places when using coordinates")
):
    """
    Comprehensive neighbourhood analysis for a postcode
    
    Combines data from selected sources:
    - Social wellbeing and demographics (ONS) - requires postcode
    - Walkability and amenities (OpenStreetMap) - requires coordinates (lat/lon)
    - Health profile and GP access (NHSBSA) - requires coordinates (lat/lon)
    - Coordinates and address data (OS Places) - requires postcode, provides coordinates
    
    **Input Requirements:**
    - **Postcode**: Required for all sources. UK postcode format (e.g., "CV34 5EH")
    - **Coordinates (lat/lon)**: Optional. If provided, skips postcode-to-coordinates resolution.
      Required for OSM and NHSBSA analysis. If not provided, system will attempt to resolve
      from OS Places or ONS data.
    
    **Data Source Dependencies:**
    - **OSM (OpenStreetMap)**: Requires coordinates. If coordinates not available, will attempt
      to resolve from OS Places or ONS. If resolution fails, OSM analysis will be skipped.
    - **NHSBSA**: Requires coordinates for proximity matching. If coordinates not available,
      will attempt to resolve from OS Places or ONS. If resolution fails, NHSBSA analysis will be skipped.
    - **OS Places**: Requires postcode. Can provide coordinates for other sources.
    - **ONS**: Requires postcode. May provide coordinates for other sources.
    
    Use query parameters to select which data sources to include.
    Returns overall neighbourhood score (0-100) with breakdown.
    """
    try:
        analyzer = NeighbourhoodAnalyzer()
        result = await analyzer.analyze(
            postcode=postcode,
            lat=lat,
            lon=lon,
            include_os_places=include_os_places,
            include_ons=include_ons,
            include_osm=include_osm,
            include_nhsbsa=include_nhsbsa,
            include_environmental=include_environmental,
            address_name=address_name
        )
        
        if result.get('error'):
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing neighbourhood for {postcode}: {e}", exc_info=True)
        # Return partial result with error instead of raising 500
        # This allows frontend to display what data was successfully retrieved
        try:
            # Try to get partial results if possible
            analyzer = NeighbourhoodAnalyzer()
            partial_result = await analyzer.analyze(
                postcode=postcode,
                lat=lat,
                lon=lon,
                include_os_places=include_os_places,
                include_ons=include_ons,
                include_osm=include_osm,
                include_nhsbsa=include_nhsbsa,
                include_environmental=False,  # Disable environmental to avoid recursive error
                address_name=address_name
            )
            partial_result['errors'] = partial_result.get('errors', {})
            partial_result['errors']['general'] = f"Analysis partially failed: {str(e)}"
            return partial_result
        except:
            # If even partial analysis fails, return minimal error response
            raise HTTPException(status_code=500, detail=f"Failed to analyze neighbourhood: {str(e)}")


@router.post("/batch", response_model=BatchJobResponse)
async def start_batch_analysis(
    request: BatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start batch analysis for multiple care homes
    
    Processes up to 100 care homes asynchronously.
    Returns job_id to check progress.
    """
    import uuid
    job_id = str(uuid.uuid4())[:8]
    
    # Initialize job
    _batch_jobs[job_id] = {
        'status': 'running',
        'total': len(request.care_homes),
        'completed': 0,
        'failed': 0,
        'started_at': datetime.now().isoformat(),
        'results': None
    }
    
    # Start background processing
    background_tasks.add_task(
        _run_batch_job,
        job_id,
        [h.dict() for h in request.care_homes],
        request.include_os_places,
        request.include_ons,
        request.include_osm,
        request.include_nhsbsa
    )
    
    return BatchJobResponse(
        job_id=job_id,
        status="running",
        total_homes=len(request.care_homes),
        message=f"Batch job started. Check progress at /api/neighbourhood/batch/{job_id}"
    )


async def _run_batch_job(
    job_id: str,
    care_homes: List[dict],
    include_os_places: bool,
    include_ons: bool,
    include_osm: bool,
    include_nhsbsa: bool
):
    """Run batch processing job"""
    try:
        processor = BatchProcessor(max_concurrent=5, chunk_size=20)
        
        def progress_callback(progress):
            if job_id in _batch_jobs:
                _batch_jobs[job_id]['completed'] = progress.completed
                _batch_jobs[job_id]['failed'] = progress.failed
        
        processor.set_progress_callback(progress_callback)
        
        results = await processor.process_care_homes(
            care_homes,
            include_os_places=include_os_places,
            include_ons=include_ons,
            include_osm=include_osm,
            include_nhsbsa=include_nhsbsa
        )
        
        _batch_jobs[job_id]['status'] = 'completed'
        _batch_jobs[job_id]['results'] = results
        _batch_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        _batch_jobs[job_id]['status'] = 'failed'
        _batch_jobs[job_id]['error'] = str(e)


@router.get("/batch/{job_id}")
async def get_batch_status(job_id: str):
    """
    Get batch job status and results
    
    Returns progress while running, full results when complete.
    """
    if job_id not in _batch_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = _batch_jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'total': job['total'],
        'completed': job['completed'],
        'failed': job['failed'],
        'progress_percent': round((job['completed'] / job['total']) * 100, 1) if job['total'] > 0 else 0,
        'started_at': job['started_at']
    }
    
    if job['status'] == 'completed':
        response['completed_at'] = job.get('completed_at')
        response['results'] = job.get('results')
    elif job['status'] == 'failed':
        response['error'] = job.get('error')
    
    return response


@router.post("/compare")
async def compare_neighbourhoods(postcodes: List[str] = Query(..., max_length=10)):
    """
    Compare neighbourhoods for multiple postcodes
    
    Useful for comparing potential care home locations.
    Returns side-by-side comparison with rankings.
    """
    if len(postcodes) < 2:
        raise HTTPException(status_code=400, detail="At least 2 postcodes required for comparison")
    
    if len(postcodes) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 postcodes for comparison")
    
    analyzer = NeighbourhoodAnalyzer()
    
    # Analyze all postcodes
    analyses = []
    for postcode in postcodes:
        try:
            result = await analyzer.analyze(postcode)
            analyses.append({
                'postcode': postcode,
                'analysis': result,
                'success': True
            })
        except Exception as e:
            analyses.append({
                'postcode': postcode,
                'error': str(e),
                'success': False
            })
    
    # Rank by overall score
    successful = [a for a in analyses if a['success']]
    successful.sort(
        key=lambda x: x['analysis'].get('overall', {}).get('score', 0),
        reverse=True
    )
    
    # Assign rankings
    for i, item in enumerate(successful):
        item['rank'] = i + 1
    
    return {
        'comparison_count': len(postcodes),
        'successful_analyses': len(successful),
        'rankings': [
            {
                'rank': item['rank'],
                'postcode': item['postcode'],
                'overall_score': item['analysis'].get('overall', {}).get('score'),
                'overall_rating': item['analysis'].get('overall', {}).get('rating'),
                'walk_score': item['analysis'].get('walkability', {}).get('score'),
                'health_index': item['analysis'].get('health', {}).get('index', {}).get('score'),
                'wellbeing_score': item['analysis'].get('social', {}).get('wellbeing', {}).get('score')
            }
            for item in successful
        ],
        'detailed_analyses': analyses,
        'recommendation': _generate_recommendation(successful)
    }


def _generate_recommendation(analyses: List[dict]) -> str:
    """Generate comparison recommendation"""
    if not analyses:
        return "Unable to analyze any of the provided postcodes"
    
    if len(analyses) == 1:
        return f"Only {analyses[0]['postcode']} could be analyzed"
    
    top = analyses[0]
    score = top['analysis'].get('overall', {}).get('score', 0)
    postcode = top['postcode']
    
    if score >= 70:
        return f"{postcode} ranks highest with an excellent neighbourhood score of {score}"
    elif score >= 55:
        return f"{postcode} ranks highest with a good neighbourhood score of {score}"
    else:
        return f"{postcode} ranks highest but consider all options carefully (score: {score})"


@router.get("/enrich")
async def enrich_care_home(
    postcode: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    name: Optional[str] = None
):
    """
    Enrich a single care home with neighbourhood data
    
    Quick endpoint for adding neighbourhood context to a care home.
    """
    processor = BatchProcessor()
    
    home = {
        'postcode': postcode,
        'name': name or postcode
    }
    if lat and lon:
        home['latitude'] = lat
        home['longitude'] = lon
    
    result = await processor.enrich_care_home(home)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Enrichment failed'))
    
    return result


@router.get("/summary/{postcode}")
async def get_neighbourhood_summary(postcode: str):
    """
    Get condensed neighbourhood summary
    
    Returns key metrics without full detail - good for cards/lists.
    """
    analyzer = NeighbourhoodAnalyzer()
    
    try:
        full = await analyzer.analyze(postcode)
        
        return {
            'postcode': postcode,
            'overall_score': full.get('overall', {}).get('score'),
            'overall_rating': full.get('overall', {}).get('rating'),
            'walk_score': full.get('walkability', {}).get('score'),
            'walk_rating': full.get('walkability', {}).get('rating'),
            'health_score': full.get('health', {}).get('index', {}).get('score'),
            'health_rating': full.get('health', {}).get('index', {}).get('rating'),
            'wellbeing_score': full.get('social', {}).get('wellbeing', {}).get('score'),
            'local_authority': full.get('social', {}).get('geography', {}).get('local_authority'),
            'gp_practices_nearby': full.get('health', {}).get('practices_nearby', 0),
            'key_considerations': [
                c.get('category') 
                for c in full.get('health', {}).get('care_home_considerations', [])
                if c.get('priority') == 'high'
            ][:3]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_all_cache():
    """Clear all neighbourhood analysis cache"""
    cache = get_cache_manager()
    
    cleared = {
        'os_places': cache.clear_source('os_places'),
        'ons': cache.clear_source('ons'),
        'osm': cache.clear_source('osm'),
        'nhsbsa': cache.clear_source('nhsbsa'),
        'neighbourhood': cache.clear_source('neighbourhood')
    }
    
    total = sum(cleared.values())
    
    return {
        "message": f"Cleared {total} cached entries",
        "by_source": cleared
    }
