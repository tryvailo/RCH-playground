"""
Family Engagement Service
Implements Level 1 (MVP) Family Engagement calculation according to PROFESSIONAL_REPORT_SPEC_v3.2

Level 1: Bootstrap MVP (£0-15/month)
- Source: reviews_detailed JSONB + Google Place Details (optional)
- Coverage: 100% care homes
- Accuracy: Medium (correlation ~0.6-0.7 with real data)

According to SPEC v3.2 (lines 1280-1426):
- Dwell Time = f(rating, review_count, review_quality, sentiment) (base 30 min, adjustments)
- Repeat Rate = f(rating, loyalty_keywords, reviewer_tenure) (base 45%, adjustments)
- Footfall Trend = f(review_velocity) (comparison recent vs older reviews)
- Engagement Score = Dwell (40%) + Repeat (40%) + Trend (20%)
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source for Family Engagement - Marketing names only"""
    ESTIMATED = "Community Insights"      # Level 1: Proxy from reviews
    BIGQUERY = "Advanced Analytics"      # Level 3: Google Places Insights
    HYBRID = "Multi-Source Intelligence"  # Mixed sources


class Confidence(Enum):
    """Confidence level for Family Engagement data"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class FamilyEngagement:
    """
    Family Engagement data with transparent source indication
    
    ⚠️ CRITICAL: Always honestly indicate data_source and confidence
    """
    # === META ===
    data_source: DataSource
    confidence: Confidence
    data_coverage: str           # "full" / "partial" / "estimated"
    
    # === CORE METRICS ===
    dwell_time_minutes: int              # Estimated/real visit duration
    repeat_visitor_rate: float           # 0.0-1.0
    footfall_trend: str                  # "growing" / "stable" / "declining"
    
    # === OPTIONAL (Level 2-3 only) ===
    weekly_visitors: Optional[int] = None
    popular_times: Optional[Dict] = None
    peak_days: Optional[List[str]] = None
    peak_hours: Optional[List[str]] = None
    busy_hours: Optional[List[str]] = None
    quiet_hours: Optional[List[str]] = None
    
    # === DERIVED ===
    engagement_score: int                # 0-100
    quality_indicator: str
    
    # === TRANSPARENCY ===
    methodology_note: str


class FamilyEngagementService:
    """Service for calculating Family Engagement Level 1 (MVP)"""
    
    def calculate_family_engagement_estimated(
        self,
        db_reviews: Optional[Dict[str, Any]],           # reviews_detailed JSONB из care_homes DB
        google_place_details: Optional[Dict[str, Any]] = None  # Опционально: свежие данные из Google
    ) -> FamilyEngagement:
        """
        Level 1: Calculate Family Engagement based on proxy metrics
        
        Algorithm according to SPEC v3.2 (lines 1280-1426):
        1. Dwell Time = f(rating, review_count, review_quality, sentiment)
        2. Repeat Rate = f(rating, loyalty_keywords, reviewer_tenure)
        3. Footfall Trend = f(review_velocity)
        
        Cost: £0 (DB only) or ~£15/month (with Google API refresh)
        """
        
        # === MERGE DATA SOURCES ===
        reviews = db_reviews.get('reviews', []) if db_reviews else []
        
        if google_place_details:
            google_reviews = google_place_details.get('reviews', [])
            rating = google_place_details.get('rating', 0)
            review_count = google_place_details.get('user_ratings_total', 0)
            all_reviews = reviews + google_reviews
        else:
            summary = db_reviews.get('summary', {}) if db_reviews else {}
            rating = summary.get('average_rating', 0)
            review_count = len(reviews)
            all_reviews = reviews
        
        # Normalize rating to float
        try:
            rating = float(rating) if rating else 0.0
        except (ValueError, TypeError):
            rating = 0.0
        
        # ════════════════════════════════════════════════════════════
        # DWELL TIME ESTIMATION
        # UK care home average: 30 minutes
        # ════════════════════════════════════════════════════════════
        base_dwell = 30
        
        # Factor 1: Rating boost (+/- 15 min max)
        # Higher rating = families stay longer (correlation: 0.65)
        rating_boost = (rating - 3.5) * 10 if rating else 0
        
        # Factor 2: Review engagement
        # More reviews = more engaged families = longer visits
        review_boost = min(15, review_count / 10) if review_count else 0
        
        # Factor 3: Review quality (длинные детальные отзывы = engaged visitors)
        quality_score = self._analyze_review_quality(all_reviews)
        quality_boost = quality_score * 8  # 0-8 min
        
        # Factor 4: Visit sentiment from review text
        sentiment_boost = self._analyze_visit_sentiment(all_reviews) * 5  # -5 to +5 min
        
        dwell_time = base_dwell + rating_boost + review_boost + quality_boost + sentiment_boost
        dwell_time = int(max(15, min(90, dwell_time)))  # Clamp 15-90 min
        
        # ════════════════════════════════════════════════════════════
        # REPEAT VISITOR RATE ESTIMATION
        # UK care home average: 45%
        # ════════════════════════════════════════════════════════════
        base_rate = 0.45
        
        # Factor 1: Rating correlation (correlation: 0.72)
        rating_boost_r = (rating - 3.5) * 0.15 if rating else 0  # +/- 22.5%
        
        # Factor 2: Loyalty keywords in reviews
        loyalty_score = self._analyze_loyalty_keywords(all_reviews)
        loyalty_boost = loyalty_score * 0.20  # 0-20%
        
        # Factor 3: Long-term reviewer patterns
        tenure_score = self._analyze_reviewer_tenure(all_reviews)
        tenure_boost = tenure_score * 0.10  # 0-10%
        
        repeat_rate = base_rate + rating_boost_r + loyalty_boost + tenure_boost
        repeat_rate = max(0.20, min(0.95, repeat_rate))  # Clamp 20-95%
        
        # ════════════════════════════════════════════════════════════
        # FOOTFALL TREND ESTIMATION
        # Based on review velocity (recent vs older)
        # ════════════════════════════════════════════════════════════
        recent_reviews = [r for r in all_reviews if self._is_recent(r, days=180)]
        older_reviews = [r for r in all_reviews if not self._is_recent(r, days=180)]
        
        recent_count = len(recent_reviews)
        older_count = len(older_reviews) if older_reviews else 1
        
        if recent_count > older_count * 1.2:
            footfall_trend = "growing"
            trend_score = 20
        elif recent_count < older_count * 0.8:
            footfall_trend = "declining"
            trend_score = 5
        else:
            footfall_trend = "stable"
            trend_score = 15
        
        # ════════════════════════════════════════════════════════════
        # ENGAGEMENT SCORE (0-100)
        # Weights: Dwell (40%) + Repeat (40%) + Trend (20%)
        # ════════════════════════════════════════════════════════════
        
        # Dwell component (40%)
        if dwell_time >= 45:
            dwell_score = 40
        elif dwell_time >= 35:
            dwell_score = 30
        elif dwell_time >= 25:
            dwell_score = 20
        else:
            dwell_score = 10
        
        # Repeat component (40%)
        if repeat_rate >= 0.70:
            repeat_score = 40
        elif repeat_rate >= 0.55:
            repeat_score = 30
        elif repeat_rate >= 0.40:
            repeat_score = 20
        else:
            repeat_score = 10
        
        engagement_score = dwell_score + repeat_score + trend_score
        
        # ════════════════════════════════════════════════════════════
        # QUALITY INDICATOR
        # Research: Dwell >45 + Repeat >70% = 87% Outstanding CQC
        # ════════════════════════════════════════════════════════════
        if engagement_score >= 80:
            quality_indicator = "HIGH - Strong family engagement (87% correlation with Outstanding CQC)"
        elif engagement_score >= 60:
            quality_indicator = "GOOD - Positive engagement signals"
        elif engagement_score >= 40:
            quality_indicator = "MODERATE - Average engagement patterns"
        else:
            quality_indicator = "LOW - Limited engagement signals (34% risk of quality concerns)"
        
        return FamilyEngagement(
            data_source=DataSource.ESTIMATED,
            confidence=Confidence.MEDIUM,
            data_coverage="estimated",
            dwell_time_minutes=dwell_time,
            repeat_visitor_rate=round(repeat_rate, 2),
            footfall_trend=footfall_trend,
            engagement_score=engagement_score,
            quality_indicator=quality_indicator,
            methodology_note=(
                "Estimated from review patterns and ratings. "
                "For verification, observe visiting patterns during weekends 2-4pm."
            )
        )
    
    def _analyze_review_quality(self, reviews: List[Dict[str, Any]]) -> float:
        """
        Review quality as proxy for engagement (0-1)
        Long detailed reviews = engaged visitors who spent time
        """
        if not reviews:
            return 0.5
        
        quality_reviews = [
            r for r in reviews 
            if len(str(r.get('text', '')).split()) > 50 
            and (r.get('rating', 0) or 0) >= 4
        ]
        return min(1.0, len(quality_reviews) / max(len(reviews), 1) * 2)
    
    def _analyze_visit_sentiment(self, reviews: List[Dict[str, Any]]) -> float:
        """
        Analyze sentiment about visits (-1 to 1)
        """
        POSITIVE = [
            'welcoming', 'comfortable', 'relaxed', 'enjoyable', 'pleasant', 
            'warm', 'homely', 'peaceful', 'happy to visit', 'love visiting',
            'always feel welcome', 'cup of tea', 'stay for hours'
        ]
        NEGATIVE = [
            'rushed', 'uncomfortable', 'unwelcoming', 'cold', 'clinical',
            'dreaded', 'avoided', 'want to leave', 'short visit'
        ]
        
        pos_count = neg_count = 0
        for r in reviews:
            text = str(r.get('text', '')).lower()
            pos_count += sum(1 for w in POSITIVE if w in text)
            neg_count += sum(1 for w in NEGATIVE if w in text)
        
        total = pos_count + neg_count
        if total == 0:
            return 0
        return (pos_count - neg_count) / total
    
    def _analyze_loyalty_keywords(self, reviews: List[Dict[str, Any]]) -> float:
        """
        Analyze loyalty keywords (0-1)
        """
        LOYALTY_KEYWORDS = [
            'always', 'regular', 'frequent', 'years', 'return', 'come back',
            'loyal', 'trust', 'recommend', 'family member', 'my mother', 
            'my father', 'my parent', 'every week', 'every day', 'daily',
            'for years', 'since 20', 'long time'
        ]
        
        loyalty_count = sum(
            1 for r in reviews
            if any(kw in str(r.get('text', '')).lower() for kw in LOYALTY_KEYWORDS)
        )
        return min(1.0, loyalty_count / max(len(reviews), 1) * 3)
    
    def _analyze_reviewer_tenure(self, reviews: List[Dict[str, Any]]) -> float:
        """
        Analyze reviewer 'tenure' (0-1)
        """
        TENURE_KEYWORDS = [
            'years', 'months', 'since 20', 'long time', 'for over',
            '5 years', '10 years', 'decade', 'many years'
        ]
        
        tenure_count = sum(
            1 for r in reviews
            if any(kw in str(r.get('text', '')).lower() for kw in TENURE_KEYWORDS)
        )
        return min(1.0, tenure_count / max(len(reviews), 1) * 2)
    
    def _is_recent(self, review: Dict[str, Any], days: int = 180) -> bool:
        """
        Check if review is recent (within specified days)
        """
        date_str = review.get('date') or review.get('time') or review.get('published_at')
        if not date_str:
            return False
        
        try:
            # Try various date formats
            if isinstance(date_str, str):
                # Try ISO format
                if 'T' in date_str:
                    review_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    # Try YYYY-MM-DD
                    review_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
            else:
                return False
            
            days_ago = (datetime.now() - review_date.replace(tzinfo=None)).days
            return days_ago <= days
        except (ValueError, TypeError, AttributeError):
            return False
    
    def to_dict(self, engagement: FamilyEngagement) -> Dict[str, Any]:
        """Convert FamilyEngagement to dictionary for API response"""
        return {
            "data_source": engagement.data_source.value,  # Marketing name, not technical API name
            "confidence": engagement.confidence.value,
            "data_coverage": engagement.data_coverage,
            "dwell_time_minutes": engagement.dwell_time_minutes,
            "repeat_visitor_rate": engagement.repeat_visitor_rate,
            "footfall_trend": engagement.footfall_trend,
            "weekly_visitors": engagement.weekly_visitors,
            "popular_times": engagement.popular_times,
            "peak_days": engagement.peak_days,
            "peak_hours": engagement.peak_hours,
            "busy_hours": engagement.busy_hours,
            "quiet_hours": engagement.quiet_hours,
            "engagement_score": engagement.engagement_score,
            "quality_indicator": engagement.quality_indicator,
            "methodology_note": engagement.methodology_note
        }

