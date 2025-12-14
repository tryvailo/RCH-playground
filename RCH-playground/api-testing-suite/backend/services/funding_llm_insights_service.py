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
        """
        print(f"🔍 generate_funding_insights called")
        print(f"   OpenAI client available: {self.client is not None}")
        print(f"   OpenAI API key available: {self.openai_api_key is not None}")
        
        if not self.client or not self.openai_api_key:
            print("📝 Using fallback insights (no OpenAI client or API key)")
            fallback_result = self._generate_fallback_insights(calculation_result)
            print(f"✅ Fallback insights generated: {type(fallback_result)}")
            print(f"   Fallback keys: {list(fallback_result.keys()) if isinstance(fallback_result, dict) else 'not a dict'}")
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
                                    "description": "Tips for maximizing LA funding"
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
                                "maximizing_eligibility": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Tips for maximizing funding eligibility"
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
- Funding strategies and optimization
- Common pitfalls and how to avoid them

Your role is to:
1. Explain complex funding calculations in clear, understandable terms
2. Help families understand what their results mean in practical terms
3. Provide actionable advice on next steps
4. Highlight opportunities to maximize funding eligibility
5. Warn about common mistakes

Always be:
- Clear and practical (avoid jargon, explain technical terms)
- Honest about limitations and uncertainties
- Action-oriented with concrete next steps
- Empathetic and supportive
- Focused on helping families access the funding they're entitled to

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
3. What they should do next to maximize their funding
4. Important things to know and common mistakes to avoid

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
    "maximizing_eligibility": ["string1", "string2", ...],
    "common_mistakes": ["string1", "string2", ...],
    "when_to_reassess": "string"
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
                    return self._generate_fallback_insights(calculation_result)
                    
            except Exception as e:
                print(f"⚠️ OpenAI API call failed: {e}")
                import traceback
                print(traceback.format_exc())
                return self._generate_fallback_insights(calculation_result)
                
        except Exception as e:
            print(f"⚠️ Error generating LLM insights: {e}")
            import traceback
            print(traceback.format_exc())
            return self._generate_fallback_insights(calculation_result)
    
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
                "weekly_savings": calculation_result.get("savings", {}).get("weekly_savings", 0)
            },
            "means_test_breakdown": calculation_result.get("_means_test_breakdown", {})
        }
        
        return context
    
    def _generate_fallback_insights(self, calculation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic fallback insights when LLM is unavailable"""
        print(f"📝 _generate_fallback_insights called")
        print(f"   Calculation result keys: {list(calculation_result.keys())}")
        
        chc_prob = calculation_result.get("chc_eligibility", {}).get("probability_percent", 0)
        la_support = calculation_result.get("la_support", {})
        dpa = calculation_result.get("dpa_eligibility", {})
        
        print(f"   CHC prob: {chc_prob}, LA support keys: {list(la_support.keys())}, DPA keys: {list(dpa.keys())}")
        
        result = {
            "generated_at": datetime.now().isoformat(),
            "model": "fallback",
            "insights": {
                "overall_explanation": {
                    "summary": f"Your funding eligibility calculation shows a CHC probability of {chc_prob}% and LA funding support of {la_support.get('full_support_probability_percent', 0)}%. These results are based on your specific circumstances including age, health needs, and financial situation.",
                    "key_findings": [
                        f"CHC eligibility probability: {chc_prob}%",
                        f"LA funding support: {la_support.get('full_support_probability_percent', 0)}%",
                        f"DPA eligibility: {'Yes' if dpa.get('is_eligible') else 'No'}"
                    ],
                    "confidence_level": "medium"
                },
                "chc_explanation": {
                    "what_it_means": f"A CHC probability of {chc_prob}% indicates your likelihood of qualifying for NHS Continuing Healthcare funding.",
                    "eligibility_factors": [
                        "Your health needs and care requirements",
                        "DST domain assessments",
                        "Primary health need indicators"
                    ],
                    "next_steps": [
                        "Contact your local CCG to request a CHC assessment",
                        "Gather medical evidence supporting your health needs",
                        "Consider getting professional advice"
                    ]
                },
                "la_funding_explanation": {
                    "what_it_means": "Local Authority funding is means-tested based on your capital assets and income.",
                    "means_test_summary": f"Your capital has been assessed at £{la_support.get('capital_assessed', 0):,.0f}.",
                    "contribution_explanation": f"You may need to contribute {la_support.get('weekly_contribution', 0) or 0} per week towards your care costs." if la_support.get('weekly_contribution') else "You may be eligible for full LA funding support.",
                    "tips": [
                        "Ensure all assets and income are properly declared",
                        "Check if you qualify for any disregards",
                        "Review your means test calculation carefully"
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
                    "maximizing_eligibility": [
                        "Ensure all health needs are properly documented",
                        "Gather supporting medical evidence",
                        "Consider professional funding advice"
                    ],
                    "common_mistakes": [
                        "Not declaring all assets and income",
                        "Missing deadlines for assessments",
                        "Not appealing unfavorable decisions"
                    ],
                    "when_to_reassess": "Reassess if your health needs change significantly or if your financial situation changes."
                },
                "actionable_next_steps": [
                    {
                        "step": "Review your CHC eligibility",
                        "priority": "high",
                        "timeline": "Within 2 weeks",
                        "details": f"With a {chc_prob}% probability, consider requesting a CHC assessment"
                    },
                    {
                        "step": "Contact your Local Authority",
                        "priority": "high",
                        "timeline": "Within 1 week",
                        "details": "Discuss LA funding options and means test"
                    },
                    {
                        "step": "Seek professional advice",
                        "priority": "medium",
                        "timeline": "Within 1 month",
                        "details": "Consider consulting a care funding specialist"
                    }
                ]
            },
            "method": "fallback"
        }
        
        print(f"✅ Fallback insights created: {list(result.keys())}")
        print(f"   Insights keys: {list(result.get('insights', {}).keys())}")
        return result

