# Fair Cost Gap Module

**САМЫЙ ЭМОЦИОНАЛЬНЫЙ И КОНВЕРСИОННЫЙ БЛОК** бесплатного отчёта.

Показывает переплату семьи над государственной "справедливой ценой" (MSIF 2025–2026).

---

## 📋 Описание

Fair Cost Gap — обязательный блок, который демонстрирует:
- Сколько семья переплачивает в неделю/год/5 лет
- Процент переплаты над справедливой ценой
- Потенциальную экономию через государственное финансирование

### Формула расчёта

1. `msif_lower` = значение из MSIF XLS по `local_authority` + `care_type`
2. `market_price` = средняя рыночная цена (из домов или budget)
3. `gap_week` = `market_price` - `msif_lower`
4. `gap_year` = `gap_week` * 52
5. `gap_5year` = `gap_year` * 5
6. `gap_percent` = (`gap_week` / `msif_lower`) * 100

### Пример

**Camden, nursing:**
- MSIF lower: £1,048/нед
- Market price: £1,912/нед
- Gap: £864/нед = £44,928/год = £224,640 за 5 лет

---

## 🏗️ Структура модуля

```
fair-cost-gap/
├── components/
│   ├── FairCostGapBlock.tsx    # Главный компонент (красный блок)
│   └── AnimatedCounter.tsx     # Анимированный счётчик
├── hooks/
│   └── useFairCostGap.ts       # Хук для расчёта gap
├── stores/
│   └── msifStore.ts            # Zustand store для кэширования MSIF
├── msifLoader.ts               # Загрузка и парсинг MSIF XLS
├── types.ts                    # TypeScript типы
├── index.ts                    # Public API
├── useFairCostGap.test.ts      # Тесты
└── README.md                   # Документация
```

---

## 🚀 Использование

### Базовое использование

```tsx
import { FairCostGapBlock } from '@/features/fair-cost-gap';

function MyComponent() {
  return (
    <FairCostGapBlock
      marketPrice={1912}
      localAuthority="Camden"
      careType="nursing"
      onUpgradeClick={() => {
        // Обработка клика на CTA
      }}
    />
  );
}
```

### Использование хука

```tsx
import { useFairCostGap } from '@/features/fair-cost-gap';

function MyComponent() {
  const {
    msifLower,
    gapWeekly,
    gapAnnual,
    gapFiveYear,
    gapPercent,
    isLoading,
    error,
  } = useFairCostGap({
    marketPrice: 1912,
    localAuthority: 'Camden',
    careType: 'nursing',
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <p>Weekly gap: £{gapWeekly}</p>
      <p>Annual gap: £{gapAnnual}</p>
    </div>
  );
}
```

### Предзагрузка MSIF данных

```tsx
import { preloadMSIFData } from '@/features/fair-cost-gap';

// Предзагрузить данные при старте приложения
useEffect(() => {
  preloadMSIFData();
}, []);
```

---

## 📦 API

### `FairCostGapBlock`

Главный компонент для отображения Fair Cost Gap.

**Props:**
- `marketPrice: number` - Средняя рыночная цена (GBP/week)
- `localAuthority: string` - Название local authority (например, "Camden", "Birmingham")
- `careType: CareType` - Тип ухода: `'residential'` | `'nursing'` | `'residential_dementia'` | `'nursing_dementia'`
- `className?: string` - Дополнительные CSS классы
- `onUpgradeClick?: () => void` - Callback при клике на CTA кнопку

### `useFairCostGap`

Хук для расчёта Fair Cost Gap.

**Parameters:**
```typescript
{
  marketPrice: number;
  localAuthority: string;
  careType: CareType;
  enabled?: boolean; // default: true
}
```

**Returns:**
```typescript
{
  msifLower: number;
  gapWeekly: number;
  gapAnnual: number;
  gapFiveYear: number;
  gapPercent: number;
  isLoading: boolean;
  error: string | null;
}
```

### `getFairCostLower`

Получить MSIF lower bound для local authority и care type.

```typescript
const msifLower = await getFairCostLower('Camden', 'nursing');
// Returns: 1048 (GBP/week) or null if not found
```

---

## 🎨 Дизайн

### Цвета

- **Красный фон:** `#EF4444` → `#DC2626` (градиент)
- **Белый текст:** Контрастный на красном фоне
- **Зелёный CTA:** `#10B981` (кнопка "Professional Report")

### Анимации

- **AnimatedCounter:** Плавная анимация счётчика (2-3 секунды)
- **Easing:** Cubic ease-out для естественного движения
- **Responsive:** Адаптивные размеры шрифтов для mobile/desktop

### Mobile-first

- Адаптивная сетка
- Оптимизированные размеры шрифтов
- Touch-friendly кнопки

---

## 🧪 Тесты

Запуск тестов:

```bash
npm test useFairCostGap.test.ts
```

Тесты проверяют:
- ✅ Расчёт для Camden nursing (£864/week gap)
- ✅ Расчёт для Birmingham residential (£300/week gap)
- ✅ Расчёт для London dementia (£380/week gap)
- ✅ Обработка ошибок (MSIF data not found)
- ✅ Обработка случая когда market price < MSIF lower

---

## 🔧 Технические детали

### MSIF Loader

- Автоматически скачивает MSIF 2025-2026 XLS файл
- Fallback на 2024-2025 если новый недоступен
- Парсит XLS используя библиотеку `xlsx`
- Кэширует данные в:
  - **localStorage** (7 дней TTL)
  - **Zustand store** (в памяти)

### Кэширование

- **localStorage:** Персистентное кэширование между сессиями
- **Zustand store:** Быстрый доступ в памяти
- **TTL:** 7 дней (можно настроить)

### Fallback данные

Если MSIF файл недоступен или парсинг не удался, используются fallback данные для основных LA:
- Camden
- Birmingham
- Westminster
- Manchester
- London

---

## 📝 Интеграция

### В FreeReportViewer

Модуль автоматически интегрирован в `ReportRenderer`:

```tsx
<FairCostGapBlock
  marketPrice={avgMarketPrice}
  localAuthority={questionnaire.city || 'Birmingham'}
  careType={mapCareType(questionnaire.care_type)}
  onUpgradeClick={() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
  }}
/>
```

### В PDF экспорт

Fair Cost Gap отображается на отдельной странице PDF (Page 5) с красным фоном и большими цифрами.

---

## 🎯 Конверсионные элементы

1. **Огромные цифры** - визуальный шок от суммы переплаты
2. **Анимация** - привлекает внимание
3. **Government coverage** - показывает возможность экономии
4. **CTA кнопка** - прямой путь к Professional Report

---

## 🔄 Обновление MSIF данных

MSIF данные обновляются автоматически при:
- Первой загрузке модуля
- Истечении кэша (7 дней)
- Вызове `preloadMSIFData()`

Для принудительного обновления:

```typescript
import { useMSIFStore } from '@/features/fair-cost-gap';

const store = useMSIFStore.getState();
store.clearCache();
// Данные будут перезагружены при следующем запросе
```

---

## 📚 Примеры

### Пример 1: Простое использование

```tsx
<FairCostGapBlock
  marketPrice={1200}
  localAuthority="Birmingham"
  careType="residential"
/>
```

### Пример 2: С обработкой клика

```tsx
<FairCostGapBlock
  marketPrice={1912}
  localAuthority="Camden"
  careType="nursing"
  onUpgradeClick={() => {
    router.push('/professional-report');
  }}
/>
```

### Пример 3: Кастомный расчёт

```tsx
const { gapWeekly, gapAnnual } = useFairCostGap({
  marketPrice: 1500,
  localAuthority: 'Manchester',
  careType: 'nursing',
});

// Использовать данные для кастомного UI
```

---

## ✅ Production Ready

- ✅ TypeScript типы
- ✅ Error handling
- ✅ Loading states
- ✅ Кэширование
- ✅ Fallback данные
- ✅ Тесты
- ✅ Responsive design
- ✅ Accessibility
- ✅ Performance optimized

---

**Это главный конверсионный триггер — пользователь должен ахнуть от цифр!** 🎯

