"""
User event models for trending calculation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """User event types."""
    
    VIEW = "view"
    CLICK = "click"
    SHARE = "share"
    LIKE = "like"
    DISLIKE = "dislike"


class UserEventBase(BaseModel):
    """Base user event model."""
    
    user_id: str = Field(..., min_length=1, max_length=100)
    article_id: str = Field(..., min_length=1, max_length=100)
    event_type: EventType
    timestamp: datetime
    user_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    user_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    location_cluster: Optional[str] = Field(None, max_length=50)


class UserEventCreate(UserEventBase):
    """User event creation model."""
    pass


class UserEvent(UserEventBase):
    """User event model with ID."""
    
    id: str = Field(..., alias="_id")
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
