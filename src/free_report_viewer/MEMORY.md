# Контекст Fair Cost Gap - ЗАПОМНИТЬ НАВСЕГДА

## Fair Cost Gap = разница между рыночной ценой и MSIF fair cost lower bound

### Источники данных:
1. **Рыночная цена (market_price):**
   - Lottie average (предпочтительно)
   - Или scraped цена с сайтов домов престарелых

2. **MSIF lower bound (msif_lower_bound):**
   - Из БД `msif_fees_2025`
   - Колонка `nursing_median` для nursing care
   - Колонка `residential_median` для residential care
   - Фильтр по `local_authority` пользователя

### Формула:
```
gap_week = market_price - msif_lower_bound
gap_year = gap_week * 52
gap_5year = gap_year * 5
```

### Визуализация:
- **ОБЯЗАТЕЛЬНЫЙ эмоциональный блок** в отчёте
- Красный цвет (#EF4444)
- Огромные цифры (font-size: 3.5rem)
- Градиентный красный заголовок
- Выделенный блок с тенью

### Определение local_authority:
- Из postcode пользователя
- Используется для запроса к БД msif_fees_2025
- Fallback на mock данные если БД недоступна

