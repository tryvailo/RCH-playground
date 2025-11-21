# 🗄️ Тестовая база данных для домов престарелых

**Дата создания:** 2025-01-XX  
**Статус:** ✅ Готово к использованию

---

## 📁 Файлы

### 1. `create_care_homes_db.sql`
**Полный SQL скрипт** для создания и заполнения базы данных PostgreSQL.

**Содержит:**
- ✅ CREATE TABLE с полной схемой
- ✅ Индексы для оптимизации запросов
- ✅ 30 INSERT statements с тестовыми данными
- ✅ Статистические запросы

**Использование:**
```bash
psql -U postgres -d care_homes_db -f create_care_homes_db.sql
```

### 2. `care_homes_db_from_json.sql`
**Автоматически сгенерированный SQL** из JSON файла.

**Создаётся командой:**
```bash
python3 create_care_homes_db.py
```

---

## 🗄️ Структура таблицы

### Основная таблица: `care_homes`

```sql
CREATE TABLE care_homes (
    id SERIAL PRIMARY KEY,
    cqc_location_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    city VARCHAR(200),
    postcode VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    region VARCHAR(100),
    local_authority VARCHAR(200),
    telephone VARCHAR(50),
    website VARCHAR(500),
    beds_total INTEGER,
    beds_available INTEGER,
    has_availability BOOLEAN,
    availability_status VARCHAR(50),
    care_residential BOOLEAN,
    care_nursing BOOLEAN,
    care_dementia BOOLEAN,
    care_respite BOOLEAN,
    fee_residential_from DECIMAL(10, 2),
    fee_nursing_from DECIMAL(10, 2),
    fee_dementia_from DECIMAL(10, 2),
    fee_respite_from DECIMAL(10, 2),
    cqc_rating_overall VARCHAR(50),
    cqc_rating_safe VARCHAR(50),
    cqc_rating_effective VARCHAR(50),
    cqc_rating_caring VARCHAR(50),
    cqc_rating_responsive VARCHAR(50),
    cqc_rating_well_led VARCHAR(50),
    cqc_last_inspection_date DATE,
    google_rating DECIMAL(2, 1),
    review_count INTEGER,
    wheelchair_access BOOLEAN,
    ensuite_rooms BOOLEAN,
    secure_garden BOOLEAN,
    wifi_available BOOLEAN,
    parking_onsite BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Индексы

- `idx_care_homes_postcode` - для поиска по postcode
- `idx_care_homes_local_authority` - для фильтрации по LA
- `idx_care_homes_cqc_rating` - для сортировки по рейтингу
- `idx_care_homes_beds_available` - для поиска доступных мест

---

## 📊 Тестовые данные

### Статистика

- **Всего домов:** 30
- **С доступными местами:** 29 (97%)
- **С Google рейтингом:** 30 (100%)
- **С ценами:** 30 (100%)

### Распределение по рейтингам CQC:

- **Outstanding:** 1 дом (3%)
- **Good:** 21 дом (70%)
- **Requires Improvement:** 7 домов (23%)
- **Inadequate:** 1 дом (3%)

### Распределение по типам ухода:

- **Residential:** 18 домов (60%)
- **Nursing:** 12 домов (40%)
- **Dementia:** 11 домов (37%)
- **Respite:** 1 дом (3%)

### Распределение по регионам:

- **West Midlands (Birmingham):** 100% (все 30 домов)

---

## 🚀 Установка

### Вариант 1: Использование готового SQL файла

```bash
# Создать базу данных
createdb -U postgres care_homes_db

# Загрузить данные
psql -U postgres -d care_homes_db -f create_care_homes_db.sql
```

### Вариант 2: Использование Python скрипта

```bash
# Сгенерировать SQL из JSON
python3 create_care_homes_db.py

# Загрузить в БД
psql -U postgres -d care_homes_db -f care_homes_db_from_json.sql
```

### Вариант 3: Через psql интерактивно

```sql
-- Подключиться к БД
\c care_homes_db

-- Выполнить скрипт
\i create_care_homes_db.sql
```

---

## 🔍 Примеры запросов

### 1. Все дома с доступными местами

```sql
SELECT name, city, postcode, beds_available, cqc_rating_overall
FROM care_homes
WHERE has_availability = TRUE
ORDER BY beds_available DESC;
```

### 2. Дома по типу ухода и бюджету

```sql
SELECT name, city, 
       COALESCE(fee_residential_from, fee_nursing_from) as weekly_price,
       cqc_rating_overall, google_rating
FROM care_homes
WHERE care_residential = TRUE
  AND fee_residential_from <= 1000
ORDER BY google_rating DESC;
```

### 3. Топ-5 домов по рейтингу

```sql
SELECT name, city, cqc_rating_overall, google_rating, review_count
FROM care_homes
WHERE cqc_rating_overall IN ('Outstanding', 'Good')
ORDER BY google_rating DESC, review_count DESC
LIMIT 5;
```

### 4. Поиск по postcode

```sql
SELECT name, city, postcode, beds_available, 
       fee_residential_from, cqc_rating_overall
FROM care_homes
WHERE postcode LIKE 'B44%'
ORDER BY beds_available DESC;
```

### 5. Статистика по local authority

```sql
SELECT 
    local_authority,
    COUNT(*) as total_homes,
    AVG(google_rating) as avg_google_rating,
    AVG(fee_residential_from) as avg_residential_price,
    SUM(beds_available) as total_beds_available
FROM care_homes
GROUP BY local_authority
ORDER BY total_homes DESC;
```

---

## 🔧 Обновление данных

### Добавить новый дом

```sql
INSERT INTO care_homes (
    cqc_location_id, name, city, postcode, latitude, longitude,
    region, local_authority, beds_total, beds_available,
    care_residential, fee_residential_from,
    cqc_rating_overall, google_rating, review_count
) VALUES (
    '1-99999999', 'New Care Home', 'Birmingham', 'B1 1AA',
    52.4862, -1.8904, 'West Midlands', 'Birmingham',
    50, 10, TRUE, 1000,
    'Good', 4.5, 100
);
```

### Обновить доступность мест

```sql
UPDATE care_homes
SET beds_available = 5,
    has_availability = TRUE,
    availability_status = 'Available',
    updated_at = CURRENT_TIMESTAMP
WHERE cqc_location_id = '1-10016894058';
```

---

## 📋 Проверка данных

### Статистика после загрузки

```sql
SELECT 
    COUNT(*) as total_homes,
    COUNT(*) FILTER (WHERE has_availability = TRUE) as homes_with_availability,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Outstanding') as outstanding_homes,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Good') as good_homes,
    AVG(google_rating) as avg_google_rating,
    SUM(beds_available) as total_beds_available
FROM care_homes;
```

---

## ✅ Готово к использованию

База данных готова для:
- ✅ Тестирования FREE Report matching algorithm
- ✅ Development без подключения к реальной БД
- ✅ Unit тестов backend
- ✅ Демонстрации функционала

---

**Файлы:**
- `create_care_homes_db.sql` - готовый SQL скрипт (30 домов)
- `care_homes_db_from_json.sql` - автогенерированный из JSON
- `create_care_homes_db.py` - Python скрипт для генерации SQL

