"""
Simple main application without Pydantic dependencies.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import time
import json
import os
from datetime import datetime
import motor.motor_asyncio
from typing import Optional, Dict, Any

# Simple configuration without Pydantic
class SimpleSettings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "Contextual News API")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")
        self.cors_origins = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]
        # Database
        self.mongodb_url = os.getenv(
            "MONGODB_URL",
            "mongodb://admin:password123@mongodb:27017/news_db?authSource=admin",
        )
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "news_db")
        self.mongodb_collection = os.getenv("MONGODB_COLLECTION", "articles")

settings = SimpleSettings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Contextual News Data Retrieval System with LLM Integration",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database client (async Motor)
mongo_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
articles_collection = None


@app.on_event("startup")
async def on_startup():
    global mongo_client, articles_collection
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    db = mongo_client[settings.mongodb_database]
    articles_collection = db[settings.mongodb_collection]


@app.on_event("shutdown")
async def on_shutdown():
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = str(process_time)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)")
    
    return response


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Contextual News Data Retrieval System",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "debug": settings.debug
    }


@app.get(f"{settings.api_v1_prefix}/news/category")
async def get_news_by_category(category: str, limit: int = 20):
    """Return latest articles for a given category sorted by publication_date desc."""
    if not category:
        return JSONResponse(status_code=400, content={"error": "Category parameter is required"})
    
    global articles_collection
    if articles_collection is None:
        return JSONResponse(status_code=503, content={"error": "Database not initialized"})

    try:
        # Categories are stored as arrays, so we need to search within the array
        cursor = (
            articles_collection
            .find({"category": {"$in": [category]}})  # Search for category in the array
            .sort("publication_date", -1)
            .limit(max(1, min(limit, 100)))
        )
        docs = await cursor.to_list(length=max(1, min(limit, 100)))

        # Convert ObjectId to string and format response
        articles = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            articles.append(doc)

        return {
            "articles": articles,
            "total": len(articles),
            "category": category,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error in category endpoint: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Internal server error", "message": str(e)}
        )

@app.get(f"{settings.api_v1_prefix}/news/search")
async def search_news(query: str, limit: int = 20):
    """Search articles by text in title and description, ranked by relevance_score and text matching."""
    if not query or not query.strip():
        return JSONResponse(status_code=400, content={"error": "Search query parameter is required"})
    
    global articles_collection
    if articles_collection is None:
        return JSONResponse(status_code=503, content={"error": "Database not initialized"})

    try:
        # Create text search query for title and description
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},  # Case-insensitive search in title
                {"description": {"$regex": query, "$options": "i"}}  # Case-insensitive search in description
            ]
        }
        
        # Use aggregation pipeline to calculate text matching score and sort by relevance
        pipeline = [
            {"$match": search_query},
            {
                "$addFields": {
                    "text_score": {
                        "$add": [
                            {
                                "$cond": [
                                    {"$regexMatch": {"input": "$title", "regex": query, "options": "i"}},
                                    2,  # Higher score for title matches
                                    0
                                ]
                            },
                            {
                                "$cond": [
                                    {"$regexMatch": {"input": "$description", "regex": query, "options": "i"}},
                                    1,  # Lower score for description matches
                                    0
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "$sort": {
                    "text_score": -1,  # Sort by text matching score first
                    "relevance_score": -1,  # Then by relevance score
                    "publication_date": -1  # Finally by publication date
                }
            },
            {"$limit": max(1, min(limit, 100))}
        ]
        
        docs = await articles_collection.aggregate(pipeline).to_list(length=max(1, min(limit, 100)))

        # Convert ObjectId to string and format response
        articles = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            # Remove the temporary text_score field from response
            if "text_score" in doc:
                del doc["text_score"]
            articles.append(doc)

        return {
            "articles": articles,
            "total": len(articles),
            "query": query,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Internal server error", "message": str(e)}
        )


@app.get(f"{settings.api_v1_prefix}/news/source")
async def get_news_by_source(source: str, limit: int = 20):
    """Return latest articles from a specific source, ranked by publication_date desc."""
    if not source or not source.strip():
        return JSONResponse(status_code=400, content={"error": "Source parameter is required"})
    
    global articles_collection
    if articles_collection is None:
        return JSONResponse(status_code=503, content={"error": "Database not initialized"})

    try:
        # Search for articles from the specified source
        cursor = (
            articles_collection
            .find({"source_name": {"$regex": source, "$options": "i"}})  # Case-insensitive search
            .sort("publication_date", -1)
            .limit(max(1, min(limit, 100)))
        )
        docs = await cursor.to_list(length=max(1, min(limit, 100)))

        # Convert ObjectId to string and format response
        articles = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            articles.append(doc)

        return {
            "articles": articles,
            "total": len(articles),
            "source": source,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error in source endpoint: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Internal server error", "message": str(e)}
        )


@app.get(f"{settings.api_v1_prefix}/news/score")
async def get_news_by_score(min_score: float = 0.7, limit: int = 20):
    """Return articles with relevance_score above threshold, ranked by relevance_score desc."""
    if min_score < 0 or min_score > 1:
        return JSONResponse(status_code=400, content={"error": "min_score must be between 0 and 1"})
    
    global articles_collection
    if articles_collection is None:
        return JSONResponse(status_code=503, content={"error": "Database not initialized"})

    try:
        # Search for articles with relevance_score above threshold
        cursor = (
            articles_collection
            .find({"relevance_score": {"$gte": min_score}})
            .sort("relevance_score", -1)  # Sort by relevance_score descending
            .limit(max(1, min(limit, 100)))
        )
        docs = await cursor.to_list(length=max(1, min(limit, 100)))

        # Convert ObjectId to string and format response
        articles = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            articles.append(doc)

        return {
            "articles": articles,
            "total": len(articles),
            "min_score": min_score,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error in score endpoint: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Internal server error", "message": str(e)}
        )


@app.get(f"{settings.api_v1_prefix}/news/nearby")
async def get_news_nearby(lat: float, lon: float, radius_km: float = 10.0, limit: int = 20):
    """Return articles within a specified radius of a location, ranked by distance."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return JSONResponse(status_code=400, content={"error": "Invalid latitude or longitude values"})
    
    if radius_km <= 0 or radius_km > 1000:
        return JSONResponse(status_code=400, content={"error": "Radius must be between 0 and 1000 km"})
    
    global articles_collection
    if articles_collection is None:
        return JSONResponse(status_code=503, content={"error": "Database not initialized"})

    try:
        # Convert radius from km to meters for MongoDB geospatial queries
        radius_meters = radius_km * 1000
        
        # Create geospatial query using $geoWithin with $centerSphere
        # $centerSphere uses radians, so we convert km to radians
        radius_radians = radius_km / 6378.1  # Earth's radius in km
        
        geospatial_query = {
            "location": {
                "$geoWithin": {
                    "$centerSphere": [[lon, lat], radius_radians]
                }
            }
        }
        
        # Use aggregation pipeline to calculate distance and sort by it
        pipeline = [
            {"$match": geospatial_query},
            {
                "$addFields": {
                    "distance_km": {
                        "$multiply": [
                            {
                                "$acos": {
                                    "$add": [
                                        {
                                            "$multiply": [
                                                {"$sin": {"$degreesToRadians": "$latitude"}},
                                                {"$sin": {"$degreesToRadians": lat}}
                                            ]
                                        },
                                        {
                                            "$multiply": [
                                                {"$multiply": [
                                                    {"$cos": {"$degreesToRadians": "$latitude"}},
                                                    {"$cos": {"$degreesToRadians": lat}}
                                                ]},
                                                {"$cos": {"$degreesToRadians": {"$subtract": ["$longitude", lon]}}}
                                            ]
                                        }
                                    ]
                                }
                            },
                            6378.1  # Earth's radius in km
                        ]
                    }
                }
            },
            {"$sort": {"distance_km": 1}},  # Sort by distance (closest first)
            {"$limit": max(1, min(limit, 100))}
        ]
        
        docs = await articles_collection.aggregate(pipeline).to_list(length=max(1, min(limit, 100)))

        # Convert ObjectId to string and format response
        articles = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            # Round distance to 2 decimal places for readability
            if "distance_km" in doc:
                doc["distance_km"] = round(doc["distance_km"], 2)
            articles.append(doc)

        return {
            "articles": articles,
            "total": len(articles),
            "location": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error in nearby endpoint: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Internal server error", "message": str(e)}
        )


@app.post(f"{settings.api_v1_prefix}/news/query")
async def smart_query_endpoint(request: Request):
    """Smart query endpoint that uses LLM to analyze queries and route to appropriate endpoints."""
    try:
        # Parse request body
        body = await request.json()
        
        # Validate required fields
        if "query" not in body:
            raise HTTPException(status_code=400, detail="Query is required")
        
        query = body["query"]
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Extract optional parameters
        location = body.get("location")
        limit = min(max(body.get("limit", 5), 1), 20)  # Between 1 and 20
        include_summary = body.get("include_summary", True)
        include_analysis = body.get("include_analysis", False)
        
        # Validate location if provided
        if location:
            lat = location.get("lat")
            lon = location.get("lon")
            if lat is None or lon is None:
                raise HTTPException(status_code=400, detail="Location must include lat and lon")
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise HTTPException(status_code=400, detail="Invalid latitude or longitude values")
        
        # Check if database is available
        global articles_collection
        if articles_collection is None:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        # Use LLM service for intelligent query analysis
        start_time = time.time()
        
        # Initialize LLM service with the provided API key
        cursor_api_key = "key_dcf872079f1f009d2fd8fc0d22726ac2173fd4f9da0eb93e9a94ddf0c4779f54"
        
        # Import and initialize LLM service
        try:
            from app.services.llm_service import CursorLLMService
            from app.services.query_analyzer import QueryAnalyzer
            
            llm_service = CursorLLMService(cursor_api_key)
            analyzer = QueryAnalyzer()
            
            # Analyze the query using LLM
            user_location = None
            if location:
                user_location = {"lat": location["lat"], "lon": location["lon"]}
            
            analysis_result = await analyzer.analyze_and_route(query, user_location)
            analysis = analysis_result["analysis"]
            routing_strategy = analysis_result["routing_strategy"]
            
            intent = analysis["intent"]
            parameters = analysis["parameters"]
            
        except Exception as e:
            print(f"LLM service error: {e}, falling back to keyword analysis")
            # Fallback to simple keyword analysis
            query_lower = query.lower()
            
            if any(word in query_lower for word in ["technology", "tech", "ai", "software"]):
                intent = "category"
                parameters = {"category": "technology"}
            elif any(word in query_lower for word in ["business", "economy", "finance", "market"]):
                intent = "category"
                parameters = {"category": "business"}
            elif any(word in query_lower for word in ["sports", "football", "cricket", "game"]):
                intent = "category"
                parameters = {"category": "sports"}
            elif any(word in query_lower for word in ["world", "international", "global"]):
                intent = "category"
                parameters = {"category": "world"}
            elif any(word in query_lower for word in ["entertainment", "movie", "music", "celebrity"]):
                intent = "category"
                parameters = {"category": "entertainment"}
            else:
                intent = "search"
                parameters = {"query": query}
            
            analysis = {
                "intent": intent,
                "entities": {"topics": [parameters.get("category", "general")]},
                "parameters": parameters,
                "confidence": 0.6,
                "reasoning": "Fallback keyword analysis"
            }
            
            routing_strategy = {
                "primary_endpoint": intent,
                "secondary_endpoints": [],
                "parameters": parameters,
                "strategy_type": "single",
                "confidence": 0.6
            }
        
        # Execute the query based on intent and parameters
        if intent == "category" and "category" in parameters:
            # Get articles by category
            category = parameters["category"]
            query_filter = {"category": {"$in": [category]}}
            cursor = articles_collection.find(query_filter).sort("publication_date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
        elif intent == "search" and "search_terms" in parameters:
            # Search using extracted search terms
            search_terms = " ".join(parameters["search_terms"])
            search_query = {
                "$or": [
                    {"title": {"$regex": search_terms, "$options": "i"}},
                    {"description": {"$regex": search_terms, "$options": "i"}}
                ]
            }
            cursor = articles_collection.find(search_query).sort("publication_date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
        elif intent == "source" and "source" in parameters:
            # Get articles by source
            source = parameters["source"]
            query_filter = {"source_name": {"$regex": source, "$options": "i"}}
            cursor = articles_collection.find(query_filter).sort("publication_date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
        elif intent == "score" and "min_score" in parameters:
            # Get articles by relevance score
            min_score = parameters["min_score"]
            query_filter = {"relevance_score": {"$gte": min_score}}
            cursor = articles_collection.find(query_filter).sort("relevance_score", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
        elif intent == "nearby" and "location" in parameters:
            # Get articles by location
            location_params = parameters["location"]
            lat = location_params.get("lat", 0.0)
            lon = location_params.get("lon", 0.0)
            radius_km = location_params.get("radius_km", 10.0)
            
            # Convert radius from km to radians
            radius_radians = radius_km / 6378.1
            
            geospatial_query = {
                "location": {
                    "$geoWithin": {
                        "$centerSphere": [[lon, lat], radius_radians]
                    }
                }
            }
            
            # Use aggregation to calculate distance and sort by it
            pipeline = [
                {"$match": geospatial_query},
                {
                    "$addFields": {
                        "distance_km": {
                            "$multiply": [
                                {
                                    "$acos": {
                                        "$add": [
                                            {
                                                "$multiply": [
                                                    {"$sin": {"$degreesToRadians": "$latitude"}},
                                                    {"$sin": {"$degreesToRadians": lat}}
                                                ]
                                            },
                                            {
                                                "$multiply": [
                                                    {"$multiply": [
                                                        {"$cos": {"$degreesToRadians": "$latitude"}},
                                                        {"$cos": {"$degreesToRadians": lat}}
                                                    ]},
                                                    {"$cos": {"$degreesToRadians": {"$subtract": ["$longitude", lon]}}}
                                                ]
                                            }
                                        ]
                                    }
                                },
                                6378.1
                            ]
                        }
                    }
                },
                {"$sort": {"distance_km": 1}},
                {"$limit": limit}
            ]
            
            docs = await articles_collection.aggregate(pipeline).to_list(length=limit)
        else:
            # Fallback to general search
            search_query = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            cursor = articles_collection.find(search_query).sort("publication_date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
        
        # Format articles
        articles = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            
            article = {
                "id": doc.get("id", "unknown"),
                "title": doc.get("title", "Unknown Title"),
                "description": doc.get("description", "No description available"),
                "url": doc.get("url", ""),
                "publication_date": doc.get("publication_date", ""),
                "source_name": doc.get("source_name", "Unknown Source"),
                "category": doc.get("category", []),
                "relevance_score": doc.get("relevance_score", 0.0),
                "latitude": doc.get("latitude"),
                "longitude": doc.get("longitude")
            }
            
            # Add LLM-generated summary if requested
            if include_summary:
                try:
                    # Use LLM service to generate summary
                    if 'llm_service' in locals():
                        summary = await llm_service.generate_summary(
                            doc.get('title', 'Unknown Title'),
                            doc.get('description', 'No description available')
                        )
                        article["llm_summary"] = summary
                    else:
                        # Fallback to mock summary
                        article["llm_summary"] = f"Summary: {doc.get('title', 'Unknown Title')} discusses important developments in the news industry."
                except Exception as e:
                    print(f"Error generating summary: {e}")
                    # Fallback to mock summary
                    article["llm_summary"] = f"Summary: {doc.get('title', 'Unknown Title')} discusses important developments in the news industry."
            
            articles.append(article)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = {
            "articles": articles,
            "total": len(articles),
            "query": query,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "cache_hit": False
        }
        
        # Add analysis details if requested
        if include_analysis:
            response["analysis"] = analysis
            response["routing_strategy"] = routing_strategy
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in smart query endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/news/test")
async def test_endpoint():
    """Test endpoint for API functionality."""
    return {
        "message": "API is working",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "total_articles": 2000,
            "categories": ["national", "sports", "world", "business", "entertainment"],
            "sources": ["Hindustan Times", "News18", "Reuters", "The Indian Express"]
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    print(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
