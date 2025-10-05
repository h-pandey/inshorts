"""
Data ingestion script for loading news data into MongoDB.
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.database import database
from app.services.data_ingestion import data_ingestion_service

# Configure logging
configure_logging()
logger = get_logger(__name__)


async def main():
    """Main data ingestion function."""
    parser = argparse.ArgumentParser(description="Ingest news data into MongoDB")
    parser.add_argument(
        "--file", 
        default="news_data.json",
        help="Path to news data JSON file (default: news_data.json)"
    )
    parser.add_argument(
        "--clear", 
        action="store_true",
        help="Clear existing data before ingestion"
    )
    parser.add_argument(
        "--stats", 
        action="store_true",
        help="Show collection statistics after ingestion"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Process data without inserting into database"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting data ingestion process")
        logger.info(f"Configuration: file={args.file}, clear={args.clear}, dry_run={args.dry_run}")
        
        # Initialize database connection
        logger.info("Connecting to database...")
        await database.connect()
        
        # Initialize data ingestion service
        await data_ingestion_service.initialize()
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No data will be inserted")
            # Just load and process data
            result = await data_ingestion_service.load_news_data(args.file)
            logger.info(f"Dry run completed: {result}")
        else:
            # Load news data
            logger.info("Loading news data...")
            load_result = await data_ingestion_service.load_news_data(args.file)
            logger.info(f"Data loaded: {load_result}")
            
            # Process and validate data
            logger.info("Processing articles...")
            articles = await data_ingestion_service._process_articles(
                await _load_raw_data(args.file)
            )
            
            # Ingest into database
            logger.info("Ingesting data into database...")
            ingest_result = await data_ingestion_service.ingest_articles(
                articles, 
                clear_existing=args.clear
            )
            logger.info(f"Ingestion completed: {ingest_result}")
        
        # Show statistics if requested
        if args.stats and not args.dry_run:
            logger.info("Retrieving collection statistics...")
            stats = await data_ingestion_service.get_collection_stats()
            _print_statistics(stats)
        
        logger.info("Data ingestion process completed successfully")
        
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        # Disconnect from database
        await database.disconnect()
        logger.info("Disconnected from database")


async def _load_raw_data(file_path: str):
    """Load raw data from JSON file."""
    import json
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path_obj, 'r', encoding='utf-8') as f:
        return json.load(f)


def _print_statistics(stats: dict):
    """Print collection statistics in a formatted way."""
    print("\n" + "="*60)
    print("📊 COLLECTION STATISTICS")
    print("="*60)
    
    print(f"📰 Total Articles: {stats['total_articles']:,}")
    
    if stats.get('date_range'):
        date_range = stats['date_range']
        print(f"📅 Date Range: {date_range['min_date']} to {date_range['max_date']}")
    
    print(f"\n📂 Top Categories:")
    for category in stats.get('top_categories', [])[:10]:
        print(f"   {category['_id']}: {category['count']:,} articles")
    
    print(f"\n📰 Top Sources:")
    for source in stats.get('top_sources', [])[:10]:
        print(f"   {source['_id']}: {source['count']:,} articles")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
