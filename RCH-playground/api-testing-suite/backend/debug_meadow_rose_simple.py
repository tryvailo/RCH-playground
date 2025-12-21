#!/usr/bin/env python3
"""
Упрощенный скрипт для анализа дома Meadow Rose Nursing Home
Использует существующие функции из report_routes
"""
import json
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path setup
from routers.report_routes import generate_professional_report

async def analyze_meadow_rose():
    """Анализ дома Meadow Rose через API endpoint"""
    
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
    
    # 2. Generate report
    print("\n2. ГЕНЕРАЦИЯ ОТЧЕТА")
    request_data = {
        "questionnaire": questionnaire
    }
    
    try:
        response = await generate_professional_report(request_data)
        
        # Handle response
        if hasattr(response, 'body'):
            report_data = json.loads(response.body)
        elif isinstance(response, dict):
            report_data = response
        else:
            report_data = response
        
        if not report_data or 'careHomes' not in report_data:
            print("   ❌ Ошибка: Нет данных о домах в ответе")
            return
        
        care_homes = report_data.get('careHomes', [])
        print(f"   ✅ Найдено {len(care_homes)} домов")
        
        # 3. Find Meadow Rose
        print("\n3. ПОИСК MEADOW ROSE NURSING HOME")
        meadow_rose = None
        for home in care_homes:
            name = str(home.get('name', '')).lower()
            if 'meadow' in name and 'rose' in name:
                meadow_rose = home
                break
        
        if not meadow_rose:
            print("   ⚠️ Meadow Rose не найден в топ-5, показываю первый дом")
            if care_homes:
                meadow_rose = care_homes[0]
            else:
                print("   ❌ Нет домов в отчете")
                return
        
        print(f"   ✅ Дом найден: {meadow_rose.get('name', 'Unknown')}")
        
        # 4. Print detailed analysis
        print("\n" + "="*80)
        print("ДЕТАЛЬНЫЙ АНАЛИЗ ДОМА")
        print("="*80)
        
        print(f"\n🏠 Название: {meadow_rose.get('name', 'Unknown')}")
        print(f"   ID: {meadow_rose.get('id', 'Unknown')}")
        print(f"   Match Score: {meadow_rose.get('matchScore', 0)}%")
        print(f"   Адрес: {meadow_rose.get('location', 'Unknown')}")
        
        # Factor Scores
        print("\n📊 FACTOR SCORES:")
        factor_scores = meadow_rose.get('factorScores', [])
        if factor_scores:
            for factor in factor_scores:
                category = factor.get('category', 'Unknown')
                score = factor.get('score', 0)
                max_score = factor.get('maxScore', 0)
                weight = factor.get('weight', 0)
                percentage = (score / max_score * 100) if max_score > 0 else 0
                print(f"   {category:30s} | {score:6.1f}/{max_score:6.1f} | {percentage:5.1f}% | weight: {weight:.2f}")
        else:
            print("   ❌ Factor Scores пустые!")
        
        # Match Result
        print("\n📈 MATCH RESULT:")
        match_result = meadow_rose.get('matchResult', {})
        if match_result:
            category_scores = match_result.get('category_scores', {})
            if category_scores:
                print("   Category Scores (0-1 scale):")
                for category, score in category_scores.items():
                    print(f"      {category:15s}: {score:.4f}")
            
            point_allocations = match_result.get('point_allocations', {})
            if point_allocations:
                print("\n   Point Allocations:")
                for category, points in point_allocations.items():
                    print(f"      {category:15s}: {points:6.2f} points")
            
            weights = match_result.get('weights', {})
            if weights:
                print("\n   Weights:")
                for category, weight in weights.items():
                    print(f"      {category:15s}: {weight:6.2f}%")
        else:
            print("   ❌ Match Result пустой!")
        
        # CQC Deep Dive
        print("\n🏥 CQC DEEP DIVE:")
        cqc_deep_dive = meadow_rose.get('cqcDeepDive', {})
        if cqc_deep_dive:
            print(f"   Overall Rating: {cqc_deep_dive.get('overall_rating', 'N/A')}")
            print(f"   Current Rating: {cqc_deep_dive.get('current_rating', 'N/A')}")
            print(f"   Rating Trend: {cqc_deep_dive.get('rating_trend', 'N/A')}")
            
            detailed_ratings = cqc_deep_dive.get('detailed_ratings', {})
            if detailed_ratings:
                print("\n   Detailed Ratings:")
                for key, value in detailed_ratings.items():
                    if isinstance(value, dict):
                        rating = value.get('rating', 'N/A')
                        print(f"      {key:15s}: {rating}")
                    else:
                        print(f"      {key:15s}: {value}")
            
            historical = cqc_deep_dive.get('historical_ratings', [])
            print(f"\n   Historical Ratings: {len(historical)} записей")
            if historical:
                for i, hist in enumerate(historical[:3], 1):
                    print(f"      {i}. {hist.get('date', 'N/A')}: {hist.get('rating', 'N/A')}")
            
            enforcement = cqc_deep_dive.get('enforcement_actions', [])
            print(f"   Enforcement Actions: {len(enforcement)} записей")
        else:
            print("   ❌ CQC Deep Dive данные отсутствуют!")
        
        # Financial Stability
        print("\n💰 FINANCIAL STABILITY:")
        financial = meadow_rose.get('financialStability', {})
        if financial:
            print(f"   Данные доступны: {bool(financial)}")
            print(f"   Ключи: {list(financial.keys())[:10]}")
            if 'financial_stability_score' in financial:
                print(f"   Financial Stability Score: {financial.get('financial_stability_score', 'N/A')}")
        else:
            print("   ❌ Financial Stability данные отсутствуют!")
        
        # Staff Quality
        print("\n👥 STAFF QUALITY:")
        staff = meadow_rose.get('staffQuality', {})
        if staff:
            print(f"   Данные доступны: {bool(staff)}")
            print(f"   Ключи: {list(staff.keys())[:10]}")
            if 'staff_quality_score' in staff:
                print(f"   Staff Quality Score: {staff.get('staff_quality_score', 'N/A')}")
        else:
            print("   ❌ Staff Quality данные отсутствуют!")
        
        # Google Places
        print("\n📍 GOOGLE PLACES:")
        google = meadow_rose.get('googlePlaces', {})
        if google:
            print(f"   Rating: {google.get('rating', 'N/A')}")
            print(f"   Review Count: {google.get('user_ratings_total', 'N/A')}")
            print(f"   Ключи: {list(google.keys())[:10]}")
        else:
            print("   ❌ Google Places данные отсутствуют!")
        
        # Full data summary
        print("\n" + "="*80)
        print("ПОЛНЫЙ ДАМП ДАННЫХ (первые 50 ключей)")
        print("="*80)
        home_keys = list(meadow_rose.keys())[:50]
        for key in home_keys:
            value = meadow_rose.get(key)
            if isinstance(value, (dict, list)):
                print(f"   {key:30s}: {type(value).__name__} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")
            elif isinstance(value, str) and len(value) > 100:
                print(f"   {key:30s}: {value[:100]}...")
            else:
                print(f"   {key:30s}: {value}")
        
        print("\n" + "="*80)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_meadow_rose())

