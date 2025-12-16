# 🔧 Настройка Indeed Search (Google Custom Search)

## Требования

Для работы Indeed Search Service нужно настроить Google Custom Search API.

## Шаг 1: Google Cloud Console

1. Откройте https://console.cloud.google.com/apis/credentials
2. Создайте новый API key (или используйте существующий `google_places.api_key`)
3. Включите "Custom Search API" в разделе APIs & Services → Library

## Шаг 2: Создание Custom Search Engine

1. Откройте https://cse.google.com/cse/all
2. Нажмите "Add" (Создать поисковую систему)
3. В поле "Sites to search" добавьте: `uk.indeed.com`
4. Дайте имя, например: "Indeed UK Search"
5. Нажмите "Create"
6. После создания, перейдите в "Control Panel" → "Basics"
7. Скопируйте **Search engine ID** (cx)

## Шаг 3: Добавить в config.json

Откройте `backend/config.json` и добавьте `search_engine_id`:

```json
{
  "google_places": {
    "api_key": "AIzaSy...",
    "search_engine_id": "ВАШ_SEARCH_ENGINE_ID_ЗДЕСЬ"
  }
}
```

## Шаг 4: Проверка

После настройки перезапустите backend и проверьте:

```bash
curl http://localhost:8000/api/indeed/health
```

Ответ должен показать:
```json
{
  "status": "ok",
  "components": {
    "google_custom_search": "configured"
  }
}
```

## Тестирование

```bash
# Поиск компании на Indeed
curl -X POST http://localhost:8000/api/indeed/search \
  -H "Content-Type: application/json" \
  -d '{
    "search_term": "Monarch Healthcare",
    "expected_city": "Burton On Trent",
    "scrape_reviews": false
  }'
```

## Стоимость

- **Бесплатно**: 100 запросов/день
- **После лимита**: $5 за 1000 запросов

## Альтернатива (без search_engine_id)

Если Google Custom Search не настроен, система автоматически использует **Perplexity AI** как fallback для поиска Indeed reviews. Это менее точно, но работает без дополнительной настройки.
