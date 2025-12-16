"""
Data Integrations Module
Provides access to external data sources for care home analysis
"""

from .os_places_loader import OSPlacesLoader
from .ons_loader import ONSLoader
from .osm_loader import OSMLoader
from .nhsbsa_loader import NHSBSALoader
from .proximity_matcher import ProximityMatcher, GeoPoint, create_proximity_index
from .batch_processor import BatchProcessor, NeighbourhoodAnalyzer, BatchProgress
from .cache_manager import CacheManager

__all__ = [
    'OSPlacesLoader',
    'ONSLoader',
    'OSMLoader',
    'NHSBSALoader',
    'ProximityMatcher',
    'GeoPoint',
    'create_proximity_index',
    'BatchProcessor',
    'NeighbourhoodAnalyzer',
    'BatchProgress',
    'CacheManager',
]
