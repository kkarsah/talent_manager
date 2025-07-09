# core/pipeline/enhanced_content_pipeline.py
"""
Enhanced Content Pipeline with Runway Integration
Extends existing content pipeline to support Alex CodeMaster's enhanced workflow
"""

from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

# Core imports
from core.pipeline.content_pipeline import ContentPipeline
from core.content.generator import ContentRequest
from talents.tech_educator.alex_codemaster import AlexCodeMaster

# Enhanced video generation
from runwayml import RunwayML
import os

logger = logging.getLogger(__name__)


class EnhancedContentPipeline(ContentPipeline):
    """Enhanced pipeline with Runway video generation and talent-specific processing"""

    def __init__(self):
        super().__init__()

        # Initialize Runway client
        runway_api_key = os.getenv("RUNWAY_API_KEY")
        if runway_api_key:
            self.runway_client = RunwayML()
            os.environ["RUNWAYML_API_SECRET"] = runway_api_key
            self.runway_enabled = True
        else:
            self.runway_client = None
            self.runway_enabled = False
            logger.warning(
                "Runway API key not found. Video generation will use fallback methods."
            )

        # Initialize talent instances
        self.alex_codemaster = AlexCodeMaster()

    async def create_enhanced_content(
        self,
        talent_name: str,
        topic: str = None,
        content_type: str = "long_form",
        auto_upload: bool = False,
        use_runway: bool = True,
    ) -> Dict[str, Any]:
        """Create content using enhanced pipeline with talent-specific processing"""

        job_id = f"enhanced_{talent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(
                f"🎬 Starting enhanced content creation for {talent_name}: {topic}"
            )

            # Step 1: Get talent instance and generate content request
            talent_instance = self._get_talent_instance(talent_name)
            if not talent_instance:
                raise ValueError(f"Talent {talent_name} not found or not supported")

            # Generate talent-specific content request
            content_request = await talent_instance.generate_content_request(
                topic=topic, content_type=content_type
            )

            # Step 2: Generate enhanced script and scenes
            logger.info("📝 Generating enhanced script with talent personality...")
            generated_content = await talent_instance.enhance_script_generation(
                content_request
            )

            # Step 3: Generate TTS audio using talent's voice settings
            logger.info("🎤 Generating voice audio...")
            voice_settings = talent_instance.get_voice_settings()
            audio_path = await self.tts_service.generate_speech(
                generated_content.script,
                voice_settings,
                f"audio_{talent_name}_{job_id}.mp3",
            )

            # Step 4: Generate video assets
            video_path = None
            if use_runway and self.runway_enabled and generated_content.visual_scenes:
                logger.info("🎥 Generating video with Runway...")
                video_path = await self._create_runway_video(
                    generated_content.visual_scenes, talent_instance, job_id
                )

            if not video_path:
                logger.info("🎞️ Using traditional video creation...")
                video_path = await self.video_creator.create_video(
                    generated_content.script,
                    audio_path,
                    generated_content.title,
                    content_type,
                    talent_name,
                )

            # Step 5: Create thumbnail
            logger.info("🖼️ Creating thumbnail...")
            thumbnail_path = await self.video_creator.create_thumbnail(
                generated_content.title, talent_name
            )

            # Step 6: Upload if requested
            youtube_result = {}
            if auto_upload and self.youtube_service.is_authenticated():
                logger.info("📤 Uploading to YouTube...")
                try:
                    video_id = await self.youtube_service.upload_video(
                        video_path=video_path,
                        title=generated_content.title,
                        description=generated_content.description,
                        tags=generated_content.tags,
                        thumbnail_path=thumbnail_path,
                    )

                    if video_id:
                        youtube_result = {
                            "youtube_video_id": video_id,
                            "youtube_url": f"https://youtube.com/watch?v={video_id}",
                            "uploaded": True,
                        }
                except Exception as e:
                    logger.error(f"YouTube upload failed: {e}")
                    youtube_result = {"upload_error": str(e)}

            result = {
                "success": True,
                "job_id": job_id,
                "talent_name": talent_name,
                "topic": content_request.topic,
                "title": generated_content.title,
                "description": generated_content.description,
                "tags": generated_content.tags,
                "content_type": content_type,
                "duration": generated_content.estimated_duration,
                "video_path": video_path,
                "audio_path": audio_path,
                "thumbnail_path": thumbnail_path,
                "runway_used": use_runway and self.runway_enabled,
                "scenes_generated": (
                    len(generated_content.visual_scenes)
                    if generated_content.visual_scenes
                    else 0
                ),
                **youtube_result,
            }

            logger.info(
                f"✅ Enhanced content creation completed: {generated_content.title}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Enhanced content creation failed: {e}")
            return {
                "success": False,
                "job_id": job_id,
                "talent_name": talent_name,
                "topic": topic,
                "error": str(e),
            }

    def _get_talent_instance(self, talent_name: str):
        """Get talent instance by name"""
        talent_map = {
            "alex_codemaster": self.alex_codemaster,
            "alex": self.alex_codemaster,  # Alias
        }
        return talent_map.get(talent_name.lower())

    async def _create_runway_video(
        self, visual_scenes: List[Dict[str, Any]], talent_instance, job_id: str
    ) -> Optional[str]:
        """Create video using Runway with talent-specific scenes"""

        if not self.runway_client or not visual_scenes:
            return None

        try:
            video_assets = []

            # Generate video for each scene
            for i, scene in enumerate(visual_scenes):
                logger.info(f"  Generating scene {i+1}/{len(visual_scenes)}...")

                # Create enhanced prompt for Runway
                runway_prompt = f"""
                {scene.get('description', '')}
                
                {talent_instance.config['visual_style']['aesthetic']}
                Environment: {talent_instance.config['visual_style']['environment']}
                Colors: {talent_instance.config['visual_style']['color_scheme']}
                Tech elements: {scene.get('tech_elements', 'modern developer tools')}
                
                Professional quality, 4K resolution, engaging for tech audience
                """

                # Generate base image
                image_task = self.runway_client.text_to_image.create(
                    model="gen4_image", prompt_text=runway_prompt, ratio="1920:1080"
                )

                # Wait for image completion
                while True:
                    await asyncio.sleep(2)
                    image_status = self.runway_client.tasks.retrieve(image_task.id)
                    if image_status.status in ["SUCCEEDED", "FAILED"]:
                        break

                if image_status.status == "SUCCEEDED":
                    base_image_url = image_status.output[0]

                    # Create video from image
                    video_task = self.runway_client.image_to_video.create(
                        model="gen4_turbo",
                        prompt_image=base_image_url,
                        prompt_text=f"Animate this tech scene: {runway_prompt}",
                        ratio="1920:1080",
                        duration=min(int(scene.get("duration", 6)), 10),
                    )

                    # Wait for video completion
                    while True:
                        await asyncio.sleep(10)
                        video_status = self.runway_client.tasks.retrieve(video_task.id)
                        if video_status.status in ["SUCCEEDED", "FAILED"]:
                            break

                    if video_status.status == "SUCCEEDED":
                        video_url = video_status.output[0]
                        video_assets.append(
                            {
                                "scene_id": f"scene_{i+1}",
                                "video_url": video_url,
                                "duration": scene.get("duration", 6),
                                "local_path": None,
                            }
                        )

            # Download and combine video assets using existing video creator
            if video_assets:
                return await self._combine_runway_assets(video_assets, job_id)

        except Exception as e:
            logger.error(f"Runway video generation failed: {e}")
            return None

        return None

    async def _combine_runway_assets(
        self, video_assets: List[Dict[str, Any]], job_id: str
    ) -> str:
        """Download and combine Runway video assets"""
        import requests
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        from pathlib import Path

        output_dir = Path("content/video")
        output_dir.mkdir(parents=True, exist_ok=True)

        clips = []

        # Download each video asset
        for asset in video_assets:
            try:
                response = requests.get(asset["video_url"], timeout=60)
                response.raise_for_status()

                local_path = output_dir / f"{asset['scene_id']}_{job_id}.mp4"
                with open(local_path, "wb") as f:
                    f.write(response.content)

                asset["local_path"] = str(local_path)
                clip = VideoFileClip(str(local_path))
                clips.append(clip)

            except Exception as e:
                logger.error(f"Error downloading {asset['scene_id']}: {e}")
                continue

        if not clips:
            return None

        # Combine clips with transitions
        if len(clips) > 1:
            # Add smooth transitions
            transition_duration = 0.3
            final_clips = [clips[0]]

            for i in range(1, len(clips)):
                prev_clip = final_clips[-1]
                current_clip = clips[i]

                if (
                    prev_clip.duration > transition_duration
                    and current_clip.duration > transition_duration
                ):
                    prev_clip = prev_clip.fadeout(transition_duration)
                    current_clip = current_clip.fadein(transition_duration)
                    final_clips[-1] = prev_clip

                final_clips.append(current_clip)

            final_video = concatenate_videoclips(final_clips, method="compose")
        else:
            final_video = clips[0]

        # Export final video
        output_path = output_dir / f"runway_video_{job_id}.mp4"
        final_video.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )

        # Cleanup
        for clip in clips:
            clip.close()
        final_video.close()

        return str(output_path)
