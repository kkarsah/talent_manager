# core/pipeline/enhanced_content_pipeline.py - CLEAN WORKING VERSION
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from core.content.enhanced_scene_service import EnhancedSceneService
from core.content.video_stitching_service import VideoStitchingService
from typing import List  # Add if not already imported
import uuid  # Add if not already imported
from core.content.enhanced_scene_service import EnhancedSceneService
from core.content.video_stitching_service import VideoStitchingService
from core.content.enhanced_scene_service import EnhancedSceneService
from core.content.video_stitching_service import VideoStitchingService


logger = logging.getLogger(__name__)


class EnhancedContentPipeline:
    """Enhanced content pipeline - WORKING VERSION"""

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

    @property
    def scene_service(self):
        """Enhanced scene generation service"""
        if not hasattr(self, "_scene_service") or self._scene_service is None:
            self._scene_service = EnhancedSceneService()
        return self._scene_service

    @property
    def stitching_service(self):
        """Video stitching service"""
        if not hasattr(self, "_stitching_service") or self._stitching_service is None:
            self._stitching_service = VideoStitchingService()
        return self._stitching_service

    @property
    def scene_service(self):
        """Enhanced scene generation service"""
        if not hasattr(self, "_scene_service") or self._scene_service is None:
            self._scene_service = EnhancedSceneService()
        return self._scene_service

    @property
    def stitching_service(self):
        """Video stitching service"""
        if not hasattr(self, "_stitching_service") or self._stitching_service is None:
            self._stitching_service = VideoStitchingService()
        return self._stitching_service

    async def create_enhanced_content(
        self,
        talent_name: str,
        topic: str = None,
        content_type: str = "long_form",
        auto_upload: bool = False,
        use_cogvideox: Optional[bool] = None,
        force_static: bool = False,
    ) -> Dict[str, Any]:
        """Enhanced content creation with CogVideoX integration"""

        job_id = f"enhanced_{talent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"🎬 Starting enhanced content creation for {talent_name}")

            # Generate content using existing pipeline
            from core.content.generator import ContentRequest

            content_request = ContentRequest(
                talent_name=talent_name,
                topic=topic or "Programming Tutorial",
                content_type=content_type,
            )

            generated_content = await self.content_generator.generate_content(
                content_request
            )

            # Clean script for TTS
            from core.content.script_cleaner import ScriptCleaner

            tts_script = ScriptCleaner.extract_spoken_content(
                generated_content.script, talent_name
            )

            logger.info(
                f"📊 Script cleaning: {len(generated_content.script)} → {len(tts_script)} chars"
            )

            # Generate audio
            voice_settings = {
                "provider": "elevenlabs",
                "voice_id": f"{talent_name.lower()}_voice",
            }
            audio_path = await self.tts_service.generate_speech(
                tts_script, voice_settings, f"enhanced_audio_{job_id}.mp3"
            )

            # ENHANCED VIDEO CREATION WITH SERVICES
            if hasattr(self, "scene_service") and hasattr(self, "stitching_service"):
                logger.info("🎨 Using enhanced services for video creation")
                video_path = await self._create_video_with_services(
                    generated_content.script,
                    audio_path,
                    generated_content.title,
                    content_type,
                    talent_name,
                    use_cogvideox=use_cogvideox,
                    force_static=force_static,
                )
            else:
                logger.info("📹 Using fallback video creator")
                video_path = await self.video_creator.create_video(
                    generated_content.script,
                    audio_path,
                    generated_content.title,
                    content_type,
                    talent_name,
                )

            # Determine method used
            if force_static:
                method = "static_scenes"
            elif video_path and "_cogvideox_" in str(video_path):
                method = "cogvideox"
            elif video_path and "_hybrid_" in str(video_path):
                method = "hybrid"
            else:
                method = "enhanced_scenes"

            result = {
                "success": True,
                "job_id": job_id,
                "title": generated_content.title,
                "description": generated_content.description,
                "tags": generated_content.tags,
                "video_path": video_path,
                "audio_path": audio_path,
                "video_creation_method": method,
                "upload_result": None,
                "enhanced": True,
                "services_used": {
                    "scene_service": hasattr(self, "_scene_service"),
                    "stitching_service": hasattr(self, "_stitching_service"),
                },
                "duration": 0,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Enhanced content creation completed: {job_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Enhanced content creation failed: {e}")
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
                "enhanced": False,
                "timestamp": datetime.now().isoformat(),
            }

    async def _create_video_with_services(
        self,
        script: str,
        audio_path: str,
        title: str,
        content_type: str,
        talent_name: str,
        use_cogvideox: Optional[bool] = None,
        force_static: bool = False,
    ) -> Optional[str]:
        """Create video using enhanced services"""

        try:
            logger.info(f"🎬 Creating video with enhanced services")

            # Parse scenes from script
            scenes = self._parse_scenes_from_script(script)
            logger.info(f"📋 Parsed {len(scenes)} scenes from script")

            # Get audio duration for timing
            audio_duration = await self._get_audio_duration(audio_path)
            if not audio_duration:
                logger.warning("Could not determine audio duration, using default")
                audio_duration = 60.0

            # Configure services based on force_static
            if force_static and hasattr(self.scene_service, "use_cogvideox"):
                original_cogvideox = self.scene_service.use_cogvideox
                self.scene_service.use_cogvideox = False

            # Generate scene content
            scene_result = await self.scene_service.generate_scene_content(
                scenes=scenes,
                content_type=content_type,
                talent_name=talent_name,
                audio_duration=audio_duration,
            )

            # Restore original setting
            if force_static and hasattr(self.scene_service, "use_cogvideox"):
                self.scene_service.use_cogvideox = original_cogvideox

            if not scene_result.get("success", False):
                logger.error(f"Scene generation failed: {scene_result.get('error')}")
                # Fallback to regular video creator
                return await self.video_creator.create_video(
                    script, audio_path, title, content_type, talent_name
                )

            # Create final video filename
            method = scene_result.get("method", "unknown")
            video_id = str(uuid.uuid4())[:8]
            output_filename = f"{content_type}_{method}_{video_id}.mp4"

            # Stitch segments with audio
            logger.info(
                f"🔧 Stitching {len(scene_result.get('segments', []))} segments using {method}"
            )

            final_video_path = await self.stitching_service.stitch_segments_with_audio(
                segments=scene_result.get("segments", []),
                audio_path=audio_path,
                output_filename=output_filename,
                content_type=content_type,
            )

            if final_video_path:
                logger.info(f"✅ Enhanced video created: {final_video_path}")
                return final_video_path
            else:
                logger.error("Video stitching failed, using fallback")
                return await self.video_creator.create_video(
                    script, audio_path, title, content_type, talent_name
                )

        except Exception as e:
            logger.error(f"Enhanced video creation failed: {e}")
            # Fallback to regular video creator
            return await self.video_creator.create_video(
                script, audio_path, title, content_type, talent_name
            )

    def _parse_scenes_from_script(self, script: str) -> List[Dict[str, str]]:
        """Parse scenes from script with scene markers"""

        scenes = []
        lines = script.split("\n")
        current_scene = None

        for line in lines:
            line = line.strip()

            # Look for scene markers like [Scene: description] or [Opening: description]
            if line.startswith("[") and "]:" in line:
                if current_scene:
                    scenes.append(current_scene)

                # Extract scene description
                scene_desc = line[1 : line.find("]:")]
                current_scene = {"description": scene_desc, "content": ""}
            elif current_scene and line and not line.startswith("["):
                # Add content to current scene
                current_scene["content"] += line + " "

        # Add final scene
        if current_scene:
            scenes.append(current_scene)

        # If no explicit scenes found, create default scenes based on content
        if not scenes:
            # Split into logical sections for scene generation
            content_parts = script.split("\n\n")  # Split by paragraphs

            if len(content_parts) >= 3:
                scenes = [
                    {
                        "description": "Professional tech studio with Alex CodeMaster",
                        "content": content_parts[0],
                    },
                    {
                        "description": "Code editor and development workspace",
                        "content": content_parts[1],
                    },
                    {
                        "description": "Live demonstration and examples",
                        "content": content_parts[2] if len(content_parts) > 2 else "",
                    },
                ]
            else:
                scenes = [
                    {
                        "description": "Professional educational environment",
                        "content": script,
                    }
                ]

        return scenes

    async def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get audio duration using ffprobe"""
        try:
            import subprocess

            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                audio_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                logger.error(f"ffprobe failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Audio duration detection failed: {e}")
            return None

    def get_video_capabilities(self) -> Dict[str, Any]:
        """Get video creation capabilities"""
        return {
            "cogvideox_available": hasattr(self, "_scene_service")
            and self.scene_service.get_capabilities().get("cogvideox_available", False),
            "enhanced_scenes_available": hasattr(self, "_scene_service"),
            "fallback_available": True,
            "services_initialized": {
                "scene_service": hasattr(self, "_scene_service"),
                "stitching_service": hasattr(self, "_stitching_service"),
            },
            "current_method": (
                "enhanced_scenes" if hasattr(self, "_scene_service") else "basic_scenes"
            ),
        }


# SERVICE INTEGRATION - ADD TO YOUR EXISTING CLASS


# Add these properties to your EnhancedContentPipeline class
@property
def scene_service(self):
    """Enhanced scene generation service"""
    if not hasattr(self, "_scene_service") or self._scene_service is None:
        self._scene_service = EnhancedSceneService()
    return self._scene_service


@property
def stitching_service(self):
    """Video stitching service"""
    if not hasattr(self, "_stitching_service") or self._stitching_service is None:
        self._stitching_service = VideoStitchingService()
    return self._stitching_service
