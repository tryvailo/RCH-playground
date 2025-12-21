"""
FSA FHRS API Client
Food Standards Agency Food Hygiene Rating Scheme API
"""
import httpx
import asyncio
from time import time
from typing import List, Dict, Optional


class FSAAPIClient:
    """FSA FHRS API Client"""
    
    def __init__(self):
        self.base_url = "http://api.ratings.food.gov.uk"
        self.headers = {
            "x-api-version": "2",
            "Accept-Language": "en-GB",
            "Accept": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests to avoid 403/429 errors
    
    async def _rate_limit(self):
        """Ensure minimum time between requests to avoid rate limiting"""
        elapsed = time() - self.last_request_time
        if elapsed < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time()
    
    async def _make_request_with_retry(
        self,
        url: str,
        params: Dict,
        max_retries: int = 3
    ) -> httpx.Response:
        """Make HTTP request with retry logic for 429 errors"""
        for attempt in range(max_retries):
            try:
                await self._rate_limit()
                response = await self.client.get(url, params=params, headers=self.headers)
                
                # Handle 429 Too Many Requests with exponential backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                        print(f"      ⚠️ FSA API rate limited (429), waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        response.raise_for_status()
                
                # Handle 403 Forbidden - check if it's HTML (blocked) or JSON (actual error)
                if response.status_code == 403:
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" in content_type:
                        # This is a block page, not a real API error
                        raise Exception(f"FSA API blocked request (403): Possible rate limiting or IP block. Response: HTML page")
                
                response.raise_for_status()
                return response
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"      ⚠️ FSA API rate limited (429), waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1 and ("429" in str(e) or "rate limit" in str(e).lower()):
                    wait_time = (attempt + 1) * 2
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        raise Exception("FSA API request failed after all retries")
    
    async def search_by_business_name(
        self,
        name: str,
        local_authority_id: Optional[int] = None,
        page_size: int = 50
    ) -> List[Dict]:
        """Search establishments by business name"""
        params = {
            "name": name,
            "pageSize": page_size  # Limit results to avoid CPU-intensive queries
        }
        
        if local_authority_id:
            params["localAuthorityId"] = local_authority_id
        
        try:
            response = await self._make_request_with_retry(
                f"{self.base_url}/Establishments",
                params
            )
            data = response.json()
            establishments = data.get("establishments", [])
            
            # Always return results, even if empty (this is valid - no matches found)
            return establishments
        except httpx.HTTPStatusError as e:
            error_msg = f"FSA API HTTP error: {e.response.status_code}"
            try:
                error_body = e.response.json()
                error_msg += f" - {error_body}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            raise Exception(error_msg)
        except httpx.RequestError as e:
            raise Exception(f"FSA API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"FSA API error: {str(e)}")
    
    async def search_by_location(
        self,
        latitude: float,
        longitude: float,
        max_distance: float = 1.0,
        page_size: int = 50
    ) -> List[Dict]:
        """Search establishments by geolocation"""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "maxDistanceLimit": max_distance,
            "pageSize": page_size  # Limit results to avoid CPU-intensive queries
        }
        
        try:
            response = await self._make_request_with_retry(
                f"{self.base_url}/Establishments",
                params
            )
            data = response.json()
            return data.get("establishments", [])
        except httpx.HTTPStatusError as e:
            error_msg = f"FSA API HTTP error: {e.response.status_code}"
            try:
                error_body = e.response.json()
                error_msg += f" - {error_body}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            raise Exception(error_msg)
        except httpx.RequestError as e:
            raise Exception(f"FSA API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"FSA API error: {str(e)}")
    
    async def search_by_business_type(
        self,
        business_type_id: int = 7835,  # 7835 = "Hospitals/Childcare/Caring Premises"
        local_authority_id: Optional[int] = None,
        name: Optional[str] = None,
        page_size: int = 50
    ) -> List[Dict]:
        """Search establishments by business type and optionally by local authority and name"""
        params = {
            "businessTypeId": business_type_id,
            "pageSize": page_size  # Increased from 20 to 50, but still limited
        }
        
        if local_authority_id:
            params["localAuthorityId"] = local_authority_id
        
        if name:
            params["name"] = name
        
        try:
            response = await self._make_request_with_retry(
                f"{self.base_url}/Establishments",
                params
            )
            data = response.json()
            establishments = data.get("establishments", [])
            return establishments
        except httpx.HTTPStatusError as e:
            error_msg = f"FSA API HTTP error: {e.response.status_code}"
            try:
                error_body = e.response.json()
                error_msg += f" - {error_body}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            raise Exception(error_msg)
        except httpx.RequestError as e:
            raise Exception(f"FSA API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"FSA API error: {str(e)}")
    
    async def get_establishment_details(self, fhrs_id: int) -> Dict:
        """Get details for a specific establishment"""
        try:
            await self._rate_limit()
            response = await self.client.get(
                f"{self.base_url}/Establishments/{fhrs_id}",
                headers=self.headers
            )
            
            # Handle 403 Forbidden - check if it's HTML (blocked)
            if response.status_code == 403:
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" in content_type:
                    raise Exception(f"FSA API blocked request (403): Possible rate limiting or IP block")
            
            response.raise_for_status()
            data = response.json()
            
            # FSA API may return establishment directly or wrapped in a structure
            # Check if it's wrapped in 'establishments' array or directly returned
            if isinstance(data, dict):
                if "establishments" in data and len(data["establishments"]) > 0:
                    establishment = data["establishments"][0]
                elif "FHRSID" in data or "BusinessName" in data:
                    # Direct establishment object
                    establishment = data
                else:
                    # Try to find establishment data in response
                    establishment = data
            else:
                establishment = data
            
            # Parse breakdown scores from the response
            breakdown_scores = self._parse_breakdown_scores(establishment)
            
            # Add parsed breakdown scores to response
            if breakdown_scores:
                establishment["breakdown_scores"] = breakdown_scores
            
            return establishment
        except httpx.HTTPStatusError as e:
            error_msg = f"FSA API HTTP error: {e.response.status_code}"
            try:
                error_body = e.response.json()
                error_msg += f" - {error_body}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            raise Exception(error_msg)
        except httpx.RequestError as e:
            raise Exception(f"FSA API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"FSA API error: {str(e)}")
    
    def _parse_breakdown_scores(self, establishment: Dict) -> Optional[Dict]:
        """Parse breakdown scores from establishment data"""
        scores = establishment.get("scores", {})
        if not scores:
            return None
        
        # FSA API provides scores in different formats
        # Try to extract hygiene, structural, and confidence scores
        hygiene = scores.get("Hygiene") or scores.get("hygiene") or scores.get("HygieneScore")
        structural = scores.get("Structural") or scores.get("structural") or scores.get("StructuralScore")
        confidence = scores.get("ConfidenceInManagement") or scores.get("confidence") or scores.get("ConfidenceScore")
        
        if hygiene is None and structural is None and confidence is None:
            return None
        
        return {
            "hygiene": hygiene,
            "structural": structural,
            "confidence_in_management": confidence,
            "hygiene_label": self._score_to_label(hygiene) if hygiene is not None else None,
            "structural_label": self._score_to_label(structural) if structural is not None else None,
            "confidence_label": self._score_to_label(confidence) if confidence is not None else None
        }
    
    def _score_to_label(self, score: Optional[int]) -> Optional[str]:
        """Convert numeric score to label"""
        if score is None:
            return None
        if score >= 5:
            return "Excellent"
        elif score >= 4:
            return "Good"
        elif score >= 3:
            return "Satisfactory"
        elif score >= 2:
            return "Needs Improvement"
        elif score >= 1:
            return "Needs Significant Improvement"
        else:
            return "Needs Urgent Improvement"
    
    def _safe_int_rating(self, rating_value) -> Optional[int]:
        """Safely convert rating value to integer"""
        if rating_value is None:
            return None
        try:
            if isinstance(rating_value, int):
                return rating_value
            if isinstance(rating_value, str):
                # Remove any non-numeric characters and convert
                cleaned = rating_value.strip()
                if cleaned:
                    return int(cleaned)
            return int(rating_value)
        except (ValueError, TypeError):
            return None
    
    async def get_inspection_history(self, fhrs_id: int) -> List[Dict]:
        """Get inspection history for an establishment"""
        try:
            # FSA API doesn't directly provide history endpoint
            # We'll need to search for all establishments with same name/location
            # and extract historical data
            details = await self.get_establishment_details(fhrs_id)
            
            # Extract current inspection data
            history = []
            rating_value = details.get("RatingValue")
            if rating_value is not None:
                rating_int = self._safe_int_rating(rating_value)
                if rating_int is not None:
                    history.append({
                        "date": details.get("RatingDate"),
                        "rating": rating_int,
                        "rating_key": details.get("RatingKey"),
                        "breakdown_scores": details.get("breakdown_scores"),
                        "local_authority": details.get("LocalAuthorityName"),
                        "inspection_type": "Full" if details.get("RatingDate") else "Unknown"
                    })
            
            return history
        except Exception as e:
            raise Exception(f"FSA API error getting inspection history: {str(e)}")
    
    async def analyze_fsa_trends(self, fhrs_id: int) -> Dict:
        """Analyze FSA rating trends"""
        try:
            details = await self.get_establishment_details(fhrs_id)
            history = await self.get_inspection_history(fhrs_id)
            
            rating_value = details.get("RatingValue")
            current_rating = self._safe_int_rating(rating_value)
            rating_date = details.get("RatingDate")
            
            # Calculate trend (simplified - would need more historical data)
            trend = "stable"
            if len(history) > 1:
                ratings = [h.get("rating") for h in history if h.get("rating") is not None]
                # Ensure all ratings are integers
                ratings = [r if isinstance(r, int) else self._safe_int_rating(r) for r in ratings]
                ratings = [r for r in ratings if r is not None]
                if len(ratings) >= 2:
                    if ratings[0] > ratings[-1]:
                        trend = "improving"
                    elif ratings[0] < ratings[-1]:
                        trend = "declining"
            
            # Calculate consistency
            history_ratings = [h.get("rating") for h in history if h.get("rating") is not None]
            history_ratings = [r if isinstance(r, int) else self._safe_int_rating(r) for r in history_ratings]
            history_ratings = [r for r in history_ratings if r is not None]
            consistency = "consistent" if len(set(history_ratings)) <= 1 else "variable"
            
            return {
                "current_rating": current_rating,
                "rating_date": rating_date,
                "trend": trend,
                "history_count": len(history),
                "consistency": consistency,
                "breakdown_scores": details.get("breakdown_scores"),
                "prediction": self._predict_next_rating(current_rating, trend)
            }
        except Exception as e:
            raise Exception(f"FSA API error analyzing trends: {str(e)}")
    
    def _predict_next_rating(self, current_rating: Optional[int], trend: str) -> Dict:
        """Predict next rating based on current rating and trend"""
        if current_rating is None:
            return {"predicted_rating": None, "predicted_label": None, "confidence": "low"}
        
        # Ensure current_rating is an integer
        if not isinstance(current_rating, int):
            current_rating = self._safe_int_rating(current_rating)
            if current_rating is None:
                return {"predicted_rating": None, "predicted_label": None, "confidence": "low"}
        
        if trend == "improving":
            predicted = min(5, current_rating + 1)
        elif trend == "declining":
            predicted = max(0, current_rating - 1)
        else:
            predicted = current_rating
        
        confidence = "high" if trend == "stable" else "medium"
        
        return {
            "predicted_rating": predicted,
            "predicted_label": self._score_to_label(predicted),
            "confidence": confidence
        }
    
    def calculate_fsa_health_score(self, establishment: Dict) -> Dict:
        """
        Calculate FSA Health Score (0-100) according to FSA-API-Analysis.md formula
        Formula:
          Hygiene_normalized = (20 - Hygiene_score) / 20 * 100
          Structural_normalized = (20 - Structural_score) / 20 * 100
          Management_normalized = (30 - ConfidenceInManagement_score) / 30 * 100
          
          FSA_Score = (
            Hygiene_normalized * 0.40 +
            Structural_normalized * 0.30 +
            Management_normalized * 0.30
          )
        """
        scores_data = establishment.get("scores", {}) or {}
        breakdown = establishment.get("breakdown_scores", {}) or {}
        
        # Get scores (lower is better in FSA)
        # Handle both None and missing keys
        hygiene_score = breakdown.get("hygiene")
        if hygiene_score is None:
            hygiene_score = scores_data.get("Hygiene")
        
        structural_score = breakdown.get("structural")
        if structural_score is None:
            structural_score = scores_data.get("Structural")
        
        management_score = breakdown.get("confidence_in_management")
        if management_score is None:
            management_score = scores_data.get("ConfidenceInManagement")
        
        # Convert string scores to int if needed
        try:
            if hygiene_score is not None and isinstance(hygiene_score, str):
                hygiene_score = int(hygiene_score)
        except (ValueError, TypeError):
            hygiene_score = None
        
        try:
            if structural_score is not None and isinstance(structural_score, str):
                structural_score = int(structural_score)
        except (ValueError, TypeError):
            structural_score = None
        
        try:
            if management_score is not None and isinstance(management_score, str):
                management_score = int(management_score)
        except (ValueError, TypeError):
            management_score = None
        
        # Normalize scores (0-100, higher is better)
        hygiene_normalized = 0
        structural_normalized = 0
        management_normalized = 0
        
        try:
            if hygiene_score is not None:
                # Ensure hygiene_score is numeric
                if isinstance(hygiene_score, (int, float)):
                    hygiene_normalized = max(0, min(100, (20 - float(hygiene_score)) / 20 * 100))
        except (TypeError, ValueError):
            hygiene_score = None
        
        try:
            if structural_score is not None:
                if isinstance(structural_score, (int, float)):
                    structural_normalized = max(0, min(100, (20 - float(structural_score)) / 20 * 100))
        except (TypeError, ValueError):
            structural_score = None
        
        try:
            if management_score is not None:
                if isinstance(management_score, (int, float)):
                    management_normalized = max(0, min(100, (30 - float(management_score)) / 30 * 100))
        except (TypeError, ValueError):
            management_score = None
        
        # Calculate weighted FSA Score
        if hygiene_score is not None and structural_score is not None and management_score is not None:
            fsa_score = (
                hygiene_normalized * 0.40 +
                structural_normalized * 0.30 +
                management_normalized * 0.30
            )
            final_score = round(fsa_score)
        else:
            # If some scores are missing, use available ones with adjusted weights
            available_weights = []
            available_scores = []
            
            if hygiene_score is not None:
                available_weights.append(0.40)
                available_scores.append(hygiene_normalized)
            if structural_score is not None:
                available_weights.append(0.30)
                available_scores.append(structural_normalized)
            if management_score is not None:
                available_weights.append(0.30)
                available_scores.append(management_normalized)
            
            if available_scores:
                # Normalize weights
                total_weight = sum(available_weights)
                if total_weight > 0:
                    normalized_weights = [w / total_weight for w in available_weights]
                    fsa_score = sum(score * weight for score, weight in zip(available_scores, normalized_weights))
                    final_score = round(fsa_score)
                else:
                    final_score = 0
            else:
                final_score = 0
        
        # Determine label
        if final_score >= 80:
            label = "EXCELLENT"
            description = "Above average"
        elif final_score >= 60:
            label = "GOOD"
            description = "Average"
        elif final_score >= 40:
            label = "FAIR"
            description = "Below average"
        else:
            label = "POOR"
            description = "Requires attention"
        
        return {
            "score": final_score,
            "label": label,
            "description": description,
            "breakdown": {
                "hygiene": {
                    "raw_score": hygiene_score,
                    "normalized": round(hygiene_normalized, 1) if hygiene_score is not None else None,
                    "weight": 0.40
                },
                "structural": {
                    "raw_score": structural_score,
                    "normalized": round(structural_normalized, 1) if structural_score is not None else None,
                    "weight": 0.30
                },
                "management": {
                    "raw_score": management_score,
                    "normalized": round(management_normalized, 1) if management_score is not None else None,
                    "weight": 0.30
                }
            },
            "max_score": 100
        }
    
    def calculate_diabetes_suitability_score(self, establishment: Dict) -> Dict:
        """
        Calculate diabetes suitability score (0-100) based on FSA rating data
        Based on documentation from INTEGRATION_GUIDE.md
        """
        score = 0
        details = []
        
        # Overall rating (40 points)
        rating_value = establishment.get("RatingValue")
        if rating_value:
            rating_int = self._safe_int_rating(rating_value)
            if rating_int is not None and rating_int >= 4:
                score += rating_int * 8  # 4*8=32, 5*8=40
                details.append(f"Overall rating {rating_int}/5: +{rating_int * 8} points")
        
        # Get breakdown scores
        breakdown = establishment.get("breakdown_scores", {})
        scores_data = establishment.get("scores", {})
        
        # Hygiene score (30 points) - inverse scoring (lower is better)
        hygiene_score_raw = breakdown.get("hygiene") or scores_data.get("Hygiene")
        hygiene_score = self._safe_int_rating(hygiene_score_raw) if hygiene_score_raw is not None else None
        if hygiene_score is not None:
            if hygiene_score <= 5:
                score += 30
                details.append(f"Hygiene score {hygiene_score}/20 (Excellent): +30 points")
            elif hygiene_score <= 10:
                score += 20
                details.append(f"Hygiene score {hygiene_score}/20 (Good): +20 points")
            elif hygiene_score <= 15:
                score += 10
                details.append(f"Hygiene score {hygiene_score}/20 (Fair): +10 points")
        
        # Management score (20 points) - inverse scoring
        management_score_raw = breakdown.get("confidence_in_management") or scores_data.get("ConfidenceInManagement")
        management_score = self._safe_int_rating(management_score_raw) if management_score_raw is not None else None
        if management_score is not None:
            if management_score <= 5:
                score += 20
                details.append(f"Management score {management_score}/30 (Excellent): +20 points")
            elif management_score <= 10:
                score += 15
                details.append(f"Management score {management_score}/30 (Good): +15 points")
            elif management_score <= 15:
                score += 10
                details.append(f"Management score {management_score}/30 (Fair): +10 points")
        
        # Recency (10 points)
        rating_date = establishment.get("RatingDate")
        if rating_date:
            try:
                from datetime import datetime, date
                if isinstance(rating_date, str):
                    rating_date_obj = datetime.fromisoformat(rating_date.replace('Z', '+00:00')).date()
                else:
                    rating_date_obj = rating_date
                
                days_since = (date.today() - rating_date_obj).days
                if days_since <= 365:
                    score += 10
                    details.append(f"Recent inspection ({days_since} days ago): +10 points")
                elif days_since <= 730:
                    score += 5
                    details.append(f"Inspection within 2 years ({days_since} days ago): +5 points")
            except Exception:
                pass
        
        final_score = min(score, 100)  # Cap at 100
        
        # Determine label
        if final_score >= 90:
            label = "EXCELLENT"
            recommendation = "Highly suitable for diabetes management"
        elif final_score >= 75:
            label = "VERY GOOD"
            recommendation = "Very suitable for diabetes management"
        elif final_score >= 60:
            label = "GOOD"
            recommendation = "Suitable for diabetes management"
        elif final_score >= 45:
            label = "FAIR"
            recommendation = "Acceptable but monitor closely"
        else:
            label = "NEEDS ATTENTION"
            recommendation = "May require special dietary considerations"
        
        return {
            "score": final_score,
            "label": label,
            "recommendation": recommendation,
            "breakdown": details,
            "max_score": 100
        }
    
    async def get_local_authorities(self) -> List[Dict]:
        """Get list of all local authorities"""
        try:
            await self._rate_limit()
            response = await self.client.get(
                f"{self.base_url}/Authorities",
                headers=self.headers
            )
            
            # Handle 403 Forbidden
            if response.status_code == 403:
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" in content_type:
                    raise Exception(f"FSA API blocked request (403): Possible rate limiting or IP block")
            
            response.raise_for_status()
            data = response.json()
            return data.get("authorities", [])
        except Exception as e:
            raise Exception(f"FSA API error: {str(e)}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

