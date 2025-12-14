# Руководство по локальной разработке

**Дата:** 2025-01-XX  
**Статус:** ✅ Готово к использованию

---

## Совместимость с локальным запуском

Текущая архитектура **полностью совместима** с локальным запуском. Все компоненты имеют fallback механизмы для работы без Vercel-специфичных сервисов.

---

## Компоненты и их локальная поддержка

### ✅ 1. Job Queue Service

**Статус:** Полностью работает локально

**Механизм:**
- **Production (Vercel):** Использует Redis (Vercel KV)
- **Local Development:** Автоматически использует in-memory storage

**Код:**
```python
# services/job_queue_service.py
if REDIS_AVAILABLE:
    redis_url = os.getenv('KV_REDIS_URL') or os.getenv('REDIS_URL')
    if redis_url:
        # Использует Redis
    else:
        # Fallback на in-memory
        self._in_memory_storage = {}
else:
    # Fallback на in-memory
    self._in_memory_storage = {}
```

**Использование:**
- Работает автоматически, без дополнительной настройки
- Данные хранятся в памяти (теряются при перезапуске)
- Для персистентности можно использовать локальный Redis

---

### ✅ 2. Retry Mechanism

**Статус:** Полностью работает локально

**Механизм:**
- **Production (Vercel):** Использует Vercel Cron (каждые 5 минут)
- **Local Development:** Использует `LocalRetryScheduler` (asyncio background task)

**Код:**
```python
# main.py lifespan
is_vercel = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
if not is_vercel:
    # Запускает LocalRetryScheduler
    scheduler = get_scheduler()
    await scheduler.start()
```

**Использование:**
- Автоматически запускается при старте приложения
- Работает в фоне, проверяет частичные отчеты каждые 5 минут
- Останавливается при shutdown приложения

---

### ✅ 3. API Endpoints

**Статус:** Все endpoints работают локально

**Endpoints:**
- `POST /api/professional-report/start` - создание job
- `GET /api/professional-report/status/{job_id}` - статус job
- `GET /api/professional-report/result/{job_id}` - результат
- `POST /api/professional-report/retry/{job_id}` - ручной retry
- `GET /api/professional-report/missing-sources/{job_id}` - недостающие источники
- `GET /api/professional-report/retry-status/{job_id}` - статус retry
- `GET /api/cron/retry-missing-data` - cron endpoint (работает как обычный endpoint локально)

**Использование:**
- Все endpoints доступны через FastAPI
- Работают идентично production версии

---

## Запуск локально

### 1. Базовый запуск

```bash
cd RCH-playground/api-testing-suite/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. С локальным Redis (опционально)

Если хотите персистентность данных между перезапусками:

```bash
# Установить Redis локально
# macOS:
brew install redis
brew services start redis

# Linux:
sudo apt-get install redis-server
sudo systemctl start redis

# Windows:
# Использовать WSL или Docker
```

```bash
# Установить переменную окружения
export REDIS_URL="redis://localhost:6379"

# Запустить приложение
uvicorn main:app --reload
```

### 3. Проверка работы

```bash
# 1. Проверить health
curl http://localhost:8000/health

# 2. Создать job
curl -X POST http://localhost:8000/api/professional-report/start \
  -H "Content-Type: application/json" \
  -d '{"questionnaire": {...}}'

# 3. Проверить статус
curl http://localhost:8000/api/professional-report/status/{job_id}

# 4. Проверить retry scheduler (локально)
curl http://localhost:8000/api/cron/retry-missing-data
```

---

## Отличия локального запуска от Production

### 1. Хранение данных

| Компонент | Production (Vercel) | Local Development |
|-----------|---------------------|-------------------|
| Job Queue | Redis (Vercel KV) | In-memory storage |
| Персистентность | ✅ Данные сохраняются | ❌ Данные теряются при перезапуске |
| Масштабирование | ✅ Множественные инстансы | ❌ Один инстанс |

### 2. Retry Scheduler

| Компонент | Production (Vercel) | Local Development |
|-----------|---------------------|-------------------|
| Механизм | Vercel Cron | asyncio background task |
| Частота | Каждые 5 минут | Каждые 5 минут |
| Запуск | Автоматически Vercel | Автоматически при старте app |

### 3. Timeout

| Компонент | Production (Vercel) | Local Development |
|-----------|---------------------|-------------------|
| Function timeout | 300s (Pro) / 900s (Enterprise) | Нет ограничений |
| Retry timeout | 3 часа | 3 часа |

---

## Настройка для локальной разработки

### 1. Переменные окружения

Создайте `.env` файл (опционально):

```bash
# .env
REDIS_URL=redis://localhost:6379  # Опционально, для персистентности
VERCEL=0  # Явно указать, что это не Vercel
```

### 2. Отключение Vercel-специфичных функций

Все автоматически определяется через переменные окружения:
- Если `VERCEL=1` или `VERCEL_ENV` установлен → используется Vercel режим
- Иначе → используется локальный режим

### 3. Логирование

Локальный retry scheduler логирует все действия:

```
✅ Local retry scheduler started (for development)
🔄 Checking partial jobs...
✅ Job abc123: Retried 2 sources successfully
✅ Job abc123: All sources loaded, marked as completed
```

---

## Тестирование локально

### 1. Тест создания job

```python
import requests

response = requests.post(
    "http://localhost:8000/api/professional-report/start",
    json={"questionnaire": {...}}
)
job_id = response.json()["job_id"]
print(f"Job created: {job_id}")
```

### 2. Тест проверки статуса

```python
response = requests.get(
    f"http://localhost:8000/api/professional-report/status/{job_id}"
)
status = response.json()
print(f"Status: {status['status']}, Progress: {status['progress']}%")
```

### 3. Тест retry

```python
# Создать частичный отчет (с недостающими данными)
# Затем вызвать retry
response = requests.post(
    f"http://localhost:8000/api/professional-report/retry/{job_id}"
)
result = response.json()
print(f"Retried: {result['retry_result']['success_count']} sources")
```

### 4. Тест cron endpoint (локально)

```python
response = requests.get(
    "http://localhost:8000/api/cron/retry-missing-data"
)
print(response.json())
```

---

## Отладка

### 1. Проверка работы retry scheduler

```python
# В Python shell или debugger
from services.local_retry_scheduler import get_scheduler
scheduler = get_scheduler()
print(f"Running: {scheduler._running}")
print(f"Task: {scheduler._task}")
```

### 2. Проверка in-memory storage

```python
from services.job_queue_service import JobQueueService
service = JobQueueService()
print(f"Jobs in memory: {len(service._in_memory_storage)}")
for job_id, job in service._in_memory_storage.items():
    print(f"  {job_id}: {job.get('status')}")
```

### 3. Логи

Все компоненты логируют важные события:
- ✅ Успешные операции
- ⚠️ Предупреждения
- ❌ Ошибки

Проверяйте консоль при запуске `uvicorn` для логов.

---

## Известные ограничения локального запуска

### 1. In-memory storage

- **Проблема:** Данные теряются при перезапуске
- **Решение:** Использовать локальный Redis для персистентности

### 2. Один инстанс

- **Проблема:** Нельзя масштабировать на несколько серверов
- **Решение:** Для production использовать Vercel или другой cloud provider

### 3. Нет автоматического мониторинга

- **Проблема:** Нет встроенного мониторинга как в Vercel
- **Решение:** Использовать внешние инструменты (Sentry, DataDog, etc.)

---

## Миграция с локального на Production

### Шаги:

1. **Настроить Vercel KV (Redis)**
   ```bash
   vercel kv create
   ```

2. **Установить переменные окружения в Vercel**
   ```
   KV_REDIS_URL=<your-redis-url>
   ```

3. **Настроить Vercel Cron**
   ```json
   // vercel.json
   {
     "crons": [{
       "path": "/api/cron/retry-missing-data",
       "schedule": "*/5 * * * *"
     }]
   }
   ```

4. **Деплой**
   ```bash
   vercel deploy
   ```

Все остальное работает автоматически!

---

## Заключение

✅ **Архитектура полностью совместима с локальным запуском**

- Все компоненты имеют fallback механизмы
- Автоматическое определение окружения (Vercel vs Local)
- Идентичное поведение API endpoints
- Retry механизм работает через background tasks локально

**Рекомендации:**
- Для разработки: используйте локальный запуск
- Для production: используйте Vercel с Redis и Cron
- Для тестирования: можно использовать оба варианта

