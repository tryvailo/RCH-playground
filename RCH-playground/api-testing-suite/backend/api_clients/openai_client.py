"""
OpenAI API Client for analyzing Google Places Insights data
"""
import httpx
from typing import Dict, Optional, List
import json


class OpenAIClient:
    """OpenAI API Client for generating insights analysis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze_care_home_insights(
        self,
        place_name: str,
        place_data: Dict,
        insights_data: Dict
    ) -> Dict:
        """
        Analyze Google Places Insights data for a care home and generate comprehensive analysis
        
        Args:
            place_name: Name of the care home
            place_data: Basic place data (rating, reviews, address, etc.)
            insights_data: Comprehensive insights (popular times, dwell time, repeat visitors, etc.)
        
        Returns:
            Dict with analysis including:
            - executive_summary: High-level overview
            - detailed_analysis: Detailed breakdown by category
            - key_insights: Most important findings
            - recommendations: Actionable recommendations
            - risk_assessment: Risk level and concerns
        """
        
        # Prepare the prompt
        prompt = self._build_analysis_prompt(place_name, place_data, insights_data)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert analyst specializing in UK care home quality assessment. 
You analyze Google Places API insights data to provide comprehensive, actionable insights for families 
considering care homes. Your analysis should be:
- Clear and easy to understand
- Data-driven and evidence-based
- Focused on care home quality indicators
- Actionable with specific recommendations
- Written in professional but accessible English
- Return ONLY valid JSON format, no markdown, no code blocks"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2500,
                "response_format": {"type": "json_object"}
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract the analysis text
            analysis_text = data["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                # Try to parse as JSON
                analysis_json = json.loads(analysis_text)
                
                # Ensure we have the expected structure
                if not isinstance(analysis_json, dict):
                    raise ValueError("Response is not a JSON object")
                
                return {
                    "status": "success",
                    "analysis": analysis_json,
                    "raw_text": analysis_text
                }
            except (json.JSONDecodeError, ValueError) as e:
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
                if json_match:
                    try:
                        analysis_json = json.loads(json_match.group(1))
                        return {
                            "status": "success",
                            "analysis": analysis_json,
                            "raw_text": analysis_text
                        }
                    except json.JSONDecodeError:
                        pass
                
                # If all parsing fails, return as formatted text
                return {
                    "status": "success",
                    "analysis": {
                        "full_analysis": analysis_text,
                        "executive_summary": {
                            "overview": "Analysis generated but formatting error occurred. Please see full analysis below.",
                            "overall_score": None,
                            "recommendation": "CONSIDER",
                            "key_highlight": "See detailed analysis"
                        }
                    },
                    "raw_text": analysis_text
                }
                
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}"
            if e.response.status_code == 401:
                error_detail += ": Invalid API key"
            elif e.response.status_code == 429:
                error_detail += ": Rate limit exceeded"
            elif e.response.status_code == 500:
                error_detail += ": OpenAI server error"
            
            try:
                error_data = e.response.json()
                error_detail += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                pass
            
            raise Exception(f"OpenAI API error: {error_detail}")
        except Exception as e:
            raise Exception(f"Error analyzing insights: {str(e)}")
    
    def _build_analysis_prompt(self, place_name: str, place_data: Dict, insights_data: Dict) -> str:
        """Build a comprehensive prompt for OpenAI analysis"""
        
        # Extract key metrics
        rating = place_data.get("rating", "N/A")
        review_count = place_data.get("user_ratings_total", 0)
        address = place_data.get("formatted_address", "N/A")
        
        # Extract insights
        popular_times = insights_data.get("popular_times", {})
        dwell_time = insights_data.get("dwell_time", {})
        repeat_rate = insights_data.get("repeat_visitor_rate", {})
        geography = insights_data.get("visitor_geography", {})
        footfall = insights_data.get("footfall_trends", {})
        summary = insights_data.get("summary", {})
        
        # Build prompt with proper string formatting to avoid f-string nesting issues
        json_structure = """{
  "executive_summary": {
    "overview": "2-3 sentence high-level overview of this care home's performance",
    "overall_score": "A score from 0-100 representing overall quality",
    "recommendation": "RECOMMEND / CONSIDER / AVOID",
    "key_highlight": "One most important positive or negative finding"
  },
  "detailed_analysis": {
    "family_engagement": {
      "score": "Score 0-100",
      "analysis": "Detailed analysis of dwell time and repeat visitor rate",
      "interpretation": "What this means for family satisfaction"
    },
    "visit_patterns": {
      "score": "Score 0-100",
      "analysis": "Analysis of popular times and visit patterns",
      "interpretation": "What this indicates about family involvement"
    },
    "geographic_reach": {
      "score": "Score 0-100",
      "analysis": "Analysis of visitor geography distribution",
      "interpretation": "What this tells us about reputation and appeal"
    },
    "trends_trajectory": {
      "score": "Score 0-100",
      "analysis": "Analysis of footfall trends over time",
      "interpretation": "Is the care home growing, stable, or declining?"
    },
    "quality_indicators": {
      "score": "Score 0-100",
      "analysis": "Key quality indicators based on all data",
      "interpretation": "How metrics correlate with Google rating"
    }
  },
  "key_insights": [
    "First important finding",
    "Second important finding",
    "Third important finding",
    "Fourth important finding",
    "Fifth important finding"
  ],
  "recommendations": {
    "for_families": [
      "Recommendation 1 for families",
      "Recommendation 2 for families"
    ],
    "for_management": [
      "Recommendation 1 for management (if applicable)",
      "Recommendation 2 for management (if applicable)"
    ]
  },
  "risk_assessment": {
    "level": "LOW / MEDIUM / HIGH",
    "score": "Risk score 0-100",
    "concerns": [
      "Concern 1 (if any)",
      "Concern 2 (if any)"
    ],
    "explanation": "Detailed explanation of risk level and why"
  }
}"""
        
        prompt = f"""Analyze the following Google Places API insights data for a UK care home and provide a comprehensive analysis.

CARE HOME INFORMATION:
- Name: {place_name}
- Address: {address}
- Google Rating: {rating}/5.0
- Total Reviews: {review_count}

GOOGLE PLACES INSIGHTS DATA:

1. POPULAR TIMES (When families visit):
{json.dumps(popular_times, indent=2)}

2. DWELL TIME (How long families stay):
{json.dumps(dwell_time, indent=2)}

3. REPEAT VISITOR RATE (Family loyalty):
{json.dumps(repeat_rate, indent=2)}

4. VISITOR GEOGRAPHY (Where visitors come from):
{json.dumps(geography, indent=2)}

5. FOOTFALL TRENDS (Visitation trends over time):
{json.dumps(footfall, indent=2)}

6. SUMMARY METRICS:
{json.dumps(summary, indent=2)}

Please provide a comprehensive analysis in the following JSON structure:

{json_structure}

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks. The JSON should be parseable directly."""

        return prompt
    
    async def generate_key_strengths(
        self,
        home_name: str,
        home_data: Dict
    ) -> List[str]:
        """
        Generate key strengths for a care home based on available data
        
        Args:
            home_name: Name of the care home
            home_data: Dictionary containing home data (CQC rating, Google rating, financial stability, etc.)
        
        Returns:
            List of 3 key strengths as single sentences
        """
        
        # Build prompt with available data
        prompt = self._build_key_strengths_prompt(home_name, home_data)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert analyst specializing in UK care home quality assessment. 
Generate exactly 3 key strengths for a care home based on the provided data. Each strength should be:
- A single, complete sentence
- Specific and data-driven
- Focused on positive attributes
- Professional but accessible
- Maximum 20 words per sentence
Return ONLY a JSON object with a "key_strengths" array containing exactly 3 strings, no markdown, no code blocks."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 200,
                "response_format": {"type": "json_object"}
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract the response text
            response_text = data["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                response_json = json.loads(response_text)
                strengths = response_json.get("key_strengths", [])
                
                # Ensure we have exactly 3 strengths
                if isinstance(strengths, list) and len(strengths) >= 3:
                    return strengths[:3]
                elif isinstance(strengths, list) and len(strengths) > 0:
                    # Pad with generic strengths if needed
                    while len(strengths) < 3:
                        strengths.append("Strong overall care quality and service delivery")
                    return strengths[:3]
                else:
                    # Fallback if parsing fails
                    return self._generate_fallback_strengths(home_data)
            except (json.JSONDecodeError, ValueError, KeyError):
                # Try to extract array from response
                import re
                array_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
                if array_match:
                    try:
                        strengths = json.loads(array_match.group(0))
                        if isinstance(strengths, list) and len(strengths) >= 3:
                            return strengths[:3]
                    except:
                        pass
                
                # Fallback if all parsing fails
                return self._generate_fallback_strengths(home_data)
                
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}"
            if e.response.status_code == 401:
                error_detail += ": Invalid API key"
            elif e.response.status_code == 429:
                error_detail += ": Rate limit exceeded"
            elif e.response.status_code == 500:
                error_detail += ": OpenAI server error"
            
            print(f"OpenAI API error for key strengths: {error_detail}")
            return self._generate_fallback_strengths(home_data)
        except Exception as e:
            print(f"Error generating key strengths: {str(e)}")
            return self._generate_fallback_strengths(home_data)
    
    def _build_key_strengths_prompt(self, home_name: str, home_data: Dict) -> str:
        """Build prompt for generating key strengths"""
        
        # Extract key metrics
        cqc_rating = home_data.get('cqcRating') or home_data.get('cqc_rating') or home_data.get('cqc_rating_overall') or 'Unknown'
        google_rating = home_data.get('googleRating') or home_data.get('google_rating')
        match_score = home_data.get('matchScore') or home_data.get('match_score')
        weekly_price = home_data.get('weeklyPrice') or home_data.get('weekly_price')
        food_hygiene = home_data.get('foodHygiene') or home_data.get('food_hygiene_rating') or home_data.get('fsa_rating')
        
        # Financial stability
        financial_stability = home_data.get('financialStability') or home_data.get('financial_stability') or {}
        financial_score = None
        if isinstance(financial_stability, dict):
            financial_score = financial_stability.get('altman_z_score') or financial_stability.get('risk_score')
        
        # CQC Deep Dive
        cqc_deep_dive = home_data.get('cqcDeepDive') or home_data.get('cqc_deep_dive') or {}
        cqc_ratings = {}
        if isinstance(cqc_deep_dive, dict):
            cqc_ratings = {
                'safe': cqc_deep_dive.get('safe_rating') or cqc_deep_dive.get('ratings', {}).get('safe'),
                'effective': cqc_deep_dive.get('effective_rating') or cqc_deep_dive.get('ratings', {}).get('effective'),
                'caring': cqc_deep_dive.get('caring_rating') or cqc_deep_dive.get('ratings', {}).get('caring'),
                'responsive': cqc_deep_dive.get('responsive_rating') or cqc_deep_dive.get('ratings', {}).get('responsive'),
                'well_led': cqc_deep_dive.get('well_led_rating') or cqc_deep_dive.get('ratings', {}).get('well_led')
            }
        
        # Factor scores
        factor_scores = home_data.get('factorScores') or home_data.get('factor_scores') or []
        top_factors = []
        if isinstance(factor_scores, list):
            # Sort by score and get top 3
            sorted_factors = sorted(factor_scores, key=lambda x: x.get('score', 0), reverse=True)
            top_factors = [f"{f.get('category', '')} ({f.get('score', 0):.1f}/{f.get('maxScore', 0)})" for f in sorted_factors[:3]]
        
        prompt = f"""Generate exactly 3 key strengths for this UK care home based on the available data.

CARE HOME: {home_name}

AVAILABLE DATA:
- CQC Overall Rating: {cqc_rating}
- Google Rating: {google_rating if google_rating else 'Not available'}
- Match Score: {match_score if match_score else 'Not available'}%
- Weekly Price: £{weekly_price:,.0f} if weekly_price else 'Not available'
- Food Hygiene Rating: {food_hygiene if food_hygiene else 'Not available'}
- Financial Stability Score: {financial_score if financial_score else 'Not available'}

CQC Detailed Ratings:
{json.dumps(cqc_ratings, indent=2) if cqc_ratings else 'Not available'}

Top Factor Scores:
{', '.join(top_factors) if top_factors else 'Not available'}

Generate exactly 3 key strengths as a JSON object with this structure:
{{
  "key_strengths": [
    "First strength as a single sentence",
    "Second strength as a single sentence",
    "Third strength as a single sentence"
  ]
}}

IMPORTANT:
- Each strength must be ONE complete sentence (max 20 words)
- Focus on the most positive and distinctive attributes
- Use specific data when available
- Return ONLY valid JSON, no markdown, no code blocks"""

        return prompt
    
    def _generate_fallback_strengths(self, home_data: Dict) -> List[str]:
        """Generate fallback key strengths when OpenAI is unavailable"""
        return OpenAIClient._generate_fallback_strengths_static(home_data)
    
    @staticmethod
    def _generate_fallback_strengths_static(home_data: Dict) -> List[str]:
        """Generate fallback key strengths when OpenAI is unavailable (static method)"""
        strengths = []
        
        cqc_rating = home_data.get('cqcRating') or home_data.get('cqc_rating') or home_data.get('cqc_rating_overall')
        if cqc_rating and str(cqc_rating).lower() in ['outstanding', 'good']:
            strengths.append(f"Strong CQC rating of {cqc_rating} indicating high quality care standards")
        
        google_rating = home_data.get('googleRating') or home_data.get('google_rating')
        if google_rating:
            try:
                rating_float = float(google_rating)
                if rating_float >= 4.0:
                    strengths.append(f"Excellent Google rating of {rating_float:.1f}/5.0 from family reviews")
            except (ValueError, TypeError):
                pass
        
        match_score = home_data.get('matchScore') or home_data.get('match_score')
        if match_score and match_score >= 80:
            strengths.append(f"High match score of {match_score:.1f}% aligning with care requirements")
        
        # Pad to 3 if needed
        while len(strengths) < 3:
            strengths.append("Comprehensive care services with dedicated staff support")
        
        return strengths[:3]

