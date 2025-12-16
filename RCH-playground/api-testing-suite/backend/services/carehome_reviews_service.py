"""
CareHome.co.uk Reviews Service
Scrapes and semantically analyzes reviews from carehome.co.uk

Key Features:
- Finds care home by name/postcode via Google Custom Search
- Scrapes ALL reviews (100+ possible) with pagination
- Extracts structured data: ratings, text, reviewer connection
- Performs aspect-based sentiment analysis
- Identifies staff quality signals from family reviews

URL Pattern: https://www.carehome.co.uk/carehome.cfm/searchazref/{ID}/startpage/{PAGE}
Reviews per page: 20
Rating categories: Facilities, Care/Support, Cleanliness, Dignity, Food, Staff, Activities, Management, Safety, Rooms, Value
"""
import re
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


# Rating categories on CareHome.co.uk
RATING_CATEGORIES = [
    "Facilities",
    "Care / Support", 
    "Cleanliness",
    "Treated with Dignity",
    "Food & Drink",
    "Staff",
    "Activities",
    "Management",
    "Safety / Security",
    "Rooms",
    "Value for Money"
]

# Reviewer connection types (family relationship to resident)
REVIEWER_CONNECTIONS = [
    "Daughter of Resident/Service User",
    "Son of Resident/Service User",
    "Wife of Resident/Service User",
    "Husband of Resident/Service User",
    "Resident / Service User",
    "Daughter-in-law of Resident/Service User",
    "Son-in-law of Resident/Service User",
    "Brother of Resident/Service User",
    "Sister of Resident/Service User",
    "Niece of Resident/Service User",
    "Nephew of Resident/Service User",
    "Friend of Resident/Service User",
    "Granddaughter of Resident/Service User",
    "Grandson of Resident/Service User",
    "Partner of Resident/Service User",
    "Respite Resident/Service User",
    "Other"
]

# Aspect keywords for semantic analysis
ASPECT_KEYWORDS = {
    "staff_quality": {
        "positive": [
            "caring staff", "friendly staff", "kind staff", "professional staff",
            "dedicated staff", "lovely staff", "wonderful staff", "amazing staff",
            "helpful staff", "patient staff", "compassionate", "attentive",
            "well trained", "skilled nurses", "competent", "respectful"
        ],
        "negative": [
            "rude staff", "unfriendly", "unprofessional", "staff shortage",
            "understaffed", "high turnover", "agency staff", "lack of training",
            "careless", "neglectful", "dismissive", "overworked"
        ]
    },
    "care_quality": {
        "positive": [
            "excellent care", "good care", "wonderful care", "outstanding care",
            "great care", "personal care", "individual needs", "dignity",
            "person-centered", "tailored care", "gentle", "thorough"
        ],
        "negative": [
            "poor care", "lack of care", "neglected", "ignored",
            "not responsive", "slow response", "complaints", "concerns"
        ]
    },
    "communication": {
        "positive": [
            "good communication", "kept informed", "regular updates",
            "approachable", "responsive", "open door", "listen"
        ],
        "negative": [
            "poor communication", "not informed", "difficult to contact",
            "unanswered calls", "no updates", "lack of information"
        ]
    },
    "cleanliness": {
        "positive": [
            "clean", "spotless", "hygienic", "well maintained", "tidy",
            "fresh", "no smell", "pleasant environment"
        ],
        "negative": [
            "dirty", "unclean", "smell", "odor", "stained", "messy",
            "unhygienic", "needs cleaning"
        ]
    },
    "food": {
        "positive": [
            "good food", "excellent food", "tasty meals", "nutritious",
            "varied menu", "home cooked", "dietary needs met"
        ],
        "negative": [
            "poor food", "bland", "cold food", "limited choice",
            "not appetizing", "same meals"
        ]
    },
    "activities": {
        "positive": [
            "great activities", "varied activities", "entertainment",
            "stimulating", "engaged", "social events", "outings"
        ],
        "negative": [
            "bored", "no activities", "limited activities", "nothing to do",
            "sat around", "lack of stimulation"
        ]
    },
    "management": {
        "positive": [
            "well managed", "good management", "efficient", "organized",
            "supportive manager", "strong leadership"
        ],
        "negative": [
            "poor management", "disorganized", "high staff turnover",
            "management issues", "lack of leadership"
        ]
    },
    "value": {
        "positive": [
            "good value", "worth the money", "reasonable fees",
            "value for money", "fair price"
        ],
        "negative": [
            "expensive", "overpriced", "not worth", "hidden costs",
            "fees increased"
        ]
    }
}

# Staff-specific signals (for staff quality analysis)
STAFF_SIGNALS = {
    "training": ["trained", "training", "qualified", "certification", "NVQ", "diploma"],
    "tenure": ["long-serving", "been here years", "experienced", "new staff", "agency"],
    "morale": ["happy staff", "staff enjoy", "good atmosphere", "staff seem stressed", "overworked"],
    "ratio": ["enough staff", "plenty of staff", "staffing levels", "short staffed", "understaffed"],
    "turnover": ["same faces", "staff left", "new staff", "always different", "constant changes"]
}


class CareHomeReviewsService:
    """Service for scraping and analyzing reviews from carehome.co.uk"""
    
    def __init__(
        self,
        google_api_key: str,
        google_search_engine_id: str,
        firecrawl_client=None,
        openai_client=None
    ):
        self.google_api_key = google_api_key
        self.google_search_engine_id = google_search_engine_id
        self.firecrawl_client = firecrawl_client
        self.openai_client = openai_client
        
        # Google Custom Search client
        from api_clients.google_custom_search_client import GoogleCustomSearchClient
        self.search_client = GoogleCustomSearchClient(
            api_key=google_api_key,
            search_engine_id=google_search_engine_id
        )
    
    async def find_care_home(
        self,
        name: str,
        postcode: Optional[str] = None,
        city: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find care home on carehome.co.uk via Firecrawl web search
        
        Returns:
            Dict with searchazref ID and URL if found
        """
        # Build search query with site: operator
        query_parts = ['site:carehome.co.uk', f'"{name}"']
        if postcode:
            query_parts.append(f'"{postcode}"')
        elif city:
            query_parts.append(city)
        
        query = " ".join(query_parts)
        
        try:
            # Use Firecrawl web search (more reliable than Google CSE)
            if self.firecrawl_client:
                search_result = await self.firecrawl_client.web_search(
                    query=query,
                    limit=5
                )
                
                results = []
                web_results = search_result.get("web", []) if isinstance(search_result, dict) else []
                
                for item in web_results:
                    results.append({
                        "link": item.get("url", ""),
                        "title": item.get("title", ""),
                        "snippet": item.get("description", ""),
                    })
            else:
                # Fallback to Google Custom Search
                import httpx
                
                params = {
                    "key": self.google_api_key,
                    "cx": self.google_search_engine_id,
                    "q": query,
                    "num": 5
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        "https://www.googleapis.com/customsearch/v1",
                        params=params
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    results = []
                    for item in data.get("items", []):
                        results.append({
                            "link": item.get("link", ""),
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", ""),
                        })
            
            if not results:
                # Fallback: Try alternative search without site: prefix
                logger.info(f"No results with site: prefix, trying alternative search for: {name}")
                alt_query_parts = [f'"{name}"', 'carehome.co.uk']
                if postcode:
                    alt_query_parts.append(postcode)
                elif city:
                    alt_query_parts.append(city)
                alt_query = " ".join(alt_query_parts)
                
                if self.firecrawl_client:
                    search_result = await self.firecrawl_client.web_search(
                        query=alt_query,
                        limit=10
                    )
                    web_results = search_result.get("web", []) if isinstance(search_result, dict) else []
                    for item in web_results:
                        url = item.get("url", "")
                        if "carehome.co.uk" in url and "searchazref" in url:
                            results.append({
                                "link": url,
                                "title": item.get("title", ""),
                                "snippet": item.get("description", ""),
                            })
            
            if not results:
                logger.warning(f"No carehome.co.uk results for: {name}")
                return {"found": False, "error": "No results found"}
            
            # Find result with searchazref pattern
            for result in results:
                url = result.get("link", "")
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                # Extract searchazref ID from URL
                # Pattern: /carehome.cfm/searchazref/20001050HARA
                match = re.search(r'/searchazref/([A-Z0-9]+)', url, re.I)
                if match:
                    searchazref = match.group(1)
                    
                    # Extract review count from snippet if available
                    review_count_match = re.search(r'(\d+)\s*reviews?', snippet, re.I)
                    review_count = int(review_count_match.group(1)) if review_count_match else None
                    
                    # Extract rating from snippet
                    rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of 10|/10)', snippet, re.I)
                    rating = float(rating_match.group(1)) if rating_match else None
                    
                    return {
                        "found": True,
                        "searchazref": searchazref,
                        "url": f"https://www.carehome.co.uk/carehome.cfm/searchazref/{searchazref}",
                        "title": title,
                        "snippet": snippet,
                        "review_count": review_count,
                        "rating": rating
                    }
            
            logger.warning(f"No valid carehome.co.uk profile found for: {name}")
            return {"found": False, "error": "No carehome.co.uk profile found"}
            
        except Exception as e:
            logger.error(f"Error searching carehome.co.uk: {e}")
            return {"found": False, "error": str(e)}
    
    async def scrape_all_reviews(
        self,
        searchazref: str,
        max_reviews: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape all reviews from carehome.co.uk profile
        
        Args:
            searchazref: The carehome.co.uk ID (e.g., "20001050HARA")
            max_reviews: Maximum reviews to scrape (default 100)
        
        Returns:
            List of review dictionaries
        """
        if not self.firecrawl_client:
            logger.error("Firecrawl client not available")
            return []
        
        base_url = f"https://www.carehome.co.uk/carehome.cfm/searchazref/{searchazref}"
        all_reviews = []
        reviews_per_page = 20
        max_pages = (max_reviews // reviews_per_page) + 1
        
        logger.info(f"Scraping reviews from {base_url}")
        
        # Scrape first page to get total count
        try:
            first_page = await self.firecrawl_client.scrape_url(
                url=base_url,
                formats=[{"type": "markdown"}]
            )
            
            markdown = first_page.get("markdown", "")
            
            # Extract total review count
            total_match = re.search(r'Reviews?\s*\((\d+)\)', markdown)
            total_reviews = int(total_match.group(1)) if total_match else 50
            
            actual_pages = min(max_pages, (total_reviews // reviews_per_page) + 1)
            logger.info(f"Found {total_reviews} total reviews, scraping {actual_pages} pages")
            
            # Extract reviews from first page
            page_reviews = await self._extract_reviews_from_page(markdown, 1)
            all_reviews.extend(page_reviews)
            
        except Exception as e:
            logger.error(f"Error scraping first page: {e}")
            return []
        
        # Scrape additional pages
        for page_num in range(2, actual_pages + 1):
            if len(all_reviews) >= max_reviews:
                break
            
            page_url = f"{base_url}/startpage/{page_num}"
            
            try:
                await asyncio.sleep(1.0)  # Rate limiting
                
                page_result = await self.firecrawl_client.scrape_url(
                    url=page_url,
                    formats=[{"type": "markdown"}]
                )
                
                markdown = page_result.get("markdown", "")
                page_reviews = await self._extract_reviews_from_page(markdown, page_num)
                all_reviews.extend(page_reviews)
                
                logger.info(f"Page {page_num}: extracted {len(page_reviews)} reviews")
                
            except Exception as e:
                logger.error(f"Error scraping page {page_num}: {e}")
                continue
        
        return all_reviews[:max_reviews]
    
    async def _extract_reviews_from_page(
        self,
        markdown: str,
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Extract reviews from page markdown using LLM"""
        
        if self.openai_client:
            return await self._extract_reviews_with_llm(markdown, page_num)
        else:
            return self._extract_reviews_regex(markdown, page_num)
    
    async def _extract_reviews_with_llm(
        self,
        markdown: str,
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Use LLM to extract structured reviews from markdown"""
        import json
        import httpx
        
        # Truncate markdown if too long
        markdown_truncated = markdown[:15000]
        
        prompt = f"""Extract all care home reviews from this page content.

For each review, extract:
1. reviewer_initials: The reviewer's initials (e.g., "J S")
2. reviewer_connection: Their relationship to resident (e.g., "Daughter of Resident")
3. date: Publication date (e.g., "16 September 2025")
4. overall_rating: Overall Experience rating (1-5, where Excellent=5, Good=4, Satisfactory=3, Poor=2, Very Poor=1)
5. review_text: The full review text
6. category_ratings: Object with ratings for each category (Facilities, Care/Support, Cleanliness, Staff, etc.)

PAGE CONTENT:
{markdown_truncated}

Return valid JSON array of reviews. Example format:
{{
  "reviews": [
    {{
      "reviewer_initials": "J S",
      "reviewer_connection": "Daughter of Resident",
      "date": "16 September 2025",
      "overall_rating": 5,
      "review_text": "Very happy with my dad's care...",
      "category_ratings": {{
        "Facilities": 5,
        "Care / Support": 5,
        "Cleanliness": 5,
        "Staff": 5
      }}
    }}
  ]
}}

Return ONLY valid JSON, no markdown formatting."""

        try:
            api_key = getattr(self.openai_client, 'api_key', None)
            base_url = getattr(self.openai_client, 'base_url', 'https://api.openai.com/v1')
            
            if not api_key:
                return self._extract_reviews_regex(markdown, page_num)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a data extraction expert. Extract structured review data from care home website content. Return only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
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
                
                reviews = result.get("reviews", [])
                
                # Add page number and source, and clean review text
                for review in reviews:
                    review["source"] = "carehome.co.uk"
                    review["page"] = page_num
                    # Clean review_text from markdown artifacts
                    if "review_text" in review:
                        review["review_text"] = self._clean_review_text(review["review_text"])
                
                return reviews
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._extract_reviews_regex(markdown, page_num)
    
    def _extract_reviews_regex(
        self,
        markdown: str,
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Fallback regex-based review extraction"""
        reviews = []
        
        # Pattern for review blocks
        review_pattern = re.compile(
            r'\*\*Review from ([A-Z\s]+) \(([^)]+)\) published on ([^*]+)\*\*.*?'
            r'\*\*Overall Experience\*\*.*?(\d+\.?\d*) out of 5.*?'
            r'([^*]{50,2000}?)(?=\*\*Review from|\Z)',
            re.DOTALL | re.IGNORECASE
        )
        
        for match in review_pattern.finditer(markdown):
            initials = match.group(1).strip()
            connection = match.group(2).strip()
            date = match.group(3).strip()
            rating = float(match.group(4))
            text = match.group(5).strip()
            
            # Clean text
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\*+', '', text)
            text = text.strip()
            
            if len(text) > 20:
                reviews.append({
                    "reviewer_initials": initials,
                    "reviewer_connection": connection,
                    "date": date,
                    "overall_rating": int(rating),
                    "review_text": text,
                    "source": "carehome.co.uk",
                    "page": page_num
                })
        
        return reviews
    
    def _clean_review_text(self, text: str) -> str:
        """Clean review text from markdown artifacts, image links, and category ratings"""
        if not text:
            return ""
        
        # Remove markdown image syntax: ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        
        # Remove standalone image URLs
        text = re.sub(r'https?://[^\s]+\.(png|jpg|jpeg|gif|svg)[^\s]*', '', text)
        
        # Remove category rating lines like "- Facilities ![](url)"
        text = re.sub(r'-\s*[A-Za-z\s/]+\s*!\[\]\([^)]+\)', '', text)
        
        # Remove remaining markdown link syntax: [text](url)
        text = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', text)
        
        # Remove lines that are just category names with no content
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that are just "- Category Name" or similar
            if re.match(r'^-?\s*[A-Za-z\s/]+\s*$', line) and len(line) < 30:
                continue
            if line:
                cleaned_lines.append(line)
        
        text = ' '.join(cleaned_lines)
        
        # Clean up multiple spaces and dots
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\s*\.\s*-\s*', '. ', text)
        
        return text.strip()
    
    def analyze_reviews_semantically(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive semantic analysis on reviews
        
        Returns:
            Dict with sentiment scores, themes, staff quality signals
        """
        if not reviews:
            return self._empty_analysis()
        
        analysis = {
            "total_reviews": len(reviews),
            "average_rating": 0,
            "rating_distribution": {},
            "aspect_sentiment": {},
            "themes": {},
            "staff_quality_signals": {},
            "reviewer_connections": {},
            "temporal_analysis": {},
            "key_quotes": []
        }
        
        # Rating distribution
        ratings = [r.get("overall_rating", 0) for r in reviews if r.get("overall_rating")]
        if ratings:
            analysis["average_rating"] = round(sum(ratings) / len(ratings), 2)
            analysis["rating_distribution"] = dict(Counter(ratings))
        
        # Reviewer connections distribution
        connections = [r.get("reviewer_connection", "Unknown") for r in reviews]
        analysis["reviewer_connections"] = dict(Counter(connections))
        
        # Aspect-based sentiment analysis
        all_text = " ".join([r.get("review_text", "") for r in reviews]).lower()
        
        for aspect, keywords in ASPECT_KEYWORDS.items():
            positive_count = sum(1 for kw in keywords["positive"] if kw in all_text)
            negative_count = sum(1 for kw in keywords["negative"] if kw in all_text)
            total = positive_count + negative_count
            
            if total > 0:
                sentiment_score = (positive_count - negative_count) / total
                analysis["aspect_sentiment"][aspect] = {
                    "score": round(sentiment_score, 2),
                    "positive_mentions": positive_count,
                    "negative_mentions": negative_count,
                    "sentiment": "positive" if sentiment_score > 0.2 else "negative" if sentiment_score < -0.2 else "neutral"
                }
        
        # Staff quality signals
        for signal_type, keywords in STAFF_SIGNALS.items():
            mentions = sum(1 for kw in keywords if kw.lower() in all_text)
            if mentions > 0:
                analysis["staff_quality_signals"][signal_type] = mentions
        
        # Extract key themes (most mentioned aspects)
        theme_counts = {}
        theme_keywords = {
            "caring_staff": ["caring", "kind", "friendly", "lovely staff"],
            "good_communication": ["communication", "informed", "updates"],
            "clean_environment": ["clean", "spotless", "hygienic"],
            "good_food": ["food", "meals", "menu"],
            "activities": ["activities", "entertainment", "events"],
            "family_welcome": ["welcome", "visiting", "family"],
            "dignity_respect": ["dignity", "respect", "individual"],
            "safe_secure": ["safe", "secure", "peace of mind"]
        }
        
        for theme, keywords in theme_keywords.items():
            count = sum(1 for kw in keywords if kw.lower() in all_text)
            if count > 0:
                theme_counts[theme] = count
        
        analysis["themes"] = dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Extract key quotes (reviews with strong sentiment)
        for review in reviews[:20]:
            text = review.get("review_text", "")
            rating = review.get("overall_rating", 0)
            
            # High rating positive quotes
            if rating >= 4 and len(text) > 50:
                if any(kw in text.lower() for kw in ["staff", "care", "recommend"]):
                    analysis["key_quotes"].append({
                        "text": text[:300],
                        "rating": rating,
                        "type": "positive"
                    })
            
            # Low rating concerning quotes
            elif rating <= 2 and len(text) > 50:
                analysis["key_quotes"].append({
                    "text": text[:300],
                    "rating": rating,
                    "type": "negative"
                })
        
        analysis["key_quotes"] = analysis["key_quotes"][:10]
        
        # Calculate overall staff quality score from reviews
        staff_score = self._calculate_staff_score_from_reviews(reviews, analysis)
        analysis["staff_quality_score"] = staff_score
        
        return analysis
    
    def _calculate_staff_score_from_reviews(
        self,
        reviews: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate staff quality score from carehome.co.uk reviews"""
        
        # Base score from Staff category ratings
        staff_ratings = []
        for review in reviews:
            category_ratings = review.get("category_ratings", {})
            staff_rating = category_ratings.get("Staff")
            if staff_rating:
                staff_ratings.append(staff_rating)
        
        base_score = 0
        if staff_ratings:
            avg_staff_rating = sum(staff_ratings) / len(staff_ratings)
            base_score = (avg_staff_rating / 5) * 100  # Convert 1-5 to 0-100
        
        # Adjust based on sentiment analysis
        staff_sentiment = analysis.get("aspect_sentiment", {}).get("staff_quality", {})
        sentiment_score = staff_sentiment.get("score", 0)
        
        # Sentiment adjustment (-10 to +10 points)
        sentiment_adjustment = sentiment_score * 10
        
        # Adjust based on management sentiment (staff morale indicator)
        management_sentiment = analysis.get("aspect_sentiment", {}).get("management", {})
        mgmt_score = management_sentiment.get("score", 0)
        management_adjustment = mgmt_score * 5
        
        final_score = base_score + sentiment_adjustment + management_adjustment
        final_score = max(0, min(100, final_score))  # Clamp to 0-100
        
        # Determine confidence based on review count
        # 10+ reviews = high confidence (sufficient sample)
        # 5-9 reviews = medium confidence
        # <5 reviews = low confidence
        review_count = len(reviews)
        if review_count >= 10:
            confidence = "high"
        elif review_count >= 5:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "score": round(final_score, 1),
            "base_score": round(base_score, 1),
            "sentiment_adjustment": round(sentiment_adjustment, 1),
            "management_adjustment": round(management_adjustment, 1),
            "confidence": confidence,
            "review_count": review_count,
            "category": self._score_to_category(final_score)
        }
    
    def _score_to_category(self, score: float) -> str:
        """Convert score to category"""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 75:
            return "GOOD"
        elif score >= 60:
            return "SATISFACTORY"
        elif score >= 40:
            return "REQUIRES_IMPROVEMENT"
        else:
            return "POOR"
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "rating_distribution": {},
            "aspect_sentiment": {},
            "themes": {},
            "staff_quality_signals": {},
            "reviewer_connections": {},
            "temporal_analysis": {},
            "key_quotes": [],
            "staff_quality_score": {
                "score": 0,
                "confidence": "none",
                "review_count": 0,
                "category": "INSUFFICIENT_DATA"
            }
        }
    
    async def get_reviews_with_analysis(
        self,
        name: str,
        postcode: Optional[str] = None,
        city: Optional[str] = None,
        max_reviews: int = 100
    ) -> Dict[str, Any]:
        """
        Full pipeline: find care home, scrape reviews, analyze semantically
        
        Returns:
            Complete analysis with reviews and insights
        """
        result = {
            "care_home": {},
            "carehome_co_uk": {},
            "reviews": [],
            "analysis": {},
            "success": False
        }
        
        # Step 1: Find care home
        search_result = await self.find_care_home(name, postcode, city)
        
        if not search_result or not search_result.get("found"):
            result["error"] = search_result.get("error", "Care home not found on carehome.co.uk")
            return result
        
        result["care_home"] = {
            "name": name,
            "postcode": postcode,
            "city": city
        }
        
        result["carehome_co_uk"] = {
            "searchazref": search_result.get("searchazref"),
            "url": search_result.get("url"),
            "title": search_result.get("title"),
            "rating": search_result.get("rating"),
            "total_reviews": search_result.get("review_count")
        }
        
        # Step 2: Scrape reviews
        if self.firecrawl_client:
            reviews = await self.scrape_all_reviews(
                searchazref=search_result["searchazref"],
                max_reviews=max_reviews
            )
            result["reviews"] = reviews
        else:
            result["reviews"] = []
            result["warning"] = "Firecrawl not configured - unable to scrape reviews"
        
        # Step 3: Analyze reviews
        if result["reviews"]:
            result["analysis"] = self.analyze_reviews_semantically(result["reviews"])
        else:
            result["analysis"] = self._empty_analysis()
        
        result["success"] = True
        return result


# Utility function for quick testing
async def test_carehome_reviews():
    """Test function for CareHome.co.uk reviews service"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from config_manager import get_credentials
    from utils.auth import credentials_store
    from utils.client_factory import get_firecrawl_client, get_openai_client
    
    creds = get_credentials()
    credentials_store['default'] = creds
    
    google_api_key = creds.google_places.api_key
    search_engine_id = getattr(creds.google_places, 'search_engine_id', None)
    
    if not search_engine_id:
        print("❌ search_engine_id not configured in config.json")
        return
    
    firecrawl_client = None
    openai_client = None
    
    try:
        firecrawl_client = get_firecrawl_client()
        print("✅ Firecrawl client loaded")
    except Exception as e:
        print(f"⚠️ Firecrawl not available: {e}")
    
    try:
        openai_client = get_openai_client()
        print("✅ OpenAI client loaded")
    except Exception as e:
        print(f"⚠️ OpenAI not available: {e}")
    
    service = CareHomeReviewsService(
        google_api_key=google_api_key,
        google_search_engine_id=search_engine_id,
        firecrawl_client=firecrawl_client,
        openai_client=openai_client
    )
    
    # Test with a care home
    result = await service.get_reviews_with_analysis(
        name="Harbledown Lodge Nursing Home",
        city="Canterbury",
        max_reviews=50
    )
    
    print("\n" + "=" * 60)
    print("CAREHOME.CO.UK REVIEWS ANALYSIS")
    print("=" * 60)
    
    if result.get("success"):
        ch = result.get("carehome_co_uk", {})
        print(f"\n📍 {ch.get('title')}")
        print(f"   URL: {ch.get('url')}")
        print(f"   Rating: {ch.get('rating')}/10")
        print(f"   Total reviews: {ch.get('total_reviews')}")
        
        analysis = result.get("analysis", {})
        print(f"\n📊 Analysis:")
        print(f"   Reviews scraped: {analysis.get('total_reviews')}")
        print(f"   Average rating: {analysis.get('average_rating')}/5")
        
        print(f"\n🎯 Staff Quality Score: {analysis.get('staff_quality_score', {}).get('score')}/100")
        print(f"   Category: {analysis.get('staff_quality_score', {}).get('category')}")
        print(f"   Confidence: {analysis.get('staff_quality_score', {}).get('confidence')}")
        
        print(f"\n💬 Key Themes:")
        for theme, count in analysis.get("themes", {}).items():
            print(f"   - {theme}: {count} mentions")
        
        print(f"\n😊 Aspect Sentiment:")
        for aspect, data in analysis.get("aspect_sentiment", {}).items():
            print(f"   - {aspect}: {data.get('sentiment')} ({data.get('score')})")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_carehome_reviews())
