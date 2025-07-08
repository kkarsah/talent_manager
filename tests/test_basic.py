# tests/test_basic.py

import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from core.database.config import get_db
from core.database.models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Talent Manager API is running"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_talents_empty(client):
    """Test listing talents when none exist"""
    response = client.get("/talents")
    assert response.status_code == 200
    assert response.json()["talents"] == []


def test_create_talent(client):
    """Test creating a new talent"""
    talent_data = {
        "name": "Test Talent",
        "specialization": "Testing",
        "personality": {"tone": "professional", "expertise_level": "expert"},
    }
    response = client.post("/talents", json=talent_data)
    assert response.status_code == 200
    assert response.json()["talent"]["name"] == "Test Talent"
    assert response.json()["message"] == "Talent created successfully"


def test_get_talent(client):
    """Test getting a specific talent"""
    # First create a talent
    talent_data = {"name": "Test Talent 2", "specialization": "Testing Advanced"}
    create_response = client.post("/talents", json=talent_data)
    talent_id = create_response.json()["talent"]["id"]

    # Then get it
    response = client.get(f"/talents/{talent_id}")
    assert response.status_code == 200
    assert response.json()["talent"]["name"] == "Test Talent 2"


def test_get_nonexistent_talent(client):
    """Test getting a talent that doesn't exist"""
    response = client.get("/talents/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Talent not found"


def test_create_content(client):
    """Test creating content for a talent"""
    # First create a talent
    talent_data = {"name": "Content Creator", "specialization": "Content Creation"}
    talent_response = client.post("/talents", json=talent_data)
    talent_id = talent_response.json()["talent"]["id"]

    # Then create content
    content_data = {
        "talent_id": talent_id,
        "title": "Test Video",
        "content_type": "long_form",
        "platform": "youtube",
    }
    response = client.post("/content", json=content_data)
    assert response.status_code == 200
    assert response.json()["content"]["title"] == "Test Video"


def test_list_content(client):
    """Test listing content"""
    response = client.get("/content")
    assert response.status_code == 200
    assert "content" in response.json()


def test_performance_metrics(client):
    """Test getting performance metrics"""
    response = client.get("/analytics/performance")
    assert response.status_code == 200
    assert "metrics" in response.json()
