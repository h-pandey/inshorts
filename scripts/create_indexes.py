"""
Script to create database indexes.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import database
from app.core.database_schema import setup_database_schema
from app.core.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


async def main():
    """Main function to create database indexes."""
    try:
        logger.info("Starting database index creation...")
        
        # Connect to database
        await database.connect()
        logger.info("Connected to database")
        
        # Setup schema and indexes
        await setup_database_schema(database.database)
        logger.info("Database schema setup completed")
        
        # Get index information
        from app.core.database_schema import DatabaseSchema
        schema = DatabaseSchema(database.database)
        index_info = await schema.get_index_info()
        
        # Print index information
        print("\n📊 Database Indexes Created:")
        print("=" * 50)
        
        for collection_name, indexes in index_info.items():
            print(f"\n🗄️  Collection: {collection_name}")
            for index in indexes:
                index_name = index.get('name', 'unnamed')
                index_keys = index.get('key', {})
                print(f"   ✅ {index_name}: {index_keys}")
        
        print("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        sys.exit(1)
    
    finally:
        # Disconnect from database
        await database.disconnect()
        logger.info("Disconnected from database")


if __name__ == "__main__":
    asyncio.run(main())
