// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the news database
db = db.getSiblingDB('news_db');

// Create collections
db.createCollection('articles');
db.createCollection('user_events');

// Create indexes for articles collection
db.articles.createIndex({ "category": 1, "publication_date": -1 });
db.articles.createIndex({ "source_name": 1, "publication_date": -1 });
db.articles.createIndex({ "relevance_score": -1 });
db.articles.createIndex({ "location": "2dsphere" });
db.articles.createIndex({ "title": "text", "description": "text" });
db.articles.createIndex({ "publication_date": -1 });
db.articles.createIndex({ "url": 1 }, { unique: true });

// Create indexes for user_events collection
db.user_events.createIndex({ "article_id": 1, "timestamp": -1 });
db.user_events.createIndex({ "user_id": 1, "timestamp": -1 });
db.user_events.createIndex({ "location_cluster": 1, "timestamp": -1 });
db.user_events.createIndex({ "event_type": 1, "timestamp": -1 });
db.user_events.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 2592000 }); // 30 days TTL

// Create a compound index for trending queries
db.user_events.createIndex({ 
    "location_cluster": 1, 
    "event_type": 1, 
    "timestamp": -1 
});

// Insert sample data (optional)
print("MongoDB initialization completed successfully!");
print("Collections created: articles, user_events");
print("Indexes created for optimal query performance");
