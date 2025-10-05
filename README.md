# Contextual News Data Retrieval System

A backend system that can fetch and organize news articles from a data source, simulating different API functionalities, and enriching these articles with LLM-generated insights.

## 🚀 Features

- **Smart Query Processing**: Uses LLM to analyze user queries and determine the best retrieval strategy
- **Multiple API Endpoints**: Category, search, nearby, source, and score-based news retrieval
- **Geospatial Queries**: Location-based news retrieval with distance calculation
- **LLM Integration**: OpenAI API integration for query analysis and article summarization
- **Trending News**: Location-based trending news with user interaction simulation
- **Caching**: Redis-based caching for improved performance
- **Real-time Processing**: Async/await architecture for high performance

## 🏗️ Architecture

```
app/
├── api/           # API endpoints and routers
├── core/          # Core configuration and database connections
├── models/        # Pydantic models and schemas
├── services/      # Business logic and service layers
├── utils/         # Utility functions and helpers
└── main.py        # FastAPI application entry point
```

## 🛠️ Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB with Motor (async driver)
- **Cache**: Redis
- **LLM**: OpenAI GPT-3.5-turbo
- **Validation**: Pydantic
- **Testing**: pytest
- **Code Quality**: black, isort, flake8, mypy

## 📋 Prerequisites

- Python 3.11 or higher
- MongoDB (local or cloud)
- Redis (local or cloud)
- OpenAI API key

## 🚀 Quick Start

### Option 1: Docker Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd contextual-news-api

# Copy environment template
cp env.example .env

# Edit .env file with your OpenAI API key
# Set: OPENAI_API_KEY=your_key_here

# Start all services with Docker
# Linux/Mac:
./scripts/docker-setup.sh start

# Windows:
scripts\docker-setup.bat start

# Or manually:
docker-compose up --build -d
```

**Docker Services:**
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB Admin**: http://localhost:8081 (admin/admin123)
- **Redis Admin**: http://localhost:8082 (admin/admin123)

### Option 2: Local Development Setup

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd contextual-news-api

# Run setup script
python scripts/setup.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/macOS:
source venv/bin/activate
```

### 2. Configuration

Copy the environment template and update with your settings:

```bash
cp env.example .env
```

Update `.env` with your configuration:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=news_db

# Redis
REDIS_URL=redis://localhost:6379

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start Services

Make sure MongoDB and Redis are running:

```bash
# Start MongoDB (if using local instance)
mongod

# Start Redis (if using local instance)
redis-server
```

### 4. Run the Application

```bash
# Development server
python scripts/run_dev.py

# Or directly
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Setup

For detailed Docker setup instructions, see [DOCKER_SETUP.md](DOCKER_SETUP.md).

**Quick Docker Commands:**
```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

## 📚 API Endpoints

### Core Endpoints

- `GET /api/v1/news/category` - Get news by category
- `GET /api/v1/news/search` - Search news articles
- `GET /api/v1/news/nearby` - Get nearby news by location
- `GET /api/v1/news/source` - Get news by source
- `GET /api/v1/news/score` - Get news by relevance score

### Smart Query

- `POST /api/v1/news/query` - Intelligent query processing with LLM

### Trending News

- `GET /api/v1/news/trending` - Get trending news by location

### Utility

- `GET /health` - Health check
- `GET /` - API information

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test types
pytest tests/unit/
pytest tests/integration/
```

## 🔧 Development

### Code Quality

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code
flake8 app/ tests/
mypy app/
```

### Database Setup

```bash
# Create indexes (will be implemented in data ingestion task)
python scripts/create_indexes.py
```

## 📊 Data Model

### Article Schema

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "url": "string",
  "publication_date": "datetime",
  "source_name": "string",
  "category": ["array"],
  "relevance_score": "float",
  "latitude": "float",
  "longitude": "float",
  "llm_summary": "string"
}
```

## 🚧 Implementation Status

- [x] **Task 1**: Project Setup ✅
- [ ] **Task 2**: Database Design
- [ ] **Task 3**: Data Ingestion
- [ ] **Task 4**: Basic API Structure
- [ ] **Task 5**: Category Endpoint
- [ ] **Task 6**: Search Endpoint
- [ ] **Task 7**: Nearby Endpoint
- [ ] **Task 8**: Source Endpoint
- [ ] **Task 9**: Score Endpoint
- [ ] **Task 10**: LLM Integration
- [ ] **Task 11**: Smart Query Endpoint
- [ ] **Task 12**: LLM Summarization
- [ ] **Task 13**: Caching Layer
- [ ] **Task 14**: Error Handling
- [ ] **Task 15**: User Events Simulation
- [ ] **Task 16**: Trending Algorithm
- [ ] **Task 17**: Trending Endpoint
- [ ] **Task 18**: Performance Optimization
- [ ] **Task 19**: Monitoring & Logging
- [ ] **Task 20**: Testing
- [ ] **Task 21**: Deployment Setup
- [ ] **Task 22**: Documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---

**Built with ❤️ using FastAPI, MongoDB, and OpenAI**