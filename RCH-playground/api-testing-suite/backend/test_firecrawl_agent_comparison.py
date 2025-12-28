#!/usr/bin/env python3
"""
Test script comparing Firecrawl Agent vs Perplexity vs Google Reviews
for Staff Quality Data section.

This script tests:
1. Firecrawl Agent - new automatic search and extraction
2. Perplexity - current fallback approach
3. Google Reviews - current primary source

Usage:
    python test_firecrawl_agent_comparison.py
"""
import asyncio
import json
import sys
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import get_credentials
from utils.auth import credentials_store
from utils.client_factory import (
    get_firecrawl_client,
    get_perplexity_client,
    get_google_places_client
)
from api_clients.firecrawl_client import FirecrawlAPIClient
from api_clients.perplexity_client import PerplexityAPIClient


class ReviewComparisonTest:
    """Test suite for comparing review sources"""
    
    def __init__(self):
        self.creds = get_credentials()
        credentials_store['default'] = self.creds
        
        self.firecrawl_client = None
        self.perplexity_client = None
        self.google_places_client = None
        
        # Test care home - First preset from StaffQualityData.tsx
        self.test_home = {
            'name': 'Westgate House Care Home',
            'location_id': '1-125863016',  # CQC location ID from preset
            'address': '178 Romford Road, Forest Gate',
            'postcode': 'E7 9HY',
            'city': 'London'
        }
        
        self.results = {
            'firecrawl_agent': None,
            'perplexity': None,
            'google_reviews': None,
            'comparison': {}
        }
    
    async def initialize_clients(self):
        """Initialize all API clients"""
        print('=' * 70)
        print('🔧 INITIALIZING CLIENTS')
        print('=' * 70)
        
        # Firecrawl
        try:
            self.firecrawl_client = get_firecrawl_client()
            if self.firecrawl_client:
                print('✅ Firecrawl client initialized')
            else:
                print('⚠️ Firecrawl client not available')
        except Exception as e:
            print(f'⚠️ Firecrawl client error: {e}')
        
        # Perplexity
        try:
            self.perplexity_client = get_perplexity_client()
            if self.perplexity_client:
                print('✅ Perplexity client initialized')
            else:
                print('⚠️ Perplexity client not available')
        except Exception as e:
            print(f'⚠️ Perplexity client error: {e}')
        
        # Google Places
        try:
            self.google_places_client = get_google_places_client()
            if self.google_places_client:
                print('✅ Google Places client initialized')
            else:
                print('⚠️ Google Places client not available')
        except Exception as e:
            print(f'⚠️ Google Places client error: {e}')
        
        print()
    
    async def test_firecrawl_agent(self) -> Dict[str, Any]:
        """Test Firecrawl Agent for extracting employee reviews"""
        print('=' * 70)
        print('🤖 TESTING FIRECRAWL AGENT')
        print('=' * 70)
        
        if not self.firecrawl_client:
            return {'error': 'Firecrawl client not available'}
        
        home = self.test_home
        start_time = time.time()
        
        # Define schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "reviews": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "rating": {"type": "number"},
                            "date": {"type": "string"},
                            "source": {"type": "string"},
                            "author": {"type": "string"}
                        },
                        "required": ["text", "source"]
                    }
                },
                "company_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "indeed_url": {"type": "string"},
                        "glassdoor_url": {"type": "string"},
                        "average_rating": {"type": "number"},
                        "total_reviews": {"type": "number"}
                    }
                }
            }
        }
        
        # Create prompt for Agent
        prompt = f"""Get employee and staff reviews about "{home['name']}" care home in {home['city']}, UK {home['postcode']}.

Search for reviews on:
1. Indeed UK (uk.indeed.com) - employee reviews and ratings
2. Glassdoor - company reviews from staff
3. Trustpilot - staff reviews and experiences
4. Other UK job review sites

Extract reviews that mention:
- Staff working conditions and environment
- Management quality and leadership
- Pay, benefits, and compensation
- Training, support, and professional development
- Work-life balance and scheduling
- Staff turnover, retention, and morale
- Team dynamics and colleague relationships
- Job satisfaction and career opportunities

Focus ONLY on reviews from:
- Current employees
- Former employees
- Job applicants who interviewed
- Staff members who worked there

EXCLUDE reviews from residents, families, or visitors.

For each review, extract:
- Full review text
- Rating (1-5 stars if available)
- Date of review
- Source platform (Indeed, Glassdoor, Trustpilot, etc.)
- Author/username if available

Return up to 20 most recent and relevant reviews."""
        
        try:
            print(f'📝 Prompt: {prompt[:100]}...')
            print('⏳ Calling Firecrawl Agent (this may take 30-60 seconds)...')
            
            result = await self.firecrawl_client.agent(
                prompt=prompt,
                schema=schema,
                max_credits=50  # Limit credits for testing
            )
            
            elapsed = time.time() - start_time
            
            # Extract reviews from result
            reviews = []
            if isinstance(result, dict):
                if 'reviews' in result:
                    reviews = result['reviews']
                elif 'data' in result and isinstance(result['data'], dict):
                    reviews = result['data'].get('reviews', [])
                elif 'data' in result and isinstance(result['data'], list):
                    reviews = result['data']
            
            print(f'✅ Firecrawl Agent completed in {elapsed:.1f}s')
            print(f'   Found {len(reviews)} reviews')
            
            return {
                'success': True,
                'reviews': reviews,
                'raw_result': result,
                'elapsed_time': elapsed,
                'review_count': len(reviews),
                'sources': list(set(r.get('source', 'Unknown') for r in reviews))
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f'❌ Firecrawl Agent error: {e}')
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'elapsed_time': elapsed
            }
    
    async def test_perplexity(self) -> Dict[str, Any]:
        """Test Perplexity for extracting employee reviews"""
        print('=' * 70)
        print('🔍 TESTING PERPLEXITY')
        print('=' * 70)
        
        if not self.perplexity_client:
            return {'error': 'Perplexity client not available'}
        
        home = self.test_home
        start_time = time.time()
        
        query = f"""Search for employee and staff reviews about "{home['name']}" care home {home['postcode']} on multiple platforms:
        
        Search on these platforms:
        1. Indeed UK - employee reviews and ratings
        2. Glassdoor - company reviews from staff
        3. Trustpilot - staff reviews and experiences
        4. Carehome.co.uk - staff feedback and reviews
        5. Reddit - discussions about working conditions at this care home
        6. Other UK job review sites (Reed, Totaljobs reviews if available)
        
        Find recent reviews (last 12 months) that mention:
        - Staff working conditions and environment
        - Management quality and leadership
        - Pay, benefits, and compensation
        - Training, support, and professional development
        - Work-life balance and scheduling
        - Staff turnover, retention, and morale
        - Team dynamics and colleague relationships
        - Job satisfaction and career opportunities
        
        For each review, extract:
        1. Review text (full quote if possible)
        2. Rating (1-5 stars or score if available)
        3. Date of review
        4. Author/username (if available)
        5. Source platform (Indeed, Glassdoor, Trustpilot, etc.)
        
        Focus ONLY on reviews from:
        - Current employees
        - Former employees
        - Job applicants who interviewed
        - Staff members who worked there
        
        EXCLUDE reviews from:
        - Residents or their families
        - Visitors
        - General public reviews about care quality
        
        Return specific review quotes, ratings, and source platforms."""
        
        try:
            print(f'📝 Query: {query[:100]}...')
            print('⏳ Calling Perplexity API...')
            
            result = await self.perplexity_client.search(
                query=query,
                model="sonar-pro",
                max_tokens=3000,
                search_recency_filter="year"
            )
            
            elapsed = time.time() - start_time
            
            content = result.get('content', '')
            citations = result.get('citations', [])
            
            # Parse reviews from content (simplified - real implementation would use LLM)
            reviews = self._parse_perplexity_reviews(content, citations)
            
            print(f'✅ Perplexity completed in {elapsed:.1f}s')
            print(f'   Found {len(reviews)} reviews')
            print(f'   Citations: {len(citations)}')
            
            return {
                'success': True,
                'reviews': reviews,
                'raw_content': content[:500] + '...' if len(content) > 500 else content,
                'citations': citations,
                'elapsed_time': elapsed,
                'review_count': len(reviews),
                'sources': list(set(r.get('source', 'Unknown') for r in reviews))
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f'❌ Perplexity error: {e}')
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'elapsed_time': elapsed
            }
    
    def _parse_perplexity_reviews(self, content: str, citations: List) -> List[Dict[str, Any]]:
        """Parse reviews from Perplexity response - improved version that filters out noise"""
        import re
        
        reviews = []
        platforms_checked = {
            'Indeed UK': False,
            'Glassdoor': False,
            'Trustpilot': False,
            'Reddit': False,
            'Carehome.co.uk': False,
            'Reed': False,
            'Totaljobs': False
        }
        
        # Keywords that indicate "no reviews found" messages (to filter out)
        no_data_keywords = [
            'no employee reviews found',
            'no reviews found',
            'no staff-specific reviews',
            'no dedicated employer page',
            'no verified employee reviews',
            'yielded no results',
            'returned no matches',
            'contains no entries',
            'zero results',
            'no matches',
            'no discussions',
            'no relevant threads',
            'not found',
            'does not appear',
            'limited presence',
            'no publicly available'
        ]
        
        # Keywords that indicate actual review content
        review_indicators = [
            'review text',
            'rating:',
            'author:',
            'said:',
            'wrote:',
            'mentioned:',
            'commented:',
            'stated:'
        ]
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            line_lower = line_stripped.lower()
            
            # Detect platform sections
            if 'indeed' in line_lower and 'uk' in line_lower:
                current_section = 'Indeed UK'
                platforms_checked['Indeed UK'] = True
            elif 'glassdoor' in line_lower:
                current_section = 'Glassdoor'
                platforms_checked['Glassdoor'] = True
            elif 'trustpilot' in line_lower:
                current_section = 'Trustpilot'
                platforms_checked['Trustpilot'] = True
            elif 'reddit' in line_lower or 'r/' in line_lower:
                current_section = 'Reddit'
                platforms_checked['Reddit'] = True
            elif 'carehome.co.uk' in line_lower or 'carehome' in line_lower:
                current_section = 'Carehome.co.uk'
                platforms_checked['Carehome.co.uk'] = True
            elif 'reed' in line_lower:
                current_section = 'Reed'
                platforms_checked['Reed'] = True
            elif 'totaljobs' in line_lower:
                current_section = 'Totaljobs'
                platforms_checked['Totaljobs'] = True
            
            # Skip lines that are clearly "no data" messages
            if any(no_keyword in line_lower for no_keyword in no_data_keywords):
                # This is a "no reviews found" message - skip it
                continue
            
            # Look for actual review content
            # Check if line contains review indicators and is substantial
            has_review_indicator = any(indicator in line_lower for indicator in review_indicators)
            is_substantial = len(line_stripped) > 50  # Longer lines are more likely to be actual reviews
            
            # Check if line looks like a quote or review text
            looks_like_review = (
                (line_stripped.startswith('"') and line_stripped.endswith('"')) or
                (line_stripped.startswith("'") and line_stripped.endswith("'")) or
                ('**' in line_stripped and ('review' in line_lower or 'rating' in line_lower)) or
                (has_review_indicator and is_substantial)
            )
            
            if looks_like_review or (has_review_indicator and is_substantial):
                # Try to extract rating
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:star|rating|/5|out of 5)', line_lower)
                rating = float(rating_match.group(1)) if rating_match else None
                
                # Try to extract author (look for patterns like "Author:", "u/username", etc.)
                author = None
                author_match = re.search(r'(?:author|username|user):\s*([^\n,]+)', line_lower, re.IGNORECASE)
                if author_match:
                    author = author_match.group(1).strip()
                elif 'u/' in line_stripped:
                    user_match = re.search(r'u/(\w+)', line_stripped)
                    if user_match:
                        author = f"u/{user_match.group(1)}"
                
                # Determine source
                source = current_section or 'Unknown'
                if 'indeed' in line_lower:
                    source = 'Indeed UK'
                elif 'glassdoor' in line_lower:
                    source = 'Glassdoor'
                elif 'trustpilot' in line_lower:
                    source = 'Trustpilot'
                elif 'reddit' in line_lower or 'r/' in line_lower:
                    source = 'Reddit'
                
                # Clean up review text (remove markdown, extra formatting)
                review_text = line_stripped
                review_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', review_text)  # Remove bold
                review_text = re.sub(r'^[-*]\s*', '', review_text)  # Remove list markers
                review_text = review_text.strip('"\'')  # Remove quotes
                
                if len(review_text) > 30:  # Only add substantial reviews
                    reviews.append({
                        'text': review_text,
                        'rating': rating,
                        'source': source,
                        'date': None,
                        'author': author
                    })
        
        # Create summary of platforms checked
        platforms_no_data = [platform for platform, checked in platforms_checked.items() if checked]
        
        # If no real reviews found, add a summary entry
        if len(reviews) == 0 and platforms_no_data:
            reviews.append({
                'text': f"Employee reviews not found on checked platforms: {', '.join(platforms_no_data)}",
                'rating': None,
                'source': 'Summary',
                'date': None,
                'author': None,
                'is_summary': True
            })
        
        return reviews[:20]  # Limit to 20
    
    async def test_google_reviews(self) -> Dict[str, Any]:
        """Test Google Reviews (current implementation)"""
        print('=' * 70)
        print('🌐 TESTING GOOGLE REVIEWS')
        print('=' * 70)
        
        if not self.google_places_client:
            return {'error': 'Google Places client not available'}
        
        home = self.test_home
        start_time = time.time()
        
        try:
            print(f'🔍 Searching for: {home["name"]} {home["postcode"]}')
            print('⏳ Calling Google Places API...')
            
            # Build search query
            query = f"{home['name']} Care Home {home['postcode']} UK"
            
            # Try text_search first (returns list)
            search_results = await self.google_places_client.text_search(query)
            
            place_id = None
            if search_results and len(search_results) > 0:
                # Find first result with ratings
                for result in search_results:
                    if result.get('user_ratings_total', 0) > 0:
                        place_id = result.get('place_id')
                        break
                if not place_id and search_results:
                    place_id = search_results[0].get('place_id')
            else:
                # Fallback to find_place
                place_result = await self.google_places_client.find_place(query)
                if place_result:
                    place_id = place_result.get('place_id')
            
            if not place_id:
                return {
                    'success': False,
                    'error': 'Place not found',
                    'elapsed_time': time.time() - start_time
                }
            
            # Get place details with reviews
            place_details = await self.google_places_client.get_place_details(
                place_id=place_id,
                fields=['reviews', 'rating', 'user_ratings_total']
            )
            
            elapsed = time.time() - start_time
            
            # Places API (New) returns reviews directly, Legacy returns in 'result'
            if 'result' in place_details:
                reviews_data = place_details.get('result', {}).get('reviews', [])
            else:
                reviews_data = place_details.get('reviews', [])
            
            # Filter for staff-related reviews
            staff_reviews = []
            staff_keywords = ['staff', 'carer', 'nurse', 'worker', 'employee', 'management', 'team']
            
            for review in reviews_data:
                text = review.get('text', '').lower()
                if any(keyword in text for keyword in staff_keywords):
                    staff_reviews.append({
                        'text': review.get('text', ''),
                        'rating': review.get('rating', 0),
                        'date': review.get('time', 0),
                        'source': 'Google',
                        'author': review.get('author_name', 'Anonymous')
                    })
            
            print(f'✅ Google Reviews completed in {elapsed:.1f}s')
            print(f'   Found {len(staff_reviews)} staff-related reviews (out of {len(reviews_data)} total)')
            
            return {
                'success': True,
                'reviews': staff_reviews,
                'total_reviews': len(reviews_data),
                'elapsed_time': elapsed,
                'review_count': len(staff_reviews),
                'sources': ['Google']
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f'❌ Google Reviews error: {e}')
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'elapsed_time': elapsed
            }
    
    def compare_results(self):
        """Compare results from all three sources"""
        print('\n' + '=' * 70)
        print('📊 COMPARISON ANALYSIS')
        print('=' * 70)
        
        comparison = {
            'review_counts': {},
            'sources': {},
            'response_times': {},
            'data_quality': {},
            'recommendations': []
        }
        
        # Review counts
        fc_result = self.results.get('firecrawl_agent', {})
        perp_result = self.results.get('perplexity', {})
        google_result = self.results.get('google_reviews', {})
        
        comparison['review_counts'] = {
            'firecrawl_agent': fc_result.get('review_count', 0),
            'perplexity': perp_result.get('review_count', 0),
            'google_reviews': google_result.get('review_count', 0)
        }
        
        # Response times
        comparison['response_times'] = {
            'firecrawl_agent': fc_result.get('elapsed_time', 0),
            'perplexity': perp_result.get('elapsed_time', 0),
            'google_reviews': google_result.get('elapsed_time', 0)
        }
        
        # Sources
        comparison['sources'] = {
            'firecrawl_agent': fc_result.get('sources', []),
            'perplexity': perp_result.get('sources', []),
            'google_reviews': google_result.get('sources', [])
        }
        
        # Print comparison
        print('\n📈 Review Counts:')
        print(f'   Firecrawl Agent: {comparison["review_counts"]["firecrawl_agent"]} reviews')
        print(f'   Perplexity:      {comparison["review_counts"]["perplexity"]} reviews')
        print(f'   Google Reviews:  {comparison["review_counts"]["google_reviews"]} reviews')
        
        print('\n⏱️  Response Times:')
        print(f'   Firecrawl Agent: {comparison["response_times"]["firecrawl_agent"]:.1f}s')
        print(f'   Perplexity:      {comparison["response_times"]["perplexity"]:.1f}s')
        print(f'   Google Reviews:  {comparison["response_times"]["google_reviews"]:.1f}s')
        
        print('\n🌐 Sources Found:')
        print(f'   Firecrawl Agent: {", ".join(comparison["sources"]["firecrawl_agent"]) or "None"}')
        print(f'   Perplexity:      {", ".join(comparison["sources"]["perplexity"]) or "None"}')
        print(f'   Google Reviews:  {", ".join(comparison["sources"]["google_reviews"]) or "None"}')
        
        # Recommendations
        print('\n💡 Recommendations:')
        
        fc_count = comparison['review_counts']['firecrawl_agent']
        perp_count = comparison['review_counts']['perplexity']
        google_count = comparison['review_counts']['google_reviews']
        
        if fc_count > perp_count and fc_count > 0:
            print('   ✅ Firecrawl Agent found more reviews than Perplexity')
            comparison['recommendations'].append('Consider using Firecrawl Agent as primary source')
        elif perp_count > fc_count and perp_count > 0:
            print('   ✅ Perplexity found more reviews than Firecrawl Agent')
            comparison['recommendations'].append('Perplexity may be more effective for this use case')
        
        if google_count > 0:
            print('   ✅ Google Reviews provides family/visitor perspective')
            comparison['recommendations'].append('Keep Google Reviews for family/visitor reviews')
        
        if fc_count == 0 and perp_count == 0:
            print('   ⚠️  Neither Firecrawl Agent nor Perplexity found reviews')
            comparison['recommendations'].append('May need to refine search queries or check data availability')
        
        # Cost considerations
        print('\n💰 Cost Considerations:')
        print('   Firecrawl Agent: Dynamic pricing (5 free runs/day during research preview)')
        print('   Perplexity:      ~$0.005 per query (sonar-pro model)')
        print('   Google Reviews:  Free (within API quota)')
        
        comparison['recommendations'].append('Firecrawl Agent has free tier but costs scale with complexity')
        comparison['recommendations'].append('Perplexity is cost-effective for fallback scenarios')
        
        self.results['comparison'] = comparison
        return comparison
    
    async def run_all_tests(self):
        """Run all comparison tests"""
        await self.initialize_clients()
        
        print('\n' + '=' * 70)
        print('🧪 RUNNING COMPARISON TESTS')
        print('=' * 70)
        print(f'Test Care Home: {self.test_home["name"]}')
        print(f'Location: {self.test_home["address"]}, {self.test_home["postcode"]}')
        print()
        
        # Test Firecrawl Agent
        self.results['firecrawl_agent'] = await self.test_firecrawl_agent()
        print()
        
        # Test Perplexity
        self.results['perplexity'] = await self.test_perplexity()
        print()
        
        # Test Google Reviews
        self.results['google_reviews'] = await self.test_google_reviews()
        print()
        
        # Compare results
        self.compare_results()
        
        # Save results
        output_file = 'firecrawl_agent_comparison_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f'\n💾 Full results saved to: {output_file}')
        print('\n' + '=' * 70)
        print('✅ COMPARISON TEST COMPLETE')
        print('=' * 70)
        
        return self.results


async def main():
    """Main test function"""
    tester = ReviewComparisonTest()
    results = await tester.run_all_tests()
    return results


if __name__ == '__main__':
    results = asyncio.run(main())

