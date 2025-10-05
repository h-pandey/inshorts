"""
Query Analysis Service for processing user queries and routing to appropriate endpoints.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Service for analyzing user queries and determining the best API strategy."""
    
    def __init__(self):
        self.llm_service = get_llm_service()
    
    async def analyze_and_route(self, user_query: str, user_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analyze user query and determine the best routing strategy.
        
        Args:
            user_query: The user's natural language query
            user_location: Optional user location with lat/lon
            
        Returns:
            Dict containing analysis and routing information
        """
        try:
            # Get LLM analysis
            if self.llm_service:
                analysis = await self.llm_service.analyze_query(user_query, user_location)
            else:
                analysis = self._fallback_analysis(user_query)
            
            # Determine routing strategy
            routing_strategy = self._determine_routing_strategy(analysis)
            
            # Create response
            result = {
                "analysis": analysis,
                "routing_strategy": routing_strategy,
                "timestamp": datetime.now().isoformat(),
                "query": user_query
            }
            
            logger.info(f"Query analysis completed: {analysis['intent']} with confidence {analysis['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return self._create_error_response(user_query, str(e))
    
    def _determine_routing_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best routing strategy based on analysis."""
        intent = analysis.get("intent", "search")
        parameters = analysis.get("parameters", {})
        confidence = analysis.get("confidence", 0.0)
        
        strategy = {
            "primary_endpoint": None,
            "secondary_endpoints": [],
            "parameters": {},
            "confidence": confidence,
            "strategy_type": "single"  # single, multiple, fallback
        }
        
        if intent == "category":
            strategy["primary_endpoint"] = "category"
            strategy["parameters"] = {
                "category": parameters.get("category", "general"),
                "limit": 5
            }
            strategy["strategy_type"] = "single"
            
        elif intent == "search":
            strategy["primary_endpoint"] = "search"
            strategy["parameters"] = {
                "query": " ".join(parameters.get("search_terms", [])),
                "limit": 5
            }
            strategy["strategy_type"] = "single"
            
        elif intent == "source":
            strategy["primary_endpoint"] = "source"
            strategy["parameters"] = {
                "source": parameters.get("source", ""),
                "limit": 5
            }
            strategy["strategy_type"] = "single"
            
        elif intent == "score":
            strategy["primary_endpoint"] = "score"
            strategy["parameters"] = {
                "min_score": parameters.get("min_score", 0.7),
                "limit": 5
            }
            strategy["strategy_type"] = "single"
            
        elif intent == "nearby":
            location = parameters.get("location", {})
            strategy["primary_endpoint"] = "nearby"
            strategy["parameters"] = {
                "lat": location.get("lat", 0.0),
                "lon": location.get("lon", 0.0),
                "radius_km": location.get("radius_km", 10.0),
                "limit": 5
            }
            strategy["strategy_type"] = "single"
            
        elif intent == "mixed":
            # For mixed intents, we'll use multiple endpoints
            strategy["strategy_type"] = "multiple"
            strategy["primary_endpoint"] = "search"  # Default fallback
            
            # Add secondary endpoints based on available parameters
            if "category" in parameters:
                strategy["secondary_endpoints"].append({
                    "endpoint": "category",
                    "parameters": {"category": parameters["category"], "limit": 3}
                })
            
            if "source" in parameters:
                strategy["secondary_endpoints"].append({
                    "endpoint": "source", 
                    "parameters": {"source": parameters["source"], "limit": 3}
                })
            
            if "search_terms" in parameters:
                strategy["primary_endpoint"] = "search"
                strategy["parameters"] = {
                    "query": " ".join(parameters["search_terms"]),
                    "limit": 5
                }
        
        else:
            # Fallback to search
            strategy["primary_endpoint"] = "search"
            strategy["parameters"] = {"query": "news", "limit": 5}
            strategy["strategy_type"] = "fallback"
        
        return strategy
    
    def _fallback_analysis(self, user_query: str) -> Dict[str, Any]:
        """Create a fallback analysis when LLM is not available."""
        # Simple keyword-based analysis
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["technology", "tech", "ai", "software"]):
            return {
                "intent": "category",
                "entities": {"topics": ["technology"]},
                "parameters": {"category": "technology"},
                "confidence": 0.6,
                "reasoning": "Fallback analysis: detected technology keywords"
            }
        elif any(word in query_lower for word in ["business", "economy", "finance", "market"]):
            return {
                "intent": "category",
                "entities": {"topics": ["business"]},
                "parameters": {"category": "business"},
                "confidence": 0.6,
                "reasoning": "Fallback analysis: detected business keywords"
            }
        elif any(word in query_lower for word in ["sports", "football", "cricket", "game"]):
            return {
                "intent": "category",
                "entities": {"topics": ["sports"]},
                "parameters": {"category": "sports"},
                "confidence": 0.6,
                "reasoning": "Fallback analysis: detected sports keywords"
            }
        else:
            return {
                "intent": "search",
                "entities": {"topics": ["general"]},
                "parameters": {"search_terms": [user_query]},
                "confidence": 0.4,
                "reasoning": "Fallback analysis: default to search"
            }
    
    def _create_error_response(self, user_query: str, error_message: str) -> Dict[str, Any]:
        """Create an error response when analysis fails."""
        return {
            "analysis": {
                "intent": "search",
                "entities": {"topics": ["general"]},
                "parameters": {"search_terms": [user_query]},
                "confidence": 0.1,
                "reasoning": f"Error in analysis: {error_message}"
            },
            "routing_strategy": {
                "primary_endpoint": "search",
                "secondary_endpoints": [],
                "parameters": {"query": user_query, "limit": 5},
                "confidence": 0.1,
                "strategy_type": "fallback"
            },
            "timestamp": datetime.now().isoformat(),
            "query": user_query,
            "error": error_message
        }


# Global query analyzer instance
query_analyzer: Optional[QueryAnalyzer] = None


def get_query_analyzer() -> Optional[QueryAnalyzer]:
    """Get the global query analyzer instance."""
    return query_analyzer


def initialize_query_analyzer() -> QueryAnalyzer:
    """Initialize the global query analyzer."""
    global query_analyzer
    query_analyzer = QueryAnalyzer()
    logger.info("Query analyzer initialized")
    return query_analyzer
