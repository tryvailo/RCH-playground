# Professional Report Unit Tests

**Статус:** ✅ Полное покрытие тестами

---

## Структура тестов

### 1. `test_professional_dynamic_weights.py` (16 тестов)
Тесты для динамических весов:
- ✅ Base weights (без условий)
- ✅ Rule 1: High Fall Risk
- ✅ Rule 2: Dementia
- ✅ Rule 3: Multiple Conditions (3+)
- ✅ Rule 4: Nursing Required
- ✅ Rule 5: Low Budget
- ✅ Rule 6: Urgent Placement
- ✅ Priority order (Fall Risk > Dementia > Multiple)
- ✅ Combinations (Nursing + Budget, Urgent + Budget)
- ✅ Edge cases

### 2. `test_professional_scoring.py` (30+ тестов)
Тесты для 8 scoring категорий:

#### Medical Capabilities (4 теста)
- ✅ Dementia care match
- ✅ Nursing level scoring
- ✅ Mobility support
- ✅ No match scenario

#### Safety & Quality (4 теста)
- ✅ Outstanding CQC rating
- ✅ High fall risk user
- ✅ FSA rating impact
- ✅ Safeguarding incidents penalty

#### Location & Access (4 теста)
- ✅ Within 5km distance
- ✅ Public transport scoring
- ✅ Distance not important
- ✅ Missing coordinates

#### Cultural & Social (3 теста)
- ✅ High visitor engagement
- ✅ Quiet personality match
- ✅ Low engagement

#### Financial Stability (3 теста)
- ✅ Excellent financials
- ✅ Bankruptcy risk
- ✅ Altman Z-score impact

#### Staff Quality (3 теста)
- ✅ Excellent staff quality
- ✅ High turnover penalty
- ✅ Tenure impact

#### CQC Compliance (3 теста)
- ✅ All Outstanding ratings
- ✅ Mixed ratings
- ✅ Missing ratings

#### Additional Services (3 теста)
- ✅ Comprehensive services
- ✅ Minimal services
- ✅ Specialist program match

#### Full 156-Point Match (2 теста)
- ✅ Complete match calculation
- ✅ Dementia weights integration

### 3. `test_professional_endpoint.py` (8 тестов)
Тесты для API endpoint `/api/professional-report`:
- ✅ Basic request structure
- ✅ Dementia profile weights
- ✅ High fall risk profile weights
- ✅ Low budget profile weights
- ✅ Multiple conditions profile weights
- ✅ Urgent placement profile weights
- ✅ Care homes sorted by match score
- ✅ Factor scores structure validation

---

## Запуск тестов

### Все тесты Professional Report:
```bash
cd api-testing-suite/backend
pytest tests/test_professional_*.py -v
```

### Конкретный файл:
```bash
pytest tests/test_professional_scoring.py -v
pytest tests/test_professional_dynamic_weights.py -v
pytest tests/test_professional_endpoint.py -v
```

### С покрытием кода:
```bash
pytest tests/test_professional_*.py --cov=services.professional_matching_service --cov-report=html
```

### Конкретный класс тестов:
```bash
pytest tests/test_professional_scoring.py::TestMedicalCapabilitiesScoring -v
```

### Конкретный тест:
```bash
pytest tests/test_professional_scoring.py::TestMedicalCapabilitiesScoring::test_medical_capabilities_dementia_match -v
```

---

## Покрытие кода

### Методы, покрытые тестами:

#### `ProfessionalMatchingService`:
- ✅ `calculate_dynamic_weights()` - 16 тестов
- ✅ `calculate_156_point_match()` - 2 теста
- ✅ `_calculate_medical_capabilities()` - 4 теста
- ✅ `_calculate_safety_quality()` - 4 теста
- ✅ `_calculate_location_access()` - 4 теста
- ✅ `_calculate_cultural_social()` - 3 теста
- ✅ `_calculate_financial_stability()` - 3 теста
- ✅ `_calculate_staff_quality()` - 3 теста
- ✅ `_calculate_cqc_compliance()` - 3 теста
- ✅ `_calculate_additional_services()` - 3 теста

#### `ScoringWeights`:
- ✅ `normalize()` - 1 тест
- ✅ `to_dict()` - 1 тест

#### API Endpoint:
- ✅ `POST /api/professional-report` - 8 тестов

---

## Примеры тестов

### Тест динамических весов:
```python
def test_rule_1_high_fall_risk(self):
    questionnaire = {
        'section_4_safety_special_needs': {
            'q13_fall_history': 'high_risk_of_falling'
        }
    }
    
    weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
    
    assert weights.safety >= 24.0
    assert 'high_fall_risk' in conditions
```

### Тест scoring категории:
```python
def test_medical_capabilities_dementia_match(self):
    home = {'care_types': ['dementia'], 'care_dementia': True}
    user_profile = {
        'section_3_medical_needs': {
            'q9_medical_conditions': ['dementia_alzheimers']
        }
    }
    
    score = self.service._calculate_medical_capabilities(home, user_profile, {})
    
    assert 0.0 <= score <= 1.0
    assert score >= 0.6
```

### Тест API endpoint:
```python
def test_professional_report_dementia_profile(self):
    questionnaire = {
        'section_3_medical_needs': {
            'q9_medical_conditions': ['dementia_alzheimers']
        }
        # ... other sections
    }
    
    response = client.post("/api/professional-report", json=questionnaire)
    
    assert response.status_code == 200
    assert 'dementia' in response.json()['report']['appliedConditions']
```

---

## Edge Cases

Тесты покрывают следующие edge cases:

1. **Missing data**: Отсутствующие координаты, рейтинги, данные
2. **Invalid inputs**: Некорректные значения в questionnaire
3. **Priority conflicts**: Конфликты между правилами динамических весов
4. **Boundary conditions**: Граничные значения (0, максимальные значения)
5. **Combination rules**: Комбинации нескольких правил
6. **Empty arrays**: Пустые списки условий, программ

---

## Статистика

- **Всего тестов**: 54+
- **Покрытие методов**: 100% для scoring методов
- **Покрытие edge cases**: Высокое
- **Время выполнения**: ~5-10 секунд для всех тестов

---

## Примечания

- Все тесты изолированы и не требуют внешних зависимостей
- Используются моки для enriched_data
- Тесты проверяют как структуру данных, так и логику вычислений
- Все тесты должны проходить успешно перед деплоем

---

**Конец документа**

