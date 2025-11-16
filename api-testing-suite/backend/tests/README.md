# Тесты для API Testing Suite

## Структура тестов

- `test_cache.py` - Тесты для Redis кэширования
- `test_google_places_cache.py` - Тесты для кэширования Google Places API
- `test_error_handling.py` - Тесты для обработки ошибок
- `test_endpoints.py` - Тесты для API эндпоинтов

## Запуск тестов

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить все тесты
pytest tests/ -v

# Запустить конкретный файл тестов
pytest tests/test_cache.py -v

# Запустить с покрытием кода
pytest tests/ --cov=. --cov-report=html
```

## Что тестируется

### Кэширование (test_cache.py)
- ✅ Отключение кэша при недоступности Redis
- ✅ Генерация ключей кэша
- ✅ Операции get/set/delete/exists
- ✅ get_or_set с кэшированием
- ✅ Обработка ошибок при операциях с кэшем

### Google Places API с кэшированием (test_google_places_cache.py)
- ✅ Попадание в кэш (cache hit)
- ✅ Промах кэша (cache miss) с последующим кэшированием
- ✅ Работа без кэша
- ✅ Генерация ключей кэша

### Обработка ошибок (test_error_handling.py)
- ✅ HTTP ошибки (401, 403, 429, 500)
- ✅ Таймауты
- ✅ Ошибки подключения
- ✅ Ошибки валидации
- ✅ Отсутствующие данные
- ✅ Структура детальной информации об ошибках

### Эндпоинты (test_endpoints.py)
- ✅ Статистика кэша
- ✅ Очистка кэша
- ✅ Тест кэша
- ✅ Обработка ошибок в эндпоинтах
- ✅ Валидация параметров

## Улучшения обработки ошибок

Все эндпоинты теперь используют улучшенную обработку ошибок через `utils.error_handler`:

1. **Детальная информация об ошибках**:
   - Тип ошибки
   - HTTP статус код (если применимо)
   - Сообщение об ошибке
   - Контекст операции
   - Предложения по исправлению

2. **Специфичные обработки**:
   - 401 Unauthorized - проверка API ключа
   - 403 Forbidden - проверка прав доступа
   - 429 Rate Limit - предложения по поводу лимитов
   - 500 Server Error - предложения по поводу сервера
   - Timeout - предложения по поводу таймаутов
   - Connection Error - предложения по поводу подключения

3. **Логирование**:
   - Все ошибки логируются с полным traceback
   - Контекст операции сохраняется в логах

## Примеры использования

### Тестирование кэша

```python
from tests.test_cache import TestCacheManager

# Тест отключения кэша
test = TestCacheManager()
await test.test_cache_disabled_when_redis_unavailable()
```

### Тестирование обработки ошибок

```python
from tests.test_error_handling import TestErrorHandler
from utils.error_handler import handle_api_error
import httpx

error = httpx.HTTPStatusError(...)
error_detail = handle_api_error(error, "Google Places", "search")
assert "suggestions" in error_detail
```

## Примечания

- Тесты используют моки для изоляции от внешних зависимостей
- Redis не требуется для запуска тестов (используются моки)
- Все тесты асинхронные (используется pytest-asyncio)

