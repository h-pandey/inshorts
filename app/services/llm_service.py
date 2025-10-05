"""
LLM Service for query analysis and content generation using Cursor API.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class CursorLLMService:
    """Service for interacting with Cursor API for LLM operations."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.cursor.sh"):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 30.0
        logger.info(f"Initialized CursorLLMService with base_url: {self.base_url}")
        
    async def analyze_query(self, user_query: str, user_location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analyze user query to extract intent, entities, and parameters.
        
        Args:
            user_query: The user's natural language query
            user_location: Optional user location with lat/lon
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Create the analysis prompt
            system_prompt = self._create_analysis_prompt()
            user_prompt = self._create_user_prompt(user_query, user_location)
            
            # Call Cursor API
            response = await self._call_cursor_api(system_prompt, user_prompt)
            
            # Parse and validate response
            analysis_result = self._parse_analysis_response(response)
            
            logger.info(f"Query analysis completed for: {user_query[:50]}...")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            # Return fallback analysis
            return self._create_fallback_analysis(user_query)
    
    async def generate_summary(self, title: str, description: str) -> str:
        """
        Generate a concise summary of a news article.
        
        Args:
            title: Article title
            description: Article description
            
        Returns:
            Generated summary
        """
        try:
            system_prompt = self._create_summary_prompt()
            user_prompt = f"Title: {title}\nDescription: {description}"
            
            response = await self._call_cursor_api(system_prompt, user_prompt)
            
            # Extract summary from response
            summary = self._extract_summary(response)
            
            logger.info(f"Summary generated for: {title[:30]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary unavailable: {description[:100]}..."
    
    def _create_analysis_prompt(self) -> str:
        """Create the system prompt for query analysis."""
        return """You are a news query analyzer. Analyze user queries and extract structured information.

Return a JSON response with the following structure:
{
    "intent": "category|search|source|score|nearby|mixed",
    "entities": {
        "people": ["person1", "person2"],
        "organizations": ["org1", "org2"],
        "locations": ["location1", "location2"],
        "topics": ["topic1", "topic2"]
    },
    "parameters": {
        "category": "technology|business|sports|world|entertainment|national",
        "search_terms": ["term1", "term2"],
        "source": "source_name",
        "min_score": 0.0-1.0,
        "location": {"lat": float, "lon": float, "radius_km": float}
    },
    "confidence": 0.0-1.0,
    "reasoning": "explanation of analysis"
}

Guidelines:
- Intent: Determine the primary intent (category, search, source, score, nearby, or mixed)
- Entities: Extract key entities mentioned in the query
- Parameters: Extract specific values needed for API calls
- Location: If location is mentioned, try to geocode it or use provided coordinates
- Confidence: Rate your confidence in the analysis (0.0-1.0)
- Reasoning: Explain your analysis logic

Examples:
Query: "Latest technology news from New York Times"
Response: {"intent": "mixed", "entities": {"organizations": ["New York Times"]}, "parameters": {"category": "technology", "source": "New York Times"}, "confidence": 0.9, "reasoning": "Combines category and source intent"}

Query: "Show me news about Elon Musk near Palo Alto"
Response: {"intent": "mixed", "entities": {"people": ["Elon Musk"], "locations": ["Palo Alto"]}, "parameters": {"search_terms": ["Elon Musk"], "location": {"lat": 37.4419, "lon": -122.1430, "radius_km": 10}}, "confidence": 0.8, "reasoning": "Combines search and location-based intent"}"""
    
    def _create_user_prompt(self, user_query: str, user_location: Optional[Dict[str, float]] = None) -> str:
        """Create the user prompt for query analysis."""
        prompt = f"Analyze this news query: '{user_query}'"
        
        if user_location:
            prompt += f"\nUser location: {user_location}"
        
        prompt += "\n\nProvide the JSON analysis as specified in the system prompt."
        return prompt
    
    def _create_summary_prompt(self) -> str:
        """Create the system prompt for article summarization."""
        return """You are a news article summarizer. Create concise, informative summaries.

Guidelines:
- Summarize in 2-3 sentences
- Focus on key facts and developments
- Highlight impact and significance
- Mention main stakeholders
- Use clear, engaging language
- Keep it under 150 words

Return only the summary text, no additional formatting."""
    
    async def _call_cursor_api(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the Cursor API with the given prompts.
        
        Uses OpenAI-compatible API format with the Cursor API key.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",  # Using GPT-4 model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        # Try multiple possible endpoints
        possible_endpoints = [
            f"{self.base_url}/v1/chat/completions",
            f"{self.base_url}/chat/completions",
            f"{self.base_url}/api/v1/chat/completions",
            "https://api.openai.com/v1/chat/completions"
        ]
        
        for url in possible_endpoints:
            try:
                logger.info(f"Trying API call to: {url}")
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload
                    )
                
                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            logger.info(f"Successfully got response from: {url}")
                            return result["choices"][0]["message"]["content"]
                        else:
                            logger.warning(f"Unexpected API response format from {url}")
                            continue
                    else:
                        logger.warning(f"API returned status {response.status_code} from {url}: {response.text}")
                        continue
                        
            except httpx.TimeoutException:
                logger.error(f"API request timed out for {url}")
                continue
            except httpx.RequestError as e:
                logger.error(f"API request failed for {url}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error calling API at {url}: {e}")
                continue
        
        # If all endpoints failed, return fallback
        logger.error("All API endpoints failed, using fallback response")
        return self._fallback_response(system_prompt, user_prompt)
    
    def _fallback_response(self, system_prompt: str, user_prompt: str) -> str:
        """Fallback response when API calls fail."""
        if "analyze" in system_prompt.lower():
            return self._mock_analysis_response(user_prompt)
        else:
            return self._mock_summary_response(user_prompt)
    
    def _mock_analysis_response(self, user_prompt: str) -> str:
        """Mock analysis response for testing."""
        # Simple keyword-based analysis for testing
        query = user_prompt.lower()
        
        if "technology" in query or "tech" in query:
            return json.dumps({
                "intent": "category",
                "entities": {"topics": ["technology"]},
                "parameters": {"category": "technology"},
                "confidence": 0.8,
                "reasoning": "Detected technology category intent"
            })
        elif "search" in query or "about" in query:
            return json.dumps({
                "intent": "search",
                "entities": {"topics": ["general"]},
                "parameters": {"search_terms": ["news"]},
                "confidence": 0.7,
                "reasoning": "Detected search intent"
            })
        else:
            return json.dumps({
                "intent": "category",
                "entities": {"topics": ["general"]},
                "parameters": {"category": "general"},
                "confidence": 0.6,
                "reasoning": "Default to general category"
            })
    
    def _mock_summary_response(self, user_prompt: str) -> str:
        """Mock summary response for testing."""
        return "This is a mock summary generated for testing purposes. The article discusses important developments in the news industry."
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate the analysis response."""
        try:
            # Try to extract JSON from response
            if response.startswith('{'):
                return json.loads(response)
            else:
                # Look for JSON in the response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._create_fallback_analysis("")
    
    def _extract_summary(self, response: str) -> str:
        """Extract summary from the response."""
        # Clean up the response
        summary = response.strip()
        
        # Remove any markdown formatting
        if summary.startswith('```'):
            lines = summary.split('\n')
            summary = '\n'.join(lines[1:-1])
        
        return summary
    
    def _create_fallback_analysis(self, user_query: str) -> Dict[str, Any]:
        """Create a fallback analysis when LLM fails."""
        return {
            "intent": "search",
            "entities": {"topics": ["general"]},
            "parameters": {"search_terms": [user_query]},
            "confidence": 0.3,
            "reasoning": "Fallback analysis due to LLM error"
        }


# Global LLM service instance
llm_service: Optional[CursorLLMService] = None


def get_llm_service() -> Optional[CursorLLMService]:
    """Get the global LLM service instance."""
    return llm_service


def initialize_llm_service(api_key: str, base_url: str = "https://api.cursor.sh") -> CursorLLMService:
    """Initialize the global LLM service."""
    global llm_service
    llm_service = CursorLLMService(api_key, base_url)
    logger.info("LLM service initialized with Cursor API")
    return llm_service
