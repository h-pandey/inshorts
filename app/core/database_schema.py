"""
Database schema definitions and index creation.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from typing import List, Dict, Any
import logging

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseSchema:
    """Database schema and index management."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
    
    async def create_indexes(self) -> None:
        """Create all necessary indexes for optimal performance."""
        logger.info("Creating database indexes...")
        
        # Articles collection indexes
        await self._create_article_indexes()
        
        # User events collection indexes
        await self._create_user_event_indexes()
        
        logger.info("Database indexes created successfully")
    
    async def _create_article_indexes(self) -> None:
        """Create indexes for articles collection."""
        collection = self.database[settings.mongodb_collection]
        
        indexes = [
            # Category queries - compound index for category and publication date
            {
                "keys": [("category", ASCENDING), ("publication_date", DESCENDING)],
                "name": "category_publication_date_idx"
            },
            
            # Source queries - compound index for source and publication date
            {
                "keys": [("source_name", ASCENDING), ("publication_date", DESCENDING)],
                "name": "source_publication_date_idx"
            },
            
            # Score-based queries - index for relevance score
            {
                "keys": [("relevance_score", DESCENDING)],
                "name": "relevance_score_idx"
            },
            
            # Geospatial queries - 2dsphere index for location
            {
                "keys": [("location", "2dsphere")],
                "name": "location_2dsphere_idx"
            },
            
            # Full-text search - text index for title and description
            {
                "keys": [("title", TEXT), ("description", TEXT)],
                "name": "title_description_text_idx"
            },
            
            # Publication date - for sorting by recency
            {
                "keys": [("publication_date", DESCENDING)],
                "name": "publication_date_idx"
            },
            
            # URL uniqueness - ensure no duplicate articles
            {
                "keys": [("url", ASCENDING)],
                "name": "url_unique_idx",
                "unique": True
            },
            
            # Source and category - for filtering
            {
                "keys": [("source_name", ASCENDING), ("category", ASCENDING)],
                "name": "source_category_idx"
            },
            
            # Created/updated timestamps - for data management
            {
                "keys": [("created_at", DESCENDING)],
                "name": "created_at_idx"
            },
            {
                "keys": [("updated_at", DESCENDING)],
                "name": "updated_at_idx"
            }
        ]
        
        for index_spec in indexes:
            try:
                await collection.create_index(
                    index_spec["keys"],
                    name=index_spec["name"],
                    unique=index_spec.get("unique", False),
                    background=True  # Create indexes in background
                )
                logger.info(f"Created index: {index_spec['name']}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_spec['name']}: {e}")
    
    async def _create_user_event_indexes(self) -> None:
        """Create indexes for user_events collection."""
        collection = self.database["user_events"]
        
        indexes = [
            # Article and timestamp - for trending calculations
            {
                "keys": [("article_id", ASCENDING), ("timestamp", DESCENDING)],
                "name": "article_timestamp_idx"
            },
            
            # User and timestamp - for user activity tracking
            {
                "keys": [("user_id", ASCENDING), ("timestamp", DESCENDING)],
                "name": "user_timestamp_idx"
            },
            
            # Location cluster and timestamp - for location-based trending
            {
                "keys": [("location_cluster", ASCENDING), ("timestamp", DESCENDING)],
                "name": "location_cluster_timestamp_idx"
            },
            
            # Event type and timestamp - for event analysis
            {
                "keys": [("event_type", ASCENDING), ("timestamp", DESCENDING)],
                "name": "event_type_timestamp_idx"
            },
            
            # TTL index - auto-delete old events (30 days)
            {
                "keys": [("timestamp", ASCENDING)],
                "name": "timestamp_ttl_idx",
                "expireAfterSeconds": 2592000  # 30 days
            },
            
            # Compound index for trending queries
            {
                "keys": [
                    ("location_cluster", ASCENDING),
                    ("event_type", ASCENDING),
                    ("timestamp", DESCENDING)
                ],
                "name": "trending_compound_idx"
            },
            
            # User location - for geographic analysis
            {
                "keys": [("user_location", "2dsphere")],
                "name": "user_location_2dsphere_idx"
            }
        ]
        
        for index_spec in indexes:
            try:
                await collection.create_index(
                    index_spec["keys"],
                    name=index_spec["name"],
                    expireAfterSeconds=index_spec.get("expireAfterSeconds"),
                    background=True
                )
                logger.info(f"Created index: {index_spec['name']}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_spec['name']}: {e}")
    
    async def get_index_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get information about existing indexes."""
        collections = [settings.mongodb_collection, "user_events"]
        index_info = {}
        
        for collection_name in collections:
            collection = self.database[collection_name]
            indexes = await collection.list_indexes().to_list(length=None)
            index_info[collection_name] = indexes
        
        return index_info
    
    async def drop_indexes(self, collection_name: str = None) -> None:
        """Drop indexes (use with caution)."""
        if collection_name:
            collections = [collection_name]
        else:
            collections = [settings.mongodb_collection, "user_events"]
        
        for coll_name in collections:
            collection = self.database[coll_name]
            try:
                # Drop all indexes except _id
                await collection.drop_indexes()
                logger.info(f"Dropped indexes for collection: {coll_name}")
            except Exception as e:
                logger.error(f"Failed to drop indexes for {coll_name}: {e}")


async def setup_database_schema(database: AsyncIOMotorDatabase) -> None:
    """Setup database schema and indexes."""
    schema = DatabaseSchema(database)
    await schema.create_indexes()
