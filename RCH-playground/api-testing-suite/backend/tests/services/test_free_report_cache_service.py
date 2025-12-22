"""Tests for Free Report Cache Service"""
import pytest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from free_report_cache_service import (
    FreeReportCacheService,
    get_free_report_cache_service,
    create_cache_service,
)


@pytest.fixture
def cache_service():
    """Create a cache service instance"""
    return create_cache_service(ttl_seconds=10)


@pytest.fixture
def sample_report():
    """Sample report data"""
    return {
        "questionnaire": {"postcode": "SW1A1AA"},
        "care_homes": [{"name": "Home 1"}],
        "fair_cost_gap": {"gap_week": 100},
        "report_id": "123",
    }


class TestFreeReportCacheService:
    """Test cache service"""

    def test_cache_key_generation(self, cache_service):
        """Test cache key generation"""
        key1 = cache_service.generate_cache_key("SW1A1AA", "residential", 1200)
        key2 = cache_service.generate_cache_key("SW1A1AA", "residential", 1200)

        # Same inputs should generate same key
        assert key1 == key2

    def test_cache_key_different_inputs(self, cache_service):
        """Test that different inputs generate different keys"""
        key1 = cache_service.generate_cache_key("SW1A1AA", "residential", 1200)
        key2 = cache_service.generate_cache_key("SW1A1AA", "nursing", 1200)
        key3 = cache_service.generate_cache_key("SW1A1AA", "residential", 1300)

        assert key1 != key2
        assert key1 != key3

    def test_cache_set_and_get(self, cache_service, sample_report):
        """Test setting and getting from cache"""
        cache_service.set("SW1A1AA", "residential", 1200, sample_report)
        cached = cache_service.get("SW1A1AA", "residential", 1200)

        assert cached is not None
        assert cached["report_id"] == "123"

    def test_cache_miss(self, cache_service):
        """Test cache miss"""
        result = cache_service.get("NONEXISTENT", "residential", 1200)
        assert result is None
        assert cache_service.misses == 1

    def test_cache_hit(self, cache_service, sample_report):
        """Test cache hit"""
        cache_service.set("SW1A1AA", "residential", 1200, sample_report)
        result = cache_service.get("SW1A1AA", "residential", 1200)

        assert result is not None
        assert cache_service.hits == 1
        assert cache_service.misses == 0

    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = create_cache_service(ttl_seconds=1)
        report = {"test": "data"}

        cache.set("SW1A1AA", "residential", 1200, report)

        # Should be available immediately
        assert cache.get("SW1A1AA", "residential", 1200) is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("SW1A1AA", "residential", 1200) is None

    def test_cache_clear(self, cache_service, sample_report):
        """Test clearing cache"""
        cache_service.set("SW1A1AA", "residential", 1200, sample_report)
        cache_service.clear()

        assert cache_service.get("SW1A1AA", "residential", 1200) is None
        assert len(cache_service.cache) == 0

    def test_cache_stats(self, cache_service, sample_report):
        """Test cache statistics"""
        cache_service.set("SW1A1AA", "residential", 1200, sample_report)

        # 1 hit
        cache_service.get("SW1A1AA", "residential", 1200)
        # 2 misses
        cache_service.get("NOTFOUND", "residential", 1200)
        cache_service.get("NOTFOUND2", "residential", 1200)

        stats = cache_service.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["total_requests"] == 3
        assert stats["hit_rate_percent"] == pytest.approx(33.3, 0.1)

    def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        cache = create_cache_service(ttl_seconds=1)

        cache.set("SW1A1AA", "residential", 1200, {"test": "1"})
        cache.set("SW1A1BB", "nursing", 1300, {"test": "2"})

        assert len(cache.cache) == 2

        time.sleep(1.1)

        removed = cache.cleanup_expired()

        assert removed == 2
        assert len(cache.cache) == 0

    def test_postcode_case_insensitive(self, cache_service, sample_report):
        """Test that postcode is case-insensitive"""
        cache_service.set("sw1a1aa", "residential", 1200, sample_report)
        result = cache_service.get("SW1A1AA", "residential", 1200)

        assert result is not None

    def test_multiple_entries(self, cache_service):
        """Test caching multiple entries"""
        data1 = {"report_id": "1"}
        data2 = {"report_id": "2"}
        data3 = {"report_id": "3"}

        cache_service.set("SW1A1AA", "residential", 1200, data1)
        cache_service.set("SW1A1BB", "nursing", 1300, data2)
        cache_service.set("SW1A1CC", "dementia", 1100, data3)

        assert cache_service.get("SW1A1AA", "residential", 1200)["report_id"] == "1"
        assert cache_service.get("SW1A1BB", "nursing", 1300)["report_id"] == "2"
        assert cache_service.get("SW1A1CC", "dementia", 1100)["report_id"] == "3"

        assert len(cache_service.cache) == 3

    def test_singleton_pattern(self):
        """Test singleton pattern"""
        service1 = get_free_report_cache_service()
        service2 = get_free_report_cache_service()

        assert service1 is service2
        assert isinstance(service1, FreeReportCacheService)

    def test_cache_hit_rate_calculation(self, cache_service, sample_report):
        """Test hit rate calculation"""
        cache_service.set("SW1A1AA", "residential", 1200, sample_report)

        # 3 hits
        cache_service.get("SW1A1AA", "residential", 1200)
        cache_service.get("SW1A1AA", "residential", 1200)
        cache_service.get("SW1A1AA", "residential", 1200)

        # 1 miss
        cache_service.get("NOTFOUND", "residential", 1200)

        stats = cache_service.get_stats()

        assert stats["hit_rate_percent"] == 75.0
