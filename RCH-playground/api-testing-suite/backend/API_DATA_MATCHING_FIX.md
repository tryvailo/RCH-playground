# Исправление: API данные (FSA, CQC, Staff Quality) не влияют на матчинг

## Проблема

API обогащение (FSA, CQC, Staff Quality) происходило **ПОСЛЕ** выбора TOP 5, поэтому эти данные не использовались при расчете матч-скора. В результате:

1. **FSA данные** не влияли на Safety Quality скор
2. **CQC данные** не влияли на CQC Compliance и Safety Quality скоры
3. **Staff Quality данные** не влияли на Staff Quality скор
4. **Financial данные** не влияли на Financial Stability скор

## Решение

### 1. Получение API данных ДО выбора TOP 5

Добавлен новый этап **"API ENRICHMENT FOR MATCHING (BEFORE TOP 5 SELECTION)"**, который:

1. Выбирает топ-30 кандидатов после первоначального скоринга
2. Получает данные от всех API источников параллельно:
   - **CQC API** - для inspection history, enforcement actions, detailed ratings
   - **FSA API** - для food hygiene ratings
   - **Staff Quality API** - для staff quality scores
   - **Companies House API** - для financial stability
3. Пересчитывает скоры с API данными
4. Использует пересчитанные скоры для выбора TOP 5

### 2. Структура enriched_data

Данные структурированы для использования в matching service:

```python
enriched_data = {
    'cqc_detailed': {
        'overall_rating': '...',
        'safe_rating': '...',
        'effective_rating': '...',
        # ... другие рейтинги
        'historical_ratings': [...],
        'enforcement_actions': [...]
    },
    'fsa_scoring': {
        'rating_value': 5,
        'fsa_points': 7,
        'health_score': 100
    },
    'fsa_detailed': {
        'rating': 5,
        'rating_date': '...',
        'trend_analysis': {...}
    },
    'staff_quality': {
        'staff_quality_score': {
            'overall_score': 85,
            'category': 'GOOD',
            'components': {...}
        }
    },
    'staff_data': {
        # Components extracted for matching
    },
    'companies_house_scoring': 75,
    'financial_data': {
        'altman_z_score': 2.5,
        'director_stability': 0.9,
        # ... другие финансовые метрики
    }
}
```

### 3. Использование в Matching Service

Matching service уже правильно использует `enriched_data`:

- **`_calculate_safety_quality`**: Использует `cqc_detailed` и `fsa_scoring`
- **`_calculate_cqc_compliance`**: Использует `cqc_detailed`
- **`_calculate_staff_quality`**: Использует `staff_quality` и `staff_data`
- **`_calculate_financial_stability`**: Использует `companies_house_scoring` и `financial_data`

### 4. Логирование

Добавлено логирование для диагностики:

- Показывает, какие API данные получены для каждого дома
- Показывает изменение скора после использования API данных
- Показывает, сколько домов было пересчитано

## Порядок выполнения

### БЫЛО (неправильно):
1. Загрузка домов
2. Скоринг с базовыми данными (только DB/CSV)
3. Выбор TOP 5
4. **API обогащение для TOP 5** ❌ (слишком поздно!)

### СТАЛО (правильно):
1. Загрузка домов
2. Скоринг с базовыми данными (только DB/CSV)
3. **API обогащение для топ-30 кандидатов** ✅
4. Пересчет скора с API данными
5. Выбор TOP 5 (с правильными скорами)
6. Дополнительное API обогащение для финального отчета (детальные данные)

## Результат

Теперь API данные:
- ✅ Используются при расчете матч-скора
- ✅ Влияют на выбор TOP 5
- ✅ Улучшают точность матчинга
- ✅ Логируются для диагностики

## Пример

### До исправления:
```
Home: Meadow Rose
- Initial score: 58/156 (37%)
- CQC: "Requires improvement" (не используется в матчинге)
- FSA: Нет данных (не используется в матчинге)
- Staff: Нет данных (не используется в матчинге)
```

### После исправления:
```
Home: Meadow Rose
- Initial score: 58/156 (37%)
- API enrichment: CQC=✅, FSA=✅, Staff=❌, Financial=❌
- Re-scored with API: 62/156 (39.7%) (+4 points)
- CQC data влияет на Safety и CQC Compliance скоры
- FSA data влияет на Safety скор
```

