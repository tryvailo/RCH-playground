# RightCareHome API Testing Suite

Comprehensive web application for testing and validating all API data sources for the RightCareHome project.

## 🚀 Features

- **Multi-API Testing**: Test 7 different API sources simultaneously
- **Real-time Progress**: WebSocket-based progress tracking
- **Data Fusion**: Combine data from multiple sources for insights
- **Cost Tracking**: Monitor API usage costs in real-time
- **Analytics Dashboard**: Visualize performance metrics
- **Export Options**: Export results as JSON, CSV, or PDF

## 📋 Supported APIs

1. **CQC API** - Care Quality Commission (Free)
2. **FSA FHRS API** - Food Standards Agency (Free)
3. **Companies House API** - Company financial data (Free)
4. **Google Places API** - Reviews and ratings (Paid)
5. **Perplexity API** - News and reputation monitoring (Paid)
6. **BestTime.app** - Footfall analytics (Paid)
7. **Autumna** - Web scraping for pricing (Free, requires proxy)

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **httpx** - Async HTTP client
- **Pydantic** - Data validation
- **WebSockets** - Real-time updates

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Zustand** - State management
- **Vite** - Build tool

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

1. Copy `.env.example` to `.env` in the root directory
2. Fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📖 Usage

### 1. Configure API Credentials

Navigate to `/config` and enter your API credentials for each service.

### 2. Run Tests

Go to `/test` and:
- Select APIs to test
- Enter test data (or use provided examples)
- Click "Run Comprehensive Test"

### 3. View Results

After tests complete, view detailed results including:
- Individual API results
- Data fusion analysis
- Risk assessment
- Cost breakdown

### 4. Analytics

Check `/analytics` for:
- API reliability metrics
- Response time comparisons
- Cost analysis
- Coverage insights

## 🔧 API Endpoints

### Configuration
- `POST /api/config/credentials` - Save API credentials
- `GET /api/config/credentials` - Get saved credentials
- `POST /api/config/validate` - Validate credentials

### Testing
- `POST /api/test/cqc` - Test CQC API
- `POST /api/test/fsa` - Test FSA API
- `POST /api/test/companies-house` - Test Companies House
- `POST /api/test/google-places` - Test Google Places
- `POST /api/test/perplexity` - Test Perplexity
- `POST /api/test/besttime` - Test BestTime
- `POST /api/test/autumna` - Test Autumna
- `POST /api/test/comprehensive` - Run all tests

### Results
- `GET /api/test/status/:job_id` - Get test status
- `GET /api/test/results/:job_id` - Get test results

### Analytics
- `POST /api/analyze/coverage` - Calculate coverage
- `POST /api/analyze/quality` - Data quality metrics
- `POST /api/analyze/costs` - Cost analysis
- `POST /api/analyze/fusion` - Data fusion analysis

## 🏗️ Project Structure

```
api-testing-suite/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── api_clients/            # API client implementations
│   ├── models/                 # Pydantic models
│   ├── services/               # Business logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── components/         # Reusable components
│   │   ├── stores/             # Zustand stores
│   │   └── types/              # TypeScript types
│   └── package.json
└── README.md
```

## 🔒 Security Notes

- API keys are stored in backend `.env` file
- Frontend never receives full API keys
- Credentials are encrypted in browser storage
- Never commit `.env` file to version control

## 📝 Development

### Adding a New API

1. Create client in `backend/api_clients/`
2. Add credentials model in `backend/models/schemas.py`
3. Add test endpoint in `backend/main.py`
4. Create test component in `frontend/src/components/ApiTester/`
5. Update API list in `frontend/src/pages/TestRunner.tsx`

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🐛 Troubleshooting

### Backend Issues
- Check API keys are correct in `.env`
- Verify Python version (3.9+)
- Check port 8000 is available

### Frontend Issues
- Clear browser cache
- Check Node.js version (18+)
- Verify backend is running

### API Connection Issues
- Validate credentials in `/config`
- Check network connectivity
- Review API rate limits

## 📚 Documentation

- [CQC API Docs](https://api-portal.service.cqc.org.uk/)
- [FSA API Docs](https://api.ratings.food.gov.uk/help)
- [Companies House Docs](https://developer.company-information.service.gov.uk/)
- [Google Places Docs](https://developers.google.com/maps/documentation/places)
- [Perplexity Docs](https://docs.perplexity.ai/)
- [BestTime Docs](https://documentation.besttime.app/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of the RightCareHome platform.

## 🆘 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub

---

**Built with ❤️ for RightCareHome**

