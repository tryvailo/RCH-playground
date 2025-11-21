# Анализ тестовых опросников на соответствие сценариям динамических весов

**Дата:** 2025-01-XX  
**Статус:** ⚠️ ТРЕБУЕТСЯ КОРРЕКТИРОВКА

---

## Правила динамических весов (из TECHNICAL_PROFESSIONAL_Dynamic_Weights_v2.md)

1. **Rule 1: High Fall Risk** (Q13: `high_risk_of_falling` или `3_plus_or_serious_injuries`)
   - Safety +9% (16% → 25%)
   - **Приоритет:** ВЫСШИЙ (останавливает все остальные)

2. **Rule 2: Dementia** (Q9: `dementia_alzheimers`)
   - Medical +7% (19% → 26%)
   - **Приоритет:** 2 (если нет Fall Risk)

3. **Rule 3: Multiple Conditions** (Q9: 3+ conditions, исключая `no_serious_medical`)
   - Medical +10% (19% → 29%)
   - **Приоритет:** 3 (если нет Dementia)

4. **Rule 4: Nursing Required** (Q8: `medical_nursing`)
   - Medical +3%, Staff +3%
   - **Приоритет:** 4

5. **Rule 5: Low Budget** (Q7: `under_3000_*`)
   - Financial +6% (13% → 19%)
   - **Приоритет:** 5

6. **Rule 6: Urgent Placement** (Q17: `urgent_2_weeks`)
   - Location +7% (10% → 17%)
   - **Приоритет:** 6

---

## Анализ текущих файлов

### ✅ File 1: professional_questionnaire_1_dementia.json

**Профиль:** Пожилой человек с деменцией

**Условия:**
- Q9: `dementia_alzheimers`, `mobility_problems` (2 условия)
- Q13: `1_2_no_serious_injuries` (НЕ high risk)
- Q7: `5000_7000_local` (НЕ low budget)
- Q17: `next_month` (НЕ urgent)
- Q8: `specialised_dementia` (НЕ `medical_nursing`)

**Применяемые правила:**
- ✅ **Rule 2: Dementia** → Medical +7% (19% → 26%)

**Статус:** ✅ ПРАВИЛЬНО - покрывает Rule 2 (Dementia)

---

### ⚠️ File 2: professional_questionnaire_2_diabetes_mobility.json

**Профиль:** Диабет + проблемы мобильности

**Условия:**
- Q9: `diabetes`, `mobility_problems` (2 условия)
- Q13: `3_plus_or_serious_injuries` ✅ **HIGH RISK!**
- Q7: `3000_5000_self` (НЕ low budget)
- Q17: `urgent_2_weeks` ✅ **URGENT!**
- Q8: `medical_nursing` ✅ **NURSING!**

**Применяемые правила:**
- ✅ **Rule 1: High Fall Risk** → Safety +9% (остановит все остальные)
- ❌ Rule 4 (Nursing) - НЕ применится (остановлено Fall Risk)
- ❌ Rule 6 (Urgent) - НЕ применится (остановлено Fall Risk)

**Статус:** ✅ ПРАВИЛЬНО - покрывает Rule 1 (High Fall Risk), но также имеет Nursing и Urgent (которые не применятся из-за приоритета)

**Рекомендация:** Оставить как есть - демонстрирует приоритетный порядок

---

### ✅ File 3: professional_questionnaire_3_cardiac_nursing.json

**Профиль:** Сердечные заболевания + сестринский уход

**Условия:**
- Q9: `heart_conditions` (1 условие)
- Q13: `no_falls_occurred`
- Q7: `over_7000_self` (НЕ low budget)
- Q17: `planning_2_3_months` (НЕ urgent)
- Q8: `medical_nursing` ✅ **NURSING!**

**Применяемые правила:**
- ✅ **Rule 4: Nursing Required** → Medical +3%, Staff +3%

**Статус:** ✅ ПРАВИЛЬНО - покрывает Rule 4 (Nursing Required)

---

### ✅ File 4: professional_questionnaire_4_healthy_residential.json

**Профиль:** Здоровый человек

**Условия:**
- Q9: `no_serious_medical`
- Q13: `no_falls_occurred`
- Q7: `under_3000_self` ✅ **LOW BUDGET!**
- Q17: `exploring_6_plus_months` (НЕ urgent)
- Q8: `general_residential` (НЕ nursing)

**Применяемые правила:**
- ✅ **Rule 5: Low Budget** → Financial +6% (13% → 19%)

**Статус:** ✅ ПРАВИЛЬНО - покрывает Rule 5 (Low Budget)

---

### ⚠️ File 5: professional_questionnaire_5_high_fall_risk.json

**Профиль:** Высокий риск падений

**Условия:**
- Q9: `mobility_problems` (1 условие)
- Q13: `high_risk_of_falling` ✅ **HIGH RISK!**
- Q7: `5000_7000_local` (НЕ low budget)
- Q17: `urgent_2_weeks` ✅ **URGENT!**
- Q8: `general_residential`, `medical_nursing` ✅ **NURSING!**

**Применяемые правила:**
- ✅ **Rule 1: High Fall Risk** → Safety +9% (остановит все остальные)
- ❌ Rule 4 (Nursing) - НЕ применится
- ❌ Rule 6 (Urgent) - НЕ применится

**Статус:** ✅ ПРАВИЛЬНО - покрывает Rule 1 (High Fall Risk), демонстрирует приоритет

---

### ⚠️ File 6: professional_questionnaire_6_complex_multiple.json

**Профиль:** Множественные медицинские проблемы

**Условия:**
- Q9: `dementia_alzheimers`, `diabetes`, `heart_conditions`, `mobility_problems` (4 условия!)
- Q13: `high_risk_of_falling` ✅ **HIGH RISK!**
- Q7: `over_7000_local` (НЕ low budget)
- Q17: `urgent_2_weeks` ✅ **URGENT!**
- Q8: `medical_nursing`, `specialised_dementia` ✅ **NURSING!**

**Применяемые правила:**
- ✅ **Rule 1: High Fall Risk** → Safety +9% (остановит ВСЕ остальные)
- ❌ Rule 2 (Dementia) - НЕ применится
- ❌ Rule 3 (Multiple Conditions) - НЕ применится
- ❌ Rule 4 (Nursing) - НЕ применится
- ❌ Rule 6 (Urgent) - НЕ применится

**Статус:** ⚠️ ПРОБЛЕМА - Fall Risk перекрывает все остальные правила, не демонстрирует Rule 3 (Multiple Conditions)

**Рекомендация:** Создать отдельный файл для Rule 3 без Fall Risk

---

## Покрытие сценариев

| Правило | Файл | Статус |
|---------|------|--------|
| Rule 1: High Fall Risk | File 2, File 5, File 6 | ✅ Покрыто (3 файла) |
| Rule 2: Dementia | File 1 | ✅ Покрыто |
| Rule 3: Multiple Conditions (3+) | File 6 (но перекрыто Fall Risk) | ⚠️ НЕ ПОКРЫТО изолированно |
| Rule 4: Nursing Required | File 3 | ✅ Покрыто |
| Rule 5: Low Budget | File 4 | ✅ Покрыто |
| Rule 6: Urgent Placement | File 2, File 5, File 6 (но перекрыто) | ⚠️ НЕ ПОКРЫТО изолированно |

---

## Проблемы

### ❌ Проблема 1: Rule 3 (Multiple Conditions) не покрыт изолированно

File 6 имеет 4 условия, но также имеет Fall Risk, который останавливает применение Rule 3.

**Решение:** Создать новый файл без Fall Risk, но с 3+ условиями.

### ❌ Проблема 2: Rule 6 (Urgent Placement) не покрыт изолированно

Все файлы с Urgent также имеют Fall Risk или другие высокоприоритетные условия.

**Решение:** Создать файл с Urgent, но без Fall Risk/Dementia/Multiple.

### ⚠️ Проблема 3: Нет комбинаций правил низкого приоритета

Нет примеров комбинаций:
- Nursing + Low Budget
- Urgent + Low Budget
- Nursing + Urgent (без Fall Risk)

---

## Рекомендации

### Создать дополнительные файлы:

1. **professional_questionnaire_7_multiple_conditions.json**
   - Q9: 3+ conditions (БЕЗ dementia, БЕЗ fall risk)
   - Демонстрирует Rule 3 изолированно

2. **professional_questionnaire_8_urgent_only.json**
   - Q17: urgent_2_weeks
   - БЕЗ Fall Risk, БЕЗ Dementia, БЕЗ Multiple
   - Демонстрирует Rule 6 изолированно

3. **professional_questionnaire_9_nursing_budget.json**
   - Q8: medical_nursing
   - Q7: under_3000_*
   - Демонстрирует комбинацию Rule 4 + Rule 5

4. **professional_questionnaire_10_urgent_budget.json**
   - Q17: urgent_2_weeks
   - Q7: under_3000_*
   - Демонстрирует комбинацию Rule 6 + Rule 5

---

## Итоговая таблица покрытия

| Сценарий | Текущие файлы | Статус |
|----------|---------------|--------|
| Base weights (нет условий) | File 4 (частично) | ⚠️ Нужен чистый пример |
| Rule 1: High Fall Risk | File 2, File 5, File 6 | ✅ Покрыто |
| Rule 2: Dementia | File 1 | ✅ Покрыто |
| Rule 3: Multiple Conditions | File 6 (перекрыто) | ❌ НЕ покрыто |
| Rule 4: Nursing | File 3 | ✅ Покрыто |
| Rule 5: Low Budget | File 4 | ✅ Покрыто |
| Rule 6: Urgent | File 2, File 5, File 6 (перекрыто) | ❌ НЕ покрыто |
| Комбинация: Nursing + Budget | - | ❌ НЕ покрыто |
| Комбинация: Urgent + Budget | - | ❌ НЕ покрыто |
| Приоритет: Fall Risk > Dementia | File 6 | ✅ Покрыто |

---

**Вывод:** Требуется создать 4 дополнительных файла для полного покрытия всех сценариев.

---

**Конец документа**

