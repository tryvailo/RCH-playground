"""
Staff Enrichment Service
Integrates Glassdoor, LinkedIn, and Job Boards data for comprehensive staff analysis
"""
import logging
from typing import Dict, Any, Optional, List
from services.glassdoor_research_service import GlassdoorResearchService
from services.linkedin_research_service import LinkedInResearchService
from services.job_boards_service import JobBoardsService
from api_clients.perplexity_client import PerplexityAPIClient

logger = logging.getLogger(__name__)


class StaffEnrichmentService:
    """Service for enriching care homes with comprehensive staff data"""
    
    def __init__(
        self,
        perplexity_client: Optional[PerplexityAPIClient] = None,
        perplexity_api_key: Optional[str] = None
    ):
        """
        Initialize Staff Enrichment Service
        
        Args:
            perplexity_client: Optional Perplexity API client instance
            perplexity_api_key: Optional Perplexity API key (if client not provided)
        """
        if perplexity_client:
            self.perplexity_client = perplexity_client
        elif perplexity_api_key:
            self.perplexity_client = PerplexityAPIClient(api_key=perplexity_api_key)
        else:
            self.perplexity_client = None
        
        self.glassdoor_service = None
        self.linkedin_service = None
        self.job_boards_service = JobBoardsService()
    
    async def enrich_staff_data(
        self,
        home: Dict[str, Any],
        use_perplexity: bool = True
    ) -> Dict[str, Any]:
        """
        Enrich care home with comprehensive staff data from all sources
        
        Args:
            home: Care home dictionary
            use_perplexity: Whether to use Perplexity AI (requires API key)
        
        Returns:
            Enriched care home with staff_data field
        """
        home_name = home.get('name') or home.get('Name', '')
        company_name = home.get('company_name') or home.get('provider_name')
        location = home.get('location') or home.get('city')
        postcode = home.get('postcode') or home.get('Postcode')
        
        if not home_name:
            logger.warning("Cannot enrich staff data: home name missing")
            return home
        
        staff_data = {
            'glassdoor': {},
            'linkedin': {},
            'job_boards': {},
            'combined_analysis': {}
        }
        
        # 1. Glassdoor Research (via Perplexity AI)
        if use_perplexity and self.perplexity_client:
            try:
                if not self.glassdoor_service:
                    self.glassdoor_service = GlassdoorResearchService(self.perplexity_client)
                
                glassdoor_data = await self.glassdoor_service.research_glassdoor_data(
                    home_name=home_name,
                    company_name=company_name,
                    location=location
                )
                staff_data['glassdoor'] = glassdoor_data
                logger.info(f"Glassdoor data enriched for {home_name}")
            except Exception as e:
                logger.error(f"Error enriching Glassdoor data for {home_name}: {str(e)}")
                staff_data['glassdoor'] = {'error': str(e)}
        
        # 2. LinkedIn Research (via Perplexity AI)
        if use_perplexity and self.perplexity_client:
            try:
                if not self.linkedin_service:
                    self.linkedin_service = LinkedInResearchService(self.perplexity_client)
                
                linkedin_data = await self.linkedin_service.research_linkedin_data(
                    home_name=home_name,
                    company_name=company_name,
                    location=location
                )
                staff_data['linkedin'] = linkedin_data
                logger.info(f"LinkedIn data enriched for {home_name}")
            except Exception as e:
                logger.error(f"Error enriching LinkedIn data for {home_name}: {str(e)}")
                staff_data['linkedin'] = {'error': str(e)}
        
        # 3. Job Boards Analysis
        try:
            job_boards_data = await self.job_boards_service.analyze_job_listings(
                home_name=home_name,
                company_name=company_name,
                location=location,
                postcode=postcode
            )
            staff_data['job_boards'] = job_boards_data
            logger.info(f"Job boards data enriched for {home_name}")
        except Exception as e:
            logger.error(f"Error enriching job boards data for {home_name}: {str(e)}")
            staff_data['job_boards'] = {'error': str(e)}
        
        # 4. Combined Analysis
        staff_data['combined_analysis'] = self._combine_staff_analysis(staff_data)
        
        # Add staff_data to home
        home['staff_data'] = staff_data
        home['staffQuality'] = self._extract_staff_quality_metrics(staff_data)
        
        return home
    
    def _combine_staff_analysis(self, staff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine data from all sources into unified analysis"""
        glassdoor = staff_data.get('glassdoor', {})
        linkedin = staff_data.get('linkedin', {})
        job_boards = staff_data.get('job_boards', {})
        
        combined = {
            'employee_satisfaction_rating': glassdoor.get('rating'),
            'review_count': glassdoor.get('review_count'),
            'management_score': glassdoor.get('management_score'),
            'work_life_balance_score': glassdoor.get('work_life_balance_score'),
            'staff_count': linkedin.get('staff_count'),
            'average_tenure_years': linkedin.get('average_tenure_years'),
            'turnover_rate_percent': self._estimate_turnover_rate(glassdoor, linkedin, job_boards),
            'certifications': linkedin.get('certifications', []),
            'department_breakdown': linkedin.get('department_breakdown', {}),
            'hiring_frequency': job_boards.get('hiring_frequency'),
            'active_job_listings': job_boards.get('active_listings_count', 0),
            'turnover_signals': job_boards.get('turnover_signals', []),
            'data_quality': self._assess_combined_data_quality(glassdoor, linkedin, job_boards)
        }
        
        return combined
    
    def _estimate_turnover_rate(
        self,
        glassdoor: Dict[str, Any],
        linkedin: Dict[str, Any],
        job_boards: Dict[str, Any]
    ) -> Optional[float]:
        """Estimate turnover rate from available data"""
        # Priority: LinkedIn estimate > Job boards signals > Glassdoor mentions
        
        # 1. LinkedIn turnover estimate
        if linkedin.get('turnover_rate_estimate') is not None:
            return linkedin.get('turnover_rate_estimate')
        
        # 2. Job boards analysis
        active_listings = job_boards.get('active_listings_count', 0)
        staff_count = linkedin.get('staff_count')
        
        # Ensure values are numbers
        if active_listings is not None:
            try:
                active_listings = float(active_listings)
            except (ValueError, TypeError):
                active_listings = 0
        else:
            active_listings = 0
        
        if staff_count is not None:
            try:
                staff_count = float(staff_count)
            except (ValueError, TypeError):
                staff_count = 0
        else:
            staff_count = 0
        
        if active_listings > 0 and staff_count > 0:
            # Estimate: if 5+ listings for a 50-person home, that's ~10% turnover signal
            estimated_rate = (active_listings / staff_count) * 20  # Rough multiplier
            return round(min(estimated_rate, 100), 1)
        
        # 3. Glassdoor turnover mentions
        if glassdoor.get('turnover_mentions'):
            # If turnover is mentioned, estimate moderate-high turnover
            return 30.0  # Default estimate
        
        return None
    
    def _assess_combined_data_quality(
        self,
        glassdoor: Dict[str, Any],
        linkedin: Dict[str, Any],
        job_boards: Dict[str, Any]
    ) -> str:
        """Assess overall data quality from all sources"""
        glassdoor_quality = glassdoor.get('data_quality', 'very_low')
        linkedin_quality = linkedin.get('data_quality', 'very_low')
        job_boards_count_raw = job_boards.get('total_listings', 0)
        
        # Ensure job_boards_count is a number
        if job_boards_count_raw is not None:
            try:
                job_boards_count = float(job_boards_count_raw)
            except (ValueError, TypeError):
                job_boards_count = 0
        else:
            job_boards_count = 0
        
        quality_scores = {
            'high': 3,
            'medium': 2,
            'low': 1,
            'very_low': 0
        }
        
        glassdoor_score = quality_scores.get(glassdoor_quality, 0)
        linkedin_score = quality_scores.get(linkedin_quality, 0)
        job_boards_score = 1 if job_boards_count > 0 else 0
        
        total_score = glassdoor_score + linkedin_score + job_boards_score
        
        if total_score >= 5:
            return 'high'
        elif total_score >= 3:
            return 'medium'
        elif total_score >= 1:
            return 'low'
        else:
            return 'very_low'
    
    def _extract_staff_quality_metrics(self, staff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract staff quality metrics for scoring"""
        combined = staff_data.get('combined_analysis', {})
        
        return {
            'glassdoor_rating': combined.get('employee_satisfaction_rating'),
            'average_tenure_years': combined.get('average_tenure_years'),
            'turnover_rate_percent': combined.get('turnover_rate_percent'),
            'management_score': combined.get('management_score'),
            'work_life_balance_score': combined.get('work_life_balance_score'),
            'staff_count': combined.get('staff_count'),
            'recent_job_listings_count': combined.get('active_job_listings', 0),
            'data_quality': combined.get('data_quality', 'very_low')
        }
    
    async def close(self):
        """Close all service connections"""
        if self.job_boards_service:
            await self.job_boards_service.close()
        if self.perplexity_client:
            await self.perplexity_client.close()

