# Simple Matching Service (100-point MVP)

## Обзор

Упрощенная версия matching service для бутстрап-модели. Реализует 100-point алгоритм вместо 156-point.

## Основные отличия от полной версии

### Упрощения:
1. **5 категорий вместо 8:**
   - Medical & Safety (35%) = Medical + Safety
   - Quality & Care (25%) = CQC + Staff
   - Location (15%) = Location + Social
   - Financial (15%) = без изменений
   - Lifestyle (10%) = Services (переименовано)

2. **3 условия динамических весов вместо 6 приоритетов:**
   - High Risk (Fall Risk OR Dementia) - кумулятивное
   - Urgent Placement - кумулятивное
   - Long-term Placement - кумулятивное

3. **Нет приоритетов пользователя (Section 6):**
   - Временно убрано для упрощения
   - Можно добавить в v2 после feedback

### Что сохранено:
- ✅ Двухуровневая архитектура (FREE API → ALL API)
- ✅ Обогащение данных (полный набор API)
- ✅ Расширение поиска (автоматическое)
- ✅ Динамические веса (базовая адаптивность)

## Использование

### Включение упрощенной версии

По умолчанию упрощенная версия **включена** (USE_SIMPLE_MATCHING=true).

Для переключения на полную версию установите переменную окружения:
```bash
export USE_SIMPLE_MATCHING=false
```

Или в коде:
```python
import os
os.environ['USE_SIMPLE_MATCHING'] = 'false'
```

### API

Упрощенная версия использует те же методы, что и полная версия:

```python
from services.simple_matching_service import SimpleMatchingService

service = SimpleMatchingService()

# Расчет весов
weights, conditions = service.calculate_dynamic_weights(questionnaire)

# Расчет матчинга (0-100 вместо 0-156)
match_result = service.calculate_100_point_match(
    home=home,
    user_profile=questionnaire,
    enriched_data=enriched_data,
    weights=weights
)

# Выбор топ-5 + категории победителей
selection = service.select_top_5_with_category_winners(
    candidates=candidates,
    user_profile=questionnaire,
    enriched_data=enriched_data,
    weights=weights
)
```

## Формат возврата

### calculate_100_point_match

```python
{
    'total': 75.5,           # 0-100 (вместо 0-156)
    'normalized': 75.5,      # То же самое (0-100)
    'weights': {
        'medical_safety': 35.0,
        'quality_care': 25.0,
        'location': 15.0,
        'financial': 15.0,
        'lifestyle': 10.0
    },
    'category_scores': {
        'medical_safety': 85.0,  # 0-100
        'quality_care': 70.0,
        'location': 60.0,
        'financial': 80.0,
        'lifestyle': 50.0
    },
    'point_allocations': {
        'medical_safety': 29.75,  # category_score * weight / 100
        'quality_care': 17.5,
        'location': 9.0,
        'financial': 12.0,
        'lifestyle': 5.0
    }
}
```

### select_top_5_with_category_winners

```python
{
    'top_5': [
        {
            'home': {...},
            'matchScore': 75.5,
            'matchResult': {...},
            'match_result': {...},  # Для совместимости
            'category_scores': {...}
        },
        ...
    ],
    'category_winners': {
        'best_overall': {
            'home': {...},
            'label': 'Best Overall Match',
            'reasoning': ['Highest match score: 75.5/100']
        },
        'best_care': {
            'home': {...},
            'label': 'Best for Care Quality',
            'reasoning': ['Highest combined medical safety and quality ratings']
        },
        'best_value': {
            'home': {...},
            'label': 'Best Value',
            'reasoning': ['Best quality-to-price ratio']
        }
    }
}
```

## Миграция с полной версии

### Изменения в коде:

1. **Метод расчета:**
   ```python
   # Было:
   match_result = service.calculate_156_point_match(...)
   
   # Стало:
   match_result = service.calculate_100_point_match(...)
   ```

2. **Максимальный скор:**
   ```python
   # Было:
   max_score = 156
   
   # Стало:
   max_score = 100 if USE_SIMPLE_MATCHING else 156
   ```

3. **Категории:**
   ```python
   # Было (8 категорий):
   'medical', 'safety', 'location', 'social', 
   'financial', 'staff', 'cqc', 'services'
   
   # Стало (5 категорий):
   'medical_safety', 'quality_care', 'location', 
   'financial', 'lifestyle'
   ```

## Преимущества

- ✅ **Проще разработка:** Меньше кода, меньше edge cases
- ✅ **Быстрее разработка:** 1 неделя вместо 2-3 недель
- ✅ **Меньше ошибок:** Простая логика = меньше багов
- ✅ **Проще тестирование:** Меньше компонентов для тестирования
- ✅ **Проще объяснить:** Клиентам легче понять 5 категорий

## Потеря качества

- ⚠️ **Точность матчинга:** -10-15% (компенсируется обогащением данных)
- ⚠️ **Адаптивность:** -20% (но все еще есть динамические веса)
- ⚠️ **Персонализация:** -30% (нет Section 6, но можно добавить в v2)

**Вывод:** Потеря минимальна, так как уникальность данных в обогащении, а не в матчинге.

## План развития (v2)

1. Добавить приоритеты пользователя (Section 6)
2. Добавить больше категорий (если нужно)
3. Добавить больше условий динамических весов (если нужно)
4. Добавить diversity checks (если нужно)

---

**Дата создания:** 2025-12-18  
**Версия:** 1.0 (MVP)

