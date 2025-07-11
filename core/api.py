# core/api.py
"""
Core API Routes for Talent Manager
Contains main system endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from .database.config import get_db
from .database.models import Talent, ContentItem, PerformanceMetric

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter()


# Pydantic models for API requests/responses
class TalentCreate(BaseModel):
    name: str
    specialization: str
    personality: dict = {}
    avatar_url: Optional[str] = None
    voice_id: Optional[str] = None


class TalentResponse(BaseModel):
    id: int
    name: str
    specialization: str
    personality: dict
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class ContentItemResponse(BaseModel):
    id: int
    talent_id: int
    title: str
    description: Optional[str]
    content_type: str
    platform: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class SystemStatus(BaseModel):
    status: str
    version: str
    database_connected: bool
    active_talents: int
    total_content_items: int


# Health and status endpoints
@router.get("/", tags=["System"])
def root():
    """Root endpoint"""
    return {
        "message": "Talent Manager API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@router.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = False

    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
    }


@router.get("/status", response_model=SystemStatus, tags=["System"])
def system_status(db: Session = Depends(get_db)):
    """Get detailed system status"""
    try:
        active_talents = db.query(Talent).filter(Talent.is_active == True).count()
        total_content = db.query(ContentItem).count()
        db_connected = True
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        active_talents = 0
        total_content = 0
        db_connected = False

    return SystemStatus(
        status="operational" if db_connected else "degraded",
        version="1.0.0",
        database_connected=db_connected,
        active_talents=active_talents,
        total_content_items=total_content,
    )


# Talent management endpoints
@router.get("/talents", response_model=List[TalentResponse], tags=["Talents"])
def list_talents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all talents"""
    talents = db.query(Talent).offset(skip).limit(limit).all()
    return talents


@router.post("/talents", response_model=dict, tags=["Talents"])
def create_talent(talent: TalentCreate, db: Session = Depends(get_db)):
    """Create a new talent"""
    try:
        db_talent = Talent(
            name=talent.name,
            specialization=talent.specialization,
            personality=talent.personality,
            avatar_url=talent.avatar_url,
            voice_id=talent.voice_id,
        )
        db.add(db_talent)
        db.commit()
        db.refresh(db_talent)

        return {
            "message": "Talent created successfully",
            "talent": {
                "id": db_talent.id,
                "name": db_talent.name,
                "specialization": db_talent.specialization,
            },
        }
    except Exception as e:
        logger.error(f"Failed to create talent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/talents/{talent_id}", response_model=dict, tags=["Talents"])
def get_talent(talent_id: int, db: Session = Depends(get_db)):
    """Get a specific talent"""
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    return {
        "talent": {
            "id": talent.id,
            "name": talent.name,
            "specialization": talent.specialization,
            "personality": talent.personality,
            "is_active": talent.is_active,
            "created_at": talent.created_at.isoformat() if talent.created_at else None,
        }
    }


@router.delete("/talents/{talent_id}", tags=["Talents"])
def delete_talent(talent_id: int, db: Session = Depends(get_db)):
    """Delete a talent"""
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    # Soft delete - just mark as inactive
    talent.is_active = False
    db.commit()

    return {"message": f"Talent {talent.name} deactivated successfully"}


# Content management endpoints
@router.get("/content", response_model=List[ContentItemResponse], tags=["Content"])
def list_content(
    talent_id: Optional[int] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List content items with optional filters"""
    query = db.query(ContentItem)

    if talent_id:
        query = query.filter(ContentItem.talent_id == talent_id)
    if platform:
        query = query.filter(ContentItem.platform == platform)
    if status:
        query = query.filter(ContentItem.status == status)

    content_items = query.offset(skip).limit(limit).all()
    return content_items


@router.get("/content/{content_id}", tags=["Content"])
def get_content_item(content_id: int, db: Session = Depends(get_db)):
    """Get a specific content item"""
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")

    return {
        "content": {
            "id": content.id,
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type,
            "platform": content.platform,
            "status": content.status,
            "video_url": content.video_url,
            "platform_url": content.platform_url,
            "created_at": (
                content.created_at.isoformat() if content.created_at else None
            ),
            "published_at": (
                content.published_at.isoformat() if content.published_at else None
            ),
        }
    }


# Analytics endpoints
@router.get("/analytics/overview", tags=["Analytics"])
def analytics_overview(db: Session = Depends(get_db)):
    """Get analytics overview"""
    try:
        total_talents = db.query(Talent).count()
        active_talents = db.query(Talent).filter(Talent.is_active == True).count()
        total_content = db.query(ContentItem).count()
        published_content = (
            db.query(ContentItem).filter(ContentItem.status == "published").count()
        )

        return {
            "overview": {
                "total_talents": total_talents,
                "active_talents": active_talents,
                "total_content_items": total_content,
                "published_content": published_content,
                "success_rate": round(
                    (
                        (published_content / total_content * 100)
                        if total_content > 0
                        else 0
                    ),
                    1,
                ),
            }
        }
    except Exception as e:
        logger.error(f"Analytics overview failed: {e}")
        return {
            "overview": {
                "total_talents": 0,
                "active_talents": 0,
                "total_content_items": 0,
                "published_content": 0,
                "success_rate": 0,
            }
        }


@router.get("/analytics/talent/{talent_id}", tags=["Analytics"])
def talent_analytics(talent_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific talent"""
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    content_count = (
        db.query(ContentItem).filter(ContentItem.talent_id == talent_id).count()
    )
    published_count = (
        db.query(ContentItem)
        .filter(ContentItem.talent_id == talent_id, ContentItem.status == "published")
        .count()
    )

    # Get performance metrics if available
    total_views = (
        db.query(PerformanceMetric)
        .filter(PerformanceMetric.talent_id == talent_id)
        .with_entities(PerformanceMetric.views)
        .all()
    )

    total_views_sum = sum([v[0] for v in total_views if v[0]]) if total_views else 0

    return {
        "talent": talent.name,
        "analytics": {
            "total_content": content_count,
            "published_content": published_count,
            "total_views": total_views_sum,
            "success_rate": round(
                (published_count / content_count * 100) if content_count > 0 else 0, 1
            ),
        },
    }


# Utility endpoints
@router.post("/test/database", tags=["Testing"])
def test_database_connection(db: Session = Depends(get_db)):
    """Test database connection and operations"""
    try:
        # Test basic query
        result = db.execute("SELECT COUNT(*) FROM talents").fetchone()
        talent_count = result[0] if result else 0

        return {
            "status": "success",
            "message": "Database connection successful",
            "talent_count": talent_count,
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/config", tags=["System"])
def get_system_config():
    """Get system configuration (non-sensitive)"""
    import os

    return {
        "config": {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database_type": (
                "SQLite" if "sqlite" in os.getenv("DATABASE_URL", "") else "PostgreSQL"
            ),
            "features": {
                "openai_available": bool(os.getenv("OPENAI_API_KEY")),
                "elevenlabs_available": bool(os.getenv("ELEVENLABS_API_KEY")),
                "youtube_available": bool(os.getenv("YOUTUBE_CLIENT_ID")),
            },
        }
    }
