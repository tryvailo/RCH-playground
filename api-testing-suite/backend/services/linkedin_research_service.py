"""
LinkedIn Research Service
Uses Perplexity AI to research LinkedIn data for care homes
"""
import re
import logging
from typing import Dict, Any, Optional
from api_clients.perplexity_client import PerplexityAPIClient
from utils.cache import get_cache_manager

logger = logging.getLogger(__name__)


class LinkedInResearchService:
    """Service for researching LinkedIn data via Perplexity AI"""
    
    def __init__(self, perplexity_client: PerplexityAPIClient, use_cache: bool = True, cache_ttl: int = 1209600):
        """
        Initialize LinkedIn Research Service
        
        Args:
            perplexity_client: Perplexity API client instance
            use_cache: Whether to use Redis cache (default True)
            cache_ttl: Cache TTL in seconds (default 14 days = 1209600)
        """
        self.perplexity_client = perplexity_client
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.cache = get_cache_manager() if use_cache else None
    
    async def research_linkedin_data(
        self,
        home_name: str,
        company_name: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Research LinkedIn data for a care home using Perplexity AI
        
        Args:
            home_name: Name of the care home
            company_name: Company/provider name (optional)
            location: Location/postcode (optional)
        
        Returns:
            Dict with LinkedIn data including:
            - Staff count
            - Average tenure
            - Certifications
            - Department organization
            - Hiring patterns
            - Turnover rate estimate
        """
        try:
            # Build search query
            query = self._build_linkedin_query(home_name, company_name, location)
            
            # Search with Perplexity
            result = await self.perplexity_client.search(
                query=query,
                model="sonar-pro",
                max_tokens=1000,
                search_recency_filter="year"
            )
            
            # Parse results
            content = result.get("content", "")
            citations = result.get("citations", [])
            
            # Extract LinkedIn data
            linkedin_data = self._parse_linkedin_data(content, home_name, company_name)
            
            # Add metadata
            linkedin_data.update({
                'data_source': 'perplexity_ai',
                'query_used': query,
                'citations': citations,
                'data_quality': self._assess_data_quality(linkedin_data, citations)
            })
            
            # Cache the result
            if self.cache:
                await self.cache.set(cache_key, linkedin_data, ttl=self.cache_ttl)
            
            logger.info(f"LinkedIn research completed for {home_name}: staff_count={linkedin_data.get('staff_count')}, avg_tenure={linkedin_data.get('average_tenure_years')}")
            
            return linkedin_data
            
        except Exception as e:
            logger.error(f"Error researching LinkedIn data for {home_name}: {str(e)}")
            return self._get_default_linkedin_data(home_name)
    
    def _build_linkedin_query(
        self,
        home_name: str,
        company_name: Optional[str],
        location: Optional[str]
    ) -> str:
        """Build optimized query for Perplexity AI"""
        parts = []
        
        if company_name:
            parts.append(f'"{company_name}"')
        
        parts.append(f'"{home_name}"')
        parts.append("care home")
        
        if location:
            parts.append(location)
        
        parts.extend([
            "linkedin",
            "employees",
            "staff",
            "team size",
            "average tenure",
            "certifications",
            "qualifications",
            "hiring patterns"
        ])
        
        return " ".join(parts)
    
    def _parse_linkedin_data(
        self,
        content: str,
        home_name: str,
        company_name: Optional[str]
    ) -> Dict[str, Any]:
        """Parse LinkedIn data from Perplexity AI response"""
        data = {
            'staff_count': None,
            'average_tenure_years': None,
            'certifications': [],
            'qualification_levels': {},
            'department_breakdown': {},
            'hiring_frequency': None,
            'recent_hires_count': None,
            'turnover_rate_estimate': None,
            'key_positions': [],
            'career_progression_patterns': None
        }
        
        if not content:
            return data
        
        content_lower = content.lower()
        
        # Extract staff count
        staff_count_patterns = [
            r'(\d+)\s*(?:employee|staff|worker|team member)',
            r'staff.*?of\s*(\d+)',
            r'team.*?size.*?(\d+)',
            r'approximately\s*(\d+)\s*(?:employee|staff)',
            r'around\s*(\d+)\s*(?:employee|staff)'
        ]
        
        for pattern in staff_count_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    count = int(match.group(1))
                    if 5 <= count <= 500:  # Reasonable range for care homes
                        data['staff_count'] = count
                        break
                except ValueError:
                    continue
        
        # Extract average tenure
        tenure_patterns = [
            r'average.*?tenure.*?(\d+\.?\d*)\s*(?:year|yr)',
            r'(\d+\.?\d*)\s*(?:year|yr).*?average.*?tenure',
            r'staff.*?stay.*?(\d+\.?\d*)\s*(?:year|yr)',
            r'average.*?(\d+\.?\d*)\s*(?:year|yr).*?service'
        ]
        
        for pattern in tenure_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    years = float(match.group(1))
                    if 0.5 <= years <= 20:  # Reasonable range
                        data['average_tenure_years'] = round(years, 1)
                        break
                except ValueError:
                    continue
        
        # Extract certifications
        cert_keywords = [
            'nvq', 'rgn', 'rn', 'rmn', 'diphe', 'degree', 'certificate',
            'qualification', 'training', 'cscs', 'first aid', 'safeguarding'
        ]
        
        certifications = []
        for keyword in cert_keywords:
            if keyword in content_lower:
                # Try to extract context
                cert_match = re.search(
                    rf'{keyword}.*?(\d+%|\d+\s*(?:staff|employee|worker))',
                    content_lower
                )
                if cert_match:
                    certifications.append(keyword.upper())
        
        data['certifications'] = list(set(certifications))[:10]  # Limit to 10
        
        # Extract qualification levels
        qual_patterns = [
            r'(\d+)%.*?(?:degree|qualified|certified)',
            r'(\d+)\s*(?:staff|employee).*?(?:degree|qualified|certified)',
            r'(?:degree|qualified|certified).*?(\d+)%'
        ]
        
        qualification_levels = {}
        for pattern in qual_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                try:
                    percentage = int(match)
                    if 'degree' in content_lower:
                        qualification_levels['degree_qualified'] = percentage
                    elif 'qualified' in content_lower or 'certified' in content_lower:
                        qualification_levels['qualified'] = percentage
                except ValueError:
                    continue
        
        data['qualification_levels'] = qualification_levels
        
        # Extract department breakdown
        dept_keywords = ['nursing', 'care', 'admin', 'management', 'kitchen', 'maintenance', 'activities']
        department_breakdown = {}
        
        for dept in dept_keywords:
            dept_pattern = rf'{dept}.*?(\d+)\s*(?:staff|employee|member)'
            match = re.search(dept_pattern, content_lower)
            if match:
                try:
                    count = int(match.group(1))
                    department_breakdown[dept] = count
                except ValueError:
                    continue
        
        data['department_breakdown'] = department_breakdown
        
        # Extract hiring frequency
        hiring_patterns = [
            r'(\d+)\s*(?:new|recent).*?hire',
            r'hiring.*?(\d+)\s*(?:time|month|year)',
            r'(\d+)\s*(?:position|role).*?open'
        ]
        
        for pattern in hiring_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    count = int(match.group(1))
                    if count > 0:
                        data['recent_hires_count'] = count
                        # Estimate hiring frequency
                        if 'month' in content_lower:
                            data['hiring_frequency'] = 'monthly'
                        elif 'year' in content_lower:
                            data['hiring_frequency'] = 'yearly'
                        else:
                            data['hiring_frequency'] = 'ongoing'
                        break
                except ValueError:
                    continue
        
        # Estimate turnover rate (if we have staff count and hiring data)
        if data.get('staff_count') and data.get('recent_hires_count'):
            annual_hires = data['recent_hires_count']
            if 'month' in content_lower:
                annual_hires *= 12
            elif 'year' in content_lower:
                pass  # Already annual
            
            if annual_hires > 0 and data['staff_count'] > 0:
                turnover_rate = (annual_hires / data['staff_count']) * 100
                data['turnover_rate_estimate'] = round(min(turnover_rate, 100), 1)
        
        # Extract key positions
        position_keywords = ['manager', 'deputy', 'supervisor', 'coordinator', 'lead', 'senior']
        key_positions = []
        
        for keyword in position_keywords:
            if keyword in content_lower:
                key_positions.append(keyword.title())
        
        data['key_positions'] = list(set(key_positions))[:10]
        
        # Career progression patterns
        if 'promotion' in content_lower or 'advancement' in content_lower:
            data['career_progression_patterns'] = 'positive'
        elif 'limited' in content_lower and 'opportunity' in content_lower:
            data['career_progression_patterns'] = 'limited'
        else:
            data['career_progression_patterns'] = 'unknown'
        
        return data
    
    def _assess_data_quality(
        self,
        data: Dict[str, Any],
        citations: list
    ) -> str:
        """Assess data quality based on available data and citations"""
        has_staff_count = data.get('staff_count') is not None
        has_tenure = data.get('average_tenure_years') is not None
        has_certs = len(data.get('certifications', [])) > 0
        citation_count = len(citations) if citations else 0
        
        if has_staff_count and has_tenure and has_certs and citation_count >= 2:
            return 'high'
        elif (has_staff_count and has_tenure) or (has_staff_count and has_certs):
            return 'medium'
        elif has_staff_count or has_tenure:
            return 'low'
        else:
            return 'very_low'
    
    def _get_cache_key(self, home_name: str, company_name: Optional[str], location: Optional[str]) -> str:
        """Generate cache key for LinkedIn data"""
        key_parts = ['linkedin', home_name.lower().replace(' ', '_')]
        if company_name:
            key_parts.append(company_name.lower().replace(' ', '_'))
        if location:
            key_parts.append(location.lower().replace(' ', '_'))
        return ':'.join(key_parts)
    
    def _get_default_linkedin_data(self, home_name: str) -> Dict[str, Any]:
        """Return default LinkedIn data when research fails"""
        return {
            'staff_count': None,
            'average_tenure_years': None,
            'certifications': [],
            'qualification_levels': {},
            'department_breakdown': {},
            'hiring_frequency': None,
            'recent_hires_count': None,
            'turnover_rate_estimate': None,
            'key_positions': [],
            'career_progression_patterns': None,
            'data_source': 'perplexity_ai',
            'data_quality': 'very_low',
            'error': 'Unable to retrieve LinkedIn data'
        }

