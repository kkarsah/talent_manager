# core/pipeline/enhanced_content_pipeline.py
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EnhancedContentPipeline:
    """Enhanced content pipeline with autonomous research integration"""
    
    def __init__(self):
        self._tts_service = None
        self._content_generator = None
        self._video_creator = None
    
    @property
    def tts_service(self):
        if self._tts_service is None:
            from core.content.tts import TTSService
            self._tts_service = TTSService()
        return self._tts_service
    
    @property
    def content_generator(self):
        if self._content_generator is None:
            from core.content.generator import ContentGenerator
            self._content_generator = ContentGenerator()
        return self._content_generator
    
    @property
    def video_creator(self):
        if self._video_creator is None:
            try:
                from core.content.enhanced_video_creator import EnhancedVideoCreator
                self._video_creator = EnhancedVideoCreator()
            except ImportError:
                from core.content.video_creator import VideoCreator
                self._video_creator = VideoCreator()
        return self._video_creator
    
    async def create_enhanced_content(
        self,
        talent_name: str,
        topic: str = None,
        content_type: str = "long_form",
        auto_upload: bool = False,
        use_runway: bool = False,
        research_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhanced content creation with autonomous research integration"""
        
        job_id = f"enhanced_{talent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"🎬 Starting enhanced content creation for {talent_name}")
            
            # If no topic provided, use autonomous research to find one
            if not topic:
                topic = await self._autonomous_topic_selection(talent_name)
            
            # Generate content using existing pipeline
            from core.content.generator import ContentRequest
            
            content_request = ContentRequest(
                talent_name=talent_name,
                topic=topic,
                content_type=content_type
            )
            
            generated_content = await self.content_generator.generate_content(content_request)
            
            # Clean script for TTS
            from core.content.script_cleaner import ScriptCleaner
            tts_script = ScriptCleaner.extract_spoken_content(generated_content.script, talent_name)
            
            logger.info(f"📊 Script cleaning: {len(generated_content.script)} → {len(tts_script)} chars")
            
            # Generate audio
            voice_settings = await self._get_voice_settings(talent_name)
            audio_path = await self.tts_service.generate_speech(
                tts_script,
                voice_settings,
                f"enhanced_audio_{job_id}.mp3"
            )
            
            # Create video
            video_path = await self.video_creator.create_video(
                generated_content.script,
                audio_path,
                generated_content.title,
                content_type,
                talent_name
            )
            
            # Upload if requested
            youtube_url = None
            if auto_upload and video_path:
                try:
                    from platforms.youtube.service import YouTubeService
                    youtube_service = YouTubeService()
                    
                    if youtube_service.is_authenticated():
                        youtube_url = await youtube_service.upload_video(
                            video_path,
                            generated_content.title,
                            generated_content.description,
                            getattr(generated_content, 'tags', [])
                        )
                except Exception as e:
                    logger.warning(f"YouTube upload failed: {e}")
            
            return {
                "success": True,
                "job_id": job_id,
                "talent_name": talent_name,
                "title": generated_content.title,
                "topic": topic,
                "content_type": content_type,
                "autonomous": True,
                "audio_path": audio_path,
                "video_path": video_path,
                "youtube_url": youtube_url,
                "tts_script_length": len(tts_script),
                "full_script_length": len(generated_content.script)
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced content creation failed: {e}")
            return {
                "success": False,
                "job_id": job_id,
                "talent_name": talent_name,
                "topic": topic,
                "error": str(e),
                "autonomous": True
            }
    
    async def _autonomous_topic_selection(self, talent_name: str) -> str:
        """Autonomous topic selection using research"""
        
        try:
            from core.research.autonomous_researcher import AutonomousResearcher
            
            # Get talent specialization
            talent_specialization = "tech_education"  # Default for Alex
            
            # Perform quick research
            async with AutonomousResearcher(talent_specialization) as researcher:
                topics = await researcher.research_trending_topics(limit=10)
            
            if topics:
                # Select best topic
                best_topic = topics[0]
                logger.info(f"🎯 Auto-selected topic: {best_topic.title}")
                return best_topic.title
            else:
                # Fallback to curated topics
                return "Latest Programming Trends Every Developer Should Know"
                
        except Exception as e:
            logger.warning(f"Autonomous topic selection failed: {e}")
            return "Latest Tech Trends for Developers"
    
    async def _get_voice_settings(self, talent_name: str) -> Dict[str, Any]:
        """Get voice settings for specific talent"""
        
        try:
            from core.content.tts import TALENT_VOICE_PROFILES
            return TALENT_VOICE_PROFILES.get(talent_name, {})
        except ImportError:
            # Fallback voice settings
            if "alex" in talent_name.lower():
                return {
                    "provider": "elevenlabs",
                    "voice_id": "alex_tech_voice",
                    "stability": 0.6,
                    "similarity_boost": 0.7,
                    "style": "enthusiastic"
                }
            else:
                return {}
