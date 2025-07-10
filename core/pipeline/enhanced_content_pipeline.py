# core/pipeline/enhanced_content_pipeline.py
"""
Enhanced Content Pipeline - NO MoviePy Dependencies
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class EnhancedContentPipeline:
    """Enhanced pipeline without any MoviePy dependencies"""

    def __init__(self):
        # Initialize components lazily to avoid circular imports
        self._content_pipeline = None

        # No Runway for now - focus on working basic system
        self.runway_enabled = False
        logger.info("✅ Enhanced content pipeline initialized (no MoviePy)")

    @property
    def content_pipeline(self):
        """Lazy load basic content pipeline"""
        if self._content_pipeline is None:
            try:
                from core.pipeline.content_pipeline import ContentPipeline

                self._content_pipeline = ContentPipeline()
            except ImportError as e:
                logger.error(f"Could not import ContentPipeline: {e}")
                raise
        return self._content_pipeline

    async def create_enhanced_content(
        self,
        talent_name: str,
        topic: Optional[str] = None,
        content_type: str = "long_form",
        auto_upload: bool = False,
        use_runway: bool = False,
    ) -> Dict[str, Any]:
        """Create enhanced content without MoviePy"""

        try:
            logger.info(f"Creating enhanced content for {talent_name}")
            logger.info(f"Topic: {topic}")
            logger.info(f"Type: {content_type}")

            # Get talent information
            talent = await self._get_talent_by_name(talent_name)
            if not talent:
                logger.error(f"Talent {talent_name} not found")
                return {"success": False, "error": f"Talent {talent_name} not found"}

            # Use the regular content pipeline (which now uses our fixed video creator)
            result = await self.content_pipeline.create_and_upload_content(
                talent.id, topic, content_type, auto_upload
            )

            # Add enhanced metadata
            if result.get("success"):
                result.update(
                    {
                        "enhanced": True,
                        "runway_used": False,  # Not using Runway for now
                        "scenes_generated": 0,
                        "talent_name": talent_name,
                        "enhanced_features": [
                            "Professional video frames",
                            "Progress indicators",
                            "Modern design themes",
                            "Intelligent text wrapping",
                        ],
                    }
                )

                logger.info(f"✅ Enhanced content created successfully")
            else:
                logger.error(f"Enhanced content creation failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Enhanced content creation error: {e}")
            return {"success": False, "error": str(e)}

    async def _get_talent_by_name(self, talent_name: str):
        """Get talent by name"""
        try:
            # Handle special case for alex
            if talent_name.lower() in ["alex", "alex_codemaster"]:
                # Create a mock talent object for Alex
                class MockTalent:
                    def __init__(self):
                        self.id = 1
                        self.name = "Alex CodeMaster"
                        self.specialization = "Tech Education"

                return MockTalent()

            # For other talents, try to get from database
            from core.database.config import SessionLocal
            from core.database.models import Talent

            db = SessionLocal()
            try:
                talent = (
                    db.query(Talent)
                    .filter(Talent.name.ilike(f"%{talent_name}%"))
                    .first()
                )
                return talent
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error getting talent {talent_name}: {e}")
            return None
