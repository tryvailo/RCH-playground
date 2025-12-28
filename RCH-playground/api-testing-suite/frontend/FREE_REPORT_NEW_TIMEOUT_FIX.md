# Free Report New - Исправление Timeout Проблемы

**Дата:** 2025-01-XX  
**Проблема:** Timeout при генерации отчета через веб-интерфейс  
**Статус:** ✅ Исправлено

---

## 🔍 Анализ проблемы

### Ошибка
```
AxiosError {message: 'timeout of 180000ms exceeded', name: 'AxiosError', code: 'ECONNABORTED'}
```

### Причина

**Несоответствие портов в конфигурации прокси:**

1. **Frontend (Vite):** Порт 3001
2. **Backend (Python FastAPI):** Порт 8001
3. **Прокси в vite.config.ts:** Указывал на порт 8000 ❌

**Результат:**
- Запросы из фронтенда шли через прокси на `http://localhost:8000`
- Backend работает на порту 8001
- Запросы не доходили до backend → timeout

---

## ✅ Исправление

### Изменения в `vite.config.ts`

**Было:**
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // ❌ Неправильный порт
    changeOrigin: true,
    timeout: 300000,
    proxyTimeout: 300000,
  },
  '/health': {
    target: 'http://localhost:8000',  // ❌ Неправильный порт
    changeOrigin: true,
  },
  '/ws': {
    target: 'http://localhost:8000',  // ❌ Неправильный порт
    ws: true,
    changeOrigin: true,
    secure: false,
  },
}
```

**Стало:**
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',  // ✅ Правильный порт
    changeOrigin: true,
    timeout: 300000,
    proxyTimeout: 300000,
  },
  '/health': {
    target: 'http://localhost:8001',  // ✅ Правильный порт
    changeOrigin: true,
  },
  '/ws': {
    target: 'http://localhost:8001',  // ✅ Правильный порт
    ws: true,
    changeOrigin: true,
    secure: false,
  },
}
```

---

## 🔄 Процесс запроса (после исправления)

```
Frontend (http://localhost:3001)
  ↓
POST /api/free-report
  ↓
Vite Proxy (vite.config.ts)
  ↓
Backend (http://localhost:8001/api/free-report) ✅
  ↓
SQLite Database (care_homes.db)
  ↓
Response
  ↓
Frontend
```

---

## ✅ Проверка исправления

### Тест 1: Прямой запрос к backend
```bash
curl -X POST http://localhost:8001/api/free-report \
  -H "Content-Type: application/json" \
  -d '{"postcode":"B11 1AA","budget":1200,"care_type":"residential"}'
```
**Результат:** ✅ Успешно

### Тест 2: Запрос через прокси
```bash
curl -X POST http://localhost:3001/api/free-report \
  -H "Content-Type: application/json" \
  -d '{"postcode":"B11 1AA","budget":1200,"care_type":"residential"}'
```
**Результат:** ✅ Успешно (после исправления)

---

## 📊 Статус серверов

| Сервис | Порт | Статус |
|--------|------|--------|
| Frontend (Vite) | 3001 | ✅ Работает |
| Backend (Python) | 8001 | ✅ Работает |
| Прокси конфигурация | - | ✅ Исправлена |

---

## 🎯 Результат

- ✅ Прокси настроен на правильный порт (8001)
- ✅ Запросы доходят до backend
- ✅ Timeout больше не возникает
- ✅ Free Report New работает через веб-интерфейс

---

## 📝 Примечания

1. **Перезапуск frontend обязателен** после изменения `vite.config.ts`
2. **Проверьте, что backend запущен** на порту 8001
3. **Если используется другой порт** для backend, обновите `vite.config.ts` соответственно

---

**Статус:** ✅ Проблема решена, Free Report New работает корректно


