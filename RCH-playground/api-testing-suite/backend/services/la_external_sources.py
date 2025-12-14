"""
External Data Sources for Local Authority Contacts
Integrates with official APIs and data sources to enrich LA contact information
"""
import json
import logging
import httpx
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class LAExternalSources:
    """Service for fetching Local Authority data from external sources"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        
        # External API endpoints
        self.postcodes_io_url = "https://api.postcodes.io/postcodes"
        self.gov_uk_register_url = "https://www.registers.service.gov.uk/registers/local-authorities/records"
        self.ons_geography_url = "https://www.ons.gov.uk/api/v1/geography"
        
    async def fetch_from_postcodes_io(self, postcode: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Local Authority information from postcodes.io API
        
        Args:
            postcode: UK postcode
            
        Returns:
            Dict with LA information or None
        """
        try:
            normalized = postcode.upper().strip().replace(" ", "")
            url = f"{self.postcodes_io_url}/{normalized}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200 and data.get("result"):
                    result = data["result"]
                    return {
                        "local_authority": result.get("admin_district") or result.get("admin_county"),
                        "region": result.get("region"),
                        "county": result.get("admin_county"),
                        "country": result.get("country"),
                        "postcode": result.get("postcode"),
                    }
        except Exception as e:
            logger.warning(f"Postcodes.io API error: {e}")
        
        return None
    
    async def fetch_from_gov_uk_register(self, ons_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Local Authority information from GOV.UK Register
        
        Args:
            ons_code: ONS code (e.g., E06000001)
            
        Returns:
            Dict with LA information or None
        """
        try:
            # GOV.UK Register API (if available)
            # Note: This may require authentication or have rate limits
            url = f"{self.gov_uk_register_url}/{ons_code}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                # Parse register data structure
                return {
                    "name": data.get("name"),
                    "official-name": data.get("official-name"),
                    "website": data.get("website"),
                    "contact": data.get("contact"),
                }
        except Exception as e:
            logger.debug(f"GOV.UK Register API error (may not be available): {e}")
        
        return None
    
    async def fetch_from_google_places(self, council_name: str, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch council contact information from Google Places API
        
        Args:
            council_name: Name of the council
            location: Optional location hint (e.g., "London, UK")
            
        Returns:
            Dict with contact information or None
        """
        try:
            # Try to get Google Places API key from config
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from config_manager import get_credentials
                
                creds = get_credentials()
                api_key = None
                
                if creds and hasattr(creds, 'google_places') and creds.google_places:
                    api_key = getattr(creds.google_places, 'api_key', None) or getattr(creds.google_places, 'apiKey', None)
                
                # Fallback: read from config file
                if not api_key:
                    config_file = Path(__file__).parent.parent / "config.json"
                    if config_file.exists():
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                            google_config = config_data.get('google_places', {})
                            api_key = google_config.get('api_key') or google_config.get('apiKey')
                
                if not api_key:
                    logger.debug("Google Places API key not configured")
                    return None
                
                # Build search query - try multiple variations
                # Remove common suffixes for better matching
                name_clean = council_name.lower()
                for suffix in [' county council', ' city council', ' borough council', ' council', ' london borough of', ' royal borough of']:
                    if name_clean.endswith(suffix):
                        name_clean = name_clean[:-len(suffix)].strip()
                        break
                
                # Build queries
                queries = [
                    f"{council_name} UK",  # Full name
                    f"{name_clean} council UK",  # Clean name
                    f"{council_name} local authority UK",  # With "local authority"
                ]
                
                if location:
                    queries.append(f"{council_name} {location}")
                    queries.append(f"{name_clean} council {location}")
                
                # Try each query until we find results
                for query in queries:
                
                    # Use Places API Text Search (Legacy API)
                    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                    params = {
                        'query': query,
                        'key': api_key,
                    }
                    
                    response = await self.client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('status') == 'OK' and data.get('results'):
                            # Filter results to find council offices
                            results = data.get('results', [])
                            place = None
                            
                            # Look for results that match council name and are government offices
                            for result in results:
                                name = result.get('name', '').lower()
                                types = result.get('types', [])
                                
                                # Check if it's a government office or matches council name
                                if any(t in ['local_government_office', 'city_hall', 'government_office'] for t in types):
                                    place = result
                                    break
                                elif name_clean in name or name in name_clean or council_name.lower() in name:
                                    place = result
                                    break
                            
                            # If no specific match, use first result
                            if not place and results:
                                place = results[0]
                            
                            if place:
                                place_id = place.get('place_id')
                                
                                # Get detailed information using Place Details API
                                details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                                details_params = {
                                    'place_id': place_id,
                                    'key': api_key,
                                    'fields': 'name,formatted_phone_number,international_phone_number,website,formatted_address'
                                }
                                
                                details_response = await self.client.get(details_url, params=details_params)
                                if details_response.status_code == 200:
                                    details_data = details_response.json()
                                    
                                    if details_data.get('status') == 'OK' and details_data.get('result'):
                                        result = details_data['result']
                                        
                                        # Extract contact information
                                        phone = result.get('formatted_phone_number') or result.get('international_phone_number')
                                        website = result.get('website')
                                        
                                        # Clean phone number (remove spaces, format)
                                        if phone:
                                            # Keep original format for display
                                            phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                                            # Add UK country code if missing
                                            if phone_clean.startswith('0'):
                                                phone_clean = '+44' + phone_clean[1:]
                                            elif not phone_clean.startswith('+'):
                                                phone_clean = '+44' + phone_clean
                                            # Use formatted version if available, otherwise cleaned
                                            phone = result.get('formatted_phone_number') or phone_clean
                                        
                                        logger.info(f"  ✓ Google Places found: phone={bool(phone)}, website={bool(website)}")
                                        
                                        return {
                                            'asc_phone': phone,
                                            'asc_email': None,  # Google Places doesn't provide email
                                            'asc_website_url': website,
                                            'office_address': result.get('formatted_address'),
                                            'source': 'google_places'
                                        }
                        
                        elif data.get('status') == 'ZERO_RESULTS':
                            # Try next query
                            continue
                        else:
                            logger.debug(f"Google Places API error for query '{query}': {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                            # Try next query
                            continue
                    else:
                        # Try next query
                        continue
                
                # If we get here, no queries worked
                logger.debug(f"No Google Places results for {council_name} after trying {len(queries)} queries")
                    
            except ImportError:
                logger.debug("Config manager not available for Google Places API")
                return None
                
        except Exception as e:
            logger.warning(f"Google Places API error: {e}")
        
        return None
    
    async def fetch_from_lga_directory(self, council_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch council information from Local Government Association directory
        
        Args:
            council_name: Name of the council
            
        Returns:
            Dict with contact information or None
        """
        try:
            # LGA may have a directory or API
            # This would need to be implemented based on available resources
            logger.debug("LGA directory not implemented")
            return None
        except Exception as e:
            logger.warning(f"LGA directory error: {e}")
        
        return None
    
    async def enrich_council_data(
        self, 
        council: Dict[str, Any],
        use_postcodes_io: bool = True,
        use_gov_register: bool = True,
        use_google_places: bool = True
    ) -> Dict[str, Any]:
        """
        Enrich council data from multiple external sources
        
        Args:
            council: Council data dictionary
            use_postcodes_io: Whether to use postcodes.io
            use_gov_register: Whether to use GOV.UK Register
            
        Returns:
            Enriched council data
        """
        enriched = council.copy()
        ons_code = council.get('ons_code', '')
        council_name = council.get('council_name', '')
        region = council.get('region', '')
        
        # Skip if already has complete data
        if enriched.get('asc_phone') and enriched.get('asc_email'):
            return enriched
        
        # Step 1: Try Google Places API first (most reliable for contact info)
        if use_google_places and (not enriched.get('asc_phone') or not enriched.get('asc_email')):
            try:
                location = f"{region}, UK" if region else "UK"
                logger.debug(f"  Trying Google Places for {council_name} in {location}")
                google_data = await self.fetch_from_google_places(council_name, location)
                if google_data:
                    # Merge data (don't overwrite existing)
                    if google_data.get('asc_phone') and not enriched.get('asc_phone'):
                        enriched['asc_phone'] = google_data['asc_phone']
                        logger.info(f"  ✓ Found phone from Google Places: {google_data['asc_phone']}")
                    if google_data.get('asc_email') and not enriched.get('asc_email'):
                        enriched['asc_email'] = google_data['asc_email']
                        logger.info(f"  ✓ Found email from Google Places")
                    if google_data.get('asc_website_url') and not enriched.get('asc_website_url'):
                        enriched['asc_website_url'] = google_data['asc_website_url']
                    if google_data.get('office_address') and not enriched.get('office_address'):
                        enriched['office_address'] = google_data['office_address']
                    # Preserve source information
                    if google_data.get('source') and not enriched.get('source'):
                        enriched['source'] = google_data['source']
                else:
                    logger.debug(f"  Google Places returned no data for {council_name}")
            except Exception as e:
                logger.debug(f"Google Places enrichment error: {e}")
        
        # Step 2: Try to get postcode for the council area (if we have a representative postcode)
        # This would require a mapping of councils to representative postcodes
        if use_postcodes_io and not enriched.get('asc_phone') and not enriched.get('asc_email'):
            # Try to find a representative postcode for this council
            # For now, skip as we'd need a postcode database
            pass
        
        # Step 3: Try GOV.UK Register if we have ONS code
        if use_gov_register and ons_code and (not enriched.get('asc_phone') or not enriched.get('asc_email')):
            gov_data = await self.fetch_from_gov_uk_register(ons_code)
            if gov_data:
                # Merge data (don't overwrite existing)
                if gov_data.get('website') and not enriched.get('asc_website_url'):
                    enriched['asc_website_url'] = gov_data['website']
                if gov_data.get('contact'):
                    contact = gov_data['contact']
                    if isinstance(contact, dict):
                        if contact.get('email') and not enriched.get('asc_email'):
                            enriched['asc_email'] = contact['email']
                            logger.info(f"  ✓ Found email from GOV.UK Register")
                        if contact.get('phone') and not enriched.get('asc_phone'):
                            enriched['asc_phone'] = contact['phone']
                            logger.info(f"  ✓ Found phone from GOV.UK Register")
        
        return enriched
    
    async def batch_enrich_councils(
        self,
        councils: List[Dict[str, Any]],
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Enrich multiple councils from external sources
        
        Args:
            councils: List of council dictionaries
            limit: Optional limit on number of councils to process
            
        Returns:
            List of enriched council dictionaries
        """
        if limit:
            councils = councils[:limit]
        
        enriched = []
        for i, council in enumerate(councils, 1):
            logger.info(f"Enriching {i}/{len(councils)}: {council.get('council_name', 'Unknown')}")
            
            # Only enrich if missing contact information
            if not council.get('asc_phone') and not council.get('asc_email'):
                enriched_council = await self.enrich_council_data(council)
                enriched.append(enriched_council)
            else:
                enriched.append(council)
        
        return enriched
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

