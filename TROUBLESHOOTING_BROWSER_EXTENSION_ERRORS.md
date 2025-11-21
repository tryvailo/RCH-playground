# Troubleshooting: Browser Extension Errors

## Ошибки, которые вы видите

```
content.js:10 Uncaught Error: Extension context invalidated.
Uncaught (in promise) Error: A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received
```

## Причина

Эти ошибки **НЕ связаны с нашим приложением**. Они возникают из-за:

1. **Расширения браузера** (например, React DevTools, Redux DevTools, или другие расширения)
2. **Обновление расширений** во время работы страницы
3. **Перезагрузка расширений** браузером

## Решение

### Вариант 1: Игнорировать ошибки (рекомендуется)
Эти ошибки не влияют на работу приложения. Вы можете безопасно игнорировать их.

### Вариант 2: Отключить расширения
1. Откройте браузер в режиме инкогнито (расширения обычно отключены)
2. Или временно отключите расширения в настройках браузера

### Вариант 3: Очистить консоль
Нажмите на иконку очистки консоли в DevTools, чтобы скрыть старые ошибки.

## Проверка работы приложения

Чтобы убедиться, что генерация отчета работает:

1. **Откройте консоль браузера** (F12)
2. **Фильтруйте ошибки** - используйте фильтр в консоли, чтобы скрыть ошибки расширений
3. **Попробуйте сгенерировать отчет** - если отчет генерируется успешно, значит все работает

## Как отличить ошибки приложения от ошибок расширений

**Ошибки приложения:**
- Содержат пути к нашим файлам: `ProfessionalReportViewer.tsx`, `useProfessionalReport.ts`, `main.py`
- Связаны с API запросами: `POST http://localhost:8000/api/professional-report`
- Показывают ошибки валидации или сервера

**Ошибки расширений:**
- Содержат `content.js`, `background.js`, `extension`
- Показывают `Extension context invalidated`
- Показывают `message channel closed`

## Если отчет не генерируется

Если отчет действительно не генерируется (не из-за ошибок расширений), проверьте:

1. **Бэкенд запущен**: `http://localhost:8000` должен отвечать
2. **Фронтенд запущен**: `http://localhost:3000` должен открываться
3. **Консоль браузера**: Ищите ошибки с путями к нашим файлам
4. **Network tab**: Проверьте запросы к `/api/professional-report` и их ответы

## Статус исправлений

Все исправления для ошибки `'>' not supported between instances of 'NoneType' and 'int'` были применены:

✅ **professional_matching_service.py** - безопасная конвертация category_scores и weights
✅ **main.py** - безопасная конвертация point_allocations и normalized
✅ **funding_optimization_service.py** - безопасная конвертация финансовых значений
✅ **negotiation_strategy_service.py** - безопасная конвертация цен
✅ **red_flags_service.py** - безопасная конвертация revenues, margins, prices
✅ **comparative_analysis_service.py** - безопасная конвертация prices и match scores
✅ **financial_enrichment_service.py** - безопасная конвертация revenues, margins, working_capitals
✅ **staff_enrichment_service.py** - безопасная конвертация active_listings, staff_count
✅ **google_places_enrichment_service.py** - безопасная конвертация average_sentiment
✅ **fsa_enrichment_service.py** - исправлена избыточная проверка None

Все эти исправления должны предотвратить ошибки типа `'>' not supported between instances of 'NoneType' and 'int'`.

