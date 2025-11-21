# 📊 Free Report Viewer - Инструкция по установке и запуску

## ✅ Реализованный функционал

### 1. Структура проекта

```
RCH-playground/
├── src/free_report_viewer/          # Основной модуль
│   ├── __init__.py
│   ├── models.py                    # Pydantic модели
│   ├── api.py                       # API клиент
│   ├── viewer.py                    # Streamlit интерфейс
│   ├── tests/                       # Тесты
│   │   ├── test_models.py
│   │   └── test_api.py
│   └── README.md
├── pages/
│   └── 1_Free_Report_Viewer.py     # Streamlit страница
├── app.py                           # Основной Streamlit app
├── data/sample_questionnaires/      # Примеры анкет
│   ├── questionnaire_1.json
│   ├── questionnaire_2.json
│   └── questionnaire_3.json
└── requirements-streamlit.txt      # Зависимости
```

### 2. Функционал

✅ **Сайдбар:**
- Выбор из 3 дефолтных JSON файлов
- `st.file_uploader` для загрузки своего JSON
- Кнопка "Сгенерировать отчёт"

✅ **Парсинг и отображение:**
- Парсинг в `QuestionnaireResponse` (pydantic)
- Красивая карточка с ключевыми данными:
  - Postcode
  - Budget
  - Care Type
  - CHC Probability

✅ **Генерация отчёта:**
- POST запрос на `/api/free-report`
- Mock данные с 3 домами
- **ОБЯЗАТЕЛЬНЫЙ** Fair Cost Gap блок

✅ **Премиум оформление:**
- Цвета: `#1E2A44`, `#10B981`, `#EF4444`
- Шрифты: Inter/Poppins
- Карточки с тенями и закруглениями

## 🚀 Быстрый старт

### Шаг 1: Установка зависимостей

```bash
# Для Streamlit приложения
pip install -r requirements-streamlit.txt

# Для FastAPI backend (если ещё не установлены)
cd api-testing-suite/backend
pip install -r requirements.txt
```

### Шаг 2: Запуск FastAPI Backend

```bash
cd api-testing-suite/backend
uvicorn main:app --reload --port 8000
```

Backend будет доступен на `http://localhost:8000`

### Шаг 3: Запуск Streamlit приложения

**Вариант A: Основной app.py (с табами)**

```bash
streamlit run app.py
```

**Вариант B: Отдельная страница**

```bash
streamlit run pages/1_Free_Report_Viewer.py
```

Приложение будет доступно на `http://localhost:8501`

## 📋 Использование

1. **Выберите анкету:**
   - Из выпадающего списка в сайдбаре (3 примера)
   - Или загрузите свой JSON файл

2. **Просмотрите данные:**
   - После выбора отобразится карточка с ключевыми данными

3. **Сгенерируйте отчёт:**
   - Нажмите "🚀 Generate Report"
   - Дождитесь загрузки данных с API

4. **Просмотрите результаты:**
   - 3 рекомендованных дома престарелых
   - Fair Cost Gap анализ

## 🔌 API Endpoint

### POST /api/free-report

**Расположение:** `api-testing-suite/backend/main.py` (строки 3743-3834)

**Request:**
```json
{
  "postcode": "SW1A 1AA",
  "budget": 1200.0,
  "care_type": "residential",
  "chc_probability": 35.5
}
```

**Response:**
```json
{
  "questionnaire": {...},
  "care_homes": [
    {
      "name": "Sunshine Care Home",
      "address": "123 High Street",
      "postcode": "SW1A 1AA",
      "weekly_cost": 1080.0,
      "care_types": ["residential", "respite"],
      "rating": "Good",
      "distance_km": 2.5,
      "features": ["Garden", "Activities", "24/7 Care"]
    },
    ...
  ],
  "fair_cost_gap": {
    "weekly_gap": 300.0,
    "annual_gap": 15600.0,
    "local_authority_rate": 900.0,
    "care_home_rate": 1200.0,
    "explanation": "...",
    "recommendations": [...]
  },
  "generated_at": "2024-01-01T12:00:00",
  "report_id": "uuid-here"
}
```

## 🧪 Тестирование

```bash
# Запуск всех тестов модуля
pytest src/free_report_viewer/tests/ -v

# Тесты моделей
pytest src/free_report_viewer/tests/test_models.py -v

# Тесты API клиента
pytest src/free_report_viewer/tests/test_api.py -v

# С покрытием
pytest src/free_report_viewer/tests/ --cov=src/free_report_viewer --cov-report=html
```

## 🎨 Стилизация

### Цветовая схема

- **#1E2A44** - Тёмно-синий (основной цвет, заголовки)
- **#10B981** - Зелёный (акцентные кнопки, успех)
- **#EF4444** - Красный (Fair Cost Gap блок, предупреждения)

### Шрифты

- **Inter** - основной текст (300, 400, 500, 600, 700)
- **Poppins** - заголовки (400, 500, 600, 700)

### Компоненты

- Карточки с `border-radius: 12px`
- Тени: `box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)`
- Hover эффекты с плавными переходами
- Градиенты для метрик

## 📝 Примеры анкет

### questionnaire_1.json (London)
```json
{
  "postcode": "SW1A 1AA",
  "budget": 1200.0,
  "care_type": "residential",
  "chc_probability": 35.5
}
```

### questionnaire_2.json (Manchester)
```json
{
  "postcode": "M1 1AA",
  "budget": 1500.0,
  "care_type": "nursing",
  "chc_probability": 42.3
}
```

### questionnaire_3.json (Birmingham)
```json
{
  "postcode": "B1 1AA",
  "budget": 1000.0,
  "care_type": "dementia",
  "chc_probability": 28.7
}
```

## ⚠️ Важные замечания

1. **Fair Cost Gap блок обязателен** - всегда присутствует в отчёте
2. **Минимум 3 дома** - отчёт всегда содержит минимум 3 рекомендованных дома
3. **Backend должен быть запущен** - перед генерацией отчёта убедитесь, что FastAPI сервер работает на порту 8000

## 🐛 Troubleshooting

### Ошибка подключения к API

```
Error generating report: Connection refused
```

**Решение:** 
1. Проверьте, что FastAPI backend запущен: `curl http://localhost:8000/`
2. Убедитесь, что порт 8000 свободен

### Ошибка парсинга JSON

```
Error parsing questionnaire: ...
```

**Решение:** 
- Проверьте формат JSON файла
- Обязательные поля: `postcode`
- Опциональные: `budget`, `care_type`, `chc_probability`

### Модуль не найден

```
ModuleNotFoundError: No module named 'free_report_viewer'
```

**Решение:**
- Убедитесь, что `src/` находится в корне проекта
- Проверьте, что путь добавлен в `sys.path`

## 📚 Дополнительная документация

- Подробная документация модуля: `src/free_report_viewer/README.md`
- Примеры использования в тестах: `src/free_report_viewer/tests/`

## ✅ Чеклист реализации

- [x] Создана структура модуля `src/free_report_viewer/`
- [x] Реализованы Pydantic модели (`models.py`)
- [x] Создан API клиент (`api.py`)
- [x] Реализован Streamlit интерфейс (`viewer.py`)
- [x] Добавлен FastAPI endpoint `/api/free-report`
- [x] Созданы 3 примера анкет
- [x] Реализованы тесты
- [x] Создана документация
- [x] Применено премиум оформление

## 🎯 Следующие шаги (опционально)

- [ ] Интеграция с реальной базой данных домов престарелых
- [ ] Реализация реального алгоритма расчёта Fair Cost Gap
- [ ] Добавление экспорта отчётов в PDF
- [ ] Интеграция с картами для отображения местоположения домов
- [ ] Добавление фильтров и сортировки для домов

