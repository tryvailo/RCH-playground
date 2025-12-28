# 🔍 Детальный анализ Facilities и Funding JSONB полей

**Дата:** 2025-12-20  
**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН

---

## 📊 Структура базы данных

### **JSONB поля в схеме БД:**

Из `care_homes_db_v2_2_PRODUCTION_FINAL.sql`:

```sql
-- ГРУППА 15: JSONB ПОЛЯ (17 полей)
regulated_activities JSONB DEFAULT '{"activities": []}'::jsonb,
facilities JSONB DEFAULT '{}'::jsonb,
staff_information JSONB DEFAULT '{}'::jsonb,
service_user_bands JSONB DEFAULT '[]'::jsonb,
...
```

**Вывод:** ✅ JSONB поля **ЕСТЬ** в схеме базы данных.

---

## 🔍 Анализ Facilities

### **Плоские поля в БД:**

Из схемы БД (строки 135-141):
```sql
wheelchair_access BOOLEAN DEFAULT FALSE,
ensuite_rooms BOOLEAN DEFAULT FALSE,
secure_garden BOOLEAN DEFAULT FALSE,
wifi_available BOOLEAN DEFAULT FALSE,
parking_onsite BOOLEAN DEFAULT FALSE,
```

**Вывод:** ✅ Плоские поля **ЕСТЬ** в схеме БД.

### **JSONB поле `facilities`:**

**Структура (из кода):**
```json
{
  "facilities": {
    "general_amenities": ["parking", "wheelchair_access", "secure_garden", "wifi"],
    "parking_onsite": true,
    "wheelchair_access": true,
    "ensuite_rooms": false,
    "secure_garden": true,
    "wifi_available": true,
    "medical_equipment": ["oxygen", "hospital_bed", "hoist"],
    "on_site_pharmacy": false
  }
}
```

### **Функция извлечения:**

**`get_amenity_value(home, amenity_name)`** из `db_field_extractor.py`:

**Логика:**
1. ✅ Проверяет плоское поле (например, `parking_onsite`)
2. ✅ Если `NULL`, проверяет JSONB `facilities` → `general_amenities` (массив)
3. ✅ Если не найдено, проверяет JSONB `facilities` → `amenity_name` (прямой ключ)
4. ✅ Возвращает `True`/`False`/`None`

**Статус:** ✅ Реализовано и используется в `simple_matching_service.py`

---

## 🔍 Анализ Funding

### **Плоские поля в БД:**

Из схемы БД (проверка):
```sql
-- НЕ НАЙДЕНО в схеме БД!
-- Нет полей: accepts_local_authority_funding, accepts_private_funding, accepts_nhs_funding
```

**Вывод:** ❌ Плоские поля для funding **ОТСУТСТВУЮТ** в схеме БД.

### **JSONB поле для Funding:**

**Проверка схемы БД:**
- ❌ Нет поля `funding` или `funding_acceptance` в JSONB полях
- ⚠️ Возможно, используется другое поле или структура

### **Функция извлечения:**

**`get_funding_acceptance(home, funding_type)`** из `db_field_extractor.py`:

**Логика:**
1. ✅ Проверяет плоские поля:
   - `accepts_self_funding`
   - `accepts_local_authority`
   - `accepts_nhs_chc`
   - `accepts_third_party_topup`
2. ❌ **НЕ проверяет JSONB** (нет логики для JSONB `funding`)

**Проблема:** Функция проверяет плоские поля, которых **НЕТ** в схеме БД!

---

## ⚠️ Критическая проблема

### **Funding поля отсутствуют:**

1. ❌ **В схеме БД:** Нет плоских полей `accepts_*_funding`
2. ❌ **В схеме БД:** Нет JSONB поля `funding` или `funding_acceptance`
3. ❌ **В CSV:** Нет полей funding
4. ⚠️ **В коде:** Функция `get_funding_acceptance()` проверяет несуществующие поля

**Вывод:** Funding данные **НЕ ДОСТУПНЫ** ни в БД, ни в CSV, ни через JSONB.

---

## ✅ Решения

### **Решение 1: Использовать Staging базу данных** ✅

**Подход:**
- Staging база (`carehome_staging_export.csv`) может содержать funding данные
- Использовать гибридный подход: CQC + Staging
- Объединить данные через `hybrid_data_merger.py`

**Статус:** ✅ Уже реализовано в гибридном подходе

**Действие:** Проверить, содержит ли Staging база funding данные

---

### **Решение 2: Обогатить через API** ⚠️

**Подход:**
- Использовать внешние источники для получения funding данных
- Обновить базу данных с этими данными

**Статус:** ⚠️ Требует реализации

---

### **Решение 3: Добавить поля в БД** ⚠️

**Подход:**
- Добавить плоские поля `accepts_*_funding` в схему БД
- Или добавить JSONB поле `funding_acceptance`

**Статус:** ⚠️ Требует миграции БД

---

## 📊 Итоговая таблица

| Категория | Плоские поля в БД | JSONB поле в БД | В CSV | Функция извлечения | Статус |
|-----------|-------------------|-----------------|-------|-------------------|--------|
| **Facilities** | ✅ Есть (5 полей) | ✅ `facilities` | ❌ Нет | ✅ `get_amenity_value()` | ✅ Работает с БД |
| **Funding** | ❌ Нет | ❌ Нет | ❌ Нет | ⚠️ `get_funding_acceptance()` | ❌ Не работает |

---

## 🎯 Рекомендации

### **Приоритет 1: Проверить Staging базу** ⚠️

**Действие:**
- Проверить, содержит ли `carehome_staging_export.csv` funding данные
- Если да, использовать гибридный подход

---

### **Приоритет 2: Обновить функцию `get_funding_acceptance()`** ⚠️

**Проблема:**
- Функция проверяет несуществующие поля
- Нужно добавить проверку JSONB или использовать альтернативные источники

**Действие:**
- Добавить проверку JSONB `funding_acceptance` (если будет добавлено)
- Или использовать данные из Staging базы

---

### **Приоритет 3: Добавить Funding в БД** ⚠️

**Действие:**
- Добавить JSONB поле `funding_acceptance` в схему БД
- Или добавить плоские поля `accepts_*_funding`

**Статус:** ⚠️ Требует миграции БД

---

## ✅ Выводы

### **Facilities:**

1. ✅ **Плоские поля ЕСТЬ** в схеме БД
2. ✅ **JSONB поле ЕСТЬ** в схеме БД
3. ❌ **НЕ экспортированы в CSV**
4. ✅ **Функция извлечения работает** (при загрузке из БД)

**Рекомендация:** ✅ Использовать базу данных напрямую для доступа к facilities данным.

---

### **Funding:**

1. ❌ **Плоские поля ОТСУТСТВУЮТ** в схеме БД
2. ❌ **JSONB поле ОТСУТСТВУЕТ** в схеме БД
3. ❌ **НЕ экспортированы в CSV**
4. ⚠️ **Функция извлечения не работает** (проверяет несуществующие поля)

**Рекомендация:** ⚠️ Проверить Staging базу или добавить funding поля в БД.

---

**Последнее обновление:** 2025-12-20





