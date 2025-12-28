# ✅ Скрипт проверки матчинга бесплатного отчета готов

## 📋 Что было сделано

1. ✅ Создан скрипт `test_free_report_matching.py` для проверки матчинга
2. ✅ Скрипт проверяет использование данных из CQC + Staging
3. ✅ Скрипт анализирует источники данных для каждого подобранного дома
4. ✅ Создана инструкция по использованию

## 🚀 Как запустить

### Вариант 1: Если сервер уже запущен

```bash
cd RCH-playground/RCH-playground/api-testing-suite/backend
python3 test_free_report_matching.py
```

### Вариант 2: Запустить сервер и тест

**Терминал 1 (сервер):**
```bash
cd RCH-playground/RCH-playground/api-testing-suite/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Терминал 2 (тест):**
```bash
cd RCH-playground/RCH-playground/api-testing-suite/backend
python3 test_free_report_matching.py
```

## 📊 Что проверяет скрипт

### 1. Загрузка данных
- ✅ Используется ли гибридный подход (CQC + Staging)
- ✅ Правильно ли объединяются данные

### 2. Использование полей из Staging
- ✅ **Pricing**: `fee_residential_from`, `fee_dementia_from`, `fee_nursing_from`
- ✅ **Reviews**: `review_average_score`, `review_count`
- ✅ **Availability**: `beds_available`, `has_availability`, `beds_total`
- ✅ **Amenities**: `wheelchair_access`, `wifi_available`, `parking_onsite`

### 3. Использование полей из CQC
- ✅ **Ratings**: `cqc_rating_overall`, `cqc_rating_safe`
- ✅ **Location**: `latitude`, `longitude`
- ✅ **Care Types**: `care_types`

### 4. Подбор топ 3 домов
- ✅ **Safe Bet**: Максимальная безопасность (safety + quality)
- ✅ **Best Reputation**: Лучшая репутация (quality + reviews)
- ✅ **Smart Value**: Оптимальное соотношение цена/качество

## 📈 Ожидаемый вывод

Скрипт выводит:
1. Информацию о анкете
2. Для каждого из 3 домов:
   - Название, postcode, город
   - Источники данных (CQC vs Staging)
   - Match Score и reasoning
3. Сводку использования данных:
   - Сколько домов имеют CQC данные
   - Сколько домов имеют Staging Pricing
   - Сколько домов имеют Staging Reviews
   - Сколько домов имеют Staging Availability

## 💾 Результаты

Результаты сохраняются в:
- `free_report_matching_test_result.json` - полные результаты в JSON формате

## ⚠️ Текущий статус

**Сервер не запущен** - нужно запустить сервер перед тестированием.

См. `FREE_REPORT_MATCHING_TEST_INSTRUCTIONS.md` для подробных инструкций.





