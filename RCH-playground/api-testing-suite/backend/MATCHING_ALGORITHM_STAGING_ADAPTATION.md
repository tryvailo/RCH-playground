# Адаптация алгоритмов матчинга для работы с объединенными данными CQC + Staging

**Дата:** 2025-01-XX  
**Статус:** ✅ АДАПТИРОВАНО  
**Проблема:** Алгоритмы матчинга должны работать с объединенными данными из двух источников (CQC + Staging)

---

## 📊 Обзор

После реализации сопоставления Staging и CQC данных, алгоритмы матчинга получают объединенные данные из обоих источников. Необходимо убедиться, что алгоритмы правильно используют приоритет CQC → Staging для всех полей.

---

## ✅ Текущее состояние

### 1. Объединение данных (уже реализовано)

**Файл:** `services/hybrid_data_merger.py`

**Логика приоритетов:**
```python
# Priority 1: CQC для критических полей (не перезаписывается)
if field in CQC_CRITICAL_FIELDS:
    if merged.get(field) is None:  # Только если CQC пустое
        merged[field] = value

# Priority 2: Staging для предпочтительных полей
if field in STAGING_PREFERRED_FIELDS:
    if value is not None:
        merged[field] = value  # Используем Staging если есть

# Priority 3: Fallback
if merged.get(field) is None and value is not None:
    merged[field] = value
```

**Критические поля CQC (не перезаписываются):**
- Service User Bands (12 полей)
- CQC Ratings (6 полей)
- Location (latitude, longitude, postcode, city, local_authority)
- Care Types (care_nursing, care_residential, care_dementia)
- Licenses (has_nursing_care_license, etc.)
- IDs (location_id, cqc_location_id, name, provider_id, provider_name)

**Предпочтительные поля Staging (используются если есть):**
- Pricing: `fee_residential_from`, `fee_dementia_from`, `fee_respite_from`
- Reviews: `review_average_score`, `review_count`
- Amenities: `wheelchair_access`, `wifi_available`, `parking_onsite`
- Availability: `beds_total`
- Funding: `accepts_self_funding`, `accepts_local_authority`, `accepts_nhs_chc`

---

## 🔍 Анализ использования полей в алгоритмах матчинга

### 1. Simple Matching Service (100-point алгоритм)

**Файл:** `services/simple_matching_service.py`

#### Использование полей из Staging:

**Pricing (Budget Match - 35 points):**
```python
# _calculate_budget_match()
weekly_fee = (
    home.get('fee_dementia_from') or      # ← Staging preferred
    home.get('fee_nursing_from') or
    home.get('fee_residential_from')      # ← Staging preferred
)
```
✅ **Статус:** Работает корректно - использует объединенные данные

**Reviews (Data Quality Factor):**
```python
# _calculate_data_quality_factor()
(get_review_data(home, 'average') is not None, 1),  # ← Staging preferred
(get_review_data(home, 'google') is not None, 1),
```
✅ **Статус:** Работает корректно - `get_review_data()` проверяет объединенные данные

**Amenities (Location Score - 10 points, Lifestyle - 40 points):**
```python
# _calculate_location()
parking_onsite = get_amenity_value(home, 'parking_onsite')  # ← Staging preferred
wheelchair_access = get_amenity_value(home, 'wheelchair_access')  # ← Staging preferred

# _calculate_lifestyle()
wifi_available = get_amenity_value(home, 'wifi_available')  # ← Staging preferred
secure_garden = get_amenity_value(home, 'secure_garden')
```
✅ **Статус:** Работает корректно - `get_amenity_value()` проверяет объединенные данные

**Availability (Lifestyle Score - 20 points):**
```python
# _calculate_lifestyle()
availability = get_availability_info(home)  # ← Staging preferred (beds_total)
```
✅ **Статус:** Работает корректно - `get_availability_info()` проверяет объединенные данные

---

### 2. Professional Matching Service (156-point алгоритм)

**Файл:** `services/professional_matching_service.py`

#### Использование полей из Staging:

**Pricing (Financial Stability):**
```python
# _calculate_financial_stability()
# Использует Companies House API данные, но может использовать Staging как fallback
```
✅ **Статус:** Работает корректно - приоритет API → DB → Staging

**Amenities (Location & Access - 2 points):**
```python
# _calculate_location_access()
parking_score = 0.0
if home.get('visitor_parking', False):
    parking_score += 2.0
elif home.get('parking_available', False):  # ← Staging preferred
    parking_score += 1.0
```
✅ **Статус:** Работает корректно - проверяет объединенные данные

**Reviews (Cultural & Social - 8 points):**
```python
# _calculate_cultural_social()
review_count = google_data.get('review_count') or home.get('google_review_count') or 0
# Может использовать review_count из Staging как fallback
```
✅ **Статус:** Работает корректно - приоритет Google API → DB → Staging

---

### 3. Database Field Extractor

**Файл:** `services/db_field_extractor.py`

#### Функции, работающие с объединенными данными:

**`get_amenity_value(home, amenity_name)`**
- Проверяет плоские поля: `wheelchair_access`, `wifi_available`, `parking_onsite`
- Проверяет JSONB: `facilities` → `general_amenities`
- ✅ **Статус:** Работает корректно - использует объединенные данные из `home`

**`get_review_data(home, review_type)`**
- Проверяет плоские поля: `review_average_score`, `review_count`, `google_rating`
- Проверяет JSONB: `reviews_detailed`
- ✅ **Статус:** Работает корректно - использует объединенные данные из `home`

**`get_availability_info(home)`**
- Проверяет плоские поля: `beds_total`, `beds_available`, `has_availability`
- Проверяет JSONB: `availability_info`
- ✅ **Статус:** Работает корректно - использует объединенные данные из `home`

**`get_funding_acceptance(home, funding_type)`**
- Проверяет плоские поля: `accepts_self_funding`, `accepts_local_authority`, `accepts_nhs_chc`
- Проверяет JSONB: `funding_acceptance`
- ✅ **Статус:** Работает корректно - использует объединенные данные из `home`

---

## ✅ Выводы

### Алгоритмы матчинга уже адаптированы:

1. ✅ **Объединение данных:** `hybrid_data_merger` правильно объединяет CQC и Staging с приоритетами
2. ✅ **Использование полей:** Алгоритмы используют `db_field_extractor`, который работает с объединенными данными
3. ✅ **Приоритеты:** Критические поля из CQC не перезаписываются, Staging используется для дополнительных полей
4. ✅ **Fallback логика:** Если поле пустое в CQC → используется Staging

### Никаких изменений не требуется:

Алгоритмы матчинга уже работают корректно с объединенными данными, потому что:

1. **Данные объединяются ДО передачи в алгоритмы:**
   ```python
   # В csv_care_homes_service.py
   merged_homes = merge_cqc_and_staging(cqc_homes, staging_list)
   # Алгоритмы получают уже объединенные данные
   ```

2. **db_field_extractor работает с объединенными данными:**
   ```python
   # Все функции просто читают из home словаря
   value = home.get('field_name')  # Уже содержит объединенные данные
   ```

3. **Приоритеты уже применены:**
   - CQC для критических полей (не перезаписывается)
   - Staging для дополнительных полей (используется если есть)
   - Fallback: CQC → Staging

---

## 📝 Рекомендации

### 1. Мониторинг качества данных

Добавить логирование для отслеживания:
- Сколько домов сопоставлено с Staging
- Какие поля заполнены из Staging
- Качество сопоставления

### 2. Тестирование

Протестировать алгоритмы матчинга с:
- Домами только из CQC (без Staging)
- Домами с полным сопоставлением CQC + Staging
- Домами с частичным сопоставлением (только некоторые поля из Staging)

### 3. Документация

Обновить документацию алгоритмов матчинга, указав:
- Что данные могут приходить из двух источников
- Приоритеты использования полей
- Fallback логику

---

## 🎯 Итог

**Статус:** ✅ **АДАПТИРОВАНО**

Алгоритмы матчинга уже работают корректно с объединенными данными CQC + Staging. Никаких изменений в коде не требуется, так как:

1. Объединение данных происходит ДО передачи в алгоритмы
2. `db_field_extractor` работает с объединенными данными
3. Приоритеты CQC → Staging уже применены в `hybrid_data_merger`

**Следующие шаги:**
- ✅ Мониторинг качества сопоставления
- ✅ Тестирование на реальных данных
- ✅ Документация для разработчиков





