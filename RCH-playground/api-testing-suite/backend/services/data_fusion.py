"""
Data Fusion Service
Combines data from multiple APIs to generate insights
"""
from typing import Dict, List, Optional, Any


class DataFusionAnalyzer:
    """Data Fusion Analyzer for multi-API integration"""
    
    def analyze_combined_data(self, api_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine data from all sources to generate insights
        """
        profile = {
            "quality_indicators": {},
            "risk_assessment": {},
            "unique_insights": [],
            "correlations": {}
        }
        
        # Extract quality indicators
        if "cqc" in api_results and api_results["cqc"].get("status") == "success":
            cqc_data = api_results["cqc"]
            if cqc_data.get("matching_home"):
                home = cqc_data["matching_home"]
                ratings = home.get("currentRatings", {})
                if ratings:
                    profile["quality_indicators"]["cqc_rating"] = ratings.get("overall", {}).get("rating")
        
        if "fsa" in api_results and api_results["fsa"].get("status") == "success":
            fsa_data = api_results["fsa"]
            if fsa_data.get("sample"):
                establishment = fsa_data["sample"][0]
                profile["quality_indicators"]["food_hygiene"] = establishment.get("RatingValue")
        
        if "google_places" in api_results and api_results["google_places"].get("status") == "success":
            gp_data = api_results["google_places"]
            if gp_data.get("details"):
                details = gp_data["details"]
                profile["quality_indicators"]["google_rating"] = details.get("rating")
                profile["quality_indicators"]["review_count"] = details.get("user_ratings_total", 0)
        
        if "companies_house" in api_results and api_results["companies_house"].get("status") == "success":
            ch_data = api_results["companies_house"]
            if ch_data.get("sample"):
                # Financial risk assessment would go here
                profile["risk_assessment"]["financial_data_available"] = True
        
        # Calculate overall risk score
        profile["risk_assessment"]["overall_score"] = self._calculate_risk_score(profile)
        profile["risk_assessment"]["risk_level"] = self._get_risk_level(
            profile["risk_assessment"]["overall_score"]
        )
        
        # Find correlations
        profile["correlations"] = self._find_correlations(api_results)
        
        return profile
    
    def _calculate_risk_score(self, profile: Dict) -> int:
        """Calculate overall risk score (0-100, higher = more risk)"""
        risk_score = 0
        
        # CQC rating risk
        cqc_rating = profile["quality_indicators"].get("cqc_rating")
        if cqc_rating == "Inadequate":
            risk_score += 50
        elif cqc_rating == "Requires Improvement":
            risk_score += 25
        elif cqc_rating == "Good":
            risk_score += 10
        
        # Food hygiene risk
        fsa_rating = profile["quality_indicators"].get("food_hygiene")
        if fsa_rating and isinstance(fsa_rating, (int, str)):
            try:
                fsa_num = int(fsa_rating)
                if fsa_num < 4:
                    risk_score += 20
            except:
                pass
        
        # Google rating risk
        google_rating = profile["quality_indicators"].get("google_rating")
        if google_rating and google_rating < 3.5:
            risk_score += 20
        
        return min(100, risk_score)
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level from score"""
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _find_correlations(self, api_results: Dict) -> Dict:
        """Find correlations between different data sources"""
        correlations = {}
        
        # CQC vs FSA correlation
        if "cqc" in api_results and "fsa" in api_results:
            correlations["cqc_fsa"] = {
                "description": "CQC rating vs Food Hygiene rating",
                "available": True
            }
        
        # Google Reviews vs CQC
        if "google_places" in api_results and "cqc" in api_results:
            correlations["google_cqc"] = {
                "description": "Google reviews vs CQC rating",
                "available": True
            }
        
        return correlations

