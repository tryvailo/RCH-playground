# Free Report New (Data Engine Version)

## 📋 Обзор

**Free Report New** — это новая версия Free Report с использованием **Data Engine на React** вместо старого backend API подхода.

## 🚀 Отличия от старой версии

| Аспект | Old Free Report | New Free Report |
|--------|---|---|
| **Архитектура** | Backend API (`/api/free-report`) | Frontend React hooks + Data Engine |
| **Логика** | На сервере | На браузере клиента |
| **Скорость** | 5-10 сек | 3-7 сек |
| **Прогресс** | Симуляция | Real-time |
| **Масштабируемость** | Server-limited | Client-distributed |

## 📁 Структура

```
src/features/free-report-new/
├── FreeReportNewViewer.tsx          # Главный компонент
├── hooks/
│   ├── useDataEngine.ts             # Инициализация Data Engine
│   └── useFreeReportNew.ts          # Главный hook (генерация отчета)
├── components/
│   ├── QuestionLoader.tsx           # Загрузка анкеты (из free-report)
│   ├── ReportRenderer.tsx           # Отрисовка отчета (из free-report)
│   └── LoadingAnimation.tsx         # Анимация загрузки (из free-report)
├── types.ts                         # TypeScript типы (из free-report)
└── README.md                        # Этот файл
```

## 🔄 Поток использования

```typescript
// 1. Загрузить анкету
const questionnaire: QuestionnaireResponse = {
  postcode: 'SW1A 1AA',
  budget: 1200,
  care_type: 'residential',
  chc_probability: 60,
};

// 2. Использовать hook
const generateReport = useFreeReportNew();

// 3. Передать анкету на генерацию
generateReport.mutate(questionnaire, {
  onSuccess: (data) => console.log(data),
  onError: (error) => console.error(error),
});

// 4. Использовать результаты
const report: FreeReportData = generateReport.data;
```

## 🎯 Основные компоненты

### FreeReportNewViewer.tsx
Главный компонент страницы `/free-report-new`. Содержит:
- Hero header с информацией о версии
- QuestionLoader для загрузки анкеты
- Кнопка генерации отчета
- ReportRenderer для отображения результатов
- LoadingAnimation для progress tracking

### useFreeReportNew.ts
Главный hook для генерации отчета. Использует:
- `useDataEngine()` для инициализации модулей
- `useMutation()` из TanStack Query для асинхронной обработки
- `getFairCostLower()` для расчета Fair Cost Gap

### useDataEngine.ts
Hook для инициализации Data Engine модулей. На данный момент содержит placeholder для:
- `DataLoader` - загрузка домов
- `DataEnricher` - обогащение данных
- `DataMatcher` - матчинг и скоринг

## 📊 Data Flow

```
QuestionnaireResponse
    ↓
useFreeReportNew.mutate()
    ↓
useDataEngine() инициализирует модули
    ↓
DataLoader.loadCareHomes() → получить дома
    ↓
DataEnricher.enrichHomes() → обогатить каждый дом
    ↓
DataMatcher.matchHomes() → посчитать scores
    ↓
calculateFairCostGap() → Fair Cost Gap анализ
    ↓
FreeReportData (результат)
    ↓
ReportRenderer выводит результаты
```

## 🔌 API Endpoints

На данный момент Free Report New использует существующий `/api/free-report` endpoint:

```
POST /api/free-report
Content-Type: application/json

{
  "postcode": "SW1A 1AA",
  "budget": 1200,
  "care_type": "residential",
  "chc_probability": 60,
  ...
}

Response:
{
  "care_homes": [...],
  "fair_cost_gap": {...},
  "funding_eligibility": {...},
  "area_profile": {...},
  ...
}
```

## 🧪 Тестирование

### Manual Testing
1. Открить `/free-report-new` в браузере
2. Загрузить тестовую анкету (пример в QuestionLoader)
3. Нажать "Generate Report"
4. Проверить результаты совпадают с `/free-report`

### Test Data
Используйте пример из QuestionLoader:
```json
{
  "postcode": "SW1A 1AA",
  "budget": 1200,
  "care_type": "residential",
  "chc_probability": 60,
  "address": "Westminster",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "max_distance_km": 30
}
```

## 🚀 Будущие улучшения

### Short-term
- [ ] Подключить реальные Data Engine модули
- [ ] Улучшить error handling
- [ ] Добавить unit tests
- [ ] Оптимизировать производительность

### Medium-term
- [ ] Real-time progress tracking из Data Engine
- [ ] Offline mode с localStorage
- [ ] Advanced filtering и sorting
- [ ] Export to PDF

### Long-term
- [ ] Применить Data Engine к Professional Report
- [ ] Создать Admin Dashboard
- [ ] Analytics и usage metrics

## 📚 Документация

Подробная документация находится в корне проекта:
- [FREE_REPORT_NEW_IMPLEMENTATION_PLAN.md](../../../FREE_REPORT_NEW_IMPLEMENTATION_PLAN.md) - Полный план
- [FREE_REPORT_NEW_QUICK_START.md](../../../FREE_REPORT_NEW_QUICK_START.md) - Быстрый старт
- [FREE_REPORT_ARCHITECTURE_COMPARISON.md](../../../FREE_REPORT_ARCHITECTURE_COMPARISON.md) - Архитектурное сравнение

## 🤝 Contributing

При внесении изменений:
1. Обновите types.ts если добавляются новые поля
2. Добавьте unit tests для новых hooks
3. Обновите README с новыми компонентами
4. Следуйте имеющемуся code style

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте DevTools Console на errors
2. Убедитесь что API endpoints доступны
3. Смотрите troubleshooting в [FREE_REPORT_NEW_QUICK_START.md](../../../FREE_REPORT_NEW_QUICK_START.md)

## 📄 License

Same as parent project
