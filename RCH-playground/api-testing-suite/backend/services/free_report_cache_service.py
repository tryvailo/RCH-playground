"""
Free Report Cache Service
Caches generated reports for quick retrieval
"""
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class FreeReportCacheService:
    """Service for caching free reports in memory"""

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache service

        Args:
            ttl_seconds: Time to live for cache entries (default 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def generate_cache_key(
        self, postcode: str, care_type: str, budget: float
    ) -> str:
        """
        Generate cache key from request parameters

        Args:
            postcode: UK postcode
            care_type: Type of care
            budget: Weekly budget

        Returns:
            Hash key for caching
        """
        key_str = f"{postcode.upper()}:{care_type}:{budget}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(
        self, postcode: str, care_type: str, budget: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached report if available and not expired

        Args:
            postcode: UK postcode
            care_type: Type of care
            budget: Weekly budget

        Returns:
            Cached response or None if not found/expired
        """
        key = self.generate_cache_key(postcode, care_type, budget)

        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]
        created_at = entry.get("created_at")

        # Check if expired
        if created_at:
            age = (datetime.now() - created_at).total_seconds()
            if age > self.ttl_seconds:
                del self.cache[key]
                self.misses += 1
                return None

        # Cache hit
        self.hits += 1
        entry["cache_hit"] = True
        return entry.get("data")

    def set(
        self, postcode: str, care_type: str, budget: float, data: Dict[str, Any]
    ) -> None:
        """
        Cache a report response

        Args:
            postcode: UK postcode
            care_type: Type of care
            budget: Weekly budget
            data: Report data to cache
        """
        key = self.generate_cache_key(postcode, care_type, budget)

        self.cache[key] = {
            "data": data,
            "created_at": datetime.now(),
            "postcode": postcode,
            "care_type": care_type,
            "budget": budget,
        }

    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with hit/miss stats
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 1),
            "cached_entries": len(self.cache),
            "ttl_seconds": self.ttl_seconds,
        }

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = []

        for key, entry in self.cache.items():
            created_at = entry.get("created_at")
            if created_at:
                age = (now - created_at).total_seconds()
                if age > self.ttl_seconds:
                    expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)


# Singleton instance
_cache_instance = None


def get_free_report_cache_service(
    ttl_seconds: int = 3600,
) -> FreeReportCacheService:
    """Get or create cache service instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = FreeReportCacheService(ttl_seconds=ttl_seconds)
    return _cache_instance


def create_cache_service(ttl_seconds: int = 3600) -> FreeReportCacheService:
    """Create a new cache service instance (for testing)"""
    return FreeReportCacheService(ttl_seconds=ttl_seconds)
