"""
Smart Query Service for orchestrating LLM analysis and API endpoint calls.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.query_models import (
    SmartQueryRequest, SmartQueryResponse, ArticleSummaryModel,
    QueryAnalysisModel, RoutingStrategyModel, ErrorResponse
)
from .llm_service import get_llm_service
from .query_analyzer import get_query_analyzer

logger = logging.getLogger(__name__)


class SmartQueryService:
    """Service for processing smart queries and orchestrating API calls."""
    
    def __init__(self):
        self.llm_service = get_llm_service()
        self.query_analyzer = get_query_analyzer()
    
    async def process_smart_query(
        self, 
        request: SmartQueryRequest,
        articles_collection
    ) -> SmartQueryResponse:
        """
        Process a smart query using LLM analysis and return enriched results.
        
        Args:
            request: Smart query request
            articles_collection: MongoDB articles collection
            
        Returns:
            SmartQueryResponse with articles and analysis
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze the query
            logger.info(f"Processing smart query: {request.query[:50]}...")
            
            user_location = None
            if request.location:
                user_location = {"lat": request.location.lat, "lon": request.location.lon}
            
            # Get query analysis and routing strategy
            analysis_result = await self.query_analyzer.analyze_and_route(
                request.query, user_location
            )
            
            # Step 2: Execute the routing strategy
            articles = await self._execute_routing_strategy(
                analysis_result["routing_strategy"],
                articles_collection,
                request.limit
            )
            
            # Step 3: Enrich articles with summaries if requested
            if request.include_summary and self.llm_service:
                articles = await self._enrich_with_summaries(articles)
            
            # Step 4: Format response
            processing_time = (time.time() - start_time) * 1000
            
            response = SmartQueryResponse(
                articles=articles,
                total=len(articles),
                query=request.query,
                analysis=QueryAnalysisModel(**analysis_result["analysis"]) if request.include_analysis else None,
                routing_strategy=RoutingStrategyModel(**analysis_result["routing_strategy"]) if request.include_analysis else None,
                processing_time_ms=round(processing_time, 2),
                timestamp=datetime.now().isoformat(),
                cache_hit=False
            )
            
            logger.info(f"Smart query processed successfully in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error processing smart query: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            # Return error response
            return SmartQueryResponse(
                articles=[],
                total=0,
                query=request.query,
                analysis=None,
                routing_strategy=None,
                processing_time_ms=round(processing_time, 2),
                timestamp=datetime.now().isoformat(),
                cache_hit=False
            )
    
    async def _execute_routing_strategy(
        self, 
        strategy: Dict[str, Any], 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Execute the routing strategy and fetch articles."""
        try:
            primary_endpoint = strategy.get("primary_endpoint", "search")
            parameters = strategy.get("parameters", {})
            strategy_type = strategy.get("strategy_type", "single")
            
            if strategy_type == "single":
                # Single endpoint strategy
                articles = await self._call_single_endpoint(
                    primary_endpoint, parameters, articles_collection, limit
                )
            elif strategy_type == "multiple":
                # Multiple endpoint strategy
                articles = await self._call_multiple_endpoints(
                    strategy, articles_collection, limit
                )
            else:
                # Fallback strategy
                articles = await self._call_single_endpoint(
                    "search", {"query": "news"}, articles_collection, limit
                )
            
            return articles
            
        except Exception as e:
            logger.error(f"Error executing routing strategy: {e}")
            return []
    
    async def _call_single_endpoint(
        self, 
        endpoint: str, 
        parameters: Dict[str, Any], 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Call a single API endpoint."""
        try:
            if endpoint == "category":
                return await self._get_articles_by_category(
                    parameters.get("category", "general"), 
                    articles_collection, 
                    limit
                )
            elif endpoint == "search":
                return await self._get_articles_by_search(
                    parameters.get("query", ""), 
                    articles_collection, 
                    limit
                )
            elif endpoint == "source":
                return await self._get_articles_by_source(
                    parameters.get("source", ""), 
                    articles_collection, 
                    limit
                )
            elif endpoint == "score":
                return await self._get_articles_by_score(
                    parameters.get("min_score", 0.7), 
                    articles_collection, 
                    limit
                )
            elif endpoint == "nearby":
                return await self._get_articles_by_location(
                    parameters.get("lat", 0.0),
                    parameters.get("lon", 0.0),
                    parameters.get("radius_km", 10.0),
                    articles_collection,
                    limit
                )
            else:
                # Default to search
                return await self._get_articles_by_search(
                    "news", articles_collection, limit
                )
                
        except Exception as e:
            logger.error(f"Error calling endpoint {endpoint}: {e}")
            return []
    
    async def _call_multiple_endpoints(
        self, 
        strategy: Dict[str, Any], 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Call multiple endpoints and combine results."""
        try:
            all_articles = []
            
            # Call primary endpoint
            primary_endpoint = strategy.get("primary_endpoint", "search")
            primary_params = strategy.get("parameters", {})
            primary_articles = await self._call_single_endpoint(
                primary_endpoint, primary_params, articles_collection, limit // 2
            )
            all_articles.extend(primary_articles)
            
            # Call secondary endpoints
            secondary_endpoints = strategy.get("secondary_endpoints", [])
            remaining_limit = limit - len(all_articles)
            
            for endpoint_config in secondary_endpoints:
                if remaining_limit <= 0:
                    break
                    
                endpoint = endpoint_config.get("endpoint", "search")
                params = endpoint_config.get("parameters", {})
                endpoint_limit = min(remaining_limit, 3)  # Max 3 per secondary endpoint
                
                secondary_articles = await self._call_single_endpoint(
                    endpoint, params, articles_collection, endpoint_limit
                )
                all_articles.extend(secondary_articles)
                remaining_limit -= len(secondary_articles)
            
            # Remove duplicates and limit results
            unique_articles = self._remove_duplicate_articles(all_articles)
            return unique_articles[:limit]
            
        except Exception as e:
            logger.error(f"Error calling multiple endpoints: {e}")
            return []
    
    async def _get_articles_by_category(
        self, 
        category: str, 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Get articles by category."""
        try:
            query = {"category": {"$in": [category]}}
            cursor = articles_collection.find(query).sort("publication_date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            return [self._doc_to_article_model(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting articles by category: {e}")
            return []
    
    async def _get_articles_by_search(
        self, 
        search_query: str, 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Get articles by text search."""
        try:
            # Simple text search in title and description
            query = {
                "$or": [
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
            # Use aggregation to calculate text matching score
            pipeline = [
                {"$match": query},
                {
                    "$addFields": {
                        "text_score": {
                            "$add": [
                                {
                                    "$cond": [
                                        {"$regexMatch": {"input": "$title", "regex": search_query, "options": "i"}},
                                        2, 0
                                    ]
                                },
                                {
                                    "$cond": [
                                        {"$regexMatch": {"input": "$description", "regex": search_query, "options": "i"}},
                                        1, 0
                                    ]
                                }
                            ]
                        }
                    }
                },
                {"$sort": {"text_score": -1, "relevance_score": -1}},
                {"$limit": limit}
            ]
            
            docs = await articles_collection.aggregate(pipeline).to_list(length=limit)
            return [self._doc_to_article_model(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting articles by search: {e}")
            return []
    
    async def _get_articles_by_source(
        self, 
        source: str, 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Get articles by source."""
        try:
            query = {"source_name": {"$regex": source, "$options": "i"}}
            cursor = articles_collection.find(query).sort("publication_date", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            return [self._doc_to_article_model(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting articles by source: {e}")
            return []
    
    async def _get_articles_by_score(
        self, 
        min_score: float, 
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Get articles by relevance score."""
        try:
            query = {"relevance_score": {"$gte": min_score}}
            cursor = articles_collection.find(query).sort("relevance_score", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            return [self._doc_to_article_model(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting articles by score: {e}")
            return []
    
    async def _get_articles_by_location(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float,
        articles_collection,
        limit: int
    ) -> List[ArticleSummaryModel]:
        """Get articles by location."""
        try:
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
            return [self._doc_to_article_model(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting articles by location: {e}")
            return []
    
    async def _enrich_with_summaries(self, articles: List[ArticleSummaryModel]) -> List[ArticleSummaryModel]:
        """Enrich articles with LLM-generated summaries."""
        if not self.llm_service:
            return articles
        
        try:
            # Process articles in parallel for better performance
            tasks = []
            for article in articles:
                task = self._generate_article_summary(article)
                tasks.append(task)
            
            # Wait for all summaries to complete
            enriched_articles = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out any exceptions and return valid articles
            valid_articles = []
            for article in enriched_articles:
                if isinstance(article, ArticleSummaryModel):
                    valid_articles.append(article)
                else:
                    logger.warning(f"Failed to generate summary for article: {article}")
            
            return valid_articles
            
        except Exception as e:
            logger.error(f"Error enriching articles with summaries: {e}")
            return articles
    
    async def _generate_article_summary(self, article: ArticleSummaryModel) -> ArticleSummaryModel:
        """Generate summary for a single article."""
        try:
            summary = await self.llm_service.generate_summary(article.title, article.description)
            article.llm_summary = summary
            return article
        except Exception as e:
            logger.warning(f"Failed to generate summary for article {article.id}: {e}")
            return article
    
    def _doc_to_article_model(self, doc: Dict[str, Any]) -> ArticleSummaryModel:
        """Convert MongoDB document to ArticleSummaryModel."""
        try:
            # Convert ObjectId to string
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            
            # Round distance if present
            if "distance_km" in doc:
                doc["distance_km"] = round(doc["distance_km"], 2)
            
            return ArticleSummaryModel(**doc)
        except Exception as e:
            logger.error(f"Error converting document to article model: {e}")
            # Return a minimal article model
            return ArticleSummaryModel(
                id=doc.get("id", "unknown"),
                title=doc.get("title", "Unknown Title"),
                description=doc.get("description", "No description available"),
                url=doc.get("url", ""),
                publication_date=doc.get("publication_date", ""),
                source_name=doc.get("source_name", "Unknown Source"),
                category=doc.get("category", []),
                relevance_score=doc.get("relevance_score", 0.0),
                latitude=doc.get("latitude"),
                longitude=doc.get("longitude"),
                distance_km=doc.get("distance_km")
            )
    
    def _remove_duplicate_articles(self, articles: List[ArticleSummaryModel]) -> List[ArticleSummaryModel]:
        """Remove duplicate articles based on ID."""
        seen_ids = set()
        unique_articles = []
        
        for article in articles:
            if article.id not in seen_ids:
                seen_ids.add(article.id)
                unique_articles.append(article)
        
        return unique_articles


# Global smart query service instance
smart_query_service: Optional[SmartQueryService] = None


def get_smart_query_service() -> Optional[SmartQueryService]:
    """Get the global smart query service instance."""
    return smart_query_service


def initialize_smart_query_service() -> SmartQueryService:
    """Initialize the global smart query service."""
    global smart_query_service
    smart_query_service = SmartQueryService()
    logger.info("Smart query service initialized")
    return smart_query_service
