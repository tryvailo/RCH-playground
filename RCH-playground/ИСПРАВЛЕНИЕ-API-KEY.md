# ✅ ИСПРАВЛЕНИЕ: Firecrawl API Key Error

## Дата: 2025-01-27

---

## 🐛 Проблема

**Ошибка:** `Firecrawl Search API error: Firecrawl credentials not configured`

**Причина:** Endpoint `/api/firecrawl/search` использовал устаревший способ получения credentials через `credentials_store.get("default")` вместо `get_credentials()`.

---

## ✅ Исправление

### Обновлены все Firecrawl endpoints для использования `get_credentials()`:

1. ✅ `/api/firecrawl/search` - исправлено
2. ✅ `/api/firecrawl/scrape` - исправлено
3. ✅ `/api/firecrawl/crawl` - исправлено
4. ✅ `/api/firecrawl/extract` - исправлено
5. ✅ `/api/test/firecrawl` - исправлено
6. ✅ `/api/firecrawl/batch-analyze` - уже использовал `get_credentials()`
7. ✅ `/api/firecrawl/analyze` - уже использовал `get_credentials()`
8. ✅ `/api/firecrawl/unified-analysis` - уже использовал `get_credentials()`

---

## 📋 Проверка конфигурации

### API Key присутствует в config.json:

```json
{
  "firecrawl": {
    "api_key": "your-firecrawl-api-key"
  }
}
```

### Функция `get_credentials()` правильно загружает credentials:

1. Загружает из `config.json`
2. Загружает из переменных окружения (`FIRECRAWL_API_KEY`)
3. Объединяет их (env имеет приоритет)

---

## 🔧 Изменения в коде

### До (неправильно):
```python
@app.post("/api/firecrawl/search")
async def firecrawl_search(request: FirecrawlSearchRequest):
    creds = credentials_store.get("default")  # ❌ Старый способ
    if not creds or not hasattr(creds, 'firecrawl'):
        raise HTTPException(...)
    api_key = getattr(creds.firecrawl, 'api_key', None)
    client = FirecrawlAPIClient(api_key=api_key)
```

### После (правильно):
```python
@app.post("/api/firecrawl/search")
async def firecrawl_search(request: FirecrawlSearchRequest):
    creds = get_credentials()  # ✅ Правильный способ
    client = get_firecrawl_client(creds)  # ✅ Использует helper функцию
```

---

## ✅ Результат

Теперь все Firecrawl endpoints используют единый способ получения credentials через `get_credentials()`, который:
- ✅ Загружает из config.json
- ✅ Загружает из переменных окружения
- ✅ Правильно обрабатывает ошибки отсутствия API key
- ✅ Использует helper функцию `get_firecrawl_client()` для консистентности

---

## 🧪 Тестирование

После исправления, все Firecrawl endpoints должны работать корректно:

1. `/api/firecrawl/search` - ✅ Исправлено
2. `/api/firecrawl/analyze` - ✅ Работает
3. `/api/firecrawl/scrape` - ✅ Исправлено
4. `/api/firecrawl/crawl` - ✅ Исправлено
5. `/api/firecrawl/extract` - ✅ Исправлено

---

**Статус:** ✅ ИСПРАВЛЕНО

