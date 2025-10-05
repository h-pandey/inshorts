"""
Test script to verify project setup.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Core config imported successfully")
        
        from app.core.database import database
        print("✅ Database module imported successfully")
        
        from app.core.redis_client import redis_client
        print("✅ Redis client imported successfully")
        
        # Test model imports
        from app.models.article import Article, ArticleResponse
        print("✅ Article models imported successfully")
        
        from app.models.query import NewsQuery, QueryAnalysis
        print("✅ Query models imported successfully")
        
        # Test main app
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ App version: {settings.app_version}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ MongoDB URL: {settings.mongodb_url}")
        print(f"✅ Redis URL: {settings.redis_url}")
        print(f"✅ API prefix: {settings.api_v1_prefix}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Testing Contextual News API setup...\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test configuration
    config_ok = test_configuration()
    
    if imports_ok and config_ok:
        print("\n🎉 Setup test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start MongoDB and Redis services")
        print("3. Update .env file with your configuration")
        print("4. Run the application: python scripts/run_dev.py")
        return 0
    else:
        print("\n❌ Setup test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
