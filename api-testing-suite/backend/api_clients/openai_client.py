"""
OpenAI API Client for analyzing Google Places Insights data
"""
import httpx
from typing import Dict, Optional
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

