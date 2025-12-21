# ✅ Исправление Regulated Activities

**Дата:** 2025-12-20  
**Проблема:** `regulated_activity_nursing_care` и `regulated_activity_personal_care` всегда `FALSE` в CSV, хотя данные есть в API

---

## 🔍 Проблема

### **Выявлено:**
- `regulated_activity_nursing_care`: 0.0% (всегда `FALSE`)
- `regulated_activity_personal_care`: 2.0% (почти всегда `FALSE`)
- В API данные есть: `regulatedActivities[]` содержит информацию
- Функция `extract_care_types_from_api` извлекает только `care_nursing` и `care_residential`, но НЕ `regulated_activity_*`

---

## ✅ Решение

### **1. Создана функция `extract_regulated_activities_from_api`**

Извлекает regulated activities из API и маппит их в CSV поля:

```python
def extract_regulated_activities_from_api(api_data: Dict) -> Dict[str, bool]:
    """Extract regulated activities from API response"""
    activities = {}
    
    regulated_activities = api_data.get('regulatedActivities', [])
    for activity in regulated_activities:
        activity_name = activity.get('name', '').lower()
        activity_code = activity.get('code', '').upper()
        
        # Map to CSV fields
        if 'nursing care' in activity_name or activity_code == 'RA1':
            activities['regulated_activity_nursing_care'] = True
        if 'personal care' in activity_name or activity_code == 'RA2':
            activities['regulated_activity_personal_care'] = True
        # ... другие activities
```

---

### **2. Добавлена логика обновления в `update_home_from_api`**

```python
# Extract and update regulated activities
if any(f.startswith('regulated_activity_') for f in fields_to_update):
    regulated_activities = extract_regulated_activities_from_api(api_data)
    for field, value in regulated_activities.items():
        if field in fields_to_update:
            # Update if current value is FALSE or empty
            current_value = home.get(field)
            is_false_or_empty = (
                current_value is None or 
                current_value == '' or 
                str(current_value).strip().upper() in ['FALSE', 'F', '0', 'NONE', 'NULL', 'N/A', 'NA']
            )
            
            # Update if FALSE/empty and API says TRUE
            if is_false_or_empty and value:
                updates[field] = 'TRUE' if value else 'FALSE'
                updated_fields.append(field)
```

---

### **3. Добавлен маппинг в `save_homes_to_csv`**

```python
# Regulated Activities (direct mapping)
elif db_field.startswith('regulated_activity_'):
    # Map directly: regulated_activity_nursing_care -> regulated_activity_nursing_care
    csv_row[db_field] = value if value else 'FALSE'
```

---

## 📊 Маппинг API → CSV

| API Code | API Name | CSV Field |
|----------|----------|-----------|
| **RA1** | "Nursing care" | `regulated_activity_nursing_care` |
| **RA2** | "Accommodation for persons who require nursing or personal care" | `regulated_activity_personal_care` |
| **RA2** | "Personal care" | `regulated_activity_personal_care` |
| **RA3** | "Surgical procedures" | `regulated_activity_surgical` |
| **RA4** | "Diagnostic and screening procedures" | `regulated_activity_diagnostic` |
| **RA5** | "Treatment of disease, disorder or injury" | `regulated_activity_treatment` |

---

## 🧪 Тестирование

### **Тест 1: API с RA2 + RA5**
```python
api_data = {
    'regulatedActivities': [
        {'code': 'RA2', 'name': 'Accommodation for persons who require nursing or personal care'},
        {'code': 'RA5', 'name': 'Treatment of disease, disorder or injury'}
    ]
}
# Результат:
# regulated_activity_personal_care: True
# regulated_activity_treatment: True
```

### **Тест 2: API с RA1 + RA2**
```python
api_data = {
    'regulatedActivities': [
        {'code': 'RA1', 'name': 'Nursing care'},
        {'code': 'RA2', 'name': 'Personal care'}
    ]
}
# Результат:
# regulated_activity_nursing_care: True
# regulated_activity_personal_care: True
```

---

## ⏭️ Следующие шаги

1. ✅ Функция извлечения создана
2. ✅ Логика обновления добавлена
3. ✅ Маппинг в CSV добавлен
4. ⚠️ Протестировать на небольшой выборке (20 домов)
5. ⚠️ Запустить полное обновление для всех домов

---

**Статус:** ✅ ИСПРАВЛЕНО

