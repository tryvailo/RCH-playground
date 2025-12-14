"""
Job Queue Service for Vercel Serverless Architecture

Provides async job processing for professional report generation.
Optimized for Vercel's serverless function limitations.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import os

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available, using in-memory storage (not recommended for production)")


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"  # Report generated but some data sources missing
    FAILED = "failed"


class JobQueueService:
    """
    Job Queue Service for async report processing
    
    Uses Redis (Vercel KV) for job storage in production,
    falls back to in-memory storage for development.
    """
    
    def __init__(self):
        self.redis_client = None
        self._in_memory_storage = {}  # Fallback for development
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            redis_url = os.getenv('KV_REDIS_URL') or os.getenv('REDIS_URL')
            if redis_url:
                try:
                    self.redis_client = redis.from_url(redis_url)
                except Exception as e:
                    print(f"⚠️ Failed to connect to Redis: {e}")
                    print("   Using in-memory storage (not recommended for production)")
    
    async def create_job(self, questionnaire: Dict[str, Any]) -> str:
        """
        Create a new job for report generation
        Returns job_id immediately (< 1 second)
        """
        job_id = str(uuid.uuid4())
        
        job_status = {
            'job_id': job_id,
            'status': JobStatus.PENDING.value,
            'progress': 0,
            'questionnaire': questionnaire,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'result': None,
            'error': None,
            'message': 'Job created, processing will start shortly...'
        }
        
        await self._save_job_status(job_id, job_status)
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a job
        Fast operation (< 1 second)
        """
        return await self._get_job_status(job_id)
    
    async def update_job_status(
        self,
        job_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update job status
        """
        current_status = await self._get_job_status(job_id)
        if not current_status:
            return False
        
        current_status.update(updates)
        current_status['updated_at'] = datetime.now().isoformat()
        
        await self._save_job_status(job_id, current_status)
        return True
    
    async def save_job_result(
        self,
        job_id: str,
        result: Dict[str, Any],
        is_partial: bool = False,
        missing_sources: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Save completed job result
        
        Args:
            job_id: Job ID
            result: Report result
            is_partial: Whether report is partial (some data missing)
            missing_sources: List of missing data sources
        """
        status = JobStatus.PARTIAL.value if is_partial else JobStatus.COMPLETED.value
        message = 'Report generated with partial data. Retrying missing sources...' if is_partial else 'Report generation completed successfully'
        
        updates = {
            'status': status,
            'progress': 100,
            'result': result,
            'message': message,
            'is_partial': is_partial
        }
        
        if missing_sources:
            updates['missing_data_sources'] = missing_sources
        
        return await self.update_job_status(job_id, updates)
    
    async def save_job_error(self, job_id: str, error: str) -> bool:
        """
        Save job error
        """
        return await self.update_job_status(job_id, {
            'status': JobStatus.FAILED.value,
            'error': error,
            'message': f'Report generation failed: {error}'
        })
    
    async def _save_job_status(self, job_id: str, status: Dict[str, Any]):
        """Save job status to storage"""
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"job:{job_id}",
                    3600,  # TTL 1 hour
                    json.dumps(status, default=str)
                )
            except Exception as e:
                print(f"⚠️ Failed to save to Redis: {e}")
                # Fallback to in-memory
                self._in_memory_storage[job_id] = status
        else:
            # In-memory storage (development only)
            self._in_memory_storage[job_id] = status
    
    async def _get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status from storage"""
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"job:{job_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"⚠️ Failed to get from Redis: {e}")
                # Fallback to in-memory
                return self._in_memory_storage.get(job_id)
        else:
            # In-memory storage (development only)
            return self._in_memory_storage.get(job_id)
    
    async def cleanup_old_jobs(self, older_than_hours: int = 24):
        """
        Clean up old completed/failed jobs
        Should be called periodically (e.g., via Vercel Cron)
        """
        # Implementation depends on storage backend
        # For Redis, use SCAN to find old jobs
        # For in-memory, iterate and delete old entries
        pass
    
    async def close(self):
        """Close Redis connection if open"""
        if self.redis_client:
            await self.redis_client.close()

