#!/usr/bin/env python3
"""
Упрощенная версия скрипта для получения данных из CQC API
Работает без Supabase клиента, использует только CQC API
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

# Загружаем переменные из .env файла, если он существует
def load_env_file():
    """Загрузить переменные из .env файла"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Настройки CQC API
# Новый базовый URL после миграции CQC API
CQC_API_BASE = "https://api.service.cqc.org.uk/public/v1"
# Ключ загружается из переменной окружения CQC_SUBSCRIPTION_KEY
# Получить ключ: CQC Developer Portal → продукт "Syndication" → subscription keys
CQC_API_KEY = os.getenv("CQC_SUBSCRIPTION_KEY")

if not CQC_API_KEY:
    print("❌ ОШИБКА: Не установлен CQC_SUBSCRIPTION_KEY")
    print("Установите переменную окружения: export CQC_SUBSCRIPTION_KEY='your-subscription-key'")
    print("Получить ключ: CQC Developer Portal → продукт 'Syndication' → subscription keys")
    exit(1)

# Заголовки для CQC API
# CQC Syndication использует только Ocp-Apim-Subscription-Key (Azure API Management)
# Bearer не используется и не нужен
CQC_HEADERS = {
    "Ocp-Apim-Subscription-Key": CQC_API_KEY,
    "Content-Type": "application/json"
}

# Тестовые location_id из таблицы
TEST_LOCATION_IDS = [
    "1-10000302982",
    "1-10000812939",
    "1-10000813008",
    "1-1000210669",
    "1-1000401911"
]


def fetch_location_from_api(location_id: str) -> Optional[Dict[str, Any]]:
    """
    Получить данные локации из CQC API
    
    Args:
        location_id: CQC location ID (например, "1-108920865")
    
    Returns:
        Словарь с данными локации или None при ошибке
    """
    # Формируем URL (новый API не требует partnerCode)
    url = f"{CQC_API_BASE}/locations/{location_id}"
    
    try:
        response = requests.get(url, headers=CQC_HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print(f"❌ 401 Unauthorized для {location_id}")
            print(f"   Проверьте правильность CQC_SUBSCRIPTION_KEY")
            print(f"   Получить ключ: CQC Developer Portal → продукт 'Syndication' → subscription keys")
            return None
        elif response.status_code == 403:
            print(f"❌ 403 Forbidden для {location_id}")
            print(f"   Возможно, API ключ не активирован или требует регистрации")
            return None
        else:
            response.raise_for_status()
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к API для {location_id}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status code: {e.response.status_code}")
            print(f"   Response: {e.response.text[:200]}")
        else:
            print(f"   Ошибка: {str(e)}")
        return None


def extract_priority_1_fields(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """Извлечь поля Приоритета 1"""
    result = {}
    
    result['organisation_type'] = api_data.get('organisationType')
    result['location_sector'] = api_data.get('type')
    result['also_known_as'] = api_data.get('alsoKnownAs')
    result['registration_status'] = api_data.get('registrationStatus')
    
    # Даты
    for field, api_field in [
        ('registration_date', 'registrationDate'),
        ('deregistration_date', 'deregistrationDate'),
        ('registered_manager_absent_date', 'registeredManagerAbsentDate')
    ]:
        date_val = api_data.get(api_field)
        if date_val:
            try:
                result[field] = date_val.split('T')[0]
            except:
                result[field] = date_val
        else:
            result[field] = None
    
    # lastInspection.date
    last_inspection = api_data.get('lastInspection', {})
    if last_inspection and isinstance(last_inspection, dict):
        inspection_date = last_inspection.get('date')
        if inspection_date:
            try:
                result['last_inspection_date'] = inspection_date.split('T')[0]
            except:
                result['last_inspection_date'] = inspection_date
        else:
            result['last_inspection_date'] = None
    else:
        result['last_inspection_date'] = None
    
    return result


def extract_priority_2_fields(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """Извлечь поля Приоритета 2 (JSONB)"""
    result = {}
    
    result['relationships'] = api_data.get('relationships', [])
    result['location_types'] = api_data.get('locationTypes', [])
    
    # regulatedActivities с кодами и контактами
    regulated_activities = api_data.get('regulatedActivities', [])
    if regulated_activities:
        enhanced = []
        for activity in regulated_activities:
            enhanced.append({
                'name': activity.get('name'),
                'code': activity.get('code'),
                'contacts': activity.get('contacts', [])
            })
        result['regulated_activities_enhanced'] = enhanced
    else:
        result['regulated_activities_enhanced'] = []
    
    # currentRatings
    current_ratings = api_data.get('currentRatings', {})
    if current_ratings and isinstance(current_ratings, dict):
        result['service_ratings'] = current_ratings.get('serviceRatings', [])
        
        overall = current_ratings.get('overall', {})
        if overall and isinstance(overall, dict):
            result['key_question_ratings_with_dates'] = overall.get('keyQuestionRatings', [])
        else:
            result['key_question_ratings_with_dates'] = []
    else:
        result['service_ratings'] = []
        result['key_question_ratings_with_dates'] = []
    
    return result


def process_location(location_id: str) -> Optional[Dict[str, Any]]:
    """Обработать одну локацию"""
    print(f"📡 Получение данных для {location_id}...")
    
    api_data = fetch_location_from_api(location_id)
    if not api_data:
        return None
    
    priority_1 = extract_priority_1_fields(api_data)
    priority_2 = extract_priority_2_fields(api_data)
    
    result = {
        'location_id': location_id,
        **priority_1,
        **priority_2,
        'fetched_at': datetime.now().isoformat()
    }
    
    # Сохранить в файл
    output_dir = "fetched_data"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/location_{location_id.replace('-', '_')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Сохранено в {filename}")
    return result


def main():
    """Основная функция"""
    print("=" * 60)
    print("CQC API Data Fetcher (Simplified)")
    print("=" * 60)
    
    print(f"\n🎯 Обработка {len(TEST_LOCATION_IDS)} тестовых локаций...")
    
    results = []
    for i, location_id in enumerate(TEST_LOCATION_IDS, 1):
        print(f"\n[{i}/{len(TEST_LOCATION_IDS)}] {location_id}")
        result = process_location(location_id)
        if result:
            results.append(result)
        time.sleep(0.5)  # Задержка между запросами
    
    # Сводка
    summary = {
        'total': len(TEST_LOCATION_IDS),
        'successful': len(results),
        'failed': len(TEST_LOCATION_IDS) - len(results),
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    output_dir = "fetched_data"
    os.makedirs(output_dir, exist_ok=True)
    summary_file = f"{output_dir}/summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ Завершено!")
    print(f"   Успешно: {summary['successful']}")
    print(f"   Ошибок: {summary['failed']}")
    print(f"   Сводка: {summary_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()

