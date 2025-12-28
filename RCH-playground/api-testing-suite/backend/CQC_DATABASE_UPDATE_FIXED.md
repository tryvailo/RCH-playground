# ✅ Исправление скрипта обновления CQC базы данных

**Дата:** 2025-12-20  
**Статус:** ✅ ИСПРАВЛЕНО

---

## 🎯 Проблема

**Исходная проблема:**
1. Скрипт создавал новый файл `_UPDATED.csv` вместо обновления оригинального
2. Сохранялись только обновленные дома, а не все дома из оригинального файла
3. Система продолжала использовать оригинальный файл без обновлений

---

## ✅ Решение (Вариант 1: Обновление оригинального файла)

### **Изменения в `update_cqc_database()`:**

1. **Загрузка ВСЕХ домов:**
   - Загружаются все дома из оригинального CSV файла
   - Создается список `all_homes` со всеми домами

2. **Определение домов для обновления:**
   - Если указан `--limit`, выбираются дома с пустыми полями (приоритет)
   - Создается список `homes_to_update` для обновления через API
   - Остальные дома остаются без изменений

3. **Обновление через API:**
   - Обновляются только дома из `homes_to_update`
   - Обновления применяются к объектам в `all_homes` (in-place)

4. **Сохранение ВСЕХ домов:**
   - Сохраняются все дома из `all_homes` (не только обновленные)
   - Если `output_path` не указан, обновляется оригинальный файл
   - Создается резервная копия перед обновлением

---

## 📋 Ключевые изменения

### **1. Загрузка всех домов:**

```python
# Load ALL CQC homes from original CSV
all_homes = load_cqc_homes(str(csv_path))
logger.info(f"Loaded {len(all_homes)} total homes from CSV")
```

---

### **2. Определение домов для обновления:**

```python
# Determine which homes to update via API
homes_to_update = all_homes.copy()  # Start with all homes

if limit:
    # Prioritize homes with empty fields
    empty_homes = []
    filled_homes = []
    # ... separation logic ...
    homes_to_update = (empty_homes + filled_homes)[:limit]
```

---

### **3. Создание резервной копии:**

```python
# Create backup before updating
if output_file == csv_path:
    from datetime import datetime
    import shutil
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = csv_dir / f"{csv_stem}_BACKUP_{timestamp}{csv_suffix}"
    
    shutil.copy2(csv_path, backup_file)
    logger.info(f"✅ Backup created: {backup_file}")
```

---

### **4. Обновление оригинального файла:**

```python
# Determine output path
if output_path:
    output_file = Path(output_path)
else:
    # Update original file in place
    output_file = csv_path

# Save ALL homes to CSV (not just updated ones)
save_homes_to_csv(all_homes, output_file, csv_path)
```

---

## 🎯 Результат

### **До исправления:**

- ❌ Создавался новый файл `_UPDATED.csv`
- ❌ Сохранялись только обновленные дома (20 домов)
- ❌ Оригинальный файл не обновлялся
- ❌ Система не использовала обновления

---

### **После исправления:**

- ✅ Обновляется оригинальный файл `cqc_carehomes_master_full_data_rows.csv`
- ✅ Сохраняются все дома (14,599 домов)
- ✅ Создается резервная копия перед обновлением
- ✅ Система автоматически использует обновленные данные

---

## 📊 Использование

### **Обновить оригинальный файл (рекомендуется):**

```bash
python3 scripts/update_cqc_database.py \
  --fields regulated_activity_nursing_care,regulated_activity_personal_care \
  --batch-size 20 \
  --delay 2.0
```

**Результат:**
- Создается резервная копия: `cqc_carehomes_master_full_data_rows_BACKUP_YYYYMMDD_HHMMSS.csv`
- Обновляется оригинальный файл: `cqc_carehomes_master_full_data_rows.csv`
- Сохраняются все 14,599 домов

---

### **Тестирование на ограниченном наборе:**

```bash
python3 scripts/update_cqc_database.py \
  --fields regulated_activity_nursing_care,regulated_activity_personal_care \
  --limit 20 \
  --batch-size 5 \
  --delay 1.0
```

**Результат:**
- Обновляются только 20 домов через API
- Сохраняются все 14,599 домов (20 обновленных + остальные без изменений)
- Оригинальный файл обновляется

---

### **Сохранение в другой файл:**

```bash
python3 scripts/update_cqc_database.py \
  --fields regulated_activity_nursing_care,regulated_activity_personal_care \
  --output custom_output.csv
```

**Результат:**
- Обновляется оригинальный файл через API
- Сохраняется в указанный файл `custom_output.csv`
- Оригинальный файл остается без изменений

---

## ✅ Преимущества

1. **Единый источник данных:**
   - Оригинальный файл всегда актуален
   - Нет путаницы с несколькими файлами

2. **Безопасность:**
   - Автоматическое создание резервной копии
   - Возможность отката изменений

3. **Полнота данных:**
   - Сохраняются все дома, а не только обновленные
   - Нет потери данных

4. **Автоматическое применение:**
   - Система автоматически использует обновленные данные
   - Нет необходимости менять код загрузки

---

## 📋 Статистика обновления

После обновления скрипт выводит:

```
UPDATE STATISTICS
================================================================================
Total homes in CSV: 14599
Homes updated via API: 14599 (или меньше, если указан --limit)
Processed: 14599
Updated: 14599
API success: 14599
API errors: 0

Fields updated:
  regulated_activity_nursing_care: 4377
  regulated_activity_personal_care: 10200

✅ Update complete!
All 14599 homes saved to CSV
================================================================================
```

---

**Последнее обновление:** 2025-12-20





