# core/database/config.py
"""
Database configuration for Talent Manager
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./talent_manager.db")

# Create engine
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    from .models import Base

    Base.metadata.create_all(bind=engine)


def test_db_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        # Use text() for raw SQL queries
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


def get_db_info():
    """Get database information"""
    try:
        db = SessionLocal()

        # Get table count using text()
        table_result = db.execute(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        ).fetchone()
        table_count = table_result[0] if table_result else 0

        db.close()

        return {
            "url": SQLALCHEMY_DATABASE_URL,
            "engine": str(engine),
            "table_count": table_count,
        }
    except Exception as e:
        return {"url": SQLALCHEMY_DATABASE_URL, "engine": str(engine), "error": str(e)}
