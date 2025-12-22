"""
Fair Cost Gap Calculation Service
Calculates the gap between market price and MSIF fair cost
Reusable across Free and Professional Reports
"""
from typing import Dict, Any


class FairCostGapService:
    """Service for calculating Fair Cost Gap analysis"""

    def calculate_gap(
        self,
        market_price: float,
        msif_lower_bound: float,
        care_type: str = "residential",
    ) -> Dict[str, Any]:
        """
        Calculate Fair Cost Gap

        Args:
            market_price: Average care home price in the area (£/week)
            msif_lower_bound: MSIF fair cost lower bound (£/week)
            care_type: Type of care (residential, nursing, etc.)

        Returns:
            Dictionary with gap calculations:
            {
                'gap_week': gap per week (£)
                'gap_year': gap per year (£)
                'gap_5year': gap over 5 years (£)
                'gap_percent': gap as percentage of MSIF
                'market_price': market price (£/week)
                'msif_lower_bound': MSIF fair cost (£/week)
                'explanation': Human-readable explanation
                'gap_text': Formatted gap text for display
                'recommendations': List of recommendations
            }

        Example:
            >>> service = FairCostGapService()
            >>> gap = service.calculate_gap(
            ...     market_price=1912,
            ...     msif_lower_bound=1048,
            ...     care_type='nursing_dementia'
            ... )
            >>> gap['gap_year']
            44928
        """
        # Calculate gaps
        weekly_gap = market_price - msif_lower_bound
        annual_gap = weekly_gap * 52
        five_year_gap = annual_gap * 5

        # Calculate percentage
        if msif_lower_bound > 0:
            gap_percent = (weekly_gap / msif_lower_bound) * 100
        else:
            gap_percent = 0

        # Generate explanation
        explanation = f"Market price of £{market_price:,.0f}/week exceeds MSIF fair cost of £{msif_lower_bound:,.0f}/week by {gap_percent:.1f}%"

        # Generate text summary
        if weekly_gap > 0:
            gap_text = f"Переплата £{annual_gap:,.0f} в год = £{five_year_gap:,.0f} за 5 лет"
        else:
            gap_text = f"Экономия £{abs(annual_gap):,.0f} в год = £{abs(five_year_gap):,.0f} за 5 лет"

        return {
            "gap_week": round(weekly_gap, 2),
            "gap_year": round(annual_gap, 2),
            "gap_5year": round(five_year_gap, 2),
            "gap_percent": round(gap_percent, 1),
            "market_price": round(market_price, 2),
            "msif_lower_bound": round(msif_lower_bound, 2),
            "explanation": explanation,
            "gap_text": gap_text,
            "recommendations": self._get_recommendations(weekly_gap),
        }

    def _get_recommendations(self, weekly_gap: float) -> list:
        """Get recommendations based on gap size"""
        recommendations = []

        if weekly_gap > 500:
            recommendations.append("Use MSIF data to negotiate lower fees")
            recommendations.append("Consider homes in adjacent local authorities")

        if weekly_gap > 200:
            recommendations.append("Request detailed cost breakdown")
            recommendations.append("Explore long-term commitment discounts")

        if weekly_gap > 0:
            recommendations.append("Compare prices across multiple homes")
        else:
            recommendations.append("This is an excellent market price")

        return recommendations


# Singleton instance
_gap_service_instance = None


def get_fair_cost_gap_service() -> FairCostGapService:
    """Get or create singleton instance"""
    global _gap_service_instance
    if _gap_service_instance is None:
        _gap_service_instance = FairCostGapService()
    return _gap_service_instance
