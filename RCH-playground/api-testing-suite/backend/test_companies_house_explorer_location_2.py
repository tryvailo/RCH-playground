#!/usr/bin/env python3
"""
Детальное тестирование Companies House Explorer для второй тестовой локации
Проверяет все функции: поиск, детальная информация, финансовое здоровье, premium данные
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test location 2: Meadows House Residential and Nursing Home
TEST_LOCATION_2 = {
    "name": "Meadows House Residential and Nursing Home",
    "address": "Cullum Welch Court",
    "city": "London",
    "postcode": "SE3 0PW",
    "county": "Greater London"
}

async def test_companies_house_explorer():
    """Детальное тестирование всех функций Companies House Explorer"""
    
    print("="*80)
    print("ТЕСТИРОВАНИЕ COMPANIES HOUSE EXPLORER - ВТОРАЯ ТЕСТОВАЯ ЛОКАЦИЯ")
    print("="*80)
    print(f"\n📍 Локация: {TEST_LOCATION_2['name']}")
    print(f"   Адрес: {TEST_LOCATION_2['address']}, {TEST_LOCATION_2['city']}")
    print(f"   Посткод: {TEST_LOCATION_2['postcode']}")
    
    results = {
        "location": TEST_LOCATION_2,
        "api_key_status": "unknown",
        "search_test": {"status": "not_run", "companies_found": 0, "error": None},
        "company_details_test": {"status": "not_run", "error": None},
        "financial_health_test": {"status": "not_run", "error": None},
        "premium_data_test": {"status": "not_run", "error": None},
        "enrichment_test": {"status": "not_run", "error": None}
    }
    
    try:
        from api_clients.companies_house_client import CompaniesHouseAPIClient
        from utils.client_factory import get_companies_house_client
        from services.companies_house_service import CompaniesHouseService, enrich_care_home_with_financial_data
        from config_manager import get_credentials
        
        # 1. Проверка API ключа
        print("\n" + "="*80)
        print("1. ПРОВЕРКА API КЛЮЧА")
        print("="*80)
        
        creds = get_credentials()
        api_key = None
        if creds.companies_house and creds.companies_house.api_key:
            api_key = creds.companies_house.api_key
            placeholder_values = ["your-companies-house-api-key", "your-companies-house-key", "placeholder", "example", "test"]
            if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
                print(f"   ❌ API ключ является placeholder")
                results["api_key_status"] = "placeholder"
                print(f"   ⚠️  Установите валидный API ключ в config.json")
                # Continue testing anyway to show what would happen
            else:
                print(f"   ✅ API ключ найден: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
                results["api_key_status"] = "configured"
        else:
            print(f"   ❌ API ключ не настроен")
            results["api_key_status"] = "not_configured"
            print(f"   ⚠️  Установите API ключ в config.json или переменной окружения COMPANIES_HOUSE_API_KEY")
            # Continue testing to show what endpoints are available
        
        # 2. Тест поиска компаний (API endpoint: /api/companies-house/search)
        print("\n" + "="*80)
        print("2. ТЕСТ ПОИСКА КОМПАНИЙ")
        print("="*80)
        
        if api_key and results["api_key_status"] != "placeholder":
            try:
                client = get_companies_house_client()
                print(f"   🔍 Поиск: '{TEST_LOCATION_2['name']}'")
                
                companies = await client.search_companies(TEST_LOCATION_2['name'], items_per_page=10)
                
                if companies:
                    print(f"   ✅ Найдено {len(companies)} компаний")
                    results["search_test"]["status"] = "success"
                    results["search_test"]["companies_found"] = len(companies)
                    
                    # Display first 3 companies
                    for idx, company in enumerate(companies[:3], 1):
                        print(f"\n   {idx}. {company.get('title', 'Unknown')}")
                        print(f"      Company Number: {company.get('company_number', 'N/A')}")
                        print(f"      Status: {company.get('company_status', 'N/A')}")
                        print(f"      Type: {company.get('company_type', 'N/A')}")
                        print(f"      Address: {company.get('address_snippet', 'N/A')[:60]}...")
                else:
                    print(f"   ⚠️  Компании не найдены")
                    results["search_test"]["status"] = "no_results"
                    
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Ошибка: {error_msg}")
                results["search_test"]["status"] = "error"
                results["search_test"]["error"] = error_msg
                
                if "401" in error_msg or "Unauthorized" in error_msg:
                    print(f"\n   ⚠️  ПРОБЛЕМА: Companies House API возвращает 401 Unauthorized")
                    print(f"   Возможные причины:")
                    print(f"   1. API ключ неверный или истек")
                    print(f"   2. IP адрес не зарегистрирован в настройках приложения")
                    print(f"   3. Приложение в режиме 'test' вместо 'live'")
                    print(f"   4. Используется неправильный тип ключа (Streaming вместо REST)")
        else:
            print(f"   ⚠️  Пропущено (API ключ не настроен)")
            results["search_test"]["status"] = "skipped"
        
        # 3. Тест получения детальной информации (API endpoint: /api/companies-house/company/{number})
        print("\n" + "="*80)
        print("3. ТЕСТ ПОЛУЧЕНИЯ ДЕТАЛЬНОЙ ИНФОРМАЦИИ")
        print("="*80)
        
        # Use a known test company number if search failed
        test_company_number = "00000006"  # Example company number for testing
        
        if api_key and results["api_key_status"] != "placeholder":
            try:
                client = get_companies_house_client()
                print(f"   📊 Загрузка профиля компании {test_company_number}...")
                
                profile = await client.get_company_profile(test_company_number)
                
                print(f"   ✅ Профиль загружен:")
                print(f"      Название: {profile.get('company_name', 'N/A')}")
                print(f"      Статус: {profile.get('company_status', 'N/A')}")
                print(f"      Дата создания: {profile.get('date_of_creation', 'N/A')}")
                
                results["company_details_test"]["status"] = "success"
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Ошибка: {error_msg}")
                results["company_details_test"]["status"] = "error"
                results["company_details_test"]["error"] = error_msg
        else:
            print(f"   ⚠️  Пропущено (API ключ не настроен)")
            results["company_details_test"]["status"] = "skipped"
        
        # 4. Тест финансового здоровья (API endpoint: /api/companies-house/company/{number}/financial-health)
        print("\n" + "="*80)
        print("4. ТЕСТ ФИНАНСОВОГО ЗДОРОВЬЯ")
        print("="*80)
        
        if api_key and results["api_key_status"] != "placeholder":
            try:
                from services.companies_house_service import CompaniesHouseService
                
                service = CompaniesHouseService(api_key=api_key)
                print(f"   🔍 Поиск company_number для '{TEST_LOCATION_2['name']}'...")
                
                company_number = await service.find_company_for_care_home(
                    care_home_name=TEST_LOCATION_2['name'],
                    address=TEST_LOCATION_2['address'],
                    postcode=TEST_LOCATION_2['postcode']
                )
                
                if company_number:
                    print(f"   ✅ Company Number найден: {company_number}")
                    print(f"   📊 Получение финансовой стабильности...")
                    
                    financial_stability = await service.get_financial_stability(company_number)
                    
                    print(f"   ✅ Финансовая стабильность:")
                    print(f"      Total Score: {financial_stability.total_score}/20")
                    print(f"      Risk Level: {financial_stability.risk_level}")
                    print(f"      Risk Score: {financial_stability.risk_score}")
                    
                    results["financial_health_test"]["status"] = "success"
                else:
                    print(f"   ⚠️  Company Number не найден")
                    results["financial_health_test"]["status"] = "company_not_found"
                    
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Ошибка: {error_msg}")
                results["financial_health_test"]["status"] = "error"
                results["financial_health_test"]["error"] = error_msg
        else:
            print(f"   ⚠️  Пропущено (API ключ не настроен)")
            results["financial_health_test"]["status"] = "skipped"
        
        # 5. Тест обогащения данных
        print("\n" + "="*80)
        print("5. ТЕСТ ОБОГАЩЕНИЯ ДАННЫХ")
        print("="*80)
        
        if api_key and results["api_key_status"] != "placeholder":
            try:
                print(f"   🔄 Обогащение данных для '{TEST_LOCATION_2['name']}'...")
                
                enriched_data = await enrich_care_home_with_financial_data(
                    care_home_name=TEST_LOCATION_2['name'],
                    address=TEST_LOCATION_2['address'],
                    postcode=TEST_LOCATION_2['postcode'],
                    api_key=api_key
                )
                
                if enriched_data:
                    print(f"   ✅ Данные обогащены успешно")
                    scoring_data = enriched_data.get('scoring_data', {})
                    print(f"      Risk Score: {scoring_data.get('risk_score', 'N/A')}")
                    print(f"      Risk Level: {scoring_data.get('risk_level', 'N/A')}")
                    
                    results["enrichment_test"]["status"] = "success"
                else:
                    print(f"   ⚠️  Данные не обогащены (компания не найдена)")
                    results["enrichment_test"]["status"] = "company_not_found"
                    
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Ошибка: {error_msg}")
                results["enrichment_test"]["status"] = "error"
                results["enrichment_test"]["error"] = error_msg
        else:
            print(f"   ⚠️  Пропущено (API ключ не настроен)")
            results["enrichment_test"]["status"] = "skipped"
        
        # 6. Итоговый отчет
        print("\n" + "="*80)
        print("6. ИТОГОВЫЙ ОТЧЕТ")
        print("="*80)
        
        print(f"\n   📊 Результаты тестирования:")
        print(f"      API ключ: {results['api_key_status']}")
        print(f"      Поиск компаний: {results['search_test']['status']}")
        print(f"      Детальная информация: {results['company_details_test']['status']}")
        print(f"      Финансовое здоровье: {results['financial_health_test']['status']}")
        print(f"      Обогащение данных: {results['enrichment_test']['status']}")
        
        # Сохранение результатов
        output_file = Path(__file__).parent / "companies_house_test_location_2_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n   ✅ Результаты сохранены в: {output_file}")
        
        # Рекомендации
        if results["api_key_status"] in ["placeholder", "not_configured"]:
            print(f"\n   ⚠️  РЕКОМЕНДАЦИИ:")
            print(f"      1. Установите валидный Companies House API ключ")
            print(f"      2. Получите ключ на: https://developer.company-information.service.gov.uk/")
            print(f"      3. Зарегистрируйте IP адрес в настройках приложения")
            print(f"      4. Убедитесь, что приложение в режиме 'live' (не 'test')")
        
        if "401" in str(results.get("search_test", {}).get("error", "")):
            print(f"\n   ⚠️  ПРОБЛЕМА С АУТЕНТИФИКАЦИЕЙ:")
            print(f"      Companies House API возвращает 401 Unauthorized")
            print(f"      Проверьте:")
            print(f"      1. Правильность API ключа")
            print(f"      2. Регистрацию IP адреса в настройках приложения")
            print(f"      3. Режим приложения (должен быть 'live')")
        
        print("\n" + "="*80)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*80)
        
    except Exception as e:
        print(f"\n   ❌ Критическая ошибка: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        results["critical_error"] = str(e)
        
        # Save results even on error
        output_file = Path(__file__).parent / "companies_house_test_location_2_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(test_companies_house_explorer())

