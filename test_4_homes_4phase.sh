#!/bin/bash

echo "=========================================="
echo "ТЕСТИРОВАНИЕ 4-ФАЗНОГО ПОДХОДА НА 4 ДОМАХ"
echo "=========================================="
echo ""

# Массив домов для тестирования
declare -a homes=(
    "Clare Court|https://www.averyhealthcare.co.uk/our-homes/clare-court"
    "Metchley Manor|https://www.careuk.com/care-homes/metchley-manor"
    "Bartley Green Lodge|https://www.sanctuary-care.co.uk/care-homes/bartley-green-lodge"
    "Inglewood|https://www.careuk.com/care-homes/inglewood"
)

results_file="test_results_4_homes_4phase.json"
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
        --max-time 600)
    
    if [ $? -eq 0 ]; then
        echo "✅ Успешно получен ответ"
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
structured = data.get('data', {}).get('structured_data', {})
completeness = data.get('data', {}).get('completeness', {})
phase0 = data.get('data', {}).get('phase0_summary', {})
map_summary = data.get('data', {}).get('map_summary', {})
crawl_summary = data.get('data', {}).get('crawl_summary', {})

print(f'📊 Метод: {data.get(\"data\", {}).get(\"extraction_method\", \"unknown\")}')
print(f'🏗️  CMS: {phase0.get(\"cms\", \"Unknown\")}')
print(f'🗺️  URLs найдено: {map_summary.get(\"total_urls_found\", 0)}')
print(f'🕷️  Страниц обработано: {crawl_summary.get(\"pages_crawled\", 0)}')
print(f'📈 Заполнено категорий: {sum(1 for v in completeness.values() if v)}/{len(completeness)}')

# Подсчет полей
total_fields = 0
filled_fields = 0
for cat, cat_data in structured.items():
    if isinstance(cat_data, dict):
        for field, value in cat_data.items():
            total_fields += 1
            if value and (isinstance(value, str) and value.strip() or isinstance(value, (list, dict)) and len(value) > 0):
                filled_fields += 1

print(f'📋 Заполнено полей: {filled_fields}/{total_fields} ({int(filled_fields/total_fields*100) if total_fields > 0 else 0}%)')
print('')
"
        
        # Сохраняем результат
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
result = {
    'name': '$name',
    'url': '$url',
    'status': 'success',
    'method': data.get('data', {}).get('extraction_method', 'unknown'),
    'cms': data.get('data', {}).get('phase0_summary', {}).get('cms', 'Unknown'),
    'urls_found': data.get('data', {}).get('map_summary', {}).get('total_urls_found', 0),
    'pages_crawled': data.get('data', {}).get('crawl_summary', {}).get('pages_crawled', 0),
    'completeness': data.get('data', {}).get('completeness', {}),
    'categories_filled': sum(1 for v in data.get('data', {}).get('completeness', {}).values() if v),
    'total_categories': len(data.get('data', {}).get('completeness', {}))
}

# Загружаем существующие результаты
with open('$results_file', 'r') as f:
    results = json.load(f)

results.append(result)

with open('$results_file', 'w') as f:
    json.dump(results, f, indent=2)
"
    else
        echo "❌ Ошибка при выполнении запроса"
        echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Ошибка: {data.get(\"detail\", \"Unknown error\")}')
except:
    print('Ошибка парсинга ответа')
"
    fi
    
    echo ""
    sleep 2  # Небольшая пауза между запросами
done

echo "=========================================="
echo "📊 ИТОГОВАЯ СТАТИСТИКА"
echo "=========================================="
echo ""

python3 << 'PYTHON_SCRIPT'
import json

with open('test_results_4_homes_4phase.json', 'r') as f:
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

# Средние значения
if results:
    avg_urls = sum(r.get('urls_found', 0) for r in results) / len(results)
    avg_pages = sum(r.get('pages_crawled', 0) for r in results) / len(results)
    avg_categories = sum(r.get('categories_filled', 0) for r in results) / len(results)
    
    print(f"📊 Средние значения:")
    print(f"   URLs найдено: {avg_urls:.1f}")
    print(f"   Страниц обработано: {avg_pages:.1f}")
    print(f"   Категорий заполнено: {avg_categories:.1f}/16")
PYTHON_SCRIPT

echo ""
echo "✅ Тестирование завершено!"
echo "📄 Результаты сохранены в: $results_file"

