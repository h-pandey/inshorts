"""
Analyze the news data structure and content.
"""

import json
from collections import Counter
from pathlib import Path


def analyze_news_data():
    """Analyze the news data file."""
    news_file = Path("news_data.json")
    
    if not news_file.exists():
        print("❌ news_data.json not found")
        return
    
    print("📊 News Data Analysis")
    print("=" * 40)
    
    with open(news_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📰 Total articles: {len(data)}")
    
    if len(data) == 0:
        print("❌ No articles found")
        return
    
    # Analyze sample article
    sample = data[0]
    print(f"\n🔍 Sample article structure:")
    for key, value in sample.items():
        if isinstance(value, str) and len(value) > 50:
            print(f"   {key}: {value[:50]}...")
        else:
            print(f"   {key}: {value}")
    
    # Analyze categories
    all_categories = []
    for article in data:
        categories = article.get('category', [])
        if isinstance(categories, list):
            all_categories.extend(categories)
    
    category_counts = Counter(all_categories)
    print(f"\n📂 Categories found ({len(category_counts)} unique):")
    for category, count in category_counts.most_common(10):
        print(f"   {category}: {count} articles")
    
    # Analyze sources
    sources = [article.get('source_name', 'Unknown') for article in data]
    source_counts = Counter(sources)
    print(f"\n📰 Sources found ({len(source_counts)} unique):")
    for source, count in source_counts.most_common(10):
        print(f"   {source}: {count} articles")
    
    # Analyze relevance scores
    scores = [article.get('relevance_score', 0) for article in data if isinstance(article.get('relevance_score'), (int, float))]
    if scores:
        print(f"\n📈 Relevance scores:")
        print(f"   Min: {min(scores):.3f}")
        print(f"   Max: {max(scores):.3f}")
        print(f"   Avg: {sum(scores)/len(scores):.3f}")
    
    # Analyze locations
    locations = [(article.get('latitude'), article.get('longitude')) for article in data]
    valid_locations = [(lat, lon) for lat, lon in locations if lat is not None and lon is not None]
    print(f"\n🌍 Location data:")
    print(f"   Articles with coordinates: {len(valid_locations)}/{len(data)}")
    
    if valid_locations:
        lats = [lat for lat, lon in valid_locations]
        lons = [lon for lat, lon in valid_locations]
        print(f"   Latitude range: {min(lats):.3f} to {max(lats):.3f}")
        print(f"   Longitude range: {min(lons):.3f} to {max(lons):.3f}")
    
    print(f"\n✅ News data analysis completed!")


if __name__ == "__main__":
    analyze_news_data()
