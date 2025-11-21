# Объяснение двух интерфейсов

## Проблема

У вас есть **два разных веб-приложения**, которые работают на разных портах:

### 1. Streamlit приложение (Free Report Viewer)
- **Файл**: `app.py`
- **Порт**: 8501
- **URL**: http://localhost:8501
- **Содержит**: Только Free Report Viewer
- **Технология**: Python Streamlit

### 2. React фронтенд (старое приложение)
- **Папка**: `api-testing-suite/frontend/`
- **Порт**: 3000
- **URL**: http://localhost:3000
- **Содержит**: Вкладки Perplexity, Google Places, CQC Explorer и т.д.
- **Технология**: React + TypeScript + Vite

## Почему они разделены?

Это два разных приложения:
- **Streamlit** (`app.py`) - новое приложение для Free Report Viewer
- **React** (`api-testing-suite/frontend`) - старое приложение для тестирования API

## Решение: Объединить в один интерфейс

Есть два варианта:

### Вариант 1: Добавить Free Report Viewer в React приложение
Добавить новую страницу/вкладку в React приложение с Free Report Viewer.

### Вариант 2: Добавить старые вкладки в Streamlit приложение
Добавить вкладки Perplexity, Google Places и т.д. в `app.py`.

## Текущий статус

- ✅ **FastAPI Backend**: http://localhost:8000 (работает)
- ✅ **Streamlit App**: http://localhost:8501 (работает)
- ❓ **React Frontend**: http://localhost:3000 (нужно запустить)

## Как запустить React фронтенд

```bash
cd api-testing-suite/frontend
npm install
npm run dev
```

Затем откройте http://localhost:3000

## Рекомендация

Объединить оба интерфейса в один Streamlit приложение, добавив вкладки для всех функций.

