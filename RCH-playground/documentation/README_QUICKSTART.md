# 🚀 BestTime.app Quick Start Guide

Быстрый старт для тестирования BestTime.app на UK care homes.

## 📁 Файлы в этой папке

```
📦 outputs/
├── BestTime_Testing_Guide_RightCareHome.md  # Полная инструкция
├── besttime_pilot_test.py                   # Готовый Python скрипт
├── test_homes_example.csv                   # Пример тестовых данных
├── .env.template                            # Шаблон для API ключей
└── README_QUICKSTART.md                     # Этот файл
```

---

## ⚡ Быстрый старт (5 минут)

### 1️⃣ Установите зависимости

```bash
pip install requests pandas python-dotenv matplotlib seaborn
```

### 2️⃣ Настройте API ключи

1. Зарегистрируйтесь на https://besttime.app
2. Получите API ключи (Private + Public)
3. Создайте файл `.env`:

```bash
cp .env.template .env
```

4. Откройте `.env` и вставьте ваши ключи:

```
BESTTIME_PRIVATE_KEY=pri_your_actual_key_here
BESTTIME_PUBLIC_KEY=pub_your_actual_key_here
```

### 3️⃣ Подготовьте данные

Используйте пример или создайте свой `test_homes.csv`:

```bash
cp test_homes_example.csv test_homes.csv
```

**Или создайте свой CSV** с колонками:
- `home_id` - Уникальный ID
- `name` - Название care home
- `address` - Адрес (улица и номер)
- `city` - Город
- `postcode` - Почтовый индекс
- `cqc_rating` - CQC рейтинг (Outstanding/Good/Requires Improvement/Inadequate)
- `beds` - Количество мест (опционально)
- `location_type` - urban/rural (опционально)

### 4️⃣ Запустите тест

```bash
python besttime_pilot_test.py
```

### 5️⃣ Проанализируйте результаты

Скрипт создаст файл `besttime_results.csv` с результатами и выведет анализ:

```
📊 PILOT TEST ANALYSIS
==========================================

1️⃣  OVERALL COVERAGE
    Total homes tested: 20
    Homes with data: 14
    Coverage rate: 70.0%
    Rating: 🟢 EXCELLENT

2️⃣  COVERAGE BY CQC RATING
    Outstanding: 80% coverage
    Good: 75% coverage
    Requires Improvement: 60% coverage
    Inadequate: 50% coverage

🎯 RECOMMENDATION
==========================================
✅ PROCEED with BestTime.app
   Coverage rate of 70.0% is sufficient
   BestTime can be primary footfall data source
```

---

## 📊 Что дальше?

### Если Coverage ≥ 70% → ✅ GO

1. **Scale up тест:** Протестируйте 100-200 homes
2. **Manual validation:** Позвоните в 5 top-scoring homes для проверки
3. **Integration:** Интегрируйте BestTime в ваш pipeline

### Если Coverage 50-70% → ⚠️ CONDITIONAL GO

1. **Hybrid approach:** Комбинируйте BestTime + Google Reviews + FSA
2. **Focus on urban:** Используйте только для urban areas
3. **Test alternatives:** Сравните с Huq

### Если Coverage < 50% → ❌ NO-GO

1. **Test Huq:** UK-специфичный провайдер (£1,000/год)
2. **Proxy metrics approach:**
   - Review velocity (reviews per month)
   - Photo upload frequency
   - FSA inspection patterns
3. **Consider partnership:** С care home management software

---

## 💰 Стоимость

**Pilot Test (20 homes):**
- Free tier: 100 credits (достаточно для 50 homes)
- Стоимость: £0

**Production (2,500 homes):**
- Initial forecast: ~£40
- Monthly refresh: ~£40/month
- **Annual cost: ~£480-500**

**Сравнение:**
- Google Places Insights: ~£2,400/год
- Huq: ~£800/год (£1,000 в некоторых источниках)
- BestTime: ~£500/год ✅

---

## 🔧 Troubleshooting

### Проблема: "API keys not found"

**Решение:**
1. Убедитесь, что файл `.env` в той же папке, что и скрипт
2. Проверьте, что ключи не закомментированы (#)
3. Ключи должны начинаться с `pri_` и `pub_`

### Проблема: "No data available" для всех домов

**Причины:**
1. **Адреса неточные** - BestTime требует точные адреса
2. **Homes слишком малы** - малые venues часто не имеют данных
3. **Rural locations** - в сельской местности меньше GPS сигналов

**Решения:**
1. Проверьте формат адресов: `"Street Number, Street Name, City, Postcode, UK"`
2. Сначала протестируйте крупные urban homes
3. Добавьте delay между запросами: `time.sleep(3)`

### Проблема: "Request timeout"

**Решение:**
- Увеличьте timeout в коде: `timeout=60`
- Проверьте интернет соединение
- Попробуйте позже (сервер может быть перегружен)

---

## 📞 Поддержка

**BestTime Support:**
- Website: https://besttime.app
- Documentation: https://documentation.besttime.app/
- Contact: Live chat на их сайте

**RightCareHome Project:**
- См. полную инструкцию: `BestTime_Testing_Guide_RightCareHome.md`

---

## 📝 Следующие шаги

После успешного pilot test:

1. ✅ Задокументируйте результаты
2. ✅ Создайте decision memo для команды
3. ✅ Если GO - интегрируйте в production pipeline
4. ✅ Если NO-GO - тестируйте Huq или альтернативы

---

## 🎓 Дополнительные ресурсы

**Полная инструкция:**
- Откройте `BestTime_Testing_Guide_RightCareHome.md` для:
  - Детальной методологии
  - Manual validation checklist
  - Decision framework
  - Cost calculators
  - Analysis scripts

**Альтернативы BestTime:**
1. **Huq** - UK/Europe focus, £1,000/год
2. **Placer.ai** - US only (не подходит)
3. **Google Places Insights** - BigQuery, ~£2,400/год
4. **Proxy metrics** - Free, но требует больше работы

---

**Good luck! 🚀**

*Questions? См. полный guide или свяжитесь с командой.*
