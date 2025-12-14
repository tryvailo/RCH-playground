"""
Geographic utilities
Common functions for geographic calculations
"""
import math
from typing import Optional


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two points using Haversine formula
    
    Args:
        lat1: Latitude of first point (degrees)
        lon1: Longitude of first point (degrees)
        lat2: Latitude of second point (degrees)
        lon2: Longitude of second point (degrees)
    
    Returns:
        Distance in kilometers (rounded to 2 decimal places)
    
    Raises:
        ValueError: If coordinates are invalid (out of range)
    """
    # Validate coordinates
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError(f"Invalid latitude: must be between -90 and 90")
    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError(f"Invalid longitude: must be between -180 and 180")
    
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )
    
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return round(distance, 2)


def calculate_distance_miles(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two points in miles
    
    Args:
        lat1: Latitude of first point (degrees)
        lon1: Longitude of first point (degrees)
        lat2: Latitude of second point (degrees)
        lon2: Longitude of second point (degrees)
    
    Returns:
        Distance in miles (rounded to 2 decimal places)
    """
    distance_km = calculate_distance_km(lat1, lon1, lat2, lon2)
    return round(distance_km * 0.621371, 2)


def validate_coordinates(
    lat: Optional[float],
    lon: Optional[float]
) -> bool:
    """
    Validate that coordinates are valid
    
    Args:
        lat: Latitude (degrees)
        lon: Longitude (degrees)
    
    Returns:
        True if coordinates are valid, False otherwise
    """
    if lat is None or lon is None:
        return False
    
    try:
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    except (TypeError, ValueError):
        return False

