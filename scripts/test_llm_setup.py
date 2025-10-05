#!/usr/bin/env python3
"""
Test script for LLM service setup and basic functionality.
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services.llm_service import CursorLLMService, initialize_llm_service
from services.query_analyzer import QueryAnalyzer, initialize_query_analyzer
from core.config import settings


async def test_llm_service():
    """Test the LLM service functionality."""
    print("🧪 Testing LLM Service Setup...")
    
    # Initialize LLM service with test API key
    # Use environment variable for API key
    test_api_key = os.getenv("CURSOR_API_KEY", "demo_key")
    if test_api_key == "demo_key":
        print("Warning: Using demo API key. Set CURSOR_API_KEY environment variable for real testing.")
    llm_service = initialize_llm_service(test_api_key)
    
    print(f"✅ LLM Service initialized with API key: {test_api_key[:20]}...")
    
    # Test query analysis
    test_queries = [
        "Latest technology news from New York Times",
        "Show me news about Elon Musk near Palo Alto",
        "High relevance business news",
        "Sports news from last week"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            analysis = await llm_service.analyze_query(query)
            print(f"✅ Analysis result:")
            print(f"   Intent: {analysis.get('intent', 'N/A')}")
            print(f"   Confidence: {analysis.get('confidence', 'N/A')}")
            print(f"   Parameters: {analysis.get('parameters', {})}")
        except Exception as e:
            print(f"❌ Error analyzing query: {e}")
    
    # Test summary generation
    print(f"\n📝 Testing summary generation...")
    try:
        summary = await llm_service.generate_summary(
            "Test Article Title",
            "This is a test article description about important developments in technology."
        )
        print(f"✅ Generated summary: {summary}")
    except Exception as e:
        print(f"❌ Error generating summary: {e}")


async def test_query_analyzer():
    """Test the query analyzer functionality."""
    print("\n🧪 Testing Query Analyzer...")
    
    # Initialize query analyzer
    analyzer = initialize_query_analyzer()
    print("✅ Query Analyzer initialized")
    
    # Test query analysis and routing
    test_queries = [
        "Latest technology news",
        "Business news from Reuters",
        "High relevance articles",
        "News near San Francisco"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            result = await analyzer.analyze_and_route(query)
            print(f"✅ Analysis and routing completed:")
            print(f"   Intent: {result['analysis'].get('intent', 'N/A')}")
            print(f"   Primary endpoint: {result['routing_strategy'].get('primary_endpoint', 'N/A')}")
            print(f"   Strategy type: {result['routing_strategy'].get('strategy_type', 'N/A')}")
            print(f"   Confidence: {result['analysis'].get('confidence', 'N/A')}")
        except Exception as e:
            print(f"❌ Error in query analysis: {e}")


async def test_configuration():
    """Test configuration loading."""
    print("\n🧪 Testing Configuration...")
    
    print(f"✅ App Name: {settings.app_name}")
    print(f"✅ API Prefix: {settings.api_v1_prefix}")
    print(f"✅ MongoDB URL: {settings.mongodb_url}")
    print(f"✅ Redis URL: {settings.redis_url}")
    print(f"✅ Cursor API Key: {'Set' if settings.cursor_api_key else 'Not set'}")
    print(f"✅ Cursor Base URL: {settings.cursor_base_url}")
    print(f"✅ Cursor Model: {settings.cursor_model}")


async def main():
    """Main test function."""
    print("🚀 Starting LLM Service Setup Tests...\n")
    
    try:
        # Test configuration
        await test_configuration()
        
        # Test LLM service
        await test_llm_service()
        
        # Test query analyzer
        await test_query_analyzer()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Set up the Cursor API key in your environment")
        print("2. Test the LLM service with real API calls")
        print("3. Integrate with the main application")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
