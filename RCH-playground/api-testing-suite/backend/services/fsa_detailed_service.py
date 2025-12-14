"""
FSA Detailed Service for Professional Report
Provides comprehensive FSA analysis per spec v3.0

Features:
- Breakdown by category (Hygiene, Structural, Management)
- Historical ratings (3-year trend)
- Dietary risk assessment
- Scoring integration (25 pts Safety & Quality)

Based on spec v3.0 PROFESSIONAL Report requirements:
- FSA FHRS Rating (0-7 pts in Safety category)
- 3-Year Trend analysis
- Dietary Risk Assessment for users with special requirements
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from enum import Enum
import asyncio


class TrendDirection(Enum):
    """Rating trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class DietaryRiskLevel(Enum):
    """Dietary management risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


@dataclass
class CategoryBreakdown:
    """FSA category breakdown"""
    category: str  # "hygiene", "structural", "management"
    raw_score: Optional[int]  # FSA penalty points (lower = better)
    normalized_score: Optional[float]  # 0-100 (higher = better)
    max_raw_score: int  # 20 for hygiene/structural, 30 for management
    label: str  # "Pass", "Improvement needed"
    weight: float  # Algorithm weight (0.40, 0.30, 0.30)
    points_awarded: float  # Points for algorithm (0-7)


@dataclass
class HistoricalRating:
    """Historical FSA rating entry"""
    date: str
    rating: int
    rating_label: str
    hygiene_score: Optional[int]
    structural_score: Optional[int]
    management_score: Optional[int]
    days_ago: int


@dataclass
class TrendAnalysis:
    """3-year FSA trend analysis"""
    direction: str  # "improving", "stable", "declining"
    direction_label: str  # "✓ IMPROVING", "→ STABLE", "⚠ DECLINING"
    current_rating: int
    oldest_rating: Optional[int]
    average_rating: float
    rating_change: int  # +1, 0, -1
    consistency: str  # "consistent", "variable"
    inspection_count: int
    last_inspection_date: Optional[str]
    days_since_inspection: Optional[int]
    prediction: Dict[str, Any]


@dataclass
class DietaryRiskAssessment:
    """Dietary management risk assessment"""
    risk_level: str  # "low", "medium", "high"
    risk_label: str  # "✓ Safe", "⚠ Monitor", "✗ Concern"
    confidence: str  # "high", "medium", "low"
    suitable_for: List[str]  # ["diabetic", "nut_allergy", etc.]
    concerns: List[str]
    recommendations: List[str]
    dietary_score: int  # 0-100


@dataclass
class FSADetailedResult:
    """Complete FSA detailed analysis for Professional Report"""
    fhrs_id: Optional[int]
    business_name: str
    address: Optional[str]
    postcode: Optional[str]
    local_authority: Optional[str]
    
    # Current rating
    current_rating: Optional[int]
    current_rating_label: str
    rating_date: Optional[str]
    days_since_inspection: Optional[int]
    
    # Category breakdown
    breakdown: List[CategoryBreakdown]
    overall_health_score: int  # 0-100
    health_score_label: str  # "EXCELLENT", "GOOD", etc.
    
    # Historical & Trend
    historical_ratings: List[HistoricalRating]
    trend_analysis: TrendAnalysis
    
    # Dietary assessment
    dietary_risk: DietaryRiskAssessment
    
    # Scoring
    algorithm_points: int  # 0-7 for Safety category
    algorithm_breakdown: Dict[str, float]
    
    # Issues & Recommendations
    issues: List[str]
    recommendations: List[str]
    
    # Metadata
    analysis_date: str
    data_freshness: str  # "current", "stale", "very_stale"


class FSADetailedService:
    """
    Service for detailed FSA analysis for Professional Report
    """
    
    def __init__(self):
        """Initialize service"""
        self._client = None
        self._enrichment_service = None
    
    async def _get_client(self):
        """Get FSA API client"""
        if self._client is None:
            from api_clients.fsa_client import FSAAPIClient
            self._client = FSAAPIClient()
        return self._client
    
    async def _get_enrichment_service(self):
        """Get FSA enrichment service"""
        if self._enrichment_service is None:
            from services.fsa_enrichment_service import FSAEnrichmentService
            self._enrichment_service = FSAEnrichmentService()
        return self._enrichment_service
    
    async def get_detailed_analysis(
        self,
        home_name: str,
        postcode: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        dietary_requirements: Optional[List[str]] = None
    ) -> FSADetailedResult:
        """
        Get detailed FSA analysis for a care home
        
        Args:
            home_name: Name of the care home
            postcode: Postcode of the care home
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            dietary_requirements: List of dietary requirements (e.g., ["diabetic", "nut_allergy"])
            
        Returns:
            FSADetailedResult with complete analysis
        """
        client = await self._get_client()
        enrichment = await self._get_enrichment_service()
        
        # Create home dict for enrichment
        home = {
            "name": home_name,
            "postcode": postcode,
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Enrich with FSA data
        enriched = await enrichment.enrich_care_home(home)
        
        # Extract FSA data
        fhrs_id = enriched.get("fsa_fhrs_id")
        current_rating = self._safe_int(enriched.get("fsa_rating"))
        rating_date = enriched.get("fsa_rating_date")
        fsa_breakdown = enriched.get("fsa_breakdown", {})
        health_score = enriched.get("fsa_health_score", {})
        historical = enriched.get("fsa_historical_ratings", [])
        
        # Calculate days since inspection
        days_since = self._calculate_days_since(rating_date)
        
        # Build category breakdown
        breakdown = self._build_category_breakdown(fsa_breakdown, health_score)
        
        # Build historical ratings
        historical_ratings = self._build_historical_ratings(historical)
        
        # Analyze trend
        trend_analysis = self._analyze_trend(
            current_rating, rating_date, historical_ratings
        )
        
        # Assess dietary risk
        dietary_risk = self._assess_dietary_risk(
            breakdown, current_rating, dietary_requirements or []
        )
        
        # Calculate algorithm points
        algorithm_points, algorithm_breakdown = self._calculate_algorithm_points(
            current_rating, breakdown, trend_analysis
        )
        
        # Collect issues
        issues = self._collect_issues(
            current_rating, days_since, breakdown, trend_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_rating, issues, dietary_requirements or []
        )
        
        # Determine data freshness
        if days_since is None:
            data_freshness = "unknown"
        elif days_since <= 365:
            data_freshness = "current"
        elif days_since <= 730:
            data_freshness = "stale"
        else:
            data_freshness = "very_stale"
        
        return FSADetailedResult(
            fhrs_id=fhrs_id,
            business_name=home_name,
            address=enriched.get("address"),
            postcode=postcode,
            local_authority=None,  # Would need separate lookup
            current_rating=current_rating,
            current_rating_label=self._rating_to_label(current_rating),
            rating_date=rating_date,
            days_since_inspection=days_since,
            breakdown=breakdown,
            overall_health_score=health_score.get("score", 0) if health_score else 0,
            health_score_label=health_score.get("label", "UNKNOWN") if health_score else "UNKNOWN",
            historical_ratings=historical_ratings,
            trend_analysis=trend_analysis,
            dietary_risk=dietary_risk,
            algorithm_points=algorithm_points,
            algorithm_breakdown=algorithm_breakdown,
            issues=issues,
            recommendations=recommendations,
            analysis_date=datetime.now().isoformat(),
            data_freshness=data_freshness
        )
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert to int"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.strip()
                if value.lower() == "exempt":
                    return 5  # Treat exempt as 5
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _calculate_days_since(self, date_str: Optional[str]) -> Optional[int]:
        """Calculate days since a date"""
        if not date_str:
            return None
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            else:
                date_obj = date_str
            return (date.today() - date_obj).days
        except:
            return None
    
    def _rating_to_label(self, rating: Optional[int]) -> str:
        """Convert rating to label"""
        if rating is None:
            return "Unknown"
        if rating == 5:
            return "Excellent (5/5)"
        elif rating == 4:
            return "Good (4/5)"
        elif rating == 3:
            return "Satisfactory (3/5)"
        elif rating == 2:
            return "Improvement Needed (2/5)"
        elif rating == 1:
            return "Major Improvement Needed (1/5)"
        elif rating == 0:
            return "Urgent Improvement Required (0/5)"
        else:
            return f"Rating: {rating}"
    
    def _score_to_pass_fail(self, score: Optional[int], max_score: int) -> str:
        """Convert FSA score to pass/fail label"""
        if score is None:
            return "Unknown"
        
        threshold = max_score * 0.5  # 50% threshold
        if score <= threshold * 0.3:  # Very low score = excellent
            return "Pass ✓"
        elif score <= threshold:  # Below threshold = pass
            return "Pass"
        else:
            return "Improvement needed"
    
    def _build_category_breakdown(
        self,
        fsa_breakdown: Dict,
        health_score: Dict
    ) -> List[CategoryBreakdown]:
        """Build category breakdown from FSA data"""
        breakdown = []
        
        # Health score breakdown
        hs_breakdown = health_score.get("breakdown", {}) if health_score else {}
        
        # Hygiene
        hygiene_raw = fsa_breakdown.get("hygiene")
        hygiene_norm = hs_breakdown.get("hygiene", {}).get("normalized")
        breakdown.append(CategoryBreakdown(
            category="hygiene",
            raw_score=self._safe_int(hygiene_raw),
            normalized_score=hygiene_norm,
            max_raw_score=20,
            label=self._score_to_pass_fail(self._safe_int(hygiene_raw), 20),
            weight=0.40,
            points_awarded=self._calculate_category_points(hygiene_norm, 0.40)
        ))
        
        # Structural
        structural_raw = fsa_breakdown.get("structural")
        structural_norm = hs_breakdown.get("structural", {}).get("normalized")
        breakdown.append(CategoryBreakdown(
            category="structural",
            raw_score=self._safe_int(structural_raw),
            normalized_score=structural_norm,
            max_raw_score=20,
            label=self._score_to_pass_fail(self._safe_int(structural_raw), 20),
            weight=0.30,
            points_awarded=self._calculate_category_points(structural_norm, 0.30)
        ))
        
        # Management
        management_raw = fsa_breakdown.get("confidence_in_management")
        management_norm = hs_breakdown.get("management", {}).get("normalized")
        breakdown.append(CategoryBreakdown(
            category="management",
            raw_score=self._safe_int(management_raw),
            normalized_score=management_norm,
            max_raw_score=30,
            label=self._score_to_pass_fail(self._safe_int(management_raw), 30),
            weight=0.30,
            points_awarded=self._calculate_category_points(management_norm, 0.30)
        ))
        
        return breakdown
    
    def _calculate_category_points(
        self,
        normalized_score: Optional[float],
        weight: float
    ) -> float:
        """Calculate points for a category"""
        if normalized_score is None:
            return 0.0
        # Max 7 points total for FSA in algorithm
        max_points = 7.0
        return round((normalized_score / 100) * max_points * weight, 2)
    
    def _build_historical_ratings(
        self,
        historical: List[Dict]
    ) -> List[HistoricalRating]:
        """Build historical ratings list"""
        result = []
        today = date.today()
        
        for entry in historical:
            rating_date_str = entry.get("date")
            days_ago = self._calculate_days_since(rating_date_str) or 0
            
            rating = self._safe_int(entry.get("rating"))
            breakdown = entry.get("breakdown_scores", {})
            
            result.append(HistoricalRating(
                date=rating_date_str or "",
                rating=rating or 0,
                rating_label=self._rating_to_label(rating),
                hygiene_score=self._safe_int(breakdown.get("hygiene")),
                structural_score=self._safe_int(breakdown.get("structural")),
                management_score=self._safe_int(breakdown.get("confidence_in_management")),
                days_ago=days_ago
            ))
        
        # Sort by date (most recent first)
        result.sort(key=lambda x: x.days_ago)
        
        return result
    
    def _analyze_trend(
        self,
        current_rating: Optional[int],
        rating_date: Optional[str],
        historical: List[HistoricalRating]
    ) -> TrendAnalysis:
        """Analyze 3-year rating trend"""
        # Filter to last 3 years (1095 days)
        three_years = [h for h in historical if h.days_ago <= 1095]
        
        if not three_years:
            return TrendAnalysis(
                direction="unknown",
                direction_label="? UNKNOWN",
                current_rating=current_rating or 0,
                oldest_rating=None,
                average_rating=float(current_rating or 0),
                rating_change=0,
                consistency="unknown",
                inspection_count=0,
                last_inspection_date=rating_date,
                days_since_inspection=self._calculate_days_since(rating_date),
                prediction={"predicted_rating": current_rating, "confidence": "low"}
            )
        
        ratings = [h.rating for h in three_years if h.rating]
        oldest_rating = three_years[-1].rating if three_years else None
        
        # Calculate direction
        if len(ratings) >= 2:
            if ratings[0] > ratings[-1]:
                direction = "improving"
                direction_label = "✓ IMPROVING"
            elif ratings[0] < ratings[-1]:
                direction = "declining"
                direction_label = "⚠ DECLINING"
            else:
                direction = "stable"
                direction_label = "→ STABLE"
        else:
            direction = "stable"
            direction_label = "→ STABLE"
        
        # Calculate consistency
        unique_ratings = set(ratings)
        consistency = "consistent" if len(unique_ratings) <= 1 else "variable"
        
        # Rating change
        rating_change = (current_rating or 0) - (oldest_rating or 0)
        
        # Prediction
        if direction == "improving":
            predicted = min(5, (current_rating or 0) + 1)
        elif direction == "declining":
            predicted = max(0, (current_rating or 0) - 1)
        else:
            predicted = current_rating
        
        return TrendAnalysis(
            direction=direction,
            direction_label=direction_label,
            current_rating=current_rating or 0,
            oldest_rating=oldest_rating,
            average_rating=sum(ratings) / len(ratings) if ratings else 0,
            rating_change=rating_change,
            consistency=consistency,
            inspection_count=len(three_years),
            last_inspection_date=rating_date,
            days_since_inspection=self._calculate_days_since(rating_date),
            prediction={
                "predicted_rating": predicted,
                "confidence": "high" if direction == "stable" else "medium"
            }
        )
    
    def _assess_dietary_risk(
        self,
        breakdown: List[CategoryBreakdown],
        current_rating: Optional[int],
        dietary_requirements: List[str]
    ) -> DietaryRiskAssessment:
        """Assess dietary management risk"""
        concerns = []
        recommendations = []
        suitable_for = []
        
        # Get hygiene score
        hygiene = next((b for b in breakdown if b.category == "hygiene"), None)
        management = next((b for b in breakdown if b.category == "management"), None)
        
        # Calculate dietary score
        dietary_score = 0
        
        # Rating contribution (40 points)
        if current_rating is not None:
            if current_rating >= 4:
                dietary_score += current_rating * 8  # 32-40 points
            elif current_rating >= 3:
                dietary_score += 20
            else:
                concerns.append("Low overall FSA rating - dietary management may be compromised")
        
        # Hygiene contribution (30 points)
        if hygiene and hygiene.raw_score is not None:
            if hygiene.raw_score <= 5:
                dietary_score += 30
                suitable_for.extend(["diabetic", "pureed_diet"])
            elif hygiene.raw_score <= 10:
                dietary_score += 20
                suitable_for.append("diabetic")
            elif hygiene.raw_score <= 15:
                dietary_score += 10
            else:
                concerns.append("Hygiene score below acceptable threshold for special diets")
        
        # Management contribution (20 points)
        if management and management.raw_score is not None:
            if management.raw_score <= 5:
                dietary_score += 20
                suitable_for.append("nut_allergy")
            elif management.raw_score <= 10:
                dietary_score += 15
            elif management.raw_score <= 15:
                dietary_score += 10
            else:
                concerns.append("Management practices may not support complex dietary needs")
        
        # Recency contribution (10 points)
        # Already factored into other scores
        dietary_score += 5  # Base points
        
        # Cap at 100
        dietary_score = min(100, dietary_score)
        
        # Determine risk level
        if dietary_score >= 80:
            risk_level = "low"
            risk_label = "✓ Safe"
            confidence = "high"
        elif dietary_score >= 60:
            risk_level = "medium"
            risk_label = "⚠ Monitor"
            confidence = "medium"
            if not concerns:
                concerns.append("Some dietary requirements may need additional verification")
        else:
            risk_level = "high"
            risk_label = "✗ Concern"
            confidence = "medium"
            if not concerns:
                concerns.append("Dietary management capability unclear - verify directly with home")
        
        # Generate recommendations based on requirements
        if "diabetic" in dietary_requirements:
            if dietary_score >= 70:
                suitable_for.append("diabetic")
                recommendations.append("Verified: Kitchen can manage diabetic diet requirements")
            else:
                concerns.append("Verify diabetic meal preparation protocols directly")
                recommendations.append("Request diabetic menu samples during visit")
        
        if "nut_allergy" in dietary_requirements:
            if dietary_score >= 80 and management and management.raw_score and management.raw_score <= 5:
                suitable_for.append("nut_allergy")
                recommendations.append("Good management practices for allergen control")
            else:
                concerns.append("Verify allergen separation protocols")
                recommendations.append("Ask about cross-contamination prevention measures")
        
        if "pureed_diet" in dietary_requirements:
            if hygiene and hygiene.raw_score and hygiene.raw_score <= 5:
                suitable_for.append("pureed_diet")
                recommendations.append("Kitchen meets hygiene standards for modified textures")
            else:
                recommendations.append("Verify texture modification capabilities")
        
        # Remove duplicates
        suitable_for = list(set(suitable_for))
        
        return DietaryRiskAssessment(
            risk_level=risk_level,
            risk_label=risk_label,
            confidence=confidence,
            suitable_for=suitable_for,
            concerns=concerns,
            recommendations=recommendations,
            dietary_score=dietary_score
        )
    
    def _calculate_algorithm_points(
        self,
        current_rating: Optional[int],
        breakdown: List[CategoryBreakdown],
        trend: TrendAnalysis
    ) -> Tuple[int, Dict[str, float]]:
        """
        Calculate algorithm points for Safety & Quality category
        
        FSA contribution: 0-7 points out of 25 total Safety points
        """
        points_breakdown = {}
        
        # Base rating points (0-3)
        if current_rating is not None:
            if current_rating == 5:
                rating_points = 3.0
            elif current_rating == 4:
                rating_points = 2.0
            elif current_rating == 3:
                rating_points = 1.0
            else:
                rating_points = 0.0
        else:
            rating_points = 0.0
        points_breakdown["rating"] = rating_points
        
        # Consistency bonus (0-2)
        if trend.consistency == "consistent" and current_rating and current_rating >= 4:
            consistency_points = 2.0
        elif trend.consistency == "consistent":
            consistency_points = 1.0
        else:
            consistency_points = 0.0
        points_breakdown["consistency"] = consistency_points
        
        # Trend bonus (0-2)
        if trend.direction == "improving":
            trend_points = 2.0
        elif trend.direction == "stable" and current_rating and current_rating >= 4:
            trend_points = 1.0
        elif trend.direction == "declining":
            trend_points = -1.0  # Penalty
        else:
            trend_points = 0.0
        points_breakdown["trend"] = trend_points
        
        # Calculate total (0-7)
        total = max(0, min(7, rating_points + consistency_points + trend_points))
        
        return int(total), points_breakdown
    
    def _collect_issues(
        self,
        current_rating: Optional[int],
        days_since: Optional[int],
        breakdown: List[CategoryBreakdown],
        trend: TrendAnalysis
    ) -> List[str]:
        """Collect FSA-related issues"""
        issues = []
        
        # Rating issues
        if current_rating is not None:
            if current_rating <= 2:
                issues.append(f"FSA rating {current_rating}/5 - Improvement needed")
            elif current_rating == 3:
                issues.append("FSA rating 3/5 - Satisfactory but not ideal")
        else:
            issues.append("No FSA rating data available")
        
        # Freshness issues
        if days_since is not None:
            if days_since > 730:
                issues.append(f"FSA inspection over 2 years ago ({days_since} days)")
            elif days_since > 550:
                issues.append(f"FSA inspection over 18 months ago ({days_since} days)")
        
        # Category issues
        for cat in breakdown:
            if cat.raw_score is not None:
                if cat.category == "hygiene" and cat.raw_score > 10:
                    issues.append("Hygiene score needs improvement")
                elif cat.category == "structural" and cat.raw_score > 10:
                    issues.append("Structural requirements need attention")
                elif cat.category == "management" and cat.raw_score > 15:
                    issues.append("Food safety management needs improvement")
        
        # Trend issues
        if trend.direction == "declining":
            issues.append("FSA rating trend is declining - monitor closely")
        
        return issues
    
    def _generate_recommendations(
        self,
        current_rating: Optional[int],
        issues: List[str],
        dietary_requirements: List[str]
    ) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        if not issues:
            recommendations.append("FSA hygiene standards are excellent")
        
        if current_rating and current_rating >= 4:
            recommendations.append("Suitable for special dietary requirements")
        elif current_rating and current_rating == 3:
            recommendations.append("Verify dietary capability during visit")
        else:
            recommendations.append("Request kitchen inspection during visit")
        
        if dietary_requirements:
            recommendations.append(f"Confirm capability for: {', '.join(dietary_requirements)}")
        
        return recommendations
    
    def to_scoring_data(self, result: FSADetailedResult) -> Dict:
        """
        Convert result to data format for 156-point algorithm
        
        Returns dict for Safety & Quality category (FSA portion: 7 pts)
        """
        return {
            'fsa_rating': result.current_rating,
            'fsa_points': result.algorithm_points,
            'fsa_health_score': result.overall_health_score,
            'fsa_trend': result.trend_analysis.direction,
            'fsa_consistency': result.trend_analysis.consistency,
            'fsa_days_since': result.days_since_inspection,
            'fsa_issues_count': len(result.issues),
            'dietary_risk_level': result.dietary_risk.risk_level,
            'dietary_score': result.dietary_risk.dietary_score
        }
    
    def to_report_section(self, result: FSADetailedResult) -> Dict:
        """
        Convert result to Professional Report section format
        
        Returns formatted section for PDF/HTML report
        """
        return {
            'title': 'FSA Food Hygiene Assessment',
            'establishment': {
                'name': result.business_name,
                'fhrs_id': result.fhrs_id,
                'address': result.address,
                'postcode': result.postcode,
                'local_authority': result.local_authority
            },
            'current_rating': {
                'value': result.current_rating,
                'label': result.current_rating_label,
                'date': result.rating_date,
                'days_since': result.days_since_inspection,
                'freshness': result.data_freshness
            },
            'health_score': {
                'score': result.overall_health_score,
                'label': result.health_score_label,
                'max': 100
            },
            'breakdown': [
                {
                    'category': cat.category.title(),
                    'status': cat.label,
                    'raw_score': f"{cat.raw_score}/{cat.max_raw_score}" if cat.raw_score else "N/A",
                    'normalized': f"{cat.normalized_score:.0f}%" if cat.normalized_score else "N/A",
                    'weight': f"{cat.weight * 100:.0f}%"
                }
                for cat in result.breakdown
            ],
            'trend': {
                'direction': result.trend_analysis.direction,
                'label': result.trend_analysis.direction_label,
                'history_years': 3,
                'inspection_count': result.trend_analysis.inspection_count,
                'rating_change': result.trend_analysis.rating_change,
                'consistency': result.trend_analysis.consistency
            },
            'historical_ratings': [
                {
                    'date': h.date,
                    'rating': h.rating,
                    'label': h.rating_label
                }
                for h in result.historical_ratings[:5]  # Last 5 inspections
            ],
            'dietary_assessment': {
                'risk_level': result.dietary_risk.risk_level,
                'risk_label': result.dietary_risk.risk_label,
                'score': result.dietary_risk.dietary_score,
                'suitable_for': result.dietary_risk.suitable_for,
                'concerns': result.dietary_risk.concerns,
                'recommendations': result.dietary_risk.recommendations
            },
            'algorithm': {
                'points': result.algorithm_points,
                'max_points': 7,
                'breakdown': result.algorithm_breakdown
            },
            'issues': result.issues,
            'recommendations': result.recommendations,
            'analysis_date': result.analysis_date
        }


async def enrich_care_home_with_fsa_detailed(
    home_name: str,
    postcode: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    dietary_requirements: Optional[List[str]] = None
) -> Optional[Dict]:
    """
    Convenience function to enrich a care home with detailed FSA data
    
    Args:
        home_name: Name of the care home
        postcode: Optional postcode
        latitude: Optional latitude
        longitude: Optional longitude
        dietary_requirements: List of dietary requirements
        
    Returns:
        FSA detailed data dict or None if not found
    """
    service = FSADetailedService()
    
    try:
        result = await service.get_detailed_analysis(
            home_name, postcode, latitude, longitude, dietary_requirements
        )
        
        return {
            'scoring_data': service.to_scoring_data(result),
            'report_section': service.to_report_section(result),
            'raw_result': asdict(result)
        }
    except Exception as e:
        print(f"FSA detailed analysis failed for {home_name}: {e}")
        return None
