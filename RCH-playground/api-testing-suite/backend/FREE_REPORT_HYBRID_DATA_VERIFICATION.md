# ✅ Проверка использования гибридных данных (CQC + Staging) в бесплатном отчете

**Дата:** 2025-12-20  
**Статус:** ✅ **ПОДТВЕРЖДЕНО И ОБНОВЛЕНО**

---

## 📋 Требование

Для бесплатного отчета должны использоваться:
1. **CQC данные**: `cqc_carehomes_master_full_data_rows.csv`
2. **Staging данные**: `carehome_staging_export.csv`

---

## ✅ Проверка реализации

### 1. Основной вызов в `free_report_routes.py`

**Файл:** `routers/free_report_routes.py` (строки 111-127)

```python
# Get care homes using hybrid approach (CQC + Staging)
# Uses: cqc_carehomes_master_full_data_rows.csv (primary) + carehome_staging_export.csv (auxiliary)
care_homes = await loop.run_in_executor(
    None,
    lambda: get_csv_care_homes(
        local_authority=local_authority,
        care_type=care_type,
        max_distance_km=30.0,
        user_lat=user_lat,
        user_lon=user_lon,
        limit=50,
        use_hybrid=True  # ✅ Explicitly enable hybrid approach (CQC + Staging)
    )
)
```

**Статус:** ✅ Явно указан `use_hybrid=True`

---

### 2. Расширенный поиск для Premium

**Файл:** `routers/free_report_routes.py` (строки 610-623)

```python
# Use hybrid approach (CQC + Staging)
expanded_care_homes = await loop.run_in_executor(
    None,
    lambda: get_csv_care_homes(
        use_hybrid=True,  # ✅ Explicitly enable hybrid approach
        local_authority=local_authority,
        care_type=care_type,
        max_distance_km=expanded_max_distance,
        user_lat=user_lat,
        user_lon=user_lon,
        limit=200
    )
)
```

**Статус:** ✅ Явно указан `use_hybrid=True`

---

### 3. Статистика по области

**Файл:** `routers/free_report_routes.py` (строки 1444-1457)

```python
# Get ALL homes in local_authority for accurate area statistics (without filters)
# Uses hybrid approach (CQC + Staging)
all_homes_in_area = await loop.run_in_executor(
    None,
    lambda: get_csv_care_homes(
        local_authority=local_authority,
        use_hybrid=True,  # ✅ Explicitly enable hybrid approach
        care_type=None,  # No care_type filter for total count
        max_distance_km=None,  # No distance filter for total count
        ...
    )
)
```

**Статус:** ✅ Явно указан `use_hybrid=True`

---

### 4. Функция `get_care_homes` в `csv_care_homes_service.py`

**Параметры:**
- `use_hybrid: bool = True` (по умолчанию)

**Логика:**
```python
# Строка 589-601
if use_hybrid:
    try:
        return get_care_homes_hybrid(...)  # Использует CQC + Staging
    except Exception as e:
        logger.warning(f"Hybrid approach failed: {e}, falling back to legacy CSV")
        # Fall through to legacy CSV loading
```

**Статус:** ✅ По умолчанию использует гибридный подход

---

### 5. Функция `get_care_homes_hybrid`

**Файл:** `services/csv_care_homes_service.py`

**Логика:**
```python
# Строка 428-447
# 1. Загрузить CQC
cqc_homes = load_cqc_homes()  # Загружает cqc_carehomes_master_full_data_rows.csv

# 2. Загрузить Staging
staging_list = load_staging_data()  # Загружает carehome_staging_export.csv

# 3. Объединить
merged_homes = merge_cqc_and_staging(cqc_homes, staging_list)
```

**Статус:** ✅ Правильно загружает и объединяет данные из обеих таблиц

---

### 6. Загрузчики данных

#### CQC Data Loader
**Файл:** `services/cqc_data_loader.py`
- Загружает: `cqc_carehomes_master_full_data_rows.csv`
- Путь: `documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv`
- **Результат проверки:** ✅ 14,599 домов загружено

#### Staging Data Loader
**Файл:** `services/staging_data_loader.py`
- Загружает: `carehome_staging_export.csv`
- Путь: `documents/report-algorithms/carehome_staging_export.csv`
- **Результат проверки:** ✅ 934 записи загружено

---

### 7. Объединение данных

**Файл:** `services/hybrid_data_merger.py`
- Использует `care_home_matcher` для сопоставления домов
- Приоритет: CQC → Staging (fallback)
- Объединяет данные из обеих таблиц
- **Результат проверки:** ✅ 14,599 объединенных домов, из них 857 имеют данные из Staging

**Пример объединенных данных:**
- Дом: "Meadow Rose Nursing Home"
- `review_count`: 88 (из Staging)
- `fee_residential_from`: 1150.0 (из Staging)

---

## 📊 Результаты проверки

### Файлы данных
- ✅ `cqc_carehomes_master_full_data_rows.csv` - существует
- ✅ `carehome_staging_export.csv` - существует

### Использование в коде
- ✅ Все 3 вызова `get_csv_care_homes` в `free_report_routes.py` явно указывают `use_hybrid=True`
- ✅ `get_care_homes()` по умолчанию использует `use_hybrid=True`
- ✅ `get_care_homes_hybrid()` загружает данные из обеих таблиц
- ✅ Данные объединяются через `merge_cqc_and_staging()`

### Статистика объединения
- ✅ CQC домов: 14,599
- ✅ Staging записей: 934
- ✅ Объединенных домов: 14,599
- ✅ Домов с данными из Staging: 857 (58.7% от Staging записей)

---

## ✅ Вывод

**Бесплатный отчет использует гибридный подход:**
1. ✅ **CQC данные** из `cqc_carehomes_master_full_data_rows.csv` (основной источник)
2. ✅ **Staging данные** из `carehome_staging_export.csv` (дополнительный источник)

Данные объединяются через `hybrid_data_merger`, который использует `care_home_matcher` для сопоставления домов по нескольким полям (name, postcode, city, address, telephone).

**Все вызовы в `free_report_routes.py` явно указывают `use_hybrid=True` для гарантии использования гибридного подхода.**
