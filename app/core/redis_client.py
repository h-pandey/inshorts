"""
Redis connection and configuration.
"""

import redis.asyncio as redis
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis connection manager."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=settings.connection_timeout,
                socket_timeout=settings.request_timeout,
            )
            
            # Test connection
            await self.client.ping()
            logger.info(f"Connected to Redis: {settings.redis_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.client:
            raise RuntimeError("Redis not connected")
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set value in Redis with optional TTL."""
        if not self.client:
            raise RuntimeError("Redis not connected")
        
        ttl = ttl or settings.cache_ttl
        return await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self.client:
            raise RuntimeError("Redis not connected")
        return await self.client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.client:
            raise RuntimeError("Redis not connected")
        return await self.client.exists(key) > 0


# Global Redis instance
redis_client = RedisClient()
