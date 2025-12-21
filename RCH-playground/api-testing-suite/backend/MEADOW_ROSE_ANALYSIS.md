# Детальный анализ: Meadow Rose Nursing Home

## Результаты анализа

### 1. Базовая информация
- **Название**: Meadow Rose Nursing Home
- **ID**: 1-1004508435
- **CQC Location ID**: 1-1004508435
- **Провайдер**: MACC Care Limited
- **Адрес**: Birmingham, B31 2TX
- **Координаты**: 52.400451, -1.987400

### 2. Общий матч-скор
- **Общий скор**: 58.00 / 156 (37.00%)
- **Нормализованный скор**: 37.00%

### 3. Category Scores (0-1 scale)

| Категория | Скор | Оценка |
|-----------|------|--------|
| Medical Capabilities | 0.3667 | Низкий |
| Safety Quality | 0.3400 | Низкий |
| Location Access | 0.3333 | Низкий |
| Cultural & Social | 0.1667 | Очень низкий |
| Financial Stability | 0.7500 | Высокий |
| Staff Quality | 0.2500 | Низкий |
| CQC Compliance | 0.4500 | Средний |
| Additional Services | 0.0000 | Отсутствует |

### 4. Point Allocations

| Категория | Баллы | Макс | % |
|-----------|-------|------|---|
| Medical | 18.42 | 30.0 | 61.4% |
| Safety | 11.83 | 25.0 | 47.3% |
| Location | 2.55 | 15.0 | 17.0% |
| Social | 1.61 | 15.0 | 10.7% |
| Financial | 12.40 | 20.0 | 62.0% |
| Staff | 4.13 | 20.0 | 20.7% |
| CQC | 7.44 | 20.0 | 37.2% |
| Services | 0.00 | 11.0 | 0.0% |

### 5. Динамические веса

**Базовые веса (после dementia adjustment):**
- Medical: 25.70%
- Safety: 17.80%
- Location: 7.90%
- Social: 9.90%
- Financial: 12.90%
- Staff: 13.90%
- CQC: 9.90%
- Services: 2.00%

**Веса после применения приоритетов пользователя:**
- Medical: 32.20% ⬆️
- Safety: 22.30% ⬆️
- Location: 4.90% ⬇️
- Social: 6.20% ⬇️
- Financial: 10.60% ⬇️
- Staff: 10.60% ⬇️
- CQC: 10.60% ⬆️
- Services: 2.50% ⬆️

### 6. Критические проблемы

#### 6.1 Несоответствие типу ухода
- **Анкета требует**: `specialised_dementia` care
- **Дом предоставляет**: `care_dementia: False` ❌
- **Влияние**: Medical Capabilities = 0.3667 (низкий скор)

#### 6.2 CQC Rating
- **Overall**: "Requires improvement" ⚠️
- **Safe**: "Requires improvement" ⚠️
- **Effective**: "Requires improvement" ⚠️
- **Caring**: "Good" ✅
- **Responsive**: "Good" ✅
- **Well-led**: "Requires improvement" ⚠️
- **Влияние**: CQC Compliance = 0.4500 (средний скор)

#### 6.3 Отсутствие дополнительных услуг
- **Services**: 0.0000 ❌
- **Влияние**: Нет дополнительных услуг (physiotherapy, mental health, etc.)

#### 6.4 Низкий Social скор
- **Social**: 0.1667 (очень низкий)
- **Влияние**: Недостаточно социальных активностей

### 7. Положительные моменты

#### 7.1 Financial Stability
- **Скор**: 0.7500 (высокий)
- **Причина**: Данные из CSV показывают стабильность

#### 7.2 CQC Caring & Responsive
- **Caring**: "Good" ✅
- **Responsive**: "Good" ✅

### 8. Отсутствующие данные от API

Для полного анализа нужны данные от:
- ❌ CQC API (location_id: 1-1004508435) - для inspection history, enforcement actions
- ❌ Companies House (name: Meadow Rose Nursing Home) - для financial stability
- ❌ Google Places (name: Meadow Rose Nursing Home) - для reviews, sentiment
- ❌ FSA (name: Meadow Rose Nursing Home) - для food hygiene rating
- ❌ Staff Quality (location_id: 1-1004508435) - для staff quality score

### 9. Рекомендации

1. **НЕ рекомендуется** для клиента с деменцией, так как `care_dementia: False`
2. **CQC Rating** "Requires improvement" - требует дополнительной проверки
3. **Services = 0** - нет дополнительных услуг
4. **Social скор очень низкий** - недостаточно социальных активностей

### 10. Вывод

**Meadow Rose Nursing Home** получил низкий общий скор (37%) из-за:
- Несоответствия типу ухода (нет dementia care)
- Низких CQC рейтингов
- Отсутствия дополнительных услуг
- Низкого социального скора

**Рекомендация**: Не подходит для клиента с деменцией из первой анкеты.

