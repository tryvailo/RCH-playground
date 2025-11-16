"""
Perplexity API Client
"""
import httpx
from typing import Dict, Optional


class PerplexityAPIClient:
    """Perplexity API Client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def search(
        self,
        query: str,
        model: str = "sonar-pro",
        max_tokens: int = 500,
        temperature: float = 0.2,
        search_recency_filter: str = "month"
    ) -> Dict:
        """Search with Perplexity API"""
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "return_citations": True,
            "search_recency_filter": search_recency_filter
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self.headers
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", error_text)
                except:
                    error_msg = error_text
                raise Exception(f"Perplexity API returned status {response.status_code}: {error_msg}")
            
            data = response.json()
            
            # Extract content and citations
            content = ""
            citations = []
            
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                content = message.get("content", "")
                
                # Citations might be in the message or in the root
                if "citations" in message:
                    citations = message["citations"]
            
            # Check root level citations
            if "citations" in data:
                citations = data["citations"]
            
            return {
                "content": content,
                "citations": citations,
                "raw_response": data
            }
        except httpx.HTTPError as e:
            error_text = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", e.response.text)
                    error_text = error_msg
                except:
                    error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            raise Exception(f"Perplexity API HTTP error: {error_text}")
        except Exception as e:
            raise Exception(f"Perplexity API error: {str(e)}")
    
    async def monitor_care_home_reputation(
        self,
        home_name: str,
        location: str = ""
    ) -> Dict:
        """Monitor reputation of a care home"""
        location_str = f"in {location}" if location else ""
        
        query = f"""Search for recent news, complaints, or concerns about 
        {home_name} {location_str} in the last 3 months. 
        
        Summarize:
        1. Any positive news (awards, improvements)
        2. Any negative news (complaints, issues, inspections)
        3. Overall reputation status
        
        Provide source links."""
        
        return await self.search(query, search_recency_filter="month")
    
    async def monitor_care_homes_advanced(
        self,
        home_name: str,
        location: str = "",
        date_range: str = "last_7_days"
    ) -> Dict:
        """
        Advanced monitoring with domain filtering and RED FLAGS detection
        
        Args:
            home_name: Name of the care home
            location: Location (city, address, etc.)
            date_range: Date range filter (last_7_days, last_30_days, month, year)
        
        Returns:
            Dict with content, citations, red_flags, and alert_level
        """
        location_str = f"in {location}" if location else ""
        
        query = f'{home_name} {location_str} news incident quality ratings 2025'
        
        # Map date_range to search_recency_filter
        recency_map = {
            "last_7_days": "week",
            "last_30_days": "month",
            "month": "month",
            "year": "year"
        }
        search_recency = recency_map.get(date_range, "month")
        
        # Perform search
        results = await self.search(
            query=query,
            search_recency_filter=search_recency,
            max_tokens=1000
        )
        
        # Analyze results for RED FLAGS
        red_flags = []
        trusted_domains = [
            'bbc.co.uk', 'birminghammail.co.uk', 'manchestereveningnews.co.uk',
            'reddit.com', 'trustpilot.com', 'carehome.co.uk', 
            'cqc.org.uk', 'gov.uk', 'nhs.uk'
        ]
        
        # Check citations for red flags
        citations = results.get("citations", [])
        content_lower = results.get("content", "").lower()
        
        red_flag_keywords = [
            'closure', 'downgrade', 'inspection', 'safeguarding', 
            'outbreak', 'complaint', 'investigation', 'enforcement',
            'staff shortage', 'safety concern', 'neglect'
        ]
        
        for citation in citations:
            url = citation.get("url", "") if isinstance(citation, dict) else str(citation)
            text = citation.get("text", "").lower() if isinstance(citation, dict) else str(citation).lower()
            
            # Check if from trusted domain
            is_trusted = any(domain in url for domain in trusted_domains)
            
            # Check for red flag keywords
            found_flags = [flag for flag in red_flag_keywords if flag in text]
            
            if found_flags and is_trusted:
                severity = "HIGH" if any(flag in text for flag in ['closure', 'safeguarding', 'neglect', 'enforcement']) else "MEDIUM"
                
                red_flags.append({
                    'home': home_name,
                    'headline': citation.get('title', '') if isinstance(citation, dict) else '',
                    'source': url,
                    'severity': severity,
                    'keywords_found': found_flags,
                    'date': citation.get('date', '') if isinstance(citation, dict) else ''
                })
        
        # Also check content for red flags
        content_flags = [flag for flag in red_flag_keywords if flag in content_lower]
        if content_flags:
            # Extract relevant sentences
            sentences = content_lower.split('.')
            flagged_sentences = [s.strip() for s in sentences if any(flag in s for flag in red_flag_keywords)]
            
            if flagged_sentences:
                red_flags.append({
                    'home': home_name,
                    'headline': 'Content Analysis Alert',
                    'source': 'Perplexity Search Results',
                    'severity': 'MEDIUM',
                    'keywords_found': content_flags,
                    'flagged_content': flagged_sentences[:3]  # First 3 flagged sentences
                })
        
        # Determine alert level
        high_severity_count = sum(1 for flag in red_flags if flag['severity'] == 'HIGH')
        alert_level = "HIGH" if high_severity_count > 0 else "MEDIUM" if red_flags else "LOW"
        
        return {
            "content": results.get("content", ""),
            "citations": citations,
            "red_flags": red_flags,
            "alert_level": alert_level,
            "red_flags_count": len(red_flags),
            "high_severity_count": high_severity_count,
            "date_range": date_range,
            "search_query": query
        }
    
    async def find_academic_research(
        self,
        topics: list
    ) -> Dict:
        """
        Find latest academic research on care home topics
        
        Args:
            topics: List of research topics (e.g., ['dementia care', 'staff retention'])
        
        Returns:
            Dict with research results per topic
        """
        research_results = {}
        
        academic_domains = [
            'researchgate.net', 'scholar.google.com', 'pubmed.ncbi.nlm.nih.gov',
            'bmj.com', 'thelancet.com', 'nejm.org', 'jama.com',
            'cochrane.org', 'ncbi.nlm.nih.gov'
        ]
        
        for topic in topics:
            query = f"{topic} care home outcomes 2025 research UK"
            
            try:
                result = await self.search(
                    query=query,
                    search_recency_filter="year",
                    max_tokens=1000
                )
                
                # Filter citations for academic sources
                all_citations = result.get("citations", [])
                academic_citations = []
                
                for citation in all_citations:
                    url = citation.get("url", "") if isinstance(citation, dict) else str(citation)
                    if any(domain in url for domain in academic_domains):
                        academic_citations.append(citation)
                
                research_results[topic] = {
                    "summary": result.get("content", ""),
                    "academic_papers": academic_citations,
                    "total_papers": len(academic_citations),
                    "all_citations": len(all_citations)
                }
            except Exception as e:
                research_results[topic] = {
                    "error": str(e),
                    "academic_papers": [],
                    "total_papers": 0
                }
        
        return research_results
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

