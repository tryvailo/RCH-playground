"""
Report Generation Services

Five-layer architecture for professional report generation:
1. DataLoader - Load and resolve location, calculate distances
2. Validator - Validate questionnaire and homes
3. Enricher - Orchestrate data enrichment (financial, staff, fsa, google)
4. Matcher - Match and score homes using 156-point algorithm
5. Assembler - Select top 5, generate reasoning, assemble final report

Usage:
    loader = ReportDataLoader()
    validator = ReportValidator()
    enricher = ReportEnricher()
    matcher = ReportMatcher()
    assembler = ReportAssembler()
    
    # Pipeline
    user_lat, user_lon = await loader.resolve_user_location(questionnaire)
    homes = await loader.load_homes(questionnaire, city, care_type, distance, user_lat, user_lon)
    homes = await loader.calculate_distances(homes, user_lat, user_lon)
    
    validator.validate_questionnaire(questionnaire)
    validation = validator.validate_homes(homes)
    homes = validation['valid_homes']
    
    enriched = await enricher.enrich_homes(homes, questionnaire)
    scored = await matcher.match_homes(homes, questionnaire, enriched)
    report = await assembler.assemble_report(scored, questionnaire, enriched_map)
"""

from services.report_generation.data_loader import ReportDataLoader
from services.report_generation.validator import ReportValidator, ValidationError
from services.report_generation.enricher import ReportEnricher
from services.report_generation.matcher import ReportMatcher
from services.report_generation.assembler import ReportAssembler

__all__ = [
    'ReportDataLoader',
    'ReportValidator',
    'ValidationError',
    'ReportEnricher',
    'ReportMatcher',
    'ReportAssembler'
]
