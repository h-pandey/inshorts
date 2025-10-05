"""
Test script to verify Docker setup.
"""

import requests
import time
import sys
from typing import Dict, Any


def test_endpoint(url: str, expected_status: int = 200) -> bool:
    """Test an endpoint and return success status."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {url} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {url} - Expected: {expected_status}, Got: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {url} - Error: {e}")
        return False


def test_health_endpoint() -> Dict[str, Any]:
    """Test the health endpoint and return health status."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint - Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Redis: {data.get('redis', 'unknown')}")
            return data
        else:
            print(f"❌ Health endpoint - Status: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint - Error: {e}")
        return {}


def main():
    """Main test function."""
    print("🧪 Testing Docker setup...")
    print("=" * 50)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Test endpoints
    endpoints = [
        ("http://localhost:8000/", 200),
        ("http://localhost:8000/health", 200),
        ("http://localhost:8000/docs", 200),
    ]
    
    results = []
    for url, expected_status in endpoints:
        results.append(test_endpoint(url, expected_status))
    
    # Test health endpoint in detail
    print("\n🔍 Detailed health check:")
    health_data = test_health_endpoint()
    
    # Test admin UIs (optional)
    print("\n🌐 Testing admin UIs:")
    admin_endpoints = [
        ("http://localhost:8081", 200),  # MongoDB Express
        ("http://localhost:8082", 200),  # Redis Commander
    ]
    
    for url, expected_status in admin_endpoints:
        results.append(test_endpoint(url, expected_status))
    
    # Summary
    print("\n" + "=" * 50)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 All tests passed! ({success_count}/{total_count})")
        print("\n📋 Service URLs:")
        print("  📊 Application: http://localhost:8000")
        print("  📚 API Docs: http://localhost:8000/docs")
        print("  🔍 Health Check: http://localhost:8000/health")
        print("  🗄️  MongoDB Admin: http://localhost:8081")
        print("  🔴 Redis Admin: http://localhost:8082")
        return 0
    else:
        print(f"❌ Some tests failed! ({success_count}/{total_count})")
        print("\n🔧 Troubleshooting:")
        print("  1. Check if all services are running: docker-compose ps")
        print("  2. Check service logs: docker-compose logs")
        print("  3. Verify .env file configuration")
        print("  4. Check if ports are available")
        return 1


if __name__ == "__main__":
    sys.exit(main())
