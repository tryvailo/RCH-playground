# Структура интерфейсов RightCareHome

## Основной интерфейс

### React фронтенд (API Testing Suite)
- **Папка**: `api-testing-suite/frontend/`
- **Порт**: 3000
- **URL**: http://localhost:3000
- **Технология**: React + TypeScript + Vite
- **Содержит**:
  - 🔍 Perplexity Research Explorer
  - 🌐 Google Places Explorer
  - 🏥 CQC Explorer
  - 🏢 Companies House Explorer
  - 🍽️ FSA Explorer
  - 🔥 Firecrawl Explorer
  - 🧪 Test Runner
  - 📊 Analytics Dashboard
  - ⚙️ API Configuration

## Backend

**FastAPI backend**:
- **Порт**: 8000
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

Backend предоставляет endpoints для React фронтенда:
- `/api/perplexity/*` - Perplexity API
- `/api/google-places/*` - Google Places API
- `/api/cqc/*` - CQC API
- `/api/companies-house/*` - Companies House API
- `/api/fsa/*` - FSA API
- `/api/firecrawl/*` - Firecrawl API
- `/api/test/comprehensive` - Comprehensive testing
- `/api/config/*` - API configuration

## Как запустить

### 1. FastAPI Backend (обязательно)
```bash
cd api-testing-suite/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend будет доступен на: http://localhost:8000

### 2. React Frontend (API Testing Suite)
```bash
cd api-testing-suite/frontend
npm install
npm run dev
```
Frontend будет доступен на: http://localhost:3000

## Текущий статус

- ✅ **FastAPI Backend**: http://localhost:8000 (работает)
- ✅ **React Frontend**: http://localhost:3000 (основной интерфейс)

## Структура проекта

```
RCH-playground/
├── api-testing-suite/
│   ├── backend/          # FastAPI backend
│   └── frontend/         # React фронтенд
├── src/
│   └── free_report_viewer/  # Free Report Viewer (отдельное приложение)
└── ...
```

## Дополнительные компоненты

### Free Report Viewer
- **Папка**: `src/free_report_viewer/`
- **Технология**: Python Streamlit
- **Назначение**: Генерация отчетов из questionnaire
- **Запуск**: `python3 -m streamlit run src/free_report_viewer/viewer.py`
- **Порт**: 8501 (по умолчанию)

