"""
CQC API Client
Care Quality Commission API integration
Based on cqcr R package functionality
"""
import httpx
from typing import List, Dict, Optional, Union
import os
from urllib.parse import urlencode, quote
import re


def _to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _build_query_params(params: Dict[str, Optional[Union[str, List[str]]]]) -> str:
    """Build query string from parameters, handling arrays"""
    query_parts = []
    
    for key, value in params.items():
        if value is None:
            continue
        
        camel_key = _to_camel_case(key)
        
        if isinstance(value, list):
            # For arrays, CQC API accepts multiple values as comma-separated or repeated params
            # Based on R code, it seems to use comma-separated
            query_parts.append(f"{camel_key}={quote(','.join(str(v) for v in value))}")
        else:
            query_parts.append(f"{camel_key}={quote(str(value))}")
    
    return '&'.join(query_parts)


class CQCAPIClient:
    """Enhanced CQC API Client with full functionality from cqcr R package
    
    Updated for new CQC API (2024-2025):
    - Uses new base URL: https://api.service.cqc.org.uk/public/v1
    - Requires subscription key authentication via Ocp-Apim-Subscription-Key header
    - Supports primary and secondary subscription keys for rotation
    """
    
    def __init__(
        self, 
        partner_code: Optional[str] = None,
        primary_subscription_key: Optional[str] = None,
        secondary_subscription_key: Optional[str] = None
    ):
        # New API base URL (migrated to Azure API Management)
        self.base_url = "https://api.service.cqc.org.uk/public/v1"
        
        # Legacy partner code (deprecated, kept for backward compatibility)
        self.partner_code = partner_code or os.getenv("CQC_PARTNER_CODE")
        
        # New subscription keys (required for new API)
        self.primary_subscription_key = (
            primary_subscription_key or 
            os.getenv("CQC_PRIMARY_SUBSCRIPTION_KEY")
        )
        self.secondary_subscription_key = (
            secondary_subscription_key or 
            os.getenv("CQC_SECONDARY_SUBSCRIPTION_KEY")
        )
        
        # Use primary key by default, fallback to secondary if primary fails
        self.current_subscription_key = self.primary_subscription_key
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with subscription key authentication"""
        headers = {"Accept": "application/json"}
        
        # Use subscription key if available (new API requirement)
        if self.current_subscription_key:
            headers["Ocp-Apim-Subscription-Key"] = self.current_subscription_key
        elif self.partner_code:
            # Fallback to legacy partner code (deprecated)
            pass  # Partner code goes in query params, not headers
        
        return headers
    
    def _add_partner_code(self, params: Dict) -> Dict:
        """Add partner code to params if available (legacy support)"""
        # Partner code is deprecated but still supported for backward compatibility
        if self.partner_code and not self.current_subscription_key:
            params["partnerCode"] = self.partner_code
        return params
    
    def _switch_to_secondary_key(self):
        """Switch to secondary subscription key if primary fails"""
        if self.secondary_subscription_key and self.current_subscription_key == self.primary_subscription_key:
            self.current_subscription_key = self.secondary_subscription_key
            return True
        return False
    
    async def _get_paginated_data(
        self,
        endpoint: str,
        params: Dict,
        data_key: str,
        page_size: int = 500,
        verbose: bool = True,
        max_pages: Optional[int] = None
    ) -> List[Dict]:
        """Handle paginated API responses
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            data_key: Key in response JSON containing the data array
            page_size: Number of items per page
            verbose: Print progress messages
            max_pages: Maximum number of pages to fetch (None = all pages)
        """
        all_data = []
        page = 1
        
        # Add pagination params
        paginated_params = params.copy()
        paginated_params["perPage"] = page_size
        paginated_params["page"] = page
        
        while True:
            paginated_params["page"] = page
            
            # Check max_pages limit
            if max_pages is not None and page > max_pages:
                break
            
            try:
                response = await self.client.get(
                    f"{self.base_url}/{endpoint}",
                    params=self._add_partner_code(paginated_params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract the data array
                items = data.get(data_key, [])
                if not items:
                    break
                
                all_data.extend(items)
                
                # Check if there are more pages
                total_pages = data.get("totalPages", 1)
                if verbose and total_pages > 1:
                    print(f"Downloading page {page} of {total_pages}")
                
                if page >= total_pages:
                    break
                
                page += 1
                
            except httpx.HTTPStatusError as e:
                # Handle 401/403 - try secondary key if available
                if e.response.status_code in (401, 403):
                    if self._switch_to_secondary_key():
                        # Retry with secondary key
                        response = await self.client.get(
                            f"{self.base_url}/{endpoint}",
                            params=self._add_partner_code(paginated_params),
                            headers=self._get_headers()
                        )
                        response.raise_for_status()
                        data = response.json()
                        items = data.get(data_key, [])
                        if not items:
                            break
                        all_data.extend(items)
                        total_pages = data.get("totalPages", 1)
                        if verbose and total_pages > 1:
                            print(f"Downloading page {page} of {total_pages}")
                        if page >= total_pages:
                            break
                        page += 1
                        # Check max_pages limit after retry
                        if max_pages is not None and page > max_pages:
                            break
                        continue
                    
                    # No secondary key or it also failed
                    error_msg = "CQC API returned 403 Forbidden. "
                    if not self.current_subscription_key and not self.partner_code:
                        error_msg += "Subscription key is required. Please register at https://api-portal.service.cqc.org.uk/ to get a subscription key, then add it in API Configuration."
                    elif self.current_subscription_key:
                        error_msg += f"Subscription key may be invalid or expired. Please check your keys at https://api-portal.service.cqc.org.uk/"
                    else:
                        error_msg += f"Partner Code may be invalid or expired. Current code: {self.partner_code[:10]}..."
                    raise Exception(error_msg)
                
                # Handle rate limiting (429)
                if e.response.status_code == 429:
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        import asyncio
                        await asyncio.sleep(int(retry_after))
                        continue
                    raise Exception(f"CQC API rate limit exceeded. Please wait before retrying.")
                
                raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                raise Exception(f"CQC API error: {str(e)}")
        
        return all_data
    
    async def search_locations(
        self,
        care_home: Optional[bool] = None,
        onspd_ccg_code: Optional[Union[str, List[str]]] = None,
        onspd_ccg_name: Optional[Union[str, List[str]]] = None,
        ods_ccg_code: Optional[Union[str, List[str]]] = None,
        ods_ccg_name: Optional[Union[str, List[str]]] = None,
        gac_service_type_description: Optional[Union[str, List[str]]] = None,
        constituency: Optional[Union[str, List[str]]] = None,
        local_authority: Optional[Union[str, List[str]]] = None,
        inspection_directorate: Optional[Union[str, List[str]]] = None,
        primary_inspection_category_code: Optional[Union[str, List[str]]] = None,
        primary_inspection_category_name: Optional[Union[str, List[str]]] = None,
        non_primary_inspection_category_code: Optional[Union[str, List[str]]] = None,
        non_primary_inspection_category_name: Optional[Union[str, List[str]]] = None,
        overall_rating: Optional[Union[str, List[str]]] = None,
        region: Optional[Union[str, List[str]]] = None,
        regulated_activity: Optional[Union[str, List[str]]] = None,
        report_type: Optional[Union[str, List[str]]] = None,
        page_size: int = 500,
        verbose: bool = True,
        max_pages: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for CQC locations with comprehensive filtering options.
        
        Based on cqc_locations_search from cqcr R package.
        
        Args:
            care_home: If True, only care homes. If False, excludes care homes. None returns all.
            onspd_ccg_code: ONSPD CCG code filter
            onspd_ccg_name: ONSPD CCG name filter
            ods_ccg_code: ODS CCG code filter
            ods_ccg_name: ODS CCG name filter
            gac_service_type_description: GAC Service Type Description filter
            constituency: Parliamentary constituency filter
            local_authority: Local authority filter
            inspection_directorate: Inspection directorate filter (e.g., "Adult social care", "Hospitals")
            primary_inspection_category_code: Primary inspection category code (e.g., "H1")
            primary_inspection_category_name: Primary inspection category name
            non_primary_inspection_category_code: Non-primary inspection category code
            non_primary_inspection_category_name: Non-primary inspection category name
            overall_rating: Overall rating filter (e.g., "Good", "Outstanding")
            region: Region filter (e.g., "London", "South East")
            regulated_activity: Regulated activity filter
            report_type: Report type filter ("Location", "Provider", "CoreService")
            page_size: Number of records per page (default 500)
            verbose: Print progress messages
        
        Returns:
            List of location dictionaries
        """
        params = {}
        
        # Handle care_home parameter
        if care_home is True:
            params["careHome"] = "Y"
        elif care_home is False:
            params["careHome"] = "N"
        
        # Add all filter parameters (convert snake_case to camelCase for API)
        filter_params = {
            "onspd_ccg_code": onspd_ccg_code,
            "onspd_ccg_name": onspd_ccg_name,
            "ods_ccg_code": ods_ccg_code,
            "ods_ccg_name": ods_ccg_name,
            "gac_service_type_description": gac_service_type_description,
            "constituency": constituency,
            "local_authority": local_authority,
            "inspection_directorate": inspection_directorate,
            "primary_inspection_category_code": primary_inspection_category_code,
            "primary_inspection_category_name": primary_inspection_category_name,
            "non_primary_inspection_category_code": non_primary_inspection_category_code,
            "non_primary_inspection_category_name": non_primary_inspection_category_name,
            "overall_rating": overall_rating,
            "region": region,
            "regulated_activity": regulated_activity,
            "report_type": report_type,
        }
        
        # Add non-None filter params (convert to camelCase for CQC API)
        for key, value in filter_params.items():
            if value is not None:
                camel_key = _to_camel_case(key)
                params[camel_key] = value
        
        return await self._get_paginated_data(
            "locations",
            params,
            "locations",
            page_size=page_size,
            verbose=verbose,
            max_pages=max_pages
        )
    
    async def search_care_homes(
        self,
        region: str = "South East",
        per_page: int = 100,
        page: int = 1,
        care_home: bool = True,
        **kwargs
    ) -> List[Dict]:
        """
        Search for care homes (backward compatibility wrapper).
        
        Use search_locations() for more advanced filtering.
        """
        results = await self.search_locations(
            care_home=care_home,
            region=region,
            page_size=per_page,
            verbose=False
        )
        # Apply pagination manually for backward compatibility
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        return results[start_idx:end_idx]
    
    async def get_location(self, location_id: str) -> Dict:
        """
        Get detailed information for a specific location.
        
        Based on cqc_location from cqcr R package.
        """
        params = {}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/locations/{location_id}",
                params=self._add_partner_code(params),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                response = await self.client.get(
                    f"{self.base_url}/locations/{location_id}",
                    params=self._add_partner_code(params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_location_details(self, location_id: str) -> Dict:
        """Alias for get_location (backward compatibility)"""
        return await self.get_location(location_id)
    
    async def get_location_inspection_areas(self, location_id: str) -> List[Dict]:
        """
        Get inspection areas for a specific location.
        
        Based on cqc_location_inspection_area from cqcr R package.
        """
        params = {}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/locations/{location_id}/inspection-areas",
                params=self._add_partner_code(params),
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            return data.get("inspectionAreas", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                response = await self.client.get(
                    f"{self.base_url}/locations/{location_id}/inspection-areas",
                    params=self._add_partner_code(params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return data.get("inspectionAreas", [])
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_location_reports(self, location_id: str) -> List[Dict]:
        """
        Get inspection reports metadata for a location.
        
        Note: In the new CQC API, reports are included in the location object itself,
        not available via a separate endpoint. This method gets the location and extracts reports.
        
        Use get_report() to get actual report content.
        """
        try:
            # Get location details which includes reports array
            location = await self.get_location(location_id)
            return location.get("reports", [])
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_report(
        self,
        inspection_report_link_id: str,
        related_document_type: Optional[str] = None,
        plain_text: bool = True
    ) -> Union[str, bytes]:
        """
        Get an inspection report as plain text or PDF.
        
        Based on cqc_reports from cqcr R package.
        
        Args:
            inspection_report_link_id: The ID of the report
            related_document_type: Optional related document type (e.g., "Use%20of%20Resources")
            plain_text: If True, returns plain text. If False, returns PDF bytes.
        
        Returns:
            Plain text string or PDF bytes
        """
        endpoint = f"reports/{inspection_report_link_id}"
        if related_document_type:
            endpoint += f"/{related_document_type}"
        
        headers = self._get_headers()
        headers["Accept"] = "text/plain" if plain_text else "application/pdf"
        
        try:
            response = await self.client.get(
                f"{self.base_url}/{endpoint}",
                params=self._add_partner_code({}),
                headers=headers
            )
            response.raise_for_status()
            
            if plain_text:
                return response.text
            else:
                return response.content
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                headers = self._get_headers()
                headers["Accept"] = "text/plain" if plain_text else "application/pdf"
                response = await self.client.get(
                    f"{self.base_url}/{endpoint}",
                    params=self._add_partner_code({}),
                    headers=headers
                )
                response.raise_for_status()
                if plain_text:
                    return response.text
                else:
                    return response.content
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def search_providers(
        self,
        constituency: Optional[Union[str, List[str]]] = None,
        local_authority: Optional[Union[str, List[str]]] = None,
        inspection_directorate: Optional[Union[str, List[str]]] = None,
        non_primary_inspection_category_code: Optional[Union[str, List[str]]] = None,
        non_primary_inspection_category_name: Optional[Union[str, List[str]]] = None,
        primary_inspection_category_code: Optional[Union[str, List[str]]] = None,
        primary_inspection_category_name: Optional[Union[str, List[str]]] = None,
        overall_rating: Optional[Union[str, List[str]]] = None,
        region: Optional[Union[str, List[str]]] = None,
        regulated_activity: Optional[Union[str, List[str]]] = None,
        report_type: Optional[Union[str, List[str]]] = None,
        page_size: int = 500,
        verbose: bool = True,
        max_pages: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for CQC providers with filtering options.
        
        Based on cqc_providers from cqcr R package.
        
        Note: CQC API expects parameters in camelCase format.
        """
        # Build filter params in snake_case (internal)
        filter_params = {
            "constituency": constituency,
            "local_authority": local_authority,
            "inspection_directorate": inspection_directorate,
            "non_primary_inspection_category_code": non_primary_inspection_category_code,
            "non_primary_inspection_category_name": non_primary_inspection_category_name,
            "primary_inspection_category_code": primary_inspection_category_code,
            "primary_inspection_category_name": primary_inspection_category_name,
            "overall_rating": overall_rating,
            "region": region,
            "regulated_activity": regulated_activity,
            "report_type": report_type,
        }
        
        # Convert to camelCase for CQC API
        params = {}
        for key, value in filter_params.items():
            if value is not None:
                camel_key = _to_camel_case(key)
                params[camel_key] = value
        
        return await self._get_paginated_data(
            "providers",
            params,
            "providers",
            page_size=page_size,
            verbose=verbose,
            max_pages=max_pages
        )
    
    async def get_provider(self, provider_id: str) -> Dict:
        """
        Get detailed information for a specific provider.
        
        Based on cqc_provider from cqcr R package.
        """
        params = {}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/providers/{provider_id}",
                params=self._add_partner_code(params),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                response = await self.client.get(
                    f"{self.base_url}/providers/{provider_id}",
                    params=self._add_partner_code(params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_provider_locations(self, provider_id: str) -> List[Dict]:
        """
        Get all locations for a specific provider.
        
        Based on cqc_provider_locations from cqcr R package.
        """
        params = {}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/providers/{provider_id}/locations",
                params=self._add_partner_code(params),
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            return data.get("locations", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                response = await self.client.get(
                    f"{self.base_url}/providers/{provider_id}/locations",
                    params=self._add_partner_code(params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return data.get("locations", [])
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_provider_inspection_areas(self, provider_id: str) -> List[Dict]:
        """
        Get inspection areas for a specific provider.
        
        Based on cqc_provider_inspection_areas from cqcr R package.
        """
        params = {}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/providers/{provider_id}/inspection-areas",
                params=self._add_partner_code(params),
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            return data.get("inspectionAreas", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                response = await self.client.get(
                    f"{self.base_url}/providers/{provider_id}/inspection-areas",
                    params=self._add_partner_code(params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return data.get("inspectionAreas", [])
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_inspection_areas(self) -> List[Dict]:
        """
        Get all CQC inspection areas.
        
        Based on cqc_inspection_areas from cqcr R package.
        """
        params = {}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/inspection-areas",
                params=self._add_partner_code(params),
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            return data.get("inspectionAreas", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403) and self._switch_to_secondary_key():
                response = await self.client.get(
                    f"{self.base_url}/inspection-areas",
                    params=self._add_partner_code(params),
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return data.get("inspectionAreas", [])
            raise Exception(f"CQC API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"CQC API error: {str(e)}")
    
    async def get_changes(
        self,
        organisation_type: str = "location",
        start_date: str = "2000-01-01",
        end_date: Optional[str] = None,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Get changes for providers or locations in a date range.
        
        Based on cqc_changes from cqcr R package.
        
        Args:
            organisation_type: "provider" or "location"
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (defaults to today)
            verbose: Print progress messages
        
        Returns:
            List of change records
        """
        from datetime import datetime
        
        # Parse dates - handle YYYY-MM-DD format
        try:
            if 'T' in start_date:
                start_ts = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_ts = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            # Try to parse as ISO format
            start_ts = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        if end_date:
            try:
                if 'T' in end_date:
                    end_ts = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_ts = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                end_ts = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_ts = datetime.now()
        
        # Format as ISO8601 with Z suffix (midnight UTC for date-only inputs)
        if 'T' not in start_date:
            start_ts = start_ts.replace(hour=0, minute=0, second=0, microsecond=0)
        if end_date and 'T' not in end_date:
            end_ts = end_ts.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        start_timestamp = start_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_timestamp = end_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        params = {
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp
        }
        
        endpoint = f"changes/{organisation_type.lower()}"
        
        return await self._get_paginated_data(
            endpoint,
            params,
            "changes",
            page_size=500,
            verbose=verbose
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
