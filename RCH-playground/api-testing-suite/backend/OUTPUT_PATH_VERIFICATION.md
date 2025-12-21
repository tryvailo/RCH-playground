# Проверка логики сохранения обновленного CSV

**Дата:** 2025-01-XX  
**Статус:** ✅ ПРОВЕРЕНО

---

## 📋 Логика определения Output Path

### **1. По умолчанию (без `--output`):**

```python
# Сохраняется в той же директории с суффиксом _UPDATED
csv_dir = csv_path.parent
csv_stem = csv_path.stem
csv_suffix = csv_path.suffix
output_file = csv_dir / f"{csv_stem}_UPDATED{csv_suffix}"
```

**Пример:**
- Оригинал: `/documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv`
- Output: `/documents/report-algorithms/cqc_carehomes_master_full_data_rows_UPDATED.csv`
- ✅ **Та же директория**

---

### **2. Относительный путь (`--output updated.csv`):**

```python
# Если относительный путь, делаем его относительно директории оригинала
if not output_path.is_absolute():
    output_path = csv_path.parent / output_path
```

**Пример:**
- Оригинал: `/documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv`
- Команда: `--output updated.csv`
- Output: `/documents/report-algorithms/updated.csv`
- ✅ **Та же директория**

---

### **3. Абсолютный путь (`--output /tmp/updated.csv`):**

```python
# Если абсолютный путь, используем как есть (пользовательский выбор)
output_path = Path(args.output)  # Если абсолютный, остается абсолютным
```

**Пример:**
- Оригинал: `/documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv`
- Команда: `--output /tmp/updated.csv`
- Output: `/tmp/updated.csv`
- ⚠️ **Другая директория** (пользователь явно указал)

---

## ✅ Вывод

**По умолчанию и при относительных путях:**
- ✅ Обновленный файл **ВСЕГДА** сохраняется в той же директории, что и оригинал
- ✅ Имя файла: `{original_name}_UPDATED.csv`

**При абсолютных путях:**
- ⚠️ Сохраняется в указанной директории (пользовательский выбор)

---

## 🔍 Проверка в коде

**Функция `update_cqc_database` (строки 477-503):**

```python
# Save updated CSV if not dry run
if not dry_run and stats['updated'] > 0:
    # Determine output path
    if output_path:
        # User specified output path
        output_file = Path(output_path)
    else:
        # Save in same directory as original, with _UPDATED suffix
        csv_dir = csv_path.parent
        csv_stem = csv_path.stem
        csv_suffix = csv_path.suffix
        output_file = csv_dir / f"{csv_stem}_UPDATED{csv_suffix}"
    
    logger.info(f"\nSaving updated CSV to {output_file}...")
    logger.info(f"Original CSV: {csv_path}")
    logger.info(f"Output CSV: {output_file}")
    logger.info(f"Same directory: {output_file.parent == csv_path.parent}")
    
    # Save updated homes to CSV
    try:
        save_homes_to_csv(homes, output_file, csv_path)
        logger.info(f"✅ Successfully saved {len(homes)} homes to {output_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save CSV: {e}")
        ...
```

**Функция `main` (строки 597-606):**

```python
# Output path
if args.output:
    # User specified output path
    output_path = Path(args.output)
    # If relative path, make it relative to original CSV directory
    if not output_path.is_absolute():
        output_path = csv_path.parent / output_path
else:
    # Default: save in same directory as original with _UPDATED suffix
    output_path = None  # Will be set in update_cqc_database function
```

---

## ✅ Итог

**Логика правильная:**
- ✅ По умолчанию: файл сохраняется в той же директории
- ✅ Относительный путь: файл сохраняется в той же директории
- ✅ Абсолютный путь: файл сохраняется в указанной директории (пользовательский выбор)

**Статус:** ✅ **ПОДТВЕРЖДЕНО**

