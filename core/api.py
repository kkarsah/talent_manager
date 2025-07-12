# core/api.py
"""
Core API Routes for Talent Manager
Contains main system endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
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

    @classmethod
    def from_orm(cls, talent):
        """Custom method to handle datetime serialization"""
        return cls(
            id=talent.id,
            name=talent.name,
            specialization=talent.specialization,
            personality=talent.personality,
            is_active=talent.is_active,
            created_at=talent.created_at.isoformat() if talent.created_at else "",
        )


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
        db.execute(text("SELECT 1"))
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
@router.get("/talents", tags=["Talents"])
def list_talents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all talents"""
    talents = db.query(Talent).offset(skip).limit(limit).all()

    # Manual serialization to handle datetime
    talent_list = []
    for talent in talents:
        talent_dict = {
            "id": talent.id,
            "name": talent.name,
            "specialization": talent.specialization,
            "personality": talent.personality,
            "is_active": talent.is_active,
            "created_at": talent.created_at.isoformat() if talent.created_at else "",
        }
        talent_list.append(talent_dict)

    return {"talents": talent_list}


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
            "created_at": talent.created_at.isoformat() if talent.created_at else "",
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
@router.get("/content", tags=["Content"])
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


# Pydantic model for content creation
class ContentCreate(BaseModel):
    talent_id: int
    title: str
    topic: Optional[str] = None
    content_type: str = "long_form"
    platform: str = "youtube"
    generate_video: bool = False


@router.post("/content", tags=["Content"])
def create_content(content_data: ContentCreate, db: Session = Depends(get_db)):
    """Create new content item with optional script generation"""
    try:
        # Validate talent exists
        talent = db.query(Talent).filter(Talent.id == content_data.talent_id).first()
        if not talent:
            raise HTTPException(status_code=404, detail="Talent not found")

        # Create content item
        db_content = ContentItem(
            talent_id=content_data.talent_id,
            title=content_data.title,
            description=content_data.topic or f"Content about {content_data.title}",
            content_type=content_data.content_type,
            platform=content_data.platform,
            status="draft",
        )

        # Generate script if requested
        if content_data.topic:
            try:
                # Simple script generation for testing
                script = f"""
[Opening: Introduction]
Welcome! Today we're learning about {content_data.topic}.

[Main: Content] 
{content_data.topic} is an important topic in {talent.specialization}.
Let me explain the key concepts and practical applications.

[Closing: Conclusion]
That's a wrap on {content_data.topic}! Thanks for watching!
"""
                db_content.script = script
                db_content.status = "script_ready"

            except Exception as e:
                logger.warning(f"Script generation failed: {e}")
                db_content.script = f"Script for: {content_data.title}"

        db.add(db_content)
        db.commit()
        db.refresh(db_content)

        return {
            "message": "Content created successfully",
            "content": {
                "id": db_content.id,
                "title": db_content.title,
                "description": db_content.description,
                "script": db_content.script,
                "content_type": db_content.content_type,
                "platform": db_content.platform,
                "status": db_content.status,
                "talent_id": db_content.talent_id,
                "created_at": (
                    db_content.created_at.isoformat() if db_content.created_at else ""
                ),
            },
        }

    except Exception as e:
        logger.error(f"Content creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
        result = db.execute(text("SELECT COUNT(*) FROM talents")).fetchone()
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
