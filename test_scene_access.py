#!/usr/bin/env python3
"""
Test Scene object access patterns
"""


def test_scene_access():
    """Test proper Scene object access"""

    try:
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(".").resolve()))

        from core.content.enhanced_video_creator import SceneBasedVideoCreator, Scene

        creator = SceneBasedVideoCreator()

        # Test 1: Create scenes from script
        test_script = "Scene 1: Introduction to Python. Scene 2: Variables and data types. Scene 3: Control structures."
        scenes = creator._parse_script_into_scenes(test_script, 30.0)

        print(f"✅ Created {len(scenes)} scenes")

        # Test 2: Access Scene object properties correctly
        if scenes:
            first_scene = scenes[0]

            # Correct way to access Scene properties
            print(f"✅ Scene text: {first_scene.text[:50]}...")
            print(f"✅ Scene duration: {first_scene.duration}")
            print(f"✅ Scene prompt: {first_scene.image_prompt[:50]}...")

            # Test all scenes
            for i, scene in enumerate(scenes):
                print(f"✅ Scene {i+1}: {len(scene.text)} chars, {scene.duration}s")

        print("🎉 Scene object access test passed!")
        return True

    except Exception as e:
        print(f"❌ Scene access test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_scene_access()
