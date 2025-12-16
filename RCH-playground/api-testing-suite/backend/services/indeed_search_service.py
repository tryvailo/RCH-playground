"""
Indeed Search Service
Implements the exact search process from staff-analysis documentation:
1. Google Custom Search to find Indeed company pages
2. Validation of results (city match, domain check)
3. Firecrawl scraping of Indeed reviews
4. OpenAI structured extraction of review data
"""
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from api_clients.google_custom_search_client import GoogleCustomSearchClient
from api_clients.firecrawl_client import FirecrawlAPIClient

logger = logging.getLogger(__name__)


class IndeedSearchService:
    """Service for searching and scraping Indeed company reviews"""
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        google_search_engine_id: Optional[str] = None,
        firecrawl_client: Optional[FirecrawlAPIClient] = None,
        openai_client: Optional[Any] = None
    ):
        """
        Initialize Indeed Search Service
        
        Args:
            google_api_key: Google Cloud API key
            google_search_engine_id: Google Custom Search Engine ID
            firecrawl_client: Optional Firecrawl client for scraping
            openai_client: Optional OpenAI client for structured extraction
        """
        self.google_client = None
        if google_api_key and google_search_engine_id:
            self.google_client = GoogleCustomSearchClient(
                api_key=google_api_key,
                search_engine_id=google_search_engine_id
            )
        
        self.firecrawl_client = firecrawl_client
        self.openai_client = openai_client
    
    async def find_indeed_company(
        self,
        search_term: str,
        expected_city: Optional[str] = None,
        expected_postcode: Optional[str] = None,
        country: str = "UK"
    ) -> Dict[str, Any]:
        """
        Find Indeed company page using Google Custom Search
        Implements the exact algorithm from staff-analysis documentation
        
        Args:
            search_term: Company/brand name to search
            expected_city: Expected city for validation
            expected_postcode: Expected postcode for validation
            country: Country code
        
        Returns:
            {
                "found": bool,
                "indeed_slug": str or None,
                "indeed_url": str or None,
                "title": str or None,
                "snippet": str or None,
                "validation": dict,
                "error": str or None
            }
        """
        if not self.google_client:
            return {
                "found": False,
                "error": "Google Custom Search not configured. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID."
            }
        
        logger.info(f"🔍 Searching Indeed for: {search_term}")
        
        try:
            # Step 1: Search Indeed via Google Custom Search
            results = await self.google_client.search_indeed_company(
                search_term=search_term,
                country=country
            )
            
            if not results:
                return {
                    "found": False,
                    "search_term": search_term,
                    "error": "No search results found on Indeed"
                }
            
            # Step 2: Take first result (highest ranked)
            first_result = results[0]
            url = first_result.get("url", "")
            title = first_result.get("title", "")
            snippet = first_result.get("snippet", "")
            
            # Step 3: Extract slug
            slug = GoogleCustomSearchClient.extract_indeed_slug(url)
            
            if not slug:
                return {
                    "found": False,
                    "search_term": search_term,
                    "url": url,
                    "error": "Could not extract Indeed slug from URL"
                }
            
            # Step 4: Validate result
            validation = self._validate_company_match(
                url=url,
                title=title,
                snippet=snippet,
                expected_city=expected_city,
                expected_postcode=expected_postcode,
                search_term=search_term
            )
            
            if not validation["is_valid"]:
                return {
                    "found": False,
                    "search_term": search_term,
                    "indeed_slug": slug,
                    "indeed_url": url,
                    "title": title,
                    "snippet": snippet,
                    "validation": validation,
                    "error": validation["reason"]
                }
            
            # Step 5: Success
            return {
                "found": True,
                "search_term": search_term,
                "indeed_slug": slug,
                "indeed_url": url,
                "title": title,
                "snippet": snippet,
                "validation": validation,
                "review_count": self._extract_review_count(title)
            }
            
        except Exception as e:
            logger.error(f"Error searching Indeed for {search_term}: {e}")
            return {
                "found": False,
                "search_term": search_term,
                "error": str(e)
            }
    
    def _validate_company_match(
        self,
        url: str,
        title: str,
        snippet: str,
        expected_city: Optional[str],
        expected_postcode: Optional[str],
        search_term: str
    ) -> Dict[str, Any]:
        """
        Validate that found company matches expected criteria
        
        Validation checklist from documentation:
        1. URL contains "/reviews"
        2. Title includes "reviews"
        3. Snippet mentions expected city
        4. Domain is uk.indeed.com
        """
        checks = {
            "has_reviews_in_url": "/reviews" in url.lower(),
            "has_reviews_in_title": "review" in title.lower(),
            "is_uk_indeed": "uk.indeed.com" in url.lower(),
            "city_match": False,
            "postcode_match": False,
            "name_match": False
        }
        
        # City validation
        if expected_city:
            city_lower = expected_city.lower()
            checks["city_match"] = (
                city_lower in snippet.lower() or
                city_lower in title.lower()
            )
        else:
            checks["city_match"] = True  # No city to validate
        
        # Postcode validation (partial match)
        if expected_postcode:
            postcode_prefix = expected_postcode.split()[0] if " " in expected_postcode else expected_postcode[:3]
            checks["postcode_match"] = postcode_prefix.upper() in snippet.upper()
        else:
            checks["postcode_match"] = True
        
        # Name match validation
        search_words = search_term.lower().split()
        title_lower = title.lower()
        checks["name_match"] = any(word in title_lower for word in search_words if len(word) > 3)
        
        # Calculate validation score
        score = sum([
            checks["has_reviews_in_url"] * 0.2,
            checks["has_reviews_in_title"] * 0.1,
            checks["is_uk_indeed"] * 0.2,
            checks["city_match"] * 0.2,
            checks["name_match"] * 0.3
        ])
        
        # Determine if valid
        is_valid = (
            checks["has_reviews_in_url"] and
            checks["is_uk_indeed"] and
            (checks["city_match"] or checks["name_match"]) and
            score >= 0.5
        )
        
        reason = None
        if not is_valid:
            if not checks["has_reviews_in_url"]:
                reason = "Not a reviews page"
            elif not checks["is_uk_indeed"]:
                reason = "Not UK Indeed domain"
            elif not checks["city_match"] and expected_city:
                reason = f"City mismatch: expected {expected_city}"
            elif not checks["name_match"]:
                reason = f"Company name mismatch"
            else:
                reason = "Low validation score"
        
        return {
            "is_valid": is_valid,
            "score": round(score, 2),
            "checks": checks,
            "reason": reason
        }
    
    def _extract_review_count(self, title: str) -> Optional[int]:
        """Extract review count from Indeed title like 'Working at Company: 137 Reviews'"""
        match = re.search(r"(\d+)\s*review", title.lower())
        if match:
            return int(match.group(1))
        return None
    
    async def scrape_indeed_reviews(
        self,
        indeed_url: str,
        max_reviews: int = 50
    ) -> Dict[str, Any]:
        """
        Scrape reviews from Indeed company page using Firecrawl
        
        Args:
            indeed_url: Indeed reviews URL
            max_reviews: Maximum number of reviews to extract
        
        Returns:
            {
                "success": bool,
                "reviews": list,
                "company_info": dict,
                "error": str or None
            }
        """
        if not self.firecrawl_client:
            return {
                "success": False,
                "error": "Firecrawl client not configured"
            }
        
        logger.info(f"📄 Scraping Indeed reviews: {indeed_url}")
        
        try:
            # Scrape the Indeed page
            result = await self.firecrawl_client.scrape_url(
                url=indeed_url,
                formats=[{"type": "markdown"}, {"type": "html"}]
            )
            
            markdown = result.get("markdown", "")
            html = result.get("html", "")
            
            if not markdown and not html:
                return {
                    "success": False,
                    "error": "No content returned from Firecrawl"
                }
            
            # Extract reviews using pattern matching or LLM
            if self.openai_client:
                reviews_data = await self._extract_reviews_with_llm(markdown, max_reviews)
            else:
                reviews_data = self._extract_reviews_with_regex(markdown, html)
            
            return {
                "success": True,
                "url": indeed_url,
                "reviews": reviews_data.get("reviews", []),
                "company_info": reviews_data.get("company_info", {}),
                "total_found": len(reviews_data.get("reviews", []))
            }
            
        except Exception as e:
            logger.error(f"Error scraping Indeed reviews: {e}")
            return {
                "success": False,
                "url": indeed_url,
                "error": str(e)
            }
    
    def _extract_reviews_with_regex(
        self,
        markdown: str,
        html: str
    ) -> Dict[str, Any]:
        """Extract reviews using regex patterns"""
        reviews = []
        
        # Pattern for Indeed review blocks
        # Indeed reviews typically have: rating, title, date, pros, cons
        
        # Try to find rating patterns (e.g., "4.0 out of 5 stars")
        rating_pattern = r"(\d\.?\d?)\s*(?:out of 5|stars?|/5)"
        ratings = re.findall(rating_pattern, markdown.lower())
        
        # Try to find date patterns
        date_pattern = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})"
        dates = re.findall(date_pattern, markdown, re.IGNORECASE)
        
        # Extract text blocks that look like reviews
        # Split by common review delimiters
        review_blocks = re.split(r"(?:---|\n\n\n|#{2,})", markdown)
        
        for i, block in enumerate(review_blocks):
            if len(block.strip()) < 50:
                continue
            
            # Check if block looks like a review
            block_lower = block.lower()
            if any(keyword in block_lower for keyword in ["pros", "cons", "review", "work", "management", "staff"]):
                rating = float(ratings[i]) if i < len(ratings) else None
                date = dates[i] if i < len(dates) else None
                
                # Determine sentiment from rating or keywords
                sentiment = "NEUTRAL"
                if rating:
                    if rating >= 4:
                        sentiment = "POSITIVE"
                    elif rating <= 2:
                        sentiment = "NEGATIVE"
                    else:
                        sentiment = "MIXED"
                
                reviews.append({
                    "source": "Indeed UK",
                    "rating": rating,
                    "text": block.strip()[:500],
                    "date": date,
                    "sentiment": sentiment,
                    "author": "Anonymous"
                })
        
        # Extract company info
        company_info = {}
        
        # Try to find overall rating
        overall_match = re.search(r"(\d\.?\d?)\s*(?:out of 5|overall|rating)", markdown.lower())
        if overall_match:
            company_info["overall_rating"] = float(overall_match.group(1))
        
        # Try to find total review count
        count_match = re.search(r"(\d+(?:,\d+)?)\s*reviews?", markdown.lower())
        if count_match:
            company_info["total_reviews"] = int(count_match.group(1).replace(",", ""))
        
        return {
            "reviews": reviews[:50],  # Limit to 50
            "company_info": company_info
        }
    
    async def _extract_reviews_with_llm(
        self,
        markdown: str,
        max_reviews: int
    ) -> Dict[str, Any]:
        """Extract reviews using OpenAI structured extraction"""
        import json
        import httpx
        
        prompt = f"""Extract employee reviews from this Indeed page content.

Content:
{markdown[:8000]}

Extract up to {max_reviews} reviews. For each review, extract:
1. rating: number 1-5 (or null if not found)
2. text: the review text (max 500 chars)
3. date: review date if found
4. sentiment: POSITIVE, MIXED, NEGATIVE, or NEUTRAL
5. pros: positive points mentioned
6. cons: negative points mentioned

Also extract company info:
- overall_rating: company's overall Indeed rating
- total_reviews: total number of reviews
- company_name: company name

Return JSON in this format:
{{
  "reviews": [
    {{
      "rating": 4.0,
      "text": "Great place to work...",
      "date": "January 2024",
      "sentiment": "POSITIVE",
      "pros": "Good management, flexible hours",
      "cons": "Low pay"
    }}
  ],
  "company_info": {{
    "overall_rating": 3.8,
    "total_reviews": 137,
    "company_name": "Company Name"
  }}
}}

Return ONLY valid JSON, no markdown or explanation."""

        try:
            api_key = getattr(self.openai_client, 'api_key', None)
            base_url = getattr(self.openai_client, 'base_url', 'https://api.openai.com/v1')
            
            if not api_key:
                return self._extract_reviews_with_regex(markdown, "")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You extract structured data from Indeed employee reviews. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 4000,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                result = json.loads(content)
                
                # Add source to each review
                for review in result.get("reviews", []):
                    review["source"] = "Indeed UK"
                    if "author" not in review:
                        review["author"] = "Anonymous"
                
                return result
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._extract_reviews_with_regex(markdown, "")
    
    async def search_and_scrape(
        self,
        search_term: str,
        expected_city: Optional[str] = None,
        expected_postcode: Optional[str] = None,
        scrape_reviews: bool = True,
        max_reviews: int = 50
    ) -> Dict[str, Any]:
        """
        Complete workflow: search for company on Indeed and scrape reviews
        
        Args:
            search_term: Company/brand name
            expected_city: Expected city for validation
            expected_postcode: Expected postcode for validation
            scrape_reviews: Whether to scrape reviews after finding company
            max_reviews: Maximum reviews to scrape
        
        Returns:
            Combined search and scrape results
        """
        # Step 1: Find company on Indeed
        search_result = await self.find_indeed_company(
            search_term=search_term,
            expected_city=expected_city,
            expected_postcode=expected_postcode
        )
        
        if not search_result.get("found"):
            return search_result
        
        # Step 2: Optionally scrape reviews
        if scrape_reviews and self.firecrawl_client:
            indeed_url = search_result.get("indeed_url")
            scrape_result = await self.scrape_indeed_reviews(
                indeed_url=indeed_url,
                max_reviews=max_reviews
            )
            
            search_result["scrape_result"] = scrape_result
            if scrape_result.get("success"):
                search_result["reviews"] = scrape_result.get("reviews", [])
                search_result["company_info"] = scrape_result.get("company_info", {})
        
        return search_result
    
    async def close(self):
        """Close all clients"""
        if self.google_client:
            await self.google_client.close()
