"""
Glassdoor Research Service
Uses Perplexity AI to research Glassdoor data for care homes
"""
import re
import logging
from typing import Dict, Any, Optional
from api_clients.perplexity_client import PerplexityAPIClient

logger = logging.getLogger(__name__)


class GlassdoorResearchService:
    """Service for researching Glassdoor data via Perplexity AI"""
    
    def __init__(self, perplexity_client: PerplexityAPIClient, use_cache: bool = True, cache_ttl: int = 1209600):
        """
        Initialize Glassdoor Research Service
        
        Args:
            perplexity_client: Perplexity API client instance
            use_cache: Whether to use Redis cache (default True)
            cache_ttl: Cache TTL in seconds (default 14 days = 1209600)
        """
        self.perplexity_client = perplexity_client
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.cache = get_cache_manager() if use_cache else None
    
    async def research_glassdoor_data(
        self,
        home_name: str,
        company_name: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Research Glassdoor data for a care home using Perplexity AI
        
        Args:
            home_name: Name of the care home
            company_name: Company/provider name (optional)
            location: Location/postcode (optional)
        
        Returns:
            Dict with Glassdoor data including:
            - Employee satisfaction rating (1-5)
            - Review count
            - Management score
            - Work-life balance score
            - Staff comments & sentiment
            - Turnover insights
        """
        # Check cache first
        cache_key = self._get_cache_key(home_name, company_name, location)
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Glassdoor data retrieved from cache for {home_name}")
                return cached_data
        
        try:
            # Build search query
            query = self._build_glassdoor_query(home_name, company_name, location)
            
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
            
            # Extract Glassdoor data
            glassdoor_data = self._parse_glassdoor_data(content, home_name, company_name)
            
            # Add metadata
            glassdoor_data.update({
                'data_source': 'perplexity_ai',
                'query_used': query,
                'citations': citations,
                'data_quality': self._assess_data_quality(glassdoor_data, citations)
            })
            
            # Cache the result
            if self.cache:
                await self.cache.set(cache_key, glassdoor_data, ttl=self.cache_ttl)
            
            logger.info(f"Glassdoor research completed for {home_name}: rating={glassdoor_data.get('rating')}, reviews={glassdoor_data.get('review_count')}")
            
            return glassdoor_data
            
        except Exception as e:
            logger.error(f"Error researching Glassdoor data for {home_name}: {str(e)}")
            return self._get_default_glassdoor_data(home_name)
    
    def _build_glassdoor_query(
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
            "glassdoor",
            "employee reviews",
            "staff satisfaction",
            "work-life balance",
            "management rating"
        ])
        
        return " ".join(parts)
    
    def _parse_glassdoor_data(
        self,
        content: str,
        home_name: str,
        company_name: Optional[str]
    ) -> Dict[str, Any]:
        """Parse Glassdoor data from Perplexity AI response"""
        data = {
            'rating': None,
            'review_count': None,
            'management_score': None,
            'work_life_balance_score': None,
            'culture_score': None,
            'career_opportunities_score': None,
            'compensation_score': None,
            'positive_sentiment': None,
            'negative_sentiment': None,
            'neutral_sentiment': None,
            'key_themes': [],
            'turnover_mentions': None,
            'staff_comments': [],
            'last_updated': None
        }
        
        if not content:
            return data
        
        content_lower = content.lower()
        
        # Extract rating (1-5 scale)
        rating_patterns = [
            r'glassdoor.*?rating.*?(\d+\.?\d*)\s*(?:out of|/)\s*5',
            r'employee.*?satisfaction.*?(\d+\.?\d*)\s*(?:out of|/)\s*5',
            r'(\d+\.?\d*)\s*(?:star|point).*?glassdoor',
            r'glassdoor.*?(\d+\.?\d*)\s*(?:star|point)'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    rating = float(match.group(1))
                    if 1.0 <= rating <= 5.0:
                        data['rating'] = round(rating, 2)
                        break
                except ValueError:
                    continue
        
        # Extract review count
        review_count_patterns = [
            r'(\d+)\s*(?:employee|staff|review).*?glassdoor',
            r'glassdoor.*?(\d+)\s*(?:review|rating)',
            r'(\d+)\s*(?:review|rating).*?submitted'
        ]
        
        for pattern in review_count_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    count = int(match.group(1))
                    if count > 0:
                        data['review_count'] = count
                        break
                except ValueError:
                    continue
        
        # Extract management score
        mgmt_patterns = [
            r'management.*?(\d+\.?\d*)\s*(?:out of|/)\s*5',
            r'management.*?rating.*?(\d+\.?\d*)',
            r'(\d+\.?\d*).*?management.*?score'
        ]
        
        for pattern in mgmt_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    score = float(match.group(1))
                    if 1.0 <= score <= 5.0:
                        data['management_score'] = round(score, 2)
                        break
                except ValueError:
                    continue
        
        # Extract work-life balance score
        wlb_patterns = [
            r'work[- ]life.*?balance.*?(\d+\.?\d*)\s*(?:out of|/)\s*5',
            r'work[- ]life.*?balance.*?rating.*?(\d+\.?\d*)',
            r'(\d+\.?\d*).*?work[- ]life.*?balance'
        ]
        
        for pattern in wlb_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    score = float(match.group(1))
                    if 1.0 <= score <= 5.0:
                        data['work_life_balance_score'] = round(score, 2)
                        break
                except ValueError:
                    continue
        
        # Extract culture score
        culture_patterns = [
            r'culture.*?(\d+\.?\d*)\s*(?:out of|/)\s*5',
            r'culture.*?rating.*?(\d+\.?\d*)',
            r'(\d+\.?\d*).*?culture.*?score'
        ]
        
        for pattern in culture_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    score = float(match.group(1))
                    if 1.0 <= score <= 5.0:
                        data['culture_score'] = round(score, 2)
                        break
                except ValueError:
                    continue
        
        # Extract sentiment indicators
        positive_keywords = ['positive', 'good', 'great', 'excellent', 'satisfied', 'happy', 'recommend']
        negative_keywords = ['negative', 'poor', 'bad', 'terrible', 'dissatisfied', 'unhappy', 'complaint']
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in content_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in content_lower)
        total_sentiment = positive_count + negative_count
        
        if total_sentiment > 0:
            data['positive_sentiment'] = round((positive_count / total_sentiment) * 100, 1)
            data['negative_sentiment'] = round((negative_count / total_sentiment) * 100, 1)
            data['neutral_sentiment'] = round(100 - data['positive_sentiment'] - data['negative_sentiment'], 1)
        
        # Extract key themes
        themes = []
        if 'turnover' in content_lower or 'staff retention' in content_lower:
            themes.append('turnover_concerns')
            data['turnover_mentions'] = True
        if 'management' in content_lower and ('poor' in content_lower or 'bad' in content_lower):
            themes.append('management_issues')
        if 'workload' in content_lower or 'understaffed' in content_lower:
            themes.append('workload_concerns')
        if 'training' in content_lower and ('good' in content_lower or 'excellent' in content_lower):
            themes.append('good_training')
        if 'benefits' in content_lower and ('good' in content_lower or 'competitive' in content_lower):
            themes.append('good_benefits')
        
        data['key_themes'] = themes
        
        # Extract sample comments (if mentioned)
        comment_patterns = [
            r'"([^"]{20,200})"',
            r'review.*?:.*?([^\.]{20,200})',
            r'employee.*?said.*?:.*?([^\.]{20,200})'
        ]
        
        comments = []
        for pattern in comment_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            comments.extend(matches[:3])  # Limit to 3 comments
        
        data['staff_comments'] = comments[:5]  # Limit to 5 total
        
        return data
    
    def _assess_data_quality(
        self,
        data: Dict[str, Any],
        citations: list
    ) -> str:
        """Assess data quality based on available data and citations"""
        has_rating = data.get('rating') is not None
        has_review_count = data.get('review_count') is not None
        has_scores = any([
            data.get('management_score'),
            data.get('work_life_balance_score'),
            data.get('culture_score')
        ])
        citation_count = len(citations) if citations else 0
        
        if has_rating and has_review_count and has_scores and citation_count >= 2:
            return 'high'
        elif has_rating and (has_review_count or has_scores):
            return 'medium'
        elif has_rating or has_review_count:
            return 'low'
        else:
            return 'very_low'
    
    def _get_cache_key(self, home_name: str, company_name: Optional[str], location: Optional[str]) -> str:
        """Generate cache key for Glassdoor data"""
        key_parts = ['glassdoor', home_name.lower().replace(' ', '_')]
        if company_name:
            key_parts.append(company_name.lower().replace(' ', '_'))
        if location:
            key_parts.append(location.lower().replace(' ', '_'))
        return ':'.join(key_parts)
    
    def _get_default_glassdoor_data(self, home_name: str) -> Dict[str, Any]:
        """Return default Glassdoor data when research fails"""
        return {
            'rating': None,
            'review_count': None,
            'management_score': None,
            'work_life_balance_score': None,
            'culture_score': None,
            'positive_sentiment': None,
            'negative_sentiment': None,
            'neutral_sentiment': None,
            'key_themes': [],
            'turnover_mentions': None,
            'staff_comments': [],
            'last_updated': None,
            'data_source': 'perplexity_ai',
            'data_quality': 'very_low',
            'error': 'Unable to retrieve Glassdoor data'
        }

