# Free Report New - Анализ с questionnaire_1.json

**Дата:** 2025-01-XX  
**Опросник:** questionnaire_1.json  
**Источник данных:** SQLite база данных (care_homes.db)

---

## 📋 Параметры запроса

Из `questionnaire_1.json`:
- **Postcode:** B11 1AA (Birmingham, Sparkbrook)
- **Coordinates:** 52.4558, -1.8704
- **Local Authority:** Birmingham
- **Budget:** £1200/week
- **Care Type:** residential_care
- **Max Distance:** 30km
- **Priority Order:** quality, proximity, cost
- **Priority Weights:** [50, 30, 20]
- **CHC Probability:** 35.5%

---

## 🗄️ SQLite База Данных

### Расположение
- **Путь:** `RCH-playground/RCH-playground/api-testing-suite/backend/care_homes.db`
- **Сервис:** `SQLiteCareHomesService`
- **Файл:** `services/sqlite_care_homes_service.py`

### Статистика базы данных

```sql
-- Общая статистика
SELECT COUNT(*) FROM care_homes;
-- Результат: [проверить через анализ]

-- Дома в Birmingham
SELECT COUNT(*) FROM care_homes 
WHERE local_authority LIKE '%Birmingham%';
-- Результат: [проверить через анализ]

-- Дома с Good/Outstanding рейтингом
SELECT COUNT(*) FROM care_homes 
WHERE local_authority LIKE '%Birmingham%' 
  AND rating IN ('Good', 'Outstanding');
-- Результат: [проверить через анализ]

-- Residential care дома
SELECT COUNT(*) FROM care_homes 
WHERE local_authority LIKE '%Birmingham%' 
  AND rating IN ('Good', 'Outstanding')
  AND (care_types LIKE '%residential%' OR care_residential = 1);
-- Результат: [проверить через анализ]
```

---

## 🔄 Процесс генерации отчета

### Шаг 1: Загрузка данных из SQLite

**Код:** `routers/free_report_routes.py` (строки 120-158)

```python
# Используется SQLiteCareHomesService
service = SQLiteCareHomesService(str(db_path))
care_homes = service.get_care_homes(
    postcode=postcode,
    local_authority=local_authority,
    care_type=care_type,
    max_distance_km=30.0,
    user_lat=user_lat,
    user_lon=user_lon,
    limit=50,
    min_rating='Good'
)
```

**Ожидаемый результат:**
- ✅ Загрузка из SQLite (<100ms)
- ✅ Фильтрация по:
  - Local Authority: Birmingham
  - Care Type: residential
  - Rating: Good или Outstanding
  - Distance: ≤ 30km
  - Price: > 0

### Шаг 2: Фильтрация по качеству

**Код:** `services/free_report_generator_service.py`

- Фильтрует дома с рейтингом Good или Outstanding
- Проверяет соответствие care_type

### Шаг 3: Matching алгоритм

**Код:** `services/free_report_matching_service.py`

Выбирает 3 дома:
1. **Safe Bet** - лучший баланс качества, цены, местоположения
2. **Best Value** - лучшее соотношение цена/качество
3. **Premium** - высочайшее качество

### Шаг 4: Fair Cost Gap расчет

**Код:** `services/fair_cost_gap_service.py`

- Рассчитывает разницу между бюджетом и MSIF fair cost
- Использует данные из MSIF таблицы в SQLite

---

## 📊 Ожидаемые результаты

### Количество домов

1. **Загружено из SQLite:** [X] домов
2. **После фильтрации по качеству:** [Y] домов
3. **После matching:** 3 дома (Safe Bet, Best Value, Premium)

### Структура ответа

```json
{
  "report_id": "uuid",
  "care_homes": [
    {
      "name": "...",
      "rating": "Good" | "Outstanding",
      "weekly_cost": 1200,
      "distance_km": 15.5,
      "match_type": "Safe Bet" | "Best Value" | "Premium"
    }
  ],
  "fair_cost_gap": {
    "gap_week": 150,
    "gap_year": 7800,
    "gap_5year": 39000
  }
}
```

---

## ✅ Критерии успешного выполнения

- [ ] Данные загружаются из SQLite базы данных
- [ ] В логах видно: "✅ Loaded X care homes from SQLite (FAST!)"
- [ ] Загружено > 0 домов для Birmingham
- [ ] Все дома имеют рейтинг Good или Outstanding
- [ ] Все дома соответствуют care_type: residential
- [ ] Все дома в пределах 30km от B11 1AA
- [ ] Выбрано 3 дома (Safe Bet, Best Value, Premium)
- [ ] Fair Cost Gap рассчитан корректно
- [ ] Время генерации < 2 секунд (благодаря SQLite)

---

## 🔍 Проверка источника данных

### Логи Python backend должны содержать:

```
📥 STEP 1 - Loading care homes from SQLite database...
✅ Loaded X care homes from SQLite (FAST!)
📊 STEP 1 - Initial load: X homes
   Sample home: [Name] | Rating: [Rating] | Price: £[Price]
```

### Если используется CSV fallback:

```
⚠️ SQLite load failed: [error]
📥 Falling back to CSV...
✅ Loaded X homes from CSV
```

---

## 📝 Следующие шаги

1. Запустить Free Report New через фронтенд
2. Проверить логи backend
3. Проанализировать результаты
4. Сравнить с ожидаемыми значениями
5. Убедиться, что данные из SQLite, а не CSV


