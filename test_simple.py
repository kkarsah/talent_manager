#!/usr/bin/env python3
"""
Simple test to verify FastAPI application works
"""


def test_imports():
    """Test that all imports work"""

    try:
        print("🧪 Testing imports...")

        # Test core database imports
        from core.database.config import SessionLocal, engine, init_db

        print("✅ Database config imports work")

        # Test core API imports
        from core.api import router

        print("✅ Core API imports work")

        # Test main app import
        from main import app

        print("✅ Main app imports work")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database():
    """Test database functionality"""

    try:
        print("🧪 Testing database...")

        from core.database.config import SessionLocal, init_db
        from sqlalchemy import text

        # Initialize database
        init_db()
        print("✅ Database initialization successful")

        # Test connection
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1")).fetchone()
            print("✅ Database connection test passed")
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def main():
    """Run all tests"""

    print("🚀 Simple FastAPI Test")
    print("=" * 25)

    if test_imports():
        print("\n🎉 All imports working!")

        if test_database():
            print("\n🎉 Database working!")

            print("\n✅ FastAPI application is ready!")
            print("\n🎮 Start the server:")
            print("   python main.py")

        else:
            print("\n⚠️  Database issues remain")
    else:
        print("\n❌ Import issues remain")


if __name__ == "__main__":
    main()
