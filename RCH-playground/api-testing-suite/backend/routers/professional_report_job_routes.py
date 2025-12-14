"""
Professional Report Job Routes for Vercel Serverless Architecture

Provides async job-based endpoints for report generation.
Optimized for Vercel's serverless function time limits.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from services.job_queue_service import JobQueueService, JobStatus

router = APIRouter(prefix="/api/professional-report", tags=["Professional Report Jobs"])


# Global job queue service instance
_job_queue_service: Optional[JobQueueService] = None


def get_job_queue_service() -> JobQueueService:
    """Get or create job queue service instance"""
    global _job_queue_service
    if _job_queue_service is None:
        _job_queue_service = JobQueueService()
    return _job_queue_service


@router.post("/start")
async def start_professional_report(request: Dict[str, Any] = Body(...)):
    """
    Start professional report generation (async job)
    
    Returns job_id immediately (< 5 seconds).
    Use /status/{job_id} to check progress.
    Use /result/{job_id} to get the completed report.
    
    **Optimized for Vercel Serverless:**
    - Fast response (< 5 seconds)
    - Background processing
    - Progress tracking
    """
    try:
        job_service = get_job_queue_service()
        job_id = await job_service.create_job(request)
        
        # Start background processing (don't wait for completion)
        asyncio.create_task(process_report_background(job_id, request))
        
        return {
            'job_id': job_id,
            'status': JobStatus.PENDING.value,
            'message': 'Report generation started. Use /status/{job_id} to check progress.',
            'status_url': f'/api/professional-report/status/{job_id}',
            'result_url': f'/api/professional-report/result/{job_id}'
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start report generation: {str(e)}"
        )


@router.get("/status/{job_id}")
async def get_report_status(job_id: str):
    """
    Get status of report generation job
    
    **Optimized for Vercel Serverless:**
    - Fast response (< 1 second)
    - Edge Function compatible
    """
    try:
        job_service = get_job_queue_service()
        job_status = await job_service.get_job_status(job_id)
        
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            'job_id': job_id,
            'status': job_status.get('status'),
            'progress': job_status.get('progress', 0),
            'message': job_status.get('message', ''),
            'created_at': job_status.get('created_at'),
            'updated_at': job_status.get('updated_at'),
            'error': job_status.get('error')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/result/{job_id}")
async def get_report_result(job_id: str):
    """
    Get completed report result
    
    **Optimized for Vercel Serverless:**
    - Fast response (< 2 seconds)
    - Returns cached result
    """
    try:
        job_service = get_job_queue_service()
        job_status = await job_service.get_job_status(job_id)
        
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        status = job_status.get('status')
        
        if status == JobStatus.PENDING.value or status == JobStatus.PROCESSING.value:
            raise HTTPException(
                status_code=400,
                detail=f"Report not ready yet. Status: {status}. Progress: {job_status.get('progress', 0)}%"
            )
        
        if status == JobStatus.FAILED.value:
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {job_status.get('error', 'Unknown error')}"
            )
        
        if status == JobStatus.COMPLETED.value:
            result = job_status.get('result')
            if not result:
                raise HTTPException(
                    status_code=500,
                    detail="Report completed but result is missing"
                )
            return result
        
        raise HTTPException(
            status_code=500,
            detail=f"Unknown job status: {status}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report result: {str(e)}"
        )


async def process_report_background(job_id: str, questionnaire: Dict[str, Any]):
    """
    Background processing of professional report
    
    This function runs asynchronously and doesn't block the main endpoint.
    It updates job status as it progresses.
    """
    job_service = get_job_queue_service()
    
    try:
        # Update status to processing
        await job_service.update_job_status(job_id, {
            'status': JobStatus.PROCESSING.value,
            'progress': 5,
            'message': 'Loading care homes...'
        })
        
        # Import here to avoid circular dependencies
        from main import generate_professional_report_internal
        
        # Generate report (this is the existing logic, but called internally)
        report = await generate_professional_report_internal(
            questionnaire,
            progress_callback=lambda progress, message: asyncio.create_task(
                job_service.update_job_status(job_id, {
                    'progress': progress,
                    'message': message
                })
            )
        )
        
        # Save result
        await job_service.save_job_result(job_id, report)
        
    except Exception as e:
        import traceback
        error_message = f"{str(e)}\n{traceback.format_exc()}"
        await job_service.save_job_error(job_id, error_message)
        print(f"❌ Background processing failed for job {job_id}: {error_message}")

