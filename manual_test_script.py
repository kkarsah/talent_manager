#!/usr/bin/env python3
"""
Manual test to isolate the 500 error issue
"""


def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")

    try:
        print("Testing core imports...")
        from core.database.config import get_db, SessionLocal, init_db
        from core.database.models import Talent, ContentItem, Base

        print("✅ Core imports successful")

        print("Testing API imports...")
        from core.api import router

        print("✅ API imports successful")

        print("Testing main app...")
        from main import app

        print("✅ Main app import successful")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_database():
    """Test database operations directly"""
    print("\n🗄️  Testing database...")

    try:
        from core.database.config import SessionLocal, init_db
        from core.database.models import Talent

        # Initialize database
        print("Initializing database...")
        init_db()
        print("✅ Database initialized")

        # Test basic operations
        db = SessionLocal()
        try:
            # Count talents
            count = db.query(Talent).count()
            print(f"✅ Talent count: {count}")

            # Try to create a talent
            test_talent = Talent(
                name="Manual Test Talent",
                specialization="Manual Testing",
                personality={"test": True},
            )
            db.add(test_talent)
            db.commit()
            db.refresh(test_talent)
            print(f"✅ Created talent with ID: {test_talent.id}")

            return True
        except Exception as e:
            print(f"❌ Database operation failed: {e}")
            return False
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_api_directly():
    """Test API endpoints directly using FastAPI TestClient"""
    print("\n🔌 Testing API directly...")

    try:
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        # Test health endpoint
        print("Testing /api/health...")
        response = client.get("/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("✅ Health endpoint works")

        # Test talents endpoint
        print("Testing /api/talents...")
        response = client.get("/api/talents")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
            print(f"Headers: {response.headers}")
        else:
            print("✅ Talents endpoint works")
            print(f"Response: {response.json()}")

        # Test talent creation
        print("Testing talent creation...")
        talent_data = {
            "name": "API Test Talent",
            "specialization": "API Testing",
            "personality": {"direct_test": True},
        }
        response = client.post("/api/talents", json=talent_data)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("✅ Talent creation works")
            print(f"Response: {response.json()}")

        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all manual tests"""
    print("🔧 Manual Diagnostic Test")
    print("=" * 30)

    tests_passed = 0
    total_tests = 3

    # Test 1: Imports
    if test_imports():
        tests_passed += 1

    # Test 2: Database
    if test_database():
        tests_passed += 1

    # Test 3: API
    if test_api_directly():
        tests_passed += 1

    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All manual tests passed! The issue might be with server startup.")
    else:
        print("⚠️  Some tests failed. This shows us where the problem is.")


if __name__ == "__main__":
    main()
