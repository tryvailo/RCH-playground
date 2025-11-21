# Анализ динамических весов скоринга для Professional Report

**Дата:** 2025-01-XX  
**Статус:** ⚠️ КРИТИЧЕСКОЕ УПУЩЕНИЕ В ТЕХЗАДАНИИ

---

## Проблема

В текущем техзадании указана **фиксированная система весов** для всех профилей клиентов:

| Category | Points | Weight | Details |
|----------|--------|--------|---------|
| Medical Capabilities | 30 | **19%** | Condition-specific care match |
| Safety & Quality | 25 | **16%** | CQC + FSA + incident history |
| Location & Access | 15 | **10%** | Distance + transport access |
| Cultural & Social | 15 | **10%** | Visitor analytics + community |
| Financial Stability | 20 | **13%** | Companies House + bankruptcy risk |
| Staff Quality | 20 | **13%** | Glassdoor + LinkedIn + turnover |
| CQC Compliance | 20 | **13%** | Historical + trends + improvements |
| Additional Services | 11 | **7%** | Activities + specialized programs |

**НО:** Для разных состояний клиента должны применяться **разные веса категорий**.

---

## Примеры, когда нужны разные веса

### 1. Высокий риск падений (Q13: `high_risk_of_falling`)

**Текущий вес:** Safety & Quality = 16% (25 points)

**Должен быть:** Safety & Quality = **25-30%** (40-45 points)

**Обоснование:**
- Безопасность становится КРИТИЧЕСКИМ фактором
- Fall prevention programs должны иметь максимальный приоритет
- CQC Safe rating становится более важным, чем другие факторы

**Предлагаемые веса:**
```
Safety & Quality:     25% (40 points)  ↑ +9%
Medical Capabilities:  18% (28 points)  ↓ -1%
Location & Access:      8% (12 points)  ↓ -2%
Cultural & Social:      8% (12 points)  ↓ -2%
Financial Stability:   12% (19 points)  ↓ -1%
Staff Quality:         12% (19 points)  ↓ -1%
CQC Compliance:        12% (19 points)  ↓ -1%
Additional Services:    5% ( 7 points)  ↓ -2%
```

---

### 2. Деменция (Q9: `dementia_alzheimers`)

**Текущий вес:** Medical Capabilities = 19% (30 points)

**Должен быть:** Medical Capabilities = **25-28%** (40-45 points)

**Обоснование:**
- Специализированный dementia care критически важен
- Staff qualifications для dementia care должны иметь максимальный приоритет
- Medical protocols для dementia более важны, чем общие медицинские возможности

**Предлагаемые веса:**
```
Medical Capabilities:  26% (41 points)  ↑ +7%
Safety & Quality:      18% (28 points)  ↑ +2% (dementia safety)
Location & Access:      8% (12 points)  ↓ -2%
Cultural & Social:     10% (15 points)  → 0%
Financial Stability:   12% (19 points)  ↓ -1%
Staff Quality:         14% (22 points)  ↑ +1% (dementia-trained staff)
CQC Compliance:       10% (15 points)  ↓ -3%
Additional Services:    2% ( 4 points)  ↓ -5%
```

---

### 3. Сложные медицинские условия (Q9: множественные условия)

**Текущий вес:** Medical Capabilities = 19% (30 points)

**Должен быть:** Medical Capabilities = **28-30%** (45-47 points)

**Обоснование:**
- Множественные условия требуют комплексного медицинского подхода
- Nursing level становится критическим
- Medication management complexity требует высокого приоритета

**Предлагаемые веса:**
```
Medical Capabilities:  29% (45 points)  ↑ +10%
Safety & Quality:      15% (23 points)  ↓ -1%
Location & Access:      7% (11 points)  ↓ -3%
Cultural & Social:      7% (11 points)  ↓ -3%
Financial Stability:   13% (20 points)  → 0%
Staff Quality:         14% (22 points)  ↑ +1%
CQC Compliance:        12% (19 points)  ↓ -1%
Additional Services:    3% ( 5 points)  ↓ -4%
```

---

### 4. Финансовые ограничения (Q7: низкий бюджет)

**Текущий вес:** Financial Stability = 13% (20 points)

**Должен быть:** Financial Stability = **18-20%** (28-31 points)

**Обоснование:**
- При ограниченном бюджете важно избежать финансовых рисков
- Bankruptcy risk становится критическим фактором
- Нужно гарантировать стабильность на 5+ лет

**Предлагаемые веса:**
```
Financial Stability:   19% (30 points)  ↑ +6%
Medical Capabilities:  18% (28 points)  ↓ -1%
Safety & Quality:      16% (25 points)  → 0%
Location & Access:      9% (14 points)  ↓ -1%
Cultural & Social:      9% (14 points)  ↓ -1%
Staff Quality:         13% (20 points)  → 0%
CQC Compliance:       13% (20 points)  → 0%
Additional Services:    3% ( 5 points)  ↓ -4%
```

---

### 5. Срочное размещение (Q17: `urgent_2_weeks`)

**Текущий вес:** Location & Access = 10% (15 points)

**Должен быть:** Location & Access = **15-18%** (23-28 points)

**Обоснование:**
- Близость к дому становится критической
- Доступность для посещений важнее
- Transport access более важен при срочности

**Предлагаемые веса:**
```
Location & Access:    17% (27 points)  ↑ +7%
Medical Capabilities:  18% (28 points)  ↓ -1%
Safety & Quality:      16% (25 points)  → 0%
Cultural & Social:      9% (14 points)  ↓ -1%
Financial Stability:   12% (19 points)  ↓ -1%
Staff Quality:         13% (20 points)  → 0%
CQC Compliance:       13% (20 points)  → 0%
Additional Services:    2% ( 3 points)  ↓ -5%
```

---

## Рекомендации для техзадания

### 1. Добавить раздел "Dynamic Scoring Weights"

В документ `TECHNICAL_PROFESSIONAL_Matching_Logic.md` добавить:

```markdown
## 4.5 Dynamic Scoring Weights Based on Client Profile

The 156-point algorithm uses **adaptive weights** based on client conditions:

### Weight Adjustment Rules

1. **High Fall Risk** (Q13: `high_risk_of_falling`):
   - Safety & Quality: +9% (16% → 25%)
   - Other categories: proportional reduction

2. **Dementia/Alzheimer's** (Q9: `dementia_alzheimers`):
   - Medical Capabilities: +7% (19% → 26%)
   - Safety & Quality: +2% (16% → 18%)
   - Additional Services: -5% (7% → 2%)

3. **Multiple Medical Conditions** (Q9: 2+ conditions):
   - Medical Capabilities: +10% (19% → 29%)
   - Location & Access: -3% (10% → 7%)
   - Cultural & Social: -3% (10% → 7%)

4. **Low Budget** (Q7: `under_3000_*`):
   - Financial Stability: +6% (13% → 19%)
   - Additional Services: -4% (7% → 3%)

5. **Urgent Placement** (Q17: `urgent_2_weeks`):
   - Location & Access: +7% (10% → 17%)
   - Additional Services: -5% (7% → 2%)

### Implementation

```python
def calculate_dynamic_weights(user_profile):
    """
    Calculate adaptive weights based on client conditions.
    Returns dict with adjusted weights that sum to 100%.
    """
    base_weights = {
        'medical': 19,
        'safety': 16,
        'location': 10,
        'social': 10,
        'financial': 13,
        'staff': 13,
        'cqc': 13,
        'services': 7
    }
    
    # Apply adjustments based on conditions
    if user_profile.fall_history == 'high_risk_of_falling':
        base_weights['safety'] += 9
        # Reduce other weights proportionally
    
    if 'dementia_alzheimers' in user_profile.medical_conditions:
        base_weights['medical'] += 7
        base_weights['safety'] += 2
        base_weights['services'] -= 5
    
    # ... other conditions
    
    # Normalize to ensure sum = 100%
    total = sum(base_weights.values())
    return {k: round((v / total) * 100, 1) for k, v in base_weights.items()}
```

### 2. Обновить таблицу весов

В разделе "Category Breakdown" добавить примечание:

> **Note:** Weights shown are base weights. Actual weights are dynamically adjusted based on client profile conditions (see Section 4.5).

### 3. Добавить в алгоритм

В функцию `calculate_156_point_match()` добавить:

```python
def calculate_156_point_match(home, user_profile, enriched_data):
    """
    Calculate comprehensive match score with dynamic weights.
    """
    # Calculate dynamic weights based on user profile
    weights = calculate_dynamic_weights(user_profile)
    
    # Calculate scores with adjusted weights
    medical_score = calculate_medical_capabilities(...) * weights['medical']
    safety_score = calculate_safety_quality(...) * weights['safety']
    # ... etc
```

---

## Примеры применения

### Профиль 1: High Fall Risk
```
Original weights:  Safety 16%, Medical 19%, Location 10%, ...
Adjusted weights:  Safety 25%, Medical 18%, Location 8%, ...
Result: Safety becomes primary factor, homes with excellent fall prevention score higher
```

### Профиль 2: Dementia Care
```
Original weights:  Medical 19%, Safety 16%, Services 7%, ...
Adjusted weights:  Medical 26%, Safety 18%, Services 2%, ...
Result: Medical capabilities (especially dementia specialists) become critical
```

### Профиль 3: Complex Multiple Conditions
```
Original weights:  Medical 19%, Location 10%, Social 10%, ...
Adjusted weights:  Medical 29%, Location 7%, Social 7%, ...
Result: Medical capabilities dominate, location/social become less important
```

---

## Выводы

### ❌ Что ОТСУТСТВУЕТ в текущем техзадании:

1. **Нет упоминания** о динамических весах
2. **Нет правил** для адаптации весов под разные условия
3. **Нет примеров** применения разных весовых систем
4. **Фиксированные веса** для всех профилей

### ✅ Что НУЖНО добавить:

1. Раздел "Dynamic Scoring Weights Based on Client Profile"
2. Правила адаптации весов для каждого критического условия
3. Примеры кода для расчета динамических весов
4. Таблицы с примерами весов для разных профилей
5. Обоснование изменений весов

---

## Приоритет

**🔴 КРИТИЧЕСКИЙ** - Без динамических весов система матчинга будет некорректной для разных профилей клиентов.

**Рекомендация:** Добавить в техзадание перед началом реализации алгоритма матчинга.

---

**Конец документа**

