# main.py - Fixed version with proper error handling

import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import Optional

# Core imports that should work
from core.database.config import get_db, init_db
from core.database.models import Talent, ContentItem

# Add this line with your other imports
from core.database.config import get_db, init_db, SessionLocal

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Talent Manager API",
    description="AI Talent Manager System for Autonomous Content Creation",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import optional dependencies
try:
    from core.pipeline.content_pipeline import ContentPipeline

    content_pipeline = ContentPipeline()
    PIPELINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Content pipeline not available: {e}")
    content_pipeline = None
    PIPELINE_AVAILABLE = False

try:
    from platforms.youtube.service import YouTubeService

    youtube_service = YouTubeService()
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"YouTube service not available: {e}")
    youtube_service = None
    YOUTUBE_AVAILABLE = False

# Try to import Celery tasks
try:
    from core.tasks.content_tasks import generate_content_task, check_content_schedule
    from celery_app import celery_app

    # Test Celery connection
    celery_app.control.ping(timeout=1.0)
    CELERY_AVAILABLE = True
    logger.info("Celery tasks loaded and connected successfully")
except Exception as e:
    logger.warning(f"Celery tasks not available: {e}")
    CELERY_AVAILABLE = False


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Talent Manager API...")
    init_db()
    logger.info("Database initialized")


# Health check endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Talent Manager API is running",
        "version": "1.0.0",
        "status": "healthy",
        "services": {
            "pipeline": PIPELINE_AVAILABLE,
            "youtube": YOUTUBE_AVAILABLE,
            "celery": CELERY_AVAILABLE,
        },
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected" if os.getenv("REDIS_URL") else "not configured",
        "services": {
            "content_pipeline": PIPELINE_AVAILABLE,
            "youtube_service": YOUTUBE_AVAILABLE,
            "celery_tasks": CELERY_AVAILABLE,
        },
        "apis": {
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
            "elevenlabs": (
                "configured" if os.getenv("ELEVENLABS_API_KEY") else "not configured"
            ),
            "youtube": (
                "configured" if os.getenv("YOUTUBE_CLIENT_ID") else "not configured"
            ),
        },
    }


# Talent management endpoints
@app.get("/talents")
async def list_talents(db: Session = Depends(get_db)):
    """List all talents"""
    talents = db.query(Talent).filter(Talent.is_active == True).all()
    return {"talents": talents}


@app.post("/talents")
async def create_talent(talent_data: dict, db: Session = Depends(get_db)):
    """Create a new talent"""
    talent = Talent(
        name=talent_data["name"],
        specialization=talent_data["specialization"],
        personality=talent_data.get("personality", {}),
        avatar_url=talent_data.get("avatar_url"),
        voice_id=talent_data.get("voice_id"),
    )
    db.add(talent)
    db.commit()
    db.refresh(talent)
    return {"talent": talent, "message": "Talent created successfully"}


@app.get("/talents/{talent_id}")
async def get_talent(talent_id: int, db: Session = Depends(get_db)):
    """Get talent by ID"""
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")
    return {"talent": talent}


@app.put("/talents/{talent_id}")
async def update_talent(
    talent_id: int, talent_data: dict, db: Session = Depends(get_db)
):
    """Update talent"""
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    for key, value in talent_data.items():
        setattr(talent, key, value)

    db.commit()
    db.refresh(talent)
    return {"talent": talent, "message": "Talent updated successfully"}


# Content management endpoints
@app.get("/content")
async def list_content(talent_id: int = None, db: Session = Depends(get_db)):
    """List content items"""
    query = db.query(ContentItem)
    if talent_id:
        query = query.filter(ContentItem.talent_id == talent_id)

    content_items = query.order_by(ContentItem.created_at.desc()).all()
    return {"content": content_items}


@app.post("/content")
async def create_content(content_data: dict, db: Session = Depends(get_db)):
    """Create new content item"""
    content = ContentItem(
        talent_id=content_data["talent_id"],
        title=content_data["title"],
        content_type=content_data.get("content_type", "long_form"),
        platform=content_data.get("platform", "youtube"),
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return {"content": content, "message": "Content created successfully"}


# Celery-powered endpoints (only if Celery is available)
@app.post("/content/generate")
async def generate_content_async(
    talent_id: int, topic: Optional[str] = None, content_type: str = "long_form"
):
    """Generate content asynchronously using Celery"""
    if not CELERY_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Celery tasks not available. Install dependencies and start worker.",
        )

    try:
        # Validate talent exists
        db = SessionLocal()
        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        db.close()

        if not talent:
            raise HTTPException(status_code=404, detail="Talent not found")

        # Queue content generation task
        task = generate_content_task.delay(talent_id, topic, content_type)

        return {
            "message": "Content generation queued",
            "task_id": task.id,
            "talent_id": talent_id,
            "topic": topic or "random topic",
            "content_type": content_type,
            "status": "queued",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/check/{talent_id}")
async def check_talent_schedule(talent_id: int):
    """Check if talent needs content and schedule if needed"""
    if not CELERY_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Celery tasks not available. Install dependencies and start worker.",
        )

    try:
        task = check_content_schedule.delay(talent_id)
        result = task.get(timeout=30)  # Quick check
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Task status endpoint
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a Celery task"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery tasks not available.")

    try:
        from celery_app import celery_app

        task = celery_app.AsyncResult(task_id)

        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": "Waiting for processing",
            }
        elif task.state == "SUCCESS":
            response = {"task_id": task_id, "state": task.state, "result": task.result}
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "state": task.state,
                "error": str(task.info),
            }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Alex CodeMaster creation endpoint
@app.post("/talents/alex-codemaster")
async def create_alex_codemaster(db: Session = Depends(get_db)):
    """Create Alex CodeMaster talent"""
    try:
        from talents.education_specialist.alex_codemaster import AlexCodeMasterProfile

        # Check if Alex already exists
        existing = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
        if existing:
            return {"message": "Alex CodeMaster already exists", "talent": existing}

        # Create Alex CodeMaster
        alex_profile = AlexCodeMasterProfile()
        talent = Talent(
            name=alex_profile.profile["basic_info"]["name"],
            specialization=alex_profile.profile["basic_info"]["specialization"],
            personality=alex_profile.profile["personality"],
            is_active=True,
        )

        db.add(talent)
        db.commit()
        db.refresh(talent)

        return {
            "message": "Alex CodeMaster created successfully",
            "talent": talent,
            "profile": alex_profile.profile["basic_info"],
        }

    except ImportError:
        # Fallback: create basic Alex CodeMaster
        existing = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
        if existing:
            return {"message": "Alex CodeMaster already exists", "talent": existing}

        talent = Talent(
            name="Alex CodeMaster",
            specialization="Programming Tutorials",
            personality={"tone": "friendly", "expertise": "programming"},
            is_active=True,
        )
        db.add(talent)
        db.commit()
        db.refresh(talent)

        return {
            "message": "Alex CodeMaster created successfully (basic version)",
            "talent": talent,
        }


# Install dependencies endpoint
@app.get("/install-guide")
async def get_install_guide():
    """Get installation guide for missing dependencies"""
    missing_deps = []

    if not PIPELINE_AVAILABLE:
        missing_deps.append("content pipeline dependencies")
    if not YOUTUBE_AVAILABLE:
        missing_deps.append(
            "google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        )
    if not CELERY_AVAILABLE:
        missing_deps.append("celery redis")

    return {
        "missing_dependencies": missing_deps,
        "install_commands": [
            "pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client",
            "pip install celery redis flower",
            "pip install openai elevenlabs",
        ],
        "setup_steps": [
            "1. Install missing dependencies with pip commands above",
            "2. Start Redis: docker run -d -p 6379:6379 redis:alpine",
            "3. Start Celery worker: celery -A celery_app worker --loglevel=info",
            "4. Restart the API server",
        ],
    }


# Add this endpoint to your main.py
@app.post("/content/generate-now")
async def generate_content_now(
    talent_id: int,
    topic: Optional[str] = None,
    content_type: str = "long_form",
    db: Session = Depends(get_db),
):
    """Generate content immediately (non-async)"""
    try:
        # Validate talent exists
        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        if not talent:
            raise HTTPException(status_code=404, detail="Talent not found")

        # Import and use the pipeline
        from core.pipeline.content_pipeline import quick_generate_content

        # Generate content
        result = await quick_generate_content(talent_id, topic, content_type)

        return {
            "message": "Content generated successfully",
            "talent_id": talent_id,
            "talent_name": talent.name,
            "topic": topic or "random topic",
            "content_type": content_type,
            "result": result,
            "status": "completed",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Content generation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
