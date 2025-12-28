# Data Engine

Модульная архитектура для обработки данных о домах престарелых.

## Структура

```
lib/data-engine/
├── core/              # Основные модули Data Engine
│   ├── data-loader.ts      # Универсальный загрузчик данных
│   ├── data-enricher.ts    # Обогащение данных
│   ├── data-matcher.ts     # Алгоритмы матчинга
│   ├── data-validator.ts   # Валидация данных
│   └── data-cache.ts       # Кэширование
├── sources/           # Источники данных
│   ├── database.ts         # PostgreSQL
│   ├── csv-loader.ts       # CSV файлы
│   └── postcode-resolver.ts # Разрешение почтовых индексов
└── utils/             # Утилиты
    ├── geo.ts              # Географические расчеты
    └── price-extractor.ts  # Извлечение цен
```

## Использование

### DataLoader

```typescript
import { DataLoader } from '@/lib/data-engine/core';

const loader = new DataLoader();

// Загрузка домов
const homes = await loader.loadCareHomes({
  careType: 'residential',
  localAuthority: 'Westminster',
  userLat: 51.5074,
  userLon: -0.1278,
  maxDistanceKm: 30,
  limit: 50,
});

// Разрешение почтового индекса
const postcodeInfo = await loader.resolvePostcode('SW1A 1AA');
```

### DataValidator

```typescript
import { DataValidator } from '@/lib/data-engine/core';

const validator = new DataValidator();

// Валидация анкеты
validator.validateQuestionnaire({
  postcode: 'SW1A 1AA',
  budget: 1200,
  care_type: 'residential',
});

// Валидация домов
const result = validator.validateHomes(homes);
if (!result.isValid) {
  console.error('Validation errors:', result.errors);
}
```

### DataEnricher

```typescript
import { DataEnricher } from '@/lib/data-engine/core';

const enricher = new DataEnricher();

// Обогащение одного дома
const enriched = await enricher.enrichHome(home, {
  enableFinancial: true,
  enableStaff: true,
  enableFSA: true,
  enableGooglePlaces: true,
});

// Пакетное обогащение
const enrichedHomes = await enricher.enrichHomes(homes, config, (progress, message) => {
  console.log(`${progress}% - ${message}`);
});
```

### DataMatcher

```typescript
import { DataMatcher } from '@/lib/data-engine/core';

const matcher = new DataMatcher();

// Матчинг домов
const scored = await matcher.matchHomes(homes, {
  budget: 1200,
  careType: 'residential',
  userLat: 51.5074,
  userLon: -0.1278,
  maxDistanceKm: 30,
});
```

### DataCache

```typescript
import { DataCache } from '@/lib/data-engine/core';

const cache = new DataCache(3600000); // 1 hour TTL

// Сохранение
cache.set('key', data, 3600000);

// Получение
const cached = cache.get<MyType>('key');

// Генерация ключа
const key = cache.generateKey('prefix', { param1: 'value1', param2: 'value2' });
```

## Утилиты

### Географические расчеты

```typescript
import { calculateDistanceKm, validateCoordinates } from '@/lib/data-engine/utils';

const distance = calculateDistanceKm(51.5074, -0.1278, 51.5155, -0.0922);
const isValid = validateCoordinates(51.5074, -0.1278);
```

### Извлечение цен

```typescript
import { extractWeeklyPrice, extractPriceRange } from '@/lib/data-engine/utils';

const price = extractWeeklyPrice(homeData, 'residential');
const range = extractPriceRange(homeData, 'residential');
```



