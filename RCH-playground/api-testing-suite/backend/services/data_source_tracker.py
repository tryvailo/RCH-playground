"""
Data Source Tracker

Tracks which data sources were successfully loaded and which failed
during professional report generation.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DataSourceResult:
    """Result of loading a data source"""
    source_type: str  # 'neighbourhood', 'fsa', 'cqc', 'google_places', 'firecrawl'
    home_id: str
    home_name: str
    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    load_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_type': self.source_type,
            'home_id': self.home_id,
            'home_name': self.home_name,
            'success': self.success,
            'error': self.error,
            'load_time_seconds': self.load_time_seconds
        }


class DataSourceTracker:
    """
    Tracks data source loading results for a report generation job
    """
    
    def __init__(self):
        self.results: List[DataSourceResult] = []
        self.start_time = datetime.now()
    
    def track_success(
        self,
        source_type: str,
        home_id: str,
        home_name: str,
        data: Optional[Dict[str, Any]] = None,
        load_time: float = 0.0
    ):
        """Track a successful data source load"""
        self.results.append(DataSourceResult(
            source_type=source_type,
            home_id=home_id,
            home_name=home_name,
            success=True,
            data=data,
            load_time_seconds=load_time
        ))
    
    def track_failure(
        self,
        source_type: str,
        home_id: str,
        home_name: str,
        error: str,
        load_time: float = 0.0
    ):
        """Track a failed data source load"""
        self.results.append(DataSourceResult(
            source_type=source_type,
            home_id=home_id,
            home_name=home_name,
            success=False,
            error=error,
            load_time_seconds=load_time
        ))
    
    def get_missing_sources(self) -> List[Dict[str, Any]]:
        """Get list of missing (failed) data sources"""
        missing = []
        for result in self.results:
            if not result.success:
                missing.append({
                    'home_id': result.home_id,
                    'home_name': result.home_name,
                    'source_type': result.source_type,
                    'source_name': self._get_source_display_name(result.source_type),
                    'error': result.error
                })
        return missing
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about data source loading"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        
        by_type = {}
        for result in self.results:
            if result.source_type not in by_type:
                by_type[result.source_type] = {'success': 0, 'failed': 0}
            if result.success:
                by_type[result.source_type]['success'] += 1
            else:
                by_type[result.source_type]['failed'] += 1
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total_sources': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0.0,
            'by_type': by_type,
            'total_time_seconds': total_time
        }
    
    def _get_source_display_name(self, source_type: str) -> str:
        """Get display name for a source type"""
        names = {
            'neighbourhood': 'Neighbourhood Analysis',
            'fsa': 'Food Hygiene Rating',
            'cqc': 'CQC Inspection History',
            'google_places': 'Google Places Insights',
            'firecrawl': 'Website Content Analysis'
        }
        return names.get(source_type, source_type.title())

