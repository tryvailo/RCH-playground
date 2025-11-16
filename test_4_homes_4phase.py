#!/usr/bin/env python3
"""
Тестирование 4-фазного подхода на 4 домах престарелых
"""
import requests
import json
import time
from datetime import datetime

# Тестовые данные
HOMES = [
    {
        "name": "Clare Court",
        "url": "https://www.averyhealthcare.co.uk/our-homes/clare-court"
    },
    {
        "name": "Metchley Manor",
        "url": "https://www.careuk.com/care-homes/metchley-manor"
    },
    {
        "name": "Bartley Green Lodge",
        "url": "https://www.sanctuary-care.co.uk/care-homes/bartley-green-lodge"
    },
    {
        "name": "Inglewood",
        "url": "https://www.careuk.com/care-homes/inglewood"
    }
]

API_URL = "http://localhost:8000/api/firecrawl/analyze"
RESULTS_FILE = "test_results_4_homes_4phase.json"

def test_care_home(name: str, url: str) -> dict:
    """Тестирование одного дома престарелых"""
    print(f"\n{'='*60}")
    print(f"🏠 Тестирование: {name}")
    print(f"🌐 URL: {url}")
    print(f"{'='*60}\n")
    
    payload = {
        "url": url,
        "care_home_name": name
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=600,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        
        # Извлекаем данные
        result_data = data.get("data", {})
        structured = result_data.get("structured_data", {})
        completeness = result_data.get("completeness", {})
        phase0 = result_data.get("phase0_summary", {})
        map_summary = result_data.get("map_summary", {})
        crawl_summary = result_data.get("crawl_summary", {})
        
        # Статистика
        method = result_data.get("extraction_method", "unknown")
        cms = phase0.get("cms", "Unknown")
        urls_found = map_summary.get("total_urls_found", 0)
        pages_crawled = crawl_summary.get("pages_crawled", 0)
        categories_filled = sum(1 for v in completeness.values() if v)
        total_categories = len(completeness)
        
        print(f"✅ Успешно получен ответ")
        print(f"📊 Метод: {method}")
        print(f"🏗️  CMS: {cms}")
        print(f"🗺️  URLs найдено: {urls_found}")
        print(f"🕷️  Страниц обработано: {pages_crawled}")
        print(f"📈 Заполнено категорий: {categories_filled}/{total_categories}")
        
        # Подсчет полей
        total_fields = 0
        filled_fields = 0
        for cat, cat_data in structured.items():
            if isinstance(cat_data, dict):
                for field, value in cat_data.items():
                    total_fields += 1
                    if value:
                        if isinstance(value, str) and value.strip():
                            filled_fields += 1
                        elif isinstance(value, (list, dict)) and len(value) > 0:
                            filled_fields += 1
                        elif not isinstance(value, str):
                            filled_fields += 1
        
        if total_fields > 0:
            percentage = int(filled_fields / total_fields * 100)
            print(f"📋 Заполнено полей: {filled_fields}/{total_fields} ({percentage}%)")
        
        # Топ категорий
        categories_with_data = []
        for cat, cat_data in structured.items():
            if isinstance(cat_data, dict):
                count = sum(1 for v in cat_data.values() if v and (
                    (isinstance(v, str) and v.strip()) or 
                    (isinstance(v, (list, dict)) and len(v) > 0) or
                    (not isinstance(v, str) and v)
                ))
                if count > 0:
                    categories_with_data.append((cat, count))
        
        categories_with_data.sort(key=lambda x: x[1], reverse=True)
        if categories_with_data:
            print(f"\n🏆 Топ-5 категорий по количеству данных:")
            for i, (cat, count) in enumerate(categories_with_data[:5], 1):
                print(f"   {i}. {cat.title()}: {count} полей")
        
        return {
            "name": name,
            "url": url,
            "status": "success",
            "method": method,
            "cms": cms,
            "urls_found": urls_found,
            "pages_crawled": pages_crawled,
            "completeness": completeness,
            "categories_filled": categories_filled,
            "total_categories": total_categories,
            "fields_filled": filled_fields,
            "total_fields": total_fields,
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
        return {
            "name": name,
            "url": url,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": name,
            "url": url,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Основная функция"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ 4-ФАЗНОГО ПОДХОДА НА 4 ДОМАХ")
    print("="*60)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    for home in HOMES:
        result = test_care_home(home["name"], home["url"])
        results.append(result)
        
        # Пауза между запросами
        if home != HOMES[-1]:
            print("\n⏳ Пауза 3 секунды перед следующим тестом...")
            time.sleep(3)
    
    # Сохраняем результаты
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Итоговая статистика
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*60 + "\n")
    
    successful = [r for r in results if r.get("status") == "success"]
    
    print(f"Всего протестировано: {len(results)} домов")
    print(f"Успешно: {len(successful)} домов")
    print(f"Ошибок: {len(results) - len(successful)} домов\n")
    
    if successful:
        for result in successful:
            print(f"🏠 {result['name']}")
            print(f"   Метод: {result.get('method', 'unknown')}")
            print(f"   CMS: {result.get('cms', 'Unknown')}")
            print(f"   URLs найдено: {result.get('urls_found', 0)}")
            print(f"   Страниц обработано: {result.get('pages_crawled', 0)}")
            print(f"   Категорий заполнено: {result.get('categories_filled', 0)}/{result.get('total_categories', 16)}")
            if result.get('total_fields', 0) > 0:
                percentage = int(result.get('fields_filled', 0) / result.get('total_fields', 1) * 100)
                print(f"   Полей заполнено: {result.get('fields_filled', 0)}/{result.get('total_fields', 0)} ({percentage}%)")
            print()
        
        # Средние значения
        avg_urls = sum(r.get('urls_found', 0) for r in successful) / len(successful)
        avg_pages = sum(r.get('pages_crawled', 0) for r in successful) / len(successful)
        avg_categories = sum(r.get('categories_filled', 0) for r in successful) / len(successful)
        avg_fields = sum(r.get('fields_filled', 0) for r in successful) / len(successful)
        total_fields_avg = sum(r.get('total_fields', 0) for r in successful) / len(successful)
        
        print(f"📊 Средние значения:")
        print(f"   URLs найдено: {avg_urls:.1f}")
        print(f"   Страниц обработано: {avg_pages:.1f}")
        print(f"   Категорий заполнено: {avg_categories:.1f}/16")
        if total_fields_avg > 0:
            avg_percentage = int(avg_fields / total_fields_avg * 100)
            print(f"   Полей заполнено: {avg_fields:.1f}/{total_fields_avg:.1f} ({avg_percentage}%)")
    
    print(f"\n✅ Тестирование завершено!")
    print(f"📄 Результаты сохранены в: {RESULTS_FILE}")

if __name__ == "__main__":
    main()

