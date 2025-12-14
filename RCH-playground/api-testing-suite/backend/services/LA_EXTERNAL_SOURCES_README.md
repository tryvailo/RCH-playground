# Local Authority External Sources Integration

## Обзор

Модуль `la_external_sources.py` предоставляет интеграцию с официальными API и источниками данных для обогащения информации о контактах Local Authorities.

## Доступные источники данных

### 1. Postcodes.io API ✅ Реализовано
- **URL**: `https://api.postcodes.io/postcodes`
- **Описание**: Бесплатный API для разрешения UK postcodes в Local Authority
- **Использование**: Уже используется в проекте для разрешения postcodes
- **Ограничения**: Не предоставляет прямые контакты, только географическую информацию

### 2. GOV.UK Register API ⚠️ Частично реализовано
- **URL**: `https://www.registers.service.gov.uk/registers/local-authorities/records`
- **Описание**: Официальный реестр Local Authorities с базовой информацией
- **Статус**: API может требовать аутентификацию или иметь ограничения
- **Данные**: Официальные названия, веб-сайты, базовая контактная информация

### 3. ONS (Office for National Statistics) API
- **URL**: `https://www.ons.gov.uk/api/v1/geography`
- **Описание**: Статистические данные о Local Authorities
- **Статус**: Требует исследования доступных endpoints
- **Данные**: Географические коды, статистика

### 4. Google Places API
- **Описание**: Поиск контактной информации через Google Places
- **Статус**: Требует API ключ (уже есть в проекте)
- **Данные**: Телефоны, адреса, веб-сайты

### 5. Local Government Association (LGA) Directory
- **Описание**: Справочник LGA с контактами советов
- **Статус**: Требует исследования доступности API или данных
- **Данные**: Контакты, веб-сайты, информация о советах

## Использование

### Базовое использование

```python
from services.la_external_sources import LAExternalSources

# Инициализация
sources = LAExternalSources()

# Обогащение данных одного совета
council = {
    'council_name': 'Birmingham City Council',
    'ons_code': 'E08000025'
}

enriched = await sources.enrich_council_data(council)
```

### Пакетная обработка

```python
# Обогащение нескольких советов
councils = [...]  # список советов
enriched = await sources.batch_enrich_councils(councils, limit=10)
```

## Интеграция в скрипт сбора

Модуль автоматически интегрирован в `la_contacts_collector.py`:

1. **Приоритет**: Внешние источники проверяются ПЕРЕД скрапингом веб-сайтов
2. **Fallback**: Если внешние источники не дают результатов, используется скрапинг
3. **Асинхронность**: Все запросы к внешним API выполняются асинхронно

## Расширение функциональности

### Добавление нового источника

1. Создайте новый метод в классе `LAExternalSources`:
```python
async def fetch_from_new_source(self, param: str) -> Optional[Dict[str, Any]]:
    """Fetch data from new source"""
    try:
        # Реализация
        pass
    except Exception as e:
        logger.warning(f"New source error: {e}")
    return None
```

2. Добавьте вызов в метод `enrich_council_data`:
```python
new_data = await self.fetch_from_new_source(council.get('param'))
if new_data:
    # Объединить данные
    pass
```

## Рекомендации по улучшению

1. **Кэширование**: Добавить кэширование результатов API запросов
2. **Rate Limiting**: Улучшить обработку rate limits для разных API
3. **Обработка ошибок**: Более детальная обработка различных типов ошибок
4. **Мониторинг**: Добавить метрики использования каждого источника
5. **Валидация данных**: Проверка качества данных из внешних источников

## Ограничения

- Некоторые API могут требовать аутентификацию
- Rate limits могут ограничивать частоту запросов
- Не все источники предоставляют полную контактную информацию
- Данные могут быть неполными или устаревшими

## Следующие шаги

1. Исследовать доступность GOV.UK Register API
2. Реализовать интеграцию с Google Places API (если доступен ключ)
3. Найти и интегрировать дополнительные источники данных
4. Добавить кэширование для улучшения производительности

