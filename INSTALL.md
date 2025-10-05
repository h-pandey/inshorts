# Installation Guide

## Quick Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# At minimum, update:
# - OPENAI_API_KEY=your_key_here
# - MONGODB_URL (if not using default)
# - REDIS_URL (if not using default)
```

### 4. Start Services

Make sure you have MongoDB and Redis running:

**MongoDB:**
```bash
# If using local MongoDB
mongod

# Or use MongoDB Atlas (cloud)
# Update MONGODB_URL in .env
```

**Redis:**
```bash
# If using local Redis
redis-server

# Or use Redis Cloud
# Update REDIS_URL in .env
```

### 5. Test Setup

```bash
# Test the setup
python scripts/test_setup.py

# Run basic tests
pytest tests/test_basic.py
```

### 6. Start Application

```bash
# Development server
python scripts/run_dev.py

# Or directly
python -m app.main
```

## Verification

Once running, you can verify the setup:

1. **Health Check**: http://localhost:8000/health
2. **API Documentation**: http://localhost:8000/docs
3. **Root Endpoint**: http://localhost:8000/

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **Database Connection**: Check MongoDB is running and accessible
3. **Redis Connection**: Check Redis is running and accessible
4. **OpenAI API**: Verify API key is valid and has credits

### Dependencies Issues

If you encounter dependency conflicts:

```bash
# Create fresh virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Python Version

Ensure you're using Python 3.11 or higher:

```bash
python --version
```

If you need to upgrade Python, visit: https://www.python.org/downloads/
