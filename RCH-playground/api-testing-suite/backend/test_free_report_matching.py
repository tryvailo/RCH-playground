#!/usr/bin/env python3
"""
Test Free Report Matching for Single Questionnaire
Tests matching algorithm with CQC + Staging merged data
"""
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any
import sys

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"  # Use 127.0.0.1 instead of localhost
# Try multiple possible paths for questionnaire
QUESTIONNAIRE_PATHS = [
    Path(__file__).parent.parent.parent / "RCH-playground" / "data" / "sample_questionnaires" / "questionnaire_1.json",
    Path(__file__).parent.parent / "frontend" / "public" / "sample_questionnaires" / "questionnaire_1.json",
    Path(__file__).parent.parent.parent.parent / "RCH-playground" / "data" / "sample_questionnaires" / "questionnaire_1.json",
]

# Fallback questionnaire if file not found
DEFAULT_QUESTIONNAIRE = {
    "postcode": "B1 1AA",
    "budget": 1200.0,
    "care_type": "residential",
    "chc_probability": 35.5
}


def test_free_report_matching(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test free report matching for a single questionnaire
    
    Args:
        questionnaire: Questionnaire data dict
        
    Returns:
        Dict with test results
    """
    print("\n" + "="*80)
    print("🧪 ТЕСТИРОВАНИЕ МАТЧИНГА БЕСПЛАТНОГО ОТЧЕТА")
    print("="*80)
    print(f"\n📋 Анкета:")
    print(f"   Postcode: {questionnaire.get('postcode', 'N/A')}")
    print(f"   Budget: £{questionnaire.get('budget', 0)}/week")
    print(f"   Care Type: {questionnaire.get('care_type', 'N/A')}")
    print(f"   CHC Probability: {questionnaire.get('chc_probability', 0)}%")
    
    try:
        print(f"\n📡 Отправка запроса на {BACKEND_URL}/api/free-report...")
        
        # Prepare request
        url = f"{BACKEND_URL}/api/free-report"
        data = json.dumps(questionnaire).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # Make request
        try:
            with urllib.request.urlopen(req, timeout=120.0) as response:
                status_code = response.getcode()
                print(f"   Статус: {status_code}")
                response_data = response.read().decode('utf-8')
                
                if status_code != 200:
                    print(f"\n❌ ОШИБКА: HTTP {status_code}")
                    try:
                        error_detail = json.loads(response_data)
                        print(f"   Детали: {str(error_detail.get('detail', error_detail))[:500]}")
                    except:
                        print(f"   Детали: {str(response_data)[:500]}")
                    return {
                        'success': False,
                        'error': f"HTTP {status_code}",
                        'detail': str(response_data)[:1000]
                    }
                
                result_data = json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"\n❌ ОШИБКА: HTTP {e.code}")
            try:
                error_detail = json.loads(error_body)
                print(f"   Детали: {str(error_detail.get('detail', error_detail))[:500]}")
            except:
                print(f"   Детали: {str(error_body)[:500]}")
            return {
                'success': False,
                'error': f"HTTP {e.code}",
                'detail': str(error_body)[:1000]
            }
        care_homes = result_data.get('care_homes', [])
        
        print(f"\n✅ Успешно получен ответ")
        print(f"   Найдено домов: {len(care_homes)}")
        
        # Analyze results
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        print("="*80)
        
        for idx, home in enumerate(care_homes, 1):
            match_type = home.get('match_type', 'Unknown')
            home_data = home.get('home', home)
            
            print(f"\n🏠 Дом #{idx}: {match_type}")
            print(f"   Название: {home_data.get('name', 'N/A')}")
            print(f"   Postcode: {home_data.get('postcode', 'N/A')}")
            print(f"   Город: {home_data.get('city', 'N/A')}")
            
            # Check data sources
            print(f"\n   📍 Источники данных:")
            
            # CQC data
            cqc_rating = (
                home_data.get('cqc_rating_overall') or 
                home_data.get('rating') or 
                home_data.get('overall_rating')
            )
            if cqc_rating:
                print(f"      ✅ CQC Rating: {cqc_rating}")
            else:
                print(f"      ⚠️  CQC Rating: не найдено")
            
            # Staging data - Pricing
            fee_residential = home_data.get('fee_residential_from')
            fee_dementia = home_data.get('fee_dementia_from')
            fee_nursing = home_data.get('fee_nursing_from')
            
            pricing_from_staging = []
            if fee_residential:
                pricing_from_staging.append(f"Residential: £{fee_residential}/week")
            if fee_dementia:
                pricing_from_staging.append(f"Dementia: £{fee_dementia}/week")
            if fee_nursing:
                pricing_from_staging.append(f"Nursing: £{fee_nursing}/week")
            
            if pricing_from_staging:
                print(f"      ✅ Pricing (Staging): {', '.join(pricing_from_staging)}")
            else:
                print(f"      ⚠️  Pricing: не найдено")
            
            # Staging data - Reviews
            review_score = home_data.get('review_average_score')
            review_count = home_data.get('review_count')
            
            if review_score or review_count:
                reviews_str = []
                if review_score:
                    reviews_str.append(f"Score: {review_score}")
                if review_count:
                    reviews_str.append(f"Count: {review_count}")
                print(f"      ✅ Reviews (Staging): {', '.join(reviews_str)}")
            else:
                print(f"      ⚠️  Reviews: не найдено")
            
            # Staging data - Availability
            beds_available = home_data.get('beds_available')
            has_availability = home_data.get('has_availability')
            beds_total = home_data.get('beds_total')
            
            if beds_available is not None or has_availability is not None or beds_total:
                availability_str = []
                if beds_total:
                    availability_str.append(f"Total: {beds_total}")
                if beds_available is not None:
                    availability_str.append(f"Available: {beds_available}")
                if has_availability is not None:
                    availability_str.append(f"Has availability: {has_availability}")
                print(f"      ✅ Availability (Staging): {', '.join(availability_str)}")
            else:
                print(f"      ⚠️  Availability: не найдено")
            
            # Staging data - Amenities
            wheelchair = home_data.get('wheelchair_access')
            wifi = home_data.get('wifi_available')
            parking = home_data.get('parking_onsite')
            
            amenities_from_staging = []
            if wheelchair is not None:
                amenities_from_staging.append(f"Wheelchair: {wheelchair}")
            if wifi is not None:
                amenities_from_staging.append(f"WiFi: {wifi}")
            if parking is not None:
                amenities_from_staging.append(f"Parking: {parking}")
            
            if amenities_from_staging:
                print(f"      ✅ Amenities (Staging): {', '.join(amenities_from_staging)}")
            else:
                print(f"      ⚠️  Amenities: не найдено")
            
            # Match score
            score = home.get('score', home_data.get('match_score', 0))
            if score:
                print(f"\n   📊 Match Score: {score}/50")
            
            # Match reasoning
            reasoning = home.get('match_reasoning', [])
            if reasoning:
                print(f"   💡 Reasoning:")
                for reason in reasoning[:3]:  # Show first 3 reasons
                    print(f"      - {reason}")
        
        # Summary
        print(f"\n{'='*80}")
        print("📈 СВОДКА:")
        print(f"   Всего домов: {len(care_homes)}")
        
        # Count data sources
        cqc_count = sum(1 for h in care_homes if (h.get('home', h).get('cqc_rating_overall') or h.get('home', h).get('rating')))
        staging_pricing_count = sum(1 for h in care_homes if (h.get('home', h).get('fee_residential_from') or h.get('home', h).get('fee_dementia_from')))
        staging_reviews_count = sum(1 for h in care_homes if (h.get('home', h).get('review_average_score') or h.get('home', h).get('review_count')))
        staging_availability_count = sum(1 for h in care_homes if (h.get('home', h).get('beds_available') is not None or h.get('home', h).get('has_availability') is not None))
        
        print(f"   CQC данные: {cqc_count}/{len(care_homes)} домов")
        print(f"   Staging Pricing: {staging_pricing_count}/{len(care_homes)} домов")
        print(f"   Staging Reviews: {staging_reviews_count}/{len(care_homes)} домов")
        print(f"   Staging Availability: {staging_availability_count}/{len(care_homes)} домов")
        print("="*80)
        
        return {
            'success': True,
            'questionnaire': questionnaire,
            'care_homes_count': len(care_homes),
            'care_homes': care_homes,
            'summary': {
                'cqc_data': cqc_count,
                'staging_pricing': staging_pricing_count,
                'staging_reviews': staging_reviews_count,
                'staging_availability': staging_availability_count
            }
        }
            
    except urllib.error.URLError as e:
        print(f"\n❌ ОШИБКА: Не удалось подключиться к серверу")
        print(f"   Убедитесь, что сервер запущен на {BACKEND_URL}")
        print(f"   Запустите: cd api-testing-suite/backend && uvicorn main:app --reload")
        print(f"   Детали: {str(e)}")
        return {
            'success': False,
            'error': 'ConnectionError',
            'detail': f'Cannot connect to {BACKEND_URL}: {str(e)}'
        }
    except Exception as e:
        print(f"\n❌ ОШИБКА: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': type(e).__name__,
            'detail': str(e)
        }


def main():
    """Main test function"""
    # Load questionnaire
    questionnaire = DEFAULT_QUESTIONNAIRE.copy()
    questionnaire_loaded = False
    
    for q_path in QUESTIONNAIRE_PATHS:
        if q_path.exists():
            try:
                with open(q_path, 'r', encoding='utf-8') as f:
                    questionnaire = json.load(f)
                print(f"✅ Загружена анкета из {q_path}")
                questionnaire_loaded = True
                break
            except Exception as e:
                print(f"⚠️  Не удалось загрузить анкету из {q_path}: {e}")
                continue
    
    if not questionnaire_loaded:
        print(f"⚠️  Файл анкеты не найден в стандартных местах")
        print(f"   Используется анкета по умолчанию: {DEFAULT_QUESTIONNAIRE}")
    
    # Run test
    result = test_free_report_matching(questionnaire)
    
    # Save results
    results_file = Path(__file__).parent / "free_report_matching_test_result.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены в: {results_file}")
    
    if result.get('success'):
        print("\n✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
        return 0
    else:
        print("\n❌ ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

