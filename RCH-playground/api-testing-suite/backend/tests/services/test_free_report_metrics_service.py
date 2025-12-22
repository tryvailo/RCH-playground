"""Tests for Free Report Metrics Service"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from free_report_metrics_service import (
    FreeReportMetricsService,
    get_free_report_metrics_service,
    create_metrics_service,
)


@pytest.fixture
def metrics_service():
    """Create a metrics service instance"""
    return create_metrics_service()


class TestFreeReportMetricsService:
    """Test metrics service"""

    def test_increment_counter(self, metrics_service):
        """Test incrementing counter"""
        metrics_service.increment_counter("test.counter")
        assert metrics_service.get_counter("test.counter") == 1

        metrics_service.increment_counter("test.counter", 5)
        assert metrics_service.get_counter("test.counter") == 6

    def test_set_gauge(self, metrics_service):
        """Test setting gauge"""
        metrics_service.set_gauge("test.gauge", 42.5)
        assert metrics_service.get_gauge("test.gauge") == 42.5

        metrics_service.set_gauge("test.gauge", 100.0)
        assert metrics_service.get_gauge("test.gauge") == 100.0

    def test_record_histogram(self, metrics_service):
        """Test recording histogram values"""
        metrics_service.record_histogram("test.histogram", 10)
        metrics_service.record_histogram("test.histogram", 20)
        metrics_service.record_histogram("test.histogram", 30)

        stats = metrics_service.get_histogram_stats("test.histogram")

        assert stats["count"] == 3
        assert stats["min"] == 10
        assert stats["max"] == 30
        assert stats["avg"] == 20

    def test_record_event(self, metrics_service):
        """Test recording events"""
        metrics_service.record_event("test.event", {"data": "value"}, status="success")

        events = metrics_service.get_recent_events(limit=10)

        assert len(events) == 1
        assert events[0]["type"] == "test.event"
        assert events[0]["status"] == "success"
        assert events[0]["data"]["data"] == "value"

    def test_get_summary(self, metrics_service):
        """Test getting metrics summary"""
        metrics_service.increment_counter("counter1", 5)
        metrics_service.set_gauge("gauge1", 10.5)
        metrics_service.record_histogram("histogram1", 100)
        metrics_service.record_event("event1", {"key": "value"})

        summary = metrics_service.get_summary()

        assert summary["counters"]["counter1"] == 5
        assert summary["gauges"]["gauge1"] == 10.5
        assert summary["histograms"]["histogram1"]["count"] == 1
        assert summary["event_count"] == 1

    def test_report_generation_success(self, metrics_service):
        """Test reporting successful report generation"""
        metrics_service.report_generation(
            report_id="123", care_type="residential", elapsed_seconds=2.5, error=None
        )

        assert metrics_service.get_counter("free_report.generated") == 1
        assert metrics_service.get_counter("free_report.generation_errors") == 0

    def test_report_generation_error(self, metrics_service):
        """Test reporting failed report generation"""
        metrics_service.report_generation(
            report_id="123",
            care_type="residential",
            elapsed_seconds=1.0,
            error="Test error",
        )

        assert metrics_service.get_counter("free_report.generated") == 1
        assert metrics_service.get_counter("free_report.generation_errors") == 1

    def test_report_cache_hit(self, metrics_service):
        """Test reporting cache hit"""
        metrics_service.report_cache_hit("SW1A1AA", "residential")

        assert metrics_service.get_counter("free_report.cache_hits") == 1

    def test_report_cache_miss(self, metrics_service):
        """Test reporting cache miss"""
        metrics_service.report_cache_miss("SW1A1AA", "residential")

        assert metrics_service.get_counter("free_report.cache_misses") == 1

    def test_report_matching(self, metrics_service):
        """Test reporting matching results"""
        metrics_service.report_matching(homes_found=50, homes_selected=3)

        summary = metrics_service.get_summary()

        assert summary["histograms"]["free_report.homes_found"]["total"] == 50
        assert summary["histograms"]["free_report.homes_selected"]["total"] == 3

    def test_report_gap_calculation(self, metrics_service):
        """Test reporting gap calculation"""
        metrics_service.report_gap_calculation(gap_week=152, gap_percent=14.5)

        summary = metrics_service.get_summary()

        assert summary["histograms"]["free_report.gap_week"]["total"] == 152
        assert summary["histograms"]["free_report.gap_percent"]["total"] == 14.5

    def test_get_recent_events_filtered(self, metrics_service):
        """Test filtering events"""
        metrics_service.record_event("event1", {"data": "1"})
        metrics_service.record_event("event2", {"data": "2"})
        metrics_service.record_event("event1", {"data": "3"})
        metrics_service.record_event("event2", {"data": "4"})

        event1s = metrics_service.get_recent_events(event_type="event1", limit=10)

        assert len(event1s) == 2
        assert all(e["type"] == "event1" for e in event1s)

    def test_get_recent_events_limit(self, metrics_service):
        """Test limiting recent events"""
        for i in range(10):
            metrics_service.record_event("event", {"index": i})

        recent = metrics_service.get_recent_events(limit=3)

        assert len(recent) == 3
        assert recent[-1]["data"]["index"] == 9

    def test_reset_metrics(self, metrics_service):
        """Test resetting metrics"""
        metrics_service.increment_counter("counter1")
        metrics_service.set_gauge("gauge1", 10)
        metrics_service.record_histogram("hist1", 5)
        metrics_service.record_event("event1", {})

        metrics_service.reset()

        assert len(metrics_service.counters) == 0
        assert len(metrics_service.gauges) == 0
        assert len(metrics_service.histograms) == 0
        assert len(metrics_service.events) == 0

    def test_histogram_statistics(self, metrics_service):
        """Test histogram statistics calculation"""
        metrics_service.record_histogram("response_time", 100)
        metrics_service.record_histogram("response_time", 200)
        metrics_service.record_histogram("response_time", 300)

        stats = metrics_service.get_histogram_stats("response_time")

        assert stats["count"] == 3
        assert stats["min"] == 100
        assert stats["max"] == 300
        assert stats["avg"] == 200
        assert stats["total"] == 600

    def test_singleton_pattern(self):
        """Test singleton pattern"""
        service1 = get_free_report_metrics_service()
        service2 = get_free_report_metrics_service()

        assert service1 is service2
        assert isinstance(service1, FreeReportMetricsService)

    def test_event_timestamp(self, metrics_service):
        """Test that events have timestamps"""
        metrics_service.record_event("test", {"data": "value"})

        events = metrics_service.get_recent_events()

        assert len(events) == 1
        assert "timestamp" in events[0]
        assert events[0]["timestamp"] is not None

    def test_multiple_metrics_tracking(self, metrics_service):
        """Test tracking multiple metrics simultaneously"""
        # Simulate multiple report generations
        for i in range(5):
            metrics_service.report_generation(
                report_id=str(i),
                care_type="residential",
                elapsed_seconds=2.0 + i * 0.5,
            )

        metrics_service.report_cache_hit("SW1A1AA", "residential")
        metrics_service.report_cache_hit("SW1A1BB", "nursing")

        assert metrics_service.get_counter("free_report.generated") == 5
        assert metrics_service.get_counter("free_report.cache_hits") == 2

        summary = metrics_service.get_summary()
        time_stats = summary["histograms"]["free_report.generation_time_seconds"]
        assert time_stats["count"] == 5
        assert time_stats["min"] == 2.0
