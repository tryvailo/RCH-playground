# Free Report Viewer Feature

Генератор бесплатных отчетов для RightCareHome на основе questionnaire данных.

## Структура

```
src/features/free-report/
├── FreeReportViewer.tsx    # Главный компонент
├── types.ts                 # TypeScript типы
├── hooks/
│   └── useFreeReport.ts    # TanStack Query хук для API
├── components/
│   ├── QuestionLoader.tsx  # Компонент загрузки questionnaire
│   └── ReportRenderer.tsx  # Компонент отображения отчета
└── README.md
```

## Основные компоненты

### FreeReportViewer
Главный компонент с хедером и сайдбаром:
- Загрузка questionnaire (дефолтные файлы или drag & drop)
- Генерация отчета через API
- Отображение результатов

### QuestionLoader
Компонент для загрузки questionnaire:
- Выбор из sample файлов (`public/sample_questionnaires/`)
- Drag & drop для загрузки своего JSON
- Валидация данных

### ReportRenderer
Компонент отображения отчета:
- **Fair Cost Gap** - обязательный эмоциональный блок с анализом переплаты
- Топ-3 рекомендованных дома престарелых
- Детальная информация по каждому дому

## Fair Cost Gap

**ОБЯЗАТЕЛЬНЫЙ** и самый эмоциональный блок отчета.

### Формула:
```
gap_week = market_price - MSIF_lower_bound
gap_year = gap_week * 52
gap_5year = gap_year * 5
```

### Пример:
- Camden nursing_dementia
- MSIF: £1,048/week
- Market: £1,912/week
- Gap: £864/week = £44,928/год = £224,640 за 5 лет

## API

### POST /api/free-report

**Request:**
```json
{
  "postcode": "SW1A 1AA",
  "budget": 1200.0,
  "care_type": "residential",
  "chc_probability": 35.5
}
```

**Response:**
```json
{
  "questionnaire": {...},
  "care_homes": [...],
  "fair_cost_gap": {
    "gap_week": 864,
    "gap_year": 44928,
    "gap_5year": 224640,
    "market_price": 1912,
    "msif_lower_bound": 1048,
    "gap_text": "Переплата £44,928 в год = £224,640 за 5 лет",
    ...
  },
  "generated_at": "...",
  "report_id": "..."
}
```

## Mock Data

Если backend недоступен, используется mock-данные с 3 домами и Fair Cost Gap анализом.

## Цветовая схема

- **Тёмно-синий**: `#1E2A44` - основной цвет хедера
- **Зелёный**: `#10B981` - успешные действия и положительные значения
- **Красный**: `#EF4444` - Fair Cost Gap (эмоциональный акцент)

## Использование

1. Перейдите на `/free-report`
2. Выберите sample questionnaire или загрузите свой JSON
3. Нажмите "Сгенерировать отчёт"
4. Просмотрите результаты с Fair Cost Gap анализом

## Логика работы хука useFreeReport

### Последовательность операций:

1. **Загрузка JSON** → POST `/api/free-report` с questionnaire данными
2. **MSIF API** → GET `/api/msif/fair-cost/{local_authority}/{care_type}` для получения MSIF lower bound
3. **Расчёт Fair Cost Gap**:
   - `gap_week = market_price - msif_lower_bound`
   - `gap_year = gap_week * 52`
   - `gap_5year = gap_year * 5`
   - `percent = (gap_week / msif_lower_bound) * 100`
4. **Matching**: 3 дома (Safe Bet, Best Value, Premium) из backend или mock
5. **Fallback**: Если backend недоступен → используется mock с 3 домами

### Кэширование

- TanStack Query кэширует результаты на 1 час (`gcTime: 1000 * 60 * 60`)
- MSIF данные кэшируются отдельно на 24 часа
- Mutation key: `['free-report']`

### Структура данных

Хук возвращает `FreeReportData`:
```typescript
{
  homes: CareHomeData[]; // 3 дома
  fairCostGap: {
    weekly: number;
    annual: number;
    fiveYear: number;
    percent: number;
  };
  chcTeaserPercent: number;
}
```

## Установка зависимостей

```bash
cd api-testing-suite/frontend
npm install
```

Новые зависимости:
- `@tanstack/react-query` - для работы с API

## Запуск

```bash
npm run dev
```

Затем перейдите на http://localhost:3000/free-report

## Тестирование

Для запуска тестов сначала установите зависимости для тестирования:

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Затем запустите:

```bash
npm run test
```

Тесты используют Vitest для unit-тестирования компонентов. Включают тесты на все 3 дефолтных JSON файла.

## Как добавить новый sample JSON

### Шаг 1: Создайте JSON файл

Создайте новый файл в `public/sample_questionnaires/` с именем `questionnaire_N.json` (где N - следующий номер):

```json
{
  "postcode": "POSTCODE_HERE",
  "budget": 1200.0,
  "care_type": "residential",
  "chc_probability": 35.5,
  "address": "Address",
  "city": "City",
  "preferences": {
    "garden": true,
    "activities": true
  }
}
```

### Шаг 2: Обновите QuestionLoader.tsx

Добавьте новый файл в массив `SAMPLE_FILES`:

```typescript
// src/features/free-report/components/QuestionLoader.tsx
const SAMPLE_FILES = [
  'questionnaire_1.json',
  'questionnaire_2.json',
  'questionnaire_3.json',
  'questionnaire_4.json', // ← Добавьте здесь
];
```

### Шаг 3: Обновите тесты (опционально)

Добавьте тест для нового файла в `FreeReportViewer.test.tsx`:

```typescript
it('loads questionnaire_4.json correctly', async () => {
  (global.fetch as any).mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      postcode: 'YOUR_POSTCODE',
      budget: YOUR_BUDGET,
      care_type: 'YOUR_CARE_TYPE',
      chc_probability: YOUR_CHC_PROBABILITY,
    }),
  });

  const user = userEvent.setup();
  renderWithQueryClient(<FreeReportViewer />);

  const button = await screen.findByText('questionnaire_4.json');
  await user.click(button);

  await waitFor(() => {
    expect(screen.getByText(/YOUR_POSTCODE/i)).toBeInTheDocument();
  });
});
```

### Шаг 4: Проверьте валидацию

Убедитесь, что JSON файл содержит обязательное поле `postcode`. Остальные поля опциональны:

- `postcode` (обязательно) - UK postcode
- `budget` (опционально) - Weekly budget in GBP
- `care_type` (опционально) - 'residential' | 'nursing' | 'dementia' | 'respite'
- `chc_probability` (опционально) - CHC probability percentage (0-100)
- `address` (опционально) - Address string
- `city` (опционально) - City name
- `latitude` (опционально) - Latitude coordinate
- `longitude` (опционально) - Longitude coordinate
- `preferences` (опционально) - Object with any preferences

### Примеры

**questionnaire_4.json** - Manchester, nursing care:
```json
{
  "postcode": "M1 2AB",
  "budget": 1400.0,
  "care_type": "nursing",
  "chc_probability": 45.0,
  "address": "City Centre",
  "city": "Manchester"
}
```

**questionnaire_5.json** - Birmingham, dementia care:
```json
{
  "postcode": "B2 4QA",
  "budget": 1100.0,
  "care_type": "dementia",
  "chc_probability": 30.0,
  "address": "City Centre",
  "city": "Birmingham",
  "preferences": {
    "secure_garden": true,
    "specialist_dementia_care": true
  }
}
```

После добавления файла он автоматически появится в списке sample questionnaires на странице `/free-report`.

## Особенности дизайна

### WOW эффект
- Hero header с градиентным фоном и анимированными элементами
- Красивый лоадер с прогресс-баром (~30 секунд)
- Плавные анимации и переходы
- Премиум цветовая схема

### Mobile Responsive
- Адаптивная сетка для всех секций
- Мобильная навигация
- Оптимизированные размеры шрифтов
- Touch-friendly интерфейс

### Error Handling
- Graceful fallback на mock данные при ошибках API
- Понятные сообщения об ошибках
- Кнопка "Попробовать снова" при ошибках
- Валидация JSON файлов

## Производительность

- Кэширование результатов через TanStack Query
- Ленивая загрузка компонентов
- Оптимизированные изображения
- Минимальные ре-рендеры

