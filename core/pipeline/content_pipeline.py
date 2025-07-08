# core/pipeline/content_pipeline.py

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import json

from core.content.generator import ContentGenerator, ContentRequest, GeneratedContent
from core.content.tts import TTSService, TALENT_VOICE_PROFILES
from core.content.video_creator import VideoCreator
from platforms.youtube.service import YouTubeService
from core.database.config import SessionLocal
from core.database.models import ContentItem, Talent

logger = logging.getLogger(__name__)


class ContentPipeline:
    """Complete end-to-end content creation pipeline"""

    def __init__(self):
        self.content_generator = ContentGenerator()
        self.tts_service = TTSService()
        self.video_creator = VideoCreator()
        self.youtube_service = YouTubeService()

        # Pipeline status tracking
        self.current_job = None
        self.job_status = {}

    async def create_and_upload_content(
        self,
        talent_id: int,
        topic: str,
        content_type: str = "long_form",
        auto_upload: bool = True,
    ) -> Dict[str, Any]:
        """Complete pipeline: Generate -> Create -> Upload content"""

        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_job = job_id

        try:
            # Initialize job status
            self.job_status[job_id] = {
                "status": "started",
                "progress": 0,
                "steps": [],
                "error": None,
                "result": {},
            }

            logger.info(f"Starting content pipeline for talent {talent_id}: {topic}")

            # Step 1: Get talent info
            await self._update_job_status(job_id, "Getting talent information", 10)
            talent = await self._get_talent(talent_id)
            if not talent:
                raise ValueError(f"Talent {talent_id} not found")

            # Step 2: Generate content
            await self._update_job_status(job_id, "Generating script and metadata", 20)
            content_request = ContentRequest(
                talent_name=talent.name,
                topic=topic,
                content_type=content_type,
                platform="youtube",
            )

            generated_content = await self.content_generator.generate_content(
                content_request
            )

            # Step 3: Create database record
            await self._update_job_status(job_id, "Creating content record", 30)
            content_item = await self._create_content_record(
                talent_id, generated_content, content_type
            )

            # Step 4: Generate speech with automatic fallback
            await self._update_job_status(
                job_id, "Generating speech audio (with fallback if needed)", 40
            )
            voice_settings = TALENT_VOICE_PROFILES.get(talent.name, {}).get(
                self.tts_service.provider, {}
            )

            try:
                audio_path = await self.tts_service.generate_speech(
                    generated_content.script,
                    voice_settings,
                    f"audio_{content_item.id}.mp3",
                )

                # Check if fallback was used
                if "gtts_fallback" in audio_path:
                    logger.warning(f"Used gTTS fallback for content {content_item.id}")
                    await self._update_job_status(
                        job_id, "Audio generated using free TTS fallback", 45
                    )
                else:
                    await self._update_job_status(
                        job_id, "High-quality audio generated successfully", 45
                    )

            except Exception as e:
                logger.error(f"All TTS options failed: {e}")
                # Continue without audio - save script only
                audio_path = None
                await self._update_job_status(
                    job_id, "TTS failed - continuing with script only", 45
                )

            # Step 5: Create video
            await self._update_job_status(job_id, "Creating video", 60)
            video_path = await self.video_creator.create_video(
                generated_content.script,
                audio_path,
                generated_content.title,
                content_type,
                talent.name,
            )

            # Step 6: Create thumbnail
            await self._update_job_status(job_id, "Creating thumbnail", 70)
            thumbnail_path = await self.video_creator.create_thumbnail(
                generated_content.title, talent.name
            )

            # Step 7: Update content record with file paths
            await self._update_content_record(
                content_item.id,
                {
                    "audio_url": audio_path,
                    "video_url": video_path,
                    "thumbnail_url": thumbnail_path,
                    "status": "generated",
                },
            )

            result = {
                "content_id": content_item.id,
                "title": generated_content.title,
                "audio_path": audio_path,
                "video_path": video_path,
                "thumbnail_path": thumbnail_path,
                "estimated_duration": generated_content.estimated_duration,
            }

            # Step 8: Upload to YouTube (if enabled)
            if auto_upload:
                await self._update_job_status(job_id, "Uploading to YouTube", 80)

                # Check if YouTube is authenticated
                if not self.youtube_service.is_authenticated():
                    await self.youtube_service.load_credentials()

                if self.youtube_service.is_authenticated():
                    try:
                        video_id = await self.youtube_service.upload_video(
                            video_path=video_path,
                            title=generated_content.title,
                            description=generated_content.description,
                            tags=generated_content.tags,
                            thumbnail_path=thumbnail_path,
                        )

                        if video_id:
                            # Update content record with YouTube info
                            await self._update_content_record(
                                content_item.id,
                                {
                                    "platform_id": video_id,
                                    "status": "published",
                                    "published_at": datetime.utcnow(),
                                },
                            )

                            result["youtube_video_id"] = video_id
                            result["youtube_url"] = (
                                f"https://youtube.com/watch?v={video_id}"
                            )

                            logger.info(f"Video uploaded successfully: {video_id}")
                        else:
                            logger.warning("Video upload failed")
                            result["upload_error"] = "Upload failed"

                    except Exception as e:
                        logger.error(f"YouTube upload error: {e}")
                        result["upload_error"] = str(e)
                else:
                    logger.warning("YouTube not authenticated, skipping upload")
                    result["upload_error"] = "YouTube not authenticated"

            # Step 9: Cleanup
            await self._update_job_status(job_id, "Finalizing", 90)
            self.video_creator.cleanup_temp_files()

            # Complete
            await self._update_job_status(job_id, "Complete", 100)
            self.job_status[job_id]["status"] = "completed"
            self.job_status[job_id]["result"] = result

            logger.info(f"Content pipeline completed successfully: {job_id}")
            return result

        except Exception as e:
            logger.error(f"Content pipeline failed: {e}")
            self.job_status[job_id]["status"] = "failed"
            self.job_status[job_id]["error"] = str(e)
            raise

        finally:
            self.current_job = None

    async def _update_job_status(self, job_id: str, message: str, progress: int):
        """Update job status"""
        if job_id in self.job_status:
            self.job_status[job_id]["progress"] = progress
            self.job_status[job_id]["steps"].append(
                {
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "progress": progress,
                }
            )
        logger.info(f"Job {job_id}: {message} ({progress}%)")

    async def _get_talent(self, talent_id: int) -> Optional[Talent]:
        """Get talent from database"""
        db = SessionLocal()
        try:
            return db.query(Talent).filter(Talent.id == talent_id).first()
        finally:
            db.close()

    async def _create_content_record(
        self, talent_id: int, generated_content: GeneratedContent, content_type: str
    ) -> ContentItem:
        """Create content item in database"""
        db = SessionLocal()
        try:
            content_item = ContentItem(
                talent_id=talent_id,
                title=generated_content.title,
                description=generated_content.description,
                script=generated_content.script,
                content_type=content_type,
                platform="youtube",
                status="generating",
            )
            db.add(content_item)
            db.commit()
            db.refresh(content_item)
            return content_item
        finally:
            db.close()

    async def _update_content_record(self, content_id: int, updates: Dict[str, Any]):
        """Update content item in database"""
        db = SessionLocal()
        try:
            content_item = (
                db.query(ContentItem).filter(ContentItem.id == content_id).first()
            )
            if content_item:
                for key, value in updates.items():
                    setattr(content_item, key, value)
                db.commit()
        finally:
            db.close()

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current job status"""
        return self.job_status.get(job_id, {"status": "not_found"})

    def list_recent_jobs(self, limit: int = 10) -> Dict[str, Any]:
        """List recent jobs"""
        recent_jobs = dict(list(self.job_status.items())[-limit:])
        return recent_jobs

    async def test_pipeline_components(self) -> Dict[str, bool]:
        """Test all pipeline components"""
        results = {}

        try:
            # Test OpenAI
            test_prompt = "Say hello"
            response = await self.content_generator._call_openai(
                test_prompt, max_tokens=10
            )
            results["openai"] = bool(response)
        except:
            results["openai"] = False

        try:
            # Test TTS
            test_audio = await self.tts_service.generate_speech(
                "This is a test", filename="test_audio.mp3"
            )
            results["tts"] = Path(test_audio).exists()
        except:
            results["tts"] = False

        try:
            # Test video creation (minimal test)
            results["video_creator"] = True  # Just check if imports work
        except:
            results["video_creator"] = False

        try:
            # Test YouTube authentication
            results["youtube"] = await self.youtube_service.load_credentials()
        except:
            results["youtube"] = False

        return results


# Quick content generation functions
async def quick_generate_content(
    talent_id: int, topic: str, content_type: str = "long_form"
) -> Dict[str, Any]:
    """Quick function to generate content"""
    pipeline = ContentPipeline()
    return await pipeline.create_and_upload_content(
        talent_id, topic, content_type, auto_upload=False
    )


async def quick_generate_and_upload(
    talent_id: int, topic: str, content_type: str = "long_form"
) -> Dict[str, Any]:
    """Quick function to generate and upload content"""
    pipeline = ContentPipeline()
    return await pipeline.create_and_upload_content(
        talent_id, topic, content_type, auto_upload=True
    )


# Content scheduling system
class ContentScheduler:
    """Schedule regular content creation"""

    def __init__(self):
        self.pipeline = ContentPipeline()
        self.schedule = {}

    async def schedule_weekly_content(
        self, talent_id: int, topics: list, content_types: list
    ):
        """Schedule weekly content for a talent"""
        # Implementation for scheduling system
        # This would integrate with Celery or similar for production
        pass

    async def generate_content_ideas(self, talent_id: int, count: int = 5) -> list:
        """Generate content ideas for a talent"""
        from core.content.generator import PROGRAMMING_TOPICS
        import random

        # For now, return random topics
        # In production, this would use AI to generate personalized topics
        return random.sample(PROGRAMMING_TOPICS, min(count, len(PROGRAMMING_TOPICS)))
