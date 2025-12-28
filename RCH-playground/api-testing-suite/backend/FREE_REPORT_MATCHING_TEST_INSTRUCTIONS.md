# Инструкция по проверке матчинга бесплатного отчета

## 🚀 Быстрый старт

### 1. Запустите сервер (если еще не запущен)

```bash
cd RCH-playground/RCH-playground/api-testing-suite/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер должен быть доступен на `http://localhost:8000`

### 2. Запустите тест матчинга

В **новом терминале**:

```bash
cd RCH-playground/RCH-playground/api-testing-suite/backend
python3 test_free_report_matching.py
```

## 📋 Что проверяет тест

Тест проверяет:
1. ✅ Загрузку данных из CQC + Staging (гибридный подход)
2. ✅ Использование `extract_weekly_price()` для цен из Staging
3. ✅ Использование `get_availability_info()` для availability из Staging
4. ✅ Использование `get_review_data()` для reviews из Staging
5. ✅ Подбор топ 3 домов (Safe Bet, Best Reputation, Smart Value)

## 📊 Ожидаемый вывод

Тест выводит:
- Информацию о каждом из 3 подобранных домов
- Источники данных (CQC vs Staging) для каждого дома
- Сводку использования данных из обеих баз

## 📁 Результаты

Результаты сохраняются в:
- `free_report_matching_test_result.json` - JSON с полными результатами

## 🔍 Проверка источников данных

Тест проверяет наличие данных из:

### CQC (критические поля):
- `cqc_rating_overall` / `rating` - CQC рейтинг
- `cqc_rating_safe` - CQC безопасность
- `latitude`, `longitude` - координаты

### Staging (предпочтительные поля):
- `fee_residential_from`, `fee_dementia_from`, `fee_nursing_from` - цены
- `review_average_score`, `review_count` - отзывы
- `beds_available`, `has_availability` - доступность
- `wheelchair_access`, `wifi_available`, `parking_onsite` - удобства

## ⚠️ Устранение неполадок

### Сервер не запускается
- Проверьте, что порт 8000 свободен: `lsof -ti:8000`
- Проверьте логи сервера на наличие ошибок

### Ошибка подключения
- Убедитесь, что сервер запущен: `curl http://localhost:8000/health`
- Проверьте, что используется правильный URL в тесте

### Нет данных в результатах
- Проверьте, что база данных содержит данные
- Проверьте, что CSV файл со Staging данными доступен
- Проверьте логи сервера на наличие ошибок загрузки данных





