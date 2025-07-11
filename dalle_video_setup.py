#!/usr/bin/env python3
"""
DALL-E Scene Video Creator Setup and Test
Sets up and tests the new scene-based video generation with DALL-E images
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(".")


async def test_dalle_access():
    """Test if DALL-E API access is working"""

    try:
        print("🔍 Testing DALL-E API access...")

        import openai
        from dotenv import load_dotenv

        load_dotenv()

        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False

        print(f"✅ OpenAI API key found: {api_key[:7]}...{api_key[-4:]}")

        # Test DALL-E access with a simple generation
        client = openai.OpenAI(api_key=api_key)

        print("🎨 Testing DALL-E 3 image generation...")

        response = await asyncio.to_thread(
            client.images.generate,
            model="dall-e-3",
            prompt="A simple test image: modern tech workspace, professional lighting, blue and white colors, clean design",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        if response.data[0].url:
            print("✅ DALL-E 3 is accessible and working!")
            print(f"🔗 Test image URL: {response.data[0].url}")
            return True
        else:
            print("❌ DALL-E response received but no image URL")
            return False

    except Exception as e:
        print(f"❌ DALL-E access test failed: {e}")

        if "billing" in str(e).lower():
            print("💳 Billing issue: Please check your OpenAI account credits")
        elif "rate_limit" in str(e).lower():
            print("⏱️ Rate limit: Please wait and try again")
        elif "invalid_api_key" in str(e).lower():
            print("🔑 Invalid API key: Please check your OPENAI_API_KEY")
        else:
            print("🤔 Unknown error - check your OpenAI account status")

        return False


async def setup_dalle_video_creator():
    """Set up the DALL-E scene-based video creator"""

    try:
        print("📁 Setting up directories...")

        # Create required directories
        directories = [
            "content/scenes",
            "content/temp",
            "content/video",
            "content/assets",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")

        # Save the enhanced video creator
        video_creator_path = Path("core/content/enhanced_video_creator.py")

        if video_creator_path.exists():
            print("✅ Enhanced video creator already exists")
        else:
            print(
                "📝 Enhanced video creator will be created when you save the artifact"
            )

        # Test import
        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()
        print("✅ SceneBasedVideoCreator imported successfully")

        return True

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


async def test_scene_parsing():
    """Test script parsing into scenes"""

    try:
        print("📋 Testing script parsing...")

        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()

        # Test script with clear scenes
        test_script = """
        [Opening shot: Alex CodeMaster in futuristic tech lab]
        Alex CodeMaster: "Welcome everyone! Today we're diving into the revolutionary world of quantum computing and its impact on software development."
        
        [Scene 2: Holographic displays showing quantum circuits]
        The quantum advantage isn't just theoretical anymore. Companies like IBM and Google are building systems that solve problems classical computers never could.
        
        [Scene 3: Close-up of quantum visualization]
        Alex CodeMaster: "Let me show you three key breakthroughs that will change programming forever."
        
        [Scene 4: Split screen showing quantum vs classical comparison]
        First, quantum algorithms can factor large numbers exponentially faster. Second, quantum machine learning opens entirely new possibilities.
        
        [Final scene: Alex with exciting quantum visualization]
        Alex CodeMaster: "The future of computing is quantum, and the future is now! Subscribe to stay ahead of the quantum revolution!"
        """

        scenes = creator._parse_script_into_scenes(test_script, "Alex CodeMaster")

        print(f"✅ Parsed {len(scenes)} scenes:")
        for i, scene in enumerate(scenes, 1):
            print(f"   Scene {i}: {scene.text[:50]}...")
            print(f"            {scene.text[:60]}...")

        return len(scenes) > 0

    except Exception as e:
        print(f"❌ Scene parsing test failed: {e}")
        return False


async def test_dalle_scene_generation():
    """Test generating a single scene with DALL-E"""

    try:
        print("🎨 Testing DALL-E scene generation...")

        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        creator = SceneBasedVideoCreator()

        # Create test scene
        test_scene = {
            "index": 1,
            "scene_description": "Professional tech presenter Alex CodeMaster in modern innovation lab with holographic displays showing quantum computing visualizations, futuristic blue lighting, high-tech environment",
            "spoken_content": "Welcome to the quantum computing revolution",
        }

        # Generate DALL-E prompt
        prompt = creator._create_dalle_prompt(
            test_scene, "Alex CodeMaster", "Quantum Computing Revolution"
        )
        print(f"📝 Generated prompt: {prompt[:100]}...")

        # Generate image
        image_path = await creator._generate_dalle_image(prompt, "test_scene")

        if image_path and os.path.exists(image_path):
            file_size = os.path.getsize(image_path) / (1024 * 1024)
            print(f"✅ DALL-E scene image generated: {image_path}")
            print(f"📊 Image size: {file_size:.1f} MB")
            return True
        else:
            print("❌ DALL-E scene generation failed")
            return False

    except Exception as e:
        print(f"❌ DALL-E scene generation test failed: {e}")
        return False


async def test_full_scene_video():
    """Test creating a complete video with DALL-E generated scenes"""

    try:
        print("🎬 Testing complete scene-based video creation...")

        from core.content.enhanced_video_creator import SceneBasedVideoCreator

        # Check for existing audio or create test audio
        import glob

        audio_files = glob.glob("content/audio/*.mp3")

        if audio_files:
            audio_path = audio_files[0]
            print(f"📄 Using existing audio: {os.path.basename(audio_path)}")
        else:
            print("🎤 Creating test audio...")
            from core.content.tts import TTSService

            tts = TTSService()
            audio_path = await tts.generate_speech(
                "This is a test narration for the DALL-E scene-based video creator. Each scene will have a custom generated image.",
                {"provider": "elevenlabs", "voice_id": "alex_tech_voice"},
                "dalle_test_audio.mp3",
            )

            if not audio_path:
                print("❌ Could not create test audio")
                return False

        # Test script
        test_script = """
        [Opening: Professional tech studio with Alex CodeMaster]
        Alex CodeMaster: "Welcome to the future of artificial intelligence development!"
        
        [Scene: Advanced AI visualization screens and neural networks]
        Today we're exploring how DALL-E and GPT are revolutionizing content creation.
        
        [Scene: Futuristic workspace with holographic AI interfaces]  
        Alex CodeMaster: "The integration of AI image generation with video creation opens incredible possibilities."
        
        [Final scene: Alex with exciting AI technology backdrop]
        This is just the beginning of AI-powered media creation!
        """

        # Create scene-based video
        creator = SceneBasedVideoCreator()

        video_path = await creator.create_video_from_scenes(
            script=test_script,
            audio_path=audio_path,
            title="AI Revolution: DALL-E Scene Generation Test",
            content_type="dalle_test",
            talent_name="Alex CodeMaster",
        )

        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            print(f"🎉 SUCCESS! DALL-E scene video created: {video_path}")
            print(f"📊 Video size: {file_size:.1f} MB")

            # Cleanup
            creator.cleanup_temp_files()

            return True
        else:
            print("❌ Scene video creation failed")
            return False

    except Exception as e:
        print(f"❌ Full scene video test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def run_complete_test():
    """Run complete test suite for DALL-E scene video creator"""

    print("🚀 DALL-E Scene Video Creator - Complete Test Suite")
    print("=" * 60)

    tests = [
        ("DALL-E API Access", test_dalle_access),
        ("Setup Directories", setup_dalle_video_creator),
        ("Script Parsing", test_scene_parsing),
        ("DALL-E Scene Generation", test_dalle_scene_generation),
        ("Full Scene Video", test_full_scene_video),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n🧪 Testing: {name}")
        print("-" * 30)

        try:
            success = await test_func()
            if success:
                print(f"✅ {name}: PASSED")
                passed += 1
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"💥 {name}: ERROR - {e}")

    print(f"\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n🎯 Your DALL-E Scene Video Creator is ready!")
        print("\n📋 Next steps:")
        print("   1. Run: python cli.py alex generate --topic 'DALL-E Video Test'")
        print("   2. Check content/video/ for your scene-based videos")
        print("   3. Check content/scenes/ for generated scene images")

        # Update pipeline integration
        print("\n🔧 To use in production:")
        print("   Update your enhanced_content_pipeline.py to use:")
        print(
            "   from core.content.enhanced_video_creator import SceneBasedVideoCreator"
        )

    elif passed >= 3:
        print("⚠️ Partial success - basic functionality working")
        print("Some advanced features may need attention")
    else:
        print("❌ Major issues found - check the errors above")

    return passed == total


# Integration commands
async def integrate_with_alex():
    """Integrate DALL-E scene creator with Alex's pipeline"""

    print("🔗 Integrating DALL-E Scene Creator with Alex CodeMaster...")

    try:
        # Test generation with Alex
        from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

        # Update the pipeline to use scene-based creator
        print(
            "📝 To integrate with Alex's pipeline, add this to enhanced_content_pipeline.py:"
        )

        integration_code = """
# Replace the video creation section in create_enhanced_content with:

        # Step 5: Create video with DALL-E generated scene images
        await self._update_job_status(job_id, "Creating video with AI-generated scenes", 60)
        
        try:
            from core.content.enhanced_video_creator import SceneBasedVideoCreator
            scene_creator = SceneBasedVideoCreator()
            
            video_path = await scene_creator.create_video_from_scenes(
                generated_content.text,
                audio_path,
                generated_content.title,
                content_type,
                talent_name
            )
            
            # Create enhanced thumbnail  
            thumbnail_path = await scene_creator.create_thumbnail(
                generated_content.title, talent_name
            )
            
            scene_creator.cleanup_temp_files()
            
        except Exception as e:
            logger.warning(f"Scene creation failed, using fallback: {e}")
            # Fallback to regular video creator
            video_path = await self.video_creator.create_video(
                generated_content.text,
                audio_path, 
                generated_content.title,
                content_type,
                talent_name
            )
        """

        print(integration_code)

        return True

    except Exception as e:
        print(f"❌ Integration preparation failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--integrate":
        asyncio.run(integrate_with_alex())
    else:
        asyncio.run(run_complete_test())
