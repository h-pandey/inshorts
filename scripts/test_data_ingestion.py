"""
Test data ingestion logic without external dependencies.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def test_news_data_loading():
    """Test loading and processing news data."""
    print("🧪 Testing Data Ingestion Logic")
    print("=" * 50)
    
    # Test 1: Load news data
    print("1. Testing news data loading...")
    try:
        with open("news_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ News data is not a list")
            return False
        
        print(f"✅ Loaded {len(data)} articles")
        
    except Exception as e:
        print(f"❌ Failed to load news data: {e}")
        return False
    
    # Test 2: Validate article structure
    print("\n2. Testing article structure validation...")
    sample_article = data[0]
    required_fields = [
        'id', 'title', 'description', 'url', 'publication_date',
        'source_name', 'category', 'relevance_score', 'latitude', 'longitude'
    ]
    
    missing_fields = [field for field in required_fields if field not in sample_article]
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False
    
    print("✅ Article structure is valid")
    
    # Test 3: Test data transformation
    print("\n3. Testing data transformation...")
    try:
        transformed = transform_article(sample_article)
        print("✅ Data transformation successful")
        print(f"   Transformed fields: {list(transformed.keys())}")
        
    except Exception as e:
        print(f"❌ Data transformation failed: {e}")
        return False
    
    # Test 4: Test batch processing
    print("\n4. Testing batch processing...")
    try:
        batch_size = 10
        batch = data[:batch_size]
        processed_batch = []
        
        for article in batch:
            try:
                transformed = transform_article(article)
                processed_batch.append(transformed)
            except Exception as e:
                print(f"⚠️  Skipping article due to error: {e}")
        
        print(f"✅ Processed {len(processed_batch)}/{len(batch)} articles in batch")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        return False
    
    # Test 5: Test data statistics
    print("\n5. Testing data statistics...")
    try:
        stats = analyze_data(data)
        print("✅ Data analysis successful")
        print(f"   Categories: {len(stats['categories'])} unique")
        print(f"   Sources: {len(stats['sources'])} unique")
        print(f"   Date range: {stats['date_range']}")
        
    except Exception as e:
        print(f"❌ Data analysis failed: {e}")
        return False
    
    print("\n🎉 All data ingestion tests passed!")
    return True


def transform_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw article data to match our schema."""
    # Convert publication_date to datetime if it's a string
    publication_date = article_data.get("publication_date")
    if isinstance(publication_date, str):
        try:
            publication_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
        except ValueError:
            # Fallback to current time if parsing fails
            publication_date = datetime.now()
    
    # Create geospatial location object
    location = {
        "type": "Point",
        "coordinates": [
            float(article_data.get("longitude", 0)),
            float(article_data.get("latitude", 0))
        ]
    }
    
    # Transform the article data
    transformed = {
        "title": article_data.get("title", ""),
        "description": article_data.get("description", ""),
        "url": article_data.get("url", ""),
        "publication_date": publication_date,
        "source_name": article_data.get("source_name", ""),
        "category": article_data.get("category", []),
        "relevance_score": float(article_data.get("relevance_score", 0.0)),
        "latitude": float(article_data.get("latitude", 0.0)),
        "longitude": float(article_data.get("longitude", 0.0)),
        "location": location,
        "llm_summary": None,  # Will be generated later
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    return transformed


def analyze_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the dataset and return statistics."""
    categories = set()
    sources = set()
    dates = []
    
    for article in data:
        # Collect categories
        article_categories = article.get("category", [])
        if isinstance(article_categories, list):
            categories.update(article_categories)
        
        # Collect sources
        source = article.get("source_name")
        if source:
            sources.add(source)
        
        # Collect dates
        pub_date = article.get("publication_date")
        if pub_date:
            dates.append(pub_date)
    
    # Calculate date range
    if dates:
        try:
            # Convert string dates to datetime objects for comparison
            date_objects = []
            for date_str in dates:
                if isinstance(date_str, str):
                    try:
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_objects.append(date_obj)
                    except ValueError:
                        continue
                else:
                    date_objects.append(date_str)
            
            if date_objects:
                min_date = min(date_objects)
                max_date = max(date_objects)
                date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            else:
                date_range = "Unable to parse dates"
        except Exception:
            date_range = "Error calculating date range"
    else:
        date_range = "No dates found"
    
    return {
        "total_articles": len(data),
        "categories": list(categories),
        "sources": list(sources),
        "date_range": date_range
    }


def main():
    """Main test function."""
    success = test_news_data_loading()
    
    if success:
        print("\n📋 Data ingestion logic is ready!")
        print("   Next steps:")
        print("   1. Start Docker Desktop")
        print("   2. Run: docker-compose up --build -d")
        print("   3. Run: python scripts/ingest_data.py")
        return 0
    else:
        print("\n❌ Data ingestion tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
