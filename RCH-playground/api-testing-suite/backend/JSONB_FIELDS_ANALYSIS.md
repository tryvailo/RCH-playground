# 🔍 Анализ JSONB полей (Facilities и Funding) в CQC базе данных

**Дата:** 2025-12-20  
**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН

---

## 📊 Общая информация

**Источник данных:** CQC CSV (`cqc_carehomes_master_full_data_rows.csv`)  
**Всего домов:** 14,599  
**Всего колонок:** 128

---

## 🔍 Анализ Facilities (Удобства)

### **Поля, необходимые для матчинга:**

| Поле | Статус в CSV | Альтернатива |
|------|--------------|--------------|
| `parking_onsite` | ❌ Отсутствует | ⚠️ Возможно в JSONB `facilities` |
| `wheelchair_access` | ❌ Отсутствует | ⚠️ Возможно в JSONB `facilities` |
| `ensuite_rooms` | ❌ Отсутствует | ⚠️ Возможно в JSONB `facilities` |
| `secure_garden` | ❌ Отсутствует | ⚠️ Возможно в JSONB `facilities` |
| `wifi_available` | ❌ Отсутствует | ⚠️ Возможно в JSONB `facilities` |

### **Проверка CSV:**

**Результат:** ❌ Поля `facilities`, `amenities`, `features` **НЕ НАЙДЕНЫ** в CSV

**Вывод:** JSONB структуры **НЕ ЭКСПОРТИРОВАНЫ** в CSV файл. Они могут быть в базе данных, но не включены в экспорт.

---

### **Реализация в коде:**

**Функция извлечения:** `get_amenity_value(home, key)` из `db_field_extractor.py`

**Логика:**
1. Проверяет плоское поле (например, `parking_onsite`)
2. Если `NULL`, проверяет JSONB `facilities` → `key`
3. Возвращает `True`/`False`/`None`

**Пример использования:**
```python
from services.db_field_extractor import get_amenity_value

parking = get_amenity_value(home, 'parking_onsite')
wheelchair = get_amenity_value(home, 'wheelchair_access')
secure_garden = get_amenity_value(home, 'secure_garden')
```

**Статус:** ✅ Реализовано в `simple_matching_service.py`

---

## 🔍 Анализ Funding (Финансирование)

### **Поля, необходимые для матчинга:**

| Поле | Статус в CSV | Альтернатива |
|------|--------------|--------------|
| `accepts_local_authority_funding` | ❌ Отсутствует | ⚠️ Возможно в JSONB `funding` |
| `accepts_private_funding` | ❌ Отсутствует | ⚠️ Возможно в JSONB `funding` |
| `accepts_nhs_funding` | ❌ Отсутствует | ⚠️ Возможно в JSONB `funding` |
| `accepts_self_funding` | ❌ Отсутствует | ⚠️ Возможно в JSONB `funding` |

### **Проверка CSV:**

**Результат:** ❌ Поля `funding`, `funding_acceptance` **НЕ НАЙДЕНЫ** в CSV

**Вывод:** JSONB структуры **НЕ ЭКСПОРТИРОВАНЫ** в CSV файл. Они могут быть в базе данных, но не включены в экспорт.

---

### **Реализация в коде:**

**Функция извлечения:** `get_funding_acceptance(home, funding_type)` из `db_field_extractor.py`

**Логика:**
1. Проверяет плоские поля (например, `accepts_local_authority_funding`)
2. Если `NULL`, проверяет JSONB `funding_acceptance` → `funding_type`
3. Возвращает `True`/`False`/`None`

**Пример использования:**
```python
from services.db_field_extractor import get_funding_acceptance

la_funding = get_funding_acceptance(home, 'local_authority')
private_funding = get_funding_acceptance(home, 'private')
nhs_funding = get_funding_acceptance(home, 'nhs')
self_funding = get_funding_acceptance(home, 'self_funding')
```

**Статус:** ✅ Реализовано в `simple_matching_service.py`

---

## 📋 Структура JSONB полей (из кода)

### **Facilities JSONB:**

**Предполагаемая структура:**
```json
{
  "facilities": {
    "parking": true,
    "wheelchair_access": true,
    "ensuite_rooms": false,
    "secure_garden": true,
    "wifi": true,
    "lift": true,
    "dining_room": true,
    "lounge": true,
    "library": false,
    "hairdressing": true
  }
}
```

**Или альтернативная структура:**
```json
{
  "amenities": [
    "parking",
    "wheelchair_access",
    "secure_garden",
    "wifi"
  ]
}
```

---

### **Funding JSONB:**

**Предполагаемая структура:**
```json
{
  "funding_acceptance": {
    "local_authority": true,
    "private": true,
    "nhs": false,
    "self_funding": true
  }
}
```

**Или альтернативная структура:**
```json
{
  "funding": {
    "accepts_local_authority": true,
    "accepts_private": true,
    "accepts_nhs": false,
    "accepts_self_funding": true
  }
}
```

---

## ⚠️ Проблема

### **JSONB структуры НЕ ЭКСПОРТИРОВАНЫ в CSV**

**Причина:**
- CSV экспорт из базы данных не включает JSONB поля
- JSONB данные остаются только в базе данных
- При загрузке из CSV эти данные теряются

**Последствия:**
- Функции `get_amenity_value()` и `get_funding_acceptance()` не могут извлечь данные из JSONB
- Они работают только с плоскими полями, которые отсутствуют в CSV

---

## ✅ Решения

### **Решение 1: Использовать базу данных напрямую** ✅

**Статус:** ✅ Уже реализовано

**Подход:**
- Загружать данные напрямую из базы данных (не из CSV)
- Использовать `AsyncDataLoader` для загрузки из БД
- JSONB поля будут доступны через `db_field_extractor.py`

**Использование:**
```python
from services.data_loader import AsyncDataLoader

loader = AsyncDataLoader()
homes = await loader.load_initial_data(...)  # Загружает из БД с JSONB
```

---

### **Решение 2: Обогатить CSV через API** ⚠️

**Подход:**
- Использовать внешние API для получения данных о facilities
- Например, Google Places API может предоставить информацию о parking, wheelchair access
- Обновить CSV с этими данными

**Статус:** ⚠️ Требует реализации

---

### **Решение 3: Использовать Staging базу данных** ✅

**Подход:**
- Staging база (`carehome_staging_export.csv`) может содержать facilities данные
- Использовать гибридный подход: CQC + Staging
- Объединить данные через `hybrid_data_merger.py`

**Статус:** ✅ Уже реализовано в гибридном подходе

---

## 📊 Текущее состояние

### **В CSV:**

| Категория | Статус |
|-----------|--------|
| **Facilities** | ❌ Отсутствуют |
| **Funding** | ❌ Отсутствуют |
| **JSONB структуры** | ❌ Не экспортированы |

### **В базе данных (предположительно):**

| Категория | Статус |
|-----------|--------|
| **Facilities JSONB** | ⚠️ Вероятно есть |
| **Funding JSONB** | ⚠️ Вероятно есть |
| **Доступ через БД** | ✅ Реализовано |

---

## 🎯 Рекомендации

### **Приоритет 1: Использовать базу данных напрямую** ✅

**Действие:**
- При загрузке данных использовать `AsyncDataLoader` вместо CSV
- Это обеспечит доступ к JSONB полям

**Статус:** ✅ Уже реализовано в `report_routes.py` (fallback на `AsyncDataLoader`)

---

### **Приоритет 2: Проверить Staging базу** ⚠️

**Действие:**
- Проверить, содержит ли `carehome_staging_export.csv` facilities и funding данные
- Если да, использовать гибридный подход

**Статус:** ⚠️ Требует проверки

---

### **Приоритет 3: Обогатить через API** ⚠️

**Действие:**
- Использовать Google Places API для получения facilities данных
- Обновить CSV с этими данными

**Статус:** ⚠️ Требует реализации

---

## ✅ Выводы

### **Текущее состояние:**

1. ❌ **JSONB структуры НЕ экспортированы в CSV**
2. ✅ **Функции извлечения реализованы** (`get_amenity_value`, `get_funding_acceptance`)
3. ✅ **Поддержка загрузки из БД реализована** (`AsyncDataLoader`)
4. ⚠️ **При загрузке из CSV JSONB данные недоступны**

### **Рекомендация:**

✅ **Использовать базу данных напрямую** для доступа к JSONB полям, или использовать гибридный подход (CQC + Staging) для получения facilities и funding данных.

---

**Последнее обновление:** 2025-12-20





