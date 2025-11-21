# Чеклист верификации Professional Report для LLM

**Версия:** 1.0  
**Дата:** 2025-01-XX  
**Назначение:** Детальный чеклист для проверки корректности Professional Report после изменений

---

## 🔴 КРИТИЧЕСКИЕ ПРОВЕРКИ (Блокирующие)

### 1. Backend: Обработка None значений

#### 1.1 Проверка всех числовых сравнений во всех сервисах
- [ ] **professional_matching_service.py**
  - [ ] `_calculate_medical_capabilities()` - проверка `rn_count`, `incidents`, `emergency_response_time`
  - [ ] `_calculate_safety_quality()` - проверка `fsa_rating`, `incidents`
  - [ ] `_calculate_location_access()` - проверка `distance_miles`, `bus_stop_distance`, `train_station_distance`
  - [ ] `_calculate_cultural_social()` - проверка `review_count`, `dwell_time`, `repeat_visitor_rate`, `community_integration_score`
  - [ ] `_calculate_financial_stability()` - проверка `net_margin`, `current_ratio`, `altman_z`
  - [ ] `_calculate_staff_quality()` - проверка `glassdoor_rating`, `avg_tenure_years`, `turnover_rate`
  - [ ] `calculate_156_point_match()` - проверка `category_scores`, `weights_dict`, `point_allocations`, `normalized`

- [ ] **funding_optimization_service.py**
  - [ ] `calculate_la_funding_availability()` - проверка `estimated_assets`, `estimated_income`, `property_value`
  - [ ] `calculate_dpa_considerations()` - проверка `property_value`, `outstanding_mortgage`, `estimated_weekly_care_cost`
  - [ ] `calculate_five_year_projections()` - проверка `eligibility_probability`, `dpa_payment_5yr`, `available_deferral`
  - [ ] `_recommend_funding_scenario()` - проверка `eligibility_probability`
  - [ ] `_calculate_funding_summary()` - проверка `eligibility_probability`
  - [ ] `_calculate_dpa_projections()` - проверка `available_deferral`, `interest_rate`, `admin_fee_annual`

- [ ] **red_flags_service.py**
  - [ ] `_assess_financial_stability_warnings()` - проверка `altman_z`, `bankruptcy_risk`, `revenues`, `margins`
  - [ ] `_assess_staff_turnover_concerns()` - проверка `turnover_rate`, `avg_tenure`, `glassdoor_rating`, `job_listings_count`
  - [ ] `_assess_pricing_increases_history()` - проверка `prices` из `pricing_history`

- [ ] **comparative_analysis_service.py**
  - [ ] `_generate_price_comparison()` - проверка `weeklyPrice` значений
  - [ ] `_identify_key_differentiators()` - проверка `weeklyPrice`, `altman_z`, `matchScore`
  - [ ] `_calculate_value_score()` - проверка `price`, `matchScore`
  - [ ] `_analyze_score_tiers()` - проверка `match_score` значений
  - [ ] `_generate_recommendation()` - проверка `top_score`, `top_price`, `score_range`, `price_range`

- [ ] **negotiation_strategy_service.py**
  - [ ] `_generate_market_rate_analysis()` - проверка `weeklyPrice`, `regional_average`, `autumna_avg`, `vs_market`, `vs_uk`
  - [ ] `_get_price_positioning()` - проверка `vs_market_percent`
  - [ ] `_assess_negotiation_potential()` - проверка `vs_market_percent`, `match_score`
  - [ ] `_identify_priority_questions()` - проверка `turnover_rate_percent`, `bankruptcy_risk_score`
  - [ ] `_identify_best_value()` - проверка `match_score`, `regional_average`, `value_score`
  - [ ] `_generate_market_insights()` - проверка `prices`, `avg_price`, `price_range`

- [ ] **financial_enrichment_service.py**
  - [ ] `_calculate_three_year_summary()` - проверка `revenues`, `margins`, `working_capitals`
  - [ ] Проверка `rev0`, `rev_last`, `margin0`, `margin_last`, `wc0`, `wc_last`

- [ ] **staff_enrichment_service.py**
  - [ ] `_calculate_overall_turnover_estimate()` - проверка `active_listings`, `staff_count`
  - [ ] `_assess_combined_data_quality()` - проверка `job_boards_count`

- [ ] **google_places_enrichment_service.py**
  - [ ] `_analyze_sentiment_simple()` - проверка `average_sentiment`

- [ ] **fsa_enrichment_service.py**
  - [ ] `_score_to_label()` - проверка `hygiene_score`, `structural_score`, `management_score`
  - [ ] `_rating_to_color()` - проверка `rating_value`

- [ ] **main.py**
  - [ ] `generate_professional_report()` - проверка `match_result['point_allocations']`, `match_result['normalized']`
  - [ ] Проверка `user_lat`, `user_lon`, `home_lat`, `home_lon` перед расчетом расстояния
  - [ ] Проверка `weeklyPrice` при добавлении в `care_homes`

**Паттерн безопасного кода:**
```python
# ❌ НЕПРАВИЛЬНО:
if value > 0:  # TypeError если value is None

# ✅ ПРАВИЛЬНО:
try:
    value_float = float(value) if value is not None else 0.0
except (ValueError, TypeError):
    value_float = 0.0
if value_float > 0:
```

#### 1.2 Проверка безопасного преобразования строк в числа
- [ ] **Проверить использование `_safe_float_convert()` во всех сервисах**
  - [ ] `negotiation_strategy_service.py` - для всех цен
  - [ ] `comparative_analysis_service.py` - для всех цен и scores
  - [ ] `main.py` - для `weeklyPrice`
  
**Паттерн безопасного кода:**
```python
# ❌ НЕПРАВИЛЬНО:
price = float(home.get('weekly_cost'))  # ValueError если "Waived fees or 2"

# ✅ ПРАВИЛЬНО:
price = _safe_float_convert(home.get('weekly_cost'))
if price and price > 0:
    # use price
```

#### 1.3 Проверка обработки отсутствующих полей
- [ ] **Проверить все обращения к вложенным словарям во всех сервисах**
  - [ ] Использование `.get()` вместо прямого доступа `['key']`
  - [ ] Дефолтные значения для всех опциональных полей
  - [ ] Проверка `is not None` перед использованием значений
  - [ ] Проверка существования списков перед `len()` и индексацией

---

### 2. Frontend: Обработка null/undefined значений

#### 2.1 Проверка вызовов методов на потенциально null объектах
- [ ] **ProfessionalReportViewer.tsx**
  - [ ] Все вызовы `.replace()` - использовать `value?.replace() || value || 'N/A'`
  - [ ] Все вызовы `.toUpperCase()`, `.toLowerCase()` - использовать `value?.toUpperCase() || 'N/A'`
  - [ ] Все вызовы `.toFixed()` - проверка на `null`/`undefined` перед вызовом
  - [ ] Все вызовы `.toLocaleString()` - проверка на `null`/`undefined` перед вызовом

- [ ] **NegotiationStrategyViewer.tsx**
  - [ ] `region?.replace('_', ' ') || region || 'N/A'`
  - [ ] `care_type?.replace('_', ' ') || care_type || 'N/A'`
  - [ ] `potential?.toUpperCase() || 'N/A'`
  - [ ] `priority?.toUpperCase() || 'N/A'`
  - [ ] `category?.replace('_', ' ') || category || 'N/A'`

- [ ] **Все компоненты с графиками**
  - [ ] Проверка данных перед передачей в графики
  - [ ] Fallback для пустых данных

**Паттерн безопасного кода:**
```typescript
// ❌ НЕПРАВИЛЬНО:
{value.replace('_', ' ')}  // TypeError если value is null

// ✅ ПРАВИЛЬНО:
{value?.replace('_', ' ') || value || 'N/A'}
```

#### 2.2 Проверка доступа к вложенным свойствам
- [ ] **Проверить все обращения к вложенным объектам**
  - [ ] `home.cqcDeepDive?.trend || 'NA'`
  - [ ] `home.financialStability?.altman_z_score ?? 'NA'`
  - [ ] `home.googlePlaces?.rating ?? 'NA'`
  - [ ] `home.staffQuality?.turnover_rate_percent ?? 'NA'`
  - [ ] `strategy.market_rate_analysis?.region?.replace() || 'N/A'`
  - [ ] `funding.chc_eligibility?.eligibility_probability ?? 'NA'`

**Паттерн безопасного кода:**
```typescript
// ❌ НЕПРАВИЛЬНО:
{home.financialStability.altman_z_score}  // TypeError если financialStability is null

// ✅ ПРАВИЛЬНО:
{home.financialStability?.altman_z_score !== null && home.financialStability?.altman_z_score !== undefined
  ? home.financialStability.altman_z_score.toFixed(2)
  : 'NA'}
```

#### 2.3 Проверка отображения секций с отсутствующими данными
- [ ] **Убедиться, что ВСЕ секции отображаются даже при отсутствии данных**
  - [ ] **CQC Deep Dive** - всегда видна, показывает "NA" если данных нет
  - [ ] **FSA Detailed Ratings** - всегда видна, показывает "NA" если данных нет
  - [ ] **Financial Stability Analysis** - всегда видна, показывает "NA" если данных нет
  - [ ] **Google Places Insights** - всегда видна, показывает "NA" если данных нет
  - [ ] **Staff Quality** - всегда видна, показывает "NA" если данных нет
  - [ ] **Funding Optimization** - все подсекции всегда видны
  - [ ] **Comparative Analysis** - всегда видна
  - [ ] **Red Flags & Risk Assessment** - всегда видна
  - [ ] **Negotiation Strategy** - всегда видна

**Паттерн безопасного кода:**
```typescript
// ❌ НЕПРАВИЛЬНО:
{home.cqcDeepDive && (
  <div>CQC Data: {home.cqcDeepDive.trend}</div>
)}  // Секция не видна если данных нет

// ✅ ПРАВИЛЬНО:
<div>
  <h4>CQC Deep Dive</h4>
  <div>Trend: {home.cqcDeepDive?.trend || 'NA'}</div>
</div>  // Секция всегда видна
```

---

### 3. JSX структура (Frontend)

#### 3.1 Проверка структуры JSX в ProfessionalReportViewer.tsx
- [ ] **Проверить все открывающие и закрывающие теги**
  - [ ] Все `<div>` имеют соответствующие `</div>`
  - [ ] Все условные рендеринги правильно закрыты
  - [ ] Нет лишних или недостающих скобок `{}`
  - [ ] Правильное использование React Fragment `<>...</>`
  - [ ] Правильная вложенность всех элементов

- [ ] **Проверить структуру условного рендеринга**
  - [ ] `{report ? (...) : (...)}` вместо `{report && (...)}`
  - [ ] Все вложенные условия правильно закрыты
  - [ ] Нет "Adjacent JSX elements" ошибок

- [ ] **Проверить структуру collapsible секций**
  - [ ] Правильное использование `useState` для `expandedHomes`
  - [ ] Правильное закрытие всех вложенных div'ов
  - [ ] Правильное использование иконок `ChevronUp`/`ChevronDown`

**Паттерн безопасного кода:**
```typescript
// ❌ НЕПРАВИЛЬНО:
{report && (
  <div>Content</div>
  <div>More content</div>  // Adjacent JSX elements error
)}

// ✅ ПРАВИЛЬНО:
{report ? (
  <>
    <div>Content</div>
    <div>More content</div>
  </>
) : null}
```

---

### 4. Валидация входных данных

#### 4.1 Проверка валидации Professional Questionnaire
- [ ] **Проверить валидацию всех 5 секций**
  - [ ] Section 1: Contact & Emergency (Q1-Q4)
  - [ ] Section 2: Location & Budget (Q5-Q7)
  - [ ] Section 3: Medical Needs (Q8-Q12)
  - [ ] Section 4: Safety & Special Needs (Q13-Q16)
  - [ ] Section 5: Timeline (Q17)

- [ ] **Проверить валидацию конкретных полей**
  - [ ] `q6_max_distance` - нормализация legacy форматов ("15km" → "within_15km")
  - [ ] `q7_budget` - проверка допустимых значений
  - [ ] `q8_care_types` - проверка массива допустимых значений
  - [ ] `q9_medical_conditions` - проверка массива допустимых значений
  - [ ] `q13_fall_history` - проверка допустимых значений

**Файлы для проверки:**
- `api-testing-suite/backend/services/professional_report_validator.py`

#### 4.2 Проверка обработки ошибок валидации
- [ ] **Проверить обработку ошибок валидации**
  - [ ] Возврат понятных сообщений об ошибках
  - [ ] HTTP статус коды (400 для валидации, 500 для серверных ошибок)
  - [ ] Логирование ошибок валидации
  - [ ] Нормализация legacy форматов без ошибок

---

## 🟡 ВАЖНЫЕ ПРОВЕРКИ (Не блокирующие, но критичные)

### 5. Форматирование чисел

#### 5.1 Проверка форматирования чисел в ответе API
- [ ] **Проверить форматирование всех числовых значений**
  - [ ] Использование `round(value, 2)` для всех `factorScores` и `matchScore`
  - [ ] Проверка, что нет значений типа `14.439360000000002`
  - [ ] Все проценты округлены до 1-2 знаков после запятой
  - [ ] Все цены округлены до 2 знаков после запятой

**Паттерн безопасного кода:**
```python
# ✅ ПРАВИЛЬНО:
'matchScore': round(float(match_result.get('normalized', 0) or 0), 2),
'score': round(float(match_result['point_allocations'].get('medical', 0) or 0), 2),
'weeklyPrice': round(weekly_price_float, 2),
```

#### 5.2 Проверка форматирования чисел во Frontend
- [ ] **Проверить отображение всех числовых значений**
  - [ ] Использование `.toFixed(2)` для отображения scores и prices
  - [ ] Проверка, что нет `undefined` или `NaN` в отображении
  - [ ] Форматирование валют (£) и процентов (%)
  - [ ] Форматирование в графиках (Recharts)

---

### 6. Структура ответа API

#### 6.1 Проверка структуры ответа Professional Report
- [ ] **Проверить структуру JSON ответа**
  - [ ] Все обязательные поля присутствуют:
    - [ ] `reportId`, `clientName`, `postcode`, `city`
    - [ ] `appliedWeights`, `appliedConditions`
    - [ ] `careHomes` (массив из 5 домов)
    - [ ] `fundingOptimization`
    - [ ] `comparativeAnalysis`
    - [ ] `riskAssessment`
    - [ ] `negotiationStrategy`
  - [ ] Типы данных соответствуют TypeScript интерфейсам
  - [ ] Нет `null` значений в обязательных полях (только опциональные могут быть `null`)

#### 6.2 Проверка структуры care homes
- [ ] **Проверить структуру каждого care home**
  - [ ] `matchScore` - число от 0 до 100, округлено до 2 знаков
  - [ ] `weeklyPrice` - число > 0, округлено до 2 знаков
  - [ ] `factorScores` - массив из 8 объектов, каждый с `score` (округлен до 2 знаков)
  - [ ] `fsaDetailed` - объект или `null`
  - [ ] `financialStability` - объект или `null`
  - [ ] `googlePlaces` - объект или `null`
  - [ ] `cqcDeepDive` - объект или `null`
  - [ ] `staffData` - объект или `null`

#### 6.3 Проверка сортировки результатов
- [ ] **Проверить сортировку care homes**
  - [ ] Сортировка по `matchScore` (descending)
  - [ ] Обработка `None` значений в `matchScore` при сортировке
  - [ ] Правильная обработка одинаковых scores

**Паттерн безопасного кода:**
```python
# ✅ ПРАВИЛЬНО:
care_homes.sort(key=lambda x: float(x.get('matchScore', 0) or 0), reverse=True)
```

---

### 7. Динамические веса

#### 7.1 Проверка расчета динамических весов
- [ ] **Проверить применение всех 6 правил**
  - [ ] Rule 1: High Fall Risk (приоритет 1)
  - [ ] Rule 2: Dementia/Specialized Care (приоритет 2)
  - [ ] Rule 3: Multiple Complex Medical Conditions (приоритет 3)
  - [ ] Rule 4: Nursing Level Required (приоритет 4)
  - [ ] Rule 5: Low Budget Constraint (приоритет 5)
  - [ ] Rule 6: Urgent Placement (приоритет 6)

- [ ] **Проверить приоритет правил**
  - [ ] Правила применяются в порядке приоритета
  - [ ] Высокоприоритетные правила перекрывают низкоприоритетные
  - [ ] Правила не конфликтуют друг с другом

- [ ] **Проверить нормализацию весов**
  - [ ] Сумма всех весов = 100%
  - [ ] Все веса >= 0
  - [ ] Веса правильно применяются в `calculate_156_point_match()`

#### 7.2 Проверка отображения динамических весов
- [ ] **Проверить отображение `appliedWeights` и `appliedConditions`**
  - [ ] Все веса отображаются в UI
  - [ ] Все примененные условия отображаются
  - [ ] Визуальные карточки для весов отображаются корректно

---

### 8. Enrichment Services

#### 8.1 Проверка работы всех enrichment services
- [ ] **CQCEnrichmentService**
  - [ ] Обработка ошибок API (401, 404, etc.)
  - [ ] Возврат дефолтных данных при ошибках
  - [ ] Правильное закрытие соединений

- [ ] **FinancialEnrichmentService**
  - [ ] Обработка отсутствующих данных Companies House
  - [ ] Расчет Altman Z-score с проверкой на None
  - [ ] Расчет bankruptcy risk score

- [ ] **FSAEnrichmentService**
  - [ ] Обработка отсутствующих FSA данных
  - [ ] Извлечение 3 sub-scores (Hygiene, Cleanliness, Management)
  - [ ] Нормализация scores

- [ ] **GooglePlacesEnrichmentService**
  - [ ] Обработка отсутствующих Google Places данных
  - [ ] Извлечение insights (dwell time, repeat rate, footfall trends)
  - [ ] Обработка ошибок API

- [ ] **StaffEnrichmentService**
  - [ ] Обработка отсутствующих Glassdoor/LinkedIn данных
  - [ ] Обработка ошибок Perplexity API
  - [ ] Кэширование данных

#### 8.2 Проверка закрытия enrichment services
- [ ] **Проверить закрытие всех enrichment services**
  - [ ] `await cqc_enrichment.close()`
  - [ ] `await financial_enrichment.close()`
  - [ ] `await fsa_enrichment.close()`
  - [ ] `await google_places_enrichment.close()`
  - [ ] `await staff_enrichment.close()`
  - [ ] Обработка ошибок при закрытии

---

### 9. Обработка ошибок

#### 9.1 Проверка обработки ошибок в endpoint
- [ ] **Проверить try/except блоки в `/api/professional-report`**
  - [ ] Все критические операции обернуты в try/except
  - [ ] Логирование ошибок с полным traceback
  - [ ] Возврат понятных сообщений об ошибках пользователю
  - [ ] Использование `handle_api_error` для консистентных ответов
  - [ ] Вывод ошибок в консоль для отладки

**Паттерн безопасного кода:**
```python
# ✅ ПРАВИЛЬНО:
try:
    # ... code ...
except ValueError as e:
    logger.error(f"Validation error: {e}", exc_info=True)
    raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
except Exception as e:
    import traceback
    error_traceback = traceback.format_exc()
    error_detail = handle_api_error(e, "Professional Report", "generate_report", {...})
    logger.error(f"Error: {e}\nFull traceback:\n{error_traceback}", exc_info=True)
    print(f"\n{'='*80}")
    print(f"ERROR in Professional Report Generation")
    print(f"{'='*80}")
    print(f"Error: {str(e)}")
    print(f"Type: {type(e).__name__}")
    print(f"\nFull traceback:")
    print(error_traceback)
    print(f"{'='*80}\n")
    raise HTTPException(status_code=500, detail=error_detail)
```

#### 9.2 Проверка обработки ошибок во Frontend
- [ ] **Проверить обработку ошибок в React компонентах**
  - [ ] Try/catch блоки в async функциях
  - [ ] Отображение понятных сообщений об ошибках
  - [ ] Обработка сетевых ошибок (500, 400, timeout)
  - [ ] Fallback UI при ошибках
  - [ ] Обработка ошибок в `useProfessionalReport` hook

---

## 🟢 ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ

### 10. Производительность

#### 10.1 Проверка производительности
- [ ] **Проверить время ответа API**
  - [ ] Endpoint отвечает в разумные сроки (< 30 секунд для Professional Report)
  - [ ] Нет блокирующих операций
  - [ ] Использование кэширования где возможно (Redis)
  - [ ] Асинхронная обработка enrichment services

#### 10.2 Проверка памяти
- [ ] **Проверить использование памяти**
  - [ ] Нет утечек памяти
  - [ ] Правильное закрытие соединений (enrichment services, API clients)
  - [ ] Очистка временных данных
  - [ ] Правильное управление кэшем

---

### 11. Тестирование

#### 11.1 Проверка unit тестов
- [ ] **Проверить наличие тестов для критических функций**
  - [ ] `test_professional_dynamic_weights.py` - тесты для динамических весов
  - [ ] `test_professional_scoring.py` - тесты для scoring категорий
  - [ ] `test_professional_endpoint.py` - тесты для endpoint
  - [ ] `test_safe_float_conversion.py` - тесты для безопасного преобразования
  - [ ] `test_negotiation_strategy_none_handling.py` - тесты для None handling
  - [ ] `test_comparative_analysis_none_handling.py` - тесты для None handling
  - [ ] `NegotiationStrategyViewer.test.tsx` - тесты для frontend компонента

#### 11.2 Проверка интеграционных тестов
- [ ] **Проверить интеграционные тесты**
  - [ ] Тесты для endpoint `/api/professional-report`
  - [ ] Тесты с различными входными данными (6 тестовых опросников)
  - [ ] Тесты с отсутствующими данными
  - [ ] Тесты для всех enrichment services

---

### 12. Документация

#### 12.1 Проверка документации
- [ ] **Проверить актуальность документации**
  - [ ] README файлы обновлены
  - [ ] Комментарии в коде актуальны
  - [ ] Описание API endpoints актуально
  - [ ] Документация по динамическим весам актуальна

---

## 📋 ЧЕКЛИСТ БЫСТРОЙ ПРОВЕРКИ

### Перед коммитом:
- [ ] Запустить линтер: `pylint` и `eslint`
- [ ] Запустить тесты: `pytest` и `npm test`
- [ ] Проверить, что приложение запускается без ошибок
- [ ] Проверить генерацию Professional Report с тестовыми данными (все 6 опросников)
- [ ] Проверить отображение Professional Report во Frontend
- [ ] Проверить, что все секции отображаются (даже с "NA")

### После деплоя:
- [ ] Проверить endpoint `/api/professional-report` с валидными данными
- [ ] Проверить endpoint с невалидными данными (должна быть ошибка 400)
- [ ] Проверить endpoint с отсутствующими данными (должна быть ошибка 400)
- [ ] Проверить endpoint с legacy форматами (например, "15km" вместо "within_15km")
- [ ] Проверить отображение Professional Report в браузере
- [ ] Проверить, что все секции отображаются (даже с "NA")
- [ ] Проверить форматирование чисел (2 знака после запятой)
- [ ] Проверить работу всех графиков (Radar Chart, CQC Trend, Financial Stability, etc.)
- [ ] Проверить работу collapsible секций
- [ ] Проверить работу navigation sidebar

---

## 🔍 СПЕЦИФИЧЕСКИЕ ПРОВЕРКИ ДЛЯ PROFESSIONAL REPORT

### 13. Professional Report специфичные проверки

#### 13.1 Проверка структуры Professional Report
- [ ] **Проверить обязательные поля Professional Report**
  - [ ] `reportId` присутствует и является UUID
  - [ ] `careHomes` массив с 5 домами
  - [ ] `appliedWeights` объект с 8 весами (сумма = 100%)
  - [ ] `appliedConditions` массив примененных условий
  - [ ] `fundingOptimization` объект со всеми подсекциями
  - [ ] `comparativeAnalysis` объект с comparison table
  - [ ] `riskAssessment` объект с risk summary
  - [ ] `negotiationStrategy` объект со всеми подсекциями

#### 13.2 Проверка данных care homes
- [ ] **Проверить данные каждого care home**
  - [ ] `matchScore` - число от 0 до 100, округлено до 2 знаков
  - [ ] `weeklyPrice` - число > 0, округлено до 2 знаков
  - [ ] `factorScores` - массив из 8 объектов:
    - [ ] Medical Capabilities (maxScore: 30)
    - [ ] Safety & Quality (maxScore: 25)
    - [ ] Location & Access (maxScore: 15)
    - [ ] Cultural & Social (maxScore: 15)
    - [ ] Financial Stability (maxScore: 20)
    - [ ] Staff Quality (maxScore: 20)
    - [ ] CQC Compliance (maxScore: 20)
    - [ ] Additional Services (maxScore: 11)
  - [ ] Все опциональные поля (`fsaDetailed`, `financialStability`, etc.) могут быть `null`

#### 13.3 Проверка Funding Optimization
- [ ] **Проверить все подсекции Funding Optimization**
  - [ ] `chc_eligibility` - объект с DST domains, eligibility_probability
  - [ ] `la_funding` - объект с capital/income assessment, funding_level
  - [ ] `dpa_considerations` - объект с property assessment, deferral_limits
  - [ ] `funding_outcomes` - массив с outcomes для каждого дома
  - [ ] `five_year_projections` - массив с projections для всех сценариев

#### 13.4 Проверка Comparative Analysis
- [ ] **Проверить структуру Comparative Analysis**
  - [ ] `comparison_table` - массив с данными для таблицы
  - [ ] `rankings` - объект с match score rankings
  - [ ] `price_comparison` - объект с price comparison
  - [ ] `key_differentiators` - массив с differentiators

#### 13.5 Проверка Red Flags & Risk Assessment
- [ ] **Проверить структуру Risk Assessment**
  - [ ] `summary` - объект с общим summary
  - [ ] `homes` - массив с risk assessment для каждого дома
  - [ ] Все risk scores корректно рассчитаны

#### 13.6 Проверка Negotiation Strategy
- [ ] **Проверить структуру Negotiation Strategy**
  - [ ] `market_rate_analysis` - объект с market analysis
  - [ ] `discount_negotiation_points` - объект с discount points
  - [ ] `contract_review_checklist` - объект с checklist
  - [ ] `email_templates` - объект с email templates
  - [ ] `questions_to_ask_at_visit` - объект с questions

---

## ⚠️ ИЗВЕСТНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: NoneType comparison error
**Симптом:** `TypeError: '>' not supported between instances of 'NoneType' and 'int'`  
**Решение:** Всегда преобразовывать значения в `float` перед сравнением во всех сервисах

### Проблема 2: Float conversion error
**Симптом:** `ValueError: could not convert string to float: 'Waived fees or 2'`  
**Решение:** Использовать `_safe_float_convert()` для всех пользовательских данных

### Проблема 3: JSX structure error
**Симптом:** `Adjacent JSX elements must be wrapped in an enclosing tag`  
**Решение:** Использовать React Fragment `<>...</>` или обернуть в `<div>`, использовать `{condition ? (...) : null}`

### Проблема 4: Null property access
**Симптом:** `Cannot read properties of null (reading 'replace')`  
**Решение:** Использовать optional chaining `value?.replace()` и fallback значения

### Проблема 5: Секции не отображаются
**Симптом:** Секции CQC, FSA, Financial Stability не видны  
**Решение:** Убрать условия `{data && (...)}`, всегда показывать секции с "NA" если данных нет

### Проблема 6: Validation error для legacy форматов
**Симптом:** `Validation failed: q6_max_distance must be one of: within_5km, ...`  
**Решение:** Нормализовать legacy форматы ("15km" → "within_15km") в валидаторе

### Проблема 7: Enriched data не определен
**Симптом:** `name 'enriched_data' is not defined`  
**Решение:** Инициализировать `enriched_data = base_enriched_data.copy()` в начале каждой итерации цикла

---

## 📝 ЗАМЕТКИ ДЛЯ LLM

При проверке Professional Report обращай особое внимание на:

1. **Все числовые сравнения во ВСЕХ сервисах** - должны быть безопасными (преобразование в float/int)
2. **Все обращения к свойствам** - должны использовать optional chaining или проверки на null
3. **ВСЕ секции UI** - должны отображаться даже при отсутствии данных (показывать "NA")
4. **Все форматирования чисел** - должны быть округлены до 2 знаков после запятой
5. **Все ошибки** - должны логироваться с полным traceback для отладки
6. **Все enrichment services** - должны правильно закрываться и обрабатывать ошибки
7. **Динамические веса** - должны правильно применяться и отображаться
8. **Все графики** - должны проверять данные перед рендерингом
9. **Валидация** - должна нормализовать legacy форматы
10. **Структура ответа API** - должна соответствовать TypeScript интерфейсам

Если находишь ошибку, которая не покрыта этим чеклистом, добавь её в раздел "Известные проблемы" для будущих проверок.

### Критические файлы для проверки:
- `api-testing-suite/backend/main.py` - endpoint `/api/professional-report`
- `api-testing-suite/backend/services/professional_matching_service.py` - 156-point matching
- `api-testing-suite/backend/services/funding_optimization_service.py` - funding calculations
- `api-testing-suite/backend/services/comparative_analysis_service.py` - comparative analysis
- `api-testing-suite/backend/services/red_flags_service.py` - risk assessment
- `api-testing-suite/backend/services/negotiation_strategy_service.py` - negotiation strategy
- `api-testing-suite/frontend/src/features/professional-report/ProfessionalReportViewer.tsx` - main component
- `api-testing-suite/frontend/src/features/professional-report/components/NegotiationStrategyViewer.tsx` - negotiation component

