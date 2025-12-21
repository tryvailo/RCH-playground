# API Placeholder Validation - Implementation Report

## Проблема

В `config.json` были обнаружены placeholder значения вместо реальных API ключей, что приводило к:
- Неудачной инициализации API клиентов
- Непонятным ошибкам при генерации профессиональных отчетов
- Отсутствию обогащения данных из внешних API

## Исправления

### 1. Companies House API ✅
**Файл:** `utils/client_factory.py` - функция `get_companies_house_client()`
- Добавлена проверка placeholder значений: `"your-companies-house-api-key"`, `"your-companies-house-key"`
- Улучшена обработка ошибок с понятными сообщениями
- Добавлена ранняя проверка в `routers/report_routes.py` перед обогащением

### 2. CQC API ✅
**Файл:** `utils/client_factory.py` - функция `get_cqc_client()`
- Добавлена проверка placeholder значений для:
  - `primary_subscription_key`: `"your-primary-subscription-key"`
  - `secondary_subscription_key`: `"your-secondary-subscription-key"`
  - `partner_code`: `"YourPartnerCode"`
- Добавлена ранняя проверка в `routers/report_routes.py` в 3 местах использования

### 3. Google Places API ✅
**Файл:** `utils/client_factory.py` - функция `get_google_places_client()`
- Добавлена проверка placeholder значений: `"your-google-places-api-key"`
- Улучшена обработка ошибок

### 4. Perplexity API ✅
**Файл:** `utils/client_factory.py` - функция `get_perplexity_client()`
- Добавлена проверка placeholder значений: `"your-perplexity-api-key"`

### 5. OpenAI API ✅
**Файл:** `utils/client_factory.py` - функция `get_openai_client()`
- Добавлена проверка placeholder значений: `"your-openai-api-key"`, `"sk-placeholder"`

### 6. Firecrawl API ✅
**Файл:** `utils/client_factory.py` - функция `get_firecrawl_client()`
- Добавлена проверка placeholder значений: `"your-firecrawl-api-key"`
- Добавлена проверка для опционального Anthropic API ключа

### 7. FSA API ✅
**Файл:** `utils/client_factory.py` - функция `get_fsa_client()`
- Добавлена проверка placeholder значений (FSA API публичный, но проверка добавлена для консистентности)
- Обработка отсутствия ключа (FSA может работать без ключа)

### 8. BestTime API ✅
**Файл:** `utils/client_factory.py` - функция `get_besttime_client()`
- Добавлена проверка placeholder значений для `private_key` и `public_key`

### 9. OS Places API ✅
**Файл:** `data_integrations/os_places_loader.py` - метод `_load_from_config()`
- Добавлена проверка placeholder значений: `"your-os-places-api-key"`

### 10. Anthropic API ✅
**Файл:** `utils/client_factory.py` - функция `get_firecrawl_client()`
- Добавлена проверка placeholder значений для опционального Anthropic ключа (используется в Firecrawl)

## Проверяемые Placeholder Значения

Все функции проверяют следующие placeholder значения:
- `"your-{service}-api-key"`
- `"your-{service}-key"`
- `"placeholder"`
- `"example"`
- `"test"`
- Любые значения, начинающиеся с `"your-"`

## Поведение при Обнаружении Placeholder

1. **Обязательные API** (Companies House, CQC, Google Places, Perplexity, OpenAI, Firecrawl, BestTime):
   - Выбрасывается `ValueError` с понятным сообщением
   - Указывается ссылка на портал для получения ключей
   - Процесс останавливается с информативным сообщением

2. **Опциональные API** (FSA, Anthropic в Firecrawl):
   - Выводится предупреждение
   - API продолжает работать без ключа (если возможно)

3. **В профессиональном отчете** (`routers/report_routes.py`):
   - Ранняя проверка перед обогащением
   - Понятные сообщения в логах
   - Пропуск обогащения без падения всего процесса

## Файлы с Изменениями

1. `utils/client_factory.py` - все функции создания клиентов
2. `routers/report_routes.py` - ранние проверки для CQC и Companies House
3. `services/companies_house_service.py` - проверка в `_get_client()`
4. `data_integrations/os_places_loader.py` - проверка в `_load_from_config()`

## Результат

Теперь все API клиенты:
- ✅ Проверяют placeholder значения перед использованием
- ✅ Выдают понятные сообщения об ошибках
- ✅ Указывают, где получить реальные API ключи
- ✅ Корректно обрабатывают отсутствие ключей
- ✅ Не падают с непонятными ошибками

## Следующие Шаги

Для использования API необходимо установить реальные ключи в `config.json`:

```json
{
  "cqc": {
    "primary_subscription_key": "реальный-ключ",
    "secondary_subscription_key": "реальный-ключ"
  },
  "companies_house": {
    "api_key": "реальный-ключ"
  },
  "google_places": {
    "api_key": "реальный-ключ"
  },
  // ... и т.д.
}
```

Или через переменные окружения (см. `config_manager.py`).

