"""
Article data models.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class ArticleBase(BaseModel):
    """Base article model."""
    
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=2000)
    url: str = Field(..., regex=r'^https?://')
    publication_date: datetime
    source_name: str = Field(..., min_length=1, max_length=100)
    category: List[str] = Field(..., min_items=1)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    llm_summary: Optional[str] = Field(None, max_length=1000)


class ArticleCreate(ArticleBase):
    """Article creation model."""
    pass


class Article(ArticleBase):
    """Article model with ID."""
    
    id: str = Field(..., alias="_id")
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class ArticleResponse(ArticleBase):
    """Article response model for API."""
    
    id: str
    distance_km: Optional[float] = None  # For nearby queries
    trending_score: Optional[float] = None  # For trending queries
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArticleListResponse(BaseModel):
    """Response model for article lists."""
    
    articles: List[ArticleResponse]
    total_count: int
    page: int = 1
    limit: int = 5
    query_type: str
    query_params: dict
