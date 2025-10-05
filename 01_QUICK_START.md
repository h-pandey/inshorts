# 🚀 Quick Start Guide
## Get Your Contextual News API Running in 5 Minutes

> **This guide will get you from zero to a fully functional news API in just 5 minutes.**

---

## ⚡ **Prerequisites Check**

Before we start, make sure you have:
- [ ] **Docker** installed and running
- [ ] **Docker Compose** available
- [ ] **Git** installed
- [ ] **4GB RAM** available
- [ ] **2GB disk space** available

**Quick check:**
```bash
docker --version
docker-compose --version
git --version
```

---

## 🎯 **Step 1: Clone & Start (2 minutes)**

```bash
# Clone the repository
git clone [your-repository-url]
cd contextual-news-api

# Start all services with one command
docker-compose up -d
```

**What this does:**
- Downloads and starts MongoDB (database)
- Downloads and starts Redis (caching)
- Builds and starts the FastAPI application
- Sets up admin interfaces for MongoDB and Redis

---

## ⏳ **Step 2: Wait for Services (1 minute)**

```bash
# Check if all services are healthy
docker-compose ps
```

**Expected output:**
```
NAME                IMAGE                    COMMAND                  SERVICE     CREATED        STATUS                    PORTS
news_api            contextual-news-api      "python app/simple_…"   app         2 minutes ago  Up 2 minutes (healthy)   0.0.0.0:8000->8000/tcp
news_mongodb        mongo:7.0               "docker-entrypoint.s…"   mongodb     2 minutes ago  Up 2 minutes (healthy)   0.0.0.0:27017->27017/tcp
news_redis          redis:7-alpine          "docker-entrypoint.s…"   redis       2 minutes ago  Up 2 minutes (healthy)   0.0.0.0:6379->6379/tcp
```

**All services should show "healthy" status.**

---

## ✅ **Step 3: Test the API (1 minute)**

```bash
# Test the health endpoint
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "cache": "connected",
    "llm_service": "available"
  }
}
```

---

## 🧠 **Step 4: Test Smart Query (1 minute)**

```bash
# Test the intelligent query endpoint
curl -X POST "http://localhost:8000/api/v1/news/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "technology news", "limit": 3}'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Query processed successfully",
  "total_results": 3,
  "query_time_ms": 150,
  "results": [
    {
      "title": "AI Breakthrough in Natural Language Processing",
      "description": "Researchers develop new model...",
      "category": ["technology"],
      "source": "TechNews",
      "publication_date": "2024-01-15T08:00:00Z",
      "relevance_score": 0.95,
      "location": {
        "name": "San Francisco, CA",
        "coordinates": {"lat": 37.7749, "lon": -122.4194}
      }
    }
  ],
  "analysis": {
    "intent": "category_search",
    "parameters": {"category": "technology"},
    "confidence": 0.9
  }
}
```

---

## 🎉 **Congratulations! You're Ready**

Your Contextual News API is now running with:

### **🌐 Access Points**
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### **🔧 Admin Interfaces**
- **MongoDB Admin**: http://localhost:8081 (admin/admin123)
- **Redis Admin**: http://localhost:8082 (admin/admin123)

---

## 🚀 **Next Steps**

### **1. Explore the API Documentation**
Visit http://localhost:8000/docs to see all available endpoints and try them interactively.

### **2. Test Different Query Types**
```bash
# Category-based search
curl "http://localhost:8000/api/v1/news/category?category=technology&limit=5"

# Full-text search
curl "http://localhost:8000/api/v1/news/search?query=climate&limit=5"

# Location-based search
curl -X POST "http://localhost:8000/api/v1/news/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "news near New York", "location": {"lat": 40.7128, "lon": -74.0060}}'
```

### **3. Use Postman Collection**
Import the Postman collection from `postman/Contextual_News_API.postman_collection.json` for comprehensive testing.

---

## 🛠️ **Troubleshooting**

### **Services Not Starting**
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f app

# Restart services
docker-compose restart
```

### **API Not Responding**
```bash
# Check if app is healthy
curl http://localhost:8000/health

# Check app logs
docker-compose logs app

# Restart app only
docker-compose restart app
```

### **Database Issues**
```bash
# Check MongoDB status
docker-compose logs mongodb

# Access MongoDB admin
open http://localhost:8081
```

### **Port Conflicts**
If you have port conflicts, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

---

## 📊 **System Status Dashboard**

### **Health Check Commands**
```bash
# Overall system health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/database

# Cache connectivity
curl http://localhost:8000/health/cache

# LLM service status
curl http://localhost:8000/health/llm
```

### **Performance Monitoring**
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/v1/news/category?category=technology"

# View system metrics
curl http://localhost:8000/metrics
```

---

## 🎯 **Quick Test Suite**

Run these commands to verify everything is working:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Category endpoint
curl "http://localhost:8000/api/v1/news/category?category=technology&limit=2"

# 3. Search endpoint
curl "http://localhost:8000/api/v1/news/search?query=news&limit=2"

# 4. Source endpoint
curl "http://localhost:8000/api/v1/news/source?source=Reuters&limit=2"

# 5. Score endpoint
curl "http://localhost:8000/api/v1/news/score?min_score=0.8&limit=2"

# 6. Smart query endpoint
curl -X POST "http://localhost:8000/api/v1/news/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "technology", "limit": 2}'
```

**All commands should return JSON responses with data.**

---

## 🏆 **Success Indicators**

You'll know everything is working when:

✅ **Health endpoint returns 200 OK**
✅ **All 6 API endpoints respond with data**
✅ **Smart query endpoint processes natural language**
✅ **Response times are under 300ms**
✅ **No error messages in logs**
✅ **Admin interfaces are accessible**

---

## 📚 **What's Next?**

Now that you have the system running, explore:

1. **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete endpoint reference
2. **[Project Analysis](docs/PROJECT_ANALYSIS.md)** - Technical deep dive
3. **[Postman Testing](docs/POSTMAN_SETUP_GUIDE.md)** - Comprehensive testing
4. **[Performance Optimization](docs/PERFORMANCE_GUIDE.md)** - Speed improvements

---

## 🆘 **Need Help?**

### **Common Issues**
- **Port 8000 already in use**: Change port in `docker-compose.yml`
- **Out of memory**: Increase Docker memory limit
- **Slow startup**: Wait 2-3 minutes for full initialization

### **Support Resources**
- Check the `docs/` directory for detailed guides
- View service logs: `docker-compose logs -f [service-name]`
- API documentation: http://localhost:8000/docs

---

## 🎉 **You're All Set!**

Your Contextual News Data Retrieval System is now running and ready for evaluation. The system demonstrates:

- ✅ **Production-ready architecture**
- ✅ **LLM-powered intelligence**
- ✅ **High-performance queries**
- ✅ **Comprehensive error handling**
- ✅ **Complete documentation**

**Start exploring**: Visit http://localhost:8000/docs to see the full API documentation.
