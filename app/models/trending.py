"""
Trending news models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TrendingScore(BaseModel):
    """Trending score calculation model."""
    
    article_id: str
    interaction_score: float = Field(..., ge=0.0)
    recency_score: float = Field(..., ge=0.0)
    location_score: float = Field(..., ge=0.0)
    total_score: float = Field(..., ge=0.0)
    interaction_count: int = Field(..., ge=0)
    last_interaction: Optional[str] = None


class TrendingResponse(BaseModel):
    """Response model for trending news."""
    
    articles: List[dict]  # Will be ArticleResponse objects
    total_count: int
    location_cluster: str
    cache_timestamp: str
    update_interval_seconds: int
