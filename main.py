# main.py

import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi import BackgroundTasks
from core.pipeline.content_pipeline import (
    ContentPipeline,
    quick_generate_content,
    quick_generate_and_upload,
)
from core.content.generator import PROGRAMMING_TOPICS, get_random_topic
from platforms.youtube.service import YouTubeService

from core.database.config import get_db, init_db
from core.database.models import Talent, ContentItem, PerformanceMetric

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

# Initialize services
content_pipeline = ContentPipeline()
youtube_service = YouTubeService()


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Talent Manager API...")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Talent Manager API is running",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected" if os.getenv("REDIS_URL") else "not configured",
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
        description=content_data.get("description"),
        script=content_data.get("script"),
        content_type=content_data["content_type"],
        platform=content_data["platform"],
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return {"content": content, "message": "Content created successfully"}


# Analytics endpoints
@app.get("/analytics/performance")
async def get_performance_metrics(talent_id: int = None, db: Session = Depends(get_db)):
    """Get performance metrics"""
    query = db.query(PerformanceMetric)
    if talent_id:
        query = query.filter(PerformanceMetric.talent_id == talent_id)

    metrics = query.order_by(PerformanceMetric.recorded_at.desc()).all()
    return {"metrics": metrics}


# Content Generation Endpoints
@app.post("/content/generate")
async def generate_content(
    background_tasks: BackgroundTasks, request: dict, db: Session = Depends(get_db)
):
    """Generate content for a talent"""
    talent_id = request.get("talent_id")
    topic = request.get("topic")
    content_type = request.get("content_type", "long_form")
    auto_upload = request.get("auto_upload", False)

    if not talent_id or not topic:
        raise HTTPException(status_code=400, detail="talent_id and topic are required")

    # Check if talent exists
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    try:
        if auto_upload:
            result = await quick_generate_and_upload(talent_id, topic, content_type)
        else:
            result = await quick_generate_content(talent_id, topic, content_type)

        return {"message": "Content generated successfully", "result": result}
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Content generation failed: {str(e)}"
        )


@app.post("/content/generate-random")
async def generate_random_content(
    talent_id: int,
    content_type: str = "long_form",
    auto_upload: bool = False,
    db: Session = Depends(get_db),
):
    """Generate content with a random topic"""

    # Check if talent exists
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    # Get random topic
    topic = get_random_topic()

    try:
        if auto_upload:
            result = await quick_generate_and_upload(talent_id, topic, content_type)
        else:
            result = await quick_generate_content(talent_id, topic, content_type)

        return {
            "message": f"Random content generated: {topic}",
            "topic": topic,
            "result": result,
        }
    except Exception as e:
        logger.error(f"Random content generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Content generation failed: {str(e)}"
        )


@app.get("/content/topics")
async def get_content_topics():
    """Get available programming topics"""
    return {"topics": PROGRAMMING_TOPICS, "total": len(PROGRAMMING_TOPICS)}


@app.get("/content/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get content generation job status"""
    status = content_pipeline.get_job_status(job_id)
    return {"job_id": job_id, "status": status}


@app.get("/content/jobs")
async def list_recent_jobs():
    """List recent content generation jobs"""
    jobs = content_pipeline.list_recent_jobs()
    return {"jobs": jobs}


# YouTube Integration Endpoints
@app.get("/youtube/auth")
async def youtube_auth():
    """Start YouTube authentication"""
    try:
        auth_url = await youtube_service.authenticate()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"YouTube auth failed: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/auth/youtube/callback")
async def youtube_callback(code: str):
    """Handle YouTube OAuth callback"""
    try:
        success = await youtube_service.handle_callback(code)
        if success:
            return {"message": "YouTube authentication successful"}
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")
    except Exception as e:
        logger.error(f"YouTube callback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Callback failed: {str(e)}")


@app.get("/youtube/channel")
async def get_youtube_channel():
    """Get YouTube channel information"""
    try:
        if not youtube_service.is_authenticated():
            if not await youtube_service.load_credentials():
                raise HTTPException(status_code=401, detail="YouTube not authenticated")

        channel_info = await youtube_service.get_channel_info()
        return {"channel": channel_info}
    except Exception as e:
        logger.error(f"Failed to get channel info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get channel info: {str(e)}"
        )


@app.get("/youtube/videos")
async def list_youtube_videos(max_results: int = 10):
    """List recent YouTube videos"""
    try:
        if not youtube_service.is_authenticated():
            if not await youtube_service.load_credentials():
                raise HTTPException(status_code=401, detail="YouTube not authenticated")

        videos = await youtube_service.list_recent_videos(max_results)
        return {"videos": videos}
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list videos: {str(e)}")


@app.get("/youtube/analytics/{video_id}")
async def get_video_analytics(video_id: str):
    """Get analytics for a specific video"""
    try:
        if not youtube_service.is_authenticated():
            if not await youtube_service.load_credentials():
                raise HTTPException(status_code=401, detail="YouTube not authenticated")

        analytics = await youtube_service.get_video_analytics(video_id)
        return {"analytics": analytics}
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}"
        )


# System Testing Endpoints
@app.get("/system/test")
async def test_system_components():
    """Test all system components"""
    try:
        results = await content_pipeline.test_pipeline_components()

        # Add database test
        db = SessionLocal()
        try:
            talent_count = db.query(Talent).count()
            results["database"] = True
        except:
            results["database"] = False
        finally:
            db.close()

        # Calculate overall health
        total_components = len(results)
        working_components = sum(1 for v in results.values() if v)
        health_percentage = (working_components / total_components) * 100

        return {
            "components": results,
            "health": {
                "percentage": health_percentage,
                "working": working_components,
                "total": total_components,
                "status": (
                    "healthy"
                    if health_percentage >= 80
                    else "degraded" if health_percentage >= 50 else "unhealthy"
                ),
            },
        }
    except Exception as e:
        logger.error(f"System test failed: {e}")
        raise HTTPException(status_code=500, detail=f"System test failed: {str(e)}")


@app.post("/talents/alex-codemaster")
async def create_alex_codemaster(db: Session = Depends(get_db)):
    """Create the Alex CodeMaster talent with predefined settings"""
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


# TTS Testing Endpoints
@app.post("/tts/test")
async def test_tts(request: dict):
    """Test text-to-speech generation"""
    text = request.get("text", "Hello, this is a test of the text to speech system.")
    voice_settings = request.get("voice_settings", {})

    try:
        from core.content.tts import TTSService

        tts = TTSService()

        audio_path = await tts.generate_speech(text, voice_settings, "test_tts.mp3")

        return {
            "message": "TTS test successful",
            "audio_path": audio_path,
            "provider": tts.provider,
        }
    except Exception as e:
        logger.error(f"TTS test failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS test failed: {str(e)}")


@app.get("/tts/voices")
async def get_tts_voices():
    """Get available TTS voices"""
    try:
        from core.content.tts import TTSService

        tts = TTSService()
        voices = tts.get_voice_options()

        return {"provider": tts.provider, "voices": voices}
    except Exception as e:
        logger.error(f"Failed to get TTS voices: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get TTS voices: {str(e)}"
        )


# Content Ideas and Topics
@app.get("/content/ideas/{talent_id}")
async def get_content_ideas(
    talent_id: int, count: int = 5, db: Session = Depends(get_db)
):
    """Get content ideas for a talent"""

    # Check if talent exists
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    from core.pipeline.content_pipeline import ContentScheduler

    scheduler = ContentScheduler()

    ideas = await scheduler.generate_content_ideas(talent_id, count)

    return {"talent": talent.name, "ideas": ideas, "count": len(ideas)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
