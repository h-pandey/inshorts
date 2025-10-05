#!/usr/bin/env python3

"""
Simple ingestion script without Pydantic.
- Reads news_data.json
- Transforms documents (publication_date, location GeoJSON)
- Upserts into MongoDB on url
- Optional --clear and --stats flags
"""

import argparse
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient, ReplaceOne
from pymongo.errors import BulkWriteError


DEFAULT_MONGO_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://admin:password123@mongodb:27017/news_db?authSource=admin",
)
DEFAULT_DB = os.getenv("MONGODB_DATABASE", "news_db")
DEFAULT_COLLECTION = os.getenv("MONGODB_COLLECTION", "articles")
DEFAULT_FILE = os.getenv("NEWS_DATA_FILE", "/app/news_data.json")


def parse_iso_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    # Try multiple formats defensively
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(str(value), fmt)
        except Exception:
            continue
    try:
        # Fallback: fromisoformat (handles many cases)
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def transform_article(doc: Dict[str, Any]) -> Dict[str, Any]:
    transformed = dict(doc)

    # Normalize categories
    category = transformed.get("category")
    if isinstance(category, str):
        transformed["category"] = [category]
    elif category is None:
        transformed["category"] = []

    # publication_date to datetime
    pub = transformed.get("publication_date")
    dt = parse_iso_datetime(pub)
    if dt is not None:
        transformed["publication_date"] = dt

    # GeoJSON location from latitude/longitude
    lat = to_float(transformed.get("latitude"))
    lon = to_float(transformed.get("longitude"))
    if lat is not None and lon is not None:
        transformed["location"] = {"type": "Point", "coordinates": [lon, lat]}

    # Ensure relevance_score numeric
    score = transformed.get("relevance_score")
    if score is not None:
        try:
            transformed["relevance_score"] = float(score)
        except Exception:
            pass

    return transformed


def load_file(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a list of articles in JSON file")
    return data


def ingest(
    client: MongoClient,
    db_name: str,
    collection_name: str,
    articles: List[Dict[str, Any]],
    clear_existing: bool,
) -> Dict[str, Any]:
    db = client[db_name]
    col = db[collection_name]

    if clear_existing:
        col.delete_many({})

    # Create unique index on url to avoid duplicates
    try:
        col.create_index("url", unique=True)
    except Exception:
        pass

    ops: List[ReplaceOne] = []
    for raw in articles:
        doc = transform_article(raw)
        url = doc.get("url")
        if not url:
            continue
        ops.append(
            ReplaceOne({"url": url}, doc, upsert=True)
        )

    result = {"matched": 0, "modified": 0, "upserted": 0, "errors": 0}
    if not ops:
        return result

    try:
        bulk = col.bulk_write(ops, ordered=False)
        result.update(
            matched=bulk.matched_count,
            modified=bulk.modified_count,
            upserted=len(bulk.upserted_ids or {}),
        )
    except BulkWriteError as bwe:
        details = bwe.details or {}
        write_errors = details.get("writeErrors", [])
        result["errors"] = len(write_errors)

    return result


def get_stats(client: MongoClient, db_name: str, collection_name: str) -> Dict[str, Any]:
    db = client[db_name]
    col = db[collection_name]
    total = col.count_documents({})

    # Date range
    min_doc = col.find({}, {"publication_date": 1}).sort("publication_date", 1).limit(1)
    max_doc = col.find({}, {"publication_date": 1}).sort("publication_date", -1).limit(1)
    min_date = None
    max_date = None
    for d in min_doc:
        min_date = d.get("publication_date")
    for d in max_doc:
        max_date = d.get("publication_date")

    # Top categories
    top_categories = list(
        col.aggregate([
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ])
    )

    # Top sources
    top_sources = list(
        col.aggregate([
            {"$group": {"_id": "$source_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ])
    )

    return {
        "total_articles": total,
        "date_range": {
            "min_date": min_date.isoformat() if isinstance(min_date, datetime) else None,
            "max_date": max_date.isoformat() if isinstance(max_date, datetime) else None,
        },
        "top_categories": top_categories,
        "top_sources": top_sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple news data ingestion")
    parser.add_argument("--file", default=DEFAULT_FILE, help="Path to news_data.json")
    parser.add_argument("--mongo", default=DEFAULT_MONGO_URL, help="MongoDB URL")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database name")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Collection name")
    parser.add_argument("--clear", action="store_true", help="Clear existing documents before ingesting")
    parser.add_argument("--stats", action="store_true", help="Print collection statistics after ingesting")
    args = parser.parse_args()

    print("📰 Simple Ingestion Starting…")
    print(f"File: {args.file}")
    print(f"Mongo: {args.mongo}")
    print(f"DB/Collection: {args.db}.{args.collection}")

    client = MongoClient(args.mongo)
    try:
        articles = load_file(args.file)
        result = ingest(client, args.db, args.collection, articles, args.clear)
        print(f"Ingestion result: {result}")
        if args.stats:
            stats = get_stats(client, args.db, args.collection)
            print(json.dumps(stats, indent=2, default=str))
    finally:
        client.close()

    print("✅ Simple Ingestion Completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
