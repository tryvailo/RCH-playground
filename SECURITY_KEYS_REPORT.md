# Отчет о найденных API ключах в репозитории

## ⚠️ КРИТИЧЕСКАЯ ПРОБЛЕМА БЕЗОПАСНОСТИ

В репозитории были обнаружены реальные API ключи, которые были закоммичены в историю git.

## Найденные ключи

### 1. Файл `api-testing-suite/backend/config.json` (УДАЛЕН из репозитория)

**Статус:** ✅ Удален из git в коммите `090122df`

**Найденные ключи:**
- **Google Places API Key:** `AIzaSyDAMAyN1b8t05DJGIBt9jr6FA3zEbAVOU8`
- **Perplexity API Key:** `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`
- **OpenAI API Key:** `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`
- **Firecrawl API Key:** `fc-864a2c592f884561aa6887041fafcaf8`
- **Companies House API Key:** `cff980e9-34b2-4060-a606-580aefae4f82`
- **OS Places API Key:** `4rt8r3Hnr6W4PreGYYtClGmmxix1ICTz`
- **OS Places API Secret:** `vkN8lePzf2EhSG49`
- **Anthropic API Key:** `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`
- **CQC Subscription Keys:**
  - Primary: `e96322da6d094f0ebec30c526a74205a`
  - Secondary: `b9dfa372a9ec40cf96fa4d5e1c1dbc23`

### 2. HTML файлы (ИСПРАВЛЕНО)

**Статус:** ✅ Заменены на placeholder в коммите `5cf9c1f9`

**Найденные ключи:**
- **Google Maps API Key:** `AIzaSyAK2cPMbhYHWeTh6FYLtv09LzYamyzjf0U`
  - Файлы:
    - `RCH-data/input/autumna/Data-MD/html 1 /test1-html.html`
    - `RCH-data/input/autumna/Data-MD/html 2/Treetops Court Care Home _ Care Home _ Leek, ST13 8XP.html`
    - `RCH-data/input/autumna/Data-MD/html 3/Hen Cloud House _ Care Home _ Leek, ST13 6EQ.html`

## Выполненные исправления

1. ✅ Удален `config.json` из git репозитория (файл остался локально, но больше не отслеживается)
2. ✅ Заменены Google Maps API ключи в HTML файлах на placeholder `YOUR_GOOGLE_MAPS_API_KEY`
3. ✅ Исправлены конфликты слияния в HTML файлах
4. ✅ Файл `config.json` уже находится в `.gitignore`

## ⚠️ КРИТИЧЕСКИ ВАЖНО: Отзыв ключей

**ВСЕ НАЙДЕННЫЕ КЛЮЧИ ДОЛЖНЫ БЫТЬ НЕМЕДЛЕННО ОТОЗВАНЫ И ПЕРЕСОЗДАНЫ!**

### Инструкции по отзыву:

#### Google Places API
1. Перейти в [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Credentials
3. Найти ключ `AIzaSyDAMAyN1b8t05DJGIBt9jr6FA3zEbAVOU8`
4. Удалить или ограничить доступ
5. Создать новый ключ

#### Google Maps API
1. Перейти в [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Credentials
3. Найти ключ `AIzaSyAK2cPMbhYHWeTh6FYLtv09LzYamyzjf0U`
4. Удалить или ограничить доступ
5. Создать новый ключ

#### OpenAI API
1. Перейти в [OpenAI Platform](https://platform.openai.com/)
2. API Keys
3. Найти ключ `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`
4. Удалить ключ
5. Создать новый ключ

#### Anthropic API
1. Перейти в [Anthropic Console](https://console.anthropic.com/)
2. API Keys
3. Найти ключ `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`
4. Удалить ключ
5. Создать новый ключ

#### Perplexity API
1. Перейти в [Perplexity Account Settings](https://www.perplexity.ai/settings)
2. API Keys
3. Удалить ключ `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`
4. Создать новый ключ

#### Firecrawl API
1. Перейти в [Firecrawl Dashboard](https://firecrawl.dev/)
2. API Keys
3. Удалить ключ `fc-864a2c592f884561aa6887041fafcaf8`
4. Создать новый ключ

#### Companies House API
1. Перейти в [Companies House Developer Hub](https://developer.company-information.service.gov.uk/)
2. API Keys
3. Удалить ключ `cff980e9-34b2-4060-a606-580aefae4f82`
4. Создать новый ключ

#### OS Places API
1. Перейти в [Ordnance Survey Developer Portal](https://osdatahub.os.uk/)
2. API Keys
3. Удалить ключ `4rt8r3Hnr6W4PreGYYtClGmmxix1ICTz` и секрет
4. Создать новый ключ

#### CQC API
1. Связаться с CQC для отзыва ключей:
   - Primary: `e96322da6d094f0ebec30c526a74205a`
   - Secondary: `b9dfa372a9ec40cf96fa4d5e1c1dbc23`

## Важные замечания

1. **История git:** Ключи все еще присутствуют в истории git. Для полного удаления необходимо использовать `git filter-branch` или `git filter-repo`, но это требует перезаписи истории и может быть проблематично для публичных репозиториев.

2. **Локальный файл:** Файл `config.json` остался локально, но больше не отслеживается git благодаря `.gitignore`.

3. **Шаблон:** Используйте `config.json.example` как шаблон для создания нового `config.json` локально.

4. **Мониторинг:** Рекомендуется настроить автоматическое сканирование репозитория на наличие секретов (например, через GitHub Secret Scanning или git-secrets).

## Коммиты с исправлениями

- `090122df` - security: remove config.json with API keys from repository
- `5cf9c1f9` - security: replace Google Maps API keys with placeholder in HTML files

## Рекомендации на будущее

1. ✅ Использовать `.env` файлы для локальной разработки
2. ✅ Никогда не коммитить файлы с реальными ключами
3. ✅ Использовать переменные окружения в production
4. ✅ Настроить pre-commit hooks для проверки на секреты
5. ✅ Использовать секретные менеджеры (AWS Secrets Manager, HashiCorp Vault и т.д.)






