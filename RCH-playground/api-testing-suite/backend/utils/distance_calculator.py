"""
Distance Calculator Utility
Reusable method for calculating distance between user postcode and care home
Used across all reports (Free Report, Professional Report, etc.)
"""
from typing import Dict, Any, Optional
from utils.geo import calculate_distance_km, validate_coordinates


async def calculate_home_distance(
    home: Dict[str, Any],
    user_lat: Optional[float],
    user_lon: Optional[float],
    postcode_loader=None
) -> Optional[float]:
    """
    Calculate distance from user location to care home.
    
    ALWAYS calculates distance from coordinates (most accurate method).
    This method implements a multi-strategy approach:
    1. Calculate from home coordinates if available (PREFERRED - always use this if possible)
    2. Calculate from home postcode resolution if coordinates missing
    
    Args:
        home: Care home dictionary with latitude, longitude, postcode
        user_lat: User latitude (from postcode resolution)
        user_lon: User longitude (from postcode resolution)
        postcode_loader: Optional async postcode loader for resolving home postcode
    
    Returns:
        Distance in kilometers (rounded to 2 decimal places) or None if cannot calculate
    """
    # Step 1: Calculate from coordinates if available (most accurate - ALWAYS PREFERRED)
    if user_lat is not None and user_lon is not None:
        home_lat = home.get('latitude')
        home_lon = home.get('longitude')
        
        if home_lat is not None and home_lon is not None:
            try:
                # Convert all coordinates to float
                user_lat_float = float(user_lat)
                user_lon_float = float(user_lon)
                home_lat_float = float(home_lat)
                home_lon_float = float(home_lon)
                
                # Validate coordinates
                if (validate_coordinates(user_lat_float, user_lon_float) and 
                    validate_coordinates(home_lat_float, home_lon_float)):
                    distance_km = calculate_distance_km(
                        user_lat_float, 
                        user_lon_float, 
                        home_lat_float, 
                        home_lon_float
                    )
                    return round(distance_km, 2)
            except (ValueError, TypeError) as e:
                # Log error but continue to next strategy
                pass
    
    # Step 2: If coordinates not available, try postcode resolution
    if (user_lat is not None and 
        user_lon is not None and 
        postcode_loader is not None):
        
        home_postcode = home.get('postcode')
        if home_postcode:
            try:
                home_postcode_info = await postcode_loader.resolve_postcode(home_postcode)
                if home_postcode_info:
                    home_lat = home_postcode_info.get('latitude')
                    home_lon = home_postcode_info.get('longitude')
                    
                    if home_lat is not None and home_lon is not None:
                        try:
                            # Convert all coordinates to float
                            user_lat_float = float(user_lat)
                            user_lon_float = float(user_lon)
                            home_lat_float = float(home_lat)
                            home_lon_float = float(home_lon)
                            
                            # Validate coordinates
                            if (validate_coordinates(user_lat_float, user_lon_float) and 
                                validate_coordinates(home_lat_float, home_lon_float)):
                                distance_km = calculate_distance_km(
                                    user_lat_float, 
                                    user_lon_float, 
                                    home_lat_float, 
                                    home_lon_float
                                )
                                return round(distance_km, 2)
                        except (ValueError, TypeError):
                            pass
            except Exception:
                # Ignore errors in postcode resolution
                pass
    
    # If all strategies fail, return None (better than wrong value)
    return None

