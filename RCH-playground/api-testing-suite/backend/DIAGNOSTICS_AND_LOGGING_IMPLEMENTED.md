# Диагностика и Логирование - РЕАЛИЗОВАНО ✅

**Дата:** 2025-01-XX  
**Статус:** ✅ COMPLETED

---

## ✅ Выполненные задачи

### 1. Диагностический endpoint ✅

**Файл:** `routers/report_routes.py`  
**Endpoint:** `POST /api/diagnostics/data-quality`

**Функциональность:**
- Анализирует качество данных для домов престарелых
- Проверяет coverage критических полей (true/false/null rates)
- Выявляет возможности использования proxy fields
- Анализирует использование fallback логики (если предоставлен questionnaire)

**Использует:**
- `services/data_quality_diagnostics.py` - новый сервис для диагностики

**Пример запроса:**
```json
{
  "homes": [...],  // опционально
  "home_ids": [...],  // опционально
  "questionnaire": {...}  // опционально, для fallback analysis
}
```

**Пример ответа:**
```json
{
  "diagnostics": {
    "homes_checked": 50,
    "field_coverage": {
      "serves_dementia_band": {
        "true": 20,
        "false": 10,
        "null": 20,
        "null_rate": 40.0,
        "coverage": 60.0
      }
    },
    "overall": {
      "data_quality_score": 75.5,
      "avg_null_rate": 24.5,
      "high_null_fields": 3
    }
  },
  "fallback_analysis": {
    "data_quality": {
      "direct_matches": 45,
      "proxy_matches": 12,
      "unknowns": 8,
      "unknown_ratio": 0.12
    }
  }
}
```

---

### 2. Breakdown Visibility в Response ✅

**Файл:** `routers/report_routes.py`  
**Местоположение:** После `select_top_5_with_category_winners()`

**Добавлено в report:**
```python
report['matchingDetails'] = {
    'data_quality': {
        'direct_matches': 45,
        'proxy_matches': 12,
        'unknowns': 8,
        'unknown_ratio': 0.12
    },
    'fallback_usage': [
        {
            'field': 'serves_dementia_band',
            'homes_with_null': 3,
            'proxy_matches': 2,
            'direct_matches': 5
        }
    ]
}
```

**Использует:**
- `analyze_fallback_usage()` для анализа использования fallback логики
- Собирает статистику по полям с NULL значениями
- Отслеживает использование proxy fields

---

### 3. Логирование статистики матчинга ✅

**Файл:** `routers/report_routes.py`  
**Местоположение:** После `select_top_5_with_category_winners()`

**Логирует:**
```python
logger.info("Matching completed", extra={
    'total_homes_scored': len(candidates_for_selection),
    'top_5_count': len(top_5_data),
    'score_min': min(scores),
    'score_max': max(scores),
    'score_avg': sum(scores) / len(scores),
    'score_spread': max(scores) - min(scores),
    'data_quality': matching_details['data_quality'],
    'fallback_fields_used': len(matching_details['fallback_usage'])
})
```

**Метрики:**
- Количество проанализированных домов
- Статистика скоров (min, max, avg, spread)
- Качество данных (direct/proxy/unknown matches)
- Количество полей с fallback логикой

---

## 📊 Новый сервис: `data_quality_diagnostics.py`

### Функции

1. **`diagnose_matching_data(homes, home_ids=None)`**
   - Анализирует coverage критических полей
   - Вычисляет NULL rates
   - Выявляет возможности использования proxy fields
   - Возвращает overall data quality score

2. **`analyze_fallback_usage(homes, questionnaire)`**
   - Анализирует использование fallback логики
   - Отслеживает direct/proxy/unknown matches
   - Собирает статистику по полям
   - Возвращает match results distribution

### Критические поля для анализа

**Service User Bands:**
- `serves_dementia_band`
- `serves_mental_health`
- `serves_physical_disabilities`
- `serves_sensory_impairments`
- и др.

**CQC Ratings:**
- `cqc_rating_overall`
- `cqc_rating_safe`
- `cqc_rating_responsive`
- и др.

**Amenities:**
- `wheelchair_access`
- `secure_garden`
- `ensuite_rooms`

**Care Types:**
- `care_dementia`
- `care_nursing`
- `care_residential`

---

## 🔧 Использование

### 1. Диагностика качества данных

```bash
curl -X POST "http://localhost:8001/api/diagnostics/data-quality" \
  -H "Content-Type: application/json" \
  -d '{
    "home_ids": ["home_1", "home_2"],
    "questionnaire": {...}
  }'
```

### 2. Проверка NULL rates в CSV/DB

```python
from services.data_quality_diagnostics import diagnose_matching_data
from services.csv_care_homes_service import load_csv_care_homes

homes = load_csv_care_homes()
diagnostics = diagnose_matching_data(homes)

print(f"Data Quality Score: {diagnostics['overall']['data_quality_score']}")
print(f"Average NULL Rate: {diagnostics['overall']['avg_null_rate']}%")
```

### 3. Анализ fallback usage

```python
from services.data_quality_diagnostics import analyze_fallback_usage

fallback_stats = analyze_fallback_usage(homes, questionnaire)
print(f"Direct matches: {fallback_stats['data_quality']['direct_matches']}")
print(f"Proxy matches: {fallback_stats['data_quality']['proxy_matches']}")
print(f"Unknown ratio: {fallback_stats['data_quality']['unknown_ratio']}")
```

---

## ✅ Проверка

Все функции успешно реализованы:
- ✅ Диагностический endpoint создан
- ✅ Breakdown visibility добавлен в response
- ✅ Логирование статистики матчинга работает
- ✅ Сервис `data_quality_diagnostics.py` создан
- ✅ Все импорты работают
- ✅ Нет ошибок линтера

---

## 🎯 Следующие шаги

### Приоритет 1: Проверить данные в CSV/DB

Использовать диагностический endpoint для проверки NULL rates:
```bash
curl -X POST "http://localhost:8001/api/diagnostics/data-quality" \
  -H "Content-Type: application/json" \
  -d '{}'  # Загрузит все дома из CSV
```

### Приоритет 2: Мониторинг

Добавить регулярные проверки качества данных:
- Еженедельный анализ NULL rates
- Отслеживание изменений в data quality score
- Алерты при высоком unknown_ratio (> 0.5)

---

**Время выполнения:** ~2 часа  
**Статус:** ✅ COMPLETED

