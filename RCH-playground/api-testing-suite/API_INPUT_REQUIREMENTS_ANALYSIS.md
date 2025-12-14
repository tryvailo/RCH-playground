# Анализ требований к входным данным для всех API

## Обзор

Этот документ описывает требования каждого источника данных к входным параметрам для анализа neighbourhood.

---

## 1. OS Places API

### Требования к входным данным
- **Основной вход**: `postcode` (UK postcode, например "CV34 5EH")
- **Альтернативный вход**: Нет (только postcode)
- **Координаты**: Не требуются на входе, но предоставляются на выходе

### Методы и их входные данные

#### `get_address_by_postcode(postcode: str)`
- **Вход**: `postcode` (строка)
- **Выход**: 
  - Список адресов с координатами
  - Centroid координаты (lat/lon)
  - UPRN для каждого адреса
  - Классификация адресов

#### `get_coordinates(postcode: str)`
- **Вход**: `postcode` (строка)
- **Выход**: `{latitude: float, longitude: float}`

### Особенности
- ✅ Работает только с postcode
- ✅ Нормализует postcode (убирает пробелы, приводит к верхнему регистру)
- ✅ Может предоставить координаты для других API
- ❌ Не может работать напрямую с координатами

### Пример использования
```python
loader = OSPlacesLoader()
result = await loader.get_address_by_postcode("CV34 5EH")
# Возвращает адреса + координаты
```

---

## 2. ONS (Office for National Statistics) API

### Требования к входным данным
- **Основной вход**: `postcode` (UK postcode)
- **Альтернативный вход**: `local_authority` (для некоторых методов)
- **Координаты**: Не требуются на входе, но могут предоставляться на выходе (через geography)

### Методы и их входные данные

#### `postcode_to_lsoa(postcode: str)`
- **Вход**: `postcode` (строка)
- **Выход**: 
  - LSOA code
  - MSOA code
  - Local Authority
  - Region
  - Координаты (иногда, через geography)

#### `get_full_area_profile(postcode: str)`
- **Вход**: `postcode` (строка)
- **Выход**: 
  - Geography (LSOA, MSOA, Local Authority, координаты если доступны)
  - Wellbeing data
  - Economic profile
  - Demographics

#### `get_wellbeing_data(lsoa_code: str, local_authority: str)`
- **Вход**: `lsoa_code` или `local_authority` (получается из postcode)
- **Выход**: Wellbeing indicators

#### `get_economic_profile(postcode: str, local_authority: str)`
- **Вход**: `postcode` или `local_authority`
- **Выход**: Economic indicators

#### `get_demographics(postcode: str, local_authority: str)`
- **Вход**: `postcode` или `local_authority`
- **Выход**: Demographic data

### Особенности
- ✅ Работает с postcode
- ✅ Может работать с local_authority (для некоторых методов)
- ✅ Может предоставить координаты через geography (не всегда)
- ❌ Не может работать напрямую только с координатами

### Пример использования
```python
loader = ONSLoader()
profile = await loader.get_full_area_profile("CV34 5EH")
# Возвращает полный профиль, включая координаты если доступны
```

---

## 3. OSM (OpenStreetMap) API

### Требования к входным данным
- **Основной вход**: `coordinates` (latitude, longitude) - **ОБЯЗАТЕЛЬНО**
- **Альтернативный вход**: Нет
- **Postcode**: Не используется напрямую

### Методы и их входные данные

#### `calculate_walk_score(lat: float, lon: float)`
- **Вход**: `lat` (float), `lon` (float) - **ОБЯЗАТЕЛЬНО**
- **Выход**: Walk Score (0-100), category breakdown, care home relevance

#### `get_nearby_amenities(lat: float, lon: float, radius_m: int)`
- **Вход**: `lat` (float), `lon` (float), `radius_m` (int, default 1600)
- **Выход**: Categorized amenities with distances

#### `get_infrastructure_report(lat: float, lon: float)`
- **Вход**: `lat` (float), `lon` (float) - **ОБЯЗАТЕЛЬНО**
- **Выход**: Public transport, pedestrian safety, accessibility

### Особенности
- ❌ **НЕ работает с postcode** - требует координаты
- ✅ Работает только с координатами (lat/lon)
- ✅ Использует Overpass API для запросов по координатам
- ⚠️ Если координаты не доступны, использует sample данные (fallback)

### Пример использования
```python
loader = OSMLoader()
walk_score = await loader.calculate_walk_score(52.287611, -1.566073)
# Требует координаты, не может работать с postcode
```

---

## 4. NHSBSA API

### Требования к входным данным
- **Основной вход**: `postcode` (UK postcode)
- **Внутреннее использование**: `coordinates` (получаются из postcode)
- **Альтернативный вход**: Нет прямого входа по координатам

### Методы и их входные данные

#### `get_area_health_profile(postcode: str, radius_km: float)`
- **Вход**: `postcode` (строка), `radius_km` (float, default 5.0)
- **Внутренняя логика**:
  1. Получает координаты из postcode через `_get_postcode_coordinates()`
  2. Использует координаты для proximity matching GP practices
- **Выход**: Health profile, prescribing patterns, care home considerations

#### `get_gp_practices(postcode: str, limit: int)`
- **Вход**: `postcode` (строка)
- **Внутренняя логика**: Получает координаты из postcode для поиска практик
- **Выход**: List of GP practices

### Особенности
- ✅ Принимает postcode на входе
- ⚠️ **Внутренне требует координаты** для proximity matching
- ⚠️ Если координаты не могут быть получены из postcode, возвращает ошибку
- ❌ Не может работать напрямую только с координатами (требует postcode для получения практик)

### Пример использования
```python
loader = NHSBSALoader()
profile = await loader.get_area_health_profile("CV34 5EH", radius_km=5.0)
# Принимает postcode, но внутренне использует координаты
```

---

## Сводная таблица требований

| API | Основной вход | Альтернативный вход | Требует координаты | Предоставляет координаты |
|-----|---------------|---------------------|-------------------|-------------------------|
| **OS Places** | ✅ Postcode | ❌ Нет | ❌ Нет | ✅ Да (centroid) |
| **ONS** | ✅ Postcode | ⚠️ Local Authority (некоторые методы) | ❌ Нет | ⚠️ Иногда (через geography) |
| **OSM** | ❌ Нет | ❌ Нет | ✅ **Да (обязательно)** | ❌ Нет |
| **NHSBSA** | ✅ Postcode | ❌ Нет | ⚠️ **Да (внутренне)** | ❌ Нет |

---

## Зависимости между API

### Цепочка получения координат

```
Postcode (вход)
    ↓
OS Places или ONS (получают координаты из postcode)
    ↓
Координаты (lat/lon)
    ↓
OSM и NHSBSA (используют координаты)
```

### Приоритет получения координат

1. **ONS** (если включен) - может предоставить координаты через geography
2. **OS Places** (всегда пытается, если нужны координаты для OSM/NHSBSA)
3. **Ошибка** (если координаты не могут быть получены)

---

## Рекомендации для UI

### Вариант 1: Только Postcode (текущая реализация)
- ✅ Простой для пользователя
- ✅ Работает для всех API
- ⚠️ Требует автоматическое получение координат

### Вариант 2: Postcode + Координаты (опционально)
- ✅ Позволяет пропустить resolution координат
- ✅ Более точный для OSM (может указать точную локацию, а не centroid postcode)
- ⚠️ Требует дополнительное поле ввода

### Вариант 3: Только Координаты
- ❌ Не работает для OS Places и ONS (они требуют postcode)
- ✅ Работает для OSM
- ⚠️ NHSBSA все равно требует postcode для получения GP practices

---

## Выводы

1. **OS Places** и **ONS** требуют **postcode** на входе
2. **OSM** требует **координаты** (lat/lon) на входе
3. **NHSBSA** принимает **postcode**, но **внутренне требует координаты** для proximity matching
4. **Текущая реализация** (только postcode) правильная, так как:
   - OS Places и ONS могут получить координаты из postcode
   - Координаты автоматически передаются в OSM и NHSBSA
   - Пользователю не нужно знать координаты

### Оптимизация

Для более точного анализа OSM можно добавить опциональный ввод координат:
- Если координаты предоставлены → использовать их напрямую для OSM
- Если нет → использовать координаты из OS Places/ONS (centroid postcode)

Это особенно полезно для больших postcode areas, где centroid может быть далеко от реальной локации care home.

