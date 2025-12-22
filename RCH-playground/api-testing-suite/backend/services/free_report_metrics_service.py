"""
Free Report Metrics Service
Tracks metrics for monitoring and observability
"""
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum


class MetricType(Enum):
    """Metric types"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class FreeReportMetricsService:
    """Service for collecting and reporting metrics"""

    def __init__(self):
        """Initialize metrics service"""
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.events: List[Dict[str, Any]] = []

    def increment_counter(self, name: str, amount: int = 1) -> None:
        """
        Increment a counter metric

        Args:
            name: Metric name
            amount: Amount to increment by
        """
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += amount

    def set_gauge(self, name: str, value: float) -> None:
        """
        Set a gauge metric

        Args:
            name: Metric name
            value: Gauge value
        """
        self.gauges[name] = value

    def record_histogram(self, name: str, value: float) -> None:
        """
        Record a histogram value

        Args:
            name: Metric name
            value: Value to record
        """
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(value)

    def record_event(
        self, event_type: str, data: Dict[str, Any], status: str = "success"
    ) -> None:
        """
        Record an event

        Args:
            event_type: Type of event
            data: Event data
            status: Event status (success, error, warning)
        """
        self.events.append(
            {
                "type": event_type,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary

        Returns:
            Dictionary with all metrics
        """
        histogram_stats = {}
        for name, values in self.histograms.items():
            if values:
                histogram_stats[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "total": sum(values),
                }

        return {
            "counters": self.counters,
            "gauges": self.gauges,
            "histograms": histogram_stats,
            "event_count": len(self.events),
            "timestamp": datetime.now().isoformat(),
        }

    def get_counter(self, name: str) -> int:
        """Get counter value"""
        return self.counters.get(name, 0)

    def get_gauge(self, name: str) -> float:
        """Get gauge value"""
        return self.gauges.get(name, 0.0)

    def get_histogram_stats(self, name: str) -> Dict[str, Any]:
        """Get histogram statistics"""
        values = self.histograms.get(name, [])
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values),
            "values": values,
        }

    def get_recent_events(self, event_type: str = None, limit: int = 10) -> List[Dict]:
        """
        Get recent events

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        filtered = self.events
        if event_type:
            filtered = [e for e in filtered if e["type"] == event_type]

        return filtered[-limit:]

    def reset(self) -> None:
        """Reset all metrics"""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.events.clear()

    def report_generation(
        self, report_id: str, care_type: str, elapsed_seconds: float, error: str = None
    ) -> None:
        """
        Report a report generation event

        Args:
            report_id: Report ID
            care_type: Care type
            elapsed_seconds: Time taken to generate
            error: Error message if failed
        """
        self.increment_counter("free_report.generated")
        self.record_histogram("free_report.generation_time_seconds", elapsed_seconds)

        status = "error" if error else "success"
        self.record_event(
            "report_generation",
            {
                "report_id": report_id,
                "care_type": care_type,
                "elapsed_seconds": elapsed_seconds,
                "error": error,
            },
            status=status,
        )

        if error:
            self.increment_counter("free_report.generation_errors")

    def report_cache_hit(self, postcode: str, care_type: str) -> None:
        """Record cache hit"""
        self.increment_counter("free_report.cache_hits")
        self.record_event(
            "cache_hit",
            {"postcode": postcode, "care_type": care_type},
        )

    def report_cache_miss(self, postcode: str, care_type: str) -> None:
        """Record cache miss"""
        self.increment_counter("free_report.cache_misses")
        self.record_event(
            "cache_miss",
            {"postcode": postcode, "care_type": care_type},
        )

    def report_matching(self, homes_found: int, homes_selected: int) -> None:
        """Report matching results"""
        self.record_histogram("free_report.homes_found", homes_found)
        self.record_histogram("free_report.homes_selected", homes_selected)
        self.record_event(
            "matching",
            {
                "homes_found": homes_found,
                "homes_selected": homes_selected,
            },
        )

    def report_gap_calculation(self, gap_week: float, gap_percent: float) -> None:
        """Report gap calculation"""
        self.record_histogram("free_report.gap_week", gap_week)
        self.record_histogram("free_report.gap_percent", gap_percent)


# Singleton instance
_metrics_instance = None


def get_free_report_metrics_service() -> FreeReportMetricsService:
    """Get or create metrics service instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = FreeReportMetricsService()
    return _metrics_instance


def create_metrics_service() -> FreeReportMetricsService:
    """Create a new metrics service instance (for testing)"""
    return FreeReportMetricsService()
