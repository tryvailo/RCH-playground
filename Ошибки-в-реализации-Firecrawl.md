# Ошибки в реализации Firecrawl API

## Анализ документации vs Реализация

### ❌ ОШИБКА #1: Неправильное использование Extract endpoint для одной страницы

**Что я сделал неправильно:**
```python
# В extract_care_home_data_full()
extract_payload = {
    "urls": [f"{url}/*"],  # Wildcard для одной страницы - НЕПРАВИЛЬНО!
    "prompt": "...",
    "schema": extraction_schema
}
```

**Правильный подход согласно документации:**

Для **одной страницы** нужно использовать **Scrape endpoint** с JSON extraction в формате:
```python
# ПРАВИЛЬНО: Scrape endpoint с JSON extraction
formats=[{
    "type": "json",
    "schema": extraction_schema,
    "prompt": "Extract care home details..."
}]
```

Extract endpoint предназначен для **нескольких URL одновременно**, а не для одной страницы с wildcard.

---

### ❌ ОШИБКА #2: Не используется правильный формат для Scrape endpoint

**Что я сделал неправильно:**
- Использую Extract endpoint вместо Scrape endpoint для одной страницы
- Не использую формат `{"type": "json", "schema": {...}}` в массиве `formats`

**Правильный формат согласно документации:**
```python
# Scrape endpoint с JSON extraction
result = firecrawl.scrape(
    'https://care-home.com/facility',
    formats=[{
        "type": "json",
        "schema": CareHome.model_json_schema(),
        "prompt": "Extract care home details including contact info and ratings"
    }]
)

# Доступ к данным
care_home_data = result['data']['json']
```

---

### ❌ ОШИБКА #3: Wildcard `url/*` не оптимален для одной страницы

**Проблема:**
- Wildcard `url/*` заставляет Firecrawl обходить весь сайт
- Это медленнее и дороже для извлечения данных с одной страницы
- Extract endpoint с wildcard предназначен для каталогов, а не для отдельных страниц

**Правильный подход:**
- Для одной страницы: использовать Scrape endpoint
- Для нескольких страниц: использовать Extract endpoint с массивом конкретных URL
- Для каталогов: использовать Extract endpoint с wildcard

---

## ✅ Правильная реализация

### Для одной страницы (рекомендуемый подход):

```python
async def extract_care_home_data_full(
    self,
    url: str,
    care_home_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract structured data from a single care home page
    Uses Scrape endpoint with JSON extraction - RECOMMENDED for single pages
    """
    extraction_schema = {
        "type": "object",
        "properties": {
            # ... schema definition
        }
    }
    
    # Используем Scrape endpoint с JSON extraction
    scrape_payload = {
        "url": url,  # Конкретный URL, не wildcard!
        "formats": [{
            "type": "json",
            "schema": extraction_schema,
            "prompt": f"""Extract comprehensive information about {care_home_name or 'this care home'}:
            1. Staff qualifications and team size
            2. All facilities and amenities
            3. Care services and specializations
            4. Detailed pricing information
            5. Activities and programs
            6. Contact details and registration info"""
        }]
    }
    
    response = await self.client.post(
        f"{self.base_url}/scrape",
        json=scrape_payload
    )
    response.raise_for_status()
    result = response.json()
    
    # Данные находятся в result['data']['json']
    if result.get("success") and "data" in result:
        json_data = result["data"].get("json", {})
        return {
            "care_home_name": care_home_name,
            "website_url": url,
            "structured_data": json_data,
            "extraction_method": "scrape-json-extraction-v2.5",
            "scraped_at": datetime.now().isoformat()
        }
```

### Для нескольких страниц (если нужно):

```python
# Используем Extract endpoint с массивом конкретных URL
extract_payload = {
    "urls": [
        f"{url}/about",
        f"{url}/services",
        f"{url}/facilities",
        f"{url}/pricing"
    ],  # Конкретные URL, не wildcard!
    "prompt": "...",
    "schema": extraction_schema
}
```

---

## Выводы

1. ❌ **Неправильно:** Использовать Extract endpoint с wildcard `url/*` для одной страницы
2. ✅ **Правильно:** Использовать Scrape endpoint с JSON extraction для одной страницы
3. ❌ **Неправильно:** Не использовать формат `{"type": "json", "schema": {...}}` в массиве `formats`
4. ✅ **Правильно:** Использовать формат `formats=[{"type": "json", "schema": {...}}]` для Scrape endpoint

---

## Почему это важно?

1. **Производительность:** Scrape endpoint быстрее для одной страницы
2. **Стоимость:** Scrape endpoint дешевле, чем Extract с wildcard
3. **Точность:** Scrape endpoint с JSON extraction дает более точные результаты для одной страницы
4. **Соответствие документации:** Документация явно рекомендует Scrape endpoint для одной страницы

