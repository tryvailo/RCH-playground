# Тестовые поисковые запросы Firecrawl Search для домов престарелых

## Тестовые дома престарелых

1. **Metchley Manor** - Birmingham, B15 2QX (Care UK)
2. **Clare Court** - Birmingham, B15 2QX (Avery Healthcare)
3. **Bartley Green** - Birmingham, B32 3QJ (Sanctuary Care)
4. **Inglewood** - Birmingham, B17 9DJ (Care UK)

---

## 1. Поиск домов престарелых по локации

### Metchley Manor
```json
{
  "query": "Metchley Manor care home Birmingham B15 2QX",
  "limit": 10,
  "sources": ["web"],
  "location": "Birmingham"
}
```

```json
{
  "query": "Metchley Manor Metchley Lane Birmingham",
  "limit": 10,
  "sources": ["web", "news"]
}
```

### Clare Court
```json
{
  "query": "Clare Court care home Birmingham B15 2QX",
  "limit": 10,
  "sources": ["web"],
  "location": "Birmingham"
}
```

```json
{
  "query": "Clare Court Avery Healthcare Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

### Bartley Green
```json
{
  "query": "Bartley Green care home Birmingham B32 3QJ",
  "limit": 10,
  "sources": ["web"],
  "location": "Birmingham"
}
```

```json
{
  "query": "Bartley Green Lodge Sanctuary Care Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

### Inglewood
```json
{
  "query": "Inglewood care home Birmingham B17 9DJ",
  "limit": 10,
  "sources": ["web"],
  "location": "Birmingham"
}
```

```json
{
  "query": "Inglewood Road care home Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

---

## 2. Поиск по типу услуг

### Metchley Manor
```json
{
  "query": "Metchley Manor dementia care Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Metchley Manor nursing care services",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Metchley Manor respite care Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

### Clare Court
```json
{
  "query": "Clare Court dementia care Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Clare Court Avery Healthcare services",
  "limit": 10,
  "sources": ["web"]
}
```

### Bartley Green
```json
{
  "query": "Bartley Green Lodge residential care Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Bartley Green Sanctuary Care services",
  "limit": 10,
  "sources": ["web"]
}
```

### Inglewood
```json
{
  "query": "Inglewood care home services Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

---

## 3. Поиск новостей и событий

### Metchley Manor
```json
{
  "query": "Metchley Manor care home news Birmingham",
  "limit": 10,
  "sources": ["news"],
  "tbs": "qdr:m"
}
```

```json
{
  "query": "Metchley Manor CQC inspection results",
  "limit": 10,
  "sources": ["news", "web"],
  "tbs": "qdr:y"
}
```

```json
{
  "query": "Metchley Manor care home awards recognition",
  "limit": 10,
  "sources": ["news"],
  "tbs": "qdr:y"
}
```

### Clare Court
```json
{
  "query": "Clare Court care home news Birmingham",
  "limit": 10,
  "sources": ["news"],
  "tbs": "qdr:m"
}
```

```json
{
  "query": "Clare Court Avery Healthcare CQC inspection",
  "limit": 10,
  "sources": ["news", "web"],
  "tbs": "qdr:y"
}
```

```json
{
  "query": "Clare Court care home complaints issues",
  "limit": 10,
  "sources": ["news"],
  "tbs": "qdr:y"
}
```

### Bartley Green
```json
{
  "query": "Bartley Green Lodge care home news",
  "limit": 10,
  "sources": ["news"],
  "tbs": "qdr:m"
}
```

```json
{
  "query": "Bartley Green Sanctuary Care CQC rating",
  "limit": 10,
  "sources": ["news", "web"],
  "tbs": "qdr:y"
}
```

### Inglewood
```json
{
  "query": "Inglewood care home Birmingham news",
  "limit": 10,
  "sources": ["news"],
  "tbs": "qdr:m"
}
```

```json
{
  "query": "Inglewood Care UK inspection results",
  "limit": 10,
  "sources": ["news", "web"],
  "tbs": "qdr:y"
}
```

---

## 4. Поиск отзывов и репутации

### Metchley Manor
```json
{
  "query": "Metchley Manor care home reviews Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Metchley Manor care home ratings testimonials",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Metchley Manor care home complaints feedback",
  "limit": 10,
  "sources": ["web", "news"]
}
```

### Clare Court
```json
{
  "query": "Clare Court care home reviews Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Clare Court Avery Healthcare reviews ratings",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Clare Court care home family feedback",
  "limit": 10,
  "sources": ["web"]
}
```

### Bartley Green
```json
{
  "query": "Bartley Green Lodge care home reviews",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Bartley Green Sanctuary Care reviews Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

### Inglewood
```json
{
  "query": "Inglewood care home reviews Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Inglewood Care UK reviews ratings",
  "limit": 10,
  "sources": ["web"]
}
```

---

## 5. Поиск цен и финансирования

### Metchley Manor
```json
{
  "query": "Metchley Manor care home prices costs Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Metchley Manor care home fees funding options",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Metchley Manor weekly rates costs",
  "limit": 10,
  "sources": ["web"]
}
```

### Clare Court
```json
{
  "query": "Clare Court care home prices Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Clare Court Avery Healthcare fees costs",
  "limit": 10,
  "sources": ["web"]
}
```

### Bartley Green
```json
{
  "query": "Bartley Green Lodge care home prices",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Bartley Green Sanctuary Care fees funding",
  "limit": 10,
  "sources": ["web"]
}
```

### Inglewood
```json
{
  "query": "Inglewood care home prices Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Inglewood Care UK costs fees",
  "limit": 10,
  "sources": ["web"]
}
```

---

## 6. Поиск компаний и операторов

### Metchley Manor
```json
{
  "query": "Care UK Metchley Manor operator company",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Care UK care homes Birmingham network",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Care UK company information ownership",
  "limit": 10,
  "sources": ["web"]
}
```

### Clare Court
```json
{
  "query": "Avery Healthcare Clare Court operator",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Avery Healthcare care homes network UK",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Avery Healthcare company information",
  "limit": 10,
  "sources": ["web"]
}
```

### Bartley Green
```json
{
  "query": "Sanctuary Care Bartley Green operator",
  "limit": 10,
  "sources": ["web"]
}
```

```json
{
  "query": "Sanctuary Care homes network Birmingham",
  "limit": 10,
  "sources": ["web"]
}
```

### Inglewood
```json
{
  "query": "Care UK Inglewood operator company",
  "limit": 10,
  "sources": ["web"]
}
```

---

## 7. Поиск исследований и академических материалов

### Общие запросы для всех домов
```json
{
  "query": "care home quality research Birmingham UK",
  "limit": 10,
  "categories": ["research"]
}
```

```json
{
  "query": "elderly care studies nursing homes UK",
  "limit": 10,
  "categories": ["research"]
}
```

```json
{
  "query": "care home quality assessment methods",
  "limit": 10,
  "categories": ["research"]
}
```

### Metchley Manor
```json
{
  "query": "care home quality research Care UK",
  "limit": 10,
  "categories": ["research"]
}
```

### Clare Court
```json
{
  "query": "dementia care research Avery Healthcare",
  "limit": 10,
  "categories": ["research"]
}
```

### Bartley Green
```json
{
  "query": "residential care research Sanctuary Care",
  "limit": 10,
  "categories": ["research"]
}
```

---

## 8. Поиск изображений и визуального контента

### Metchley Manor
```json
{
  "query": "Metchley Manor care home Birmingham images photos",
  "limit": 8,
  "sources": ["images"]
}
```

```json
{
  "query": "Metchley Manor care home facilities rooms",
  "limit": 8,
  "sources": ["images"]
}
```

```json
{
  "query": "Metchley Manor care home virtual tour",
  "limit": 5,
  "sources": ["images"]
}
```

### Clare Court
```json
{
  "query": "Clare Court care home Birmingham photos",
  "limit": 8,
  "sources": ["images"]
}
```

```json
{
  "query": "Clare Court Avery Healthcare facilities images",
  "limit": 8,
  "sources": ["images"]
}
```

### Bartley Green
```json
{
  "query": "Bartley Green Lodge care home photos",
  "limit": 8,
  "sources": ["images"]
}
```

```json
{
  "query": "Bartley Green Sanctuary Care images",
  "limit": 8,
  "sources": ["images"]
}
```

### Inglewood
```json
{
  "query": "Inglewood care home Birmingham images",
  "limit": 8,
  "sources": ["images"]
}
```

---

## 9. Поиск в GitHub (код и проекты)

### Общие запросы
```json
{
  "query": "care home management software",
  "limit": 10,
  "categories": ["github"]
}
```

```json
{
  "query": "elderly care API integration",
  "limit": 10,
  "categories": ["github"]
}
```

```json
{
  "query": "care home booking system open source",
  "limit": 10,
  "categories": ["github"]
}
```

```json
{
  "query": "CQC inspection data API",
  "limit": 10,
  "categories": ["github"]
}
```

```json
{
  "query": "care home quality assessment tools",
  "limit": 10,
  "categories": ["github"]
}
```

---

## 10. Поиск PDF документов

### Metchley Manor
```json
{
  "query": "Metchley Manor CQC inspection report PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

```json
{
  "query": "Metchley Manor care home policies PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

### Clare Court
```json
{
  "query": "Clare Court CQC inspection report PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

```json
{
  "query": "Clare Court Avery Healthcare brochure PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

### Bartley Green
```json
{
  "query": "Bartley Green Lodge CQC report PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

### Inglewood
```json
{
  "query": "Inglewood care home CQC inspection PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

### Общие PDF запросы
```json
{
  "query": "care home standards guidance PDF UK",
  "limit": 10,
  "categories": ["pdf"]
}
```

```json
{
  "query": "care home policies procedures PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

```json
{
  "query": "CQC inspection reports care homes PDF",
  "limit": 10,
  "categories": ["pdf"]
}
```

---

## Комбинированные запросы (несколько параметров)

### Поиск с фильтром по времени и локации
```json
{
  "query": "care homes Birmingham news 2024",
  "limit": 10,
  "sources": ["news"],
  "location": "Birmingham",
  "tbs": "qdr:m"
}
```

### Поиск с scraping результатов
```json
{
  "query": "Metchley Manor care home Birmingham",
  "limit": 5,
  "sources": ["web"],
  "scrape_options": {
    "formats": ["markdown", "links"]
  }
}
```

### Комбинированный поиск (web + news + images)
```json
{
  "query": "Clare Court care home Birmingham",
  "limit": 10,
  "sources": ["web", "news", "images"]
}
```

### Поиск в нескольких категориях
```json
{
  "query": "care home management software",
  "limit": 15,
  "categories": ["github", "research"]
}
```

### Поиск с временным фильтром и локацией
```json
{
  "query": "care homes Birmingham reviews",
  "limit": 10,
  "sources": ["web"],
  "location": "Birmingham",
  "tbs": "qdr:m"
}
```

---

## Примеры использования в UI

### Быстрые тесты для Metchley Manor
1. **Базовый поиск:** "Metchley Manor care home Birmingham"
2. **Новости:** "Metchley Manor news" (sources: news, tbs: qdr:m)
3. **Отзывы:** "Metchley Manor reviews" (sources: web)
4. **Изображения:** "Metchley Manor photos" (sources: images)
5. **CQC отчет:** "Metchley Manor CQC report PDF" (categories: pdf)

### Быстрые тесты для Clare Court
1. **Базовый поиск:** "Clare Court care home Birmingham"
2. **Новости:** "Clare Court Avery Healthcare news" (sources: news, tbs: qdr:m)
3. **Отзывы:** "Clare Court reviews" (sources: web)
4. **Изображения:** "Clare Court photos" (sources: images)
5. **CQC отчет:** "Clare Court CQC report PDF" (categories: pdf)

### Быстрые тесты для Bartley Green
1. **Базовый поиск:** "Bartley Green Lodge care home Birmingham"
2. **Новости:** "Bartley Green Sanctuary Care news" (sources: news, tbs: qdr:m)
3. **Отзывы:** "Bartley Green reviews" (sources: web)
4. **Изображения:** "Bartley Green photos" (sources: images)
5. **CQC отчет:** "Bartley Green CQC report PDF" (categories: pdf)

### Быстрые тесты для Inglewood
1. **Базовый поиск:** "Inglewood care home Birmingham"
2. **Новости:** "Inglewood Care UK news" (sources: news, tbs: qdr:m)
3. **Отзывы:** "Inglewood reviews" (sources: web)
4. **Изображения:** "Inglewood photos" (sources: images)
5. **CQC отчет:** "Inglewood CQC report PDF" (categories: pdf)

---

## Рекомендации по использованию

1. **Начните с базового поиска** без фильтров для общего обзора
2. **Используйте фильтры по времени** для актуальной информации (tbs: qdr:m)
3. **Комбинируйте источники** для более полной картины (web + news + images)
4. **Включайте scraping** только когда нужен полный контент страниц
5. **Используйте категории** для специализированного поиска (research, github, pdf)
6. **Экспериментируйте с формулировками** запросов для лучших результатов

