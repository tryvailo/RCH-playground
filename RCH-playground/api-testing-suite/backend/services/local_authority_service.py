"""
Local Authority Contacts Service
Loads and provides Local Authority contact information from JSON database
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)

class LocalAuthorityService:
    """Service for managing Local Authority contact information"""
    
    def __init__(self):
        """Initialize the service and load LA contacts data"""
        self.contacts_data: Optional[Dict[str, Any]] = None
        self.contacts_by_name: Dict[str, Dict[str, Any]] = {}
        self.contacts_by_ons_code: Dict[str, Dict[str, Any]] = {}
        self.postcode_client = httpx.AsyncClient(timeout=10.0)
        self.postcodes_io_url = "https://api.postcodes.io/postcodes"
        self._postcode_cache: Dict[str, Dict[str, Any]] = {}  # Cache for postcode lookups
        self._load_contacts()
    
    def _load_contacts(self):
        """Load LA contacts from JSON file"""
        try:
            # Get the path to the data file
            current_file = Path(__file__)
            data_file = current_file.parent.parent / "data" / "local_authority_contacts.json"
            
            if not data_file.exists():
                logger.warning(f"LA contacts file not found at {data_file}")
                return
            
            with open(data_file, 'r', encoding='utf-8') as f:
                self.contacts_data = json.load(f)
            
            # Build lookup dictionaries with multiple name variations
            councils = self.contacts_data.get('councils', [])
            for council in councils:
                council_name = council.get('council_name', '')
                ons_code = council.get('ons_code', '')
                
                # Store by full name (normalized)
                normalized_full = self._normalize_name(council_name)
                self.contacts_by_name[normalized_full] = council
                
                # Store by short name (without suffixes)
                short_name = self._get_short_name(council_name)
                if short_name and short_name != normalized_full:
                    self.contacts_by_name[short_name.lower()] = council
                
                # Store by ONS code
                if ons_code:
                    self.contacts_by_ons_code[ons_code] = council
            
            logger.info(f"Loaded {len(councils)} Local Authority contacts with {len(self.contacts_by_name)} name variations")
            
        except Exception as e:
            logger.error(f"Error loading LA contacts: {e}")
            self.contacts_data = None
    
    def _normalize_name(self, name: str) -> str:
        """Normalize council name for matching"""
        if not name:
            return ""
        
        normalized = name.lower().strip()
        
        # Remove common suffixes
        suffixes = [
            " city council",
            " borough council",
            " county council",
            " council",
            " london borough of",
            " royal borough of",
            " london borough",
            " city",
            " borough",
            " county"
        ]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        return normalized
    
    def _get_short_name(self, name: str) -> str:
        """Get short name without prefixes like 'London Borough of', 'Royal Borough of'"""
        if not name:
            return ""
        
        # Remove prefixes
        prefixes = [
            "london borough of ",
            "royal borough of ",
            "city of ",
        ]
        
        short = name.lower().strip()
        for prefix in prefixes:
            if short.startswith(prefix):
                short = short[len(prefix):].strip()
                break
        
        # Remove suffixes
        return self._normalize_name(short)
    
    async def get_la_by_postcode(self, postcode: str, use_cache: bool = True, use_priority: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get Local Authority contact information by postcode
        
        Args:
            postcode: UK postcode
            use_cache: Whether to use cached results
            use_priority: Whether to check priority LA list first (faster for MVP)
            
        Returns:
            Dict with LA contact information or None if not found
        """
        if not postcode:
            return None
        
        # Try priority LA list first (faster for MVP)
        if use_priority:
            try:
                priority_file = Path(__file__).parent.parent / "data" / "priority_la_contacts.json"
                if priority_file.exists():
                    with open(priority_file, 'r', encoding='utf-8') as f:
                        priority_data = json.load(f)
                        priority_councils = priority_data.get('councils', [])
            except Exception:
                priority_councils = []
        else:
            priority_councils = []
        
        try:
            # Normalize postcode
            normalized_postcode = postcode.upper().strip().replace(" ", "")
            
            # Check cache first
            if use_cache and normalized_postcode in self._postcode_cache:
                logger.debug(f"Using cached LA lookup for postcode: {normalized_postcode}")
                return self._postcode_cache[normalized_postcode]
            
            # Call postcodes.io API to get LA name
            try:
                response = await self.postcode_client.get(
                    f"{self.postcodes_io_url}/{normalized_postcode}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('result', {})
                    
                    # Get admin_district (Local Authority name) - primary source
                    la_name = result.get('admin_district')
                    
                    # Also check codes for ONS code matching
                    codes = result.get('codes', {})
                    ons_code = codes.get('admin_district')  # ONS code for the LA
                    
                    # Try ONS code match first (most reliable)
                    if ons_code and ons_code in self.contacts_by_ons_code:
                        logger.info(f"Found LA by ONS code: {ons_code}")
                        found_contact = dict(self.contacts_by_ons_code[ons_code])
                        # Cache the result
                        if use_cache:
                            self._postcode_cache[normalized_postcode] = found_contact
                        return found_contact
                    
                    # Try name matching with multiple strategies
                    if la_name:
                        # Strategy 1: Exact normalized match
                        la_contact = self._find_la_by_name(la_name)
                        if la_contact:
                            logger.info(f"Found LA by exact name match: {la_name}")
                            found_contact = dict(la_contact)
                            if use_cache:
                                self._postcode_cache[normalized_postcode] = found_contact
                            return found_contact
                        
                        # Strategy 2: Partial/fuzzy match
                        la_contact = self._find_la_by_partial_name(la_name)
                        if la_contact:
                            logger.info(f"Found LA by partial name match: {la_name}")
                            found_contact = dict(la_contact)
                            if use_cache:
                                self._postcode_cache[normalized_postcode] = found_contact
                            return found_contact
                        
                        # Strategy 3: Try with common variations
                        la_contact = self._find_la_with_variations(la_name)
                        if la_contact:
                            logger.info(f"Found LA by name variation: {la_name}")
                            found_contact = dict(la_contact)
                            if use_cache:
                                self._postcode_cache[normalized_postcode] = found_contact
                            return found_contact
                    
                    # Fallback: Try admin_county (for county councils)
                    admin_county = result.get('admin_county')
                    if admin_county and admin_county != la_name:
                        la_contact = self._find_la_by_name(admin_county)
                        if la_contact:
                            logger.info(f"Found LA by county name: {admin_county}")
                            found_contact = dict(la_contact)
                            if use_cache:
                                self._postcode_cache[normalized_postcode] = found_contact
                            return found_contact
                    
                    # If not found, return basic info from postcodes.io with helpful message
                    fallback_result = {
                        "council_name": la_name or admin_county or "Unknown",
                        "region": result.get('region', 'Unknown'),
                        "postcode": normalized_postcode,
                        "note": f"Contact information for {la_name or admin_county or 'this council'} is not available in our database. Please visit the council website or contact them directly.",
                        "asc_website_url": None,
                        "asc_phone": None,
                        "asc_email": None,
                        "ons_code": ons_code
                    }
                    
                    # Cache the result (even if not found in our DB)
                    if use_cache:
                        self._postcode_cache[normalized_postcode] = fallback_result
                    
                    return fallback_result
                else:
                    logger.warning(f"Postcodes.io API returned {response.status_code} for postcode {postcode}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error calling postcodes.io API: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting LA by postcode: {e}")
            return None
    
    def _find_la_by_name(self, la_name: str) -> Optional[Dict[str, Any]]:
        """Find LA contact by exact or normalized name"""
        if not la_name:
            return None
        
        # Normalize the input name
        normalized = self._normalize_name(la_name)
        
        # Try exact match with normalized name
        if normalized in self.contacts_by_name:
            return self.contacts_by_name[normalized]
        
        # Try matching against all stored variations
        for stored_name, council_data in self.contacts_by_name.items():
            if normalized == stored_name:
                return council_data
        
        return None
    
    def _find_la_by_partial_name(self, la_name: str) -> Optional[Dict[str, Any]]:
        """Find LA contact by partial name match"""
        if not la_name:
            return None
        
        normalized = self._normalize_name(la_name)
        
        # Try partial matches (substring)
        for stored_name, council_data in self.contacts_by_name.items():
            # Check if one contains the other
            if normalized in stored_name or stored_name in normalized:
                # Prefer longer matches (more specific)
                if len(stored_name) >= len(normalized) * 0.7:  # At least 70% match
                    return council_data
        
        return None
    
    def _find_la_with_variations(self, la_name: str) -> Optional[Dict[str, Any]]:
        """Find LA contact by trying common name variations"""
        if not la_name:
            return None
        
        normalized = la_name.lower().strip()
        
        # Common variations mapping
        variations = [
            normalized,
            f"{normalized} city council",
            f"{normalized} borough council",
            f"{normalized} county council",
            f"{normalized} council",
            f"london borough of {normalized}",
            f"royal borough of {normalized}",
        ]
        
        # Also try removing "City", "Borough", "County" if present
        if " city" in normalized:
            variations.append(normalized.replace(" city", ""))
        if " borough" in normalized:
            variations.append(normalized.replace(" borough", ""))
        if " county" in normalized:
            variations.append(normalized.replace(" county", ""))
        
        # Try each variation
        for variation in variations:
            normalized_var = self._normalize_name(variation)
            if normalized_var in self.contacts_by_name:
                return self.contacts_by_name[normalized_var]
        
        # Try fuzzy matching - check if key words match
        # Split into words and check if major words match
        input_words = set(normalized.split())
        for stored_name, council_data in self.contacts_by_name.items():
            stored_words = set(stored_name.split())
            # If at least 2 words match, consider it a match
            common_words = input_words.intersection(stored_words)
            if len(common_words) >= 2 and len(common_words) >= len(input_words) * 0.5:
                return council_data
        
        return None
    
    def get_la_by_name(self, la_name: str) -> Optional[Dict[str, Any]]:
        """Get LA contact by name"""
        return self._find_la_by_name(la_name)
    
    def get_all_councils(self) -> List[Dict[str, Any]]:
        """Get all councils in the database"""
        if not self.contacts_data:
            return []
        return self.contacts_data.get('councils', [])

