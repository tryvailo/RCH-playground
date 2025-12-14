# Реализация Retry механизма для Professional Report

**Дата:** 2025-01-XX  
**Статус:** ✅ Реализовано  
**Цель:** Обеспечить генерацию отчета даже при сбоях источников данных, с автоматическим retry до полной готовности (до 3 часов)

---

## Архитектура

### Компоненты

1. **ReportRetryService** (`services/report_retry_service.py`)
   - Отслеживает недостающие источники данных
   - Управляет retry логикой с exponential backoff
   - Загружает недостающие данные

2. **DataSourceTracker** (`services/data_source_tracker.py`)
   - Отслеживает успешные/неуспешные загрузки данных
   - Генерирует статистику
   - Определяет недостающие источники

3. **JobQueueService** (расширен)
   - Поддержка статуса `PARTIAL` (частично готов)
   - Отслеживание недостающих источников данных
   - Метрики полноты отчета

4. **Report Retry Routes** (`routers/report_retry_routes.py`)
   - `/api/professional-report/retry/{job_id}` - ручной retry
   - `/api/professional-report/missing-sources/{job_id}` - список недостающих источников
   - `/api/professional-report/retry-status/{job_id}` - статус retry

5. **Cron Job** (`cron/retry_missing_data.py`)
   - Автоматический retry каждые 5 минут
   - Проверяет все частичные отчеты
   - Запускает retry для готовых источников

---

## Процесс работы

### 1. Генерация отчета (первичная)

```
1. Пользователь запрашивает отчет
2. Создается job с status='pending'
3. Начинается обработка домов
4. Для каждого дома загружаются источники данных:
   - Neighbourhood Analysis
   - FSA Food Hygiene
   - CQC Inspection History
   - Google Places Insights
   - Firecrawl Website Data
5. DataSourceTracker отслеживает успех/неудачу каждого источника
6. Отчет генерируется с доступными данными
7. Если есть недостающие источники:
   - status='partial'
   - missing_data_sources сохраняются
   - completeness рассчитывается
8. Отчет возвращается пользователю (даже частичный)
```

### 2. Автоматический Retry

```
1. Cron job запускается каждые 5 минут
2. Находит все jobs со status='partial'
3. Для каждого job:
   - Проверяет timeout (3 часа)
   - Проверяет какие источники готовы для retry
   - Retry с exponential backoff:
     - 1-я попытка: через 5 минут
     - 2-я попытка: через 7.5 минут
     - 3-я попытка: через 11.25 минут
     - ...
     - Максимум 10 попыток
4. Если источник загружен успешно:
   - Обновляет отчет с новыми данными
   - Удаляет из missing_data_sources
5. Если все источники загружены:
   - status='completed'
   - is_partial=False
   - completeness=100%
```

### 3. Ручной Retry

```
1. Пользователь вызывает /api/professional-report/retry/{job_id}
2. Система проверяет:
   - Job существует
   - Status='partial' или 'completed'
   - Timeout не превышен (3 часа)
3. Retry всех готовых источников
4. Возвращает результат retry
```

---

## Конфигурация Retry

```python
MAX_RETRY_ATTEMPTS = 10  # Максимум попыток на источник
RETRY_DELAY_SECONDS = 300  # 5 минут между попытками
MAX_TOTAL_TIME_HOURS = 3  # 3 часа общий timeout
RETRY_BACKOFF_MULTIPLIER = 1.5  # Exponential backoff
```

### Пример Retry Schedule

| Попытка | Задержка | Время с начала |
|---------|----------|----------------|
| 1       | 5 мин    | 5 мин          |
| 2       | 7.5 мин  | 12.5 мин       |
| 3       | 11.25 мин| 23.75 мин      |
| 4       | 16.88 мин| 40.63 мин      |
| 5       | 25.31 мин| 65.94 мин      |
| ...     | ...      | ...            |
| 10      | ~191 мин | ~3 часа        |

---

## Интеграция в main.py

### Шаг 1: Добавить DataSourceTracker

```python
from services.data_source_tracker import DataSourceTracker

# В начале обработки домов
tracker = DataSourceTracker()

# При загрузке каждого источника
try:
    start_time = time.time()
    neighbourhood_data = await load_neighbourhood(...)
    load_time = time.time() - start_time
    
    if neighbourhood_data:
        tracker.track_success('neighbourhood', home_id, home_name, load_time=load_time)
    else:
        tracker.track_failure('neighbourhood', home_id, home_name, 'No data returned', load_time)
except Exception as e:
    tracker.track_failure('neighbourhood', home_id, home_name, str(e))
```

### Шаг 2: Сохранить частичный результат

```python
# После генерации отчета
missing_sources = tracker.get_missing_sources()
is_partial = len(missing_sources) > 0

# Сохранить в job queue
await job_service.save_job_result(
    job_id=job_id,
    result=report,
    is_partial=is_partial,
    missing_sources=missing_sources
)
```

### Шаг 3: Запустить автоматический retry

```python
# После сохранения частичного результата
if is_partial:
    # Запустить фоновую задачу для retry
    asyncio.create_task(
        schedule_retry_job(job_id, questionnaire)
    )
```

---

## API Endpoints

### 1. Retry Missing Data

```http
POST /api/professional-report/retry/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "retry_result": {
    "retried_sources": [...],
    "success_count": 2,
    "still_missing": [...],
    "message": "Retried 3 sources, 2 succeeded"
  },
  "time_elapsed_hours": 0.5,
  "time_remaining_hours": 2.5
}
```

### 2. Get Missing Sources

```http
GET /api/professional-report/missing-sources/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "missing_sources": [
    {
      "home_id": "123",
      "home_name": "Care Home Name",
      "source_type": "firecrawl",
      "source_name": "Website Content Analysis",
      "retry_count": 2,
      "error": "Timeout after 30 seconds"
    }
  ],
  "missing_by_type": {
    "firecrawl": [...],
    "google_places": [...]
  },
  "total_missing": 3,
  "is_partial": true,
  "completeness": 85.0
}
```

### 3. Get Retry Status

```http
GET /api/professional-report/retry-status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "is_partial": true,
  "completeness": 85.0,
  "missing_sources_count": 3,
  "next_retries": [
    {
      "source_type": "firecrawl",
      "home_name": "Care Home Name",
      "next_retry_at": "2025-01-XXT12:30:00",
      "time_until_retry_seconds": 180,
      "retry_count": 2,
      "max_retries": 10
    }
  ],
  "time_elapsed_hours": 0.5,
  "time_remaining_hours": 2.5,
  "will_auto_retry": true
}
```

---

## Vercel Cron Configuration

Добавить в `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/retry-missing-data",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

Это запустит cron job каждые 5 минут для автоматического retry.

---

## Frontend Integration

### 1. Проверка статуса отчета

```typescript
const { data: status } = useQuery({
  queryKey: ['report-status', jobId],
  queryFn: async () => {
    const response = await axios.get(`/api/professional-report/status/${jobId}`);
    return response.data;
  },
  refetchInterval: (data) => {
    // Poll every 10 seconds if partial
    if (data?.status === 'partial') {
      return 10000;
    }
    return false;
  }
});
```

### 2. Отображение частичного статуса

```typescript
{status?.is_partial && (
  <div className="alert alert-info">
    <p>Report is being generated with partial data.</p>
    <p>Completeness: {status.completeness}%</p>
    <p>Missing sources: {status.missing_sources_count}</p>
    <p>System will automatically retry missing sources...</p>
  </div>
)}
```

### 3. Ручной retry (опционально)

```typescript
const retryMissingData = async () => {
  const response = await axios.post(`/api/professional-report/retry/${jobId}`);
  // Show success message
};
```

---

## Мониторинг и Логирование

### Логи для отслеживания

1. **При первичной генерации:**
   ```
   📊 Report generation started
   ✅ Neighbourhood data loaded for Home 1
   ❌ Firecrawl data failed for Home 1: Timeout
   ⚠️ Report generated with partial data (85% complete)
   📋 Missing sources: 3
   ```

2. **При retry:**
   ```
   🔄 Retrying missing sources for job {job_id}
   ✅ Firecrawl data loaded for Home 1 (retry #2)
   ⚠️ Google Places still failed for Home 2 (retry #3)
   📊 Completeness: 90% (up from 85%)
   ```

3. **При завершении:**
   ```
   ✅ All data sources loaded successfully
   📊 Report completeness: 100%
   ✅ Report status: completed
   ```

---

## Обработка Edge Cases

### 1. Timeout (3 часа)

- Если timeout превышен, retry прекращается
- Отчет остается в статусе `partial`
- Пользователь получает уведомление

### 2. Источник недоступен постоянно

- После 10 попыток источник помечается как "permanently failed"
- Отчет генерируется без этого источника
- Используются fallback данные

### 3. Job не найден

- Retry прекращается
- Логируется ошибка
- Пользователь получает уведомление

---

## Тестирование

### Unit Tests

```python
def test_retry_service_tracks_missing_sources():
    # Test tracking missing sources
    pass

def test_retry_service_retries_sources():
    # Test retry logic
    pass

def test_retry_service_respects_timeout():
    # Test 3-hour timeout
    pass
```

### Integration Tests

```python
async def test_full_retry_flow():
    # 1. Generate partial report
    # 2. Check missing sources
    # 3. Retry missing sources
    # 4. Verify report completeness
    pass
```

---

## Производительность

### Оценка времени

- **Первичная генерация:** 3-5 минут (с оптимизацией)
- **Retry одного источника:** 5-30 секунд
- **Полный retry (все источники):** 1-2 минуты
- **Общее время до полной готовности:** до 3 часов

### Оптимизации

1. **Параллельный retry:** Retry нескольких источников одновременно
2. **Кэширование:** Кэшировать успешно загруженные данные
3. **Приоритизация:** Retry критичных источников первыми

---

## Следующие шаги

1. ✅ Реализовать ReportRetryService
2. ✅ Реализовать DataSourceTracker
3. ✅ Расширить JobQueueService
4. ✅ Создать API endpoints
5. ✅ Создать Cron job
6. ⚠️ Интегрировать в main.py (требуется модификация)
7. ⚠️ Обновить frontend для отображения частичного статуса
8. ⚠️ Настроить Vercel Cron
9. ⚠️ Добавить мониторинг и алерты

---

## Заключение

Система retry обеспечивает:
- ✅ Отчет всегда генерируется (даже частичный)
- ✅ Автоматический retry недостающих источников
- ✅ До 3 часов на полную загрузку
- ✅ Прозрачность для пользователя (статус, полнота)
- ✅ Ручной retry при необходимости

