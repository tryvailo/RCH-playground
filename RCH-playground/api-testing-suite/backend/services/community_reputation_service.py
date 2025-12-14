"""
Community Reputation Service
Implements Section 10: Community Reputation according to PROFESSIONAL_REPORT_SPEC_v3.2

According to SPEC v3.2:
- PRIMARY: reviews_detailed JSONB from care_homes DB
- SECONDARY: Google Places Details API (only if DB stale >30 days or rating differs)
- Aspect-based sentiment analysis (staff, food, cleanliness, communication, activities)
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, date
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Review:
    """Review dataclass according to SPEC v3.2"""
    source: str
    rating: int
    text: str
    date: Optional[date]
    author: str
    has_response: bool
    response: Optional[str] = None


@dataclass
class SentimentAnalysis:
    """SentimentAnalysis dataclass according to SPEC v3.2"""
    overall: str  # "Positive" / "Neutral" / "Negative"
    score: float  # -1.0 to 1.0
    themes: Dict[str, float]  # {"staff": 0.8, "food": 0.3, ...}
    positive_keywords: List[str]
    negative_keywords: List[str]


@dataclass
class CommunityReputation:
    """CommunityReputation dataclass according to SPEC v3.2"""
    # Aggregate scores (from flat fields)
    average_score: float  # review_average_score
    total_reviews: int  # review_count
    google_rating: Optional[float]  # google_rating
    
    # Detailed reviews (from JSONB)
    reviews: List[Review]
    
    # Sentiment Analysis (calculated)
    sentiment: SentimentAnalysis
    
    # Response rate
    management_response_rate: float


class CommunityReputationService:
    """Service for building Community Reputation according to SPEC v3.2"""
    
    def build_community_reputation(
        self,
        db_reviews: Optional[Dict[str, Any]],  # reviews_detailed JSONB from DB
        review_average_score: Optional[float] = None,
        review_count: Optional[int] = None,
        google_rating: Optional[float] = None,
        google_place_details: Optional[Dict[str, Any]] = None  # Optional: Google Places API refresh
    ) -> CommunityReputation:
        """
        Build Community Reputation from PRIMARY source (reviews_detailed JSONB)
        with optional Google Places API enrichment
        
        According to SPEC v3.2:
        - PRIMARY: reviews_detailed JSONB from care_homes DB
        - SECONDARY: Google Places Details API (only if DB stale >30 days or rating differs)
        """
        # Parse reviews from PRIMARY source (reviews_detailed JSONB)
        reviews = self._parse_reviews_from_db(db_reviews)
        
        # Optionally merge with Google Places API if provided
        if google_place_details:
            google_reviews = self._parse_google_place_reviews(google_place_details)
            # Merge, avoiding duplicates
            existing_texts = {r.text.lower()[:50] for r in reviews}
            for gr in google_reviews:
                if gr.text.lower()[:50] not in existing_texts:
                    reviews.append(gr)
        
        # Calculate response rate
        response_count = sum(1 for r in reviews if r.has_response)
        response_rate = response_count / len(reviews) if reviews else 0.0
        
        # Analyze sentiment with aspect-based analysis
        sentiment = self._analyze_review_sentiment(reviews)
        
        # Use provided values or calculate from reviews
        if review_average_score is None and reviews:
            review_average_score = sum(r.rating for r in reviews) / len(reviews)
        elif review_average_score is None:
            review_average_score = 0.0
        
        if review_count is None:
            review_count = len(reviews)
        
        return CommunityReputation(
            average_score=review_average_score,
            total_reviews=review_count,
            google_rating=google_rating,
            reviews=reviews,
            sentiment=sentiment,
            management_response_rate=response_rate
        )
    
    def _get_marketing_source_name(self, technical_source: str) -> str:
        """Convert technical source name to marketing name"""
        source_mapping = {
            'google': 'Public Reviews',
            'internal': 'Care Home Reviews',
            'carehome.co.uk': 'Care Home Directory',
            'unknown': 'Community Feedback',
            'carehome': 'Care Home Directory',
            'testimonial': 'Family Testimonials'
        }
        return source_mapping.get(technical_source.lower(), 'Community Feedback')
    
    def _parse_reviews_from_db(self, db_reviews: Optional[Dict[str, Any]]) -> List[Review]:
        """Parse reviews from reviews_detailed JSONB"""
        reviews = []
        
        if not db_reviews:
            return reviews
        
        # Handle string JSON
        if isinstance(db_reviews, str):
            try:
                db_reviews = json.loads(db_reviews)
            except json.JSONDecodeError:
                logger.warning("Failed to parse reviews_detailed JSONB")
                return reviews
        
        # Extract reviews list
        reviews_list = db_reviews.get('reviews', [])
        if not isinstance(reviews_list, list):
            return reviews
        
        for r in reviews_list:
            if not isinstance(r, dict):
                continue
            
            # Parse date
            review_date = None
            date_str = r.get('date') or r.get('time') or r.get('published_at')
            if date_str:
                review_date = self._parse_date(date_str)
            
            review = Review(
                source=self._get_marketing_source_name(r.get('source', 'unknown')),
                rating=int(r.get('rating', 0)) if r.get('rating') else 0,
                text=str(r.get('text', '')),
                date=review_date,
                author=r.get('author', 'Anonymous'),
                has_response=bool(r.get('has_response', False)),
                response=r.get('response') if r.get('has_response') else None
            )
            reviews.append(review)
        
        return reviews
    
    def _parse_google_place_reviews(self, google_place_details: Dict[str, Any]) -> List[Review]:
        """Parse reviews from Google Places API response"""
        reviews = []
        
        google_reviews = google_place_details.get('reviews', [])
        if not isinstance(google_reviews, list):
            return reviews
        
        for gr in google_reviews:
            if not isinstance(gr, dict):
                continue
            
            # Parse date from Google Places format
            review_date = None
            time_value = gr.get('time') or gr.get('relative_time_description')
            if time_value:
                review_date = self._parse_google_date(time_value)
            
            review = Review(
                source='Public Reviews',  # Marketing name, not technical API name
                rating=int(gr.get('rating', 0)) if gr.get('rating') else 0,
                text=str(gr.get('text', '')),
                date=review_date,
                author=gr.get('author_name', 'Anonymous'),
                has_response=bool(gr.get('response', False)),
                response=gr.get('response', {}).get('text') if gr.get('response') else None
            )
            reviews.append(review)
        
        return reviews
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        
        try:
            # Try ISO format
            if 'T' in str(date_str):
                return datetime.fromisoformat(str(date_str).replace('Z', '+00:00')).date()
            # Try YYYY-MM-DD
            return datetime.strptime(str(date_str)[:10], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    def _parse_google_date(self, time_value: Any) -> Optional[date]:
        """Parse Google Places date format"""
        # Google Places uses relative time or timestamp
        if isinstance(time_value, (int, float)):
            try:
                return datetime.fromtimestamp(time_value).date()
            except (ValueError, OSError):
                return None
        return None
    
    def _analyze_review_sentiment(self, reviews: List[Review]) -> SentimentAnalysis:
        """
        NLP анализ sentiment из текстов отзывов
        According to SPEC v3.2 (lines 1094-1159)
        """
        ASPECT_KEYWORDS = {
            "staff": ["staff", "carer", "nurse", "team", "friendly", "kind", "caring", "caregiver", "worker"],
            "food": ["food", "meal", "dinner", "lunch", "breakfast", "menu", "cooking", "catering", "dining"],
            "cleanliness": ["clean", "tidy", "hygiene", "spotless", "smell", "dirty", "messy", "sanitary"],
            "communication": ["communication", "update", "inform", "responsive", "contact", "call", "notify", "tell"],
            "activities": ["activity", "activities", "entertainment", "social", "event", "program", "outings"]
        }
        
        POSITIVE_WORDS = [
            "excellent", "wonderful", "amazing", "fantastic", "great", "lovely",
            "caring", "kind", "professional", "dedicated", "clean", "comfortable",
            "outstanding", "superb", "brilliant", "perfect", "delighted", "pleased"
        ]
        
        NEGATIVE_WORDS = [
            "poor", "terrible", "awful", "disappointing", "understaffed", "dirty",
            "rude", "neglect", "cold", "slow", "expensive", "complaint",
            "horrible", "worst", "bad", "unhappy", "dissatisfied", "concerned"
        ]
        
        aspect_scores = {aspect: [] for aspect in ASPECT_KEYWORDS}
        positive_found = []
        negative_found = []
        overall_scores = []
        
        for review in reviews:
            if not review.text:
                continue
            
            text_lower = review.text.lower()
            
            # Rating-based sentiment
            rating_sentiment = (review.rating - 3) / 2 if review.rating else 0
            overall_scores.append(rating_sentiment)
            
            # Keyword analysis
            for word in POSITIVE_WORDS:
                if word in text_lower and word not in positive_found:
                    positive_found.append(word)
            
            for word in NEGATIVE_WORDS:
                if word in text_lower and word not in negative_found:
                    negative_found.append(word)
            
            # Aspect-based sentiment
            for aspect, keywords in ASPECT_KEYWORDS.items():
                if any(kw in text_lower for kw in keywords):
                    aspect_scores[aspect].append(rating_sentiment)
        
        # Calculate averages
        overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        theme_scores = {}
        for aspect, scores in aspect_scores.items():
            theme_scores[aspect] = sum(scores) / len(scores) if scores else 0
        
        return SentimentAnalysis(
            overall="Positive" if overall_score > 0.2 else "Negative" if overall_score < -0.2 else "Neutral",
            score=round(overall_score, 2),
            themes=theme_scores,
            positive_keywords=positive_found[:5],
            negative_keywords=negative_found[:5]
        )
    
    def to_dict(self, reputation: CommunityReputation) -> Dict[str, Any]:
        """Convert CommunityReputation to dictionary for API response"""
        return {
            "google_rating": reputation.google_rating,
            "google_review_count": reputation.total_reviews,
            "carehome_rating": reputation.average_score,
            "trust_score": self._calculate_trust_score(reputation),
            "sentiment_analysis": {
                "average_sentiment": reputation.sentiment.score,
                "sentiment_label": reputation.sentiment.overall.lower(),
                "total_reviews": reputation.total_reviews,
                "positive_reviews": sum(1 for r in reputation.reviews if r.rating >= 4),
                "negative_reviews": sum(1 for r in reputation.reviews if r.rating <= 2),
                "neutral_reviews": sum(1 for r in reputation.reviews if 2 < r.rating < 4),
                "sentiment_distribution": self._calculate_sentiment_distribution(reputation.reviews),
                "themes": reputation.sentiment.themes,
                "positive_keywords": reputation.sentiment.positive_keywords,
                "negative_keywords": reputation.sentiment.negative_keywords
            },
            "sample_reviews": [
                {
                    "text": r.text[:200] if r.text else "",
                    "rating": r.rating,
                    "author": r.author,
                    "source": r.source,
                    "date": r.date.isoformat() if r.date else None,
                    "has_response": r.has_response,
                    "response": r.response[:200] if r.response else None
                }
                for r in sorted(reputation.reviews, key=lambda x: (x.rating, x.date or date.min), reverse=True)[:5]
            ],
            "total_reviews_analyzed": len(reputation.reviews),
            "review_sources": list(set([r.source for r in reputation.reviews])),
            "management_response_rate": round(reputation.management_response_rate * 100, 1)
        }
    
    def _calculate_trust_score(self, reputation: CommunityReputation) -> float:
        """Calculate trust score based on rating and review count"""
        trust_score = 0.0
        
        # Use google_rating if available, otherwise average_score
        rating = reputation.google_rating or reputation.average_score
        
        if rating:
            # Rating component (0-70 points)
            rating_score = (rating / 5.0) * 70
            trust_score += rating_score
            
            # Review count component (0-30 points)
            count = reputation.total_reviews
            if count >= 100:
                count_score = 30
            elif count >= 50:
                count_score = 25
            elif count >= 20:
                count_score = 20
            elif count >= 10:
                count_score = 15
            elif count >= 5:
                count_score = 10
            else:
                count_score = 5
            trust_score += count_score
        
        return round(trust_score, 1)
    
    def _calculate_sentiment_distribution(self, reviews: List[Review]) -> Dict[str, float]:
        """Calculate sentiment distribution percentages"""
        if not reviews:
            return {"positive": 0, "negative": 0, "neutral": 0}
        
        positive = sum(1 for r in reviews if r.rating >= 4)
        negative = sum(1 for r in reviews if r.rating <= 2)
        neutral = len(reviews) - positive - negative
        
        total = len(reviews)
        return {
            "positive": round(positive / total * 100, 1) if total > 0 else 0,
            "negative": round(negative / total * 100, 1) if total > 0 else 0,
            "neutral": round(neutral / total * 100, 1) if total > 0 else 0
        }
    
    def should_refresh_from_google(
        self,
        db_reviews: Optional[Dict[str, Any]],
        db_google_rating: Optional[float],
        google_place_details: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Determine if Google Places API refresh is needed
        
        According to SPEC v3.2:
        - Refresh if DB data is stale >30 days
        - Refresh if google_rating in DB differs from API
        """
        if not google_place_details:
            return False
        
        # Check if rating differs
        api_rating = google_place_details.get('rating')
        if api_rating and db_google_rating:
            if abs(float(api_rating) - float(db_google_rating)) > 0.1:
                return True
        
        # Check if DB data is stale (would need last_update date, simplified here)
        # In practice, this would check updated_at field from care_homes table
        # For now, we'll use the presence of reviews as a proxy
        
        if not db_reviews or not db_reviews.get('reviews'):
            return True  # No DB data, need refresh
        
        return False

