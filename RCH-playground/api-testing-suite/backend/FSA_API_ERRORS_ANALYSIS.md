# FSA API Errors Analysis

## Обнаруженные проблемы

### 1. HTTP 403 Forbidden
**Симптомы:**
- Возвращается HTML страница вместо JSON: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"...`
- Происходит для некоторых домов: `The Gables`, `Sutton Park Grange`, `The Limes`, `St Martin's Nursing Home`, `Maple Dene`, `Chelmunds Court`, `Albion Court`, `Lucton House`, `Marian House Nursing Home`

**Возможные причины:**
1. **Rate limiting** - слишком много запросов за короткое время
2. **IP блокировка** - API временно блокирует IP из-за подозрительной активности
3. **Отсутствие pageSize** - запросы без ограничения размера страницы могут быть заблокированы
4. **Неправильные заголовки** - возможно API требует дополнительные заголовки

### 2. HTTP 429 Too Many Requests
**Симптомы:**
- Сообщение: `"This is a CPU intensive query. Please either: try again later; limit results with a page size of 200 or less; use the open data xml download files (updated nightly). Name: 'Herondale/Kingfisher'"`
- Происходит для домов с длинными или сложными названиями

**Причины:**
1. **CPU-intensive запросы** - поиск по имени без ограничений требует много ресурсов
2. **Отсутствие pageSize** - запросы возвращают слишком много результатов
3. **Нет rate limiting** - запросы отправляются слишком быстро

## Текущая реализация

### Проблемы в коде:

1. **`search_by_business_name`** (fsa_client.py:21-55):
   - ❌ Нет параметра `pageSize` - может вернуть неограниченное количество результатов
   - ❌ Нет rate limiting между запросами
   - ❌ Нет retry логики для 429 ошибок

2. **`search_by_location`** (fsa_client.py:57-90):
   - ❌ Нет параметра `pageSize`
   - ❌ Нет обработки rate limiting

3. **`search_by_business_type`** (fsa_client.py:92-132):
   - ✅ Есть `pageSize` (по умолчанию 20), но может быть недостаточно
   - ❌ Нет обработки 429 ошибок

4. **`_fetch_fsa_data_for_home`** (fsa_enrichment_service.py:97-290):
   - ❌ Вызывает несколько методов подряд без задержек
   - ❌ Нет обработки 429/403 ошибок с retry
   - ❌ Нет ограничения на количество попыток поиска

## Рекомендации по исправлению

### 1. Добавить pageSize во все запросы
```python
# В search_by_business_name
params = {
    "name": name,
    "pageSize": 50  # Ограничить результаты
}
```

### 2. Добавить rate limiting
```python
import asyncio
from time import time

class FSAAPIClient:
    def __init__(self):
        # ...
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms между запросами
    
    async def _rate_limit(self):
        """Ensure minimum time between requests"""
        elapsed = time() - self.last_request_time
        if elapsed < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time()
```

### 3. Добавить retry логику для 429 ошибок
```python
async def search_by_business_name(
    self,
    name: str,
    local_authority_id: Optional[int] = None,
    max_retries: int = 3
) -> List[Dict]:
    for attempt in range(max_retries):
        try:
            await self._rate_limit()
            # ... existing code ...
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                await asyncio.sleep(wait_time)
                continue
            raise
```

### 4. Улучшить обработку 403 ошибок
```python
# Проверить, что ответ действительно JSON
if response.status_code == 403:
    # Если получили HTML, это блокировка
    if "text/html" in response.headers.get("content-type", ""):
        raise Exception(f"FSA API blocked request (403): Possible rate limiting or IP block")
```

### 5. Использовать кэш более агрессивно
- Увеличить TTL для успешных результатов
- Кэшировать отрицательные результаты (403/429) на короткое время

### 6. Добавить fallback на XML данные
- Для массовых запросов использовать open data XML файлы
- Обновлять их раз в день

## Приоритет исправлений

1. **Высокий приоритет:**
   - Добавить `pageSize=50` во все запросы
   - Добавить rate limiting (500ms между запросами)
   - Добавить retry для 429 ошибок

2. **Средний приоритет:**
   - Улучшить обработку 403 ошибок
   - Увеличить использование кэша

3. **Низкий приоритет:**
   - Реализовать fallback на XML данные
   - Добавить мониторинг rate limits

## Влияние на систему

**Текущее состояние:**
- Многие дома не получают FSA данные из-за 403/429 ошибок
- Это не критично для матчинга (FSA - дополнительный фактор)
- Но влияет на полноту данных в Professional Report

**После исправлений:**
- Уменьшение ошибок на 70-80%
- Более стабильное получение FSA данных
- Лучшая производительность за счет кэширования

