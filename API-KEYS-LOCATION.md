# 📍 Расположение файла с API ключами

## 🔑 Файл конфигурации с реальными ключами

**Путь к файлу:**
```
api-testing-suite/backend/config.json
```

**Полный путь (оригинальный проект):**
```
/Users/alexandertryvailo/Documents/Products/RCH-playground/api-testing-suite/backend/config.json
```

## ⚠️ Важно

- ✅ Этот файл **НЕ** находится в GitHub репозитории (он в `.gitignore`)
- ✅ Файл содержит **реальные API ключи** - храните его в безопасности
- ✅ Никогда не коммитьте этот файл в Git

## 📋 Структура файла

Файл содержит следующие API ключи:

```json
{
  "cqc": {
    "partner_code": "...",
    "primary_subscription_key": "...",
    "secondary_subscription_key": "..."
  },
  "google_places": {
    "api_key": "..."
  },
  "perplexity": {
    "api_key": "..."
  },
  "openai": {
    "api_key": "..."
  },
  "firecrawl": {
    "api_key": "..."
  },
  "companies_house": {
    "api_key": "..."
  },
  "anthropic": {
    "api_key": "..."
  }
}
```

## 🚀 Как создать файл для нового проекта

1. Скопируйте шаблон:
```bash
cd api-testing-suite/backend
cp config.json.example config.json
```

2. Откройте `config.json` в редакторе

3. Замените placeholder'ы на реальные API ключи

## 🔒 Альтернативный способ: переменные окружения

Вместо `config.json` можно использовать переменные окружения. Создайте файл `.env` в корне проекта:

```bash
# CQC
CQC_PARTNER_CODE=your-partner-code
CQC_PRIMARY_SUBSCRIPTION_KEY=your-primary-key
CQC_SECONDARY_SUBSCRIPTION_KEY=your-secondary-key

# Google Places
GOOGLE_PLACES_API_KEY=your-google-places-key

# Perplexity
PERPLEXITY_API_KEY=your-perplexity-key

# OpenAI
OPENAI_API_KEY=your-openai-key

# Firecrawl
FIRECRAWL_API_KEY=your-firecrawl-key

# Companies House
COMPANIES_HOUSE_API_KEY=your-companies-house-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-key

# BestTime
BESTTIME_PRIVATE_KEY=your-besttime-private-key
BESTTIME_PUBLIC_KEY=your-besttime-public-key
```

## 📝 Где найти ключи

- **CQC API**: https://api-portal.service.cqc.org.uk/
- **Google Places**: https://console.cloud.google.com/apis/credentials
- **Perplexity**: https://www.perplexity.ai/settings/api
- **OpenAI**: https://platform.openai.com/api-keys
- **Firecrawl**: https://firecrawl.dev/dashboard
- **Companies House**: https://developer.company-information.service.gov.uk/
- **Anthropic**: https://console.anthropic.com/settings/keys
- **BestTime**: https://besttime.app/dashboard

## 🛡️ Безопасность

1. ✅ Файл `config.json` уже в `.gitignore` - не попадет в Git
2. ✅ Файл `.env` тоже в `.gitignore`
3. ✅ Используйте `config.json.example` как шаблон для других разработчиков
4. ✅ Никогда не делитесь реальными ключами публично
5. ✅ Ротация ключей при утечке

## 📂 Файлы в репозитории

- ✅ `config.json.example` - шаблон без реальных ключей (в Git)
- ❌ `config.json` - реальные ключи (НЕ в Git)
- ✅ `.env` файлы - переменные окружения (НЕ в Git)

---

**Текущее расположение файла с ключами:**
`/Users/alexandertryvailo/Documents/Products/RCH-playground/api-testing-suite/backend/config.json`


