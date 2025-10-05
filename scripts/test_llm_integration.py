#!/usr/bin/env python3
"""
Integration test for LLM service with the main application.
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services.llm_service import initialize_llm_service
from services.query_analyzer import initialize_query_analyzer
from core.config import settings


async def test_integration():
    """Test LLM integration with the main application."""
    print("🧪 Testing LLM Integration...")
    
    # Set up the Cursor API key
    # Use environment variable for API key
    cursor_api_key = os.getenv("CURSOR_API_KEY", "demo_key")
    if cursor_api_key == "demo_key":
        print("Warning: Using demo API key. Set CURSOR_API_KEY environment variable for real testing.")
    
    # Initialize services
    print("🔧 Initializing LLM services...")
    llm_service = initialize_llm_service(cursor_api_key)
    analyzer = initialize_query_analyzer()
    
    print("✅ Services initialized successfully")
    
    # Test a complex query
    test_query = "Latest technology news from New York Times about AI developments"
    user_location = {"lat": 37.7749, "lon": -122.4194}  # San Francisco
    
    print(f"\n🔍 Testing complex query: '{test_query}'")
    print(f"📍 User location: {user_location}")
    
    try:
        # Analyze the query
        result = await analyzer.analyze_and_route(test_query, user_location)
        
        print("\n📊 Analysis Results:")
        print(f"   Query: {result['query']}")
        print(f"   Intent: {result['analysis']['intent']}")
        print(f"   Confidence: {result['analysis']['confidence']}")
        print(f"   Entities: {result['analysis']['entities']}")
        print(f"   Parameters: {result['analysis']['parameters']}")
        print(f"   Reasoning: {result['analysis']['reasoning']}")
        
        print("\n🎯 Routing Strategy:")
        print(f"   Primary endpoint: {result['routing_strategy']['primary_endpoint']}")
        print(f"   Strategy type: {result['routing_strategy']['strategy_type']}")
        print(f"   Parameters: {result['routing_strategy']['parameters']}")
        print(f"   Confidence: {result['routing_strategy']['confidence']}")
        
        # Test summary generation
        print("\n📝 Testing summary generation...")
        summary = await llm_service.generate_summary(
            "AI Breakthrough: New Language Model Achieves Human-Level Performance",
            "Researchers at a leading tech company have developed a new language model that demonstrates human-level performance across multiple benchmarks, marking a significant milestone in artificial intelligence development."
        )
        print(f"✅ Generated summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


async def test_fallback_behavior():
    """Test fallback behavior when LLM is not available."""
    print("\n🧪 Testing Fallback Behavior...")
    
    # Test without LLM service
    analyzer = initialize_query_analyzer()
    
    test_query = "Technology news about artificial intelligence"
    
    try:
        result = await analyzer.analyze_and_route(test_query)
        
        print(f"✅ Fallback analysis completed:")
        print(f"   Intent: {result['analysis']['intent']}")
        print(f"   Confidence: {result['analysis']['confidence']}")
        print(f"   Reasoning: {result['analysis']['reasoning']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False


async def main():
    """Main integration test function."""
    print("🚀 Starting LLM Integration Tests...\n")
    
    try:
        # Test main integration
        integration_success = await test_integration()
        
        # Test fallback behavior
        fallback_success = await test_fallback_behavior()
        
        if integration_success and fallback_success:
            print("\n🎉 All integration tests passed!")
            print("\n📋 LLM Service is ready for integration with the main application.")
            print("\n🔧 Next steps:")
            print("1. Add the smart query endpoint to the main application")
            print("2. Test with real API calls")
            print("3. Add caching layer")
            print("4. Add error handling and monitoring")
        else:
            print("\n❌ Some integration tests failed.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
