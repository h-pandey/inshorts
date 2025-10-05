"""Data models and schemas."""

from .article import Article, ArticleResponse, ArticleCreate
from .query import NewsQuery, QueryResponse, QueryAnalysis
from .user_event import UserEvent, UserEventCreate
from .trending import TrendingScore, TrendingResponse

__all__ = [
    "Article",
    "ArticleResponse", 
    "ArticleCreate",
    "NewsQuery",
    "QueryResponse",
    "QueryAnalysis",
    "UserEvent",
    "UserEventCreate",
    "TrendingScore",
    "TrendingResponse",
]
