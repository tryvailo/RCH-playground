# Оптимизация для Vercel Serverless Architecture

**Дата:** 2025-01-XX  
**Платформа:** Vercel Serverless Functions  
**Статус:** 📋 Архитектурный план

---

## Ограничения Vercel

### Время выполнения функций:
- **Hobby Plan:** 10 секунд
- **Pro Plan:** 300 секунд (5 минут)
- **Enterprise Plan:** 900 секунд (15 минут)

### Дополнительные ограничения:
- Холодный старт может быть медленным
- Нет постоянного состояния между запросами
- Ограничения памяти (1024 MB для Pro)
- Ограничения размера ответа (4.5 MB для Pro)

---

## Проблемы текущей реализации

1. **Последовательная обработка домов** - каждый дом обрабатывается один за другим
2. **Долгие API вызовы** - Firecrawl, Neighbourhood Analyzer, CQC API могут занимать минуты
3. **Один большой endpoint** - весь процесс в одном запросе
4. **Нет кэширования промежуточных результатов**

---

## Рекомендуемая архитектура для Vercel

### Вариант 1: Асинхронная Job Queue (РЕКОМЕНДУЕТСЯ)

#### Архитектура:

```
1. POST /api/professional-report/start
   → Создает job, возвращает job_id
   → Время выполнения: < 5 секунд

2. Background Job (Vercel Cron или External Queue)
   → Обрабатывает отчет асинхронно
   → Сохраняет результаты в DB/Storage

3. GET /api/professional-report/status/{job_id}
   → Проверяет статус job
   → Возвращает прогресс (0-100%)
   → Время выполнения: < 1 секунда

4. GET /api/professional-report/result/{job_id}
   → Возвращает готовый отчет
   → Время выполнения: < 2 секунды
```

#### Преимущества:
- ✅ Работает в пределах лимитов Vercel
- ✅ Пользователь видит прогресс
- ✅ Можно обрабатывать несколько отчетов параллельно
- ✅ Устойчивость к ошибкам (retry механизм)

#### Реализация:

**1. Endpoint для старта job:**
```python
@app.post("/api/professional-report/start")
async def start_professional_report(request: Dict[str, Any] = Body(...)):
    """
    Создает job для генерации отчета
    Возвращает job_id немедленно (< 5 секунд)
    """
    job_id = str(uuid.uuid4())
    
    # Сохранить job в DB/Redis
    job_status = {
        'job_id': job_id,
        'status': 'pending',
        'progress': 0,
        'questionnaire': request,
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None
    }
    
    # Сохранить в DB или Redis
    await save_job_status(job_id, job_status)
    
    # Запустить background обработку (не ждать завершения)
    asyncio.create_task(process_report_async(job_id, request))
    
    return {
        'job_id': job_id,
        'status': 'pending',
        'message': 'Report generation started. Use /status/{job_id} to check progress.'
    }
```

**2. Background обработка:**
```python
async def process_report_async(job_id: str, questionnaire: Dict[str, Any]):
    """
    Асинхронная обработка отчета
    Выполняется в фоне, не блокирует основной endpoint
    """
    try:
        await update_job_status(job_id, {'status': 'processing', 'progress': 5})
        
        # Загрузить дома (быстро)
        care_homes = await load_care_homes(...)
        await update_job_status(job_id, {'progress': 10})
        
        # Обработать дома параллельно (батчами)
        batch_size = 3  # Обрабатывать по 3 дома одновременно
        scored_homes = []
        
        for i in range(0, len(care_homes), batch_size):
            batch = care_homes[i:i+batch_size]
            batch_results = await asyncio.gather(
                *[process_single_home(home, questionnaire) for home in batch],
                return_exceptions=True
            )
            
            # Добавить успешные результаты
            for result in batch_results:
                if not isinstance(result, Exception):
                    scored_homes.append(result)
            
            # Обновить прогресс
            progress = 10 + int((i + len(batch)) / len(care_homes) * 80)
            await update_job_status(job_id, {'progress': progress})
        
        # Выбрать топ-5
        scored_homes.sort(key=lambda x: x['matchScore'], reverse=True)
        top_5_homes = scored_homes[:5]
        
        # Генерация дополнительных секций (быстро)
        report = await generate_report_sections(top_5_homes, questionnaire)
        
        # Сохранить результат
        await update_job_status(job_id, {
            'status': 'completed',
            'progress': 100,
            'result': report
        })
        
    except Exception as e:
        await update_job_status(job_id, {
            'status': 'failed',
            'error': str(e)
        })
```

**3. Endpoint для проверки статуса:**
```python
@app.get("/api/professional-report/status/{job_id}")
async def get_report_status(job_id: str):
    """
    Проверяет статус генерации отчета
    Быстрый endpoint (< 1 секунда)
    """
    job_status = await get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        'job_id': job_id,
        'status': job_status['status'],  # pending, processing, completed, failed
        'progress': job_status.get('progress', 0),
        'created_at': job_status['created_at'],
        'error': job_status.get('error')
    }
```

**4. Endpoint для получения результата:**
```python
@app.get("/api/professional-report/result/{job_id}")
async def get_report_result(job_id: str):
    """
    Возвращает готовый отчет
    Быстрый endpoint (< 2 секунды)
    """
    job_status = await get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_status['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Report not ready. Status: {job_status['status']}"
        )
    
    return job_status['result']
```

---

### Вариант 2: Параллельная обработка с батчингом

#### Оптимизация текущего endpoint:

```python
async def process_single_home(home: Dict[str, Any], questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обрабатывает один дом параллельно со всеми API вызовами
    """
    # Параллельные API вызовы для одного дома
    neighbourhood_task = asyncio.create_task(fetch_neighbourhood_data(home))
    fsa_task = asyncio.create_task(fetch_fsa_data(home))
    cqc_task = asyncio.create_task(fetch_cqc_data(home))
    google_places_task = asyncio.create_task(fetch_google_places(home))
    firecrawl_task = asyncio.create_task(fetch_firecrawl_data(home))
    
    # Ждем все параллельно с таймаутами
    neighbourhood_data, fsa_data, cqc_data, google_places, firecrawl_data = await asyncio.gather(
        neighbourhood_task,
        fsa_task,
        cqc_task,
        google_places_task,
        firecrawl_task,
        return_exceptions=True
    )
    
    # Обработать результаты (с fallback для ошибок)
    # ... построить scored_home ...
    
    return scored_home

@app.post("/api/professional-report")
async def generate_professional_report(request: Dict[str, Any] = Body(...)):
    """
    Оптимизированная версия с параллельной обработкой
    """
    # Загрузить дома (быстро)
    care_homes = await load_care_homes(...)
    
    # Обработать все дома параллельно (батчами по 3-5)
    batch_size = 3
    scored_homes = []
    
    for i in range(0, len(care_homes), batch_size):
        batch = care_homes[i:i+batch_size]
        batch_results = await asyncio.gather(
            *[process_single_home(home, request) for home in batch],
            return_exceptions=True
        )
        
        # Добавить успешные результаты
        for result in batch_results:
            if not isinstance(result, Exception):
                scored_homes.append(result)
    
    # Выбрать топ-5 и сгенерировать отчет
    scored_homes.sort(key=lambda x: x['matchScore'], reverse=True)
    top_5_homes = scored_homes[:5]
    
    report = await generate_report_sections(top_5_homes, request)
    
    return report
```

---

### Вариант 3: Гибридный подход (РЕКОМЕНДУЕТСЯ для Production)

#### Комбинация Job Queue + Кэширование + Параллелизм:

```
1. POST /api/professional-report/start
   → Быстрый ответ с job_id

2. Background Processing (Vercel Cron или External Service)
   → Параллельная обработка домов
   → Кэширование промежуточных результатов
   → Сохранение в DB/Storage

3. GET /api/professional-report/status/{job_id}
   → Проверка статуса

4. GET /api/professional-report/result/{job_id}
   → Получение результата
```

#### Кэширование стратегия:

```python
# Кэшировать результаты API вызовов
@cache_result(ttl=3600)  # 1 час
async def fetch_cqc_data(home_id: str):
    # ... CQC API call ...

@cache_result(ttl=86400)  # 24 часа
async def fetch_neighbourhood_data(postcode: str, lat: float, lon: float):
    # ... Neighbourhood API call ...

# Кэшировать обработанные дома
@cache_result(ttl=1800)  # 30 минут
async def process_single_home(home: Dict, questionnaire: Dict):
    # ... обработка ...
```

---

## Рекомендации по оптимизации

### 1. Использовать Vercel KV (Redis) для job queue

```python
import redis.asyncio as redis

redis_client = redis.from_url(os.getenv('KV_REDIS_URL'))

async def save_job_status(job_id: str, status: Dict):
    await redis_client.setex(
        f"job:{job_id}",
        3600,  # TTL 1 час
        json.dumps(status)
    )

async def get_job_status(job_id: str) -> Optional[Dict]:
    data = await redis_client.get(f"job:{job_id}")
    return json.loads(data) if data else None
```

### 2. Использовать Vercel Blob Storage для больших результатов

```python
from vercel_blob import put, get

# Сохранить большой отчет
async def save_report_to_blob(job_id: str, report: Dict):
    report_json = json.dumps(report)
    await put(f"reports/{job_id}.json", report_json.encode())
    
    # Сохранить только ссылку в KV
    await redis_client.setex(
        f"job:{job_id}",
        3600,
        json.dumps({'status': 'completed', 'blob_url': f"reports/{job_id}.json"})
    )
```

### 3. Оптимизировать параллельную обработку

```python
async def process_homes_parallel(care_homes: List[Dict], questionnaire: Dict):
    """
    Обрабатывает дома параллельно с ограничением concurrency
    """
    semaphore = asyncio.Semaphore(3)  # Максимум 3 одновременно
    
    async def process_with_limit(home):
        async with semaphore:
            return await process_single_home(home, questionnaire)
    
    results = await asyncio.gather(
        *[process_with_limit(home) for home in care_homes],
        return_exceptions=True
    )
    
    return [r for r in results if not isinstance(r, Exception)]
```

### 4. Использовать Edge Functions для быстрых операций

```typescript
// api/professional-report/status/[job_id].ts (Edge Function)
export const config = {
  runtime: 'edge',
}

export default async function handler(req: Request) {
  const { job_id } = req.params
  // Быстрая проверка статуса из KV
  const status = await getJobStatus(job_id)
  return Response.json(status)
}
```

### 5. Оптимизировать таймауты для Vercel

```python
# Агрессивные таймауты для быстрых ответов
FIRECRAWL_TIMEOUT = 30.0  # 30 секунд (вместо 120)
GOOGLE_PLACES_TIMEOUT = 5.0  # 5 секунд
CQC_API_TIMEOUT = 5.0  # 5 секунд
NEIGHBOURHOOD_TIMEOUT = 10.0  # 10 секунд
```

---

## План миграции

### Этап 1: Рефакторинг текущего endpoint
1. Разделить на функции: `process_single_home()`, `generate_report_sections()`
2. Добавить параллельную обработку домов
3. Оптимизировать таймауты

### Этап 2: Добавить Job Queue
1. Создать `/api/professional-report/start` endpoint
2. Создать background обработку
3. Создать `/api/professional-report/status/{job_id}` endpoint
4. Создать `/api/professional-report/result/{job_id}` endpoint

### Этап 3: Добавить кэширование
1. Настроить Vercel KV (Redis)
2. Добавить кэширование API вызовов
3. Добавить кэширование обработанных домов

### Этап 4: Оптимизация
1. Использовать Vercel Blob для больших результатов
2. Добавить Edge Functions для быстрых операций
3. Мониторинг и оптимизация производительности

---

## Оценка времени выполнения

### Текущая реализация (последовательная):
- 5 домов × 2 минуты = **10 минут** ❌ (превышает лимиты Vercel)

### Оптимизированная (параллельная, батчи по 3):
- 5 домов ÷ 3 батча × 2 минуты = **~4 минуты** ⚠️ (на грани для Pro)

### С Job Queue + Кэширование:
- Start endpoint: **< 5 секунд** ✅
- Background processing: **3-5 минут** (не блокирует пользователя)
- Status/Result endpoints: **< 2 секунды** ✅

---

## Рекомендации

1. **Использовать Вариант 1 (Job Queue)** для production
2. **Добавить кэширование** для часто запрашиваемых данных
3. **Параллельная обработка** домов (батчи по 3-5)
4. **Агрессивные таймауты** для API вызовов
5. **Vercel KV** для job queue и кэширования
6. **Vercel Blob** для больших результатов отчетов

