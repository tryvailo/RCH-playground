"""
Report Enricher

Orchestrates enrichment of care homes for professional reports.
Wrapper around EnrichmentOrchestrator.

Extracted from report_routes.py lines 700-850
"""

import logging
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)


class ReportEnricher:
    """Orchestrate enrichment for professional reports"""
    
    def __init__(self):
        """Initialize enricher"""
        from services.enrichment_orchestrator import EnrichmentOrchestrator
        self.orchestrator = EnrichmentOrchestrator()
    
    async def enrich_homes(
        self,
        homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any],
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enrich all homes in batch.
        
        Args:
            homes: List of care homes
            questionnaire: User questionnaire (for context)
            progress_callback: Optional progress callback
        
        Returns:
            List of enriched homes with metadata
        """
        from services.enrichment_orchestrator import EnrichmentConfig
        
        logger.info(f"Starting enrichment of {len(homes)} homes...")
        
        config = EnrichmentConfig(
            enabled_sources=['financial', 'staff', 'fsa', 'google'],
            parallel_limit=5,
            timeout_per_source=30,
            cache_results=True
        )
        
        context = {
            'questionnaire': questionnaire,
            'use_perplexity': True
        }
        
        enriched_homes = await self.orchestrator.enrich_homes_batch(
            homes, config, context, progress_callback
        )
        
        logger.info(f"✅ Enrichment complete for {len(enriched_homes)} homes")
        
        return enriched_homes
