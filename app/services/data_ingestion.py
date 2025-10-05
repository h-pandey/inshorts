"""
Data ingestion service for loading news data into MongoDB.
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import get_logger, log_database_operation, log_performance
from app.models.article import ArticleCreate
from app.core.database import database

logger = get_logger(__name__)


class DataIngestionService:
    """Service for ingesting news data into MongoDB."""
    
    def __init__(self):
        self.collection: Optional[AsyncIOMotorCollection] = None
        self.batch_size = 100  # Process articles in batches
    
    async def initialize(self) -> None:
        """Initialize the data ingestion service."""
        if not database.database:
            await database.connect()
        
        self.collection = database.get_collection(settings.mongodb_collection)
        logger.info("Data ingestion service initialized")
    
    async def load_news_data(self, file_path: str = "news_data.json") -> Dict[str, Any]:
        """Load news data from JSON file."""
        start_time = datetime.now()
        
        try:
            logger.info(f"Loading news data from {file_path}")
            
            # Check if file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"News data file not found: {file_path}")
            
            # Load JSON data
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            if not isinstance(raw_data, list):
                raise ValueError("News data must be a list of articles")
            
            logger.info(f"Loaded {len(raw_data)} articles from file")
            
            # Process and validate data
            processed_data = await self._process_articles(raw_data)
            
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            log_performance("data_load", load_time, articles_count=len(processed_data))
            
            return {
                "total_articles": len(raw_data),
                "processed_articles": len(processed_data),
                "load_time_ms": load_time,
                "file_path": file_path
            }
            
        except Exception as e:
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(
                f"Failed to load news data: {e}",
                file_path=file_path,
                load_time_ms=load_time,
                exc_info=True
            )
            raise
    
    async def _process_articles(self, raw_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate raw article data."""
        processed_articles = []
        validation_errors = []
        
        logger.info(f"Processing {len(raw_articles)} articles")
        
        for i, article_data in enumerate(raw_articles):
            try:
                # Transform the data to match our schema
                processed_article = await self._transform_article(article_data)
                
                # Validate using Pydantic model
                article_model = ArticleCreate(**processed_article)
                processed_articles.append(article_model.dict())
                
                # Log progress for large datasets
                if (i + 1) % 500 == 0:
                    logger.info(f"Processed {i + 1}/{len(raw_articles)} articles")
                
            except ValidationError as e:
                validation_errors.append({
                    "index": i,
                    "article_id": article_data.get("id", "unknown"),
                    "error": str(e)
                })
                logger.warning(f"Validation error for article {i}: {e}")
            except Exception as e:
                validation_errors.append({
                    "index": i,
                    "article_id": article_data.get("id", "unknown"),
                    "error": str(e)
                })
                logger.error(f"Processing error for article {i}: {e}")
        
        if validation_errors:
            logger.warning(f"Found {len(validation_errors)} validation errors")
            # Log first few errors for debugging
            for error in validation_errors[:5]:
                logger.debug(f"Validation error: {error}")
        
        logger.info(
            f"Article processing completed",
            total_articles=len(raw_articles),
            processed_articles=len(processed_articles),
            validation_errors=len(validation_errors)
        )
        
        return processed_articles
    
    async def _transform_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw article data to match our schema."""
        # Convert publication_date to datetime if it's a string
        publication_date = article_data.get("publication_date")
        if isinstance(publication_date, str):
            try:
                publication_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            except ValueError:
                # Fallback to current time if parsing fails
                publication_date = datetime.now()
        
        # Create geospatial location object
        location = {
            "type": "Point",
            "coordinates": [
                float(article_data.get("longitude", 0)),
                float(article_data.get("latitude", 0))
            ]
        }
        
        # Transform the article data
        transformed = {
            "title": article_data.get("title", ""),
            "description": article_data.get("description", ""),
            "url": article_data.get("url", ""),
            "publication_date": publication_date,
            "source_name": article_data.get("source_name", ""),
            "category": article_data.get("category", []),
            "relevance_score": float(article_data.get("relevance_score", 0.0)),
            "latitude": float(article_data.get("latitude", 0.0)),
            "longitude": float(article_data.get("longitude", 0.0)),
            "location": location,
            "llm_summary": None,  # Will be generated later
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return transformed
    
    async def ingest_articles(self, articles: List[Dict[str, Any]], 
                            clear_existing: bool = False) -> Dict[str, Any]:
        """Ingest articles into MongoDB."""
        if not self.collection:
            await self.initialize()
        
        start_time = datetime.now()
        
        try:
            # Clear existing data if requested
            if clear_existing:
                logger.info("Clearing existing articles from collection")
                await self.collection.delete_many({})
                log_database_operation("delete_many", settings.mongodb_collection, 
                                     filter_criteria="all")
            
            # Insert articles in batches
            total_inserted = 0
            total_errors = 0
            
            for i in range(0, len(articles), self.batch_size):
                batch = articles[i:i + self.batch_size]
                
                try:
                    # Prepare batch for insertion
                    batch_docs = []
                    for article in batch:
                        # Add MongoDB _id if not present
                        if "_id" not in article:
                            article["_id"] = ObjectId()
                        batch_docs.append(article)
                    
                    # Insert batch
                    result = await self.collection.insert_many(batch_docs)
                    total_inserted += len(result.inserted_ids)
                    
                    log_database_operation(
                        "insert_many", 
                        settings.mongodb_collection,
                        batch_size=len(batch_docs),
                        inserted_count=len(result.inserted_ids)
                    )
                    
                    logger.info(f"Inserted batch {i//self.batch_size + 1}: {len(result.inserted_ids)} articles")
                    
                except Exception as e:
                    total_errors += len(batch)
                    logger.error(f"Failed to insert batch {i//self.batch_size + 1}: {e}")
            
            # Create indexes after data insertion
            await self._create_indexes()
            
            ingestion_time = (datetime.now() - start_time).total_seconds() * 1000
            log_performance("data_ingestion", ingestion_time, 
                          articles_processed=len(articles),
                          articles_inserted=total_inserted)
            
            result = {
                "total_articles": len(articles),
                "inserted_articles": total_inserted,
                "failed_articles": total_errors,
                "ingestion_time_ms": ingestion_time,
                "clear_existing": clear_existing
            }
            
            logger.info(
                "Data ingestion completed",
                **result
            )
            
            return result
            
        except Exception as e:
            ingestion_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(
                f"Data ingestion failed: {e}",
                ingestion_time_ms=ingestion_time,
                exc_info=True
            )
            raise
    
    async def _create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        try:
            logger.info("Creating database indexes")
            
            # Import and use the database schema setup
            from app.core.database_schema import setup_database_schema
            await setup_database_schema(database.database)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}", exc_info=True)
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.collection:
            await self.initialize()
        
        try:
            # Get basic stats
            total_count = await self.collection.count_documents({})
            
            # Get category distribution
            category_pipeline = [
                {"$unwind": "$category"},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            category_stats = await self.collection.aggregate(category_pipeline).to_list(length=10)
            
            # Get source distribution
            source_pipeline = [
                {"$group": {"_id": "$source_name", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            source_stats = await self.collection.aggregate(source_pipeline).to_list(length=10)
            
            # Get date range
            date_pipeline = [
                {"$group": {
                    "_id": None,
                    "min_date": {"$min": "$publication_date"},
                    "max_date": {"$max": "$publication_date"}
                }}
            ]
            date_stats = await self.collection.aggregate(date_pipeline).to_list(length=1)
            
            stats = {
                "total_articles": total_count,
                "top_categories": category_stats,
                "top_sources": source_stats,
                "date_range": date_stats[0] if date_stats else None
            }
            
            logger.info("Collection statistics retrieved", total_articles=total_count)
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}", exc_info=True)
            raise


# Global service instance
data_ingestion_service = DataIngestionService()
