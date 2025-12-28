#!/usr/bin/env python3
"""
Тестирование Companies House для второй тестовой локации
Вторая локация: Meadows House Residential and Nursing Home
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

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

async def test_companies_house_location_2():
    """Тестирование Companies House для второй тестовой локации"""
    
    print("="*80)
    print("ТЕСТИРОВАНИЕ COMPANIES HOUSE - ВТОРАЯ ТЕСТОВАЯ ЛОКАЦИЯ")
    print("="*80)
    print(f"\n📍 Локация: {TEST_LOCATION_2['name']}")
    print(f"   Адрес: {TEST_LOCATION_2['address']}, {TEST_LOCATION_2['city']}")
    print(f"   Посткод: {TEST_LOCATION_2['postcode']}")
    
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
                print(f"   ❌ API ключ является placeholder: {api_key[:20]}...")
                print(f"   ⚠️  Установите валидный API ключ в config.json")
                return
            else:
                print(f"   ✅ API ключ найден: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
        else:
            print(f"   ❌ API ключ не настроен")
            print(f"   ⚠️  Установите API ключ в config.json или переменной окружения COMPANIES_HOUSE_API_KEY")
            return
        
        # 2. Поиск компании по имени
        print("\n" + "="*80)
        print("2. ПОИСК КОМПАНИИ ПО ИМЕНИ")
        print("="*80)
        
        try:
            client = get_companies_house_client()
            print(f"   🔍 Поиск компании: '{TEST_LOCATION_2['name']}'")
            
            companies = await client.search_companies(TEST_LOCATION_2['name'], items_per_page=10)
            
            if not companies:
                print(f"   ❌ Компания не найдена")
                print(f"   ⚠️  Попробуем альтернативные варианты...")
                
                # Try alternative names
                alternative_names = [
                    f"{TEST_LOCATION_2['name']} Ltd",
                    f"{TEST_LOCATION_2['name']} Limited",
                    "Meadows House",
                    "Meadows House Care"
                ]
                
                for alt_name in alternative_names:
                    print(f"   🔍 Поиск: '{alt_name}'")
                    companies = await client.search_companies(alt_name, items_per_page=5)
                    if companies:
                        print(f"   ✅ Найдено {len(companies)} компаний для '{alt_name}'")
                        break
                
                if not companies:
                    print(f"   ❌ Компания не найдена ни по одному варианту")
                    return
            else:
                print(f"   ✅ Найдено {len(companies)} компаний")
            
            # Display found companies
            print(f"\n   📋 Найденные компании:")
            for idx, company in enumerate(companies[:5], 1):
                print(f"      {idx}. {company.get('title', 'Unknown')}")
                print(f"         Company Number: {company.get('company_number', 'N/A')}")
                print(f"         Status: {company.get('company_status', 'N/A')}")
                print(f"         Address: {company.get('address_snippet', 'N/A')}")
                print()
            
            # Use first company for detailed analysis
            if companies:
                selected_company = companies[0]
                company_number = selected_company.get('company_number')
                company_name = selected_company.get('title', 'Unknown')
                
                print(f"   ✅ Выбрана компания: {company_name} ({company_number})")
            else:
                print(f"   ❌ Нет компаний для анализа")
                return
                
        except Exception as e:
            print(f"   ❌ Ошибка при поиске компании: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return
        
        # 3. Получение детальной информации о компании
        print("\n" + "="*80)
        print("3. ПОЛУЧЕНИЕ ДЕТАЛЬНОЙ ИНФОРМАЦИИ О КОМПАНИИ")
        print("="*80)
        
        try:
            print(f"   📊 Загрузка профиля компании {company_number}...")
            profile = await client.get_company_profile(company_number)
            
            print(f"   ✅ Профиль загружен:")
            print(f"      Название: {profile.get('company_name', 'N/A')}")
            print(f"      Статус: {profile.get('company_status', 'N/A')}")
            print(f"      Дата создания: {profile.get('date_of_creation', 'N/A')}")
            print(f"      Тип: {profile.get('type', 'N/A')}")
            
            print(f"\n   📊 Загрузка директоров...")
            officers = await client.get_company_officers(company_number)
            print(f"   ✅ Найдено директоров: {len(officers)}")
            
            print(f"\n   📊 Загрузка залогов (charges)...")
            charges = await client.get_charges(company_number)
            print(f"   ✅ Найдено залогов: {len(charges)}")
            
        except Exception as e:
            print(f"   ❌ Ошибка при загрузке детальной информации: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return
        
        # 4. Тестирование обогащения данных через enrich_care_home_with_financial_data
        print("\n" + "="*80)
        print("4. ТЕСТИРОВАНИЕ ОБОГАЩЕНИЯ ДАННЫХ")
        print("="*80)
        
        try:
            print(f"   🔄 Обогащение данных для '{TEST_LOCATION_2['name']}'...")
            print(f"      Адрес: {TEST_LOCATION_2['address']}")
            print(f"      Посткод: {TEST_LOCATION_2['postcode']}")
            
            enriched_data = await enrich_care_home_with_financial_data(
                care_home_name=TEST_LOCATION_2['name'],
                address=TEST_LOCATION_2['address'],
                postcode=TEST_LOCATION_2['postcode'],
                api_key=api_key
            )
            
            if enriched_data:
                print(f"   ✅ Данные обогащены успешно")
                
                company_number_found = enriched_data.get('company_number')
                scoring_data = enriched_data.get('scoring_data', {})
                report_section = enriched_data.get('report_section', {})
                
                print(f"\n   📊 Результаты обогащения:")
                print(f"      Company Number: {company_number_found}")
                print(f"      Risk Score: {scoring_data.get('risk_score', 'N/A')}")
                print(f"      Risk Level: {scoring_data.get('risk_level', 'N/A')}")
                print(f"      Altman Z-Score: {scoring_data.get('altman_z_score', 'N/A')}")
                print(f"      Financial Stability Score: {scoring_data.get('financial_stability_score', 'N/A')}")
                
                if report_section:
                    company_info = report_section.get('company_info', {})
                    print(f"\n   📋 Информация о компании:")
                    print(f"      Название: {company_info.get('name', 'N/A')}")
                    print(f"      Статус: {company_info.get('status', 'N/A')}")
                    print(f"      Возраст: {company_info.get('age_years', 'N/A')} лет")
                    
                    scores = report_section.get('scores', {})
                    print(f"\n   📈 Оценки:")
                    print(f"      Total Score: {scores.get('total', 'N/A')}")
                    print(f"      Risk Level: {scores.get('risk_level', 'N/A')}")
                    print(f"      Risk Score: {scores.get('risk_score', 'N/A')}")
            else:
                print(f"   ❌ Данные не обогащены (компания не найдена)")
                
        except Exception as e:
            print(f"   ❌ Ошибка при обогащении данных: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
        
        # 5. Тестирование через CompaniesHouseService
        print("\n" + "="*80)
        print("5. ТЕСТИРОВАНИЕ ЧЕРЕЗ CompaniesHouseService")
        print("="*80)
        
        try:
            service = CompaniesHouseService(api_key=api_key)
            
            print(f"   🔍 Поиск company_number для '{TEST_LOCATION_2['name']}'...")
            company_number_found = await service.find_company_for_care_home(
                care_home_name=TEST_LOCATION_2['name'],
                address=TEST_LOCATION_2['address'],
                postcode=TEST_LOCATION_2['postcode']
            )
            
            if company_number_found:
                print(f"   ✅ Company Number найден: {company_number_found}")
                
                print(f"\n   📊 Получение финансовой стабильности...")
                financial_stability = await service.get_financial_stability(company_number_found)
                
                print(f"   ✅ Финансовая стабильность рассчитана:")
                print(f"      Total Score: {financial_stability.total_score}/20")
                print(f"      Risk Level: {financial_stability.risk_level}")
                print(f"      Risk Score: {financial_stability.risk_score}")
                print(f"      Altman Z-Score: {financial_stability.altman_z_score.z_score:.2f} ({financial_stability.altman_z_score.z_score_label})")
                print(f"      Director Stability: {financial_stability.director_stability.stability_label}")
                print(f"      Ownership Type: {financial_stability.ownership_stability.ownership_type}")
                
                if financial_stability.issues:
                    print(f"\n   ⚠️  Проблемы ({len(financial_stability.issues)}):")
                    for issue in financial_stability.issues[:5]:
                        print(f"      - {issue}")
            else:
                print(f"   ❌ Company Number не найден")
                
        except Exception as e:
            print(f"   ❌ Ошибка при работе с CompaniesHouseService: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
        
        # 6. Итоговый отчет
        print("\n" + "="*80)
        print("6. ИТОГОВЫЙ ОТЧЕТ")
        print("="*80)
        
        print(f"\n   ✅ Тестирование завершено для:")
        print(f"      Локация: {TEST_LOCATION_2['name']}")
        print(f"      Посткод: {TEST_LOCATION_2['postcode']}")
        
        if 'company_number_found' in locals() and company_number_found:
            print(f"      ✅ Company Number найден: {company_number_found}")
        else:
            print(f"      ❌ Company Number не найден")
        
        if 'enriched_data' in locals() and enriched_data:
            print(f"      ✅ Данные обогащены успешно")
        else:
            print(f"      ❌ Данные не обогащены")
        
        print("\n" + "="*80)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*80)
        
    except Exception as e:
        print(f"\n   ❌ Критическая ошибка: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    asyncio.run(test_companies_house_location_2())

