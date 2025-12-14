# Руководство по реализации для Vercel

**Дата:** 2025-01-XX  
**Платформа:** Vercel Serverless Functions  
**Статус:** 📋 Пошаговое руководство

---

## Шаг 1: Установка зависимостей

### 1.1 Добавить Redis (Vercel KV)

```bash
# Установить Vercel KV
vercel kv create

# Или использовать внешний Redis
# Добавить переменную окружения KV_REDIS_URL или REDIS_URL
```

### 1.2 Установить зависимости

```bash
pip install redis[hiredis]  # Для async Redis
```

---

## Шаг 2: Рефакторинг текущего endpoint

### 2.1 Создать внутреннюю функцию

**Файл:** `backend/main.py`

```python
async def generate_professional_report_internal(
    questionnaire: Dict[str, Any],
    progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
) -> Dict[str, Any]:
    """
    Internal function for report generation
    Can be called from job queue or directly
    """
    # Существующая логика из generate_professional_report
    # Но с поддержкой progress_callback
    
    if progress_callback:
        await progress_callback(10, "Loading care homes...")
    
    # ... остальная логика ...
    
    if progress_callback:
        await progress_callback(50, "Processing care homes...")
    
    # ... обработка домов ...
    
    if progress_callback:
        await progress_callback(90, "Generating final report...")
    
    # ... генерация отчета ...
    
    return report
```

### 2.2 Обновить существующий endpoint

```python
@app.post("/api/professional-report")
async def generate_professional_report(request: Dict[str, Any] = Body(...)):
    """
    Legacy endpoint - redirects to job queue for better performance
    """
    # Для обратной совместимости, создаем job и возвращаем результат
    # Но рекомендуется использовать /start endpoint
    job_service = JobQueueService()
    job_id = await job_service.create_job(request)
    
    # Обработать синхронно (для обратной совместимости)
    # Но это может превысить лимиты Vercel!
    try:
        report = await generate_professional_report_internal(request)
        await job_service.save_job_result(job_id, report)
        return report
    except asyncio.TimeoutError:
        # Если превышен лимит, вернуть job_id для async обработки
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': 'Report generation is taking longer than expected. Use /status/{job_id} to check progress.',
            'status_url': f'/api/professional-report/status/{job_id}'
        }
```

---

## Шаг 3: Оптимизация параллельной обработки

### 3.1 Создать функцию для обработки одного дома

```python
async def process_single_home_optimized(
    home: Dict[str, Any],
    questionnaire: Dict[str, Any],
    timeout_per_home: float = 60.0  # 1 минута на дом
) -> Optional[Dict[str, Any]]:
    """
    Оптимизированная обработка одного дома
    Все API вызовы параллельны с таймаутами
    """
    try:
        # Параллельные API вызовы с агрессивными таймаутами
        neighbourhood_task = asyncio.create_task(
            asyncio.wait_for(fetch_neighbourhood_data(home), timeout=10.0)
        )
        fsa_task = asyncio.create_task(
            asyncio.wait_for(fetch_fsa_data(home), timeout=8.0)
        )
        cqc_task = asyncio.create_task(
            asyncio.wait_for(fetch_cqc_data(home), timeout=8.0)
        )
        google_places_task = asyncio.create_task(
            asyncio.wait_for(fetch_google_places(home), timeout=5.0)
        )
        firecrawl_task = asyncio.create_task(
            asyncio.wait_for(fetch_firecrawl_data(home), timeout=30.0)  # Уменьшено с 120
        )
        
        # Ждем все параллельно
        results = await asyncio.gather(
            neighbourhood_task,
            fsa_task,
            cqc_task,
            google_places_task,
            firecrawl_task,
            return_exceptions=True
        )
        
        neighbourhood_data, fsa_data, cqc_data, google_places, firecrawl_data = results
        
        # Обработать результаты (с fallback для ошибок)
        scored_home = build_scored_home(
            home,
            questionnaire,
            neighbourhood_data if not isinstance(neighbourhood_data, Exception) else None,
            fsa_data if not isinstance(fsa_data, Exception) else None,
            cqc_data if not isinstance(cqc_data, Exception) else None,
            google_places if not isinstance(google_places, Exception) else None,
            firecrawl_data if not isinstance(firecrawl_data, Exception) else None
        )
        
        return scored_home
        
    except asyncio.TimeoutError:
        print(f"⚠️ Timeout processing home {home.get('name')}")
        # Вернуть базовую версию без enrichment
        return build_scored_home_basic(home, questionnaire)
    except Exception as e:
        print(f"⚠️ Error processing home {home.get('name')}: {e}")
        return None
```

### 3.2 Параллельная обработка батчами

```python
async def process_homes_parallel_optimized(
    care_homes: List[Dict[str, Any]],
    questionnaire: Dict[str, Any],
    batch_size: int = 3,
    max_concurrent: int = 3
) -> List[Dict[str, Any]]:
    """
    Параллельная обработка домов с ограничением concurrency
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    scored_homes = []
    
    async def process_with_limit(home):
        async with semaphore:
            return await process_single_home_optimized(home, questionnaire)
    
    # Обработать все дома параллельно
    results = await asyncio.gather(
        *[process_with_limit(home) for home in care_homes],
        return_exceptions=True
    )
    
    # Фильтровать успешные результаты
    for result in results:
        if result and not isinstance(result, Exception):
            scored_homes.append(result)
    
    return scored_homes
```

---

## Шаг 4: Настройка Vercel

### 4.1 vercel.json конфигурация

```json
{
  "functions": {
    "api/professional-report/start.ts": {
      "maxDuration": 10
    },
    "api/professional-report/status/[job_id].ts": {
      "maxDuration": 5
    },
    "api/professional-report/result/[job_id].ts": {
      "maxDuration": 10
    },
    "api/professional-report.ts": {
      "maxDuration": 300
    }
  },
  "crons": [
    {
      "path": "/api/cron/process-jobs",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

### 4.2 Переменные окружения

```bash
# .env.local
KV_REDIS_URL=redis://...
REDIS_URL=redis://...
VERCEL_ENV=production
```

---

## Шаг 5: Frontend интеграция

### 5.1 Обновить hook для job queue

```typescript
// useProfessionalReport.ts

export const useStartProfessionalReport = () => {
  return useMutation<{job_id: string}, Error, ProfessionalQuestionnaireResponse>({
    mutationFn: async (questionnaire) => {
      const response = await axios.post('/api/professional-report/start', questionnaire);
      return response.data;
    }
  });
};

export const usePollReportStatus = (jobId: string | null) => {
  return useQuery({
    queryKey: ['report-status', jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const response = await axios.get(`/api/professional-report/status/${jobId}`);
      return response.data;
    },
    enabled: !!jobId,
    refetchInterval: (data) => {
      // Poll every 2 seconds if processing, stop if completed/failed
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 2000;
      }
      return false;
    }
  });
};

export const useGetReportResult = (jobId: string | null) => {
  return useQuery({
    queryKey: ['report-result', jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const response = await axios.get(`/api/professional-report/result/${jobId}`);
      return response.data;
    },
    enabled: !!jobId && jobId !== null,
    retry: false
  });
};
```

### 5.2 Обновить компонент

```typescript
// ProfessionalReportViewer.tsx

const startReport = useStartProfessionalReport();
const { data: status } = usePollReportStatus(jobId);
const { data: report } = useGetReportResult(
  status?.status === 'completed' ? jobId : null
);

const handleGenerate = async () => {
  const result = await startReport.mutateAsync(questionnaire);
  setJobId(result.job_id);
};

// Показывать прогресс
{status && (
  <div>
    <ProgressBar value={status.progress} />
    <p>{status.message}</p>
  </div>
)}
```

---

## Шаг 6: Кэширование

### 6.1 Кэширование API вызовов

```python
from functools import lru_cache
import hashlib
import json

def cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key"""
    key_data = json.dumps(kwargs, sort_keys=True)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"

@cache_result(ttl=3600)  # 1 hour
async def fetch_cqc_data_cached(home_id: str):
    return await fetch_cqc_data(home_id)
```

### 6.2 Использовать Vercel KV для кэша

```python
async def get_cached_or_fetch(key: str, fetch_fn, ttl: int = 3600):
    """Get from cache or fetch and cache"""
    job_service = get_job_queue_service()
    
    # Try cache
    cached = await job_service.redis_client.get(f"cache:{key}")
    if cached:
        return json.loads(cached)
    
    # Fetch
    result = await fetch_fn()
    
    # Cache
    await job_service.redis_client.setex(
        f"cache:{key}",
        ttl,
        json.dumps(result, default=str)
    )
    
    return result
```

---

## Шаг 7: Мониторинг и оптимизация

### 7.1 Логирование времени выполнения

```python
import time

async def timed_operation(name: str, operation):
    start = time.time()
    try:
        result = await operation()
        duration = time.time() - start
        print(f"✅ {name} completed in {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start
        print(f"❌ {name} failed after {duration:.2f}s: {e}")
        raise
```

### 7.2 Метрики производительности

```python
# Отслеживать:
# - Время на каждый дом
# - Время на каждый API вызов
# - Общее время генерации
# - Количество таймаутов
# - Использование кэша
```

---

## Приоритеты реализации

### Высокий приоритет (сделать сразу):
1. ✅ Увеличить таймаут frontend до 10 минут
2. ✅ Уменьшить таймаут Firecrawl до 30 секунд
3. ✅ Добавить параллельную обработку домов (батчи по 3)
4. ✅ Оптимизировать таймауты для всех API вызовов

### Средний приоритет (следующий этап):
1. ⚠️ Реализовать Job Queue Service
2. ⚠️ Создать `/start`, `/status`, `/result` endpoints
3. ⚠️ Интегрировать Vercel KV (Redis)
4. ⚠️ Обновить frontend для использования job queue

### Низкий приоритет (оптимизация):
1. 🔵 Добавить кэширование API вызовов
2. 🔵 Использовать Vercel Blob для больших результатов
3. 🔵 Добавить Edge Functions для быстрых операций
4. 🔵 Мониторинг и метрики

---

## Оценка времени реализации

- **Высокий приоритет:** 2-4 часа
- **Средний приоритет:** 1-2 дня
- **Низкий приоритет:** 2-3 дня

---

## Чеклист для деплоя на Vercel

- [ ] Настроить Vercel KV (Redis)
- [ ] Установить переменные окружения
- [ ] Настроить vercel.json с правильными maxDuration
- [ ] Протестировать job queue endpoints
- [ ] Протестировать frontend интеграцию
- [ ] Настроить мониторинг
- [ ] Протестировать с реальными данными
- [ ] Оптимизировать таймауты на основе метрик

