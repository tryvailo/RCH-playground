# Next.js Migration - Care Reports

Параллельная реализация Free Report и Professional Report на Next.js/TypeScript с модульной архитектурой Data Engine.

## ⚠️ Важно

Это **параллельная реализация** - существующий код в `api-testing-suite/` **НЕ ТРОГАЕТСЯ**.

## Структура проекта

```
nextjs-migration/
├── app/                    # Next.js App Router
│   ├── api/                # API routes
│   └── ...                 # Pages
├── lib/
│   ├── data-engine/        # ⭐ Data Engine Core
│   ├── reports/            # Free & Professional Reports
│   └── shared/             # Shared types & constants
└── components/             # React Components
```

## Установка

```bash
cd nextjs-migration
npm install
```

## Разработка

```bash
# Запуск Next.js (новый API)
npm run dev

# Старый API (Python) - в отдельном терминале
cd ../api-testing-suite/backend
python -m uvicorn main:app --reload --port 8000
```

## Переключение между версиями

Используйте переменные окружения в `.env.local`:

```bash
# Использовать новый API
NEXT_PUBLIC_USE_NEW_API=true

# Использовать старый API
NEXT_PUBLIC_USE_NEW_API=false
```

## Статус миграции

- ✅ **Фаза 1:** Data Engine Core (завершена)
- ⏳ **Фаза 2:** Free Report (в процессе)
- ⏳ **Фаза 3:** Professional Report (ожидает)
- ⏳ **Фаза 4:** Тестирование (ожидает)

## Документация

- [Data Engine README](./lib/data-engine/README.md)
