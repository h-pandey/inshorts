"""
Application configuration management.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_name: str = "Contextual News API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "news_db"
    mongodb_collection: str = "articles"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 500
    
    # Cursor API Configuration
    cursor_api_key: Optional[str] = None
    cursor_base_url: str = "https://api.cursor.sh"
    cursor_model: str = "gpt-4"
    cursor_max_tokens: int = 1000
    cursor_temperature: float = 0.3
    
    # Performance Configuration
    max_connections: int = 100
    connection_timeout: int = 30
    request_timeout: int = 60
    
    # Cache Configuration
    cache_ttl: int = 3600  # 1 hour in seconds
    trending_cache_ttl: int = 900  # 15 minutes in seconds
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 20
    
    # Geospatial Configuration
    default_radius_km: float = 10.0
    max_radius_km: float = 100.0
    grid_size_km: float = 5.0
    
    # Trending Configuration
    trending_update_interval: int = 900  # 15 minutes in seconds
    trending_decay_factor: float = 0.1
    trending_interaction_weight: float = 1.0
    trending_recency_weight: float = 0.5
    trending_location_weight: float = 0.3
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
