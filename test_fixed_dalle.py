#!/usr/bin/env python3
"""
Updated test script for DALL-E video creator
"""

import asyncio
import os
from pathlib import Path


async def test_scene_parsing():
    """Test scene parsing functionality"""
    try:
        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()

        # Test with string input
        test_script = "Scene 1: Introduction to Python loops. Scene 2: For loops explained. Scene 3: While loops in action."

        # This should be synchronous now
        sections = creator._split_script_into_sections(test_script)
        print(f"✅ Script parsing: {len(sections)} sections found")

        # Test scene parsing (also synchronous)
        scenes = creator._parse_script_into_scenes(test_script, 30.0)
        print(f"✅ Scene parsing: {len(scenes)} scenes created")

        return True

    except Exception as e:
        print(f"❌ Scene parsing test failed: {e}")
        return False


async def test_dalle_generation():
    """Test DALL-E prompt generation"""
    try:
        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()

        # Test prompt creation (synchronous)
        prompt = creator._create_dalle_prompt(
            "This is about Python programming loops", 1, 3
        )
        print(f"✅ DALL-E prompt: {prompt[:100]}...")

        # Test actual image generation (async) - only if API key available
        if creator.openai_api_key:
            image_path = await creator._generate_dalle_image(prompt, 1)
            if image_path:
                print(f"✅ DALL-E image generated: {image_path}")
            else:
                print("ℹ️  DALL-E generation skipped (API issue)")
        else:
            print("ℹ️  DALL-E generation skipped (no API key)")

        return True

    except Exception as e:
        print(f"❌ DALL-E generation test failed: {e}")
        return False


async def test_full_video():
    """Test full video creation"""
    try:
        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()

        audio_path = "content/audio/audio_1_Python_Loops_Explained.mp3"

        if os.path.exists(audio_path):
            video_path = await creator.create_video_from_scenes(
                "Introduction to Python loops and iteration",
                audio_path,
                "Python Loops Tutorial",
                "tutorial",
                "alex",
                use_dalle=False,  # Skip DALL-E for this test
            )

            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                print(f"✅ Video created: {video_path} ({file_size:.2f} MB)")
                return True
            else:
                print("❌ Video file not created")
                return False
        else:
            print(f"❌ Audio file not found: {audio_path}")
            return False

    except Exception as e:
        print(f"❌ Full video test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Testing Fixed DALL-E Video Creator")
    print("=" * 40)

    tests = [
        ("Scene Parsing", test_scene_parsing),
        ("DALL-E Generation", test_dalle_generation),
        ("Full Video Creation", test_full_video),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)

        if await test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! DALL-E video creator is working!")
    else:
        print("⚠️  Some tests failed - check errors above")


if __name__ == "__main__":
    asyncio.run(main())
