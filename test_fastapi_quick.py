#!/usr/bin/env python3
"""
Test the FastAPI application
"""

import requests
import time
import subprocess
import signal
import os
from pathlib import Path


def test_api_endpoints():
    """Test API endpoints"""

    base_url = "http://localhost:8000"

    endpoints_to_test = [
        ("/", "Root redirect"),
        ("/api/health", "Health check"),
        ("/api/status", "System status"),
        ("/api/talents", "List talents"),
        ("/api/content", "List content"),
        ("/api/analytics/overview", "Analytics overview"),
        ("/api/system/info", "System info"),
        ("/docs", "API documentation"),
    ]

    print("🧪 Testing API endpoints...")

    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code in [200, 307] else "❌"
            print(f"{status} {description}: {endpoint} -> {response.status_code}")

            # Show response for key endpoints
            if (
                endpoint in ["/api/health", "/api/system/info"]
                and response.status_code == 200
            ):
                print(f"    Response: {response.json()}")

        except Exception as e:
            print(f"❌ {description}: {endpoint} -> ERROR: {e}")


def test_talent_creation():
    """Test creating a talent"""

    base_url = "http://localhost:8000"

    talent_data = {
        "name": "Test Talent",
        "specialization": "Testing",
        "personality": {"tone": "professional", "expertise_level": "expert"},
    }

    try:
        response = requests.post(f"{base_url}/api/talents", json=talent_data, timeout=5)
        if response.status_code == 200:
            print("✅ Talent creation test: SUCCESS")
            print(f"    Response: {response.json()}")
        else:
            print(f"❌ Talent creation test: FAILED - {response.status_code}")
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"❌ Talent creation test: ERROR - {e}")


def run_quick_test():
    """Run a quick test without starting a server"""

    print("🚀 Quick FastAPI Application Test")
    print("=" * 40)

    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        print("✅ Server is already running!")

        # Test endpoints
        test_api_endpoints()

        print("\n🧪 Testing talent creation...")
        test_talent_creation()

    except requests.exceptions.ConnectionError:
        print("ℹ️  Server not running. Start it manually with:")
        print("   python main.py")
        print("\nThen run this test again:")
        print("   python test_fastapi_quick.py")


def run_full_test():
    """Run the full test with server startup"""

    print("🚀 Full FastAPI Application Test")
    print("=" * 40)

    # Start the server
    print("🔧 Starting development server...")
    server = subprocess.Popen(
        ["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)

    try:
        # Test endpoints
        test_api_endpoints()

        print("\n🧪 Testing talent creation...")
        test_talent_creation()

        print("\n🎉 FastAPI application test completed!")
        print("\n📋 Next steps:")
        print("1. Visit http://localhost:8000/docs for API documentation")
        print("2. Test creating a talent: POST /api/talents")
        print("3. Check system status: GET /api/status")

    finally:
        # Stop the server
        print("\n🛑 Stopping test server...")
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        run_full_test()
    else:
        run_quick_test()
