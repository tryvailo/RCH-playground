"""
CQC Enrichment Service
Enriches care home data with detailed CQC information including:
- Historical ratings (3-5 years)
- 5 detailed ratings with explanations
- Active improvement plans
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from api_clients.cqc_client import CQCAPIClient

logger = logging.getLogger(__name__)


class CQCEnrichmentService:
    """Service for enriching care home data with detailed CQC information"""
    
    def __init__(self, cqc_client: Optional[CQCAPIClient] = None):
        """
        Initialize CQC Enrichment Service
        
        Args:
            cqc_client: Optional CQC API client instance. If None, creates a new one.
        """
        self.cqc_client = cqc_client or CQCAPIClient()
    
    async def enrich_cqc_data(
        self,
        location_id: str,
        years: int = 5
    ) -> Dict[str, Any]:
        """
        Enrich care home data with comprehensive CQC information.
        
        Args:
            location_id: CQC location ID
            years: Number of years for historical data (default 5)
        
        Returns:
            Dict with enriched CQC data:
            - overall_rating: Current overall rating
            - detailed_ratings: 5 key question ratings
            - historical_ratings: Historical ratings over time
            - trend: Rating trend (improving/declining/stable)
            - action_plans: Active improvement plans
            - inspection_dates: Key inspection dates
        """
        try:
            # Get location details
            location = await self.cqc_client.get_location(location_id)
            
            # Extract current ratings
            current_ratings = location.get("currentRatings", {})
            overall = current_ratings.get("overall", {})
            
            # Get 5 detailed ratings
            detailed_ratings = self._extract_detailed_ratings(current_ratings)
            
            # Get historical ratings
            historical_data = await self.cqc_client.get_location_historical_ratings(
                location_id, 
                years=years
            )
            
            # Get action plans
            action_plans = await self.cqc_client.get_location_action_plans(location_id)
            
            # Extract inspection dates
            inspection_dates = self._extract_inspection_dates(location)
            
            # Build enriched data structure
            enriched_data = {
                "overall_rating": overall.get("rating"),
                "overall_report_date": overall.get("reportDate"),
                "overall_report_id": overall.get("reportLinkId"),
                
                "detailed_ratings": detailed_ratings,
                
                "historical_ratings": historical_data.get("historical_ratings", []),
                "trend": historical_data.get("trend", "stable"),
                "rating_changes": historical_data.get("rating_changes", []),
                "years_covered": historical_data.get("years_covered", years),
                
                "action_plans": action_plans,
                "active_action_plans_count": len([ap for ap in action_plans if ap.get("status") == "Active"]),
                
                "inspection_dates": inspection_dates,
                "last_inspection_date": inspection_dates.get("last_inspection"),
                "next_inspection_due": inspection_dates.get("next_inspection_due"),
                
                "safeguarding_incidents": self._extract_safeguarding_incidents(location),
                
                "location_id": location_id,
                "enrichment_date": datetime.now().isoformat()
            }
            
            logger.info(f"CQC data enriched for location {location_id}: "
                       f"rating={enriched_data['overall_rating']}, "
                       f"trend={enriched_data['trend']}, "
                       f"action_plans={enriched_data['active_action_plans_count']}")
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriching CQC data for location {location_id}: {str(e)}")
            # Return minimal structure on error
            return {
                "overall_rating": None,
                "detailed_ratings": {},
                "historical_ratings": [],
                "trend": "unknown",
                "action_plans": [],
                "error": str(e)
            }
    
    def _extract_detailed_ratings(self, current_ratings: Dict) -> Dict[str, Dict[str, Any]]:
        """
        Extract 5 detailed ratings with explanations.
        
        Returns:
            Dict with keys: safe, effective, caring, responsive, well_led
            Each contains: rating, report_date, report_id, explanation
        """
        detailed = {}
        overall = current_ratings.get("overall", {})
        key_questions = overall.get("keyQuestionRatings", [])
        
        # Rating explanations
        rating_explanations = {
            "Outstanding": "Exceptional quality of care and service delivery",
            "Good": "Meets all expected standards of quality care",
            "Requires improvement": "Does not meet all standards; improvements needed",
            "Inadequate": "Fails to meet fundamental standards; urgent action required"
        }
        
        for kq in key_questions:
            name = kq.get("name", "")
            rating = kq.get("rating")
            report_date = kq.get("reportDate")
            report_id = kq.get("reportLinkId")
            
            if not rating or rating in ["Do not include in report", "No published rating"]:
                continue
            
            # Normalize name to key
            key = name.lower().replace(" ", "_")
            
            detailed[key] = {
                "rating": rating,
                "report_date": report_date,
                "report_id": report_id,
                "explanation": rating_explanations.get(rating, "Rating information available")
            }
        
        # Ensure all 5 ratings are present (use overall if missing)
        required_ratings = ["safe", "effective", "caring", "responsive", "well_led"]
        overall_rating = overall.get("rating")
        overall_date = overall.get("reportDate")
        overall_id = overall.get("reportLinkId")
        
        for key in required_ratings:
            if key not in detailed:
                detailed[key] = {
                    "rating": overall_rating,
                    "report_date": overall_date,
                    "report_id": overall_id,
                    "explanation": rating_explanations.get(overall_rating, "Rating information available")
                }
        
        return detailed
    
    def _extract_inspection_dates(self, location: Dict) -> Dict[str, Optional[str]]:
        """Extract key inspection dates from location data"""
        last_inspection = location.get("lastInspection", {})
        last_report = location.get("lastReport", {})
        
        return {
            "last_inspection": last_inspection.get("date"),
            "last_report_publication": last_report.get("publicationDate"),
            "next_inspection_due": self._estimate_next_inspection_due(last_inspection.get("date"))
        }
    
    def _estimate_next_inspection_due(self, last_inspection_date: Optional[str]) -> Optional[str]:
        """
        Estimate next inspection due date.
        
        CQC typically inspects:
        - Outstanding/Good: Every 2-3 years
        - Requires improvement: Every 12-18 months
        - Inadequate: Every 6-12 months
        """
        if not last_inspection_date:
            return None
        
        try:
            last_dt = datetime.strptime(last_inspection_date, "%Y-%m-%d")
            # Default to 2 years (most common)
            next_dt = last_dt.replace(year=last_dt.year + 2)
            return next_dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
    
    def _extract_safeguarding_incidents(self, location: Dict) -> int:
        """
        Extract safeguarding incidents count.
        
        Note: This information may not be directly available in CQC API.
        In production, this might require parsing reports or using additional data sources.
        """
        # For now, return 0 as this data is not directly available
        # In production, could parse reports or use other sources
        return 0
    
    async def close(self):
        """Close CQC client connection"""
        if self.cqc_client:
            await self.cqc_client.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

