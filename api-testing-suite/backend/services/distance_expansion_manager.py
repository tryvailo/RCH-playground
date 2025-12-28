"""
Distance Expansion Manager for Enhanced MVP Matching Service
Implements progressive radius expansion when insufficient results found
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExpansionPhase:
    """Configuration for each expansion phase"""
    phase_num: int
    radius_km: float
    min_results_needed: int
    name: str
    description: str


@dataclass
class ExpansionResult:
    """Result of distance expansion search"""
    matched_homes: List[Dict[str, Any]]
    expansion_phase: int
    expansion_message: str
    total_homes_evaluated: int
    homes_at_preferred_distance: int
    search_expanded: bool


class DistanceExpansionManager:
    """
    Manages progressive distance expansion for home matching.
    
    When initial search returns insufficient results, systematically
    expands the search radius while maintaining match quality.
    """
    
    # Expansion phases: radius_km, min_results_needed
    EXPANSION_PHASES = [
        ExpansionPhase(
            phase_num=0,
            radius_km=5,
            min_results_needed=5,
            name='preferred',
            description='Within preferred radius'
        ),
        ExpansionPhase(
            phase_num=1,
            radius_km=10,
            min_results_needed=3,
            name='nearby',
            description='Nearby area (expanded search)'
        ),
        ExpansionPhase(
            phase_num=2,
            radius_km=15,
            min_results_needed=3,
            name='regional',
            description='Regional area (wider search)'
        ),
        ExpansionPhase(
            phase_num=3,
            radius_km=25,
            min_results_needed=2,
            name='expanded',
            description='Expanded region (much wider)'
        ),
        ExpansionPhase(
            phase_num=4,
            radius_km=50,
            min_results_needed=1,
            name='very_wide',
            description='Very wide area'
        ),
        ExpansionPhase(
            phase_num=5,
            radius_km=float('inf'),
            min_results_needed=1,
            name='nationwide',
            description='Nationwide search'
        ),
    ]
    
    def __init__(self):
        """Initialize expansion manager"""
        logger.info("Initializing DistanceExpansionManager")
    
    def expand_search(
        self,
        homes: List[Dict[str, Any]],
        matching_service,
        questionnaire: Dict[str, Any],
        preferred_radius_km: float = 5.0,
        top_n: int = 5,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None
    ) -> ExpansionResult:
        """
        Progressively expand distance search until sufficient results found.
        
        Args:
            homes: All available homes with distance_km field
            matching_service: Service with match_homes() method
            questionnaire: User questionnaire data
            preferred_radius_km: Initial preferred search radius
            top_n: Number of results to return
            user_lat: User latitude (optional, for additional distance calc)
            user_lon: User longitude (optional, for additional distance calc)
        
        Returns:
            ExpansionResult with matched homes and expansion metadata
        """
        
        logger.info(f"Starting distance expansion search. Preferred radius: {preferred_radius_km}km")
        
        # Count homes at preferred distance
        homes_at_preferred = [
            h for h in homes 
            if h.get('distance_km', float('inf')) <= preferred_radius_km
        ]
        homes_at_preferred_count = len(homes_at_preferred)
        logger.info(f"Homes at preferred distance ({preferred_radius_km}km): {homes_at_preferred_count}")
        
        # Try each expansion phase
        for phase in self.EXPANSION_PHASES:
            logger.info(f"Expansion Phase {phase.phase_num}: {phase.name} "
                       f"({phase.radius_km}km, min {phase.min_results_needed} results)")
            
            # Filter homes by radius
            if phase.radius_km == float('inf'):
                homes_in_phase = homes
            else:
                homes_in_phase = [
                    h for h in homes 
                    if h.get('distance_km', float('inf')) <= phase.radius_km
                ]
            
            logger.debug(f"Homes in phase {phase.phase_num}: {len(homes_in_phase)}")
            
            # Skip if no homes in this radius
            if not homes_in_phase:
                logger.debug(f"No homes in radius {phase.radius_km}km, continuing...")
                continue
            
            # Match homes in this radius
            try:
                matching_results = matching_service.match_homes(
                    homes=homes_in_phase,
                    questionnaire=questionnaire,
                    top_n=min(top_n, len(homes_in_phase))
                )
                
                num_results = len(matching_results)
                logger.info(f"Got {num_results} results at phase {phase.phase_num}")
                
                # Check if we have enough results
                if num_results >= phase.min_results_needed:
                    return self._create_result(
                        matched_homes=matching_results,
                        expansion_phase=phase.phase_num,
                        expansion_name=phase.name,
                        preferred_radius=preferred_radius_km,
                        actual_radius=phase.radius_km,
                        total_homes_evaluated=len(homes),
                        homes_at_preferred=homes_at_preferred_count,
                        search_expanded=(phase.phase_num > 0)
                    )
                
            except Exception as e:
                logger.warning(f"Error matching homes in phase {phase.phase_num}: {e}")
                continue
        
        # Fallback: return all matches from nationwide search
        logger.warning("No sufficient results even at nationwide level")
        try:
            matching_results = matching_service.match_homes(
                homes=homes,
                questionnaire=questionnaire,
                top_n=top_n
            )
            
            return self._create_result(
                matched_homes=matching_results,
                expansion_phase=6,
                expansion_name='nationwide_fallback',
                preferred_radius=preferred_radius_km,
                actual_radius=float('inf'),
                total_homes_evaluated=len(homes),
                homes_at_preferred=homes_at_preferred_count,
                search_expanded=True,
                is_fallback=True
            )
        except Exception as e:
            logger.error(f"Fallback matching failed: {e}")
            return ExpansionResult(
                matched_homes=[],
                expansion_phase=-1,
                expansion_message=f"Error during search expansion: {str(e)}",
                total_homes_evaluated=len(homes),
                homes_at_preferred_distance=homes_at_preferred_count,
                search_expanded=False
            )
    
    def _create_result(
        self,
        matched_homes,
        expansion_phase: int,
        expansion_name: str,
        preferred_radius: float,
        actual_radius: float,
        total_homes_evaluated: int,
        homes_at_preferred: int,
        search_expanded: bool,
        is_fallback: bool = False
    ) -> ExpansionResult:
        """Create ExpansionResult object with appropriate message"""
        
        # Generate message based on phase
        if expansion_phase == 0:
            message = f"Found {len(matched_homes)} homes within preferred {preferred_radius}km radius"
        elif is_fallback:
            message = f"Limited availability. Showing from nationwide search (all available homes)"
        else:
            distance_diff = actual_radius - preferred_radius
            message = (
                f"Search expanded to {actual_radius}km radius "
                f"({distance_diff:.0f}km beyond preferred). "
                f"Found {len(matched_homes)} matching homes."
            )
        
        logger.info(f"Expansion result: {message}")
        
        return ExpansionResult(
            matched_homes=matched_homes,
            expansion_phase=expansion_phase,
            expansion_message=message,
            total_homes_evaluated=total_homes_evaluated,
            homes_at_preferred_distance=homes_at_preferred,
            search_expanded=search_expanded
        )
    
    def get_expansion_phase_info(self, phase_num: int) -> Optional[ExpansionPhase]:
        """Get information about a specific expansion phase"""
        for phase in self.EXPANSION_PHASES:
            if phase.phase_num == phase_num:
                return phase
        return None
    
    def should_expand_search(
        self,
        current_results: int,
        required_results: int,
        current_phase: int
    ) -> bool:
        """
        Determine if search should expand to next phase.
        
        Args:
            current_results: Number of results found
            required_results: Minimum required results
            current_phase: Current expansion phase
        
        Returns:
            True if should expand
        """
        should_expand = (
            current_results < required_results and
            current_phase < len(self.EXPANSION_PHASES) - 1
        )
        
        logger.debug(
            f"Should expand search? {should_expand} "
            f"(have {current_results}, need {required_results}, phase {current_phase})"
        )
        
        return should_expand


# ==================== INTEGRATION HELPER ====================

def integrate_expansion_into_report_generation(
    care_homes: List[Dict],
    matching_service,
    questionnaire: Dict,
    max_distance_km: Optional[float] = None,
    top_n: int = 5
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Helper function to integrate distance expansion into report generation.
    
    Args:
        care_homes: Initial list of care homes
        matching_service: Enhanced MVP matching service
        questionnaire: User questionnaire
        max_distance_km: Max distance preference (5, 15, 30, or None)
        top_n: Number of results to return
    
    Returns:
        (matched_homes, metadata)
    
    Example usage:
        matched_homes, metadata = integrate_expansion_into_report_generation(
            care_homes=care_homes,
            matching_service=matching_service,
            questionnaire=questionnaire,
            max_distance_km=15.0,
            top_n=5
        )
        
        if not matched_homes:
            return {'error': metadata['message']}
        
        # Format response with metadata
        response = {
            'topMatches': format_homes(matched_homes),
            'searchMetadata': metadata
        }
    """
    
    expansion_manager = DistanceExpansionManager()
    
    # Determine initial search radius
    if max_distance_km is None:
        initial_radius = 15.0  # Default
    else:
        initial_radius = min(max_distance_km, 5.0)  # Start from preferred
    
    # Run expansion search
    result = expansion_manager.expand_search(
        homes=care_homes,
        matching_service=matching_service,
        questionnaire=questionnaire,
        preferred_radius_km=initial_radius,
        top_n=top_n
    )
    
    # Extract homes from MatchingResult objects
    matched_homes_data = []
    for match_result in result.matched_homes:
        home_dict = (
            match_result.home if isinstance(match_result.home, dict)
            else match_result.home.__dict__
        )
        home_dict['matchScore'] = match_result.score.total_score
        home_dict['factorScores'] = {
            'medical': match_result.score.medical_score,
            'safety': match_result.score.safety_score,
            'location': match_result.score.location_score,
        }
        matched_homes_data.append(home_dict)
    
    # Create metadata
    metadata = {
        'total_homes_considered': result.total_homes_evaluated,
        'homes_matched': len(matched_homes_data),
        'homes_at_preferred_distance': result.homes_at_preferred_distance,
        'expansion_phase': result.expansion_phase,
        'expansion_message': result.expansion_message,
        'search_expanded': result.search_expanded,
        'notes': [
            "Homes scored on: medical fit (30%), safety (40%), location (25%), bonus (5%)",
            "Hard constraints enforced for patient safety",
        ] if not result.search_expanded else [
            f"Initial search returned limited results.",
            f"Automatically expanded to: {result.expansion_message}",
            "Results ranked by match score. Closer homes scored higher.",
        ]
    }
    
    return matched_homes_data, metadata
