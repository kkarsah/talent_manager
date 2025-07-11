# main.py - Complete FastAPI Application
"""
Talent Manager - AI Content Creation System
Complete FastAPI application with all components
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Core imports
from core.database.config import get_db, init_db
from core.database.models import Base, Talent, ContentItem
from core.api import router as core_router


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Talent Manager API...")

    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

    # Test database connection
    try:
        from core.database.config import SessionLocal

        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

    logger.info("🎉 Talent Manager API started successfully!")
    yield
    logger.info("🛑 Shutting down Talent Manager API...")


# Initialize FastAPI app
app = FastAPI(
    title="Talent Manager",
    description="AI Talent Manager System for Autonomous Content Creation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core API routes
app.include_router(core_router, prefix="/api")


# Root redirect to docs
@app.get("/", include_in_schema=False)
def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")


# Try to include Alex CodeMaster integration
try:
    from talents.tech_educator.api import alex_router

    app.include_router(alex_router, prefix="/api")
    logger.info("✅ Alex CodeMaster integration loaded")
    ALEX_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Alex CodeMaster not available: {e}")
    ALEX_AVAILABLE = False


# Add system info endpoint
@app.get("/api/system/info", tags=["System"])
def system_info():
    """Get system information and available features"""
    return {
        "system": "Talent Manager",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "core_api": True,
            "alex_codemaster": ALEX_AVAILABLE,
            "dalle_video_creator": True,  # This is working!
            "database": True,
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "talents": "/api/talents",
            "content": "/api/content",
            "analytics": "/api/analytics/overview",
        },
    }


# Development server
if __name__ == "__main__":
    import uvicorn

    logger.info("🔧 Starting development server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
