# Анализ проблемы: Your Priorities Match показывает нули

## Проблема
В таблице "Your Priorities Match" почти для каждого дома показывается полное отсутствие матчинга (нули). Также CQC deep dive и другие параметры почти все нули.

## Причины

### 1. Проблема с `factorScores`
- `factorScores` может быть пустым массивом или содержать нули
- `categoryScoresMap` не заполняется, если `factorScores` пустой
- В результате все приоритеты показывают 0%

### 2. Проблема с маппингом категорий
- В анкете используется старый формат `medical_safety`
- `priorityCategoryMapping` поддерживает `medical_safety`, но маппится на `['medical', 'safety']`
- Если `categoryScoresMap` пустой, то даже правильный маппинг не поможет

### 3. Проблема с данными из backend
- `category_scores` из `match_result` могут быть пустыми или нулями
- `point_allocations` могут быть пустыми
- `max_points_per_category` может быть неправильным

## Решение

### 1. Проверить, что `factorScores` правильно передаются из backend
- Убедиться, что `point_allocations` и `category_scores` не пустые
- Убедиться, что `max_points_per_category` правильный

### 2. Добавить fallback для `categoryScoresMap`
- Если `factorScores` пустой, использовать `matchResult.category_scores` напрямую
- Нормализовать `category_scores` (0-1 scale) к 0-100 scale

### 3. Добавить логирование
- Логировать `factorScores` для каждого дома
- Логировать `categoryScoresMap` после построения
- Логировать расчеты для каждого приоритета

### 4. Исправить обработку `medical_safety`
- Убедиться, что `medical_safety` правильно маппится на `['medical', 'safety']`
- Убедиться, что `categoryScoresMap` содержит `medical` и `safety`

## План исправления

1. Добавить fallback в `calculateHomeMatches` для использования `matchResult.category_scores` если `factorScores` пустой
2. Добавить логирование для диагностики
3. Проверить, что backend правильно передает `factorScores`
4. Исправить нормализацию `category_scores` (0-1 scale → 0-100 scale)

