"""
Proximity Matcher
Finds nearby entities based on geographic coordinates
Used for matching care homes to GP practices, pharmacies, etc.
"""
from typing import List, Dict, Any, Optional, Tuple
from math import radians, cos, sin, asin, sqrt
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class GeoPoint:
    """Geographic point with coordinates"""
    lat: float
    lon: float
    id: Optional[str] = None
    name: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ProximityMatcher:
    """
    Efficient proximity matching for geographic entities
    
    Uses Haversine formula for distance calculations
    Optimized for batch operations
    """
    
    # Earth radius in km
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self):
        """Initialize proximity matcher"""
        self._entities: List[GeoPoint] = []
        self._grid_index: Dict[Tuple[int, int], List[int]] = {}
        self._grid_resolution = 0.1  # ~11km grid cells
    
    def add_entity(self, entity: GeoPoint):
        """Add an entity to the matcher"""
        idx = len(self._entities)
        self._entities.append(entity)
        
        # Add to grid index
        grid_key = self._get_grid_key(entity.lat, entity.lon)
        if grid_key not in self._grid_index:
            self._grid_index[grid_key] = []
        self._grid_index[grid_key].append(idx)
    
    def add_entities(self, entities: List[GeoPoint]):
        """Add multiple entities"""
        for entity in entities:
            self.add_entity(entity)
    
    def clear(self):
        """Clear all entities"""
        self._entities = []
        self._grid_index = {}
    
    def _get_grid_key(self, lat: float, lon: float) -> Tuple[int, int]:
        """Get grid cell key for coordinates"""
        return (
            int(lat / self._grid_resolution),
            int(lon / self._grid_resolution)
        )
    
    def _get_nearby_grid_keys(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float
    ) -> List[Tuple[int, int]]:
        """Get all grid keys that could contain points within radius"""
        # Approximate grid cells to check based on radius
        cells_to_check = int(radius_km / (self._grid_resolution * 111)) + 1  # ~111km per degree
        
        center_key = self._get_grid_key(lat, lon)
        keys = []
        
        for dlat in range(-cells_to_check, cells_to_check + 1):
            for dlon in range(-cells_to_check, cells_to_check + 1):
                keys.append((center_key[0] + dlat, center_key[1] + dlon))
        
        return keys
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance in km between two points using Haversine formula
        """
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return ProximityMatcher.EARTH_RADIUS_KM * c
    
    def find_nearest(
        self, 
        lat: float, 
        lon: float, 
        max_results: int = 10,
        max_distance_km: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Find nearest entities to a point
        
        Args:
            lat: Target latitude
            lon: Target longitude
            max_results: Maximum number of results
            max_distance_km: Optional maximum distance filter
            
        Returns:
            List of dicts with entity data and distance
        """
        if not self._entities:
            return []
        
        # Calculate distances for all candidates
        candidates = []
        
        if max_distance_km:
            # Use grid index for efficiency
            grid_keys = self._get_nearby_grid_keys(lat, lon, max_distance_km)
            candidate_indices = set()
            for key in grid_keys:
                candidate_indices.update(self._grid_index.get(key, []))
            
            for idx in candidate_indices:
                entity = self._entities[idx]
                dist = self.haversine_distance(lat, lon, entity.lat, entity.lon)
                if dist <= max_distance_km:
                    candidates.append((dist, entity))
        else:
            # Check all entities
            for entity in self._entities:
                dist = self.haversine_distance(lat, lon, entity.lat, entity.lon)
                candidates.append((dist, entity))
        
        # Sort by distance and limit
        candidates.sort(key=lambda x: x[0])
        candidates = candidates[:max_results]
        
        # Format results
        results = []
        for dist, entity in candidates:
            result = {
                'id': entity.id,
                'name': entity.name,
                'distance_km': round(dist, 2),
                'lat': entity.lat,
                'lon': entity.lon
            }
            if entity.data:
                result['data'] = entity.data
            results.append(result)
        
        return results
    
    def find_within_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float
    ) -> List[Dict[str, Any]]:
        """
        Find all entities within a radius
        
        Args:
            lat: Target latitude
            lon: Target longitude
            radius_km: Search radius in km
            
        Returns:
            List of entities within radius
        """
        return self.find_nearest(lat, lon, max_results=1000, max_distance_km=radius_km)
    
    def batch_find_nearest(
        self,
        points: List[Tuple[float, float]],
        max_results: int = 5,
        max_distance_km: Optional[float] = None
    ) -> Dict[Tuple[float, float], List[Dict[str, Any]]]:
        """
        Find nearest entities for multiple points
        
        Args:
            points: List of (lat, lon) tuples
            max_results: Max results per point
            max_distance_km: Optional max distance
            
        Returns:
            Dict mapping each point to its nearest entities
        """
        results = {}
        for lat, lon in points:
            results[(lat, lon)] = self.find_nearest(
                lat, lon, max_results, max_distance_km
            )
        return results


def create_proximity_index(
    entities: List[Dict[str, Any]],
    lat_key: str = 'latitude',
    lon_key: str = 'longitude',
    id_key: str = 'id',
    name_key: str = 'name'
) -> ProximityMatcher:
    """
    Create proximity index from list of entities
    
    Args:
        entities: List of entity dicts
        lat_key: Key for latitude
        lon_key: Key for longitude
        id_key: Key for ID
        name_key: Key for name
        
    Returns:
        ProximityMatcher with indexed entities
    """
    matcher = ProximityMatcher()
    
    for entity in entities:
        lat = entity.get(lat_key)
        lon = entity.get(lon_key)
        
        if lat is not None and lon is not None:
            try:
                point = GeoPoint(
                    lat=float(lat),
                    lon=float(lon),
                    id=str(entity.get(id_key, '')),
                    name=entity.get(name_key, ''),
                    data=entity
                )
                matcher.add_entity(point)
            except (ValueError, TypeError):
                continue
    
    return matcher
