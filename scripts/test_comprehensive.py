"""
Comprehensive test script for the Contextual News API project.
Tests both local setup and Docker configuration.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple


class TestResult:
    """Test result container."""
    
    def __init__(self, name: str, success: bool, message: str = "", details: str = ""):
        self.name = name
        self.success = success
        self.message = message
        self.details = details


class ComprehensiveTester:
    """Comprehensive test suite for the project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: List[TestResult] = []
    
    def run_test(self, test_func, *args, **kwargs) -> TestResult:
        """Run a test function and record the result."""
        try:
            result = test_func(*args, **kwargs)
            if isinstance(result, TestResult):
                self.results.append(result)
                return result
            else:
                # If test function returns boolean, create TestResult
                success = bool(result)
                test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
                result_obj = TestResult(test_name, success, "Test completed" if success else "Test failed")
                self.results.append(result_obj)
                return result_obj
        except Exception as e:
            test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
            result = TestResult(test_name, False, f"Test failed with exception: {e}")
            self.results.append(result)
            return result
    
    def test_project_structure(self) -> TestResult:
        """Test if all required files and directories exist."""
        required_files = [
            "app/main.py",
            "app/core/config.py",
            "app/core/database.py",
            "app/core/redis_client.py",
            "app/models/article.py",
            "app/models/query.py",
            "requirements.txt",
            "docker-compose.yml",
            "Dockerfile",
            "README.md",
            "IMPLEMENTATION_DECISIONS.md"
        ]
        
        required_dirs = [
            "app",
            "app/api",
            "app/core", 
            "app/models",
            "app/services",
            "app/utils",
            "tests",
            "scripts"
        ]
        
        missing_files = []
        missing_dirs = []
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).is_dir():
                missing_dirs.append(dir_path)
        
        if missing_files or missing_dirs:
            message = "Missing files or directories"
            details = f"Missing files: {missing_files}\nMissing dirs: {missing_dirs}"
            return TestResult("Project Structure", False, message, details)
        else:
            return TestResult("Project Structure", True, "All required files and directories exist")
    
    def test_python_version(self) -> TestResult:
        """Test Python version compatibility."""
        try:
            version = sys.version_info
            if version >= (3, 11):
                return TestResult("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro} is compatible")
            else:
                return TestResult("Python Version", False, f"Python {version.major}.{version.minor}.{version.micro} is not compatible (requires 3.11+)")
        except Exception as e:
            return TestResult("Python Version", False, f"Error checking Python version: {e}")
    
    def test_requirements_file(self) -> TestResult:
        """Test if requirements.txt is valid."""
        try:
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                return TestResult("Requirements File", False, "requirements.txt not found")
            
            with open(requirements_file, 'r') as f:
                lines = f.readlines()
            
            valid_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            
            if len(valid_lines) > 0:
                return TestResult("Requirements File", True, f"Found {len(valid_lines)} valid dependencies")
            else:
                return TestResult("Requirements File", False, "No valid dependencies found")
        except Exception as e:
            return TestResult("Requirements File", False, f"Error reading requirements.txt: {e}")
    
    def test_docker_files(self) -> TestResult:
        """Test Docker configuration files."""
        docker_files = [
            "docker-compose.yml",
            "Dockerfile", 
            "Dockerfile.dev",
            "docker-compose.dev.yml",
            ".dockerignore"
        ]
        
        missing_files = []
        for file_name in docker_files:
            if not (self.project_root / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            return TestResult("Docker Files", False, f"Missing Docker files: {missing_files}")
        else:
            return TestResult("Docker Files", True, "All Docker configuration files exist")
    
    def test_docker_compose_config(self) -> TestResult:
        """Test Docker Compose configuration validity."""
        try:
            result = subprocess.run(
                ["docker-compose", "config"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return TestResult("Docker Compose Config", True, "Docker Compose configuration is valid")
            else:
                return TestResult("Docker Compose Config", False, f"Docker Compose config error: {result.stderr}")
        except subprocess.TimeoutExpired:
            return TestResult("Docker Compose Config", False, "Docker Compose config check timed out")
        except FileNotFoundError:
            return TestResult("Docker Compose Config", False, "Docker Compose not found - please install Docker Desktop")
        except Exception as e:
            return TestResult("Docker Compose Config", False, f"Error checking Docker Compose: {e}")
    
    def test_environment_file(self) -> TestResult:
        """Test environment configuration."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / "env.example"
        
        if not env_example.exists():
            return TestResult("Environment File", False, "env.example not found")
        
        if not env_file.exists():
            return TestResult("Environment File", False, ".env file not found - please copy from env.example")
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            if "OPENAI_API_KEY=your_openai_api_key_here" in content:
                return TestResult("Environment File", False, "Please update OPENAI_API_KEY in .env file")
            else:
                return TestResult("Environment File", True, ".env file exists and appears configured")
        except Exception as e:
            return TestResult("Environment File", False, f"Error reading .env file: {e}")
    
    def test_news_data_file(self) -> TestResult:
        """Test if news data file exists and is valid JSON."""
        news_data_file = self.project_root / "news_data.json"
        
        if not news_data_file.exists():
            return TestResult("News Data File", False, "news_data.json not found")
        
        try:
            with open(news_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                # Check if it has the expected structure
                sample = data[0]
                required_fields = ['id', 'title', 'description', 'url', 'publication_date', 'source_name', 'category', 'relevance_score', 'latitude', 'longitude']
                
                missing_fields = [field for field in required_fields if field not in sample]
                
                if missing_fields:
                    return TestResult("News Data File", False, f"Missing fields in news data: {missing_fields}")
                else:
                    return TestResult("News Data File", True, f"Valid news data with {len(data)} articles")
            else:
                return TestResult("News Data File", False, "News data is not a valid list or is empty")
        except json.JSONDecodeError as e:
            return TestResult("News Data File", False, f"Invalid JSON in news_data.json: {e}")
        except Exception as e:
            return TestResult("News Data File", False, f"Error reading news_data.json: {e}")
    
    def test_docker_availability(self) -> TestResult:
        """Test if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                return TestResult("Docker Availability", True, f"Docker is available: {version}")
            else:
                return TestResult("Docker Availability", False, "Docker command failed")
        except subprocess.TimeoutExpired:
            return TestResult("Docker Availability", False, "Docker command timed out")
        except FileNotFoundError:
            return TestResult("Docker Availability", False, "Docker not found - please install Docker Desktop")
        except Exception as e:
            return TestResult("Docker Availability", False, f"Error checking Docker: {e}")
    
    def test_docker_desktop_running(self) -> TestResult:
        """Test if Docker Desktop is running."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return TestResult("Docker Desktop Running", True, "Docker Desktop is running")
            else:
                return TestResult("Docker Desktop Running", False, "Docker Desktop is not running - please start Docker Desktop")
        except subprocess.TimeoutExpired:
            return TestResult("Docker Desktop Running", False, "Docker info command timed out")
        except Exception as e:
            return TestResult("Docker Desktop Running", False, f"Error checking Docker status: {e}")
    
    def run_all_tests(self) -> None:
        """Run all tests."""
        print("🧪 Running Comprehensive Tests for Contextual News API")
        print("=" * 60)
        
        # Core tests
        self.run_test(self.test_project_structure)
        self.run_test(self.test_python_version)
        self.run_test(self.test_requirements_file)
        self.run_test(self.test_docker_files)
        self.run_test(self.test_environment_file)
        self.run_test(self.test_news_data_file)
        
        # Docker tests
        self.run_test(self.test_docker_availability)
        self.run_test(self.test_docker_desktop_running)
        self.run_test(self.test_docker_compose_config)
        
        # Print results
        self.print_results()
    
    def print_results(self) -> None:
        """Print test results."""
        print("\n📊 Test Results:")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} {result.name}")
            if result.message:
                print(f"    {result.message}")
            if result.details:
                print(f"    Details: {result.details}")
            print()
            
            if result.success:
                passed += 1
            else:
                failed += 1
        
        print("=" * 60)
        print(f"📈 Summary: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! The project is ready for development.")
        else:
            print("⚠️  Some tests failed. Please address the issues above.")
        
        # Provide next steps
        self.print_next_steps()
    
    def print_next_steps(self) -> None:
        """Print next steps based on test results."""
        print("\n🚀 Next Steps:")
        print("=" * 60)
        
        docker_available = any(r.name == "Docker Availability" and r.success for r in self.results)
        docker_running = any(r.name == "Docker Desktop Running" and r.success for r in self.results)
        
        if docker_available and docker_running:
            print("1. 🐳 Start the application with Docker:")
            print("   docker-compose up --build -d")
            print()
            print("2. 🔍 Check service health:")
            print("   docker-compose ps")
            print()
            print("3. 📚 Access the application:")
            print("   - API: http://localhost:8000")
            print("   - Docs: http://localhost:8000/docs")
            print("   - Health: http://localhost:8000/health")
            print()
            print("4. 🗄️  Access admin UIs:")
            print("   - MongoDB: http://localhost:8081 (admin/admin123)")
            print("   - Redis: http://localhost:8082 (admin/admin123)")
        elif docker_available:
            print("1. 🐳 Start Docker Desktop")
            print("2. 🚀 Then run: docker-compose up --build -d")
        else:
            print("1. 🐳 Install Docker Desktop")
            print("2. 🚀 Then run: docker-compose up --build -d")
        
        print("\n📖 For detailed instructions, see:")
        print("   - README.md")
        print("   - DOCKER_SETUP.md")
        print("   - INSTALL.md")


def main():
    """Main function."""
    tester = ComprehensiveTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
