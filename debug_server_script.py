#!/usr/bin/env python3
"""
Debug Server Script - Get detailed error information
This will help us see exactly what's causing the 500 errors
"""

import requests
import subprocess
import time
import json
from pathlib import Path


def start_server_with_logs():
    """Start server and capture logs"""
    print("🚀 Starting server with detailed logging...")

    # Start server with verbose output
    server = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Wait for server to start
    for attempt in range(10):
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server started (attempt {attempt + 1})")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Server failed to start")
        return None

    return server


def test_endpoints_with_details():
    """Test endpoints and get detailed error information"""
    print("\n🔍 Testing endpoints with detailed error capture...")

    base_url = "http://localhost:8000"

    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/status", "System Status"),
        ("/api/system/info", "System Info"),
        ("/api/talents", "List Talents"),
        ("/api/content", "List Content"),
    ]

    for endpoint, description in endpoints:
        print(f"\n🧪 Testing: {description}")
        print(f"URL: {base_url}{endpoint}")

        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                print("✅ SUCCESS")
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"Response: {response.text[:200]}...")
            else:
                print("❌ FAILED")
                print(f"Headers: {dict(response.headers)}")
                print(f"Error Response: {response.text}")

                # Try to get more details
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    try:
                        error_data = response.json()
                        print(f"Error Details: {json.dumps(error_data, indent=2)}")
                    except:
                        pass

        except Exception as e:
            print(f"💥 REQUEST FAILED: {e}")


def test_talent_creation():
    """Test talent creation with detailed error handling"""
    print("\n🎭 Testing Talent Creation with Details...")

    talent_data = {
        "name": "Debug Test Talent",
        "specialization": "Debugging",
        "personality": {"tone": "analytical", "expertise": "troubleshooting"},
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/talents", json=talent_data, timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            print("✅ Talent creation successful!")
            data = response.json()
            print(f"Created talent: {data}")
        else:
            print("❌ Talent creation failed!")

            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error: {response.text}")

    except Exception as e:
        print(f"💥 Talent creation request failed: {e}")


def check_database_directly():
    """Check database directly without going through API"""
    print("\n🗄️  Testing Database Directly...")

    try:
        import sys

        sys.path.append(".")

        from core.database.config import SessionLocal, test_db_connection
        from core.database.models import Talent, ContentItem

        # Test connection
        if test_db_connection():
            print("✅ Direct database connection successful")
        else:
            print("❌ Direct database connection failed")
            return

        # Test queries
        db = SessionLocal()
        try:
            talent_count = db.query(Talent).count()
            content_count = db.query(ContentItem).count()

            print(f"📊 Direct database results:")
            print(f"   Talents: {talent_count}")
            print(f"   Content: {content_count}")

            # Try to get talents
            talents = db.query(Talent).limit(5).all()
            print(f"   Sample talents: {len(talents)}")
            for talent in talents:
                print(f"     - {talent.name} ({talent.specialization})")

        except Exception as e:
            print(f"❌ Direct database query failed: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"💥 Database test failed: {e}")


def check_imports():
    """Check if all required imports work"""
    print("\n📦 Testing Critical Imports...")

    imports_to_test = [
        ("core.database.config", "Database config"),
        ("core.database.models", "Database models"),
        ("core.api", "Core API"),
        ("main", "Main application"),
    ]

    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}: {module_name}")
        except Exception as e:
            print(f"❌ {description}: {module_name} - {e}")


def main():
    """Main debug function"""
    print("🐛 Talent Manager Debug Tool")
    print("=" * 40)

    # Check imports first
    check_imports()

    # Check database directly
    check_database_directly()

    # Start server and test
    server = start_server_with_logs()
    if not server:
        print("❌ Cannot proceed without server")
        return

    try:
        # Wait a moment for full startup
        time.sleep(2)

        # Test endpoints
        test_endpoints_with_details()

        # Test talent creation
        test_talent_creation()

    finally:
        # Clean up
        print("\n🛑 Stopping server...")
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

        # Show any server logs
        if server.stderr:
            stderr_output = server.stderr.read()
            if stderr_output:
                print("\n📋 Server Error Logs:")
                print(stderr_output[:1000])  # Show first 1000 chars

        if server.stdout:
            stdout_output = server.stdout.read()
            if stdout_output:
                print("\n📋 Server Output Logs:")
                print(stdout_output[:1000])  # Show first 1000 chars


if __name__ == "__main__":
    main()
