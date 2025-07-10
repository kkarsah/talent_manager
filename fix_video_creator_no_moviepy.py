#!/usr/bin/env python3
"""
Fix video creator without MoviePy dependency
Creates enhanced videos using PIL + ffmpeg (which you already have)
"""

import os
import shutil
from pathlib import Path


def create_simple_video_creator():
    """Create a simple video creator that works without MoviePy"""

    simple_video_creator_code = '''# core/content/video_creator.py
"""
Enhanced Video Creator - No MoviePy dependency required
Uses PIL for images + ffmpeg for video assembly
"""

import os
import logging
import uuid
import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class VideoCreator:
    """Enhanced video creator without MoviePy dependency"""
    
    def __init__(self):
        self.output_dir = Path("content/video")
        self.temp_dir = Path("content/temp")
        self.assets_dir = Path("content/assets")
        
        # Create directories
        for directory in [self.output_dir, self.temp_dir, self.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Color schemes for different content types
        self.color_schemes = {
            "tech": {
                "background": (30, 58, 138),   # Blue
                "accent": (96, 165, 250),      # Light blue
                "text": (255, 255, 255),      # White
                "highlight": (34, 197, 94)    # Green
            },
            "general": {
                "background": (55, 65, 81),   # Gray
                "accent": (156, 163, 175),    # Light gray
                "text": (255, 255, 255),     # White
                "highlight": (251, 191, 36)  # Yellow
            }
        }
    
    async def create_video(
        self,
        script: str,
        audio_path: str,
        title: str,
        content_type: str,
        talent_name: str
    ) -> str:
        """Create enhanced video with visuals"""
        
        try:
            logger.info(f"Creating enhanced video: {title}")
            
            # Determine visual style
            style = "tech" if "alex" in talent_name.lower() else "general"
            color_scheme = self.color_schemes[style]
            
            # Get audio duration
            duration = await self._get_audio_duration(audio_path)
            
            # Extract keywords from script
            keywords = self._extract_keywords(script, title)
            
            # Create multiple frames with different visuals
            frames = await self._create_visual_frames(
                title, talent_name, keywords, color_scheme, duration
            )
            
            # Create video from frames + audio
            video_path = await self._assemble_video(frames, audio_path, content_type, duration)
            
            # Clean up frames
            for frame in frames:
                try:
                    os.remove(frame)
                except:
                    pass
            
            logger.info(f"Enhanced video created: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Enhanced video creation failed: {e}")
            # Fallback to simple video
            return await self._create_simple_video(script, audio_path, title, content_type)
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration using ffprobe"""
        try:
            # Try ffprobe first
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', audio_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data['format']['duration'])
        except:
            pass
        
        # Fallback: estimate from file size
        try:
            file_size = os.path.getsize(audio_path)
            # Rough estimate: 128kbps audio
            estimated_duration = file_size / (128 * 1000 / 8)
            return max(estimated_duration, 30)  # At least 30 seconds
        except:
            return 120  # Default 2 minutes
    
    def _extract_keywords(self, script: str, title: str) -> List[str]:
        """Extract keywords for visual elements"""
        
        # Combine script and title for keyword extraction
        text = f"{title} {script}".lower()
        
        # Tech-related keywords
        tech_keywords = [
            "python", "javascript", "code", "programming", "debug", "api",
            "function", "variable", "class", "method", "framework", "library",
            "algorithm", "data", "web", "development", "software", "tutorial",
            "guide", "tips", "tricks", "best", "practice", "example"
        ]
        
        found_keywords = []
        
        # Find tech keywords
        for keyword in tech_keywords:
            if keyword in text and keyword.title() not in found_keywords:
                found_keywords.append(keyword.title())
        
        # Extract other important words
        words = script.split()
        for word in words:
            clean_word = word.strip('.,!?;:').lower()
            if (len(clean_word) > 4 and 
                clean_word.isalpha() and 
                clean_word not in ['this', 'that', 'with', 'from', 'will', 'have', 'been'] and
                clean_word.title() not in found_keywords):
                found_keywords.append(clean_word.title())
                
            if len(found_keywords) >= 8:
                break
        
        return found_keywords[:8]
    
    async def _create_visual_frames(
        self,
        title: str,
        talent_name: str,
        keywords: List[str],
        color_scheme: Dict,
        duration: float
    ) -> List[str]:
        """Create visual frames for the video"""
        
        frames = []
        
        # Calculate number of frames (1 frame per 5-10 seconds)
        num_frames = max(int(duration / 7), 4)  # At least 4 frames
        
        for i in range(num_frames):
            frame_type = self._get_frame_type(i, num_frames)
            frame_path = await self._create_frame(
                i, frame_type, title, talent_name, keywords, color_scheme
            )
            frames.append(frame_path)
        
        return frames
    
    def _get_frame_type(self, index: int, total: int) -> str:
        """Determine frame type based on position"""
        if index == 0:
            return "intro"
        elif index == total - 1:
            return "outro"
        elif index % 3 == 1:
            return "highlight"
        else:
            return "content"
    
    async def _create_frame(
        self,
        frame_index: int,
        frame_type: str,
        title: str,
        talent_name: str,
        keywords: List[str],
        color_scheme: Dict
    ) -> str:
        """Create a single frame"""
        
        # Create image
        width, height = 1280, 720
        image = Image.new("RGB", (width, height), color=color_scheme["background"])
        draw = ImageDraw.Draw(image)
        
        # Load fonts (with fallbacks)
        fonts = self._load_fonts()
        
        # Draw based on frame type
        if frame_type == "intro":
            self._draw_intro(draw, title, talent_name, color_scheme, fonts, width, height)
        elif frame_type == "outro":
            self._draw_outro(draw, color_scheme, fonts, width, height)
        elif frame_type == "highlight":
            self._draw_highlight(draw, keywords, color_scheme, fonts, width, height, frame_index)
        else:
            self._draw_content(draw, title, keywords, color_scheme, fonts, width, height, frame_index)
        
        # Add decorative elements
        self._add_decorations(draw, color_scheme, width, height, frame_index)
        
        # Save frame
        frame_path = self.temp_dir / f"frame_{frame_index:03d}.png"
        image.save(frame_path)
        
        return str(frame_path)
    
    def _load_fonts(self) -> Dict:
        """Load fonts with fallbacks"""
        fonts = {}
        
        # Try to load system fonts
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/Windows/Fonts/arial.ttf",         # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "arial.ttf"  # System path
        ]
        
        for size_name, size in [("large", 72), ("medium", 48), ("small", 36)]:
            fonts[size_name] = None
            for font_path in font_paths:
                try:
                    fonts[size_name] = ImageFont.truetype(font_path, size)
                    break
                except:
                    continue
            
            # Fallback to default font
            if fonts[size_name] is None:
                fonts[size_name] = ImageFont.load_default()
        
        return fonts
    
    def _draw_intro(self, draw, title, talent_name, color_scheme, fonts, width, height):
        """Draw intro frame"""
        
        # Background accents
        draw.rectangle([0, 0, width, 100], fill=color_scheme["accent"])
        draw.rectangle([0, height-100, width, height], fill=color_scheme["highlight"])
        
        # Main title
        if len(title) > 35:
            title = title[:32] + "..."
        
        title_bbox = draw.textbbox((0, 0), title, font=fonts["large"])
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 2 - 50
        
        draw.text((title_x, title_y), title, fill=color_scheme["text"], font=fonts["large"])
        
        # Talent name
        talent_text = f"by {talent_name}"
        talent_bbox = draw.textbbox((0, 0), talent_text, font=fonts["medium"])
        talent_width = talent_bbox[2] - talent_bbox[0]
        talent_x = (width - talent_width) // 2
        talent_y = title_y + 100
        
        draw.text((talent_x, talent_y), talent_text, fill=color_scheme["accent"], font=fonts["medium"])
    
    def _draw_outro(self, draw, color_scheme, fonts, width, height):
        """Draw outro frame"""
        
        # Background gradient effect
        draw.rectangle([0, 0, width, height//3], fill=color_scheme["highlight"])
        
        # Thank you message
        thanks = "Thanks for Watching!"
        thanks_bbox = draw.textbbox((0, 0), thanks, font=fonts["large"])
        thanks_width = thanks_bbox[2] - thanks_bbox[0]
        thanks_x = (width - thanks_width) // 2
        thanks_y = height // 2 - 50
        
        draw.text((thanks_x, thanks_y), thanks, fill=color_scheme["text"], font=fonts["large"])
        
        # Subscribe message
        subscribe = "Subscribe for more!"
        sub_bbox = draw.textbbox((0, 0), subscribe, font=fonts["medium"])
        sub_width = sub_bbox[2] - sub_bbox[0]
        sub_x = (width - sub_width) // 2
        sub_y = thanks_y + 100
        
        draw.text((sub_x, sub_y), subscribe, fill=color_scheme["accent"], font=fonts["medium"])
    
    def _draw_highlight(self, draw, keywords, color_scheme, fonts, width, height, frame_index):
        """Draw highlight frame"""
        
        # Highlight box
        box_width, box_height = 800, 180
        box_x = (width - box_width) // 2
        box_y = (height - box_height) // 2
        
        draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], 
                      fill=color_scheme["highlight"])
        
        # Icon/indicator
        icon = "💡 KEY POINT"
        icon_bbox = draw.textbbox((0, 0), icon, font=fonts["small"])
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_x = (width - icon_width) // 2
        icon_y = box_y + 20
        
        draw.text((icon_x, icon_y), icon, fill=color_scheme["background"], font=fonts["small"])
        
        # Keyword
        if keywords and frame_index < len(keywords):
            keyword = keywords[frame_index % len(keywords)]
            keyword_bbox = draw.textbbox((0, 0), keyword, font=fonts["medium"])
            keyword_width = keyword_bbox[2] - keyword_bbox[0]
            keyword_x = (width - keyword_width) // 2
            keyword_y = icon_y + 60
            
            draw.text((keyword_x, keyword_y), keyword, fill=color_scheme["background"], font=fonts["medium"])
    
    def _draw_content(self, draw, title, keywords, color_scheme, fonts, width, height, frame_index):
        """Draw content frame"""
        
        # Content area background
        draw.rectangle([50, 150, width-50, height-150], 
                      fill=(*color_scheme["accent"], 30))
        
        # Current keyword or topic
        if keywords and frame_index < len(keywords):
            current_keyword = keywords[frame_index % len(keywords)]
        else:
            current_keyword = "Content"
        
        # Main content text
        content_bbox = draw.textbbox((0, 0), current_keyword, font=fonts["medium"])
        content_width = content_bbox[2] - content_bbox[0]
        content_x = (width - content_width) // 2
        content_y = height // 2
        
        draw.text((content_x, content_y), current_keyword, fill=color_scheme["text"], font=fonts["medium"])
        
        # Section indicator
        section = f"Section {frame_index + 1}"
        draw.text((60, 60), section, fill=color_scheme["accent"], font=fonts["small"])
    
    def _add_decorations(self, draw, color_scheme, width, height, frame_index):
        """Add decorative elements"""
        
        # Progress bar at bottom
        bar_width = width - 100
        bar_height = 6
        bar_x = 50
        bar_y = height - 25
        
        # Background bar
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                      fill=color_scheme["accent"])
        
        # Progress (based on frame index)
        progress = (frame_index + 1) / 6  # Assume max 6 frames
        progress_width = int(bar_width * progress)
        draw.rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height], 
                      fill=color_scheme["highlight"])
        
        # Corner accent
        draw.rectangle([0, 0, 50, 50], fill=color_scheme["accent"])
        draw.rectangle([width-50, 0, width, 50], fill=color_scheme["highlight"])
    
    async def _assemble_video(
        self,
        frames: List[str],
        audio_path: str,
        content_type: str,
        duration: float
    ) -> str:
        """Assemble video from frames and audio"""
        
        try:
            # Generate output path
            video_id = str(uuid.uuid4())[:8]
            output_filename = f"{content_type}_{video_id}.mp4"
            output_path = self.output_dir / output_filename
            
            # Calculate frame duration
            frame_duration = duration / len(frames)
            
            # Create frame list for ffmpeg
            frame_list_path = self.temp_dir / f"frames_{video_id}.txt"
            with open(frame_list_path, 'w') as f:
                for frame_path in frames:
                    f.write(f"file '{os.path.abspath(frame_path)}'\\n")
                    f.write(f"duration {frame_duration}\\n")
                # Last frame
                f.write(f"file '{os.path.abspath(frames[-1])}'\\n")
            
            # Use ffmpeg to create video
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-f', 'concat',
                '-safe', '0',
                '-i', str(frame_list_path),
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',  # Match shortest input
                str(output_path)
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up
            try:
                os.remove(frame_list_path)
            except:
                pass
            
            if result.returncode == 0:
                return str(output_path)
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return await self._create_simple_video(None, audio_path, "Video", content_type)
                
        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            return await self._create_simple_video(None, audio_path, "Video", content_type)
    
    async def _create_simple_video(self, script, audio_path: str, title: str, content_type: str) -> str:
        """Create simple video as fallback"""
        
        logger.info("Creating simple fallback video")
        
        try:
            # Create single frame
            width, height = 1280, 720
            image = Image.new("RGB", (width, height), color=(30, 58, 138))
            draw = ImageDraw.Draw(image)
            
            # Load font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # Draw title
            if len(title) > 30:
                title = title[:27] + "..."
            
            title_bbox = draw.textbbox((0, 0), title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            title_y = (height - 60) // 2
            
            draw.text((title_x, title_y), title, fill=(255, 255, 255), font=font)
            
            # Save frame
            frame_path = self.temp_dir / "simple_frame.png"
            image.save(frame_path)
            
            # Create video
            video_id = str(uuid.uuid4())[:8]
            output_filename = f"{content_type}_{video_id}.mp4"
            output_path = self.output_dir / output_filename
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', str(frame_path),
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                str(output_path)
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up
            try:
                os.remove(frame_path)
            except:
                pass
            
            if result.returncode == 0:
                return str(output_path)
            else:
                logger.error(f"Simple video creation failed: {result.stderr}")
                raise Exception("Video creation failed")
                
        except Exception as e:
            logger.error(f"Simple video creation failed: {e}")
            raise
    
    async def create_thumbnail(self, title: str, talent_name: str) -> str:
        """Create video thumbnail"""
        
        try:
            width, height = 1280, 720
            
            # Determine style
            style = "tech" if "alex" in talent_name.lower() else "general"
            color_scheme = self.color_schemes[style]
            
            # Create thumbnail
            image = Image.new("RGB", (width, height), color=color_scheme["background"])
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            fonts = self._load_fonts()
            
            # Background elements
            draw.rectangle([0, 0, width, 80], fill=color_scheme["accent"])
            draw.rectangle([0, height-80, width, height], fill=color_scheme["highlight"])
            
            # Title
            if len(title) > 40:
                title = title[:37] + "..."
            
            title_bbox = draw.textbbox((0, 0), title, font=fonts["large"])
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            title_y = height // 3
            
            draw.text((title_x, title_y), title, fill=color_scheme["text"], font=fonts["large"])
            
            # Talent name
            talent_bbox = draw.textbbox((0, 0), talent_name, font=fonts["medium"])
            talent_width = talent_bbox[2] - talent_bbox[0]
            talent_x = (width - talent_width) // 2
            talent_y = title_y + 120
            
            draw.text((talent_x, talent_y), talent_name, fill=color_scheme["accent"], font=fonts["medium"])
            
            # Save thumbnail
            thumbnail_id = str(uuid.uuid4())[:8]
            thumbnail_path = self.output_dir / f"thumbnail_{thumbnail_id}.png"
            image.save(thumbnail_path)
            
            return str(thumbnail_path)
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            # Return a placeholder path
            return str(self.output_dir / "default_thumbnail.png")
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_files = list(self.temp_dir.glob("*"))
            for temp_file in temp_files:
                if temp_file.is_file() and temp_file.name.startswith(('frame_', 'frames_')):
                    temp_file.unlink()
        except Exception as e:
            logger.warning(f"Could not clean up temp files: {e}")
'''

    # Create the file
    video_creator_path = Path("core/content/video_creator.py")

    # Backup existing file
    if video_creator_path.exists():
        backup_path = video_creator_path.with_suffix(".py.backup")
        shutil.copy2(video_creator_path, backup_path)
        print(f"📁 Backed up existing file to {backup_path}")

    # Create enhanced video creator
    video_creator_path.parent.mkdir(parents=True, exist_ok=True)
    with open(video_creator_path, "w") as f:
        f.write(simple_video_creator_code)

    print(f"✅ Created enhanced video creator: {video_creator_path}")


def clear_cache():
    """Clear Python cache"""
    import shutil

    cache_dirs = list(Path(".").rglob("__pycache__"))
    for cache_dir in cache_dirs:
        if cache_dir.is_dir():
            try:
                shutil.rmtree(cache_dir)
            except:
                pass


def test_video_creator():
    """Test if the video creator can be imported"""
    try:
        import sys

        sys.path.insert(0, str(Path(".").resolve()))

        from core.content.video_creator import VideoCreator

        # Test instantiation
        creator = VideoCreator()

        print("✅ Enhanced video creator can be imported and instantiated")
        return True

    except Exception as e:
        print(f"❌ Video creator test failed: {e}")
        return False


def main():
    """Apply the fix"""
    print("🎬 Enhanced Video Creator Fix (No MoviePy)")
    print("=" * 50)

    # Step 1: Create enhanced video creator
    create_simple_video_creator()

    # Step 2: Clear cache
    clear_cache()

    # Step 3: Test
    success = test_video_creator()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Enhanced Video Creator Fixed!")
        print("✅ Your videos will now have:")
        print("   • Multiple visual frames with different content")
        print("   • Intro frames with title and talent branding")
        print("   • Content frames with keywords and concepts")
        print("   • Highlight frames with key points")
        print("   • Outro frames with call-to-action")
        print("   • Progress bars and decorative elements")
        print("   • Professional thumbnails")

        print("\n🎬 Test it now:")
        print("   python cli.py alex generate --topic 'Enhanced video without MoviePy'")

    else:
        print("⚠️  Some issues remain - check the error above")

    print("\n📋 What was done:")
    print("• ✅ Replaced video creator with enhanced version")
    print("• ✅ No MoviePy dependency required")
    print("• ✅ Uses PIL for images + ffmpeg for video")
    print("• ✅ Multiple frame types with visual variety")
    print("• ✅ Cleared Python cache")


if __name__ == "__main__":
    main()
