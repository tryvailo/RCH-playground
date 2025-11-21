# Local Testing Guide

**Дата:** 2025-01-XX  
**Статус:** ✅ ПРИЛОЖЕНИЕ ЗАПУЩЕНО

---

## 🚀 Статус запуска

### Backend
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Status:** ✅ Запущен

### Frontend
- **URL:** http://localhost:3001
- **Professional Report:** http://localhost:3001/professional-report
- **Status:** ✅ Запущен

---

## 📋 Доступные эндпоинты

### Professional Report
- **POST** `/api/professional-report` - Генерация профессионального отчета
- **GET** `/api/professional-report/{job_id}` - Проверка статуса (будущее)
- **GET** `/api/professional-report/{report_id}/pdf` - Получение PDF (будущее)

### Free Report
- **POST** `/api/free-report` - Генерация бесплатного отчета

### API Documentation
- **GET** `/docs` - Swagger UI документация
- **GET** `/redoc` - ReDoc документация

---

## 🧪 Тестирование Professional Report

### 1. Через Frontend

1. Откройте http://localhost:3001/professional-report
2. Выберите один из 10 тестовых опросников
3. Нажмите "Generate Professional Report"
4. Просмотрите результаты с примененными весами

### 2. Через API (curl)

```bash
# Загрузить тестовый опросник
curl -X POST http://localhost:8000/api/professional-report \
  -H "Content-Type: application/json" \
  -d @api-testing-suite/frontend/public/sample_questionnaires/professional_questionnaire_1_dementia.json
```

### 3. Через Swagger UI

1. Откройте http://localhost:8000/docs
2. Найдите endpoint `/api/professional-report`
3. Нажмите "Try it out"
4. Вставьте JSON из тестового файла
5. Нажмите "Execute"

---

## 📁 Тестовые данные

### Professional Questionnaires (10 файлов):

1. `professional_questionnaire_1_dementia.json` - Rule 2: Dementia
2. `professional_questionnaire_2_diabetes_mobility.json` - Rule 1: High Fall Risk
3. `professional_questionnaire_3_cardiac_nursing.json` - Rule 4: Nursing
4. `professional_questionnaire_4_healthy_residential.json` - Rule 5: Low Budget
5. `professional_questionnaire_5_high_fall_risk.json` - Rule 1: High Fall Risk
6. `professional_questionnaire_6_complex_multiple.json` - Rule 1: Fall Risk (priority)
7. `professional_questionnaire_7_multiple_conditions.json` - Rule 3: Multiple Conditions
8. `professional_questionnaire_8_urgent_only.json` - Rule 6: Urgent Placement
9. `professional_questionnaire_9_nursing_budget.json` - Rule 4 + Rule 5
10. `professional_questionnaire_10_urgent_budget.json` - Rule 6 + Rule 5

**Расположение:** `api-testing-suite/frontend/public/sample_questionnaires/`

---

## 🔍 Проверка функциональности

### 1. Проверка динамических весов

```bash
# Тест с dementia профилем
curl -X POST http://localhost:8000/api/professional-report \
  -H "Content-Type: application/json" \
  -d @api-testing-suite/frontend/public/sample_questionnaires/professional_questionnaire_1_dementia.json \
  | jq '.report.appliedWeights.medical'

# Ожидаемый результат: >= 25.0 (увеличенный вес для dementia)
```

### 2. Проверка валидации

```bash
# Тест с невалидными данными
curl -X POST http://localhost:8000/api/professional-report \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'

# Ожидаемый результат: 400 Bad Request с описанием ошибки
```

### 3. Проверка scoring

```bash
# Тест с fall risk профилем
curl -X POST http://localhost:8000/api/professional-report \
  -H "Content-Type: application/json" \
  -d @api-testing-suite/frontend/public/sample_questionnaires/professional_questionnaire_5_high_fall_risk.json \
  | jq '.report.appliedWeights.safety'

# Ожидаемый результат: >= 24.0 (увеличенный вес для safety)
```

---

## 🐛 Troubleshooting

### Backend не запускается

```bash
# Проверить порт 8000
lsof -ti:8000

# Остановить процесс на порту 8000
lsof -ti:8000 | xargs kill -9

# Запустить заново
cd api-testing-suite/backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend не запускается

```bash
# Проверить порт 3000/3001
lsof -ti:3000
lsof -ti:3001

# Остановить процесс
lsof -ti:3001 | xargs kill -9

# Запустить заново
cd api-testing-suite/frontend
npm run dev
```

### Синтаксические ошибки

```bash
# Проверить синтаксис Python
cd api-testing-suite/backend
python3 -m py_compile main.py

# Проверить TypeScript
cd api-testing-suite/frontend
npm run lint
```

---

## 📊 Мониторинг

### Логи Backend

```bash
# Просмотр логов в реальном времени
tail -f /tmp/backend.log

# Или если запущен в терминале
# Логи выводятся в консоль
```

### Логи Frontend

```bash
# Просмотр логов в реальном времени
tail -f /tmp/frontend.log

# Или если запущен в терминале
# Логи выводятся в консоль
```

---

## ✅ Чеклист тестирования

- [x] Backend запущен на порту 8000
- [x] Frontend запущен на порту 3001
- [ ] Протестировать загрузку questionnaire через UI
- [ ] Протестировать генерацию отчета
- [ ] Проверить применение динамических весов
- [ ] Проверить валидацию входных данных
- [ ] Проверить обработку ошибок
- [ ] Проверить логирование

---

## 🔗 Полезные ссылки

- **Backend API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3001
- **Professional Report:** http://localhost:3001/professional-report
- **Free Report:** http://localhost:3001/free-report

---

**Конец документа**

