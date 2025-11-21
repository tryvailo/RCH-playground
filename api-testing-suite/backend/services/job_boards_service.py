"""
Job Boards Service
Integrates with job boards to analyze hiring patterns and turnover signals
"""
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from utils.cache import get_cache_manager

logger = logging.getLogger(__name__)


class JobBoardsService:
    """Service for analyzing job board data for care homes"""
    
    def __init__(self, use_cache: bool = True, cache_ttl: int = 86400):
        """
        Initialize Job Boards Service
        
        Args:
            use_cache: Whether to use Redis cache (default True)
            cache_ttl: Cache TTL in seconds (default 24 hours = 86400)
        """
        self.client = httpx.AsyncClient(timeout=30.0)
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.cache = get_cache_manager() if use_cache else None
        # Note: In production, you would configure API keys for Indeed, Reed, Totaljobs, etc.
        # For now, we'll use web scraping with proper rate limiting and ToS compliance
    
    async def analyze_job_listings(
        self,
        home_name: str,
        company_name: Optional[str] = None,
        location: Optional[str] = None,
        postcode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze job listings for a care home
        
        Args:
            home_name: Name of the care home
            company_name: Company/provider name (optional)
            location: Location/city (optional)
            postcode: Postcode (optional)
        
        Returns:
            Dict with job board analysis including:
            - Active job listings count
            - Job titles & salary ranges
            - Hiring frequency
            - Department needs
            - Turnover signals
        """
        # Check cache first
        cache_key = self._get_cache_key(home_name, company_name, location, postcode)
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Job boards data retrieved from cache for {home_name}")
                return cached_data
        
        try:
            # Search multiple job boards
            indeed_results = await self._search_indeed(home_name, company_name, location, postcode)
            reed_results = await self._search_reed(home_name, company_name, location, postcode)
            totaljobs_results = await self._search_totaljobs(home_name, company_name, location, postcode)
            
            # Combine and analyze results
            all_listings = []
            all_listings.extend(indeed_results.get('listings', []))
            all_listings.extend(reed_results.get('listings', []))
            all_listings.extend(totaljobs_results.get('listings', []))
            
            # Analyze combined data
            analysis = self._analyze_listings(all_listings, home_name, company_name)
            
            # Add metadata
            analysis.update({
                'data_sources': {
                    'indeed': len(indeed_results.get('listings', [])),
                    'reed': len(reed_results.get('listings', [])),
                    'totaljobs': len(totaljobs_results.get('listings', []))
                },
                'total_listings': len(all_listings),
                'last_updated': datetime.now().isoformat()
            })
            
            # Cache the result
            if self.cache:
                await self.cache.set(cache_key, analysis, ttl=self.cache_ttl)
            
            logger.info(f"Job board analysis completed for {home_name}: {len(all_listings)} listings found")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing job listings for {home_name}: {str(e)}")
            return self._get_default_job_data(home_name)
    
    async def _search_indeed(
        self,
        home_name: str,
        company_name: Optional[str],
        location: Optional[str],
        postcode: Optional[str]
    ) -> Dict[str, Any]:
        """Search Indeed for job listings"""
        # TODO: Implement Indeed API integration or web scraping
        # For now, return empty results
        # In production, use Indeed API: https://ads.indeed.com/jobroll/xmlfeed
        
        query_parts = []
        if company_name:
            query_parts.append(company_name)
        query_parts.append(home_name)
        query_parts.append("care home")
        if location:
            query_parts.append(location)
        
        # Placeholder for actual API call
        # response = await self.client.get(
        #     "https://ads.indeed.com/jobroll/xmlfeed",
        #     params={
        #         "publisher": "YOUR_PUBLISHER_ID",
        #         "q": " ".join(query_parts),
        #         "l": location or postcode or "",
        #         "radius": 25,
        #         "limit": 50
        #     }
        # )
        
        return {
            'listings': [],
            'source': 'indeed',
            'status': 'not_implemented'
        }
    
    async def _search_reed(
        self,
        home_name: str,
        company_name: Optional[str],
        location: Optional[str],
        postcode: Optional[str]
    ) -> Dict[str, Any]:
        """Search Reed for job listings"""
        # TODO: Implement Reed API integration
        # Reed API: https://www.reed.co.uk/api/
        
        return {
            'listings': [],
            'source': 'reed',
            'status': 'not_implemented'
        }
    
    async def _search_totaljobs(
        self,
        home_name: str,
        company_name: Optional[str],
        location: Optional[str],
        postcode: Optional[str]
    ) -> Dict[str, Any]:
        """Search Totaljobs for job listings"""
        # TODO: Implement Totaljobs API integration or web scraping
        
        return {
            'listings': [],
            'source': 'totaljobs',
            'status': 'not_implemented'
        }
    
    def _analyze_listings(
        self,
        listings: List[Dict[str, Any]],
        home_name: str,
        company_name: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze job listings to extract insights"""
        if not listings:
            return {
                'active_listings_count': 0,
                'job_titles': [],
                'salary_ranges': {},
                'hiring_frequency': 'unknown',
                'department_needs': {},
                'turnover_signals': [],
                'urgency_indicators': []
            }
        
        # Extract job titles
        job_titles = []
        for listing in listings:
            title = listing.get('title', '')
            if title:
                job_titles.append(title)
        
        # Count by department
        department_needs = {}
        for title in job_titles:
            title_lower = title.lower()
            if 'nurse' in title_lower or 'rgn' in title_lower or 'rmn' in title_lower:
                department_needs['nursing'] = department_needs.get('nursing', 0) + 1
            elif 'care' in title_lower and 'assistant' in title_lower:
                department_needs['care'] = department_needs.get('care', 0) + 1
            elif 'manager' in title_lower or 'supervisor' in title_lower:
                department_needs['management'] = department_needs.get('management', 0) + 1
            elif 'kitchen' in title_lower or 'cook' in title_lower:
                department_needs['kitchen'] = department_needs.get('kitchen', 0) + 1
            elif 'admin' in title_lower or 'administrator' in title_lower:
                department_needs['administration'] = department_needs.get('administration', 0) + 1
            elif 'activities' in title_lower or 'coordinator' in title_lower:
                department_needs['activities'] = department_needs.get('activities', 0) + 1
        
        # Extract salary ranges
        salary_ranges = {}
        for listing in listings:
            salary = listing.get('salary', '')
            if salary:
                # Parse salary range
                salary_match = re.search(r'£?(\d+)[kK]?\s*[-–]\s*£?(\d+)[kK]?', salary)
                if salary_match:
                    min_sal = int(salary_match.group(1))
                    max_sal = int(salary_match.group(2))
                    if 'k' in salary.lower():
                        min_sal *= 1000
                        max_sal *= 1000
                    salary_ranges[listing.get('title', 'Unknown')] = {
                        'min': min_sal,
                        'max': max_sal
                    }
        
        # Analyze hiring frequency
        posting_dates = [listing.get('posted_date') for listing in listings if listing.get('posted_date')]
        if posting_dates:
            # Count listings per month
            recent_listings = [d for d in posting_dates if self._is_recent(d, days=30)]
            if len(recent_listings) >= 5:
                hiring_frequency = 'very_high'
            elif len(recent_listings) >= 3:
                hiring_frequency = 'high'
            elif len(recent_listings) >= 1:
                hiring_frequency = 'moderate'
            else:
                hiring_frequency = 'low'
        else:
            hiring_frequency = 'unknown'
        
        # Identify turnover signals
        turnover_signals = []
        if len(listings) >= 5:
            turnover_signals.append('high_number_of_openings')
        if 'urgent' in ' '.join(job_titles).lower():
            turnover_signals.append('urgent_hiring')
        if department_needs.get('nursing', 0) >= 3:
            turnover_signals.append('nursing_staff_shortage')
        if department_needs.get('care', 0) >= 5:
            turnover_signals.append('care_staff_shortage')
        
        # Urgency indicators
        urgency_indicators = []
        for listing in listings:
            if listing.get('urgent', False):
                urgency_indicators.append('urgent_flag')
            if 'immediate' in listing.get('title', '').lower():
                urgency_indicators.append('immediate_start')
            if 'asap' in listing.get('description', '').lower():
                urgency_indicators.append('asap_required')
        
        return {
            'active_listings_count': len(listings),
            'job_titles': list(set(job_titles))[:20],  # Limit to 20 unique titles
            'salary_ranges': salary_ranges,
            'hiring_frequency': hiring_frequency,
            'department_needs': department_needs,
            'turnover_signals': list(set(turnover_signals)),
            'urgency_indicators': list(set(urgency_indicators)),
            'recent_postings_count': len(recent_listings) if posting_dates else 0
        }
    
    def _is_recent(self, date_str: str, days: int = 30) -> bool:
        """Check if a date is within the specified number of days"""
        try:
            # Try various date formats
            date_formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    delta = datetime.now() - date_obj
                    return delta.days <= days
                except ValueError:
                    continue
            
            return False
        except Exception:
            return False
    
    def _get_cache_key(
        self,
        home_name: str,
        company_name: Optional[str],
        location: Optional[str],
        postcode: Optional[str]
    ) -> str:
        """Generate cache key for job boards data"""
        key_parts = ['job_boards', home_name.lower().replace(' ', '_')]
        if company_name:
            key_parts.append(company_name.lower().replace(' ', '_'))
        if location:
            key_parts.append(location.lower().replace(' ', '_'))
        if postcode:
            key_parts.append(postcode.lower().replace(' ', '_'))
        return ':'.join(key_parts)
    
    def _get_default_job_data(self, home_name: str) -> Dict[str, Any]:
        """Return default job board data when analysis fails"""
        return {
            'active_listings_count': 0,
            'job_titles': [],
            'salary_ranges': {},
            'hiring_frequency': 'unknown',
            'department_needs': {},
            'turnover_signals': [],
            'urgency_indicators': [],
            'data_sources': {
                'indeed': 0,
                'reed': 0,
                'totaljobs': 0
            },
            'total_listings': 0,
            'last_updated': datetime.now().isoformat(),
            'error': 'Unable to retrieve job board data'
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

