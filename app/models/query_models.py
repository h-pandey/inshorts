"""
Pydantic models for smart query endpoint requests and responses.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class LocationModel(BaseModel):
    """Location model for user location."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")


class SmartQueryRequest(BaseModel):
    """Request model for smart query endpoint."""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")
    location: Optional[LocationModel] = Field(None, description="User location (optional)")
    limit: int = Field(5, ge=1, le=20, description="Maximum number of articles to return")
    include_summary: bool = Field(True, description="Whether to include LLM-generated summaries")
    include_analysis: bool = Field(False, description="Whether to include query analysis details")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query content."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class QueryAnalysisModel(BaseModel):
    """Model for query analysis results."""
    intent: str = Field(..., description="Detected intent (category, search, source, score, nearby, mixed)")
    entities: Dict[str, List[str]] = Field(..., description="Extracted entities")
    parameters: Dict[str, Any] = Field(..., description="Extracted parameters")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence score")
    reasoning: str = Field(..., description="Explanation of analysis")


class RoutingStrategyModel(BaseModel):
    """Model for routing strategy."""
    primary_endpoint: str = Field(..., description="Primary API endpoint to use")
    secondary_endpoints: List[Dict[str, Any]] = Field(default_factory=list, description="Secondary endpoints")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the endpoint")
    strategy_type: str = Field(..., description="Strategy type (single, multiple, fallback)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Routing confidence score")


class ArticleSummaryModel(BaseModel):
    """Model for article with summary."""
    id: str = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    description: str = Field(..., description="Article description")
    url: str = Field(..., description="Article URL")
    publication_date: str = Field(..., description="Publication date")
    source_name: str = Field(..., description="Source name")
    category: List[str] = Field(..., description="Article categories")
    relevance_score: float = Field(..., description="Relevance score")
    latitude: Optional[float] = Field(None, description="Article latitude")
    longitude: Optional[float] = Field(None, description="Article longitude")
    distance_km: Optional[float] = Field(None, description="Distance from user location (if applicable)")
    llm_summary: Optional[str] = Field(None, description="LLM-generated summary")


class SmartQueryResponse(BaseModel):
    """Response model for smart query endpoint."""
    articles: List[ArticleSummaryModel] = Field(..., description="List of articles")
    total: int = Field(..., description="Total number of articles returned")
    query: str = Field(..., description="Original query")
    analysis: Optional[QueryAnalysisModel] = Field(None, description="Query analysis details")
    routing_strategy: Optional[RoutingStrategyModel] = Field(None, description="Routing strategy used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="Response timestamp")
    cache_hit: bool = Field(False, description="Whether response was served from cache")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")
