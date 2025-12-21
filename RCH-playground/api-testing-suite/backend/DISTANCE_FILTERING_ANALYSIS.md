# Анализ фильтрации по расстоянию

## Проблемы в текущей реализации

### 1. Отсутствует автоматическое расширение радиуса ДО загрузки домов

**ТЗ требует (STEP 2):**
- Расчет расстояния для ВСЕХ домов
- Сортировка по расстоянию
- Фильтрация по preferred_radius
- **Автоматическое расширение**, если недостаточно домов (MIN_REQUIRED = 5)
- EXPANSION_STEPS = [5, 10, 15, 30, 50, 75, 100]

**Текущая реализация:**
- `get_csv_care_homes` фильтрует по `max_distance_km`, но НЕ расширяет автоматически
- В `report_routes.py` есть логика расширения, но она работает ПОСЛЕ скоринга (если низкие матчинги)
- Нет проверки на MIN_REQUIRED = 5 домов ДО загрузки

### 2. Расстояние рассчитывается, но не всегда сохраняется

**ТЗ требует:**
- `distance_km` должен быть в каждом доме для скоринга Location

**Текущая реализация:**
- `get_csv_care_homes` рассчитывает `distance_km` для всех домов (✅)
- Но если домов недостаточно и происходит расширение, расстояние может не пересчитываться

### 3. Несоответствие логики расширения

**ТЗ:**
- Расширение ДО скоринга (если недостаточно домов для фильтрации)

**Текущая реализация:**
- Расширение ПОСЛЕ скоринга (если низкие матчинги)

## Рекомендации по исправлению

### Вариант 1: Модифицировать `get_csv_care_homes` (предпочтительно)

Добавить логику автоматического расширения в `get_csv_care_homes`:

```python
def get_care_homes(
    ...,
    max_distance_km: Optional[float] = None,
    min_required: int = 5,  # NEW: минимальное количество домов
    auto_expand: bool = True  # NEW: автоматическое расширение
) -> List[Dict]:
    """
    Load care homes with automatic radius expansion if needed.
    """
    # 1. Загрузить все дома
    all_homes = load_csv_care_homes()
    
    # 2. Рассчитать расстояние для всех
    if user_lat and user_lon:
        for h in all_homes:
            distance = _calculate_distance_km(...)
            h['distance_km'] = distance
    
    # 3. Сортировать по расстоянию
    all_homes.sort(key=lambda h: h.get('distance_km', 9999))
    
    # 4. Попробовать preferred_radius
    preferred_radius = max_distance_km or 100.0
    in_preferred = [h for h in all_homes if h.get('distance_km', 9999) <= preferred_radius]
    
    # 5. Автоматическое расширение, если недостаточно
    if auto_expand and len(in_preferred) < min_required:
        EXPANSION_STEPS = [5, 10, 15, 30, 50, 75, 100]
        expanded_radius = preferred_radius
        
        for step in EXPANSION_STEPS:
            if step > preferred_radius:
                expanded_radius = step
                in_expanded = [h for h in all_homes if h.get('distance_km', 9999) <= expanded_radius]
                if len(in_expanded) >= min_required:
                    return in_expanded[:limit] if limit else in_expanded
        
        # Если даже после расширения недостаточно, вернуть все что есть
        return in_expanded[:limit] if limit else in_expanded
    
    # 6. Вернуть отфильтрованные дома
    return in_preferred[:limit] if limit else in_preferred
```

### Вариант 2: Добавить логику в `report_routes.py`

Добавить проверку и расширение ДО вызова `get_csv_care_homes`:

```python
# STEP 1: Попробовать загрузить с preferred_radius
care_homes = get_csv_care_homes(..., max_distance_km=initial_max_distance_km)

# STEP 2: Проверить, достаточно ли домов
MIN_REQUIRED = 5
if len(care_homes) < MIN_REQUIRED:
    # Расширить радиус
    EXPANSION_STEPS = [5, 10, 15, 30, 50, 75, 100]
    for step in EXPANSION_STEPS:
        if step > initial_max_distance_km:
            expanded_homes = get_csv_care_homes(..., max_distance_km=step)
            if len(expanded_homes) >= MIN_REQUIRED:
                care_homes = expanded_homes
                max_distance_km = step
                break
```

## Выбранное решение

**Вариант 1** (модификация `get_csv_care_homes`) - предпочтительнее, так как:
- Логика инкапсулирована в одном месте
- Переиспользуется для Free Report и Professional Report
- Соответствует ТЗ (STEP 2)

