"""
Test the simple app without external dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_simple_app():
    """Test the simple app structure."""
    print("🧪 Testing Simple App Structure")
    print("=" * 40)
    
    # Test 1: Check simple main file
    print("1. Testing simple main app...")
    try:
        simple_main_file = project_root / "app" / "simple_main.py"
        
        if not simple_main_file.exists():
            print("❌ Simple main app file not found")
            return False
        
        with open(simple_main_file, 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            "FastAPI",
            "app = FastAPI",
            "@app.get",
            "health_check",
            "root"
        ]
        
        missing_components = [comp for comp in required_components if comp not in content]
        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        
        print("✅ Simple main app structure is valid")
        
    except Exception as e:
        print(f"❌ Error checking simple main app: {e}")
        return False
    
    # Test 2: Check simple models
    print("\n2. Testing simple models...")
    try:
        simple_models_file = project_root / "app" / "models" / "simple_models.py"
        
        if not simple_models_file.exists():
            print("❌ Simple models file not found")
            return False
        
        with open(simple_models_file, 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            "class SimpleArticle",
            "class SimpleQuery",
            "to_dict",
            "from_dict"
        ]
        
        missing_components = [comp for comp in required_components if comp not in content]
        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        
        print("✅ Simple models structure is valid")
        
    except Exception as e:
        print(f"❌ Error checking simple models: {e}")
        return False
    
    # Test 3: Check requirements
    print("\n3. Testing requirements...")
    try:
        requirements_file = project_root / "requirements-no-pydantic.txt"
        
        if not requirements_file.exists():
            print("❌ No-pydantic requirements file not found")
            return False
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Check that pydantic is not included (excluding comments)
        lines = content.split('\n')
        package_lines = [line for line in lines if not line.strip().startswith('#') and line.strip()]
        package_content = '\n'.join(package_lines)
        
        if "pydantic" in package_content.lower():
            print(f"❌ Pydantic found in no-pydantic requirements: {package_content}")
            return False
        
        # Check for essential packages
        essential_packages = ["fastapi", "uvicorn", "motor", "redis"]
        missing_packages = [pkg for pkg in essential_packages if pkg not in content.lower()]
        if missing_packages:
            print(f"❌ Missing essential packages: {missing_packages}")
            return False
        
        print("✅ Requirements file is valid")
        
    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
        return False
    
    # Test 4: Check Dockerfile
    print("\n4. Testing Dockerfile...")
    try:
        dockerfile = project_root / "Dockerfile.simple-app"
        
        if not dockerfile.exists():
            print("❌ Simple app Dockerfile not found")
            return False
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            "FROM python:3.11-slim",
            "requirements-no-pydantic.txt",
            "app.simple_main"
        ]
        
        missing_components = [comp for comp in required_components if comp not in content]
        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        
        print("✅ Simple app Dockerfile is valid")
        
    except Exception as e:
        print(f"❌ Error checking Dockerfile: {e}")
        return False
    
    print("\n🎉 All simple app tests passed!")
    return True


def main():
    """Main test function."""
    success = test_simple_app()
    
    if success:
        print("\n📋 Simple app is ready for Docker build!")
        print("   This version avoids compilation issues by:")
        print("   - Using Python 3.11 (better wheel support)")
        print("   - Avoiding pydantic (no Rust compilation)")
        print("   - Using minimal dependencies")
        print("   - Simple FastAPI app without complex validation")
        
        print("\n🚀 Next steps:")
        print("   1. Run: scripts\\fix-docker-build.bat")
        print("   2. Wait for build to complete (should be fast)")
        print("   3. Test: curl http://localhost:8000/health")
        
        return 0
    else:
        print("\n❌ Simple app tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
