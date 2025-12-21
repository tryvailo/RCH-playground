#!/usr/bin/env python3
"""
Прямой анализ дома Meadow Rose Nursing Home
Использует функции напрямую без FastAPI
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import functions directly
from services.csv_care_homes_service import get_care_homes
from services.professional_matching_service import ProfessionalMatchingService

def analyze_meadow_rose():
    """Анализ дома Meadow Rose"""
    
    print("="*80)
    print("ДЕТАЛЬНЫЙ АНАЛИЗ: MEADOW ROSE NURSING HOME")
    print("="*80)
    
    # 1. Load questionnaire
    print("\n1. ЗАГРУЗКА АНКЕТЫ")
    questionnaire_path = "RCH-playground/RCH-playground/api-testing-suite/frontend/public/sample_questionnaires/professional_questionnaire_1_dementia.json"
    with open(questionnaire_path, 'r') as f:
        questionnaire = json.load(f)
    
    print(f"   ✅ Анкета загружена")
    print(f"   Клиент: {questionnaire.get('profile_description', 'Unknown')}")
    
    # 2. Load care homes
    print("\n2. ЗАГРУЗКА ДОМОВ ИЗ CSV")
    all_homes = get_care_homes()
    print(f"   ✅ Загружено {len(all_homes)} домов")
    
    # 3. Find Meadow Rose
    print("\n3. ПОИСК MEADOW ROSE NURSING HOME")
    meadow_rose = None
    for home in all_homes:
        name = str(home.get('name', '')).lower()
        if 'meadow' in name and 'rose' in name:
            meadow_rose = home
            break
    
    if not meadow_rose:
        print("   ❌ Дом Meadow Rose Nursing Home не найден!")
        print("   Доступные дома с 'meadow' или 'rose' в названии:")
        for home in all_homes[:20]:
            name = str(home.get('name', '')).lower()
            if 'meadow' in name or 'rose' in name:
                print(f"      - {home.get('name', 'Unknown')}")
        return
    
    print(f"   ✅ Дом найден: {meadow_rose.get('name', 'Unknown')}")
    print(f"   ID: {meadow_rose.get('id', 'Unknown')}")
    print(f"   CQC Location ID: {meadow_rose.get('cqc_location_id', 'Unknown')}")
    print(f"   Адрес: {meadow_rose.get('address', 'Unknown')}")
    print(f"   Посткод: {meadow_rose.get('postcode', 'Unknown')}")
    
    # 4. Calculate weights
    print("\n4. РАСЧЕТ ДИНАМИЧЕСКИХ ВЕСОВ")
    matching_service = ProfessionalMatchingService()
    weights, applied_conditions = matching_service.calculate_dynamic_weights(questionnaire)
    
    print(f"   Примененные условия: {applied_conditions}")
    print(f"   Веса:")
    weights_dict = weights.to_dict()
    for category, weight in weights_dict.items():
        print(f"      {category:15s}: {weight:6.2f}%")
    
    # Apply user priorities
    priorities = questionnaire.get('section_6_priorities', {}).get('q18_priority_ranking', {})
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
    
    # 5. Calculate match with empty enriched_data (basic calculation)
    print("\n5. РАСЧЕТ 156-POINT MATCH (без API данных)")
    enriched_data = {}  # Start with empty, will show what's missing
    
    match_result = matching_service.calculate_156_point_match(
        home=meadow_rose,
        user_profile=questionnaire,
        enriched_data=enriched_data,
        weights=weights
    )
    
    print(f"\n   Общий скор: {match_result.get('total', 0):.2f} / 156")
    print(f"   Нормализованный скор: {match_result.get('normalized', 0):.2f}%")
    
    print(f"\n   Category Scores (0-1 scale):")
    category_scores = match_result.get('category_scores', {})
    for category, score in category_scores.items():
        print(f"      {category:15s}: {score:.4f}")
    
    print(f"\n   Point Allocations:")
    point_allocations = match_result.get('point_allocations', {})
    for category, points in point_allocations.items():
        print(f"      {category:15s}: {points:6.2f} points")
    
    # 6. Detailed category breakdown
    print("\n6. ДЕТАЛЬНЫЙ РАЗБОР КАТЕГОРИЙ")
    
    categories = [
        ('Medical Capabilities', '_calculate_medical_capabilities'),
        ('Safety Quality', '_calculate_safety_quality'),
        ('Location Access', '_calculate_location_access'),
        ('Cultural Social', '_calculate_cultural_social'),
        ('Financial Stability', '_calculate_financial_stability'),
        ('Staff Quality', '_calculate_staff_quality'),
        ('CQC Compliance', '_calculate_cqc_compliance'),
        ('Additional Services', '_calculate_additional_services'),
    ]
    
    for category_name, method_name in categories:
        method = getattr(matching_service, method_name, None)
        if method:
            try:
                # Check method signature
                import inspect
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                if len(params) == 2:  # (home, user_profile) or (home, enriched_data)
                    if 'user_profile' in params:
                        score = method(meadow_rose, questionnaire)
                    else:
                        score = method(meadow_rose, enriched_data)
                elif len(params) == 3:  # (home, user_profile, enriched_data) or (home, enriched_data, ...)
                    if 'user_profile' in params:
                        score = method(meadow_rose, questionnaire, enriched_data)
                    else:
                        score = method(meadow_rose, enriched_data)
                else:
                    score = method(meadow_rose, questionnaire, enriched_data)
                
                print(f"   {category_name:25s}: {score:.4f} (0-1 scale)")
            except Exception as e:
                print(f"   {category_name:25s}: ERROR - {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   {category_name:25s}: Method not found")
    
    # 7. Home data summary
    print("\n7. ДАННЫЕ ДОМА (первые 40 ключей)")
    home_keys = list(meadow_rose.keys())[:40]
    for key in home_keys:
        value = meadow_rose.get(key)
        if isinstance(value, (dict, list)):
            print(f"   {key:30s}: {type(value).__name__} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")
        elif isinstance(value, str) and len(value) > 80:
            print(f"   {key:30s}: {value[:80]}...")
        else:
            print(f"   {key:30s}: {value}")
    
    # 8. Check what data is missing
    print("\n8. АНАЛИЗ ОТСУТСТВУЮЩИХ ДАННЫХ")
    print("   Для полного анализа нужны данные от:")
    print("      - CQC API (location_id: {})".format(meadow_rose.get('cqc_location_id', 'N/A')))
    print("      - Companies House (name: {})".format(meadow_rose.get('name', 'N/A')))
    print("      - Google Places (name: {})".format(meadow_rose.get('name', 'N/A')))
    print("      - FSA (name: {})".format(meadow_rose.get('name', 'N/A')))
    print("      - Staff Quality (location_id: {})".format(meadow_rose.get('cqc_location_id', 'N/A')))
    
    print("\n" + "="*80)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*80)
    print("\n💡 Для получения данных от всех API источников запустите")
    print("   генерацию отчета через API endpoint /professional-report")

if __name__ == "__main__":
    analyze_meadow_rose()

