"""
Local Retry Scheduler

Provides background task scheduling for retry mechanism when running locally.
Uses asyncio background tasks instead of Vercel Cron.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from services.job_queue_service import JobQueueService, JobStatus
from services.report_retry_service import ReportRetryService

logger = logging.getLogger(__name__)


class LocalRetryScheduler:
    """
    Schedules and manages retry tasks for local development
    
    In production (Vercel), use cron jobs instead.
    """
    
    def __init__(self):
        self.job_service = JobQueueService()
        self.retry_service = ReportRetryService(self.job_service)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._retry_interval = 300  # 5 minutes
    
    async def start(self):
        """Start the retry scheduler"""
        if self._running:
            logger.warning("Retry scheduler is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._retry_loop())
        logger.info("Local retry scheduler started")
    
    async def stop(self):
        """Stop the retry scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Local retry scheduler stopped")
    
    async def _retry_loop(self):
        """Main retry loop - runs every 5 minutes"""
        while self._running:
            try:
                await self._check_and_retry_partial_jobs()
            except Exception as e:
                logger.error(f"Error in retry loop: {e}", exc_info=True)
            
            # Wait 5 minutes before next check
            await asyncio.sleep(self._retry_interval)
    
    async def _check_and_retry_partial_jobs(self):
        """
        Check all partial jobs and retry missing sources
        
        Note: This is a simplified implementation for local development.
        In production with Redis, you'd scan all jobs efficiently.
        """
        try:
            # Get all jobs from in-memory storage (local dev only)
            if hasattr(self.job_service, '_in_memory_storage'):
                jobs = self.job_service._in_memory_storage
                
                for job_id, job_status in jobs.items():
                    if job_status.get('status') == JobStatus.PARTIAL.value:
                        # Check timeout (3 hours)
                        created_at = datetime.fromisoformat(
                            job_status.get('created_at', datetime.now().isoformat())
                        )
                        time_elapsed = (datetime.now() - created_at).total_seconds() / 3600
                        
                        if time_elapsed >= 3:
                            logger.info(f"Job {job_id} exceeded 3-hour timeout, skipping retry")
                            continue
                        
                        # Get questionnaire
                        questionnaire = job_status.get('questionnaire')
                        if not questionnaire:
                            logger.warning(f"Job {job_id} missing questionnaire, skipping retry")
                            continue
                        
                        # Retry missing sources
                        try:
                            result = await self.retry_service.retry_missing_sources(
                                job_id,
                                questionnaire
                            )
                            
                            if result['success_count'] > 0:
                                logger.info(
                                    f"Job {job_id}: Retried {result['success_count']} sources successfully"
                                )
                            
                            # Check if all sources are now loaded
                            missing = await self.retry_service.get_missing_data_sources(job_id)
                            if not missing:
                                # All sources loaded, mark as completed
                                await self.job_service.update_job_status(job_id, {
                                    'status': JobStatus.COMPLETED.value,
                                    'is_partial': False,
                                    'completeness': 100.0,
                                    'message': 'Report generation completed with all data sources'
                                })
                                logger.info(f"Job {job_id}: All sources loaded, marked as completed")
                        
                        except Exception as e:
                            logger.error(f"Error retrying job {job_id}: {e}", exc_info=True)
            
        except Exception as e:
            logger.error(f"Error checking partial jobs: {e}", exc_info=True)
    
    def set_retry_interval(self, seconds: int):
        """Set retry interval in seconds (default: 300 = 5 minutes)"""
        self._retry_interval = seconds
        logger.info(f"Retry interval set to {seconds} seconds")


# Global scheduler instance
_scheduler: Optional[LocalRetryScheduler] = None


def get_scheduler() -> LocalRetryScheduler:
    """Get or create global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = LocalRetryScheduler()
    return _scheduler

