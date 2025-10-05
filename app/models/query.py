"""
Query models for news retrieval.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class QueryAnalysis(BaseModel):
    """LLM analysis of user query."""
    
    entities: List[str] = Field(default_factory=list)
    intent: str = Field(..., description="Query intent: category, search, nearby, source, score")
    location: Optional[Dict[str, float]] = Field(None, description="Location with lat/lon")
    search_terms: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class NewsQuery(BaseModel):
    """News query model."""
    
    query: str = Field(..., min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    radius_km: Optional[float] = Field(None, ge=0.1, le=100.0)
    limit: int = Field(5, ge=1, le=50)
    
    @validator("radius_km")
    def validate_radius_with_location(cls, v, values):
        """Validate radius is provided when location is specified."""
        if (values.get("latitude") is not None or values.get("longitude") is not None) and v is None:
            raise ValueError("Radius must be provided when location is specified")
        return v


class QueryResponse(BaseModel):
    """Response model for smart queries."""
    
    analysis: QueryAnalysis
    articles: List[dict]  # Will be ArticleResponse objects
    total_count: int
    query_type: str
    execution_time_ms: float
