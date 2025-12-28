# 🚀 План реализации Enrichment Services в Data Engine

**Дата:** 2025-01-XX  
**Цель:** Модульная реализация enrichment services в архитектуре Data Engine

---

## 📋 Очередность шагов

### Шаг 1: Базовая инфраструктура Data Engine для Enrichment
**Цель:** Создать базовую структуру для enrichment в data engine
- [ ] Создать `lib/data-engine/enrichment/base-enrichment.ts` (базовый класс)
- [ ] Создать `lib/data-engine/enrichment/types.ts` (типы)
- [ ] Создать `lib/data-engine/enrichment/cache.ts` (кэширование)
- [ ] Создать `lib/data-engine/enrichment/retry.ts` (retry логика)
- [ ] Обновить `lib/data-engine/core/index.ts` (экспорты)

**Время:** ~1 час  
**Приоритет:** 🔴 Критично

---

### Шаг 2: FSA Enrichment Service (самый простой)
**Цель:** Реализовать FSA Enrichment как первый пример
- [ ] Создать `lib/data-engine/enrichment/services/fsa.ts`
- [ ] Реализовать FSA API client
- [ ] Добавить кэширование (7 дней TTL)
- [ ] Добавить обработку ошибок
- [ ] Написать unit тесты
- [ ] Интегрировать в EnrichmentOrchestrator

**Время:** 2-3 часа  
**Приоритет:** 🟡 Высокий (самый простой, бесплатный API)

---

### Шаг 3: Financial Enrichment Service (Companies House)
**Цель:** Реализовать Financial Enrichment
- [ ] Создать `lib/data-engine/enrichment/services/financial.ts`
- [ ] Реализовать Companies House API client
- [ ] Реализовать Altman Z-score calculation
- [ ] Реализовать bankruptcy risk calculation
- [ ] Добавить кэширование
- [ ] Написать unit тесты
- [ ] Интегрировать в EnrichmentOrchestrator

**Время:** 4-6 часов  
**Приоритет:** 🔴 Критично (20 points в matching)

---

### Шаг 4: Google Places Enrichment Service
**Цель:** Реализовать Google Places Enrichment
- [ ] Создать `lib/data-engine/enrichment/services/google-places.ts`
- [ ] Реализовать Google Places API client
- [ ] Реализовать Google Places Insights API client (опционально)
- [ ] Добавить кэширование (24 часа TTL)
- [ ] Добавить обработку ошибок
- [ ] Написать unit тесты
- [ ] Интегрировать в EnrichmentOrchestrator

**Время:** 4-6 часов  
**Приоритет:** 🟡 Средний (2 points, но много секций)

---

### Шаг 5: Staff Enrichment Service (самый сложный)
**Цель:** Реализовать Staff Enrichment
- [ ] Создать `lib/data-engine/enrichment/services/staff.ts`
- [ ] Реализовать Glassdoor scraping/research
- [ ] Реализовать LinkedIn research (опционально)
- [ ] Реализовать Job Boards analysis
- [ ] Добавить кэширование
- [ ] Написать unit тесты
- [ ] Интегрировать в EnrichmentOrchestrator

**Время:** 8-12 часов  
**Приоритет:** 🔴 Критично (18 points), но самый сложный

---

### Шаг 6: Интеграция и тестирование
**Цель:** Полная интеграция всех services
- [ ] Обновить EnrichmentOrchestrator для использования data engine
- [ ] Добавить feature flags проверки
- [ ] Написать integration тесты
- [ ] Обновить документацию
- [ ] Провести end-to-end тестирование

**Время:** 2-3 часа  
**Приоритет:** 🔴 Критично

---

## 🏗️ Архитектура

```
lib/data-engine/
├── enrichment/
│   ├── base-enrichment.ts          # Базовый класс для всех enrichment services
│   ├── types.ts                    # Типы и интерфейсы
│   ├── cache.ts                    # Кэширование enrichment данных
│   ├── retry.ts                    # Retry логика (может использовать shared/utils/retry)
│   ├── services/
│   │   ├── fsa.ts                  # FSA Enrichment Service
│   │   ├── financial.ts            # Financial Enrichment Service
│   │   ├── google-places.ts        # Google Places Enrichment Service
│   │   └── staff.ts                # Staff Enrichment Service
│   └── index.ts                    # Экспорты
├── core/
│   └── ... (существующие модули)
└── utils/
    └── ... (существующие утилиты)
```

---

## 📐 Принципы дизайна

### 1. Модульность
- Каждый enrichment service = отдельный модуль
- Базовый класс для общей логики
- Легко добавлять новые services

### 2. Переиспользование
- Использовать существующие утилиты (retry, logger, cache)
- Единый интерфейс для всех services
- Общая обработка ошибок

### 3. Тестируемость
- Unit тесты для каждого service
- Mock для внешних API
- Integration тесты для orchestrator

### 4. Производительность
- Кэширование результатов
- Параллельное выполнение
- Timeout management

### 5. Надежность
- Retry механизм
- Graceful degradation
- Feature flags

---

## 🔧 Базовый интерфейс

```typescript
// lib/data-engine/enrichment/base-enrichment.ts

export abstract class BaseEnrichmentService {
  abstract serviceName: string;
  abstract enrich(home: CareHome, context?: any): Promise<EnrichmentResult>;
  
  protected cache?: EnrichmentCache;
  protected logger: Logger;
  protected retry: RetryFunction;
  
  constructor(options?: EnrichmentOptions) {
    // Инициализация
  }
  
  protected async withRetry<T>(
    fn: () => Promise<T>,
    options?: RetryOptions
  ): Promise<T> {
    // Retry логика
  }
  
  protected async withCache<T>(
    key: string,
    fn: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    // Кэширование
  }
}
```

---

## 📊 Статус реализации

| Шаг | Статус | Прогресс |
|-----|--------|----------|
| 1. Базовая инфраструктура | ⏳ В процессе | 0% |
| 2. FSA Enrichment | ⏸️ Ожидает | 0% |
| 3. Financial Enrichment | ⏸️ Ожидает | 0% |
| 4. Google Places Enrichment | ⏸️ Ожидает | 0% |
| 5. Staff Enrichment | ⏸️ Ожидает | 0% |
| 6. Интеграция и тестирование | ⏸️ Ожидает | 0% |

---

## 🎯 Критерии готовности

### Для каждого enrichment service:
- ✅ Реализован базовый функционал
- ✅ Добавлена обработка ошибок
- ✅ Добавлено кэширование
- ✅ Добавлен retry механизм
- ✅ Написаны unit тесты
- ✅ Интегрирован в orchestrator
- ✅ Работает с feature flags

### Для всей системы:
- ✅ Все services работают параллельно
- ✅ Graceful degradation при ошибках
- ✅ Логирование всех операций
- ✅ Integration тесты проходят
- ✅ Документация обновлена

---

**Начинаем с Шага 1: Базовая инфраструктура Data Engine для Enrichment**

