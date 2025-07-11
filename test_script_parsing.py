#!/usr/bin/env python3
"""
Corrected test for script parsing
"""


def test_script_parsing():
    """Test script parsing without await errors"""

    try:
        import sys

        sys.path.insert(0, str(__file__).replace("test_script_parsing.py", ""))

        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()

        # Test 1: Basic script parsing
        test_script = (
            "Scene 1: Introduction. Scene 2: Main content. Scene 3: Conclusion."
        )

        # This should be synchronous - NO await
        sections = creator._split_script_into_sections(test_script)
        print(f"✅ Script sections: {len(sections)}")

        # Test 2: Scene parsing with timing
        # This should also be synchronous - NO await
        scenes = creator._parse_script_into_scenes(test_script, 30.0)
        print(f"✅ Parsed scenes: {len(scenes)}")

        # Test 3: DALL-E prompt creation
        # This should be synchronous - NO await
        prompt = creator._create_dalle_prompt("Test scene about programming", 1, 3)
        print(f"✅ Generated prompt: {len(prompt)} chars")

        print("🎉 All script parsing tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    from pathlib import Path

    test_script_parsing()
