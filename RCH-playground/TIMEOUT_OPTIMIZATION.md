# Оптимизация Таймаутов для Professional Report

**Дата:** 2025-01-XX  
**Статус:** ✅ Исправлено

---

## Проблема

Генерация Professional Report занимала более 5 минут и приводила к таймауту на frontend.

---

## Исправления

### 1. Увеличен таймаут на Frontend

**Файл:** `frontend/src/features/professional-report/hooks/useProfessionalReport.ts`

**Изменения:**
- ✅ Таймаут увеличен с 5 минут (300000ms) до **10 минут (600000ms)**
- ✅ Обновлено сообщение об ошибке таймаута
- ✅ Обновлен комментарий в коде

**Код:**
```typescript
// Было: 300000 (5 минут)
// Стало: 600000 (10 минут)
const REPORT_TIMEOUT = 600000; // 10 minutes (600 seconds) - increased for complex reports
timeout: 600000, // 10 minutes timeout for report generation
```

### 2. Оптимизирован таймаут Firecrawl

**Файл:** `backend/main.py`

**Изменения:**
- ✅ Таймаут Firecrawl уменьшен с 5 минут (300.0s) до **2 минут (120.0s)**
- ✅ Это предотвращает блокировку процесса на одном доме

**Код:**
```python
# Было: timeout=300.0  # 5 minutes
# Стало: timeout=120.0  # 2 minutes
firecrawl_data = await asyncio.wait_for(
    firecrawl_client.extract_care_home_data_full(website_url, home.get('name')),
    timeout=120.0  # 2 minutes timeout (reduced to prevent overall timeout)
)
```

---

## Рекомендации для дальнейшей оптимизации

### 1. Параллельная обработка домов

**Текущее состояние:** Дома обрабатываются последовательно в цикле `for idx, home in enumerate(care_homes, 1):`

**Рекомендация:** Использовать `asyncio.gather()` для параллельной обработки нескольких домов одновременно:

```python
# Пример оптимизации
async def process_single_home(home, idx, total):
    # ... обработка одного дома ...
    return scored_home

# Параллельная обработка (например, по 3 дома одновременно)
batch_size = 3
for i in range(0, len(care_homes), batch_size):
    batch = care_homes[i:i+batch_size]
    results = await asyncio.gather(
        *[process_single_home(home, i+j+1, len(care_homes)) for j, home in enumerate(batch)],
        return_exceptions=True
    )
    scored_homes.extend([r for r in results if not isinstance(r, Exception)])
```

### 2. Кэширование API вызовов

**Рекомендация:** Использовать более агрессивное кэширование для:
- CQC API вызовов
- Google Places API вызовов
- FSA API вызовов
- Neighbourhood Analyzer результатов

### 3. Асинхронная обработка через Job Queue

**Рекомендация:** Для очень больших отчетов рассмотреть:
- Celery или FastAPI BackgroundTasks
- Job status tracking
- Progress updates через WebSocket или polling

### 4. Ранний выход для медленных операций

**Рекомендация:** Добавить максимальное время на операцию:
- Если Firecrawl занимает > 2 минут - пропустить и использовать только DB данные
- Если Google Places API занимает > 30 секунд - использовать кэш или fallback
- Если Neighbourhood Analyzer занимает > 1 минуты - использовать упрощенный анализ

---

## Текущие таймауты

| Операция | Таймаут | Файл |
|----------|---------|------|
| **Frontend Request** | 10 минут | `useProfessionalReport.ts` |
| **Firecrawl** | 2 минуты | `main.py` |
| **FSA API** | 8 секунд | `main.py` |
| **Google Places API** | 8 секунд | `main.py` |
| **CQC API** | 8 секунд | `main.py` |

---

## Мониторинг

Рекомендуется добавить логирование времени выполнения:
- Время на каждый дом
- Время на каждый API вызов
- Общее время генерации отчета

Это поможет выявить узкие места в будущем.

