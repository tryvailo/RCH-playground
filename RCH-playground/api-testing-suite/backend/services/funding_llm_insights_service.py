"""
LLM Insights Service for Funding Eligibility Calculator
Uses OpenAI GPT with structured output to generate expert explanations and advice
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import httpx

class FundingLLMInsightsService:
    """Service to generate LLM-powered insights and explanations for funding eligibility calculations"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.client = None
        if openai_api_key:
            try:
                self.client = httpx.AsyncClient(timeout=60.0)
                print("✅ OpenAI client initialized for funding insights")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")
    
    async def generate_funding_insights(
        self,
        calculation_result: Dict[str, Any],
        patient_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive LLM insights for funding eligibility calculation
        
        Returns structured insights including:
        - Overall explanation of results
        - CHC eligibility explanation
        - LA funding explanation
        - DPA eligibility explanation
        - Expert advice and next steps
        
        Priority:
        1. OpenAI GPT-4o (if key available)
        2. Perplexity API (fallback)
        3. Hardcoded template (last resort)
        """
        print(f"🔍 generate_funding_insights called")
        print(f"   OpenAI client available: {self.client is not None}")
        print(f"   OpenAI API key available: {self.openai_api_key is not None}")
        
        if not self.client or not self.openai_api_key:
            print("⚠️ OpenAI not available, trying Perplexity API...")
            perplexity_result = await self._try_perplexity_insights(calculation_result, patient_profile)
            if perplexity_result:
                return perplexity_result
            
            print("⚠️ Perplexity also not available, using hardcoded fallback")
            fallback_result = self._generate_hardcoded_fallback(calculation_result)
            print(f"✅ Fallback insights generated: {type(fallback_result)}")
            return fallback_result
        
        try:
            # Prepare structured output schema
            schema = {
                "name": "funding_insights",
                "description": "Expert insights and explanations for a funding eligibility calculation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "overall_explanation": {
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string",
                                    "description": "A clear, concise summary of what these funding results mean for the client"
                                },
                                "key_findings": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "3-5 key findings from the calculation"
                                },
                                "confidence_level": {
                                    "type": "string",
                                    "enum": ["high", "medium", "moderate"],
                                    "description": "Overall confidence in the calculations"
                                }
                            },
                            "required": ["summary", "key_findings", "confidence_level"]
                        },
                        "chc_explanation": {
                            "type": "object",
                            "properties": {
                                "what_it_means": {
                                    "type": "string",
                                    "description": "What the CHC probability means in practical terms"
                                },
                                "eligibility_factors": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Key factors that influenced the CHC probability"
                                },
                                "next_steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Recommended next steps for CHC assessment"
                                },
                                "important_notes": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Important things to know about CHC eligibility"
                                }
                            },
                            "required": ["what_it_means", "eligibility_factors"]
                        },
                        "la_funding_explanation": {
                            "type": "object",
                            "properties": {
                                "what_it_means": {
                                    "type": "string",
                                    "description": "What the LA funding results mean"
                                },
                                "means_test_summary": {
                                    "type": "string",
                                    "description": "Summary of the means test calculation"
                                },
                                "contribution_explanation": {
                                    "type": "string",
                                    "description": "Explanation of any required contribution"
                                },
                                "tips": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Tips for maximising LA funding"
                                }
                            },
                            "required": ["what_it_means", "means_test_summary"]
                        },
                        "dpa_explanation": {
                            "type": "object",
                            "properties": {
                                "what_it_means": {
                                    "type": "string",
                                    "description": "What DPA eligibility means"
                                },
                                "property_status": {
                                    "type": "string",
                                    "description": "Explanation of property disregard status"
                                },
                                "benefits": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Benefits of using DPA if eligible"
                                },
                                "considerations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Things to consider about DPA"
                                }
                            },
                            "required": ["what_it_means", "property_status"]
                        },
                        "expert_advice": {
                            "type": "object",
                            "properties": {
                                "funding_strategy": {
                                    "type": "string",
                                    "description": "Recommended funding strategy based on results"
                                },
                                "maximising_eligibility": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Tips for maximising funding eligibility"
                                },
                                "common_mistakes": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Common mistakes to avoid"
                                },
                                "when_to_reassess": {
                                    "type": "string",
                                    "description": "When to reassess eligibility"
                                }
                            },
                            "required": ["funding_strategy"]
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
                        },
                        "hypothetical_savings_explanation": {
                            "type": "object",
                            "properties": {
                                "is_applicable": {
                                    "type": "boolean",
                                    "description": "Whether hypothetical savings explanation applies (true if savings.is_hypothetical=true)"
                                },
                                "explanation": {
                                    "type": "string",
                                    "description": "Clear explanation that savings are hypothetical and what this means"
                                },
                                "what_would_be_saved": {
                                    "type": "string",
                                    "description": "Amount that would be saved IF funding were received"
                                },
                                "what_needs_to_change": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "What needs to change to improve eligibility"
                                },
                                "realistic_pathway": {
                                    "type": "string",
                                    "description": "How to realistically improve eligibility"
                                },
                                "practical_steps_to_improve": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "category": {
                                                "type": "string",
                                                "enum": ["CHC Eligibility", "LA Funding", "DPA", "General"],
                                                "description": "Category of the step"
                                            },
                                            "step": {
                                                "type": "string",
                                                "description": "Specific actionable step title"
                                            },
                                            "priority": {
                                                "type": "string",
                                                "enum": ["high", "medium", "low"],
                                                "description": "Priority level"
                                            },
                                            "timeline": {
                                                "type": "string",
                                                "description": "When to do this (e.g., 'Within 2 weeks', 'Immediately - ongoing')"
                                            },
                                            "details": {
                                                "type": "string",
                                                "description": "Detailed explanation of what to do and why"
                                            },
                                            "expected_impact": {
                                                "type": "string",
                                                "description": "What improvement they can expect"
                                            }
                                        },
                                        "required": ["category", "step", "priority", "timeline", "details"]
                                    },
                                    "description": "Detailed, practical steps to improve eligibility (REQUIRED if is_hypothetical=true)"
                                }
                            },
                            "required": ["is_applicable", "explanation", "practical_steps_to_improve"]
                        }
                    },
                    "required": ["overall_explanation", "chc_explanation", "la_funding_explanation", "dpa_explanation", "expert_advice", "actionable_next_steps"]
                }
            }
            
            # Prepare context for LLM
            context = self._prepare_context(calculation_result, patient_profile)
            
            # System prompt as a funding specialist
            system_prompt = """You are an expert UK care funding specialist with 20+ years of experience helping families understand and access care funding. You have deep knowledge of:

- NHS Continuing Healthcare (CHC) eligibility and assessment process
- Local Authority (LA) funding and means testing (2025-2026 thresholds)
- Deferred Payment Agreements (DPA) and property disregards
- DST (Decision Support Tool) domains and scoring
- Funding strategies and optimisation
- Common pitfalls and how to avoid them

Your role is to:
1. Explain complex funding calculations in clear, understandable terms
2. Help families understand what their results mean in practical terms
3. Provide actionable advice on next steps
4. Highlight opportunities to maximise funding eligibility
5. Warn about common mistakes

Always be:
- Clear and practical (avoid jargon, explain technical terms)
- Honest about limitations and uncertainties
- Action-oriented with concrete next steps
- Empathetic and supportive
- Focused on helping families access the funding they're entitled to

CRITICAL: Write in British English (UK spelling and terminology):
- Use "colour" not "color"
- Use "favour" not "favor"
- Use "realise" not "realize"
- Use "organise" not "organize"
- Use "centre" not "center"
- Use "licence" (noun) not "license"
- Use "practice" (noun) not "practise" (verb)
- Use UK terminology: "Local Authority" not "local government", "care home" not "nursing home" (unless specifically nursing care)

Write in a warm, professional tone that empowers families while being realistic about the process."""
            
            # User prompt
            user_prompt = f"""Analyze this funding eligibility calculation and provide expert insights.

## PATIENT PROFILE
{json.dumps(patient_profile, indent=2, default=str)}

## CALCULATION RESULTS
{json.dumps(context, indent=2, default=str)}

## YOUR TASK
Provide comprehensive insights that help the client understand:
1. What these funding results mean for them specifically
2. Why they got these results (CHC probability, LA funding, DPA eligibility)
3. What they should do next to maximise their funding
4. Important things to know and common mistakes to avoid

## CRITICAL: SAVINGS EXPLANATION
If savings.is_hypothetical is true, this means the client has LOW probability of receiving funding (< 50%). In this case:
- DO NOT present savings as "expected" or "likely" savings
- Clearly explain that savings are HYPOTHETICAL - what they WOULD save IF they received funding
- Emphasize that current eligibility is LOW and they are NOT likely to receive this funding
- Explain what changes would be needed to improve eligibility
- If hypothetical_weekly_savings is provided, explain what they would save IF funding were received, but make it clear this is conditional
- MOST IMPORTANTLY: Provide detailed, practical steps they can take to improve their eligibility (see below)

If savings.is_hypothetical is false, you can present savings as expected/likely savings based on probability.

## PRACTICAL STEPS TO IMPROVE ELIGIBILITY
If savings.is_hypothetical is true, you MUST provide detailed, actionable steps in "practical_steps_to_improve" section. These should be:
- Specific and actionable (not vague)
- Include timelines (e.g., "Within 2 weeks", "Within 1-2 months")
- Include expected impact (what improvement they can expect)
- Organised by category (CHC Eligibility, LA Funding, DPA, General)
- Based on their specific circumstances (CHC probability, capital assessed, etc.)

Examples of good practical steps:
- "Document all health needs comprehensively - Request detailed medical reports from GP, specialists. Document all 12 DST domains. Timeline: Immediately - ongoing. Expected impact: Could increase CHC probability from 34% to 50-70%"
- "Reduce capital below £23,250 threshold - Your capital (£45,000) exceeds threshold by £21,750. Legal ways: spend on care costs, home adaptations, investment bonds. Get professional advice. Timeline: Plan over 6-12 months. Expected impact: Would make you eligible for LA funding"

Be specific to this client's situation. Reference actual numbers from the calculation (CHC probability, capital assessed, weekly contribution, etc.) to support your insights.

## REQUIRED JSON STRUCTURE
Return your response as a JSON object with the following structure:
{{
  "overall_explanation": {{
    "summary": "string",
    "key_findings": ["string1", "string2", ...],
    "confidence_level": "high" | "medium" | "moderate"
  }},
  "chc_explanation": {{
    "what_it_means": "string",
    "eligibility_factors": ["string1", "string2", ...],
    "next_steps": ["string1", "string2", ...],
    "important_notes": ["string1", "string2", ...]
  }},
  "la_funding_explanation": {{
    "what_it_means": "string",
    "means_test_summary": "string",
    "contribution_explanation": "string",
    "tips": ["string1", "string2", ...]
  }},
  "dpa_explanation": {{
    "what_it_means": "string",
    "property_status": "string",
    "benefits": ["string1", "string2", ...],
    "considerations": ["string1", "string2", ...]
  }},
  "expert_advice": {{
    "funding_strategy": "string",
    "maximising_eligibility": ["string1", "string2", ...],
    "common_mistakes": ["string1", "string2", ...],
    "when_to_reassess": "string"
  }},
  "hypothetical_savings_explanation": {{
    "is_applicable": true/false,
    "explanation": "Clear explanation of hypothetical savings (only if is_hypothetical=true)",
    "what_would_be_saved": "Amount that would be saved IF funding received",
    "what_needs_to_change": ["change1", "change2", ...],
    "realistic_pathway": "How to improve eligibility",
    "practical_steps_to_improve": [
      {{
        "category": "CHC Eligibility" | "LA Funding" | "DPA" | "General",
        "step": "Specific actionable step",
        "priority": "high" | "medium" | "low",
        "timeline": "When to do this (e.g., 'Within 2 weeks', 'Immediately - ongoing')",
        "details": "Detailed explanation of what to do and why",
        "expected_impact": "What improvement they can expect (e.g., 'Could increase CHC probability from 34% to 50-70%')"
      }}
    ]
  }},
  "actionable_next_steps": [
    {{
      "step": "string",
      "priority": "high" | "medium" | "low",
      "timeline": "string",
      "details": "string"
    }}
  ]
}}

Return ONLY valid JSON, no markdown, no code blocks."""
            
            # Call OpenAI API with structured output
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Prepare OpenAI request payload
                payload = {
                    "model": "gpt-4o",  # Using gpt-4o for better quality
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt + "\n\nIMPORTANT: Return your response as valid JSON matching the schema provided. Do not include markdown code blocks, just return pure JSON."
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "response_format": {"type": "json_object"}  # OpenAI structured output
                }
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
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
                            raise ValueError("Could not parse JSON from response")
                    
                    result = {
                        "generated_at": datetime.now().isoformat(),
                        "model": "gpt-4o",
                        "insights": insights_json,
                        "method": "openai_structured_output"
                    }
                    print(f"✅ OpenAI insights parsed: {list(result.keys())}")
                    print(f"   Insights data keys: {list(result.get('insights', {}).keys())}")
                    return result
                else:
                    print("⚠️ No choices in OpenAI response")
                    perplexity_result = await self._try_perplexity_insights(calculation_result, {})
                    if perplexity_result:
                        return perplexity_result
                    return self._generate_hardcoded_fallback(calculation_result)
                    
            except Exception as e:
                print(f"⚠️ OpenAI API call failed: {e}")
                import traceback
                print(traceback.format_exc())
                perplexity_result = await self._try_perplexity_insights(calculation_result, patient_profile)
                if perplexity_result:
                    return perplexity_result
                return self._generate_hardcoded_fallback(calculation_result)
                
        except Exception as e:
            print(f"⚠️ Error generating LLM insights: {e}")
            import traceback
            print(traceback.format_exc())
            perplexity_result = await self._try_perplexity_insights(calculation_result, patient_profile)
            if perplexity_result:
                return perplexity_result
            return self._generate_hardcoded_fallback(calculation_result)
    
    def _prepare_context(self, calculation_result: Dict[str, Any], patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare simplified context for LLM"""
        context = {
            "age": patient_profile.get("age", 0),
            "chc_eligibility": {
                "probability_percent": calculation_result.get("chc_eligibility", {}).get("probability_percent", 0),
                "is_likely_eligible": calculation_result.get("chc_eligibility", {}).get("is_likely_eligible", False),
                "threshold_category": calculation_result.get("chc_eligibility", {}).get("threshold_category", ""),
                "reasoning": calculation_result.get("chc_eligibility", {}).get("reasoning", "")
            },
            "la_support": {
                "top_up_probability_percent": calculation_result.get("la_support", {}).get("top_up_probability_percent", 0),
                "full_support_probability_percent": calculation_result.get("la_support", {}).get("full_support_probability_percent", 0),
                "capital_assessed": calculation_result.get("la_support", {}).get("capital_assessed", 0),
                "weekly_contribution": calculation_result.get("la_support", {}).get("weekly_contribution"),
                "is_fully_funded": calculation_result.get("la_support", {}).get("is_fully_funded", False)
            },
            "dpa_eligibility": {
                "is_eligible": calculation_result.get("dpa_eligibility", {}).get("is_eligible", False),
                "property_disregarded": calculation_result.get("dpa_eligibility", {}).get("property_disregarded", False),
                "reasoning": calculation_result.get("dpa_eligibility", {}).get("reasoning", "")
            },
            "savings": {
                "annual_gbp": calculation_result.get("savings", {}).get("annual_gbp", 0),
                "weekly_savings": calculation_result.get("savings", {}).get("weekly_savings", 0),
                "is_hypothetical": calculation_result.get("savings", {}).get("is_hypothetical", False),
                "hypothetical_weekly_savings": calculation_result.get("savings", {}).get("hypothetical_weekly_savings"),
                "highest_probability": calculation_result.get("savings", {}).get("highest_probability", 0.0)
            },
            "means_test_breakdown": calculation_result.get("_means_test_breakdown", {})
        }
        
        return context
    
    async def _try_perplexity_insights(
        self,
        calculation_result: Dict[str, Any],
        patient_profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Try to generate insights using Perplexity API as fallback
        """
        try:
            from config_manager import get_credentials
            creds = get_credentials()
            
            if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
                print("⚠️ Perplexity credentials not configured")
                return None
            
            perplexity_key = getattr(creds.perplexity, 'api_key', None)
            if not perplexity_key or perplexity_key.startswith('your-'):
                print("⚠️ Perplexity API key not set")
                return None
            
            print(f"📡 Using Perplexity API for insights generation")
            
            # Create HTTP client
            if not hasattr(self, '_perplexity_client') or self._perplexity_client is None:
                self._perplexity_client = httpx.AsyncClient(timeout=60.0)
            
            context = self._prepare_context(calculation_result, patient_profile)
            
            # Prepare Perplexity request
            headers = {
                "Authorization": f"Bearer {perplexity_key}",
                "Content-Type": "application/json"
            }
            
            user_prompt = f"""Analyze this UK care funding eligibility calculation and provide expert insights in JSON format.

## PATIENT PROFILE
- Age: {patient_profile.get('age', 'Unknown')}

## CALCULATION RESULTS
- CHC Probability: {context['chc_eligibility']['probability_percent']}%
- LA Support: {context['la_support']['full_support_probability_percent']}%
- Capital Assessed: £{context['la_support']['capital_assessed']:,.0f}
- DPA Eligible: {context['dpa_eligibility']['is_eligible']}

## REQUIRED JSON RESPONSE
Return ONLY a valid JSON object (no markdown) with this exact structure:
{{
  "overall_explanation": {{
    "summary": "Clear explanation of what these results mean",
    "key_findings": ["finding1", "finding2", "finding3"],
    "confidence_level": "high|medium|moderate"
  }},
  "chc_explanation": {{
    "what_it_means": "What the CHC probability means",
    "eligibility_factors": ["factor1", "factor2"],
    "next_steps": ["step1", "step2"],
    "important_notes": ["note1", "note2"]
  }},
  "la_funding_explanation": {{
    "what_it_means": "What LA funding means",
    "means_test_summary": "Summary of means test",
    "contribution_explanation": "Explanation of contributions",
    "tips": ["tip1", "tip2"]
  }},
  "dpa_explanation": {{
    "what_it_means": "What DPA means",
    "property_status": "Status of property",
    "benefits": ["benefit1"],
    "considerations": ["consideration1"]
  }},
  "expert_advice": {{
    "funding_strategy": "Recommended strategy",
    "maximising_eligibility": ["idea1"],
    "common_mistakes": ["mistake1"],
    "when_to_reassess": "When to reassess"
  }},
  "actionable_next_steps": [
    {{"step": "action", "priority": "high|medium|low", "timeline": "timing", "details": "details"}}
  ]
}}"""
            
            payload = {
                "model": "sonar",  # Perplexity sonar model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a UK care funding expert. Respond with valid JSON only, no markdown."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            response = await self._perplexity_client.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("choices") and len(data["choices"]) > 0:
                response_text = data["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    insights_json = json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        insights_json = json.loads(json_match.group(0))
                    else:
                        print("⚠️ Could not parse Perplexity JSON response")
                        return None
                
                result = {
                    "generated_at": datetime.now().isoformat(),
                    "model": "sonar",
                    "insights": insights_json,
                    "method": "perplexity_api"
                }
                print(f"✅ Perplexity insights generated successfully")
                return result
            else:
                print("⚠️ No choices in Perplexity response")
                return None
                
        except Exception as e:
            print(f"⚠️ Perplexity API error: {e}")
            return None
    
    def _generate_hardcoded_fallback(self, calculation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent fallback insights based on calculation results"""
        print(f"📝 _generate_hardcoded_fallback called (intelligent fallback)")
        print(f"   Calculation result keys: {list(calculation_result.keys())}")
        
        # Extract key data
        chc_prob = calculation_result.get("chc_eligibility", {}).get("probability_percent", 0)
        chc_reasoning = calculation_result.get("chc_eligibility", {}).get("reasoning", "")
        la_support = calculation_result.get("la_support", {})
        la_full_support = la_support.get("full_support_probability_percent", 0)
        capital_assessed = la_support.get("capital_assessed", 0)
        dpa = calculation_result.get("dpa_eligibility", {})
        dpa_eligible = dpa.get("is_eligible", False)
        savings = calculation_result.get("savings", {})
        weekly_savings = savings.get("weekly_savings", 0)
        is_hypothetical = savings.get("is_hypothetical", False)
        hypothetical_weekly_savings = savings.get("hypothetical_weekly_savings")
        highest_probability = savings.get("highest_probability", 0.0)
        
        print(f"   CHC prob: {chc_prob}, LA support keys: {list(la_support.keys())}, DPA keys: {list(dpa.keys())}")
        print(f"   Savings: is_hypothetical={is_hypothetical}, highest_prob={highest_probability}")
        
        # Build intelligent summary based on results
        chc_status = "likely eligible" if chc_prob >= 70 else "possible" if chc_prob >= 50 else "unlikely"
        la_status = "likely eligible" if la_full_support >= 70 else "possible" if la_full_support >= 50 else "unlikely"
        dpa_status = "eligible" if dpa_eligible else "not eligible"
        
        summary = f"Based on your circumstances, you have a {chc_prob}% probability of CHC eligibility and {la_full_support}% probability of LA funding support. "
        if chc_prob >= 70:
            summary += "You appear to be a strong candidate for NHS funding. "
        elif chc_prob >= 50:
            summary += "CHC assessment may be worth pursuing. "
        else:
            summary += "LA funding and private resources will likely be primary options. "
        
        # Use British English spelling
        # Convert to British English
        summary = (summary.replace("optimize", "optimise")
                   .replace("organize", "organise")
                   .replace("maximize", "maximise")
                   .replace("maximizing", "maximising")
                   .replace("color", "colour")
                   .replace("favor", "favour")
                   .replace("realize", "realise")
                   .replace("center", "centre")
                   .replace("unfavorable", "unfavourable")
                   .replace("unfavourable", "unfavourable"))  # Ensure British spelling
        
        # Handle savings explanation based on whether it's hypothetical
        if is_hypothetical and hypothetical_weekly_savings:
            summary += f"Note: While your current eligibility probability is low ({highest_probability*100:.0f}%), if you were to receive funding, you could potentially save £{hypothetical_weekly_savings:.2f} per week. "
            summary += "However, this is hypothetical and depends on improving your eligibility."
        elif weekly_savings > 0 and not is_hypothetical:
            summary += f"Expected weekly savings: £{weekly_savings:.2f}."
        
        result = {
            "generated_at": datetime.now().isoformat(),
            "model": "intelligent_fallback",
            "method": "intelligent_fallback",
            "insights": {
                "overall_explanation": {
                    "summary": summary,
                    "key_findings": [
                        f"CHC eligibility probability: {chc_prob}% ({chc_status})",
                        f"LA funding support: {la_full_support}% ({la_status})",
                        f"DPA eligibility: {dpa_status}",
                        f"Capital assessed: £{capital_assessed:,.0f}",
                        f"{'Hypothetical savings (if funding received)' if is_hypothetical else 'Expected savings'}: £{weekly_savings * 52:,.0f} annually" + (f" (would be £{hypothetical_weekly_savings * 52:,.0f} if funding received)" if is_hypothetical and hypothetical_weekly_savings else "")
                    ],
                    "confidence_level": "high"
                },
                "chc_explanation": {
                    "what_it_means": f"A CHC probability of {chc_prob}% means you have a {chc_status} chance of qualifying for full NHS funding of your care costs.",
                    "eligibility_factors": [
                        "Your documented health needs (breathing, mobility, cognition, etc.)",
                        "Whether you have a 'primary health need' that drives your care requirements",
                        "Consistency and complexity of your care needs",
                        f"Current assessment: {chc_reasoning}" if chc_reasoning else "Your health domain scores"
                    ],
                    "next_steps": [
                        "Contact your local CCG (Clinical Commissioning Group) to discuss a full CHC assessment",
                        "Gather comprehensive medical evidence from your GP and specialists",
                        "Consider independent advice - some charities offer free CHC guidance"
                    ] if chc_prob >= 30 else [
                        "Focus on LA funding as primary option",
                        "Explore private care insurance options",
                        "Contact a care funding specialist for alternative strategies"
                    ],
                    "important_notes": [
                        "CHC assessments are subjective and can vary by assessor",
                        "You can request a reassessment if your health changes",
                        "Backdated CHC funding may be available in some cases"
                    ]
                },
                "la_funding_explanation": {
                    "what_it_means": "Local Authority funding is means-tested - your access depends on your capital and income, not just health needs.",
                    "means_test_summary": f"Your capital assessed at £{capital_assessed:,.0f}. " + 
                        ("You may qualify for support." if capital_assessed < 23250 else "You exceed the capital threshold for support." if capital_assessed > 23250 else "You are at the capital threshold."),
                    "contribution_explanation": (
                        f"You need to contribute £{la_support.get('weekly_contribution', 0) or 0}/week towards care costs."
                        if la_support.get('weekly_contribution') 
                        else "Full LA support may be available depending on income."
                    ),
                    "tips": [
                        "Review all allowed disregards (disability-related spending, personal injury compensation, etc.)",
                        "Keep documentation of any care-related expenses",
                        "Reassess annually as thresholds and circumstances change"
                    ]
                },
                "dpa_explanation": {
                    "what_it_means": "A Deferred Payment Agreement allows you to delay selling your property to pay for care.",
                    "property_status": "Your property may be disregarded from means testing in certain circumstances.",
                    "benefits": [
                        "Keep your home while receiving care",
                        "Pay for care costs later from property sale"
                    ],
                    "considerations": [
                        "Interest charges apply on deferred amounts",
                        "Property will eventually need to be sold",
                        "Eligibility depends on specific circumstances"
                    ]
                },
                    "expert_advice": {
                    "funding_strategy": "Review all three funding options (CHC, LA, DPA) to determine the best approach for your situation.",
                    "maximising_eligibility": [
                        "Ensure all health needs are properly documented",
                        "Gather supporting medical evidence",
                        "Consider professional funding advice"
                    ],
                    "common_mistakes": [
                        "Not declaring all assets and income",
                        "Missing deadlines for assessments",
                        "Not appealing unfavourable decisions"
                    ],
                    "when_to_reassess": "Reassess if your health needs change significantly or if your financial situation changes."
                },
                "hypothetical_savings_explanation": {
                    "is_applicable": is_hypothetical,
                    "explanation": (
                        f"IMPORTANT: Your current eligibility probability is LOW ({highest_probability*100:.0f}%), meaning you are NOT likely to receive funding at this time. "
                        f"The savings shown (£{weekly_savings:.2f}/week) are HYPOTHETICAL - they represent what you WOULD save IF you were to receive funding, "
                        f"but this is unlikely given your current circumstances. "
                        f"If you were to receive funding, you could potentially save £{hypothetical_weekly_savings:.2f}/week, "
                        f"but this depends on significant improvements in your eligibility."
                        if is_hypothetical and hypothetical_weekly_savings
                        else "Not applicable - you have realistic probability of receiving funding."
                    ),
                    "what_would_be_saved": (
                        f"£{hypothetical_weekly_savings:.2f}/week (£{hypothetical_weekly_savings * 52:,.0f}/year) if funding were received"
                        if is_hypothetical and hypothetical_weekly_savings
                        else "N/A"
                    ),
                    "what_needs_to_change": [
                        f"Increase CHC probability from {chc_prob}% to at least 50%+ by demonstrating primary health need",
                        "Improve health domain scores (especially if currently low)",
                        "Document unpredictable or fluctuating health needs",
                        "Reduce capital below £23,250 for LA funding eligibility" if capital_assessed > 23250 else "Maintain capital below £23,250 for LA funding"
                    ] if is_hypothetical else [],
                    "realistic_pathway": (
                        "To realistically access funding, you would need to either: "
                        "(1) Demonstrate a significant primary health need that drives your care requirements (for CHC), "
                        "(2) Reduce your capital below the LA threshold (for LA funding), or "
                        "(3) Show that your health needs have become more complex, unpredictable, or intensive. "
                        "Consider consulting with a care funding specialist to explore these options."
                        if is_hypothetical
                        else "You have a realistic pathway to funding based on current eligibility."
                    ),
                    "practical_steps_to_improve": self._generate_practical_steps_to_improve(
                        chc_prob, la_full_support, capital_assessed, dpa_eligible, 
                        is_hypothetical, chc_reasoning, la_support
                    ) if is_hypothetical else []
                },
                "actionable_next_steps": self._generate_actionable_steps(
                    chc_prob, la_full_support, capital_assessed, dpa_eligible,
                    is_hypothetical, chc_reasoning, la_support
                )
            },
            "method": "fallback"
        }
        
        print(f"✅ Fallback insights created: {list(result.keys())}")
        print(f"   Insights keys: {list(result.get('insights', {}).keys())}")
        return result
    
    def _generate_practical_steps_to_improve(
        self,
        chc_prob: float,
        la_full_support: float,
        capital_assessed: float,
        dpa_eligible: bool,
        is_hypothetical: bool,
        chc_reasoning: str,
        la_support: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate practical, actionable steps to improve funding eligibility.
        
        Returns list of steps with priority, timeline, and specific actions.
        """
        steps = []
        
        # CHC improvement steps
        if chc_prob < 50:
            steps.append({
                "category": "CHC Eligibility",
                "step": "Document all health needs comprehensively",
                "priority": "high",
                "timeline": "Immediately - ongoing",
                "details": (
                    "Request detailed medical reports from GP, specialists, and care providers. "
                    "Document: (1) All 12 DST domains with severity levels, "
                    "(2) Unpredictable or fluctuating conditions, "
                    "(3) Complex therapies (PEG feeding, tracheostomy, injections), "
                    "(4) Primary health need that drives care requirements. "
                    f"Current CHC probability: {chc_prob}% - aim to reach 50%+ for realistic eligibility."
                ),
                "expected_impact": f"Could increase CHC probability from {chc_prob}% to 50-70%"
            })
            
            if chc_prob < 30:
                steps.append({
                    "category": "CHC Eligibility",
                    "step": "Request NHS Continuing Healthcare (CHC) Checklist Assessment",
                    "priority": "high",
                    "timeline": "Within 2-4 weeks",
                    "details": (
                        "Contact your local ICB (Integrated Care Board) to request a CHC Checklist. "
                        "Even with low probability, the assessment process can help identify areas to improve. "
                        "If Checklist is positive, you'll proceed to full DST assessment. "
                        "Bring all medical evidence, care plans, and documentation of health needs."
                    ),
                    "expected_impact": "Formal assessment may identify previously undocumented needs"
                })
            
            steps.append({
                "category": "CHC Eligibility",
                "step": "Focus on demonstrating 'Primary Health Need'",
                "priority": "high",
                "timeline": "Within 1-2 months",
                "details": (
                    "CHC requires a 'primary health need' - health needs that are the main reason for care. "
                    "Work with healthcare professionals to clearly document: "
                    "(1) Nature - what health conditions require care, "
                    "(2) Intensity - how much care is needed, "
                    "(3) Complexity - multiple interacting conditions, "
                    "(4) Unpredictability - fluctuating or deteriorating conditions. "
                    "This is the key factor that distinguishes CHC from social care needs."
                ),
                "expected_impact": "Primary health need is the critical factor for CHC eligibility"
            })
        
        # LA funding improvement steps
        if capital_assessed > 23250:
            capital_excess = capital_assessed - 23250
            steps.append({
                "category": "LA Funding",
                "step": f"Reduce capital below £23,250 threshold",
                "priority": "high",
                "timeline": "Plan over 6-12 months",
                "details": (
                    f"Your capital (£{capital_assessed:,.0f}) exceeds the LA threshold by £{capital_excess:,.0f}. "
                    "Legal ways to reduce capital: "
                    "(1) Spend on care costs (but be careful of 'deprivation of assets' rules), "
                    "(2) Use capital for home adaptations or necessary expenses, "
                    "(3) Consider gifting (but only if done >6 months before care assessment and not to avoid care costs), "
                    "(4) Explore investment bonds that may be disregarded. "
                    "⚠️ IMPORTANT: Get professional financial advice - deprivation of assets can disqualify you."
                ),
                "expected_impact": f"Would make you eligible for LA funding (currently {la_full_support}% probability)"
            })
        
        if capital_assessed <= 23250 and la_full_support < 50:
            steps.append({
                "category": "LA Funding",
                "step": "Maximise income disregards and DRE (Disability-Related Expenditure)",
                "priority": "medium",
                "timeline": "Within 1 month",
                "details": (
                    "Ensure all eligible income is disregarded: Attendance Allowance, PIP, DLA, "
                    "war pensions, earnings, direct payments, child benefit. "
                    "Also document all Disability-Related Expenditure (DRE): "
                    "specialist equipment, adaptations, extra heating, laundry, transport to medical appointments. "
                    "DRE reduces your assessed income, increasing LA support."
                ),
                "expected_impact": "Could increase LA support probability"
            })
        
        # DPA improvement steps
        if not dpa_eligible and capital_assessed > 23250:
            steps.append({
                "category": "Deferred Payment Agreement",
                "step": "Explore DPA eligibility if capital reduces",
                "priority": "low",
                "timeline": "When capital falls below £23,250",
                "details": (
                    "DPA allows you to delay selling your property to pay for care. "
                    "You become eligible when non-property capital falls below £23,250. "
                    "This can help manage cash flow while keeping your home. "
                    "Interest charges apply on deferred amounts."
                ),
                "expected_impact": "Would enable DPA if capital reduces"
            })
        
        # General improvement steps
        steps.append({
            "category": "General",
            "step": "Request reassessment if health needs change",
            "priority": "medium",
            "timeline": "As health changes occur",
            "details": (
                "If health needs become more complex, unpredictable, or intensive, request a new assessment. "
                "Key triggers: new medical conditions, deterioration, increased care needs, "
                "new complex therapies (PEG, tracheostomy), or hospital admissions. "
                "Keep detailed records of all health changes."
            ),
            "expected_impact": "Reassessment with improved health needs could increase eligibility"
        })
        
        steps.append({
            "category": "General",
            "step": "Seek professional funding advice",
            "priority": "high",
            "timeline": "Within 1 month",
            "details": (
                "Consider consulting: (1) Care funding specialists (some charities offer free advice), "
                "(2) Independent financial advisors specializing in care funding, "
                "(3) Solicitors with expertise in care funding appeals. "
                "They can help: navigate the assessment process, prepare evidence, "
                "appeal unfavourable decisions, and explore all funding options."
            ),
            "expected_impact": "Professional guidance can significantly improve success rates"
        })
        
        return steps
    
    def _generate_actionable_steps(
        self,
        chc_prob: float,
        la_full_support: float,
        capital_assessed: float,
        dpa_eligible: bool,
        is_hypothetical: bool,
        chc_reasoning: str,
        la_support: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate prioritized actionable next steps based on eligibility results.
        """
        steps = []
        
        # If hypothetical, prioritize improvement steps
        if is_hypothetical:
            if chc_prob < 50:
                steps.append({
                    "step": "Document health needs to improve CHC eligibility",
                    "priority": "high",
                    "timeline": "Immediately - ongoing",
                    "details": (
                        f"Current CHC probability: {chc_prob}%. "
                        "Gather comprehensive medical evidence from all healthcare providers. "
                        "Focus on demonstrating primary health need, unpredictable conditions, "
                        "and complex care requirements. Request CHC Checklist assessment."
                    )
                })
            
            if capital_assessed > 23250:
                steps.append({
                    "step": "Develop strategy to reduce capital for LA funding",
                    "priority": "high",
                    "timeline": "Within 3-6 months",
                    "details": (
                        f"Capital (£{capital_assessed:,.0f}) exceeds LA threshold. "
                        "Consult financial advisor about legal ways to reduce capital. "
                        "Be aware of deprivation of assets rules."
                    )
                })
            
            steps.append({
                "step": "Consult care funding specialist",
                "priority": "high",
                "timeline": "Within 1 month",
                "details": (
                    "Professional guidance can help identify specific steps to improve eligibility. "
                    "Some charities offer free advice. Consider independent financial advisor "
                    "specializing in care funding."
                )
            })
        else:
            # If not hypothetical, provide standard next steps
            if chc_prob >= 50:
                steps.append({
                    "step": "Request full CHC DST assessment",
                    "priority": "high",
                    "timeline": "Within 2 weeks",
                    "details": f"With {chc_prob}% probability, you have a good chance. Contact your local ICB."
                })
            
            if la_full_support >= 50:
                steps.append({
                    "step": "Apply for LA funding support",
                    "priority": "high",
                    "timeline": "Within 1 week",
                    "details": "Contact your Local Authority to start the means test process."
                })
            
            steps.append({
                "step": "Gather all required documentation",
                "priority": "medium",
                "timeline": "Within 2 weeks",
                "details": "Medical reports, financial statements, care plans, and evidence of health needs."
            })
        
        return steps

