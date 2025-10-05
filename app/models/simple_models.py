"""
Simple models without Pydantic for initial testing.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime


class SimpleArticle:
    """Simple article model without Pydantic validation."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.url = kwargs.get('url', '')
        self.publication_date = kwargs.get('publication_date')
        self.source_name = kwargs.get('source_name', '')
        self.category = kwargs.get('category', [])
        self.relevance_score = kwargs.get('relevance_score', 0.0)
        self.latitude = kwargs.get('latitude', 0.0)
        self.longitude = kwargs.get('longitude', 0.0)
        self.llm_summary = kwargs.get('llm_summary')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'publication_date': self.publication_date,
            'source_name': self.source_name,
            'category': self.category,
            'relevance_score': self.relevance_score,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'llm_summary': self.llm_summary,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimpleArticle':
        """Create from dictionary."""
        return cls(**data)


class SimpleQuery:
    """Simple query model without Pydantic validation."""
    
    def __init__(self, **kwargs):
        self.query = kwargs.get('query', '')
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.radius_km = kwargs.get('radius_km')
        self.limit = kwargs.get('limit', 5)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius_km': self.radius_km,
            'limit': self.limit
        }
