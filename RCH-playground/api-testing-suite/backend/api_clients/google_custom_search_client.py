"""
Google Custom Search API Client
For searching Indeed UK company pages using site-specific queries
Based on staff-analysis documentation approach
"""
import httpx
import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote, unquote


class GoogleCustomSearchClient:
    """Google Custom Search API Client for Indeed company discovery"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize Google Custom Search client
        
        Args:
            api_key: Google Cloud API key with Custom Search API enabled
            search_engine_id: Custom Search Engine ID (cx) configured for uk.indeed.com
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search(
        self,
        query: str,
        num_results: int = 3,
        site_restrict: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute Google Custom Search
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
            site_restrict: Optional site restriction (e.g., "uk.indeed.com")
        
        Returns:
            List of search results with url, title, snippet
        """
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(num_results, 10)
        }
        
        if site_restrict:
            params["siteSearch"] = site_restrict
            params["siteSearchFilter"] = "i"  # Include only results from site
        
        try:
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "url": item.get("link", ""),
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "display_link": item.get("displayLink", "")
                })
            
            return results
            
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = error_body.get("error", {}).get("message", str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Google Custom Search API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise Exception(f"Google Custom Search error: {str(e)}")
    
    async def search_indeed_company(
        self,
        search_term: str,
        country: str = "UK"
    ) -> List[Dict[str, Any]]:
        """
        Search for a company on Indeed using site-specific query
        
        Query format: site:uk.indeed.com "{search_term}" reviews
        
        Args:
            search_term: Company/brand name to search
            country: Country code ("UK" or "US")
        
        Returns:
            List of Indeed company results
        """
        indeed_domain = "uk.indeed.com" if country == "UK" else "indeed.com"
        query = f'site:{indeed_domain} "{search_term}" reviews'
        
        results = await self.search(query, num_results=3)
        
        # Filter to only Indeed company pages
        indeed_results = []
        for result in results:
            url = result.get("url", "")
            if "/cmp/" in url and indeed_domain in url:
                indeed_results.append(result)
        
        return indeed_results
    
    @staticmethod
    def extract_indeed_slug(url: str) -> Optional[str]:
        """
        Extract company slug from Indeed URL
        
        Examples:
            https://uk.indeed.com/cmp/Monarch-Healthcare/reviews → "Monarch-Healthcare"
            https://uk.indeed.com/cmp/B%26M-Care/reviews → "B&M-Care"
        
        Args:
            url: Indeed company URL
        
        Returns:
            Company slug or None
        """
        pattern = r"/cmp/([^/]+)"
        match = re.search(pattern, url)
        
        if match:
            slug = unquote(match.group(1))
            return slug
        
        return None
    
    @staticmethod
    def build_indeed_reviews_url(slug: str, country: str = "UK") -> str:
        """
        Build Indeed reviews URL from slug
        
        Args:
            slug: Company slug
            country: Country code
        
        Returns:
            Full Indeed reviews URL
        """
        domain = "uk.indeed.com" if country == "UK" else "indeed.com"
        encoded_slug = quote(slug, safe="-")
        return f"https://{domain}/cmp/{encoded_slug}/reviews"
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
