#!/usr/bin/env python3
"""
Test database connection and basic queries.
"""

import asyncio
import motor.motor_asyncio
import os
from datetime import datetime

async def test_db_connection():
    """Test MongoDB connection and basic operations."""
    
    # Connection settings
    mongodb_url = "mongodb://admin:password123@mongodb:27017/news_db?authSource=admin"
    database_name = "news_db"
    collection_name = "articles"
    
    print("🔌 Testing MongoDB Connection...")
    print(f"URL: {mongodb_url}")
    print(f"Database: {database_name}")
    print(f"Collection: {collection_name}")
    
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        collection = db[collection_name]
        
        # Test connection
        print("\n📊 Testing connection...")
        await client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Test collection access
        print("\n📋 Testing collection access...")
        count = await collection.count_documents({})
        print(f"✅ Total documents in collection: {count}")
        
        # Test a simple query
        print("\n🔍 Testing simple query...")
        sample_doc = await collection.find_one({})
        if sample_doc:
            print(f"✅ Sample document found: {sample_doc.get('title', 'No title')[:50]}...")
            print(f"   Category: {sample_doc.get('category', 'No category')}")
            print(f"   Source: {sample_doc.get('source_name', 'No source')}")
        else:
            print("❌ No documents found")
        
        # Test category query
        print("\n🏷️ Testing category query...")
        tech_count = await collection.count_documents({"category": "technology"})
        print(f"✅ Technology articles: {tech_count}")
        
        if tech_count > 0:
            tech_article = await collection.find_one({"category": "technology"})
            if tech_article:
                print(f"   Sample tech article: {tech_article.get('title', 'No title')[:50]}...")
        
        # Test categories
        print("\n📊 Available categories:")
        categories = await collection.distinct("category")
        for cat in categories[:10]:  # Show first 10
            count = await collection.count_documents({"category": cat})
            print(f"   {cat}: {count} articles")
        
        # Close connection
        client.close()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db_connection())
