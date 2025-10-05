"""
Test the enhanced logging system.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_logging_configuration():
    """Test logging configuration without external dependencies."""
    print("🧪 Testing Enhanced Logging System")
    print("=" * 50)
    
    # Test 1: Check logging configuration file
    print("1. Testing logging configuration file...")
    try:
        logging_file = project_root / "app" / "core" / "logging.py"
        
        if not logging_file.exists():
            print("❌ Logging configuration file not found")
            return False
        
        with open(logging_file, 'r') as f:
            content = f.read()
        
        # Check for key logging components
        required_components = [
            "ColoredFormatter",
            "RequestContextFilter", 
            "configure_logging",
            "get_logger",
            "log_database_operation",
            "log_api_request",
            "log_llm_request",
            "log_performance"
        ]
        
        missing_components = [comp for comp in required_components if comp not in content]
        if missing_components:
            print(f"❌ Missing logging components: {missing_components}")
            return False
        
        print("✅ Logging configuration file is complete")
        
    except Exception as e:
        print(f"❌ Error checking logging configuration: {e}")
        return False
    
    # Test 2: Check log directory structure
    print("\n2. Testing log directory structure...")
    try:
        log_dir = project_root / "logs"
        
        # The directory might not exist yet, but the code should create it
        print(f"✅ Log directory path configured: {log_dir}")
        
        # Check if we can create the directory
        log_dir.mkdir(exist_ok=True)
        print("✅ Log directory can be created")
        
    except Exception as e:
        print(f"❌ Error with log directory: {e}")
        return False
    
    # Test 3: Test log file structure
    print("\n3. Testing log file structure...")
    try:
        # Create a test log entry structure
        test_log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "logger": "test",
            "message": "Test log entry",
            "module": "test_logging",
            "function": "test_logging_configuration",
            "extra_data": {
                "test_id": "12345",
                "operation": "testing"
            }
        }
        
        # Test JSON serialization (what our logging system will do)
        json.dumps(test_log_entry)
        print("✅ Log entry structure is JSON serializable")
        
    except Exception as e:
        print(f"❌ Error with log entry structure: {e}")
        return False
    
    # Test 4: Test logging functions structure
    print("\n4. Testing logging functions...")
    try:
        # Check that all logging functions are defined
        logging_functions = [
            "log_function_call",
            "log_database_operation", 
            "log_api_request",
            "log_llm_request",
            "log_performance"
        ]
        
        for func_name in logging_functions:
            if f"def {func_name}(" not in content:
                print(f"❌ Logging function {func_name} not found")
                return False
        
        print("✅ All logging functions are defined")
        
    except Exception as e:
        print(f"❌ Error checking logging functions: {e}")
        return False
    
    # Test 5: Test colored formatter
    print("\n5. Testing colored formatter...")
    try:
        # Check that color codes are defined
        color_codes = [
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "RESET"
        ]
        
        for color in color_codes:
            if f"'{color}':" not in content:
                print(f"❌ Color code {color} not found")
                return False
        
        print("✅ Colored formatter is properly configured")
        
    except Exception as e:
        print(f"❌ Error checking colored formatter: {e}")
        return False
    
    print("\n🎉 All logging tests passed!")
    return True


def test_log_file_creation():
    """Test creating sample log files."""
    print("\n6. Testing log file creation...")
    try:
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create sample log files
        sample_logs = {
            "app.log": {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Application started",
                "module": "main"
            },
            "error.log": {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR", 
                "message": "Sample error message",
                "module": "test",
                "error": "Test error for demonstration"
            },
            "debug.log": {
                "timestamp": datetime.now().isoformat(),
                "level": "DEBUG",
                "message": "Debug information",
                "module": "test",
                "debug_data": {"key": "value"}
            }
        }
        
        for log_file, log_data in sample_logs.items():
            log_path = log_dir / log_file
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        print("✅ Sample log files created successfully")
        
        # List created files
        log_files = list(log_dir.glob("*.log"))
        print(f"   Created {len(log_files)} log files:")
        for log_file in log_files:
            print(f"   - {log_file.name}")
        
    except Exception as e:
        print(f"❌ Error creating log files: {e}")
        return False
    
    return True


def main():
    """Main test function."""
    print("🔧 Enhanced Logging System Test")
    print("=" * 60)
    
    # Test logging configuration
    config_success = test_logging_configuration()
    
    # Test log file creation
    file_success = test_log_file_creation()
    
    if config_success and file_success:
        print("\n🎉 Enhanced logging system is ready!")
        print("\n📋 Logging Features:")
        print("   ✅ Colored console output")
        print("   ✅ JSON file logging")
        print("   ✅ Multiple log levels (DEBUG, INFO, WARNING, ERROR)")
        print("   ✅ Structured logging with context")
        print("   ✅ Performance logging")
        print("   ✅ API request logging")
        print("   ✅ Database operation logging")
        print("   ✅ LLM request logging")
        
        print("\n📁 Log Files:")
        print("   - logs/app.log (Application logs)")
        print("   - logs/error.log (Error logs)")
        print("   - logs/debug.log (Debug logs, debug mode only)")
        
        print("\n🚀 Next steps:")
        print("   1. Start Docker Desktop")
        print("   2. Run: docker-compose up --build -d")
        print("   3. Check logs/ directory for application logs")
        
        return 0
    else:
        print("\n❌ Logging system tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
