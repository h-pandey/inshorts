"""
Database connection and configuration with enhanced logging.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from typing import Optional
import asyncio
import time
from datetime import datetime

from .config import settings
from .logging import get_logger, log_database_operation, log_performance

logger = get_logger(__name__)


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """Connect to MongoDB with enhanced logging."""
        start_time = time.time()
        
        try:
            logger.info(
                "Connecting to MongoDB",
                url=settings.mongodb_url,
                database=settings.mongodb_database,
                max_connections=settings.max_connections
            )
            
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=settings.max_connections,
                serverSelectionTimeoutMS=settings.connection_timeout * 1000,
            )
            self.database = self.client[settings.mongodb_database]
            
            # Test connection
            await self.client.admin.command('ping')
            
            connection_time = (time.time() - start_time) * 1000
            log_performance("mongodb_connection", connection_time)
            
            logger.info(
                "Successfully connected to MongoDB",
                database=settings.mongodb_database,
                connection_time_ms=connection_time
            )
            
        except Exception as e:
            connection_time = (time.time() - start_time) * 1000
            logger.error(
                "Failed to connect to MongoDB",
                error=str(e),
                connection_time_ms=connection_time,
                exc_info=True
            )
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str = None):
        """Get a collection from the database."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        collection_name = collection_name or settings.mongodb_collection
        return self.database[collection_name]


# Global database instance
database = Database()
