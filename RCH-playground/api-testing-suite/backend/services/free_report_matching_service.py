"""
Free Report Matching Service
Selects top 3 strategic care homes (Safe Bet, Best Value, Premium)
based on quality, price, and location criteria
"""
from typing import Dict, List, Any, Optional
from utils.price_extractor import extract_weekly_price
from utils.geo import calculate_distance_km, validate_coordinates


class FreeReportMatchingService:
    """Service for selecting top 3 strategic care homes for free report"""

    def select_top_3_homes(
        self,
        homes: List[Dict[str, Any]],
        budget: float,
        care_type: str,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        max_distance_km: float = 30.0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Select 3 homes with different strategies:
        - Safe Bet: Best balance of quality, price, location
        - Best Value: Best price/quality ratio
        - Premium: Highest quality available

        Args:
            homes: List of care homes with data
            budget: Weekly budget in £
            care_type: Type of care (residential, nursing, etc.)
            user_lat: User latitude for distance calculation
            user_lon: User longitude for distance calculation
            max_distance_km: Maximum distance in km

        Returns:
            Dictionary with:
            {
                'safe_bet': {...},
                'best_value': {...},
                'premium': {...}
            }
        """
        # Filter homes first
        filtered_homes = self._filter_by_quality(homes)
        filtered_homes = self._filter_by_price(filtered_homes, budget, care_type)
        filtered_homes = self._filter_by_location(
            filtered_homes, user_lat, user_lon, max_distance_km
        )

        if not filtered_homes:
            # Fallback: return first 3 homes from input
            return {
                "safe_bet": homes[0] if len(homes) > 0 else None,
                "best_value": homes[1] if len(homes) > 1 else None,
                "premium": homes[2] if len(homes) > 2 else None,
            }

        # Score all homes
        scored_homes = self._score_homes(filtered_homes, budget, care_type)

        # Limit to top 10 homes by score for efficiency
        top_homes = scored_homes[:10] if len(scored_homes) > 10 else scored_homes

        # Find Safe Bet
        safe_bet = self._find_safe_bet(top_homes, budget, care_type)

        # Find Best Value (excluding Safe Bet)
        remaining_homes = [
            h
            for h in top_homes
            if safe_bet is None or h["home"]["name"] != safe_bet["name"]
        ]
        best_value = self._find_best_value(remaining_homes, budget, care_type)

        # Find Premium (excluding Safe Bet and Best Value)
        remaining_homes = [
            h
            for h in remaining_homes
            if best_value is None or h["home"]["name"] != best_value["name"]
        ]
        premium = self._find_premium(remaining_homes, budget, care_type)

        return {
            "safe_bet": safe_bet,
            "best_value": best_value,
            "premium": premium,
        }

    def _filter_by_quality(
        self, homes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter homes with Good or Outstanding CQC rating"""
        return [
            h
            for h in homes
            if self._get_cqc_rating(h).lower() in ["good", "outstanding"]
        ]

    def _filter_by_price(
        self, homes: List[Dict[str, Any]], budget: float, care_type: str, tolerance_pct: float = 30
    ) -> List[Dict[str, Any]]:
        """Filter homes within budget with tolerance percentage"""
        if budget <= 0:
            return homes

        max_price = budget * (1 + tolerance_pct / 100)
        return [
            h
            for h in homes
            if extract_weekly_price(h, care_type) <= max_price
        ]

    def _filter_by_location(
        self,
        homes: List[Dict[str, Any]],
        user_lat: Optional[float],
        user_lon: Optional[float],
        max_distance_km: float,
    ) -> List[Dict[str, Any]]:
        """Filter homes within max distance"""
        if not user_lat or not user_lon:
            return homes

        filtered = []
        for h in homes:
            h_lat = h.get("latitude")
            h_lon = h.get("longitude")

            if h_lat and h_lon:
                try:
                    if validate_coordinates(
                        float(user_lat), float(user_lon)
                    ) and validate_coordinates(float(h_lat), float(h_lon)):
                        distance = calculate_distance_km(
                            float(user_lat),
                            float(user_lon),
                            float(h_lat),
                            float(h_lon),
                        )
                        if distance <= max_distance_km:
                            h["distance_km"] = distance
                            filtered.append(h)
                except (ValueError, TypeError):
                    pass

        return filtered if filtered else homes

    def _score_homes(
        self,
        homes: List[Dict[str, Any]],
        budget: float,
        care_type: str,
    ) -> List[Dict[str, Any]]:
        """Score all homes for ranking"""
        scored = []

        for home in homes:
            price = extract_weekly_price(home, care_type)
            if price <= 0:
                continue  # Skip homes without valid price

            score = self._calculate_home_score(home, budget, care_type, price)
            scored.append({"home": home, "score": score})

        # Sort by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _calculate_home_score(
        self,
        home: Dict[str, Any],
        budget: float,
        care_type: str,
        price: float,
    ) -> float:
        """Calculate scoring for a home"""
        score = 50.0  # Base score

        # Quality (1-4 points)
        cqc_rating = self._get_cqc_rating(home)
        if cqc_rating.lower() == "outstanding":
            score += 25
        elif cqc_rating.lower() == "good":
            score += 20

        # FSA Food Hygiene Rating penalty/bonus (per spec: FSA <= 3 gives -1 penalty)
        fsa_rating = home.get("fsa_rating")
        if fsa_rating is not None:
            try:
                fsa_int = int(fsa_rating) if isinstance(fsa_rating, (int, float, str)) else None
                if fsa_int is not None:
                    if fsa_int >= 5:
                        score += 2  # Bonus for excellent food hygiene
                    elif fsa_int <= 3:
                        score -= 5  # Penalty for poor food hygiene (FSA 2 or 3 = red/amber)
                        # Additional penalty for very poor (FSA 1-2)
                        if fsa_int <= 2:
                            score -= 3  # Extra penalty for red rating
            except (ValueError, TypeError):
                pass  # Ignore invalid FSA rating values

        # Price fit (1-3 points)
        if budget > 0:
            price_diff = abs(price - budget)
            if price_diff < 50:
                score += 20
            elif price_diff < 100:
                score += 15
            elif price_diff < 200:
                score += 10

        # Distance (1-2 points)
        distance = home.get("distance_km", 999)
        if isinstance(distance, (int, float)):
            if distance < 5:
                score += 10
            elif distance < 15:
                score += 5

        return max(0, score)  # Ensure score doesn't go negative

    def _find_safe_bet(
        self,
        scored_homes: List[Dict[str, Any]],
        budget: float,
        care_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Find best balance of quality, price, location (40-40-20 weighting)"""
        best = None
        best_score = -1

        for scored in scored_homes:
            home = scored["home"]
            price = extract_weekly_price(home, care_type)
            cqc = self._get_cqc_rating_score(self._get_cqc_rating(home))

            # Must have Good or Outstanding quality (CQC >= 3)
            if cqc < 3:
                continue

            # FSA Rating check: Prefer homes with good FSA rating for "Safe Bet"
            # Homes with FSA <= 2 (red) should be penalized or excluded
            fsa_rating = home.get("fsa_rating")
            fsa_penalty = 0
            if fsa_rating is not None:
                try:
                    fsa_int = int(fsa_rating) if isinstance(fsa_rating, (int, float, str)) else None
                    if fsa_int is not None:
                        if fsa_int <= 2:
                            fsa_penalty = -15  # Significant penalty for red FSA rating (unsafe for "Safe Bet")
                        elif fsa_int == 3:
                            fsa_penalty = -5  # Penalty for amber FSA rating
                except (ValueError, TypeError):
                    pass

            # Quality score (40 points max)
            quality_score = 40 if cqc == 4 else 30
            
            # Price score (40 points max)
            price_score = 0
            if budget > 0:
                price_diff = abs(price - budget)
                if price_diff < 50:
                    price_score = 40
                elif price_diff < 100:
                    price_score = 30
                elif price_diff < 200:
                    price_score = 20
                else:
                    price_score = 0
            
            # Distance score (20 points max)
            distance = home.get("distance_km", 999)
            if distance < 5:
                distance_score = 20
            elif distance < 10:
                distance_score = 15
            elif distance < 15:
                distance_score = 10
            else:
                distance_score = 0
            
            # Total balance score (with FSA penalty)
            balance = quality_score + price_score + distance_score + fsa_penalty

            if balance > best_score:
                best_score = balance
                best = home

        return best

    def _find_best_value(
        self,
        scored_homes: List[Dict[str, Any]],
        budget: float,
        care_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Find best price/quality ratio"""
        best = None
        best_score = -1

        for scored in scored_homes:
            home = scored["home"]
            price = extract_weekly_price(home, care_type)
            cqc = self._get_cqc_rating_score(self._get_cqc_rating(home))

            # Must have Good or Outstanding (CQC >= 3)
            if cqc < 3:
                continue

            # Price bounds check: price should be 50-130% of budget
            if budget > 0:
                if price < (budget * 0.5) or price > (budget * 1.3):
                    continue

            # Value score: quality/price ratio
            if price > 0:
                value_score = cqc / (price / 100)
            else:
                continue

            if value_score > best_score:
                best_score = value_score
                best = home

        return best

    def _find_premium(
        self,
        scored_homes: List[Dict[str, Any]],
        budget: float,
        care_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Find highest quality home, selecting max price for same quality"""
        # First, try to find Outstanding (CQC 4) homes
        outstanding = []
        good = []
        
        for scored in scored_homes:
            home = scored["home"]
            cqc = self._get_cqc_rating_score(self._get_cqc_rating(home))
            
            if cqc == 4:  # Outstanding
                price = extract_weekly_price(home, care_type)
                outstanding.append((home, price))
            elif cqc == 3:  # Good
                price = extract_weekly_price(home, care_type)
                good.append((home, price))
        
        # If Outstanding homes exist, select the one with max price
        if outstanding:
            return max(outstanding, key=lambda x: x[1])[0]
        
        # Fallback to Good homes with max price
        if good:
            return max(good, key=lambda x: x[1])[0]
        
        # No candidates found
        return None

    def _get_cqc_rating(self, home: Dict[str, Any]) -> str:
        """Extract CQC rating from home data"""
        return (
            home.get("cqc_rating_overall")
            or home.get("overall_cqc_rating")
            or home.get("rating")
            or "Unknown"
        )

    def _get_cqc_rating_score(self, rating_str: str) -> float:
        """Convert CQC rating to numeric score"""
        if not rating_str or not isinstance(rating_str, str):
            return 0

        rating_lower = rating_str.lower()
        if "outstanding" in rating_lower:
            return 4
        elif "good" in rating_lower:
            return 3
        elif "requires improvement" in rating_lower:
            return 2
        elif "inadequate" in rating_lower:
            return 1
        return 0


def get_free_report_matching_service() -> FreeReportMatchingService:
    """Get matching service instance"""
    return FreeReportMatchingService()
