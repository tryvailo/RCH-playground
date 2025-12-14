"""
Staff Quality Service
Implements staff quality score calculation based on CQC ratings, employee reviews, and sentiment analysis.

Algorithm based on staff-quality.md specification.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from api_clients.cqc_client import CQCAPIClient
from utils.client_factory import (
    get_cqc_client, 
    get_google_places_client, 
    get_perplexity_client,
    get_openai_client
)


class StaffQualityService:
    """Service for calculating staff quality scores"""
    
    def __init__(self):
        self.cqc_client = get_cqc_client()
        self.google_places_client = None
        self.perplexity_client = None
        self.openai_client = None
        
        try:
            self.google_places_client = get_google_places_client()
        except Exception as e:
            print(f"Warning: Google Places API not available: {e}")
            self.google_places_client = None
        
        try:
            self.perplexity_client = get_perplexity_client()
        except Exception as e:
            print(f"Warning: Perplexity API not available: {e}")
            self.perplexity_client = None
        
        try:
            self.openai_client = get_openai_client()
        except Exception as e:
            print(f"Warning: OpenAI API not available: {e}")
            self.openai_client = None
    
    async def analyze_by_location_id(self, location_id: str) -> Dict[str, Any]:
        """Analyze staff quality for a care home by CQC location ID"""
        try:
            # Get CQC location data
            location_data = await self.cqc_client.get_location(location_id)
            
            if not location_data:
                raise ValueError(f"CQC location data not found for location_id: {location_id}")
        except Exception as e:
            error_msg = f"Failed to fetch CQC location data for location_id {location_id}: {str(e)}"
            print(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        # Extract CQC ratings
        try:
            cqc_data = self._extract_cqc_ratings(location_data)
        except Exception as e:
            print(f"Error extracting CQC ratings: {e}")
            # Continue with empty ratings rather than failing completely
            cqc_data = {
                'well_led': None,
                'effective': None,
                'last_inspection_date': None,
            }
        
        # Get CQC report for sentiment analysis
        cqc_sentiment = await self._extract_cqc_sentiment(location_data)
        if cqc_sentiment:
            cqc_data['staff_sentiment'] = cqc_sentiment
        
        # Get employee reviews from Google Reviews and Indeed UK
        reviews: List[Dict[str, Any]] = []
        try:
            google_reviews = await self._fetch_google_reviews(
                name=location_data.get('name', ''),
                address=self._extract_address(location_data),
                postcode=location_data.get('postalCode', '')
            )
            reviews.extend(google_reviews)
        except Exception as e:
            print(f"Warning: Failed to fetch Google Reviews: {e}")
        
        # Fetch employee reviews from multiple sources via Perplexity Search
        try:
            employee_reviews = await self._fetch_employee_reviews_from_multiple_sources(
                name=location_data.get('name', ''),
                address=self._extract_address(location_data),
                postcode=location_data.get('postalCode', '')
            )
            reviews.extend(employee_reviews)
        except Exception as e:
            print(f"Warning: Failed to fetch employee reviews from multiple sources: {e}")
        
        # Apply LLM-based sentiment analysis to all reviews
        if reviews and self.openai_client:
            try:
                reviews = await self._apply_llm_sentiment_analysis(reviews)
            except Exception as e:
                print(f"Warning: LLM sentiment analysis failed: {e}")
        
        # Calculate staff quality score
        try:
            staff_quality_score = self._calculate_staff_quality_score(cqc_data, reviews)
        except Exception as e:
            print(f"Error calculating staff quality score: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to calculate staff quality score: {str(e)}")
        
        # Build care home info
        try:
            care_home = {
                'id': location_id,
                'name': location_data.get('name', 'Unknown'),
                'address': self._extract_address(location_data),
                'postcode': location_data.get('postalCode', ''),
                'local_authority': location_data.get('localAuthority', {}).get('name', '') if isinstance(location_data.get('localAuthority'), dict) else '',
            }
        except Exception as e:
            print(f"Error building care home info: {e}")
            # Fallback to minimal info
            care_home = {
                'id': location_id,
                'name': location_data.get('name', 'Unknown'),
                'address': '',
                'postcode': location_data.get('postalCode', ''),
                'local_authority': '',
            }
        
        return {
            'care_home': care_home,
            'cqc_data': cqc_data,
            'reviews': reviews,
            'staff_quality_score': staff_quality_score
        }
    
    async def analyze_by_search(
        self,
        name: Optional[str] = None,
        postcode: Optional[str] = None,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for care home and analyze staff quality"""
        # Search for care home with limited pages to avoid timeout
        # Note: Searching all care homes can be very slow, so we limit aggressively
        search_params = {
            'care_home': True,
            'page_size': 50,  # Smaller page size to reduce memory usage
            'max_pages': 2,  # Limit to 2 pages (100 results max) to prevent timeout
            'verbose': False
        }
        
        try:
            if name:
                # CQC API doesn't support name search directly, so we search and filter
                # Limit search to prevent timeout
                try:
                    all_locations = await self.cqc_client.search_locations(**search_params)
                except Exception as e:
                    raise ValueError(f"Failed to search CQC locations: {str(e)}")
                
                if not all_locations:
                    raise ValueError(f"No CQC locations found. The search may have timed out or returned no results.")
                
                # Filter by name (case-insensitive partial match)
                locations = [
                    loc for loc in all_locations
                    if name.lower() in loc.get('name', '').lower()
                ]
                
                if not locations:
                    raise ValueError(f"No care homes found matching name: '{name}'. Try using a more specific name or provide a postcode.")
                
                # Limit to first 10 matches to avoid processing too many
                locations = locations[:10]
            elif postcode:
                try:
                    all_locations = await self.cqc_client.search_locations(**search_params)
                except Exception as e:
                    raise ValueError(f"Failed to search CQC locations: {str(e)}")
                
                if not all_locations:
                    raise ValueError(f"No CQC locations found. The search may have timed out or returned no results.")
                
                # Filter by postcode
                postcode_normalized = postcode.replace(' ', '').upper()
                locations = [
                    loc for loc in all_locations
                    if loc.get('postalCode') and postcode_normalized in loc.get('postalCode', '').replace(' ', '').upper()
                ]
                
                if not locations:
                    raise ValueError(f"No care homes found matching postcode: '{postcode}'. Please verify the postcode is correct.")
                
                # Limit to first 10 matches
                locations = locations[:10]
            else:
                raise ValueError("Either name or postcode must be provided for search")
            
            # Use first match
            location_id = locations[0].get('locationId')
            if not location_id:
                raise ValueError("Location ID not found in search results. The CQC API may have returned incomplete data.")
            
            # Analyze by location ID (this will also fetch Google Reviews)
            result = await self.analyze_by_location_id(location_id)
            
            return result
            
        except ValueError:
            # Re-raise ValueError as-is
            raise
        except Exception as e:
            # Wrap other exceptions with more context
            raise Exception(f"Error searching for care home: {str(e)}")
    
    def _extract_cqc_ratings(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract CQC ratings from location data"""
        ratings = {
            'well_led': None,
            'effective': None,
            'last_inspection_date': None,
        }
        
        # Extract from currentRatings structure
        current_ratings = location_data.get('currentRatings', {})
        
        # Get overall rating which contains key question ratings
        overall = current_ratings.get('overall', {})
        
        # Extract key question ratings
        key_question_ratings = overall.get('keyQuestionRatings', [])
        for kq in key_question_ratings:
            kq_name = kq.get('name', '')
            if kq_name == 'Well-led':
                ratings['well_led'] = kq.get('rating')
            elif kq_name == 'Effective':
                ratings['effective'] = kq.get('rating')
        
        # Extract last inspection date
        last_inspection = location_data.get('lastInspection')
        if last_inspection:
            ratings['last_inspection_date'] = last_inspection.get('date')
        
        return ratings
    
    async def _extract_cqc_sentiment(self, location_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract staff sentiment from CQC inspection report"""
        try:
            # Get the latest report
            reports = location_data.get('reports', [])
            if not reports:
                return None
            
            # Get the most recent report
            latest_report = sorted(
                reports,
                key=lambda r: r.get('publicationDate', ''),
                reverse=True
            )[0]
            
            report_link_id = latest_report.get('reportLinkId')
            if not report_link_id:
                return None
            
            # Fetch report text
            report_text = await self.cqc_client.get_report(
                report_link_id,
                plain_text=True
            )
            
            if not report_text or not isinstance(report_text, str):
                return None
            
            # Analyze sentiment using keyword matching
            sentiment = self._analyze_report_sentiment(report_text)
            return sentiment
            
        except Exception as e:
            print(f"Error extracting CQC sentiment: {e}")
            return None
    
    def _analyze_report_sentiment(self, report_text: str) -> Dict[str, Any]:
        """Analyze staff sentiment from CQC report text using keyword matching"""
        text_lower = report_text.lower()
        
        # Positive keywords
        positive_patterns = [
            r'staff trained',
            r'low turnover',
            r'good morale',
            r'supportive management',
            r'staff development',
            r'well-trained',
            r'high morale',
            r'good staffing',
            r'adequate staffing',
            r'staff retention',
        ]
        
        # Negative keywords
        negative_patterns = [
            r'staff shortage',
            r'high turnover',
            r'staff morale concern',
            r'insufficient training',
            r'staff vacancy',
            r'understaffed',
            r'staffing concerns',
            r'staffing issues',
            r'poor morale',
            r'staff retention problems',
        ]
        
        # Count matches
        positive_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in positive_patterns
        )
        
        negative_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in negative_patterns
        )
        
        # Neutral mentions (just "staff" or "staffing")
        neutral_count = len(re.findall(r'\bstaff\b|\bstaffing\b', text_lower))
        # Subtract positive and negative mentions from neutral
        neutral_count = max(0, neutral_count - positive_count - negative_count)
        
        # Calculate score
        total = positive_count + neutral_count + negative_count
        if total == 0:
            score = 50  # Neutral if no mentions
        else:
            net_sentiment = (positive_count - negative_count) / total
            score = 50 + (net_sentiment * 50)
        
        return {
            'positive': positive_count,
            'neutral': neutral_count,
            'negative': negative_count,
            'score': round(score, 1)
        }
    
    def _calculate_staff_quality_score(
        self,
        cqc_data: Dict[str, Any],
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate staff quality score based on algorithm from staff-quality.md"""
        
        # Convert CQC ratings to scores
        well_led_score = self._convert_cqc_rating_to_score(
            cqc_data.get('well_led'),
            'well_led'
        )
        effective_score = self._convert_cqc_rating_to_score(
            cqc_data.get('effective'),
            'effective'
        )
        
        # CQC Staff Sentiment score
        staff_sentiment = cqc_data.get('staff_sentiment')
        if staff_sentiment:
            cqc_sentiment_score = staff_sentiment.get('score', 50)
        else:
            cqc_sentiment_score = 50  # Default if no sentiment data
        
        # Employee Reviews Sentiment
        employee_sentiment_score = self._calculate_employee_sentiment(reviews)
        has_employee_reviews = employee_sentiment_score is not None
        
        # Determine weights based on data availability
        if has_employee_reviews:
            weights = {
                'cqc_well_led': 0.40,
                'cqc_effective': 0.20,
                'cqc_staff_sentiment': 0.10,
                'employee_sentiment': 0.30,
            }
        else:
            weights = {
                'cqc_well_led': 0.45,
                'cqc_effective': 0.25,
                'cqc_staff_sentiment': 0.30,
                'employee_sentiment': 0,
            }
        
        # Calculate overall score
        overall_score = (
            well_led_score * weights['cqc_well_led'] +
            effective_score * weights['cqc_effective'] +
            cqc_sentiment_score * weights['cqc_staff_sentiment'] +
            (employee_sentiment_score or 0) * weights['employee_sentiment']
        )
        
        # Determine category
        if overall_score >= 90:
            category = 'EXCELLENT'
        elif overall_score >= 75:
            category = 'GOOD'
        elif overall_score >= 60:
            category = 'ADEQUATE'
        elif overall_score >= 40:
            category = 'CONCERNING'
        else:
            category = 'POOR'
        
        # Determine confidence
        last_inspection_date = cqc_data.get('last_inspection_date')
        inspection_age_months = 24  # Default
        if last_inspection_date:
            try:
                # Handle different date formats
                date_str = str(last_inspection_date)
                if 'T' in date_str:
                    # ISO format with time
                    inspection_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if inspection_date.tzinfo:
                        inspection_date = inspection_date.replace(tzinfo=None)
                elif len(date_str) == 10 and '-' in date_str:
                    # YYYY-MM-DD format
                    inspection_date = datetime.fromisoformat(date_str)
                else:
                    # Try parsing as date string (fallback)
                    try:
                        # Try common date formats
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                            try:
                                inspection_date = datetime.strptime(date_str, fmt)
                                break
                            except:
                                continue
                        else:
                            # If all formats fail, use default
                            raise ValueError("Could not parse date")
                    except:
                        raise ValueError("Could not parse date")
                
                inspection_age_months = (datetime.now() - inspection_date).days // 30
            except Exception as e:
                print(f"Warning: Could not parse inspection date '{last_inspection_date}': {e}")
                inspection_age_months = 24
        
        review_count = len(reviews)
        
        if inspection_age_months < 6 and review_count >= 5:
            confidence = 'High'
        elif inspection_age_months < 12 and review_count >= 3:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        # Generate flags
        flags = []
        
        # Check for missing CQC ratings
        if not cqc_data.get('well_led') and not cqc_data.get('effective'):
            flags.append({
                'type': 'yellow',
                'message': '⚠️ Insufficient CQC data: Missing Well-Led and Effective ratings. Score calculated with limited data.'
            })
        elif not cqc_data.get('well_led'):
            flags.append({
                'type': 'yellow',
                'message': '⚠️ Missing CQC Well-Led rating. Score may be less accurate.'
            })
        elif not cqc_data.get('effective'):
            flags.append({
                'type': 'yellow',
                'message': '⚠️ Missing CQC Effective rating. Score may be less accurate.'
            })
        
        if cqc_data.get('well_led') in ['Requires Improvement', 'Inadequate']:
            flags.append({
                'type': 'red',
                'message': f"🔴 CQC rated \"{cqc_data.get('well_led')}\" for Well-Led - Significant management/leadership concerns identified"
            })
        
        if inspection_age_months > 18:
            flags.append({
                'type': 'yellow',
                'message': f"⚠️ CQC inspection data is {inspection_age_months} months old - may be outdated. Consider requesting updated inspection."
            })
        
        # Check for insufficient employee reviews
        if not has_employee_reviews:
            flags.append({
                'type': 'yellow',
                'message': f'⚠️ Insufficient employee review data: Only {review_count} review(s) found. Need at least 3 relevant reviews for accurate sentiment analysis. Score calculated without employee sentiment component.'
            })
        elif review_count < 5:
            flags.append({
                'type': 'yellow',
                'message': f'⚠️ Limited employee review data: Only {review_count} review(s) found. More reviews would improve accuracy.'
            })
        
        if has_employee_reviews and employee_sentiment_score is not None:
            if cqc_data.get('well_led') == 'Outstanding' and employee_sentiment_score < 40:
                flags.append({
                    'type': 'yellow',
                    'message': '⚠️ CQC rates management highly but employee reviews are negative - verify data recency'
                })
        
        # Check for missing CQC staff sentiment
        if not cqc_data.get('staff_sentiment'):
            flags.append({
                'type': 'yellow',
                'message': '⚠️ No CQC staff sentiment data available from inspection reports. Score calculated without this component.'
            })
        
        # Extract themes from reviews (if any)
        themes = {
            'positive': [],
            'negative': []
        }
        
        for review in reviews:
            text = review.get('text', '').lower()
            if 'supportive' in text or 'good training' in text or 'management' in text:
                themes['positive'].append('Management supportive & approachable')
            if 'training' in text:
                themes['positive'].append('Good training program')
            if 'understaff' in text or 'shortage' in text:
                themes['negative'].append('Understaffed during peak shifts')
            if 'pay' in text or 'salary' in text or 'wage' in text:
                themes['negative'].append('Pay concerns mentioned')
        
        # Remove duplicates
        themes['positive'] = list(set(themes['positive']))
        themes['negative'] = list(set(themes['negative']))
        
        return {
            'overall_score': round(overall_score, 1),
            'category': category,
            'confidence': confidence,
            'components': {
                'cqc_well_led': {
                    'score': well_led_score,
                    'weight': weights['cqc_well_led'],
                    'rating': cqc_data.get('well_led')
                },
                'cqc_effective': {
                    'score': effective_score,
                    'weight': weights['cqc_effective'],
                    'rating': cqc_data.get('effective')
                },
                'cqc_staff_sentiment': {
                    'score': cqc_sentiment_score,
                    'weight': weights['cqc_staff_sentiment']
                },
                'employee_sentiment': {
                    'score': employee_sentiment_score,
                    'weight': weights['employee_sentiment'],
                    'review_count': review_count
                }
            },
            'flags': flags,
            'themes': themes,
            'data_quality': {
                'cqc_data_age': f"{inspection_age_months} months ago" if inspection_age_months > 0 else 'Recent',
                'review_count': review_count,
                'has_insufficient_data': (
                    not has_employee_reviews or 
                    not cqc_data.get('well_led') or 
                    not cqc_data.get('effective') or
                    inspection_age_months > 24
                ),
                'data_completeness': {
                    'has_cqc_well_led': bool(cqc_data.get('well_led')),
                    'has_cqc_effective': bool(cqc_data.get('effective')),
                    'has_cqc_staff_sentiment': bool(cqc_data.get('staff_sentiment')),
                    'has_employee_reviews': has_employee_reviews,
                    'employee_review_count': review_count
                }
            }
        }
    
    def _convert_cqc_rating_to_score(
        self,
        rating: Optional[str],
        rating_type: str
    ) -> float:
        """Convert CQC rating to 0-100 score"""
        if not rating:
            return 50  # Default if no rating
        
        if rating_type == 'well_led':
            rating_map = {
                'Outstanding': 95,
                'Good': 75,
                'Requires Improvement': 40,
                'Inadequate': 10,
            }
        else:  # effective
            rating_map = {
                'Outstanding': 90,
                'Good': 70,
                'Requires Improvement': 35,
                'Inadequate': 5,
            }
        
        return rating_map.get(rating, 50)
    
    def _calculate_employee_sentiment(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Optional[float]:
        """Calculate employee sentiment score from reviews"""
        # Filter relevant reviews
        relevant_reviews = [
            r for r in reviews
            if r.get('sentiment') in ['POSITIVE', 'MIXED', 'NEGATIVE']
        ]
        
        if len(relevant_reviews) < 3:
            return None  # Insufficient data
        
        positive = sum(1 for r in relevant_reviews if r.get('sentiment') == 'POSITIVE')
        mixed = sum(1 for r in relevant_reviews if r.get('sentiment') == 'MIXED')
        negative = sum(1 for r in relevant_reviews if r.get('sentiment') == 'NEGATIVE')
        total = len(relevant_reviews)
        
        return (positive * 100 + mixed * 50 + negative * 0) / total
    
    async def _fetch_google_reviews(
        self,
        name: str,
        address: Optional[str] = None,
        postcode: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch and filter Google Reviews for staff quality analysis"""
        if not self.google_places_client:
            return []
        
        try:
            # Build search query
            query = name
            if postcode:
                query += f" {postcode}"
            elif address:
                query += f" {address}"
            
            # Find place
            place_result = await self.google_places_client.find_place(query)
            if not place_result or not place_result.get('place_id'):
                return []
            
            place_id = place_result.get('place_id')
            
            # Get place details with reviews
            details = await self.google_places_client.get_place_details(
                place_id,
                fields=['name', 'rating', 'user_ratings_total', 'reviews']
            )
            
            if not details or not details.get('reviews'):
                return []
            
            # Filter reviews that mention staff/work conditions
            staff_keywords = [
                'staff', 'carer', 'care worker', 'nurse', 'worker', 'management',
                'work', 'job', 'shift', 'training', 'pay', 'salary', 'wage',
                'employee', 'team', 'colleague', 'supervisor', 'manager'
            ]
            
            filtered_reviews = []
            for review in details.get('reviews', []):
                review_text = review.get('text', '').lower()
                
                # Check if review mentions staff or work conditions
                if any(keyword in review_text for keyword in staff_keywords):
                    # Analyze sentiment
                    sentiment = self._analyze_review_sentiment(review)
                    
                    # Format date - Google Places API returns publishTime in ISO format
                    review_date = None
                    time_value = review.get('time') or review.get('publishTime')
                    if time_value:
                        try:
                            if isinstance(time_value, str):
                                # Google Places API returns ISO format like "2024-01-15T10:30:00Z"
                                if 'T' in time_value:
                                    # Remove timezone info and parse
                                    time_clean = time_value.split('T')[0] if 'T' in time_value else time_value
                                    review_date = time_clean.split('+')[0].split('Z')[0]
                                elif len(time_value) == 10 and '-' in time_value:
                                    # Already in YYYY-MM-DD format
                                    review_date = time_value
                        except Exception as e:
                            print(f"Warning: Could not parse review date: {time_value}, error: {e}")
                    
                    filtered_reviews.append({
                        'source': 'Google',
                        'rating': review.get('rating', 0),
                        'sentiment': sentiment,
                        'text': review.get('text', ''),
                        'date': review_date,
                        'author': review.get('author_name', 'Anonymous')
                    })
            
            return filtered_reviews
            
        except Exception as e:
            print(f"Error fetching Google Reviews: {e}")
            return []
    
    def _analyze_review_sentiment(self, review: Dict[str, Any]) -> str:
        """Analyze sentiment of a single review"""
        text = review.get('text', '').lower()
        rating = review.get('rating', 0)
        
        try:
            rating = float(rating) if rating else 0.0
        except (ValueError, TypeError):
            rating = 0.0
        
        # Positive keywords for staff/work context
        positive_keywords = [
            'supportive', 'good training', 'flexible', 'appreciated', 'valued',
            'great management', 'good team', 'well managed', 'professional',
            'caring management', 'good pay', 'fair', 'respectful'
        ]
        
        # Negative keywords for staff/work context
        negative_keywords = [
            'understaffed', 'shortage', 'low pay', 'poor management', 'disrespectful',
            'high turnover', 'overworked', 'stressful', 'unfair', 'toxic',
            'poor training', 'unsupported', 'neglected', 'exploited'
        ]
        
        # Count keyword matches
        positive_matches = sum(1 for keyword in positive_keywords if keyword in text)
        negative_matches = sum(1 for keyword in negative_keywords if keyword in text)
        
        # Determine sentiment
        if rating >= 4 and positive_matches > negative_matches:
            return 'POSITIVE'
        elif rating <= 2 or negative_matches > positive_matches:
            return 'NEGATIVE'
        elif positive_matches > 0 or negative_matches > 0:
            return 'MIXED'
        else:
            return 'NEUTRAL'
    
    async def _fetch_employee_reviews_from_multiple_sources(
        self,
        name: str,
        address: Optional[str] = None,
        postcode: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch employee reviews from multiple sources using Perplexity Search API
        
        Searches across:
        - Indeed UK (employee reviews)
        - Glassdoor (company reviews)
        - Trustpilot (staff reviews)
        - Carehome.co.uk (staff feedback)
        - Reddit (discussions about working conditions)
        - Other UK job review sites
        """
        if not self.perplexity_client:
            return []
        
        try:
            location_str = postcode or address or ""
            
            query = f"""Search for employee and staff reviews about "{name}" care home {location_str} on multiple platforms:
            
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
            
            Return specific review quotes, ratings, and source platforms. 
            Organize by platform if possible."""
            
            # Search with Perplexity
            result = await self.perplexity_client.search(
                query=query,
                model="sonar-pro",
                max_tokens=3000,
                search_recency_filter="year"
            )
            
            content = result.get('content', '')
            citations = result.get('citations', [])
            
            if not content:
                return []
            
            # Parse reviews from Perplexity response
            reviews = self._parse_employee_reviews_from_multiple_sources(
                content, 
                name, 
                citations
            )
            return reviews
            
        except Exception as e:
            print(f"Error fetching employee reviews from multiple sources via Perplexity: {e}")
            return []
    
    def _parse_employee_reviews_from_multiple_sources(
        self,
        content: str,
        care_home_name: str,
        citations: Optional[List] = None
    ) -> List[Dict[str, Any]]:
        """Parse employee reviews from multiple sources (Indeed, Glassdoor, Trustpilot, etc.) from Perplexity search response"""
        reviews = []
        
        # Keywords to identify staff-related reviews
        staff_keywords = [
            'staff', 'carer', 'care worker', 'nurse', 'worker', 'employee',
            'management', 'work', 'job', 'shift', 'training', 'pay', 'salary',
            'wage', 'colleague', 'supervisor', 'manager', 'team', 'colleague',
            'workplace', 'employment', 'hiring', 'recruitment'
        ]
        
        # Platform detection patterns
        platform_patterns = {
            'Indeed UK': [r'indeed', r'indeed\.co\.uk', r'indeed uk'],
            'Glassdoor': [r'glassdoor', r'glassdoor\.co\.uk'],
            'Trustpilot': [r'trustpilot', r'trustpilot\.co\.uk'],
            'Carehome.co.uk': [r'carehome\.co\.uk', r'carehome'],
            'Reddit': [r'reddit', r'r/\w+'],
            'Reed': [r'reed\.co\.uk', r'reed'],
            'Totaljobs': [r'totaljobs', r'totaljobs\.co\.uk']
        }
        
        def detect_source(text: str, url: str = '') -> str:
            """Detect review source from text and URL"""
            text_lower = text.lower()
            url_lower = url.lower()
            
            for platform, patterns in platform_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower) or re.search(pattern, url_lower):
                        return platform
            
            # Default to generic source if platform not detected
            if any(keyword in text_lower for keyword in ['indeed', 'job site', 'job board']):
                return 'Indeed UK'
            elif any(keyword in text_lower for keyword in ['glassdoor', 'company review']):
                return 'Glassdoor'
            elif any(keyword in text_lower for keyword in ['trustpilot', 'review site']):
                return 'Trustpilot'
            else:
                return 'Employee Review Site'
        
        # Create citation URL map for better source detection
        citation_urls = {}
        if citations:
            for citation in citations:
                if isinstance(citation, dict):
                    url = citation.get('url', '')
                    title = citation.get('title', '')
                    if url:
                        citation_urls[url] = title
        
        # Try to extract review-like patterns from content
        # Perplexity may return structured or unstructured text
        lines = content.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if line contains staff-related keywords
            if any(keyword in line_lower for keyword in staff_keywords):
                # Try to extract rating
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:star|rating|out of 5|/5|out of 10|/10)', line_lower)
                rating = float(rating_match.group(1)) if rating_match else None
                
                # Try to extract date
                date_patterns = [
                    r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}',
                    r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                    r'(last\s+week|last\s+month|recently|this\s+year)'
                ]
                review_date = None
                for pattern in date_patterns:
                    date_match = re.search(pattern, line_lower)
                    if date_match:
                        review_date = date_match.group(0)
                        break
                
                # Extract review text (clean up)
                review_text = line.strip()
                if len(review_text) > 20:  # Only consider substantial reviews
                    # Detect source
                    source = detect_source(review_text)
                    
                    # Analyze sentiment using keyword matching (will be enhanced by LLM later)
                    sentiment = self._analyze_review_sentiment({
                        'text': review_text,
                        'rating': rating or 3.0
                    })
                    
                    reviews.append({
                        'source': source,
                        'rating': rating or 3.0,
                        'sentiment': sentiment,
                        'text': review_text,
                        'date': review_date,
                        'author': 'Anonymous'
                    })
        
        # If no structured reviews found, try to extract from paragraphs
        if not reviews:
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                para_lower = para.lower()
                if any(keyword in para_lower for keyword in staff_keywords) and len(para) > 50:
                    rating_match = re.search(r'(\d+\.?\d*)\s*(?:star|rating|out of 5|/5|out of 10|/10)', para_lower)
                    rating = float(rating_match.group(1)) if rating_match else 3.0
                    
                    # Detect source
                    source = detect_source(para)
                    
                    sentiment = self._analyze_review_sentiment({
                        'text': para,
                        'rating': rating
                    })
                    
                    reviews.append({
                        'source': source,
                        'rating': rating,
                        'sentiment': sentiment,
                        'text': para.strip(),
                        'date': None,
                        'author': 'Anonymous'
                    })
        
        # Remove duplicates based on text similarity
        unique_reviews = []
        seen_texts = set()
        for review in reviews:
            # Normalize text for comparison
            text_normalized = review['text'].lower().strip()[:100]  # First 100 chars
            if text_normalized not in seen_texts:
                seen_texts.add(text_normalized)
                unique_reviews.append(review)
        
        # Limit to 15 most relevant reviews
        return unique_reviews[:15]
    
    async def _apply_llm_sentiment_analysis(
        self,
        reviews: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply LLM-based sentiment analysis to reviews for more accurate classification"""
        if not reviews or not self.openai_client:
            return reviews
        
        try:
            # Batch reviews for efficiency (analyze up to 10 at a time)
            batch_size = 10
            analyzed_reviews = []
            
            for i in range(0, len(reviews), batch_size):
                batch = reviews[i:i + batch_size]
                
                # Prepare review texts for analysis
                review_texts = []
                for review in batch:
                    review_texts.append({
                        'text': review.get('text', ''),
                        'rating': review.get('rating', 0),
                        'source': review.get('source', 'Unknown')
                    })
                
                # Build prompt for sentiment analysis
                prompt = self._build_sentiment_analysis_prompt(review_texts)
                
                # Call OpenAI for sentiment analysis
                try:
                    # Use OpenAI's analyze_care_home_insights method structure
                    # But we'll create a simpler direct call
                    import json
                    import httpx
                    
                    headers = {
                        "Authorization": f"Bearer {self.openai_client.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "gpt-4o-mini",  # Cost-effective model
                        "messages": [
                            {
                                "role": "system",
                                "content": """You are an expert sentiment analyst specializing in employee reviews for UK care homes.
Analyze each review and classify sentiment as: POSITIVE, MIXED, NEGATIVE, or NEUTRAL.
Focus on staff working conditions, management quality, pay, training, and work-life balance.
Return ONLY valid JSON array, no markdown, no code blocks."""
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000,
                        "response_format": {"type": "json_object"}
                    }
                    
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            f"{self.openai_client.base_url}/chat/completions",
                            headers=headers,
                            json=payload
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        analysis_text = data["choices"][0]["message"]["content"]
                        
                        # Try to parse JSON
                        try:
                            analysis_json = json.loads(analysis_text)
                        except json.JSONDecodeError:
                            # Try to extract JSON from markdown code blocks
                            import re
                            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
                            if json_match:
                                analysis_json = json.loads(json_match.group(1))
                            else:
                                # If parsing fails, skip LLM analysis for this batch
                                print(f"Warning: Could not parse LLM response as JSON: {analysis_text[:200]}")
                                analyzed_reviews.extend(batch)
                                continue
                        
                        # Extract sentiment classifications
                        sentiments = analysis_json.get('sentiments', [])
                        
                        # Update reviews with LLM-analyzed sentiment
                        for j, review in enumerate(batch):
                            if j < len(sentiments):
                                sentiment_data = sentiments[j]
                                llm_sentiment = sentiment_data.get('sentiment', review.get('sentiment', 'NEUTRAL'))
                                # Use LLM sentiment if it's more specific than keyword-based
                                if llm_sentiment in ['POSITIVE', 'MIXED', 'NEGATIVE', 'NEUTRAL']:
                                    review['sentiment'] = llm_sentiment
                                    review['llm_analyzed'] = True
                                    # Store confidence if provided
                                    if 'confidence' in sentiment_data:
                                        review['sentiment_confidence'] = sentiment_data['confidence']
                            
                            analyzed_reviews.append(review)
                
                except Exception as e:
                    print(f"Warning: LLM sentiment analysis failed for batch: {e}")
                    # Fallback: keep original sentiment
                    analyzed_reviews.extend(batch)
            
            return analyzed_reviews
            
        except Exception as e:
            print(f"Error in LLM sentiment analysis: {e}")
            return reviews  # Return original reviews if analysis fails
    
    def _build_sentiment_analysis_prompt(
        self,
        review_texts: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM sentiment analysis"""
        reviews_str = ""
        for i, review in enumerate(review_texts, 1):
            reviews_str += f"""
Review {i}:
Source: {review.get('source', 'Unknown')}
Rating: {review.get('rating', 'N/A')}/5
Text: {review.get('text', '')}
---
"""
        
        prompt = f"""Analyze the sentiment of these employee reviews for a UK care home.
Focus on staff working conditions, management quality, pay, training, and work-life balance.

{reviews_str}

For each review, classify the sentiment as:
- POSITIVE: Generally favorable about working conditions, management, pay, or support
- MIXED: Contains both positive and negative aspects
- NEGATIVE: Generally unfavorable about working conditions, management, pay, or support
- NEUTRAL: No clear sentiment or not related to staff/working conditions

Return JSON in this format:
{{
  "sentiments": [
    {{
      "review_number": 1,
      "sentiment": "POSITIVE|MIXED|NEGATIVE|NEUTRAL",
      "confidence": 0.0-1.0,
      "key_themes": ["theme1", "theme2"]
    }},
    ...
  ]
}}

IMPORTANT: Return ONLY valid JSON, no markdown, no code blocks."""
        
        return prompt
    
    def _extract_address(self, location_data: Dict[str, Any]) -> str:
        """Extract formatted address from location data"""
        parts = []
        
        postal_address = location_data.get('postalAddress', {})
        if postal_address:
            if postal_address.get('addressLine1'):
                parts.append(postal_address['addressLine1'])
            if postal_address.get('addressLine2'):
                parts.append(postal_address['addressLine2'])
            if postal_address.get('townCity'):
                parts.append(postal_address['townCity'])
            if postal_address.get('county'):
                parts.append(postal_address['county'])
        
        return ', '.join(parts) if parts else ''

