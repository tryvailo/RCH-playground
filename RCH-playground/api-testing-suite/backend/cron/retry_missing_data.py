"""
Vercel Cron Job: Retry Missing Data Sources

This cron job runs periodically (every 5 minutes) to retry loading
missing data sources for partial professional reports.

Configure in vercel.json:
{
  "crons": [
    {
      "path": "/api/cron/retry-missing-data",
      "schedule": "*/5 * * * *"
    }
  ]
}
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta
import asyncio

from services.job_queue_service import JobQueueService, JobStatus
from services.report_retry_service import ReportRetryService

router = APIRouter(prefix="/api/cron", tags=["Cron Jobs"])


@router.get("/retry-missing-data")
async def retry_missing_data_cron():
    """
    Cron job to automatically retry missing data sources
    
    This endpoint:
    1. Finds all jobs with status 'partial'
    2. Checks if retry is needed (time elapsed, retry count, etc.)
    3. Retries missing data sources
    4. Updates job status if all sources are loaded
    """
    try:
        job_service = JobQueueService()
        retry_service = ReportRetryService(job_service)
        
        # This is a simplified implementation
        # In production, you'd want to:
        # 1. Scan all jobs in Redis/database
        # 2. Filter for 'partial' status
        # 3. Check timeout (3 hours)
        # 4. Retry missing sources
        
        result = await retry_service.check_and_retry_jobs()
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'result': result,
            'message': 'Cron job executed successfully'
        }
        
    except Exception as e:
        # Don't raise HTTPException in cron jobs - log and return error
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'message': 'Cron job failed'
        }

