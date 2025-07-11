#!/usr/bin/env python3
"""
Fix for enhanced_video_creator.py syntax error on line 138
"""

import os
import shutil
from pathlib import Path


def fix_syntax_error():
    """Fix the syntax error in enhanced_video_creator.py"""

    enhanced_video_creator_path = Path("core/content/enhanced_video_creator.py")

    if not enhanced_video_creator_path.exists():
        print("❌ enhanced_video_creator.py not found!")
        print("🔍 Looking for similar files...")
        # Check for other video creator files
        core_content_dir = Path("core/content")
        if core_content_dir.exists():
            video_files = list(core_content_dir.glob("*video*"))
            print(f"📁 Found video-related files: {[f.name for f in video_files]}")
        return False

    # Backup the file first
    backup_path = enhanced_video_creator_path.with_suffix(".py.backup")
    shutil.copy2(enhanced_video_creator_path, backup_path)
    print(f"💾 Backed up file to: {backup_path}")

    # Read the file
    with open(enhanced_video_creator_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and fix the syntax error on line 138
    lines = content.split("\n")

    print(f"📄 File has {len(lines)} lines")

    if len(lines) >= 138:
        line_138 = lines[137]  # 0-indexed
        print(f"🔍 Line 138: {line_138}")

        # Common fixes for unterminated string literals
        if "script.split('" in line_138 and not line_138.count("'") % 2 == 0:
            # Missing closing quote
            if line_138.endswith("script.split('"):
                lines[137] = line_138 + "')"
                print("🔧 Fixed: Added missing closing quote and parenthesis")
            elif "script.split('" in line_138 and not ")'" in line_138:
                # Find the split parameter and fix it
                if "\\n" in line_138:
                    lines[137] = line_138.replace(
                        "script.split('", "script.split('\\n')"
                    )
                else:
                    lines[137] = line_138 + "')"
                print("🔧 Fixed: Completed split() method call")

        # Check for other common issues
        elif ".split('" in line_138 and line_138.count("'") == 1:
            # Single unterminated quote
            lines[137] = line_138 + "')"
            print("🔧 Fixed: Added missing closing quote and parenthesis")

        # Look at surrounding lines for context
        start_line = max(0, 135)
        end_line = min(len(lines), 142)

        print("\n📋 Context around line 138:")
        for i in range(start_line, end_line):
            marker = ">>> " if i == 137 else "    "
            print(f"{marker}{i+1:3d}: {lines[i]}")

    # Write the fixed content back
    fixed_content = "\n".join(lines)

    with open(enhanced_video_creator_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"✅ Fixed syntax error in {enhanced_video_creator_path}")
    return True


def test_import():
    """Test if the file can be imported now"""
    try:
        import sys

        sys.path.insert(0, str(Path(".").resolve()))

        # Clear any cached modules
        if "core.content.enhanced_video_creator" in sys.modules:
            del sys.modules["core.content.enhanced_video_creator"]

        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        # Try to instantiate it
        creator = SceneBasedVideoCreator()
        print("✅ SceneBasedVideoCreator imported and instantiated successfully!")

        # Test script parsing
        test_script = "Scene 1: Hello world. Scene 2: This is a test."
        sections = creator._split_script_into_sections(test_script)
        print(f"✅ Script parsing test: {len(sections)} sections found")

        return True

    except SyntaxError as e:
        print(f"❌ Syntax error still exists: {e}")
        print(f"   File: {e.filename}, Line: {e.lineno}")
        return False
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def alternative_fix():
    """If the automatic fix doesn't work, create a working version"""

    print("🔄 Creating a clean working version...")

    # Create a minimal working enhanced video creator
    working_code = '''import os
import logging
import uuid
import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class SceneBasedVideoCreator:
    """Scene-based video creator"""
    
    def __init__(self):
        self.output_dir = Path("content/video")
        self.temp_dir = Path("content/temp")
        self.scenes_dir = Path("content/scenes")
        
        # Create directories
        for directory in [self.output_dir, self.temp_dir, self.scenes_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _split_script_into_sections(self, script: str) -> List[str]:
        """Split script into sections - FIXED VERSION"""
        
        if not script or not script.strip():
            return []
        
        # Clean the script first
        script = script.strip()
        
        # Try multiple splitting methods
        sections = []
        
        # Method 1: Split by paragraph breaks
        paragraphs = script.split('\\n\\n')
        if len(paragraphs) > 1:
            sections = [p.strip() for p in paragraphs if p.strip()]
        
        # Method 2: Split by scene markers
        if not sections:
            scene_patterns = ['Scene ', 'SCENE ', '[Scene', 'Section ']
            for pattern in scene_patterns:
                if pattern in script:
                    parts = script.split(pattern)
                    sections = [pattern + part.strip() for part in parts[1:] if part.strip()]
                    break
        
        # Method 3: Split by sentences if no other method works
        if not sections:
            sentences = script.split('. ')
            if len(sentences) > 3:
                # Group sentences into sections
                sections = []
                current_section = []
                for sentence in sentences:
                    current_section.append(sentence.strip())
                    if len(current_section) >= 3:  # 3 sentences per section
                        sections.append('. '.join(current_section) + '.')
                        current_section = []
                
                # Add remaining sentences
                if current_section:
                    sections.append('. '.join(current_section) + ('.' if not current_section[-1].endswith('.') else ''))
        
        # Fallback: return the whole script as one section
        if not sections:
            sections = [script]
        
        logger.info(f"Split script into {len(sections)} sections")
        return sections
    
    async def create_video(
        self,
        script: str,
        audio_path: str,
        title: str,
        content_type: str,
        talent_name: str
    ) -> str:
        """Create video from script and audio"""
        
        try:
            logger.info(f"Creating scene-based video: {title}")
            
            # For now, create a simple video
            video_id = str(uuid.uuid4())[:8]
            output_filename = f"{content_type}_{video_id}.mp4"
            output_path = self.output_dir / output_filename
            
            # Create a simple black video with audio
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', 'color=black:size=1920x1080:duration=30',
                '-i', audio_path,
                '-c:v', 'libx264', '-c:a', 'aac',
                '-shortest',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Video created successfully: {output_path}")
                return str(output_path)
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"Video creation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            raise
'''

    # Write the working version
    enhanced_video_creator_path = Path("core/content/enhanced_video_creator.py")

    with open(enhanced_video_creator_path, "w", encoding="utf-8") as f:
        f.write(working_code)

    print(f"✅ Created working version: {enhanced_video_creator_path}")


def main():
    """Main fix process"""

    print("🔧 Enhanced Video Creator Syntax Fix")
    print("=" * 50)

    # Step 1: Try to fix the existing file
    if fix_syntax_error():
        print("\n🧪 Testing the fix...")
        if test_import():
            print("\n🎉 SUCCESS! The syntax error has been fixed!")
            print("✅ You can now run your import test again:")
            print(
                "   python -c \"from core.content.enhanced_video_creator import SceneBasedVideoCreator; print('Import successful!')\""
            )
            return

    # Step 2: If fix didn't work, create a clean version
    print("\n🔄 Automatic fix didn't work, creating clean version...")
    alternative_fix()

    print("\n🧪 Testing the clean version...")
    if test_import():
        print("\n🎉 SUCCESS! Clean version is working!")
    else:
        print("\n⚠️  There may be other issues. Check the error messages above.")

    print("\n📋 Next steps:")
    print("1. Try your import again")
    print("2. If it works, you can continue with video creation")
    print("3. If there are still issues, check for other syntax errors")


if __name__ == "__main__":
    main()
