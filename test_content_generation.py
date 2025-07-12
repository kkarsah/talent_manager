#!/usr/bin/env python3
"""
Simple Content Generation Test
"""

from fastapi.testclient import TestClient
from main import app
import json


def test_content_generation():
    """Test content generation endpoint"""
    client = TestClient(app)

    print("🧪 Testing Content Generation")
    print("=" * 30)

    # First create a talent
    talent_data = {"name": "Content Test Talent", "specialization": "Content Testing"}

    print("Creating test talent...")
    talent_response = client.post("/api/talents", json=talent_data)
    print(f"Talent creation status: {talent_response.status_code}")

    if talent_response.status_code != 200:
        print(f"❌ Failed to create talent: {talent_response.text}")
        return False

    talent_id = talent_response.json()["talent"]["id"]
    print(f"✅ Created talent with ID: {talent_id}")

    # Test content generation
    content_data = {
        "talent_id": talent_id,
        "title": "Test Content",
        "topic": "Python basics",
        "content_type": "short_form",
        "platform": "youtube",
    }

    print("Testing content generation...")
    response = client.post("/api/content", json=content_data)
    print(f"Content generation status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Content generation successful!")
        data = response.json()
        print(f"Generated content: {data.get('content', {}).get('title')}")
        return True
    else:
        print(f"❌ Content generation failed: {response.text}")
        return False


if __name__ == "__main__":
    success = test_content_generation()
    if success:
        print("\n🎉 Content generation test passed!")
    else:
        print("\n❌ Content generation test failed!")
