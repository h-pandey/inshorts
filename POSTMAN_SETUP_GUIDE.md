# Postman Collection Setup Guide

## 📥 How to Import the API Collection

### Step 1: Download the Collection File
The collection file `Contextual_News_API.postman_collection.json` has been created in your project root directory.

### Step 2: Import into Postman

#### Method 1: Direct Import
1. Open Postman
2. Click **Import** button (top left)
3. Select **Upload Files**
4. Choose `Contextual_News_API.postman_collection.json`
5. Click **Import**

#### Method 2: Copy-Paste Import
1. Open Postman
2. Click **Import** button
3. Select **Raw text**
4. Copy the entire content of `Contextual_News_API.postman_collection.json`
5. Paste it into the text area
6. Click **Import**

### Step 3: Verify Import
After importing, you should see a new collection called **"Contextual News Data Retrieval System"** in your Postman workspace.

## 🚀 Quick Start Guide

### 1. Start Your API Server
```bash
# Make sure your API is running
docker-compose up -d

# Check if it's healthy
curl http://localhost:8000/health
```

### 2. Test Basic Endpoints
Start with these simple tests:

#### Health Check
- **Collection**: Health & System → Health Check
- **Method**: GET
- **URL**: `http://localhost:8000/health`
- **Expected**: 200 OK with status "healthy"

#### Get Technology News
- **Collection**: News Endpoints → Get News by Category
- **Method**: GET
- **URL**: `http://localhost:8000/api/v1/news/category?category=technology&limit=3`
- **Expected**: Array of technology articles

### 3. Test Smart Query Endpoint
- **Collection**: Smart Query (LLM-Powered) → Smart Query - Technology News
- **Method**: POST
- **URL**: `http://localhost:8000/api/v1/news/query`
- **Body**: Pre-configured JSON with technology query
- **Expected**: Intelligent analysis and relevant articles

## 📋 Collection Structure

### 🏥 Health & System
- **Health Check**: Verify API is running
- **Root Endpoint**: Get API information
- **API Documentation**: Access Swagger UI

### 📰 News Endpoints
- **Get News by Category**: Filter by category (technology, sports, business, etc.)
- **Search News**: Text search in titles and descriptions
- **Get News by Source**: Filter by news source (Reuters, Hindustan Times, etc.)
- **Get News by Score**: Filter by relevance score (0.0-1.0)
- **Get News Nearby**: Location-based search with radius

### 🤖 Smart Query (LLM-Powered)
- **Smart Query - Basic**: Simple natural language queries
- **Smart Query - With Location**: Location-aware queries
- **Smart Query - Technology News**: Pre-configured technology query
- **Smart Query - Sports News**: Pre-configured sports query
- **Smart Query - Business News**: Pre-configured business query
- **Smart Query - Source Specific**: Source-specific queries
- **Smart Query - High Quality News**: Quality-based queries
- **Smart Query - Location Based**: Location-based queries
- **Smart Query - Complex Query**: Multi-criteria queries

### 🧪 Test Scenarios
- **Test All Categories**: Pre-configured tests for all news categories
- **Test All Sources**: Tests for major news sources
- **Test Search Queries**: Various search term tests
- **Test Score Ranges**: Different quality thresholds
- **Test Locations**: Major Indian cities with different radii

### ❌ Error Testing
- **Invalid Category**: Test error handling
- **Empty Search Query**: Test validation
- **Invalid Score Range**: Test parameter validation
- **Invalid Coordinates**: Test geospatial validation
- **Empty Smart Query**: Test smart query validation

## 🔧 Environment Variables

The collection includes these pre-configured variables:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `category` | `technology` | Default category |
| `limit` | `5` | Default article limit |
| `search_query` | `cricket` | Default search term |
| `source_name` | `Hindustan Times` | Default news source |
| `min_score` | `0.7` | Default relevance score |
| `latitude` | `28.6139` | Default latitude (Delhi) |
| `longitude` | `77.2090` | Default longitude (Delhi) |
| `radius_km` | `10` | Default search radius |
| `smart_query` | `technology news` | Default smart query |
| `include_summary` | `true` | Include LLM summaries |
| `include_analysis` | `true` | Include analysis details |

## 🎯 Recommended Testing Sequence

### 1. System Health Check
```
Health & System → Health Check
```
**Expected**: 200 OK with healthy status

### 2. Basic News Retrieval
```
News Endpoints → Get News by Category
```
**Parameters**: `category=technology&limit=3`
**Expected**: Array of technology articles

### 3. Smart Query Testing
```
Smart Query (LLM-Powered) → Smart Query - Technology News
```
**Expected**: Intelligent analysis + relevant articles

### 4. Location-Based Testing
```
Smart Query (LLM-Powered) → Smart Query - Location Based
```
**Expected**: Location-aware results

### 5. Error Handling
```
Error Testing → Empty Search Query
```
**Expected**: 400 Bad Request error

## 📊 Expected Response Formats

### Standard News Response
```json
{
  "articles": [
    {
      "id": "article-id",
      "title": "Article Title",
      "description": "Article description...",
      "url": "https://example.com/article",
      "publication_date": "2025-03-25T18:00:55",
      "source_name": "Hindustan Times",
      "category": ["technology"],
      "relevance_score": 0.85,
      "latitude": 28.6139,
      "longitude": 77.2090
    }
  ],
  "total": 3,
  "category": "technology",
  "limit": 3
}
```

### Smart Query Response
```json
{
  "articles": [...],
  "total": 3,
  "query": "technology news",
  "processing_time_ms": 45.2,
  "timestamp": "2025-03-22T13:09:06.123456",
  "cache_hit": false,
  "analysis": {
    "intent": "category",
    "entities": {"topics": ["technology"]},
    "parameters": {"category": "technology"},
    "confidence": 0.8,
    "reasoning": "Detected technology category intent"
  },
  "routing_strategy": {
    "primary_endpoint": "category",
    "secondary_endpoints": [],
    "parameters": {"category": "technology"},
    "strategy_type": "single",
    "confidence": 0.8
  }
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Connection Refused
**Error**: `Could not get any response`
**Solution**: 
- Ensure API is running: `docker-compose ps`
- Check if port 8000 is accessible: `curl http://localhost:8000/health`

#### 2. Empty Results
**Error**: No articles returned
**Solution**:
- Check if data is loaded: Test basic category endpoint
- Try different query terms
- Verify database connection

#### 3. Smart Query Errors
**Error**: 500 Internal Server Error
**Solution**:
- Check API logs: `docker-compose logs app`
- Try simpler queries first
- Verify LLM service configuration

#### 4. Invalid JSON
**Error**: 400 Bad Request
**Solution**:
- Check JSON syntax in request body
- Ensure all required fields are present
- Validate parameter types

### Performance Expectations

| Endpoint Type | Expected Response Time |
|---------------|----------------------|
| Health Check | < 50ms |
| Category/Source/Score | < 100ms |
| Search | < 200ms |
| Nearby | < 200ms |
| Smart Query | < 1000ms |

## 🎉 Success Indicators

### ✅ Healthy System
- Health check returns 200 OK
- All basic endpoints return data
- Response times under expected thresholds

### ✅ Smart Query Working
- Intent detection working (category, search, source, etc.)
- Analysis confidence scores > 0.5
- Relevant articles returned
- Processing time < 1000ms

### ✅ Error Handling
- Invalid inputs return appropriate error codes
- Error messages are descriptive
- System remains stable after errors

## 📈 Advanced Testing

### Load Testing
Use Postman's Collection Runner to:
1. Select multiple requests
2. Set iterations (e.g., 10)
3. Run collection
4. Monitor response times and success rates

### Automated Testing
Create Postman tests to:
1. Validate response structure
2. Check response times
3. Verify error handling
4. Test data quality

### Example Test Script
```javascript
// Add to Tests tab in Postman
pm.test("Response time is less than 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

pm.test("Response has articles array", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('articles');
    pm.expect(jsonData.articles).to.be.an('array');
});

pm.test("Response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('total');
    pm.expect(jsonData).to.have.property('query');
});
```

## 🚀 Next Steps

1. **Import the collection** using the steps above
2. **Start with health check** to verify API is running
3. **Test basic endpoints** to ensure data is loaded
4. **Try smart queries** to test LLM integration
5. **Run test scenarios** to validate all functionality
6. **Test error cases** to verify error handling
7. **Monitor performance** and response times

The collection is designed to be comprehensive and user-friendly, with pre-configured examples and clear documentation for each endpoint.


