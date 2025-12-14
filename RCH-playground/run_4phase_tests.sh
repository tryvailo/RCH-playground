#!/bin/bash

echo "=========================================="
echo "ТЕСТИРОВАНИЕ 4-ФАЗНОГО ПОДХОДА"
echo "=========================================="
echo ""

# Дома для тестирования
declare -a homes=(
    "Clare Court|https://www.averyhealthcare.co.uk/our-homes/clare-court"
    "Metchley Manor|https://www.careuk.com/care-homes/metchley-manor"
    "Bartley Green Lodge|https://www.sanctuary-care.co.uk/care-homes/bartley-green-lodge"
    "Inglewood|https://www.careuk.com/care-homes/inglewood"
)

results_file="test_results_4phase_$(date +%Y%m%d_%H%M%S).json"
echo "[]" > "$results_file"

for home_info in "${homes[@]}"; do
    IFS='|' read -r name url <<< "$home_info"
    
    echo "=========================================="
    echo "🏠 Тестирование: $name"
    echo "🌐 URL: $url"
    echo "=========================================="
    
    response=$(curl -s -X POST http://localhost:8000/api/firecrawl/analyze \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$url\", \"care_home_name\": \"$name\"}" \
        --max-time 600 2>&1)
    
    if echo "$response" | grep -q '"status".*"success"'; then
        echo "✅ Успешно получен ответ"
        
        # Извлекаем ключевые метрики
        method=$(echo "$response" | grep -o '"extraction_method":"[^"]*"' | cut -d'"' -f4)
        cms=$(echo "$response" | grep -o '"cms":"[^"]*"' | cut -d'"' -f4)
        urls_found=$(echo "$response" | grep -o '"total_urls_found":[0-9]*' | cut -d':' -f2)
        pages_crawled=$(echo "$response" | grep -o '"pages_crawled":[0-9]*' | cut -d':' -f2)
        
        echo "📊 Метод: ${method:-unknown}"
        echo "🏗️  CMS: ${cms:-Unknown}"
        echo "🗺️  URLs найдено: ${urls_found:-0}"
        echo "🕷️  Страниц обработано: ${pages_crawled:-0}"
        
        # Сохраняем полный ответ
        echo "$response" > "response_${name// /_}.json"
        
        # Добавляем в результаты
        echo "$response" | python3 << 'PYTHON'
import sys, json
try:
    data = json.load(sys.stdin)
    result = {
        'name': '$name',
        'url': '$url',
        'status': 'success',
        'method': data.get('data', {}).get('extraction_method', 'unknown'),
        'cms': data.get('data', {}).get('phase0_summary', {}).get('cms', 'Unknown'),
        'urls_found': data.get('data', {}).get('map_summary', {}).get('total_urls_found', 0),
        'pages_crawled': data.get('data', {}).get('crawl_summary', {}).get('pages_crawled', 0),
        'categories_filled': sum(1 for v in data.get('data', {}).get('completeness', {}).values() if v),
        'total_categories': len(data.get('data', {}).get('completeness', {}))
    }
    
    with open('$results_file', 'r') as f:
        results = json.load(f)
    results.append(result)
    with open('$results_file', 'w') as f:
        json.dump(results, f, indent=2)
except Exception as e:
    print(f"Ошибка обработки: {e}")
PYTHON
        
    else
        echo "❌ Ошибка при выполнении запроса"
        echo "$response" | head -5
    fi
    
    echo ""
    sleep 2
done

echo "=========================================="
echo "📊 ИТОГОВАЯ СТАТИСТИКА"
echo "=========================================="
echo ""

python3 << 'PYTHON'
import json, sys
try:
    with open('$results_file', 'r') as f:
        results = json.load(f)
    
    print(f"Всего протестировано: {len(results)} домов\n")
    
    for result in results:
        print(f"🏠 {result['name']}")
        print(f"   Метод: {result.get('method', 'unknown')}")
        print(f"   CMS: {result.get('cms', 'Unknown')}")
        print(f"   URLs найдено: {result.get('urls_found', 0)}")
        print(f"   Страниц обработано: {result.get('pages_crawled', 0)}")
        print(f"   Категорий заполнено: {result.get('categories_filled', 0)}/{result.get('total_categories', 16)}")
        print("")
    
    if results:
        avg_urls = sum(r.get('urls_found', 0) for r in results) / len(results)
        avg_pages = sum(r.get('pages_crawled', 0) for r in results) / len(results)
        avg_categories = sum(r.get('categories_filled', 0) for r in results) / len(results)
        
        print(f"📊 Средние значения:")
        print(f"   URLs найдено: {avg_urls:.1f}")
        print(f"   Страниц обработано: {avg_pages:.1f}")
        print(f"   Категорий заполнено: {avg_categories:.1f}/16")
except Exception as e:
    print(f"Ошибка: {e}")
PYTHON

echo ""
echo "✅ Тестирование завершено!"
echo "📄 Результаты сохранены в: $results_file"

