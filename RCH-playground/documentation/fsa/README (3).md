# 🏥 FSA FHRS API Integration для RightCareHome

Полный пакет документации и кода для интеграции Food Standards Agency (FSA) Food Hygiene Rating Scheme API в платформу RightCareHome.

---

## 📦 Что включено

### 1. 📄 **INTEGRATION_GUIDE.md** (НАЧНИТЕ ЗДЕСЬ!)
Итоговый документ с полными рекомендациями по интеграции:
- Резюме всех возможностей API
- Поэтапный план внедрения (12 недель)
- Архитектура БД
- Алгоритмы анализа (diabetes suitability, risk assessment)
- UI/UX рекомендации
- Performance optimization
- Testing strategy

### 2. 📚 **FSA_API_Examples.md**
Подробная документация по API с примерами:
- 50+ примеров curl-запросов
- Все эндпоинты с описанием параметров
- Фильтры, сортировки, пагинация
- Региональные особенности (England/Scotland)
- Советы по оптимизации

### 3. 🐍 **fsa_api_test.py**
Базовый Python-клиент для тестирования API:
```python
# Пример использования
from fsa_api_test import FSA_FHRS_API

api = FSA_FHRS_API()

# Поиск домов престарелых в Birmingham
homes = api.find_care_homes_near_location(
    latitude=52.4862,
    longitude=-1.8904,
    radius_miles=5,
    min_rating=4
)
```

**Функции:**
- Поиск по координатам, названию, postcode
- Получение детальной информации
- Форматирование результатов
- Error handling

### 4. 🚀 **rightcarehome_fsa_integration.py**
Полная production-ready интеграция для RightCareHome:
```python
from rightcarehome_fsa_integration import FSARightCareHomeIntegration

fsa = FSARightCareHomeIntegration()

# Найти homes
homes = fsa.find_care_homes_near_location(52.4862, -1.8904, 5)

# Оценить риск
for home in homes:
    risk_level, explanation = fsa.assess_food_safety_risk(home)
    print(f"{home.name}: {risk_level.value}")
    
# Diabetes suitability score
score, details = fsa.generate_diabetes_suitability_score(homes[0])
print(f"Diabetes Score: {score}/100")

# Форматирование для разных тарифов
print(fsa.format_for_free_tier(homes[0]))
print(fsa.format_for_professional_tier(homes[0], "diabetes"))
```

**Возможности:**
- Классы для структурированных данных
- Risk assessment (5 уровней)
- Diabetes suitability scoring (0-100)
- Форматирование для FREE/Professional/Premium тарифов
- Trend analysis
- Full type hints

### 5. 📮 **FSA_FHRS_Postman_Collection.json**
Postman коллекция с готовыми запросами для тестирования:
- Справочники (Business Types, Ratings, Authorities)
- Поиск (по названию, postcode, координатам)
- Фильтрованный поиск (только 5/5, только 4-5, red flags)
- Региональные запросы (London, Manchester, Edinburgh)
- Сортировка и пагинация

**Как использовать:**
1. Импортировать в Postman
2. Все переменные уже настроены
3. Запускать запросы по очереди

---

## 🚀 Быстрый старт

### Шаг 1: Протестировать API вручную

```bash
# Простейший тест
curl -X GET "https://api.ratings.food.gov.uk/BusinessTypes/basic" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Шаг 2: Установить зависимости

```bash
pip install requests
```

### Шаг 3: Запустить тестовый скрипт

```bash
python3 fsa_api_test.py
```

### Шаг 4: Интегрировать в свой код

```python
from rightcarehome_fsa_integration import FSARightCareHomeIntegration

fsa = FSARightCareHomeIntegration()

# Ваш код здесь
```

---

## 🎯 Ключевые концепты

### API Endpoint
```
Base URL: https://api.ratings.food.gov.uk
```

### Обязательный заголовок
```
x-api-version: 2  ← БЕЗ ЭТОГО API НЕ РАБОТАЕТ!
```

### BusinessTypeId для Care Homes
```
7835 = "Hospitals/Childcare/Caring Premises"
```

### Рейтинговая система
```
England/Wales/N.Ireland (FHRS):
5 = Excellent
4 = Good
3 = Satisfactory
2 = Improvement needed
1 = Major improvement needed
0 = Urgent improvement needed

Scotland (FHIS):
Pass / Improvement Required
```

### Scores (чем НИЖЕ, тем ЛУЧШЕ!)
```
Hygiene: 0-20 (penalty points)
Structural: 0-20 (penalty points)
Management: 0-30 (penalty points)

0-5 = Excellent
6-10 = Good
11-15 = Fair
16+ = Poor
```

---

## 💡 Практические примеры

### Пример 1: FREE tier - поиск ближайших домов

```python
api = FSARightCareHomeIntegration()

# User location: Birmingham
homes = api.find_care_homes_near_location(
    latitude=52.4862,
    longitude=-1.8904,
    radius_miles=5,
    min_rating=4  # Показываем только 4-5 рейтинг
)

# Топ-3 для shortlist
for home in homes[:3]:
    print(api.format_for_free_tier(home))
```

### Пример 2: Professional tier - diabetes analysis

```python
# User с диабетом выбрал дом для анализа
home = api.get_care_home_details(fhrsid=123456)

# Детальный анализ
print(api.format_for_professional_tier(home, "diabetes"))

# Получить numeric score
score, explanation = api.generate_diabetes_suitability_score(home)
if score >= 80:
    print("✅ EXCELLENT для диабета")
elif score >= 60:
    print("✓ GOOD для диабета")
else:
    print("⚠️ Требует внимания")
```

### Пример 3: Premium tier - мониторинг

```python
# Еженедельная проверка (cron job)
tracked_homes = get_user_tracked_homes(user_id)

for home in tracked_homes:
    # Получить текущий рейтинг
    current = api.get_care_home_details(home.fhrsid)
    
    # Сравнить с предыдущим
    if current.rating_value != home.last_known_rating:
        # Рейтинг изменился!
        send_alert_to_user(
            user_id,
            f"🚨 Rating changed: {home.name} "
            f"{home.last_known_rating} → {current.rating_value}"
        )
        
        # Обновить БД
        update_rating_history(home.fhrsid, current)
```

---

## 📊 Use Cases для RightCareHome

### ✅ FREE Shortlist (3 homes)
**Что показывать:**
- ⭐ Rating: 5/5 или 4/5
- 📅 Last Inspection: October 2024
- ✅ "Safe for diabetes" badge (если 4+)

**Код:**
```python
print(api.format_for_free_tier(home))
```

---

### 💼 Professional Assessment (£119)
**Что показывать:**
- ⭐ Overall Rating: 5/5
- 🔬 Detailed Scores:
  - Hygiene: 3/20 (Excellent)
  - Structural: 5/20 (Excellent)
  - Management: 2/30 (Excellent)
- 🎯 Risk Assessment: ✅ SAFE
- 💉 Diabetes Suitability: 92/100 (EXCELLENT)
- 💬 Right to Reply (если есть)

**Код:**
```python
print(api.format_for_professional_tier(home, "diabetes"))
```

---

### ⭐ Premium Intelligence (£299)
**Что показывать:**
- Всё из Professional +
- 📈 Historical Trend (последние 5 инспекций)
- 🔮 Prediction: следующая инспекция
- ⚡ Active Monitoring: "We check weekly"
- 📲 Alert System: "Instant WhatsApp notification"

**Код:**
```python
history = get_historical_ratings(home.fhrsid)
print(api.format_for_premium_tier(home, history))
```

---

## 🗄️ База данных

### Минимальная схема

```sql
-- Текущие рейтинги
CREATE TABLE fsa_ratings (
    fhrsid INT PRIMARY KEY,
    care_home_id INT,
    rating_value VARCHAR(10),
    rating_date DATE,
    hygiene_score INT,
    structural_score INT,
    management_score INT,
    updated_at TIMESTAMP
);

-- История изменений
CREATE TABLE fsa_rating_history (
    id SERIAL PRIMARY KEY,
    fhrsid INT,
    rating_value VARCHAR(10),
    rating_date DATE,
    detected_at TIMESTAMP
);
```

---

## ⚙️ Production considerations

### 1. Кэширование
```python
# Redis cache (7 дней)
redis.setex(f"fsa:{fhrsid}", 604800, json.dumps(data))
```

### 2. Rate Limiting
```
Рекомендация: max 100 requests/hour
```

### 3. Error Handling
```python
try:
    data = api.get_establishment_details(fhrsid)
except requests.Timeout:
    # Использовать cached version
    data = get_from_cache(fhrsid)
```

### 4. Monitoring
```
- Log всех API calls
- Track response times
- Alert при failures
- Weekly data refresh
```

---

## 🔗 Полезные ссылки

- **API Docs**: https://api.ratings.food.gov.uk/help
- **FSA Website**: https://ratings.food.gov.uk
- **Open Data**: http://ratings.food.gov.uk/open-data/
- **Support**: foodhygiene.rating@food.gov.uk

---

## 📝 Следующие шаги

1. ✅ Прочитать **INTEGRATION_GUIDE.md** (полный план)
2. ✅ Изучить **FSA_API_Examples.md** (все запросы)
3. ✅ Протестировать **Postman коллекцию**
4. ✅ Запустить **fsa_api_test.py**
5. ✅ Интегрировать **rightcarehome_fsa_integration.py**

---

## 🎉 Заключение

FSA FHRS API даёт RightCareHome:

✅ **Конкурентное преимущество** - никто не использует  
✅ **Критичную информацию** - пищевая безопасность для диабета/аллергий  
✅ **Дифференциацию тарифов** - FREE/Professional/Premium  
✅ **Мониторинг качества** - раннее предупреждение о проблемах  
✅ **Доверие клиентов** - объективные государственные данные  

**Бесплатно. Без регистрации. Полное покрытие UK.**

---

*Подготовлено: November 2025*  
*Для: RightCareHome Platform*  
*Версия: 1.0*

## 📞 Вопросы?

Все файлы готовы к использованию. Начните с INTEGRATION_GUIDE.md для полного понимания возможностей!
