"""
Basic application test without external dependencies.
Tests core application structure and configuration.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_config_loading():
    """Test configuration loading."""
    try:
        # Test if we can import config (will fail without dependencies, but we can test the file structure)
        config_file = project_root / "app" / "core" / "config.py"
        
        if not config_file.exists():
            return False, "Config file not found"
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Check for key configuration elements
        required_elements = [
            "class Settings",
            "mongodb_url",
            "redis_url", 
            "openai_api_key",
            "app_name"
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in content]
        
        if missing_elements:
            return False, f"Missing configuration elements: {missing_elements}"
        
        return True, "Configuration file structure is valid"
    
    except Exception as e:
        return False, f"Error testing config: {e}"


def test_models_structure():
    """Test Pydantic models structure."""
    try:
        model_files = [
            "app/models/article.py",
            "app/models/query.py", 
            "app/models/user_event.py",
            "app/models/trending.py"
        ]
        
        for model_file in model_files:
            file_path = project_root / model_file
            if not file_path.exists():
                return False, f"Model file not found: {model_file}"
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for Pydantic model classes
            if "BaseModel" not in content:
                return False, f"BaseModel not found in {model_file}"
        
        return True, "All model files have correct structure"
    
    except Exception as e:
        return False, f"Error testing models: {e}"


def test_main_app_structure():
    """Test main application structure."""
    try:
        main_file = project_root / "app" / "main.py"
        
        if not main_file.exists():
            return False, "Main app file not found"
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check for key FastAPI elements
        required_elements = [
            "FastAPI",
            "app = FastAPI",
            "@app.get",
            "startup_event",
            "shutdown_event"
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in content]
        
        if missing_elements:
            return False, f"Missing FastAPI elements: {missing_elements}"
        
        return True, "Main application structure is valid"
    
    except Exception as e:
        return False, f"Error testing main app: {e}"


def test_news_data_structure():
    """Test news data structure."""
    try:
        news_file = project_root / "news_data.json"
        
        if not news_file.exists():
            return False, "News data file not found"
        
        with open(news_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return False, "News data is not a list"
        
        if len(data) == 0:
            return False, "News data is empty"
        
        # Test first article structure
        sample = data[0]
        required_fields = [
            'id', 'title', 'description', 'url', 'publication_date',
            'source_name', 'category', 'relevance_score', 'latitude', 'longitude'
        ]
        
        missing_fields = [field for field in required_fields if field not in sample]
        
        if missing_fields:
            return False, f"Missing fields in news data: {missing_fields}"
        
        # Test data types
        if not isinstance(sample['title'], str):
            return False, "Title should be string"
        
        if not isinstance(sample['category'], list):
            return False, "Category should be list"
        
        if not isinstance(sample['relevance_score'], (int, float)):
            return False, "Relevance score should be number"
        
        return True, f"News data structure is valid ({len(data)} articles)"
    
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in news data: {e}"
    except Exception as e:
        return False, f"Error testing news data: {e}"


def test_docker_configuration():
    """Test Docker configuration files."""
    try:
        docker_files = [
            "docker-compose.yml",
            "Dockerfile",
            "scripts/mongo-init.js"
        ]
        
        for docker_file in docker_files:
            file_path = project_root / docker_file
            if not file_path.exists():
                return False, f"Docker file not found: {docker_file}"
        
        # Test docker-compose.yml structure
        compose_file = project_root / "docker-compose.yml"
        with open(compose_file, 'r') as f:
            content = f.read()
        
        required_services = ["app", "mongodb", "redis"]
        missing_services = [service for service in required_services if f"  {service}:" not in content]
        
        if missing_services:
            return False, f"Missing services in docker-compose.yml: {missing_services}"
        
        return True, "Docker configuration is valid"
    
    except Exception as e:
        return False, f"Error testing Docker config: {e}"


def main():
    """Main test function."""
    print("🧪 Basic Application Tests (No Dependencies)")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Models Structure", test_models_structure),
        ("Main App Structure", test_main_app_structure),
        ("News Data Structure", test_news_data_structure),
        ("Docker Configuration", test_docker_configuration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            print(f"    {message}")
            print()
            
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL {test_name}")
            print(f"    Exception: {e}")
            print()
            failed += 1
    
    print("=" * 50)
    print(f"📈 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All basic tests passed!")
        print("\n📋 The application structure is ready.")
        print("   Next steps:")
        print("   1. Start Docker Desktop")
        print("   2. Run: docker-compose up --build -d")
        print("   3. Test the API endpoints")
    else:
        print("⚠️  Some basic tests failed.")
        print("   Please check the issues above before proceeding.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
