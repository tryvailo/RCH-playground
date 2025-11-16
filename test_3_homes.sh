#!/bin/bash

echo "=========================================="
echo "ТЕСТИРОВАНИЕ РАСШИРЕННОЙ СХЕМЫ НА 3 ДОМАХ"
echo "=========================================="
echo ""

# Массив домов для тестирования
declare -a homes=(
    "Clare Court|https://www.averyhealthcare.co.uk/our-homes/clare-court"
    "Metchley Manor|https://www.careuk.com/care-homes/metchley-manor"
    "Bartley Green Lodge|https://www.sanctuary-care.co.uk/care-homes/bartley-green-lodge"
)

results_file="test_results_3_homes.json"
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
        --max-time 300)
    
    if [ $? -eq 0 ]; then
        echo "✅ Успешно получен ответ"
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
structured = data.get('data', {}).get('structured_data', {})
completeness = data.get('data', {}).get('completeness', {})

print(f'📊 Метод: {data.get(\"data\", {}).get(\"extraction_method\", \"unknown\")}')
print(f'📈 Заполнено категорий: {sum(1 for v in completeness.values() if v)}/{len(completeness)}')

# Подсчет полей
total_fields = 0
filled_fields = 0
for cat, cat_data in structured.items():
    if isinstance(cat_data, dict):
        for k, v in cat_data.items():
            total_fields += 1
            if v:
                if isinstance(v, list) and v:
                    filled_fields += 1
                elif isinstance(v, dict) and v:
                    filled_fields += 1
                elif v:
                    filled_fields += 1
    elif cat_data:
        total_fields += 1
        filled_fields += 1

print(f'📋 Заполнено полей: {filled_fields}/{total_fields} ({int(filled_fields/total_fields*100) if total_fields > 0 else 0}%)')
print()

# Топ-5 категорий с наибольшим количеством данных
categories_with_data = []
for cat, cat_data in structured.items():
    if isinstance(cat_data, dict):
        count = sum(1 for v in cat_data.values() if v)
        if count > 0:
            categories_with_data.append((cat, count))
    elif cat_data:
        categories_with_data.append((cat, 1))

categories_with_data.sort(key=lambda x: x[1], reverse=True)
print('🏆 Топ-5 категорий по количеству данных:')
for i, (cat, count) in enumerate(categories_with_data[:5], 1):
    print(f'   {i}. {cat.title()}: {count} полей')
"
        
        # Сохраняем результат
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = json.load(open('$results_file'))
results.append({
    'name': '$name',
    'url': '$url',
    'status': data.get('status'),
    'method': data.get('data', {}).get('extraction_method'),
    'completeness': data.get('data', {}).get('completeness', {}),
    'categories_filled': sum(1 for v in data.get('data', {}).get('completeness', {}).values() if v),
    'total_categories': len(data.get('data', {}).get('completeness', {}))
})
json.dump(results, open('$results_file', 'w'), indent=2)
"
    else
        echo "❌ Ошибка при запросе"
    fi
    
    echo ""
    sleep 2
done

echo "=========================================="
echo "📊 ИТОГОВАЯ СТАТИСТИКА"
echo "=========================================="
python3 << 'PYTHON'
import json

with open('test_results_3_homes.json', 'r') as f:
    results = json.load(f)

print(f"Всего протестировано: {len(results)} домов")
print()

for result in results:
    name = result['name']
    filled = result['categories_filled']
    total = result['total_categories']
    percentage = int(filled/total*100) if total > 0 else 0
    
    print(f"🏠 {name}:")
    print(f"   Заполнено категорий: {filled}/{total} ({percentage}%)")
    print(f"   Метод: {result['method']}")
    print()

# Средняя статистика
avg_filled = sum(r['categories_filled'] for r in results) / len(results)
avg_total = sum(r['total_categories'] for r in results) / len(results)
avg_percentage = int(avg_filled/avg_total*100) if avg_total > 0 else 0

print(f"📈 Средние показатели:")
print(f"   Заполнено категорий: {avg_filled:.1f}/{avg_total:.0f} ({avg_percentage}%)")
PYTHON

