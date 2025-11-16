# ✅ ИСПРАВЛЕНИЕ: FirecrawlSearchRequest Missing Fields

## Дата: 2025-01-27

---

## 🐛 Проблема

**Ошибка:** `'FirecrawlSearchRequest' object has no attribute 'location'`

**Причина:** Схема `FirecrawlSearchRequest` не содержала всех полей, которые используются в endpoint `/api/firecrawl/search`.

---

## ✅ Исправление

### Добавлены недостающие поля в схему `FirecrawlSearchRequest`:

1. ✅ `location: Optional[str]` - Фильтр по местоположению
2. ✅ `tbs: Optional[str]` - Временной фильтр поиска (например, 'qdr:d' для последнего дня)
3. ✅ `timeout: Optional[int]` - Таймаут операции поиска (1-300 секунд)
4. ✅ `scrape_options: Optional[Dict[str, Any]]` - Опции для скрапинга результатов поиска

---

## 📋 Обновленная схема

```python
class FirecrawlSearchRequest(BaseModel):
    """Firecrawl Web Search Request"""
    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results")
    sources: Optional[List[str]] = Field(
        default=None,
        description="Result types: web, news, images"
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description="Categories: github, research, pdf"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location filter for search results"
    )
    tbs: Optional[str] = Field(
        default=None,
        description="Time-based search filter (e.g., 'qdr:d' for past day)"
    )
    timeout: Optional[int] = Field(
        default=None,
        ge=1,
        le=300,
        description="Timeout in seconds for search operation"
    )
    scrape_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options for scraping search results (formats, etc.)"
    )
```

---

## ✅ Результат

Теперь все поля, используемые в endpoint `/api/firecrawl/search`, присутствуют в схеме `FirecrawlSearchRequest`:

- ✅ `query` - обязательное поле
- ✅ `limit` - обязательное поле с дефолтом
- ✅ `sources` - опциональное поле
- ✅ `categories` - опциональное поле
- ✅ `location` - опциональное поле (добавлено)
- ✅ `tbs` - опциональное поле (добавлено)
- ✅ `timeout` - опциональное поле (добавлено)
- ✅ `scrape_options` - опциональное поле (добавлено)

---

## 🧪 Тестирование

После исправления, endpoint `/api/firecrawl/search` должен работать корректно со всеми параметрами:

```json
{
  "query": "care homes in London",
  "limit": 10,
  "sources": ["web", "news"],
  "location": "London, UK",
  "tbs": "qdr:m",
  "timeout": 30,
  "scrape_options": {
    "formats": ["markdown"]
  }
}
```

---

**Статус:** ✅ ИСПРАВЛЕНО

