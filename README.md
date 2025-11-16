# RCH Playground

A comprehensive playground and testing suite for RightCareHome project APIs and data sources.

## 📁 Project Structure

```
RCH-playground/
├── api-testing-suite/          # Main API testing web application
│   ├── backend/                # FastAPI backend
│   └── frontend/               # React + TypeScript frontend
├── companies-house/            # Companies House API integration scripts
├── cqcr-master/               # CQC R package (external dependency)
├── documentation/            # API documentation and guides
└── *.py                       # Standalone testing scripts
```

## 🚀 Quick Start

### API Testing Suite

The main web application for testing multiple APIs. See detailed instructions in [`api-testing-suite/README.md`](api-testing-suite/README.md).

**Quick setup:**
```bash
# Backend
cd api-testing-suite/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd api-testing-suite/frontend
npm install
```

**Configuration:**
1. Copy `api-testing-suite/backend/config.json.example` to `api-testing-suite/backend/config.json`
2. Add your API keys to `config.json` (see [API Credentials Guide](documentation/API-Credentials-Guide.md))
3. Or use environment variables (see `env.template`)

**Run:**
```bash
# Terminal 1 - Backend
cd api-testing-suite/backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd api-testing-suite/frontend
npm run dev
```

Open `http://localhost:3000` in your browser.

## 📋 Supported APIs

1. **CQC API** - Care Quality Commission (Free)
2. **FSA FHRS API** - Food Standards Agency (Free)
3. **Companies House API** - Company financial data (Free)
4. **Google Places API** - Reviews and ratings (Paid)
5. **Perplexity API** - News and reputation monitoring (Paid)
6. **BestTime.app** - Footfall analytics (Paid)
7. **Firecrawl** - Web scraping (Paid)
8. **OpenAI** - AI processing (Paid)
9. **Anthropic Claude** - AI processing (Paid)

## 📚 Documentation

- [API Credentials Guide](documentation/API-Credentials-Guide.md) - How to obtain API keys
- [CQC API Setup Guide](documentation/CQC_API_SETUP_GUIDE.md) - CQC API configuration
- [FSA Integration Guide](documentation/fsa/) - FSA API documentation
- [Companies House Guide](companies-house/CompaniesHouse_README.md) - Companies House integration

## 🔒 Security

**⚠️ Important:** Never commit API keys or sensitive credentials to the repository.

- `config.json` files are in `.gitignore`
- Use `config.json.example` as a template
- Prefer environment variables for production
- See `.gitignore` for excluded files

## 🛠️ Development

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Adding a New API

1. Create client in `api-testing-suite/backend/api_clients/`
2. Add credentials model in `api-testing-suite/backend/models/schemas.py`
3. Add test endpoint in `api-testing-suite/backend/main.py`
4. Create frontend component in `api-testing-suite/frontend/src/pages/`

## 📝 License

This project is part of the RightCareHome platform.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all sensitive data is excluded
5. Submit a pull request

## 🆘 Support

For issues or questions:
- Check the documentation in `documentation/` folder
- Review API-specific guides
- Open an issue on GitHub

---

**Built with ❤️ for RightCareHome**

