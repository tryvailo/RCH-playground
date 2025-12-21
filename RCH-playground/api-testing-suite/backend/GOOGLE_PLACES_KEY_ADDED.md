# Google Places API Key - Configuration Status

## ✅ Ключ добавлен в config.json

**Дата:** 2025-01-XX
**Ключ:** `AIzaSyDAMAyN1b8t05DJGIBt9jr6FA3zEbAVOU8`

### Расположение
Файл: `RCH-playground/RCH-playground/api-testing-suite/backend/config.json`

```json
{
  "google_places": {
    "api_key": "AIzaSyDAMAyN1b8t05DJGIBt9jr6FA3zEbAVOU8",
    "search_engine_id": "your-search-engine-id"
  }
}
```

## Проверка работы

### 1. Загрузка ключа
Ключ загружается через:
- `config_manager.py` → `get_credentials()`
- `utils/client_factory.py` → `get_google_places_client()`
- Проверка placeholder значений пропускает реальный ключ ✅

### 2. Google Places Explorer
**Frontend:** `frontend/src/pages/GooglePlacesExplorer.tsx`
**Route:** `/google-places`
**Backend Routes:** `/api/google-places/*`

#### Доступные эндпоинты:
- `GET /api/google-places/search` - поиск по имени/адресу
- `GET /api/google-places/nearby` - поиск рядом с координатами
- `GET /api/google-places/details/{place_id}` - детали места
- `GET /api/google-places/photo/{photo_reference}` - фото места
- `GET /api/google-places/{place_id}/popular-times` - популярные времена (требует BestTime API)
- `GET /api/google-places/{place_id}/insights` - инсайты (требует BestTime API)

### 3. Использование в профессиональном отчете
Google Places API используется для обогащения данных в:
- `routers/report_routes.py` - секция обогащения Google Places
- `services/google_places_enrichment_service.py` - сервис обогащения

## Проверка работоспособности

### Тест 1: Инициализация клиента
```python
from utils.client_factory import get_google_places_client
client = get_google_places_client()
# Должен успешно создать клиент без ошибок
```

### Тест 2: Поиск места
```bash
curl "http://localhost:8000/api/google-places/search?query=care+home+London"
```

### Тест 3: Frontend Explorer
1. Открыть `http://localhost:3000/google-places`
2. Ввести название care home
3. Проверить, что результаты возвращаются

## Важные замечания

1. **Placeholder проверка:** Ключ `AIzaSyDAMAyN1b8t05DJGIBt9jr6FA3zEbAVOU8` не является placeholder, поэтому проверка в `get_google_places_client()` пропустит его ✅

2. **Search Engine ID:** `search_engine_id` все еще placeholder, но он используется только для Custom Search API (если используется), не для Places API

3. **Кэширование:** Google Places API использует Redis кэш для оптимизации стоимости (см. `api_clients/google_places_client.py`)

4. **Стоимость API:**
   - Find Place: ~£0.0346
   - Place Details: ~£0.017
   - Nearby Search: ~£0.032 за результат
   - Кэш снижает стоимость на 24 часа

## Следующие шаги

1. ✅ Ключ добавлен в config.json
2. ⏳ Перезапустить backend сервер для загрузки нового ключа
3. ⏳ Протестировать Google Places Explorer через UI
4. ⏳ Проверить работу в профессиональном отчете

## Статус

✅ **Ключ добавлен и готов к использованию**

После перезапуска backend сервера Google Places Explorer должен работать корректно.

