"""
Location normalization service to map city names to local authority names
for consistent database matching.
"""

from typing import Optional, Dict, List
import re


class LocationNormalizer:
    """Normalize city names to local authority names for database matching"""
    
    # Mapping of common city names to their local authority equivalents
    CITY_TO_LOCAL_AUTHORITY: Dict[str, List[str]] = {
        'manchester': ['Manchester', 'Manchester City Council', 'City of Manchester'],
        'london': ['London', 'City of London', 'Greater London', 'Westminster', 'Camden', 'Islington', 'Hackney', 'Tower Hamlets', 'Greenwich', 'Lewisham', 'Southwark', 'Lambeth', 'Wandsworth', 'Hammersmith and Fulham', 'Kensington and Chelsea', 'Hammersmith & Fulham', 'Kensington & Chelsea'],
        'birmingham': ['Birmingham', 'Birmingham City Council', 'City of Birmingham'],
        'leeds': ['Leeds', 'Leeds City Council', 'City of Leeds'],
        'liverpool': ['Liverpool', 'Liverpool City Council', 'City of Liverpool'],
        'sheffield': ['Sheffield', 'Sheffield City Council', 'City of Sheffield'],
        'bristol': ['Bristol', 'Bristol City Council', 'City of Bristol'],
        'edinburgh': ['Edinburgh', 'City of Edinburgh', 'Edinburgh City Council'],
        'glasgow': ['Glasgow', 'Glasgow City Council', 'City of Glasgow'],
        'cardiff': ['Cardiff', 'Cardiff City Council', 'City of Cardiff'],
        'belfast': ['Belfast', 'Belfast City Council', 'City of Belfast'],
        'newcastle': ['Newcastle upon Tyne', 'Newcastle', 'Newcastle City Council'],
        'nottingham': ['Nottingham', 'Nottingham City Council', 'City of Nottingham'],
        'leicester': ['Leicester', 'Leicester City Council', 'City of Leicester'],
        'cambridge': ['Cambridge', 'Cambridge City Council', 'City of Cambridge'],
        'oxford': ['Oxford', 'Oxford City Council', 'City of Oxford'],
        'york': ['York', 'City of York', 'York City Council'],
        'brighton': ['Brighton and Hove', 'Brighton', 'Brighton & Hove', 'Brighton and Hove City Council'],
        'southampton': ['Southampton', 'Southampton City Council', 'City of Southampton'],
        'portsmouth': ['Portsmouth', 'Portsmouth City Council', 'City of Portsmouth'],
        'plymouth': ['Plymouth', 'Plymouth City Council', 'City of Plymouth'],
        'reading': ['Reading', 'Reading Borough Council'],
        'northampton': ['Northampton', 'Northampton Borough Council'],
        'luton': ['Luton', 'Luton Borough Council'],
        'bolton': ['Bolton', 'Bolton Metropolitan Borough Council'],
        'oldham': ['Oldham', 'Oldham Metropolitan Borough Council'],
        'rochdale': ['Rochdale', 'Rochdale Metropolitan Borough Council'],
        'stockport': ['Stockport', 'Stockport Metropolitan Borough Council'],
        'tameside': ['Tameside', 'Tameside Metropolitan Borough Council'],
        'trafford': ['Trafford', 'Trafford Metropolitan Borough Council'],
        'wigan': ['Wigan', 'Wigan Metropolitan Borough Council'],
        'salford': ['Salford', 'Salford City Council'],
        'bury': ['Bury', 'Bury Metropolitan Borough Council'],
    }
    
    @classmethod
    def normalize_city_name(cls, city_name: Optional[str]) -> Optional[str]:
        """
        Normalize city name by removing extra spaces, converting to title case
        
        Args:
            city_name: Raw city name from user input
            
        Returns:
            Normalized city name
        """
        if not city_name:
            return None
        
        # Remove extra whitespace and convert to title case
        normalized = re.sub(r'\s+', ' ', city_name.strip()).title()
        return normalized if normalized else None
    
    @classmethod
    def get_local_authority_variants(cls, city_name: Optional[str]) -> List[str]:
        """
        Get all possible local authority name variants for a city name
        
        Args:
            city_name: City name (will be normalized)
            
        Returns:
            List of possible local authority names to search for
        """
        if not city_name:
            return []
        
        normalized = cls.normalize_city_name(city_name)
        if not normalized:
            return []
        
        # Check if we have a mapping
        city_lower = normalized.lower()
        if city_lower in cls.CITY_TO_LOCAL_AUTHORITY:
            variants = cls.CITY_TO_LOCAL_AUTHORITY[city_lower].copy()
            # Add the normalized name itself as a variant
            if normalized not in variants:
                variants.insert(0, normalized)
            return variants
        
        # If no mapping found, return normalized name and common variations
        variants = [normalized]
        
        # Add common suffixes
        if 'City' not in normalized and 'Council' not in normalized:
            variants.append(f"{normalized} City Council")
            variants.append(f"City of {normalized}")
        
        return variants
    
    @classmethod
    def build_location_query(cls, city_name: Optional[str]) -> Optional[str]:
        """
        Build SQL WHERE clause for location matching with multiple variants
        
        Args:
            city_name: City name from user input
            
        Returns:
            SQL WHERE clause fragment or None
        """
        variants = cls.get_local_authority_variants(city_name)
        if not variants:
            return None
        
        # Build OR conditions for all variants
        conditions = []
        for variant in variants:
            conditions.append(f"(LOWER(local_authority) = LOWER(%s) OR LOWER(city) = LOWER(%s))")
        
        return " AND (" + " OR ".join(conditions) + ")"
    
    @classmethod
    def get_location_params(cls, city_name: Optional[str]) -> List[str]:
        """
        Get SQL parameters for location matching
        
        Args:
            city_name: City name from user input
            
        Returns:
            List of parameters to use in SQL query (each variant appears twice for local_authority and city)
        """
        variants = cls.get_local_authority_variants(city_name)
        params = []
        for variant in variants:
            params.append(variant)  # For local_authority
            params.append(variant)  # For city
        return params


def normalize_location_for_search(city_name: Optional[str]) -> Dict[str, any]:
    """
    Convenience function to normalize location for database search
    
    Args:
        city_name: City name from user input
        
    Returns:
        Dict with 'query_fragment' and 'params' for SQL query building
    """
    normalizer = LocationNormalizer()
    variants = normalizer.get_local_authority_variants(city_name)
    
    if not variants:
        return {
            'query_fragment': None,
            'params': [],
            'variants': []
        }
    
    # Build query fragment
    conditions = []
    for variant in variants:
        conditions.append(f"(LOWER(local_authority) = LOWER(%s) OR LOWER(city) = LOWER(%s))")
    
    query_fragment = " AND (" + " OR ".join(conditions) + ")"
    
    # Build params (each variant twice: for local_authority and city)
    params = []
    for variant in variants:
        params.append(variant)
        params.append(variant)
    
    return {
        'query_fragment': query_fragment,
        'params': params,
        'variants': variants
    }

