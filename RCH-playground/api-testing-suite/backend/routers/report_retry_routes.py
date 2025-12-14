"""
Report Retry Routes

Endpoints for retrying missing data sources in professional reports.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from services.job_queue_service import JobQueueService, JobStatus
from services.report_retry_service import ReportRetryService, MissingDataSource

router = APIRouter(prefix="/api/professional-report", tags=["Professional Report Retry"])


# Global service instances
_job_queue_service: Optional[JobQueueService] = None
_retry_service: Optional[ReportRetryService] = None


def get_services():
    """Get or create service instances"""
    global _job_queue_service, _retry_service
    if _job_queue_service is None:
        _job_queue_service = JobQueueService()
    if _retry_service is None:
        _retry_service = ReportRetryService(_job_queue_service)
    return _job_queue_service, _retry_service


@router.post("/retry/{job_id}")
async def retry_missing_data(job_id: str):
    """
    Manually trigger retry for missing data sources in a report
    
    This endpoint allows manual retry of missing data sources.
    The system will also automatically retry periodically.
    """
    try:
        job_service, retry_service = get_services()
        
        # Get job status
        job_status = await job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if job is in a state that allows retry
        status = job_status.get('status')
        if status not in [JobStatus.PARTIAL.value, JobStatus.COMPLETED.value]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot retry job in status: {status}. Job must be 'partial' or 'completed'."
            )
        
        # Check timeout (3 hours)
        created_at = datetime.fromisoformat(job_status.get('created_at', datetime.now().isoformat()))
        time_elapsed = (datetime.now() - created_at).total_seconds() / 3600  # hours
        
        if time_elapsed >= 3:
            raise HTTPException(
                status_code=400,
                detail="Retry timeout exceeded (3 hours). Report generation has expired."
            )
        
        # Get questionnaire
        questionnaire = job_status.get('questionnaire')
        if not questionnaire:
            raise HTTPException(
                status_code=400,
                detail="Questionnaire not found in job. Cannot retry without original questionnaire."
            )
        
        # Retry missing sources
        result = await retry_service.retry_missing_sources(job_id, questionnaire)
        
        # Update job status
        if result['success_count'] > 0:
            # Some sources were successfully loaded
            await job_service.update_job_status(job_id, {
                'message': f"Retry completed: {result['success_count']} sources loaded successfully",
                'last_retry_at': datetime.now().isoformat()
            })
        
        return {
            'job_id': job_id,
            'retry_result': result,
            'time_elapsed_hours': time_elapsed,
            'time_remaining_hours': 3 - time_elapsed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry missing data: {str(e)}"
        )


@router.get("/missing-sources/{job_id}")
async def get_missing_sources(job_id: str):
    """
    Get list of missing data sources for a job
    """
    try:
        job_service, retry_service = get_services()
        
        # Get job status
        job_status = await job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get missing sources
        missing_sources = await retry_service.get_missing_data_sources(job_id)
        
        # Calculate retry info
        missing_dicts = [s.to_dict() for s in missing_sources]
        
        # Group by source type
        by_type = {}
        for source in missing_dicts:
            source_type = source['source_type']
            if source_type not in by_type:
                by_type[source_type] = []
            by_type[source_type].append(source)
        
        return {
            'job_id': job_id,
            'missing_sources': missing_dicts,
            'missing_by_type': by_type,
            'total_missing': len(missing_dicts),
            'is_partial': job_status.get('is_partial', False),
            'completeness': job_status.get('completeness', 100.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get missing sources: {str(e)}"
        )


@router.get("/retry-status/{job_id}")
async def get_retry_status(job_id: str):
    """
    Get retry status and next retry time for a job
    """
    try:
        job_service, retry_service = get_services()
        
        # Get job status
        job_status = await job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get missing sources
        missing_sources = await retry_service.get_missing_data_sources(job_id)
        
        # Calculate next retry times
        now = datetime.now()
        next_retries = []
        
        for source in missing_sources:
            if source.last_attempt:
                retry_delay = retry_service.RETRY_DELAY_SECONDS * (
                    retry_service.RETRY_BACKOFF_MULTIPLIER ** source.retry_count
                )
                next_retry = source.last_attempt + timedelta(seconds=retry_delay)
                time_until_retry = (next_retry - now).total_seconds()
                
                next_retries.append({
                    'source_type': source.source_type,
                    'home_name': source.home_name,
                    'next_retry_at': next_retry.isoformat(),
                    'time_until_retry_seconds': max(0, time_until_retry),
                    'retry_count': source.retry_count,
                    'max_retries': retry_service.MAX_RETRY_ATTEMPTS
                })
        
        # Check timeout
        created_at = datetime.fromisoformat(job_status.get('created_at', datetime.now().isoformat()))
        time_elapsed = (datetime.now() - created_at).total_seconds() / 3600
        time_remaining = 3 - time_elapsed
        
        return {
            'job_id': job_id,
            'is_partial': job_status.get('is_partial', False),
            'completeness': job_status.get('completeness', 100.0),
            'missing_sources_count': len(missing_sources),
            'next_retries': next_retries,
            'time_elapsed_hours': time_elapsed,
            'time_remaining_hours': max(0, time_remaining),
            'will_auto_retry': time_remaining > 0 and len(missing_sources) > 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get retry status: {str(e)}"
        )

