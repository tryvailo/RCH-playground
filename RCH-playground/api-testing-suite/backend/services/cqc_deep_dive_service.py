"""
CQC Deep Dive Service
Implements Section 6: CQC Deep Dive according to PROFESSIONAL_REPORT_SPEC_v3.2

Provides:
- Inspection history (5+ years)
- Enforcement actions (red flags)
- Provider-level pattern detection
- Rating trend calculation
- Regulated activities parsing
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import date, datetime
import logging
from api_clients.cqc_client import CQCAPIClient

logger = logging.getLogger(__name__)


@dataclass
class RegulatedActivity:
    """Regulated Activity according to PROFESSIONAL_REPORT_SPEC_v3.2"""
    id: str  # e.g., "accommodation_nursing"
    name: str  # e.g., "Accommodation for persons who require nursing..."
    active: bool
    cqc_field: str  # Original CQC field name


@dataclass
class CQCDeepDive:
    """CQC Deep Dive data structure according to PROFESSIONAL_REPORT_SPEC_v3.2"""
    # Current Ratings
    overall: str  # "Outstanding" / "Good" / "Requires improvement" / "Inadequate"
    safe: str
    effective: str
    caring: str
    responsive: str
    well_led: str
    
    # Dates
    last_inspection_date: Optional[date]
    publication_date: Optional[date]
    report_url: Optional[str]
    
    # Regulated Activities (from JSONB)
    regulated_activities: List[RegulatedActivity]
    
    # Quick flags
    has_nursing_care_license: bool
    has_personal_care_license: bool
    has_surgical_procedures_license: bool
    has_treatment_license: bool
    has_diagnostic_license: bool
    
    # Derived
    days_since_inspection: Optional[int]
    rating_trend: str  # "Improving" / "Stable" / "Declining" / "Insufficient data"
    
    # Enrichment from CQC API
    inspection_history: List[Dict[str, Any]]  # Full history 5+ years
    enforcement_actions: List[Dict[str, Any]]  # Warning notices, conditions
    provider_locations: Optional[List[Dict[str, Any]]]  # All provider locations for pattern detection


class CQCDeepDiveService:
    """Service for building CQC Deep Dive data according to SPEC v3.2"""
    
    def __init__(self, cqc_client: Optional[CQCAPIClient] = None):
        """
        Initialize CQC Deep Dive Service
        
        Args:
            cqc_client: Optional CQC API client instance. If None, creates a new one.
        """
        self.cqc_client = cqc_client or CQCAPIClient()
    
    def calculate_rating_trend(
        self,
        current_rating: str,
        inspection_history: List[Dict[str, Any]]
    ) -> str:
        """
        Calculate rating trend according to PROFESSIONAL_REPORT_SPEC_v3.2 (lines 392-430)
        
        Args:
            current_rating: Current overall rating
            inspection_history: List of inspection records from CQC API
            
        Returns:
            "Improving" / "Stable" / "Declining" / "Insufficient data"
        """
        RATING_ORDER = {
            "Inadequate": 1,
            "Requires improvement": 2,
            "Good": 3,
            "Outstanding": 4
        }
        
        if len(inspection_history) < 2:
            return "Insufficient data"
        
        # Sort by date (newest first)
        sorted_history = sorted(
            inspection_history,
            key=lambda x: self._parse_inspection_date(x),
            reverse=True
        )
        
        current = RATING_ORDER.get(
            str(sorted_history[0].get('overall') or sorted_history[0].get('overall_rating') or current_rating).strip(),
            0
        )
        previous = RATING_ORDER.get(
            str(sorted_history[1].get('overall') or sorted_history[1].get('overall_rating')).strip(),
            0
        )
        
        if current == 0 or previous == 0:
            return "Insufficient data"
        
        if current > previous:
            return "Improving"
        elif current < previous:
            return "Declining"
        else:
            return "Stable"
    
    def _parse_inspection_date(self, inspection: Dict[str, Any]) -> str:
        """Parse inspection date from various possible fields"""
        date_str = (
            inspection.get('inspection_date') or
            inspection.get('date') or
            inspection.get('publicationDate') or
            inspection.get('reportDate') or
            '1900-01-01'  # Fallback for sorting
        )
        return str(date_str)[:10]  # Take first 10 chars (YYYY-MM-DD)
    
    def parse_regulated_activities(self, regulated_activities_data: Optional[Dict[str, Any]]) -> List[RegulatedActivity]:
        """
        Parse regulated_activities JSONB according to SPEC v3.2
        
        Args:
            regulated_activities_data: JSONB data from care_homes DB
            
        Returns:
            List of RegulatedActivity objects
        """
        activities = []
        
        if not regulated_activities_data:
            return activities
        
        # Handle different possible structures
        activities_list = []
        if isinstance(regulated_activities_data, list):
            activities_list = regulated_activities_data
        elif isinstance(regulated_activities_data, dict):
            activities_list = regulated_activities_data.get('activities', [])
            if not activities_list:
                # Try to extract from flat structure
                for key, value in regulated_activities_data.items():
                    if isinstance(value, dict) and value.get('active', False):
                        activities_list.append({
                            'id': key,
                            'name': value.get('name', key),
                            'active': True,
                            'cqc_field': key
                        })
        
        # Parse each activity
        for act in activities_list:
            if isinstance(act, dict):
                activity = RegulatedActivity(
                    id=act.get('id', act.get('activity_id', '')),
                    name=act.get('name', act.get('activity_name', '')),
                    active=act.get('active', True),
                    cqc_field=act.get('cqc_field', act.get('id', ''))
                )
                activities.append(activity)
        
        return activities
    
    async def build_cqc_deep_dive(
        self,
        db_data: Dict[str, Any],
        location_id: str,
        provider_id: Optional[str] = None
    ) -> CQCDeepDive:
        """
        Build complete CQC Deep Dive data according to SPEC v3.2
        
        Args:
            db_data: Data from care_homes DB
            location_id: CQC location ID
            provider_id: Optional provider ID for provider-level analysis
            
        Returns:
            CQCDeepDive object with all required data
        """
        # First try to get live data from CQC API
        overall = str(db_data.get('cqc_rating_overall') or 'Unknown').strip()
        safe = str(db_data.get('cqc_rating_safe') or 'Unknown').strip()
        effective = str(db_data.get('cqc_rating_effective') or 'Unknown').strip()
        caring = str(db_data.get('cqc_rating_caring') or 'Unknown').strip()
        responsive = str(db_data.get('cqc_rating_responsive') or 'Unknown').strip()
        well_led = str(db_data.get('cqc_rating_well_led') or 'Unknown').strip()
        
        # Extract dates from DB initially
        last_inspection_date = self._parse_date(db_data.get('cqc_last_inspection_date'))
        publication_date = self._parse_date(db_data.get('cqc_publication_date'))
        report_url = db_data.get('cqc_latest_report_url')
        
        # Try to enrich with live CQC API data
        try:
            location_details = await self.cqc_client.get_location_details(location_id)
            if location_details:
                current_ratings = location_details.get('currentRatings', {})
                overall_data = current_ratings.get('overall', {})
                
                # Get overall rating
                api_overall = overall_data.get('rating')
                if api_overall:
                    overall = api_overall
                
                # Get detailed key question ratings
                key_question_ratings = overall_data.get('keyQuestionRatings', [])
                for kqr in key_question_ratings:
                    name = kqr.get('name', '').lower()
                    rating = kqr.get('rating')
                    if rating:
                        if name == 'safe':
                            safe = rating
                        elif name == 'effective':
                            effective = rating
                        elif name == 'caring':
                            caring = rating
                        elif name == 'responsive':
                            responsive = rating
                        elif name == 'well-led' or name == 'wellled' or name == 'well_led':
                            well_led = rating
                
                # Get dates from API
                report_date = overall_data.get('reportDate')
                if report_date:
                    last_inspection_date = self._parse_date(report_date)
                    publication_date = self._parse_date(report_date)
                
                # Get report URL
                report_link_id = overall_data.get('reportLinkId')
                if report_link_id:
                    report_url = f"https://www.cqc.org.uk/location/{location_id}/reports"
                
                logger.info(f"Enriched CQC data for {location_id}: {overall}, Safe={safe}, Effective={effective}, Caring={caring}, Responsive={responsive}, Well-led={well_led}")
        except Exception as e:
            logger.warning(f"Failed to get CQC API details for {location_id}: {e}")
        
        # Parse regulated activities
        regulated_activities = self.parse_regulated_activities(
            db_data.get('regulated_activities')
        )
        
        # Extract license flags
        has_nursing_care_license = bool(db_data.get('has_nursing_care_license'))
        has_personal_care_license = bool(db_data.get('has_personal_care_license'))
        has_surgical_procedures_license = bool(db_data.get('has_surgical_procedures_license'))
        has_treatment_license = bool(db_data.get('has_treatment_license'))
        has_diagnostic_license = bool(db_data.get('has_diagnostic_license'))
        
        # Calculate days since inspection
        days_since_inspection = None
        if last_inspection_date:
            days_since_inspection = (date.today() - last_inspection_date).days
        
        # ========================================================================
        # CQC API ENRICHMENT (CRITICAL according to SPEC v3.2)
        # ========================================================================
        
        inspection_history = []
        enforcement_actions = []
        provider_locations = None
        
        try:
            # 1. Get inspection history (5+ years) - CRITICAL for trend
            logger.info(f"Fetching inspection history for location {location_id}")
            inspection_history = await self.cqc_client.get_location_inspection_history(location_id)
            
            # 2. Get enforcement actions - CRITICAL red flags
            logger.info(f"Fetching enforcement actions for location {location_id}")
            enforcement_actions = await self.cqc_client.get_location_enforcement_actions(location_id)
            
            # 3. Get provider-level data for pattern detection
            if provider_id:
                logger.info(f"Fetching provider locations for provider {provider_id}")
                provider_locations = await self.cqc_client.get_provider_locations(provider_id)
        except Exception as e:
            logger.warning(f"Error enriching CQC data for {location_id}: {e}")
            # Continue with DB data only
        
        # Calculate rating trend from inspection history
        rating_trend = self.calculate_rating_trend(overall, inspection_history)
        
        return CQCDeepDive(
            overall=overall,
            safe=safe,
            effective=effective,
            caring=caring,
            responsive=responsive,
            well_led=well_led,
            last_inspection_date=last_inspection_date,
            publication_date=publication_date,
            report_url=report_url,
            regulated_activities=regulated_activities,
            has_nursing_care_license=has_nursing_care_license,
            has_personal_care_license=has_personal_care_license,
            has_surgical_procedures_license=has_surgical_procedures_license,
            has_treatment_license=has_treatment_license,
            has_diagnostic_license=has_diagnostic_license,
            days_since_inspection=days_since_inspection,
            rating_trend=rating_trend,
            inspection_history=inspection_history,
            enforcement_actions=enforcement_actions,
            provider_locations=provider_locations
        )
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats"""
        if not date_value:
            return None
        
        if isinstance(date_value, date):
            return date_value
        
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_value[:10]).date()
            except ValueError:
                try:
                    # Try other common formats
                    return datetime.strptime(date_value[:10], "%Y-%m-%d").date()
                except ValueError:
                    return None
        
        return None
    
    def to_dict(self, cqc_deep_dive: CQCDeepDive) -> Dict[str, Any]:
        """Convert CQCDeepDive to dictionary for API response"""
        return {
            "overall_rating": cqc_deep_dive.overall,
            "current_rating": cqc_deep_dive.overall,
            "detailed_ratings": {
                "safe": {"rating": cqc_deep_dive.safe},
                "effective": {"rating": cqc_deep_dive.effective},
                "caring": {"rating": cqc_deep_dive.caring},
                "responsive": {"rating": cqc_deep_dive.responsive},
                "well_led": {"rating": cqc_deep_dive.well_led}
            },
            "last_inspection_date": cqc_deep_dive.last_inspection_date.isoformat() if cqc_deep_dive.last_inspection_date else None,
            "publication_date": cqc_deep_dive.publication_date.isoformat() if cqc_deep_dive.publication_date else None,
            "report_url": cqc_deep_dive.report_url,
            "regulated_activities": [
                {
                    "id": act.id,
                    "name": act.name,
                    "active": act.active,
                    "cqc_field": act.cqc_field
                }
                for act in cqc_deep_dive.regulated_activities
            ],
            "license_flags": {
                "has_nursing_care_license": cqc_deep_dive.has_nursing_care_license,
                "has_personal_care_license": cqc_deep_dive.has_personal_care_license,
                "has_surgical_procedures_license": cqc_deep_dive.has_surgical_procedures_license,
                "has_treatment_license": cqc_deep_dive.has_treatment_license,
                "has_diagnostic_license": cqc_deep_dive.has_diagnostic_license
            },
            "days_since_inspection": cqc_deep_dive.days_since_inspection,
            "rating_trend": cqc_deep_dive.rating_trend,
            "historical_ratings": cqc_deep_dive.inspection_history,
            "enforcement_actions": cqc_deep_dive.enforcement_actions,
            "provider_locations_count": len(cqc_deep_dive.provider_locations) if cqc_deep_dive.provider_locations else None
        }
    
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

