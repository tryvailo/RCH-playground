"""
LLM Insights Service for Professional Report
Uses OpenAI GPT-4o (priority 1), Anthropic Claude (priority 2), or fallback
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import httpx

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ Anthropic library not installed. Install with: pip install anthropic")


class ReportLLMInsightsService:
    """Service to generate LLM-powered insights and explanations for professional reports"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        # Initialize OpenAI client (priority 1)
        self.openai_api_key = openai_api_key
        self.openai_client = None
        if openai_api_key:
            try:
                self.openai_client = httpx.AsyncClient(timeout=60.0)
                print("✅ OpenAI client initialized for report insights")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")
        
        # Initialize Anthropic client (priority 2)
        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            try:
                self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)
                print("✅ Anthropic Claude client initialized for report insights (fallback)")
            except Exception as e:
                print(f"⚠️ Failed to initialize Anthropic client: {e}")
    
    async def generate_report_insights(
        self,
        report_data: Dict[str, Any],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive LLM insights for the professional report
        
        Priority:
        1. OpenAI GPT-4o (if available)
        2. Anthropic Claude (if OpenAI unavailable)
        3. Fallback insights (if both unavailable)
        
        Returns structured insights including:
        - Overall report explanation
        - Key findings summary
        - Expert advice and recommendations
        - Actionable next steps
        """
        # ✅ FIX: Debug logging to understand why OpenAI is not called
        print(f"\n🔍 LLM Insights Generation Debug:")
        print(f"   OpenAI client: {'✅ initialized' if self.openai_client else '❌ not initialized'}")
        print(f"   OpenAI API key: {'✅ present' if self.openai_api_key and self.openai_api_key != 'your-openai-api-key' else '❌ not configured'}")
        print(f"   Anthropic client: {'✅ initialized' if self.anthropic_client else '❌ not initialized'}")
        print(f"   Anthropic API key: {'✅ present' if hasattr(self, 'anthropic_api_key') and self.anthropic_api_key else '❌ not configured'}")
        
        # Try OpenAI first (priority 1)
        if self.openai_client and self.openai_api_key and self.openai_api_key != 'your-openai-api-key':
            print(f"   🚀 Attempting OpenAI generation...")
            try:
                result = await self._generate_with_openai(report_data, questionnaire)
                print(f"   ✅ OpenAI generation successful!")
                return result
            except Exception as e:
                print(f"   ⚠️ OpenAI generation failed: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                # Continue to try Anthropic
        else:
            if not self.openai_client:
                print(f"   ⚠️ OpenAI client not initialized")
            if not self.openai_api_key or self.openai_api_key == 'your-openai-api-key':
                print(f"   ⚠️ OpenAI API key not configured or is placeholder")
        
        # Try Anthropic Claude (priority 2)
        if self.anthropic_client:
            print(f"   🚀 Attempting Anthropic Claude generation...")
            try:
                result = await self._generate_with_anthropic(report_data, questionnaire)
                print(f"   ✅ Anthropic Claude generation successful!")
                return result
            except Exception as e:
                print(f"   ⚠️ Anthropic Claude generation failed: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
        
        # Fallback if both unavailable
        print(f"   ⚠️ Both OpenAI and Anthropic unavailable, using fallback insights")
        return self._generate_fallback_insights(report_data)
    
    async def _generate_with_openai(
        self,
        report_data: Dict[str, Any],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights using OpenAI GPT-4o"""
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
                                        "description": "Why this home is recommended for this specific client, emphasizing benefits and value"
                                    },
                                    "data_sources_explanation": {
                                        "type": "string",
                                        "description": "Explanation of ALL data sources used for this home (CQC, FSA, Companies House, Google Places API, Google Places New API, etc.) and what each source reveals"
                                    },
                                    "key_benefits": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Specific benefits and value propositions this home offers to THIS client, with data references"
                                    },
                                    "key_strengths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Top 3-5 strengths specific to client needs, with data source references"
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
                                "required": ["home_name", "rank", "why_recommended", "data_sources_explanation", "key_benefits", "key_strengths"]
                            },
                            "description": "Analysis of top 3-5 recommended homes with data sources and benefits"
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
            print(f"   📊 Context prepared: {len(context.get('top_homes', []))} homes, context size: {len(json.dumps(context))} bytes")
            
            # System prompt as a care home placement specialist
            system_prompt = """You are an expert care home placement specialist with 20+ years of experience helping families find the right care home in the UK. You have deep knowledge of:

- UK care home regulations (CQC, FSA)
- Funding options (CHC, LA funding, self-funding, DPA)
- Care home quality indicators and what they mean in practice
- Data sources used in professional reports (CQC, FSA, Companies House, Google Places, Google Places New API, etc.)
- Family decision-making processes and common concerns
- Negotiation strategies with care homes
- Red flags and warning signs to watch for

Your role is to:
1. Explain ALL data sources used for each care home and what they reveal
2. Highlight the SPECIFIC BENEFITS and VALUE each home offers to THIS client
3. Reference actual data points from each source (CQC ratings, FSA scores, financial stability, Google Places insights, etc.)
4. Explain why each data point matters for the client's specific situation
5. Emphasize the competitive advantages and unique selling points of each home

CRITICAL REQUIREMENTS:
- For EACH home, explain which data sources were used (CQC, FSA, Companies House, Google Places API, Google Places New API, etc.)
- For EACH home, highlight specific benefits and value propositions
- Reference actual numbers, ratings, and scores from the data
- Explain what each data source tells us about the home's quality, safety, financial stability, family engagement, etc.
- Make it clear why this home is valuable for THIS specific client

Always be:
- Empathetic and supportive
- Clear and practical (avoid jargon)
- Data-driven (cite specific numbers and sources)
- Benefit-focused (emphasize value and advantages)
- Honest about limitations and uncertainties
- Focused on the client's specific needs and situation

Write in a warm, professional tone that reassures families while being realistic about the process."""
            
            # User prompt
            user_prompt = f"""Analyze this professional care home matching report and provide expert insights focused on DATA SOURCES and BENEFITS for each home.

## CLIENT PROFILE
{json.dumps(questionnaire, indent=2, default=str)}

## REPORT DATA
{json.dumps(context, indent=2, default=str)}

## YOUR TASK
For EACH recommended home, provide:

1. **DATA SOURCES EXPLANATION**: 
   - List ALL data sources used for this home (CQC, FSA, Companies House, Google Places API, Google Places New API, etc.)
   - Explain what each source tells us about the home
   - Reference specific data points from each source (ratings, scores, metrics)

2. **BENEFITS AND VALUE**:
   - Highlight specific benefits this home offers to THIS client
   - Explain competitive advantages and unique selling points
   - Reference actual numbers (match scores, CQC ratings, pricing, Google Places insights, etc.)
   - Explain why these benefits matter for the client's specific needs

3. **WHY RECOMMENDED**:
   - Explain why this home was recommended based on the data
   - Connect data points to client needs
   - Emphasize value proposition

Be specific to this client's needs and situation. Reference actual data from ALL sources (match scores, CQC ratings, FSA scores, financial stability metrics, Google Places insights, pricing, etc.) to support your insights.

Return your response as valid JSON matching the schema provided. Do not include markdown code blocks, just return pure JSON."""
            
            # Call OpenAI API with structured output
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # ✅ FIX: Ensure user prompt explicitly requests JSON (required for json_object response_format)
            user_prompt_with_json_request = user_prompt + "\n\nIMPORTANT: Return your response as valid JSON only. Do not include markdown code blocks, just return pure JSON matching the schema."
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt_with_json_request
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000,
                "response_format": {"type": "json_object"}
            }
            
            print(f"   📡 Calling OpenAI API: https://api.openai.com/v1/chat/completions")
            print(f"   📦 Payload size: {len(json.dumps(payload))} bytes")
            print(f"   🔑 API Key: {self.openai_api_key[:10]}...{self.openai_api_key[-4:] if len(self.openai_api_key) > 14 else ''}")
            
            try:
                response = await self.openai_client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                print(f"   📥 OpenAI API Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text[:500] if hasattr(response, 'text') else str(response)
                    print(f"   ❌ OpenAI API Error: {response.status_code} - {error_text}")
                    raise ValueError(f"OpenAI API returned status {response.status_code}: {error_text}")
                
                response.raise_for_status()
                data = response.json()
                print(f"   ✅ OpenAI API Response received successfully")
            except httpx.HTTPStatusError as e:
                print(f"   ❌ OpenAI API HTTP Error: {e.response.status_code}")
                if hasattr(e, 'response') and e.response:
                    try:
                        error_data = e.response.json()
                        print(f"   Error details: {error_data}")
                    except:
                        print(f"   Error text: {e.response.text[:500] if hasattr(e.response, 'text') else str(e.response)}")
                raise
            except httpx.RequestError as e:
                print(f"   ❌ OpenAI API Request Error: {e}")
                raise
            
            # Extract the content from OpenAI response
            if data.get("choices") and len(data["choices"]) > 0:
                response_text = data["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    insights_json = json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks if present
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        insights_json = json.loads(json_match.group(0))
                    else:
                        raise ValueError("Could not parse JSON from OpenAI response")
                
                # ✅ DEBUG: Log structure of insights_json
                print(f"   📊 Parsed insights_json keys: {list(insights_json.keys()) if isinstance(insights_json, dict) else 'Not a dict'}")
                if isinstance(insights_json, dict):
                    if 'top_home_analysis' in insights_json:
                        print(f"   📊 top_home_analysis length: {len(insights_json.get('top_home_analysis', []))}")
                    elif 'insights' in insights_json and isinstance(insights_json['insights'], dict):
                        print(f"   📊 insights.top_home_analysis length: {len(insights_json['insights'].get('top_home_analysis', []))}")
                    else:
                        print(f"   ⚠️ top_home_analysis not found in insights_json")
                        print(f"   📊 Full structure: {json.dumps(insights_json, indent=2, default=str)[:500]}")
                
                # ✅ FIX: Handle case where OpenAI returns nested structure
                # OpenAI might return { "insights": {...} } or just {...}
                if isinstance(insights_json, dict) and 'insights' in insights_json:
                    # Already nested, use as is
                    final_insights = insights_json['insights']
                else:
                    # Top-level structure, wrap in insights
                    final_insights = insights_json
                
                # ✅ FIX: Ensure top_home_analysis exists
                if not final_insights.get('top_home_analysis'):
                    print(f"   ⚠️ top_home_analysis missing in final_insights, generating fallback")
                    # Use fallback if top_home_analysis is missing
                    return self._generate_fallback_insights(report_data)
                
                return {
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-4o",
                    "insights": final_insights,
                    "method": "openai_structured_output"
                }
            else:
                raise ValueError("OpenAI response has no choices")
                
        except Exception as e:
            print(f"❌ Error generating insights with OpenAI: {e}")
            import traceback
            print(f"Full traceback:\n{traceback.format_exc()}")
            # ✅ FIX: Log response details if available
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json() if hasattr(e.response, 'json') else str(e.response)
                    print(f"OpenAI API Error Response: {error_data}")
                except:
                    print(f"OpenAI API Error Response (raw): {e.response}")
            raise  # Re-raise to trigger Anthropic fallback
    
    async def _generate_with_anthropic(
        self,
        report_data: Dict[str, Any],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights using Anthropic Claude (fallback)"""
        try:
            # Prepare structured output schema (same as OpenAI)
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
                                        "description": "Why this home is recommended for this specific client, emphasizing benefits and value"
                                    },
                                    "data_sources_explanation": {
                                        "type": "string",
                                        "description": "Explanation of ALL data sources used for this home (CQC, FSA, Companies House, Google Places API, Google Places New API, etc.) and what each source reveals"
                                    },
                                    "key_benefits": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Specific benefits and value propositions this home offers to THIS client, with data references"
                                    },
                                    "key_strengths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Top 3-5 strengths specific to client needs, with data source references"
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
                                "required": ["home_name", "rank", "why_recommended", "data_sources_explanation", "key_benefits", "key_strengths"]
                            },
                            "description": "Analysis of top 3-5 recommended homes with data sources and benefits"
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
            
            # System prompt (same as OpenAI)
            system_prompt = """You are an expert care home placement specialist with 20+ years of experience helping families find the right care home in the UK. You have deep knowledge of:

- UK care home regulations (CQC, FSA)
- Funding options (CHC, LA funding, self-funding, DPA)
- Care home quality indicators and what they mean in practice
- Data sources used in professional reports (CQC, FSA, Companies House, Google Places, Google Places New API, etc.)
- Family decision-making processes and common concerns
- Negotiation strategies with care homes
- Red flags and warning signs to watch for

Your role is to:
1. Explain ALL data sources used for each care home and what they reveal
2. Highlight the SPECIFIC BENEFITS and VALUE each home offers to THIS client
3. Reference actual data points from each source (CQC ratings, FSA scores, financial stability, Google Places insights, etc.)
4. Explain why each data point matters for the client's specific situation
5. Emphasize the competitive advantages and unique selling points of each home

CRITICAL REQUIREMENTS:
- For EACH home, explain which data sources were used (CQC, FSA, Companies House, Google Places API, Google Places New API, etc.)
- For EACH home, highlight specific benefits and value propositions
- Reference actual numbers, ratings, and scores from the data
- Explain what each data source tells us about the home's quality, safety, financial stability, family engagement, etc.
- Make it clear why this home is valuable for THIS specific client

Always be:
- Empathetic and supportive
- Clear and practical (avoid jargon)
- Data-driven (cite specific numbers and sources)
- Benefit-focused (emphasize value and advantages)
- Honest about limitations and uncertainties
- Focused on the client's specific needs and situation

Write in a warm, professional tone that reassures families while being realistic about the process."""
            
            # User prompt
            user_prompt = f"""Analyze this professional care home matching report and provide expert insights focused on DATA SOURCES and BENEFITS for each home.

## CLIENT PROFILE
{json.dumps(questionnaire, indent=2, default=str)}

## REPORT DATA
{json.dumps(context, indent=2, default=str)}

## YOUR TASK
For EACH recommended home, provide:

1. **DATA SOURCES EXPLANATION**: 
   - List ALL data sources used for this home (CQC, FSA, Companies House, Google Places API, Google Places New API, etc.)
   - Explain what each source tells us about the home
   - Reference specific data points from each source (ratings, scores, metrics)

2. **BENEFITS AND VALUE**:
   - Highlight specific benefits this home offers to THIS client
   - Explain competitive advantages and unique selling points
   - Reference actual numbers (match scores, CQC ratings, pricing, Google Places insights, etc.)
   - Explain why these benefits matter for the client's specific needs

3. **WHY RECOMMENDED**:
   - Explain why this home was recommended based on the data
   - Connect data points to client needs
   - Emphasize value proposition

Be specific to this client's needs and situation. Reference actual data from ALL sources (match scores, CQC ratings, FSA scores, financial stability metrics, Google Places insights, pricing, etc.) to support your insights."""
            
            # Call Anthropic API with structured output
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
                raise ValueError("Anthropic response has no content")
                
        except Exception as e:
            print(f"⚠️ Error generating insights with Anthropic: {e}")
            import traceback
            print(traceback.format_exc())
            raise  # Re-raise to trigger fallback
    
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
        
        # Extract top 5 homes with comprehensive data including all sources
        care_homes = report_data.get("careHomes", [])[:5]
        for home in care_homes:
            home_summary = {
                "name": home.get("name", "Unknown"),
                "match_score": home.get("matchScore") or home.get("executiveSummary", {}).get("matchScore", 0),
                "match_reason": home.get("whyChosen") or home.get("executiveSummary", {}).get("matchReason", ""),
                "weekly_price": home.get("weeklyPrice") or home.get("pricing", {}).get("weeklyPrice", 0),
                "cqc_rating": home.get("cqcRating", "Unknown"),
                "key_strengths": home.get("keyStrengths") or home.get("executiveSummary", {}).get("keyStrengths", []),
                # CQC Data
                "cqc_data": {
                    "rating": home.get("cqcRating"),
                    "deep_dive": home.get("cqcDeepDive"),
                    "last_inspection": home.get("cqcDeepDive", {}).get("last_inspection_date") if home.get("cqcDeepDive") else None
                },
                # FSA Data
                "fsa_data": {
                    "rating": home.get("fsaDetailed", {}).get("rating") if home.get("fsaDetailed") else None,
                    "breakdown_scores": home.get("fsaDetailed", {}).get("breakdown_scores") if home.get("fsaDetailed") else None
                },
                # Financial Stability Data
                "financial_data": {
                    "z_score": home.get("financialStability", {}).get("z_score") if home.get("financialStability") else None,
                    "bankruptcy_risk": home.get("financialStability", {}).get("bankruptcy_risk") if home.get("financialStability") else None,
                    "financial_rating": home.get("financialStability", {}).get("financial_rating") if home.get("financialStability") else None
                },
                # Google Places Data
                "google_places_data": {
                    "rating": home.get("googlePlaces", {}).get("rating") if home.get("googlePlaces") else home.get("googleRating"),
                    "review_count": home.get("googlePlaces", {}).get("user_ratings_total") if home.get("googlePlaces") else home.get("reviewCount"),
                    "insights": home.get("googlePlaces", {}).get("insights") if home.get("googlePlaces") else None
                },
                # Google Places New API Data
                "google_places_new_data": {
                    "dwell_time": home.get("average_dwell_time_minutes") or (home.get("googlePlaces", {}).get("insights", {}).get("dwell_time", {}).get("average_dwell_time_minutes") if home.get("googlePlaces", {}).get("insights") else None),
                    "repeat_visitor_rate": home.get("repeat_visitor_rate") or (home.get("googlePlaces", {}).get("insights", {}).get("repeat_visitor_rate", {}).get("repeat_visitor_rate_percent") if home.get("googlePlaces", {}).get("insights") else None),
                    "footfall_trend": home.get("footfall_trend") or (home.get("googlePlaces", {}).get("insights", {}).get("footfall_trends", {}).get("trend_direction") if home.get("googlePlaces", {}).get("insights") else None),
                    "family_engagement_score": home.get("family_engagement_score") or (home.get("googlePlaces", {}).get("insights", {}).get("summary", {}).get("family_engagement_score") if home.get("googlePlaces", {}).get("insights") else None)
                },
                # Community Reputation
                "community_reputation": {
                    "trust_score": home.get("communityReputation", {}).get("trust_score") if home.get("communityReputation") else None,
                    "sentiment": home.get("communityReputation", {}).get("sentiment_analysis") if home.get("communityReputation") else None
                },
                # Staff Quality
                "staff_quality": {
                    "overall_score": home.get("staffQuality", {}).get("overallScore") if home.get("staffQuality") else None,
                    "category": home.get("staffQuality", {}).get("category") if home.get("staffQuality") else None
                },
                # Neighbourhood
                "neighbourhood": {
                    "walkability": home.get("neighbourhood", {}).get("walkability_score") if home.get("neighbourhood") else None,
                    "amenities": home.get("neighbourhood", {}).get("amenities") if home.get("neighbourhood") else None
                }
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
        top_homes = care_homes[:5] if care_homes else []
        
        # Generate insights for all top 5 homes
        top_home_analysis = []
        for idx, home in enumerate(top_homes):
            # ✅ FIX: Get home name from multiple possible fields
            home_name = (
                home.get("name") or 
                home.get("home_name") or 
                home.get("id") or 
                f"Home {idx + 1}"
            )
            match_score = home.get("matchScore") or home.get("executiveSummary", {}).get("matchScore", 0)
            why_chosen = (
                home.get("whyChosen") or 
                home.get("executiveSummary", {}).get("matchReason") or 
                home.get("matchReason") or
                f"Strong match with your requirements based on comprehensive analysis"
            )
            key_strengths = (
                home.get("keyStrengths") or 
                home.get("executiveSummary", {}).get("keyStrengths", [])[:3] or
                []
            )
            must_verify = home.get("mustVerify", [])[:2] or ["Schedule a visit to see the home in person", "Ask about availability and waiting lists"]
            cqc_rating = home.get("cqcRating") or "Good"
            
            top_home_analysis.append({
                "home_name": home_name,
                "rank": idx + 1,
                "why_recommended": why_chosen,
                "data_sources_explanation": "This home has been analyzed using multiple data sources including CQC (Care Quality Commission) for quality ratings, FSA (Food Standards Agency) for food hygiene, Companies House for financial stability, and Google Places API for community reputation and reviews.",
                "key_benefits": [
                    f"Match score of {match_score}% indicates strong alignment with your specific needs",
                    f"CQC rating of {cqc_rating} ensures quality care standards",
                    "Comprehensive data analysis from multiple official sources provides confidence in the recommendation"
                ],
                "key_strengths": key_strengths if key_strengths else [
                    f"Match score of {match_score}% indicates strong alignment",
                    f"CQC rating of {cqc_rating}",
                    "Comprehensive data analysis"
                ],
                "considerations": must_verify,
                "match_score_explanation": f"Match score of {match_score}% indicates {'excellent' if match_score >= 80 else 'strong' if match_score >= 60 else 'good'} alignment with your needs"
            })
        
        return {
            "generated_at": datetime.now().isoformat(),
            "model": "fallback",
            "method": "data_driven_analysis",
            "insights": {
                "overall_explanation": {
                    "summary": f"This report analyzed {report_data.get('analysisSummary', {}).get('totalHomesAnalyzed', len(care_homes))} care homes to find the best matches for your specific needs. The top recommendations are based on a comprehensive matching algorithm that considers your medical needs, preferences, and care requirements.",
                    "key_insights": [
                        "Each recommended home has been carefully matched to your specific profile",
                        "Match scores reflect how well each home aligns with your needs",
                        "All homes meet minimum quality standards (CQC registered)"
                    ],
                    "confidence_level": "medium"
                },
                "top_home_analysis": top_home_analysis,
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

