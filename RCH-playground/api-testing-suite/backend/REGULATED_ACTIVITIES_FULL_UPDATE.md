# 🔄 Полное обновление Regulated Activities

**Дата начала:** 2025-12-20  
**Статус:** 🔄 ВЫПОЛНЯЕТСЯ

---

## 📋 Параметры обновления

**Команда:**
```bash
python3 scripts/update_cqc_database.py \
  --fields regulated_activity_nursing_care,regulated_activity_personal_care \
  --batch-size 20 \
  --delay 2.0
```

**Параметры:**
- **Поля:** `regulated_activity_nursing_care`, `regulated_activity_personal_care`
- **Batch size:** 20 домов
- **Delay:** 2.0 секунды между батчами
- **Всего домов:** 14,599
- **Ожидаемое время:** ~24 минуты

---

## 📊 Ожидаемые результаты

### **До обновления:**
- `regulated_activity_nursing_care`: 0.0% (всегда `FALSE`)
- `regulated_activity_personal_care`: 2.0% (почти всегда `FALSE`)

### **После обновления:**
- `regulated_activity_nursing_care`: ожидается ~30% (дома с nursing care)
- `regulated_activity_personal_care`: ожидается ~70-80% (большинство домов)

---

## 🔍 Мониторинг

**Лог файл:**
```bash
tail -f /tmp/cqc_regulated_activities_full_update.log
```

---

**Статус:** 🔄 ВЫПОЛНЯЕТСЯ (фоновый процесс)

