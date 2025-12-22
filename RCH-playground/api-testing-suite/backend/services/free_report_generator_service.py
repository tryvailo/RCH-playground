"""
Free Report Generator Service
Orchestrates the report generation process
"""
import uuid
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, List

from models.free_report_models import FreeReportRequest, FreeReportResponse
from utils.logging_utils import GenerationContext, GenerationStep
from services.fair_cost_gap_service import get_fair_cost_gap_service
from services.free_report_matching_service import get_free_report_matching_service
from utils.price_extractor import extract_weekly_price

logger = logging.getLogger(__name__)


class FreeReportGeneratorService:
    """Service for generating free reports"""

    def __init__(
        self,
        fair_cost_gap_service=None,
        matching_service=None,
        data_loader_service=None,
    ):
        """
        Initialize with services (dependency injection)

        Args:
            fair_cost_gap_service: Service for gap calculation
            matching_service: Service for home matching
            data_loader_service: Service for loading care homes
        """
        self.gap_service = fair_cost_gap_service or get_fair_cost_gap_service()
        self.matching_service = (
            matching_service or get_free_report_matching_service()
        )
        self.data_loader = data_loader_service

    async def generate(
        self,
        request: FreeReportRequest,
        care_homes: List[Dict[str, Any]],
        local_authority: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
    ) -> FreeReportResponse:
        """
        Generate a free report

        Args:
            request: Validated questionnaire request
            care_homes: List of care homes from database
            local_authority: Local authority name
            user_lat: User latitude
            user_lon: User longitude

        Returns:
            FreeReportResponse with complete report data
        """
        # Initialize context
        report_id = str(uuid.uuid4())
        context = GenerationContext(
            report_id, request.postcode, request.care_type
        )

        context.log_step_start(GenerationStep.FILTERING)

        try:
            # Step 1: Filter homes by quality
            filtered_homes = self._filter_by_quality(care_homes, request.care_type)
            context.log_step_complete(
                GenerationStep.FILTERING, {"count": len(filtered_homes)}
            )

            # Step 2: Matching
            context.log_step_start(GenerationStep.MATCHING)
            matched = self.matching_service.select_top_3_homes(
                homes=filtered_homes,
                budget=request.budget,
                care_type=request.care_type,
                user_lat=user_lat,
                user_lon=user_lon,
                max_distance_km=request.max_distance_km or 30.0,
            )
            context.log_step_complete(GenerationStep.MATCHING)

            # Step 3: Fair Cost Gap calculation
            context.log_step_start(GenerationStep.GAP_CALCULATION)
            fair_cost_gap = self._calculate_fair_cost_gap(
                matched, request.care_type, request.budget
            )
            context.log_step_complete(
                GenerationStep.GAP_CALCULATION,
                {"gap_week": fair_cost_gap.get("gap_week")},
            )

            # Step 4: Format response
            context.log_step_start(GenerationStep.RESPONSE_ASSEMBLY)

            care_homes_list = self._format_matched_homes(
                matched, request.care_type
            )

            response = FreeReportResponse(
                questionnaire=request.dict(),
                care_homes=care_homes_list,
                fair_cost_gap=fair_cost_gap,
                area_profile=None,  # Can be extended
                area_map=None,  # Can be extended
                llm_insights=None,  # Can be extended
                generated_at=datetime.now().isoformat(),
                report_id=report_id,
            )

            context.log_step_complete(GenerationStep.RESPONSE_ASSEMBLY)

            # Log summary
            summary = context.get_summary()
            logger.info(f"Report generated successfully: {json.dumps(summary)}")

            return response

        except Exception as e:
            context.log_error(GenerationStep.RESPONSE_ASSEMBLY, e)
            logger.error(f"Report generation failed: {e}", exc_info=True)
            raise

    def _filter_by_quality(
        self, homes: List[Dict[str, Any]], care_type: str
    ) -> List[Dict[str, Any]]:
        """Filter homes by CQC quality rating"""
        filtered = [
            h
            for h in homes
            if (
                h.get("cqc_rating_overall", "").lower()
                in ["good", "outstanding"]
                or h.get("rating", "").lower() in ["good", "outstanding"]
                or h.get("overall_cqc_rating", "").lower()
                in ["good", "outstanding"]
            )
        ]
        return filtered if filtered else homes

    def _calculate_fair_cost_gap(
        self,
        matched: Dict[str, Optional[Dict[str, Any]]],
        care_type: str,
        budget: float,
    ) -> Dict[str, Any]:
        """Calculate fair cost gap"""
        # Use average price from matched homes
        prices = []
        for home in [matched.get("safe_bet"), matched.get("best_value"), matched.get("premium")]:
            if home:
                price = extract_weekly_price(home, care_type)
                if price > 0:
                    prices.append(price)

        market_price = (
            sum(prices) / len(prices) if prices else budget or 1200.0
        )

        # Default MSIF values
        msif_defaults = {
            "residential": 700,
            "nursing": 1048,
            "dementia": 800,
            "respite": 700,
        }
        msif_lower_bound = msif_defaults.get(care_type, 700)

        return self.gap_service.calculate_gap(
            market_price=market_price,
            msif_lower_bound=msif_lower_bound,
            care_type=care_type,
        )

    def _format_matched_homes(
        self,
        matched: Dict[str, Optional[Dict[str, Any]]],
        care_type: str,
    ) -> List[Dict[str, Any]]:
        """Format matched homes for response"""
        homes = []

        for match_type, home in [
            ("Safe Bet", matched.get("safe_bet")),
            ("Best Value", matched.get("best_value")),
            ("Premium", matched.get("premium")),
        ]:
            if home:
                formatted = {
                    "name": home.get("name"),
                    "address": home.get("address"),
                    "postcode": home.get("postcode"),
                    "weekly_cost": extract_weekly_price(home, care_type),
                    "rating": home.get("cqc_rating_overall")
                    or home.get("rating"),
                    "care_types": home.get("care_types", []),
                    "distance_km": home.get("distance_km"),
                    "match_type": match_type,
                    "photo_url": home.get("photo_url"),
                    "fsa_rating": home.get("fsa_rating"),
                }
                homes.append(formatted)

        return homes


def get_free_report_generator_service(
    fair_cost_gap_service=None,
    matching_service=None,
    data_loader_service=None,
) -> FreeReportGeneratorService:
    """Get generator service with optional dependency injection"""
    return FreeReportGeneratorService(
        fair_cost_gap_service=fair_cost_gap_service,
        matching_service=matching_service,
        data_loader_service=data_loader_service,
    )
