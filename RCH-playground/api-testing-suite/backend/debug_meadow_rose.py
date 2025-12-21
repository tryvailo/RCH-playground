#!/usr/bin/env python3
"""
Детальный анализ дома Meadow Rose Nursing Home с первой анкетой
Рассчитывает все скоринги и получает данные от всех источников
"""
import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.professional_matching_service import ProfessionalMatchingService, ScoringWeights
from services.csv_care_homes_service import get_care_homes
from services.cqc_deep_dive_service import CQCDeepDiveService
from services.companies_house_service import CompaniesHouseService
from services.google_places_enrichment_service import GooglePlacesEnrichmentService
from services.fsa_enrichment_service import FSAEnrichmentService
from services.staff_quality_service import StaffQualityService
from api_clients.cqc_client import CQCAPIClient
from utils.auth import get_credentials

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'─'*80}")
    print(f"  {title}")
    print(f"{'─'*80}")

def print_dict(data: Dict[str, Any], indent: int = 2, max_depth: int = 3, current_depth: int = 0):
    """Recursively print dictionary with depth limit"""
    if current_depth >= max_depth:
        print(" " * indent + "... (max depth reached)")
        return
    
    for key, value in data.items():
        if isinstance(value, dict):
            print(" " * indent + f"{key}:")
            print_dict(value, indent + 2, max_depth, current_depth + 1)
        elif isinstance(value, list):
            print(" " * indent + f"{key}: [{len(value)} items]")
            if len(value) > 0 and isinstance(value[0], dict):
                print(" " * (indent + 2) + f"First item keys: {list(value[0].keys())[:5]}")
        else:
            print(" " * indent + f"{key}: {value}")

async def analyze_meadow_rose():
    """Полный анализ дома Meadow Rose Nursing Home"""
    
    print_section("ДЕТАЛЬНЫЙ АНАЛИЗ: MEADOW ROSE NURSING HOME")
    
    # 1. Load questionnaire
    print_subsection("1. ЗАГРУЗКА АНКЕТЫ")
    questionnaire_path = "RCH-playground/RCH-playground/api-testing-suite/frontend/public/sample_questionnaires/professional_questionnaire_1_dementia.json"
    with open(questionnaire_path, 'r') as f:
        questionnaire = json.load(f)
    
    print(f"   ✅ Анкета загружена: {questionnaire_path}")
    print(f"   Клиент: {questionnaire.get('profile_description', 'Unknown')}")
    
    # Extract priorities
    priorities = questionnaire.get('section_6_priorities', {}).get('q18_priority_ranking', {})
    if priorities:
        print(f"   Приоритеты: {priorities.get('priority_order', [])}")
        print(f"   Веса: {priorities.get('priority_weights', [])}")
    
    # 2. Load care homes and find Meadow Rose
    print_subsection("2. ПОИСК ДОМА MEADOW ROSE NURSING HOME")
    all_homes = get_care_homes()
    
    meadow_rose = None
    for home in all_homes:
        name = str(home.get('name', '')).lower()
        if 'meadow' in name and 'rose' in name:
            meadow_rose = home
            break
    
    if not meadow_rose:
        print("   ❌ Дом Meadow Rose Nursing Home не найден!")
        return
    
    print(f"   ✅ Дом найден: {meadow_rose.get('name', 'Unknown')}")
    print(f"   ID: {meadow_rose.get('id', 'Unknown')}")
    print(f"   CQC Location ID: {meadow_rose.get('cqc_location_id', 'Unknown')}")
    print(f"   Адрес: {meadow_rose.get('address', 'Unknown')}")
    print(f"   Посткод: {meadow_rose.get('postcode', 'Unknown')}")
    
    # 3. Calculate dynamic weights
    print_subsection("3. РАСЧЕТ ДИНАМИЧЕСКИХ ВЕСОВ")
    matching_service = ProfessionalMatchingService()
    weights, applied_conditions = matching_service.calculate_dynamic_weights(questionnaire)
    
    print(f"   Примененные условия: {applied_conditions}")
    print(f"   Веса:")
    weights_dict = weights.to_dict()
    for category, weight in weights_dict.items():
        print(f"      {category:15s}: {weight:6.2f}%")
    
    # Apply user priorities
    if priorities:
        priority_order = priorities.get('priority_order', [])
        priority_weights = priorities.get('priority_weights', [])
        if priority_order and priority_weights:
            user_priorities = {
                'priority_order': priority_order,
                'priority_weights': priority_weights
            }
            adjusted_weights = matching_service.apply_user_priorities(weights, user_priorities)
            print(f"\n   Веса после применения приоритетов пользователя:")
            adjusted_weights_dict = adjusted_weights.to_dict()
            for category, weight in adjusted_weights_dict.items():
                print(f"      {category:15s}: {weight:6.2f}%")
            weights = adjusted_weights
    
    # 4. Get enriched data from all sources
    print_subsection("4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ВСЕХ ИСТОЧНИКОВ")
    
    enriched_data = {}
    
    # 4.1 CQC Data
    print("\n   4.1 CQC Deep Dive")
    location_id = meadow_rose.get('cqc_location_id') or meadow_rose.get('location_id')
    provider_id = meadow_rose.get('provider_id') or meadow_rose.get('providerId')
    
    if location_id:
        try:
            creds = get_credentials()
            cqc_client = None
            if creds.cqc and creds.cqc.primary_subscription_key:
                cqc_client = CQCAPIClient(
                    primary_subscription_key=creds.cqc.primary_subscription_key,
                    secondary_subscription_key=creds.cqc.secondary_subscription_key
                )
            else:
                cqc_client = CQCAPIClient()
            
            cqc_service = CQCDeepDiveService(cqc_client=cqc_client)
            cqc_deep_dive = await cqc_service.build_cqc_deep_dive(
                db_data=meadow_rose,
                location_id=location_id,
                provider_id=provider_id
            )
            cqc_dict = cqc_service.to_dict(cqc_deep_dive)
            enriched_data['cqc_detailed'] = cqc_dict
            print(f"      ✅ CQC данные получены")
            print(f"         Overall Rating: {cqc_dict.get('overall_rating', 'N/A')}")
            print(f"         Detailed Ratings: {len(cqc_dict.get('detailed_ratings', {}))} категорий")
            print(f"         Historical Ratings: {len(cqc_dict.get('historical_ratings', []))} записей")
            print(f"         Enforcement Actions: {len(cqc_dict.get('enforcement_actions', []))} записей")
            await cqc_service.close()
        except Exception as e:
            print(f"      ⚠️ Ошибка получения CQC данных: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"      ⚠️ CQC Location ID не найден")
    
    # 4.2 Companies House (Financial Stability)
    print("\n   4.2 Companies House (Financial Stability)")
    home_name = meadow_rose.get('name', '')
    if home_name:
        try:
            companies_house_service = CompaniesHouseService()
            financial_data = await companies_house_service.get_financial_stability(home_name)
            if financial_data:
                enriched_data['companies_house_scoring'] = financial_data
                print(f"      ✅ Financial данные получены")
                print(f"         Financial Stability Score: {financial_data.get('financial_stability_score', 'N/A')}")
                print(f"         Keys: {list(financial_data.keys())[:10]}")
            else:
                print(f"      ⚠️ Financial данные не найдены")
        except Exception as e:
            print(f"      ⚠️ Ошибка получения Financial данных: {e}")
            import traceback
            traceback.print_exc()
    
    # 4.3 Google Places
    print("\n   4.3 Google Places")
    if home_name:
        try:
            google_service = GooglePlacesEnrichmentService()
            google_data = await google_service.enrich_care_home(
                name=home_name,
                address=meadow_rose.get('address', ''),
                postcode=meadow_rose.get('postcode', '')
            )
            if google_data:
                enriched_data['google_places'] = google_data
                print(f"      ✅ Google Places данные получены")
                print(f"         Rating: {google_data.get('rating', 'N/A')}")
                print(f"         Review Count: {google_data.get('user_ratings_total', 'N/A')}")
                print(f"         Keys: {list(google_data.keys())[:10]}")
            else:
                print(f"      ⚠️ Google Places данные не найдены")
        except Exception as e:
            print(f"      ⚠️ Ошибка получения Google Places данных: {e}")
            import traceback
            traceback.print_exc()
    
    # 4.4 FSA (Food Hygiene)
    print("\n   4.4 FSA (Food Hygiene)")
    if home_name:
        try:
            fsa_service = FSAEnrichmentService()
            fsa_data = await fsa_service.get_food_hygiene_rating(
                business_name=home_name,
                postcode=meadow_rose.get('postcode', ''),
                latitude=meadow_rose.get('latitude'),
                longitude=meadow_rose.get('longitude')
            )
            if fsa_data:
                enriched_data['fsa_scoring'] = fsa_data
                print(f"      ✅ FSA данные получены")
                print(f"         Rating: {fsa_data.get('rating_value', 'N/A')}")
                print(f"         Health Score: {fsa_data.get('health_score', 'N/A')}")
            else:
                print(f"      ⚠️ FSA данные не найдены")
        except Exception as e:
            print(f"      ⚠️ Ошибка получения FSA данных: {e}")
            import traceback
            traceback.print_exc()
    
    # 4.5 Staff Quality
    print("\n   4.5 Staff Quality")
    if location_id:
        try:
            staff_service = StaffQualityService()
            staff_data = await staff_service.analyze_by_location_id(location_id)
            if staff_data:
                enriched_data['staff_quality'] = staff_data
                print(f"      ✅ Staff Quality данные получены")
                print(f"         Staff Quality Score: {staff_data.get('staff_quality_score', 'N/A')}")
                print(f"         Keys: {list(staff_data.keys())[:10]}")
            else:
                print(f"      ⚠️ Staff Quality данные не найдены")
        except Exception as e:
            print(f"      ⚠️ Ошибка получения Staff Quality данных: {e}")
            import traceback
            traceback.print_exc()
    
    # 5. Calculate 156-point match
    print_subsection("5. РАСЧЕТ 156-POINT MATCH")
    
    match_result = matching_service.calculate_156_point_match(
        home=meadow_rose,
        user_profile=questionnaire,
        enriched_data=enriched_data,
        weights=weights
    )
    
    print(f"   Общий скор: {match_result.get('total', 0):.2f} / 156")
    print(f"   Нормализованный скор: {match_result.get('normalized', 0):.2f}%")
    
    print(f"\n   Category Scores (0-1 scale):")
    category_scores = match_result.get('category_scores', {})
    for category, score in category_scores.items():
        print(f"      {category:15s}: {score:.4f}")
    
    print(f"\n   Point Allocations:")
    point_allocations = match_result.get('point_allocations', {})
    for category, points in point_allocations.items():
        print(f"      {category:15s}: {points:6.2f} points")
    
    print(f"\n   Weights:")
    weights_result = match_result.get('weights', {})
    for category, weight in weights_result.items():
        print(f"      {category:15s}: {weight:6.2f}%")
    
    # 6. Detailed breakdown
    print_subsection("6. ДЕТАЛЬНЫЙ РАЗБОР КАТЕГОРИЙ")
    
    # 6.1 Medical Capabilities
    print("\n   6.1 Medical Capabilities")
    medical_score = matching_service._calculate_medical_capabilities(
        meadow_rose, questionnaire, enriched_data
    )
    print(f"      Score: {medical_score:.4f} (0-1 scale)")
    
    # 6.2 Safety Quality
    print("\n   6.2 Safety Quality")
    safety_score = matching_service._calculate_safety_quality(
        meadow_rose, questionnaire, enriched_data
    )
    print(f"      Score: {safety_score:.4f} (0-1 scale)")
    
    # 6.3 Location Access
    print("\n   6.3 Location Access")
    location_score = matching_service._calculate_location_access(
        meadow_rose, questionnaire
    )
    print(f"      Score: {location_score:.4f} (0-1 scale)")
    
    # 6.4 Cultural Social
    print("\n   6.4 Cultural & Social")
    social_score = matching_service._calculate_cultural_social(
        meadow_rose, questionnaire, enriched_data
    )
    print(f"      Score: {social_score:.4f} (0-1 scale)")
    
    # 6.5 Financial Stability
    print("\n   6.5 Financial Stability")
    financial_score = matching_service._calculate_financial_stability(
        meadow_rose, enriched_data
    )
    print(f"      Score: {financial_score:.4f} (0-1 scale)")
    
    # 6.6 Staff Quality
    print("\n   6.6 Staff Quality")
    staff_score = matching_service._calculate_staff_quality(
        meadow_rose, enriched_data
    )
    print(f"      Score: {staff_score:.4f} (0-1 scale)")
    
    # 6.7 CQC Compliance
    print("\n   6.7 CQC Compliance")
    cqc_score = matching_service._calculate_cqc_compliance(
        meadow_rose, enriched_data
    )
    print(f"      Score: {cqc_score:.4f} (0-1 scale)")
    
    # 6.8 Additional Services
    print("\n   6.8 Additional Services")
    services_score = matching_service._calculate_additional_services(
        meadow_rose, questionnaire
    )
    print(f"      Score: {services_score:.4f} (0-1 scale)")
    
    # 7. Full data dump
    print_subsection("7. ПОЛНЫЙ ДАМП ДАННЫХ")
    
    print("\n   7.1 Home Data (first 30 keys):")
    home_keys = list(meadow_rose.keys())[:30]
    for key in home_keys:
        value = meadow_rose.get(key)
        if isinstance(value, (dict, list)):
            print(f"      {key:30s}: {type(value).__name__} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")
        else:
            print(f"      {key:30s}: {value}")
    
    print("\n   7.2 Enriched Data Summary:")
    for source, data in enriched_data.items():
        if isinstance(data, dict):
            print(f"      {source:30s}: {len(data)} keys")
        else:
            print(f"      {source:30s}: {type(data).__name__}")
    
    print("\n   7.3 Match Result Summary:")
    print(f"      Total Score: {match_result.get('total', 0):.2f}")
    print(f"      Normalized: {match_result.get('normalized', 0):.2f}%")
    print(f"      Category Scores: {len(category_scores)} categories")
    print(f"      Point Allocations: {len(point_allocations)} categories")
    
    print_section("АНАЛИЗ ЗАВЕРШЕН")
    
    # Return summary
    return {
        'home': meadow_rose,
        'questionnaire': questionnaire,
        'weights': weights_dict,
        'enriched_data': enriched_data,
        'match_result': match_result
    }

if __name__ == "__main__":
    result = asyncio.run(analyze_meadow_rose())

