# Contextual News Data Retrieval System - API Documentation

## 📋 Overview

The Contextual News Data Retrieval System provides a comprehensive REST API for fetching, searching, and filtering news articles. The API is built with FastAPI and provides real-time access to a database of 1,791 news articles with advanced filtering and ranking capabilities.

## 🔗 Base URL

```
http://localhost:8000
```

## 📚 API Endpoints

### 1. Health Check

#### GET `/health`

Check the health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-03-22T13:09:06.123456",
  "version": "1.0.0",
  "debug": false
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Category Endpoint

#### GET `/api/v1/news/category`

Retrieve articles from a specific category, ranked by publication date (newest first).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `category` | string | Yes | - | News category to filter by |
| `limit` | integer | No | 20 | Maximum number of articles (1-100) |

**Example Request:**
```bash
GET /api/v1/news/category?category=technology&limit=5
```

**Example Response:**
```json
{
  "articles": [
    {
      "_id": "68d14a3b4599653f1e99f86b",
      "id": "c1548bec-1414-46fb-a7cc-c04fd160b698",
      "title": "83,668 WhatsApp, 3,962 Skype IDs linked to digital arrests blocked",
      "description": "The Centre on Tuesday said that it has blocked over 83,668 WhatsApp and 3,962 Skype accounts used for digital arrests...",
      "url": "https://www.hindustantimes.com/india-news/govt-blocks-83-668-whatsapp-3-962-skype-accounts-linked-to-digital-arrests-101742900554945-amp.html",
      "publication_date": "2025-03-25T18:00:55",
      "source_name": "Hindustan Times",
      "category": ["national", "technology"],
      "relevance_score": 0.0,
      "latitude": 19.865113,
      "longitude": 77.250991,
      "location": {
        "type": "Point",
        "coordinates": [77.250991, 19.865113]
      }
    }
  ],
  "total": 1,
  "category": "technology",
  "limit": 5
}
```

**Available Categories:**
- `national` (647 articles)
- `sports` (296 articles)
- `world` (246 articles)
- `business` (211 articles)
- `entertainment` (208 articles)
- `politics` (205 articles)
- `technology` (89 articles)
- `General` (130 articles)
- `IPL_2025` (127 articles)
- `Health___Fitness` (86 articles)

**Status Codes:**
- `200 OK` - Articles retrieved successfully
- `400 Bad Request` - Invalid parameters
- `503 Service Unavailable` - Database not available

---

### 3. Search Endpoint

#### GET `/api/v1/news/search`

Search articles by text in title and description, ranked by relevance score and text matching.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search term to look for |
| `limit` | integer | No | 20 | Maximum number of articles (1-100) |

**Example Request:**
```bash
GET /api/v1/news/search?query=cricket&limit=3
```

**Example Response:**
```json
{
  "articles": [
    {
      "_id": "68d14a3c4599653f1e99fcf9",
      "id": "8c33fc2d-3c44-485c-b740-82634435cdf5",
      "title": "Pakistan suffer their biggest defeat in T20I cricket history",
      "description": "New Zealand defeated Pakistan by 115 runs in the fourth T20I in Mount Maunganui to take an unassailable 3-1 lead in the five-match series...",
      "url": "https://www.espncricinfo.com/series/new-zealand-vs-pakistan-2024-25-1443540/new-zealand-vs-pakistan-4th-t20i-1443552/live-cricket-score?ex_cid=inshorts",
      "publication_date": "2025-03-23T12:02:55",
      "source_name": "ESPNcricinfo",
      "category": ["sports", "cricket"],
      "relevance_score": 0.99,
      "latitude": 19.682557,
      "longitude": 75.746459,
      "location": {
        "type": "Point",
        "coordinates": [75.746459, 19.682557]
      }
    }
  ],
  "total": 1,
  "query": "cricket",
  "limit": 3
}
```

**Search Features:**
- **Case-insensitive** text search
- **Weighted scoring**: Title matches (weight: 2) > Description matches (weight: 1)
- **Multi-factor ranking**: Text score → Relevance score → Publication date
- **Regex-based** pattern matching

**Status Codes:**
- `200 OK` - Search completed successfully
- `400 Bad Request` - Invalid search query
- `503 Service Unavailable` - Database not available

---

### 4. Source Endpoint

#### GET `/api/v1/news/source`

Retrieve articles from a specific news source, ranked by publication date (newest first).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | Yes | - | News source name to filter by |
| `limit` | integer | No | 20 | Maximum number of articles (1-100) |

**Example Request:**
```bash
GET /api/v1/news/source?source=Reuters&limit=2
```

**Example Response:**
```json
{
  "articles": [
    {
      "_id": "68d14a3b4599653f1e99f845",
      "id": "86d6bde5-f598-407c-9d4b-b490d0ab456b",
      "title": "Oscar-winning Palestinian director injured in Israeli attack released",
      "description": "Hamdan Ballal, the Palestinian co-director of Oscar-winning film 'No Other Land', has been released from Israeli detention after being attacked by Israeli settlers...",
      "url": "https://www.reuters.com/world/middle-east/oscar-winning-palestinian-director-injured-clash-with-israeli-settlers-arrested-2025-03-25/",
      "publication_date": "2025-03-26T03:26:57",
      "source_name": "Reuters",
      "category": ["world", "entertainment"],
      "relevance_score": 0.91,
      "latitude": 21.700474,
      "longitude": 79.654412,
      "location": {
        "type": "Point",
        "coordinates": [79.654412, 21.700474]
      }
    }
  ],
  "total": 1,
  "source": "Reuters",
  "limit": 2
}
```

**Top News Sources:**
- `Hindustan Times` (132 articles)
- `News Karnataka` (127 articles)
- `Free Press Journal` (121 articles)
- `News18` (95 articles)
- `The Indian Express` (82 articles)
- `Moneycontrol` (63 articles)
- `Reuters` (53 articles)
- `PTI` (50 articles)
- `Times Now` (50 articles)
- `ANI` (42 articles)

**Features:**
- **Case-insensitive** source name matching
- **Partial name** matching support
- **Publication date** ranking (newest first)

**Status Codes:**
- `200 OK` - Articles retrieved successfully
- `400 Bad Request` - Invalid source parameter
- `503 Service Unavailable` - Database not available

---

### 5. Score Endpoint

#### GET `/api/v1/news/score`

Retrieve articles with relevance score above a threshold, ranked by relevance score (highest first).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `min_score` | float | No | 0.7 | Minimum relevance score (0.0-1.0) |
| `limit` | integer | No | 20 | Maximum number of articles (1-100) |

**Example Request:**
```bash
GET /api/v1/news/score?min_score=0.8&limit=3
```

**Example Response:**
```json
{
  "articles": [
    {
      "_id": "68d14a3b4599653f1e99f961",
      "id": "e7f184e2-80bb-44f2-94a8-1c2c61d8ec35",
      "title": "Parents are B'wood hillbillies, came to Mumbai from village: Abhay",
      "description": "Actor Abhay Deol opened up about his family dynamics in a recent interview and called his parents \"Bollywood hillbillies\"...",
      "url": "https://indianexpress.com/article/entertainment/bollywood/abhay-deol-calls-his-parents-bollywood-hillbillies-reveals-his-relationship-with-mother-it-was-not-a-normal-situation-9903157/lite/",
      "publication_date": "2025-03-25T11:12:24",
      "source_name": "The Indian Express",
      "category": ["entertainment"],
      "relevance_score": 1.0,
      "latitude": 17.813524,
      "longitude": 80.152686,
      "location": {
        "type": "Point",
        "coordinates": [80.152686, 17.813524]
      }
    }
  ],
  "total": 1,
  "min_score": 0.8,
  "limit": 3
}
```

**Score Ranges:**
- **0.0 - 0.3**: Low relevance
- **0.3 - 0.6**: Medium relevance
- **0.6 - 0.8**: High relevance
- **0.8 - 1.0**: Very high relevance

**Features:**
- **Quality filtering**: Only high-relevance articles
- **Score-based ranking**: Highest scores first
- **Configurable threshold**: Adjustable quality level

**Status Codes:**
- `200 OK` - Articles retrieved successfully
- `400 Bad Request` - Invalid score range
- `503 Service Unavailable` - Database not available

---

## 📊 Data Model

### Article Object

```json
{
  "_id": "string",                    // MongoDB ObjectId
  "id": "string",                     // UUID for external reference
  "title": "string",                  // Article title
  "description": "string",            // Article description/summary
  "url": "string",                    // Source article URL
  "publication_date": "string",       // ISO 8601 timestamp
  "source_name": "string",            // News source name
  "category": ["string"],             // Array of categories
  "relevance_score": "number",        // Relevance score (0.0-1.0)
  "latitude": "number",               // Geographic latitude
  "longitude": "number",              // Geographic longitude
  "location": {                       // GeoJSON Point
    "type": "Point",
    "coordinates": [longitude, latitude]
  }
}
```

### Response Format

All endpoints return a consistent response format:

```json
{
  "articles": [Article],              // Array of article objects
  "total": "number",                  // Number of articles returned
  "query_metadata": {                 // Endpoint-specific metadata
    "category": "string",             // For category endpoint
    "query": "string",                // For search endpoint
    "source": "string",               // For source endpoint
    "min_score": "number"             // For score endpoint
  },
  "limit": "number"                   // Requested limit
}
```

## 🔧 Error Handling

### Error Response Format

```json
{
  "error": "string",                  // Error type
  "message": "string",                // Human-readable error message
  "timestamp": "string",              // ISO 8601 timestamp
  "request_id": "string"              // Unique request identifier (optional)
}
```

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| `400 Bad Request` | Validation Error | Invalid parameters or missing required fields |
| `404 Not Found` | Not Found | Endpoint or resource not found |
| `500 Internal Server Error` | Server Error | Unexpected server error |
| `503 Service Unavailable` | Service Error | Database or external service unavailable |

### Example Error Response

```json
{
  "error": "Validation Error",
  "message": "Category parameter is required",
  "timestamp": "2025-03-22T13:09:06.123456"
}
```

## 🚀 Performance

### Response Times

| Endpoint | Average Response Time | Target |
|----------|----------------------|---------|
| Health Check | < 10ms | < 50ms |
| Category | < 50ms | < 100ms |
| Search | < 100ms | < 200ms |
| Source | < 50ms | < 100ms |
| Score | < 50ms | < 100ms |

### Rate Limiting

- **Default**: 100 requests per minute per IP
- **Burst**: 200 requests per minute for short periods
- **Headers**: Rate limit information in response headers

### Caching

- **Response Caching**: 5 minutes for category and source endpoints
- **Search Caching**: 1 minute for search results
- **Cache Headers**: Standard HTTP caching headers

## 🔒 Security

### Authentication

Currently, the API is open for development. Production deployment should include:

- **API Key Authentication**: Required for all endpoints
- **Rate Limiting**: Per-user rate limits
- **Input Validation**: Comprehensive parameter validation

### CORS

```javascript
// Allowed origins
allow_origins: [
  "http://localhost:3000",
  "http://localhost:8080",
  "http://localhost:8000"
]

// Allowed methods
allow_methods: ["GET", "POST"]

// Allowed headers
allow_headers: ["*"]
```

## 📈 Usage Examples

### 1. Get Latest Technology News

```bash
curl -X GET "http://localhost:8000/api/v1/news/category?category=technology&limit=5" \
  -H "accept: application/json"
```

### 2. Search for Cricket News

```bash
curl -X GET "http://localhost:8000/api/v1/news/search?query=cricket&limit=3" \
  -H "accept: application/json"
```

### 3. Get High-Quality Articles

```bash
curl -X GET "http://localhost:8000/api/v1/news/score?min_score=0.8&limit=5" \
  -H "accept: application/json"
```

### 4. Get Reuters News

```bash
curl -X GET "http://localhost:8000/api/v1/news/source?source=Reuters&limit=3" \
  -H "accept: application/json"
```

## 🧪 Testing

### Interactive API Documentation

Visit the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test Scripts

```bash
# Test all endpoints
python scripts/test_all_endpoints.py

# Test specific endpoint
python scripts/test_category_endpoint.py

# Load testing
python scripts/load_test.py
```

## 📋 Changelog

### Version 1.0.0 (Current)
- ✅ Category endpoint with publication date ranking
- ✅ Search endpoint with text matching and relevance scoring
- ✅ Source endpoint with case-insensitive matching
- ✅ Score endpoint with threshold-based filtering
- ✅ Comprehensive error handling
- ✅ Consistent response format
- ✅ Performance optimization with database indexes

### Upcoming Features
- 🔄 Nearby endpoint with geospatial queries
- 🔄 LLM integration for intelligent query processing
- 🔄 Trending news algorithm
- 🔄 Redis caching layer
- 🔄 Advanced analytics and monitoring

---

## 📞 Support

For API support and questions:
- **Documentation**: This file and interactive docs at `/docs`
- **Health Check**: Monitor service status at `/health`
- **Logs**: Check application logs for debugging

## 🎯 Best Practices

1. **Use appropriate limits**: Don't request more than 100 articles per request
2. **Handle errors gracefully**: Always check response status codes
3. **Cache responses**: Implement client-side caching for better performance
4. **Monitor rate limits**: Respect API rate limits to avoid throttling
5. **Use specific queries**: More specific queries return better results
