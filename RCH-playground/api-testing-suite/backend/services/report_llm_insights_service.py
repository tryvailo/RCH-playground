"""
LLM Insights Service for Professional Report
Uses Anthropic Claude with structured output to generate expert explanations and advice
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ Anthropic library not installed. Install with: pip install anthropic")


class ReportLLMInsightsService:
    """Service to generate LLM-powered insights and explanations for professional reports"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            try:
                self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)
                print("✅ Anthropic Claude client initialized for report insights")
            except Exception as e:
                print(f"⚠️ Failed to initialize Anthropic client: {e}")
    
    async def generate_report_insights(
        self,
        report_data: Dict[str, Any],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive LLM insights for the professional report
        
        Returns structured insights including:
        - Overall report explanation
        - Key findings summary
        - Expert advice and recommendations
        - Actionable next steps
        """
        if not self.anthropic_client:
            return self._generate_fallback_insights(report_data)
        
        try:
            # Prepare structured output schema
            schema = {
                "name": "report_insights",
                "description": "Expert insights and explanations for a professional care home matching report",
                "schema": {
                    "type": "object",
                    "properties": {
                        "overall_explanation": {
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string",
                                    "description": "A clear, concise summary of what this report means for the client"
                                },
                                "key_insights": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "3-5 key insights that stand out in this report"
                                },
                                "confidence_level": {
                                    "type": "string",
                                    "enum": ["high", "medium", "moderate"],
                                    "description": "Overall confidence in the recommendations"
                                }
                            },
                            "required": ["summary", "key_insights", "confidence_level"]
                        },
                        "top_home_analysis": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "home_name": {"type": "string"},
                                    "rank": {"type": "integer"},
                                    "why_recommended": {
                                        "type": "string",
                                        "description": "Why this home is recommended for this specific client"
                                    },
                                    "key_strengths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Top 3-5 strengths specific to client needs"
                                    },
                                    "considerations": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Things to consider or verify"
                                    },
                                    "match_score_explanation": {
                                        "type": "string",
                                        "description": "What the match score means in practical terms"
                                    }
                                },
                                "required": ["home_name", "rank", "why_recommended", "key_strengths"]
                            },
                            "description": "Analysis of top 3 recommended homes"
                        },
                        "expert_advice": {
                            "type": "object",
                            "properties": {
                                "funding_strategy": {
                                    "type": "string",
                                    "description": "Expert advice on funding options and strategies"
                                },
                                "decision_timeline": {
                                    "type": "string",
                                    "description": "Recommended timeline for making a decision"
                                },
                                "red_flags_to_watch": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Warning signs or concerns to be aware of"
                                },
                                "negotiation_tips": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Practical tips for negotiating with care homes"
                                }
                            },
                            "required": ["funding_strategy", "decision_timeline"]
                        },
                        "actionable_next_steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "string"},
                                    "priority": {
                                        "type": "string",
                                        "enum": ["high", "medium", "low"]
                                    },
                                    "timeline": {"type": "string"},
                                    "details": {"type": "string"}
                                },
                                "required": ["step", "priority", "timeline"]
                            },
                            "description": "Prioritized action items for the client"
                        }
                    },
                    "required": ["overall_explanation", "top_home_analysis", "expert_advice", "actionable_next_steps"]
                }
            }
            
            # Prepare context for LLM
            context = self._prepare_context(report_data, questionnaire)
            
            # System prompt as a care home placement specialist
            system_prompt = """You are an expert care home placement specialist with 20+ years of experience helping families find the right care home in the UK. You have deep knowledge of:

- UK care home regulations (CQC, FSA)
- Funding options (CHC, LA funding, self-funding, DPA)
- Care home quality indicators and what they mean in practice
- Family decision-making processes and common concerns
- Negotiation strategies with care homes
- Red flags and warning signs to watch for

Your role is to:
1. Explain complex report data in clear, understandable terms
2. Highlight what matters most for THIS specific client
3. Provide actionable, practical advice
4. Help families make informed decisions with confidence

Always be:
- Empathetic and supportive
- Clear and practical (avoid jargon)
- Honest about limitations and uncertainties
- Focused on the client's specific needs and situation
- Action-oriented with concrete next steps

Write in a warm, professional tone that reassures families while being realistic about the process."""
            
            # User prompt
            user_prompt = f"""Analyze this professional care home matching report and provide expert insights.

## CLIENT PROFILE
{json.dumps(questionnaire, indent=2, default=str)}

## REPORT DATA
{json.dumps(context, indent=2, default=str)}

## YOUR TASK
Provide comprehensive insights that help the client understand:
1. What this report means for them specifically
2. Why these homes were recommended
3. What to focus on when visiting
4. How to proceed with confidence

Be specific to this client's needs and situation. Reference actual data from the report (match scores, CQC ratings, pricing, etc.) to support your insights."""
            
            # Call Anthropic API with structured output
            # Note: Structured output requires specific format - using text extraction as fallback
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": user_prompt
                    }],
                    response_format={"type": "json_schema", "json_schema": schema}
                )
            except Exception as e:
                # Fallback to regular API call if structured output not supported
                print(f"⚠️ Structured output failed, using regular API call: {e}")
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": user_prompt
                    }]
                )
            
            # Parse structured response
            if response.content and len(response.content) > 0:
                content_item = response.content[0]
                # Handle both text and structured output formats
                if hasattr(content_item, 'text'):
                    response_text = content_item.text
                elif hasattr(content_item, 'input') and hasattr(content_item.input, 'text'):
                    response_text = content_item.input.text
                elif isinstance(content_item, str):
                    response_text = content_item
                else:
                    response_text = str(content_item)
                
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    insights_json = json.loads(json_match.group(0))
                else:
                    # If no JSON found, try parsing entire response
                    insights_json = json.loads(response_text)
                
                return {
                    "generated_at": datetime.now().isoformat(),
                    "model": "claude-3-5-sonnet",
                    "insights": insights_json,
                    "method": "anthropic_structured_output"
                }
            else:
                return self._generate_fallback_insights(report_data)
                
        except Exception as e:
            print(f"⚠️ Error generating LLM insights: {e}")
            import traceback
            print(traceback.format_exc())
            return self._generate_fallback_insights(report_data)
    
    def _prepare_context(self, report_data: Dict[str, Any], questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare simplified context for LLM"""
        context = {
            "client_name": report_data.get("clientName", "Client"),
            "location": report_data.get("city", "Unknown"),
            "analysis_summary": report_data.get("analysisSummary", {}),
            "executive_summary": report_data.get("executiveSummary", {}),
            "total_homes_analyzed": report_data.get("analysisSummary", {}).get("totalHomesAnalyzed", 0),
            "top_homes": []
        }
        
        # Extract top 3 homes with key data
        care_homes = report_data.get("careHomes", [])[:3]
        for home in care_homes:
            home_summary = {
                "name": home.get("name", "Unknown"),
                "match_score": home.get("executiveSummary", {}).get("matchScore", 0),
                "match_reason": home.get("executiveSummary", {}).get("matchReason", ""),
                "weekly_price": home.get("pricing", {}).get("weeklyPrice", 0),
                "cqc_rating": home.get("cqcRating", "Unknown"),
                "key_strengths": home.get("executiveSummary", {}).get("keyStrengths", [])
            }
            context["top_homes"].append(home_summary)
        
        # Add funding information if available
        if "fundingOptimization" in report_data:
            context["funding"] = {
                "chc_probability": report_data["fundingOptimization"].get("chcEligibility", {}).get("probabilityPercent", 0),
                "la_support": report_data["fundingOptimization"].get("laSupport", {}).get("topUpProbabilityPercent", 0)
            }
        
        return context
    
    def _generate_fallback_insights(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic fallback insights when LLM is unavailable"""
        care_homes = report_data.get("careHomes", [])
        top_home = care_homes[0] if care_homes else {}
        
        return {
            "generated_at": datetime.now().isoformat(),
            "model": "fallback",
            "insights": {
                "overall_explanation": {
                    "summary": f"This report analyzed {report_data.get('analysisSummary', {}).get('totalHomesAnalyzed', 0)} care homes to find the best matches for your specific needs. The top recommendations are based on a comprehensive 156-point matching algorithm that considers your medical needs, preferences, and care requirements.",
                    "key_insights": [
                        "Each recommended home has been carefully matched to your specific profile",
                        "Match scores reflect how well each home aligns with your needs",
                        "All homes meet minimum quality standards (CQC registered)"
                    ],
                    "confidence_level": "medium"
                },
                "top_home_analysis": [
                    {
                        "home_name": top_home.get("name", "Recommended Home"),
                        "rank": 1,
                        "why_recommended": top_home.get("executiveSummary", {}).get("matchReason", "Strong match with your requirements"),
                        "key_strengths": top_home.get("executiveSummary", {}).get("keyStrengths", [])[:3],
                        "considerations": ["Schedule a visit to see the home in person", "Ask about availability and waiting lists"],
                        "match_score_explanation": f"Match score of {top_home.get('executiveSummary', {}).get('matchScore', 0)} indicates strong alignment with your needs"
                    }
                ] if top_home else [],
                "expert_advice": {
                    "funding_strategy": "Review the funding options section of this report to understand your eligibility for CHC, LA funding, or self-funding options.",
                    "decision_timeline": "We recommend visiting top 3 homes within 2-3 weeks to make an informed decision.",
                    "red_flags_to_watch": [
                        "Homes with recent CQC ratings below 'Good'",
                        "Significant price increases without justification",
                        "High staff turnover rates"
                    ],
                    "negotiation_tips": [
                        "Ask about introductory rates or discounts for longer commitments",
                        "Inquire about what's included in the weekly fee",
                        "Compare pricing with similar homes in the area"
                    ]
                },
                "actionable_next_steps": [
                    {
                        "step": "Review the top 3 recommended homes",
                        "priority": "high",
                        "timeline": "This week",
                        "details": "Read through each home's detailed profile and match score breakdown"
                    },
                    {
                        "step": "Schedule visits to top homes",
                        "priority": "high",
                        "timeline": "Within 2 weeks",
                        "details": "Contact homes to arrange personal tours"
                    },
                    {
                        "step": "Review funding options",
                        "priority": "medium",
                        "timeline": "Before visits",
                        "details": "Understand your funding eligibility to discuss during visits"
                    }
                ]
            },
            "method": "fallback"
        }

