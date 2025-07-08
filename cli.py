# cli.py

import click
import os
import sys
from dotenv import load_dotenv
import click
import asyncio
from pathlib import Path
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.config import SessionLocal, init_db
from core.database.models import Talent, ContentItem

import asyncio
from core.pipeline.content_pipeline import (
    ContentPipeline,
    quick_generate_content,
    quick_generate_and_upload,
)
from core.content.generator import PROGRAMMING_TOPICS, get_random_topic
from platforms.youtube.service import YouTubeService

import asyncio
from core.pipeline.content_pipeline import (
    ContentPipeline,
    quick_generate_content,
    quick_generate_and_upload,
)
from core.content.generator import PROGRAMMING_TOPICS, get_random_topic
from platforms.youtube.service import YouTubeService

load_dotenv()


@click.group()
def cli():
    """Talent Manager CLI - Manage your AI talents from command line"""
    pass


@cli.command()
def init():
    """Initialize the database"""
    click.echo("Initializing database...")
    init_db()
    click.echo("✅ Database initialized successfully!")


@cli.command()
def status():
    """Check system status"""
    click.echo("🔍 Checking system status...")

    # Check database connection
    try:
        db = SessionLocal()
        talent_count = db.query(Talent).count()
        content_count = db.query(ContentItem).count()
        db.close()
        click.echo(
            f"✅ Database: Connected ({talent_count} talents, {content_count} content items)"
        )
    except Exception as e:
        click.echo(f"❌ Database: Error - {e}")

    # Check API keys
    openai_key = "✅ Configured" if os.getenv("OPENAI_API_KEY") else "❌ Not configured"
    elevenlabs_key = (
        "✅ Configured" if os.getenv("ELEVENLABS_API_KEY") else "❌ Not configured"
    )
    youtube_key = (
        "✅ Configured" if os.getenv("YOUTUBE_CLIENT_ID") else "❌ Not configured"
    )

    click.echo(f"🔑 OpenAI API: {openai_key}")
    click.echo(f"🔑 ElevenLabs API: {elevenlabs_key}")
    click.echo(f"🔑 YouTube API: {youtube_key}")


@cli.command()
@click.option("--name", prompt="Talent name", help="Name of the talent")
@click.option("--specialization", prompt="Specialization", help="Talent specialization")
def create_talent(name, specialization):
    """Create a new talent"""
    click.echo(f"Creating talent: {name}")

    # Basic personality template
    personality = {
        "tone": "friendly and professional",
        "expertise_level": "intermediate to advanced",
        "teaching_style": "clear and engaging",
        "target_audience": "general audience interested in " + specialization.lower(),
    }

    db = SessionLocal()
    talent = Talent(
        name=name,
        specialization=specialization,
        personality=personality,
        is_active=True,
    )
    db.add(talent)
    db.commit()
    db.refresh(talent)
    db.close()

    click.echo(f"✅ Talent '{name}' created successfully with ID: {talent.id}")


@cli.command()
def list_talents():
    """List all talents"""
    click.echo("📋 Current talents:")

    db = SessionLocal()
    talents = db.query(Talent).filter(Talent.is_active == True).all()
    db.close()

    if not talents:
        click.echo("No talents found. Create one with: python cli.py create-talent")
        return

    for talent in talents:
        status = "🟢 Active" if talent.is_active else "🔴 Inactive"
        click.echo(f"  {talent.id}: {talent.name} ({talent.specialization}) - {status}")


@cli.command()
@click.option("--talent-id", type=int, prompt="Talent ID", help="ID of the talent")
@click.option("--title", prompt="Content title", help="Title of the content")
@click.option(
    "--type",
    "content_type",
    prompt="Content type",
    type=click.Choice(["long_form", "short", "reel"]),
    help="Type of content",
)
@click.option(
    "--platform",
    prompt="Platform",
    type=click.Choice(["youtube", "tiktok", "instagram"]),
    help="Target platform",
)
def create_content(talent_id, title, content_type, platform):
    """Create a new content item"""
    click.echo(f"Creating content: {title}")

    db = SessionLocal()

    # Check if talent exists
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    if not talent:
        click.echo(f"❌ Talent with ID {talent_id} not found")
        db.close()
        return

    content = ContentItem(
        talent_id=talent_id,
        title=title,
        content_type=content_type,
        platform=platform,
        status="draft",
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    db.close()

    click.echo(f"✅ Content '{title}' created successfully with ID: {content.id}")


@cli.command()
def run_server():
    """Run the development server"""
    click.echo("🚀 Starting development server...")
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# Add these commands to cli.py

# Add these commands to cli.py

import asyncio
from core.pipeline.content_pipeline import (
    ContentPipeline,
    quick_generate_content,
    quick_generate_and_upload,
)
from core.content.generator import PROGRAMMING_TOPICS, get_random_topic
from platforms.youtube.service import YouTubeService


@cli.command()
def create_alex():
    """Create Alex CodeMaster talent with predefined settings"""
    click.echo("🎭 Creating Alex CodeMaster talent...")

    from talents.education_specialist.alex_codemaster import AlexCodeMasterProfile

    db = SessionLocal()

    # Check if Alex already exists
    existing = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    if existing:
        click.echo(f"✅ Alex CodeMaster already exists with ID: {existing.id}")
        db.close()
        return

    # Create Alex CodeMaster
    alex_profile = AlexCodeMasterProfile()
    talent = Talent(
        name=alex_profile.profile["basic_info"]["name"],
        specialization=alex_profile.profile["basic_info"]["specialization"],
        personality=alex_profile.profile["personality"],
        is_active=True,
    )

    db.add(talent)
    db.commit()
    db.refresh(talent)
    db.close()

    click.echo(f"✅ Alex CodeMaster created successfully!")
    click.echo(f"   ID: {talent.id}")
    click.echo(f"   Specialization: {talent.specialization}")
    click.echo(f"   Personality: {talent.personality['tone']}")


@cli.command()
@click.option("--talent-id", type=int, prompt="Talent ID", help="ID of the talent")
@click.option("--topic", prompt="Topic", help="Content topic")
@click.option(
    "--type",
    "content_type",
    default="long_form",
    type=click.Choice(["long_form", "shorts"]),
    help="Content type",
)
@click.option("--upload/--no-upload", default=False, help="Auto-upload to YouTube")
def generate(talent_id, topic, content_type, upload):
    """Generate content for a talent"""
    click.echo(f"🎬 Generating {content_type} content for talent {talent_id}: {topic}")

    async def run_generation():
        try:
            if upload:
                result = await quick_generate_and_upload(talent_id, topic, content_type)
                click.echo("✅ Content generated and uploaded successfully!")
                if "youtube_url" in result:
                    click.echo(f"🎥 YouTube URL: {result['youtube_url']}")
            else:
                result = await quick_generate_content(talent_id, topic, content_type)
                click.echo("✅ Content generated successfully!")

            click.echo(f"📁 Video: {result.get('video_path', 'N/A')}")
            click.echo(f"🎵 Audio: {result.get('audio_path', 'N/A')}")
            click.echo(f"🖼️ Thumbnail: {result.get('thumbnail_path', 'N/A')}")
            click.echo(f"⏱️ Duration: {result.get('estimated_duration', 0)} seconds")

        except Exception as e:
            click.echo(f"❌ Generation failed: {e}")

    asyncio.run(run_generation())


@cli.command()
@click.option("--talent-id", type=int, prompt="Talent ID", help="ID of the talent")
@click.option(
    "--type",
    "content_type",
    default="long_form",
    type=click.Choice(["long_form", "shorts"]),
    help="Content type",
)
@click.option("--upload/--no-upload", default=False, help="Auto-upload to YouTube")
def generate_random(talent_id, content_type, upload):
    """Generate content with a random topic"""

    topic = get_random_topic()
    click.echo(f"🎲 Random topic selected: {topic}")

    async def run_generation():
        try:
            if upload:
                result = await quick_generate_and_upload(talent_id, topic, content_type)
                click.echo("✅ Random content generated and uploaded!")
                if "youtube_url" in result:
                    click.echo(f"🎥 YouTube URL: {result['youtube_url']}")
            else:
                result = await quick_generate_content(talent_id, topic, content_type)
                click.echo("✅ Random content generated!")

            click.echo(f"📁 Files created in content/ directory")

        except Exception as e:
            click.echo(f"❌ Generation failed: {e}")

    asyncio.run(run_generation())


@cli.command()
def topics():
    """List available programming topics"""
    click.echo("📚 Available Programming Topics:")
    click.echo("")

    for i, topic in enumerate(PROGRAMMING_TOPICS, 1):
        click.echo(f"  {i:2d}. {topic}")

    click.echo(f"\nTotal: {len(PROGRAMMING_TOPICS)} topics")


@cli.command()
def test_tts():
    """Test text-to-speech generation"""
    click.echo("🎵 Testing Text-to-Speech...")

    async def run_test():
        try:
            from core.content.tts import TTSService

            tts = TTSService()

            click.echo(f"Provider: {tts.provider}")

            test_text = "Hello! This is Alex CodeMaster. Welcome to today's programming tutorial."
            audio_path = await tts.generate_speech(test_text, filename="test_tts.mp3")

            click.echo(f"✅ TTS test successful!")
            click.echo(f"📁 Audio saved to: {audio_path}")

        except Exception as e:
            click.echo(f"❌ TTS test failed: {e}")

    asyncio.run(run_test())


@cli.command()
def youtube_auth():
    """Authenticate with YouTube"""
    click.echo("🔑 Starting YouTube authentication...")

    async def run_auth():
        try:
            youtube = YouTubeService()
            auth_url = await youtube.authenticate()

            click.echo("📱 Please visit this URL to authenticate:")
            click.echo(f"   {auth_url}")
            click.echo("")
            click.echo("After authorizing, copy the code from the redirect URL:")

            code = click.prompt("Enter authorization code")

            success = await youtube.handle_callback(code)
            if success:
                click.echo("✅ YouTube authentication successful!")

                # Test by getting channel info
                channel_info = await youtube.get_channel_info()
                if channel_info:
                    click.echo(f"📺 Channel: {channel_info.get('title', 'Unknown')}")
                    click.echo(
                        f"👥 Subscribers: {channel_info.get('subscriber_count', 0):,}"
                    )
                    click.echo(f"🎥 Videos: {channel_info.get('video_count', 0):,}")
            else:
                click.echo("❌ YouTube authentication failed!")

        except Exception as e:
            click.echo(f"❌ Authentication error: {e}")

    asyncio.run(run_auth())


@cli.command()
def youtube_status():
    """Check YouTube authentication status"""
    click.echo("📊 Checking YouTube status...")

    async def check_status():
        try:
            youtube = YouTubeService()

            # Try to load existing credentials
            authenticated = await youtube.load_credentials()

            if authenticated:
                click.echo("✅ YouTube: Authenticated")

                # Get channel info
                channel_info = await youtube.get_channel_info()
                if channel_info:
                    click.echo(f"📺 Channel: {channel_info.get('title', 'Unknown')}")
                    click.echo(
                        f"👥 Subscribers: {channel_info.get('subscriber_count', 0):,}"
                    )
                    click.echo(f"🎥 Videos: {channel_info.get('video_count', 0):,}")
                    click.echo(f"👀 Total views: {channel_info.get('view_count', 0):,}")

                # List recent videos
                videos = await youtube.list_recent_videos(5)
                if videos:
                    click.echo("\n🎬 Recent videos:")
                    for video in videos:
                        click.echo(f"   • {video['title']} ({video['views']:,} views)")
            else:
                click.echo("❌ YouTube: Not authenticated")
                click.echo("   Run 'python cli.py youtube-auth' to authenticate")

        except Exception as e:
            click.echo(f"❌ Status check failed: {e}")

    asyncio.run(check_status())


@cli.command()
def test_pipeline():
    """Test the complete content pipeline"""
    click.echo("🧪 Testing content pipeline components...")

    async def run_test():
        try:
            pipeline = ContentPipeline()
            results = await pipeline.test_pipeline_components()

            click.echo("\n🔍 Component Test Results:")
            for component, status in results.items():
                icon = "✅" if status else "❌"
                click.echo(
                    f"   {icon} {component.title()}: {'Working' if status else 'Failed'}"
                )

            # Calculate health
            working = sum(1 for v in results.values() if v)
            total = len(results)
            health = (working / total) * 100

            click.echo(
                f"\n📊 System Health: {health:.1f}% ({working}/{total} components working)"
            )

            if health >= 80:
                click.echo("🟢 System Status: Healthy")
            elif health >= 50:
                click.echo("🟡 System Status: Degraded")
            else:
                click.echo("🔴 System Status: Unhealthy")

        except Exception as e:
            click.echo(f"❌ Pipeline test failed: {e}")

    asyncio.run(run_test())


@cli.command()
@click.option("--talent-id", type=int, help="Filter by talent ID")
def list_content(talent_id):
    """List generated content"""
    click.echo("📋 Generated Content:")

    db = SessionLocal()
    query = db.query(ContentItem)

    if talent_id:
        query = query.filter(ContentItem.talent_id == talent_id)

    content_items = query.order_by(ContentItem.created_at.desc()).limit(10).all()
    db.close()

    if not content_items:
        click.echo("No content found.")
        return

    for item in content_items:
        status_icon = {
            "draft": "📝",
            "generating": "⚙️",
            "generated": "✅",
            "published": "🎥",
            "failed": "❌",
        }.get(item.status, "❓")

        click.echo(f"\n{status_icon} {item.title}")
        click.echo(
            f"   ID: {item.id} | Type: {item.content_type} | Status: {item.status}"
        )
        click.echo(f"   Created: {item.created_at.strftime('%Y-%m-%d %H:%M')}")

        if item.platform_id:
            click.echo(f"   🎥 YouTube: https://youtube.com/watch?v={item.platform_id}")


@cli.command()
@click.option("--talent-id", type=int, prompt="Talent ID", help="ID of the talent")
@click.option("--topic", prompt="Topic", help="Content topic")
@click.option(
    "--type",
    "content_type",
    default="long_form",
    type=click.Choice(["long_form", "shorts"]),
    help="Content type",
)
def generate_audio_only(talent_id, topic, content_type):
    """Generate script and audio without video creation"""
    click.echo(f"🎵 Generating audio-only content for talent {talent_id}: {topic}")

    async def run_generation():
        try:
            from core.content.generator import ContentGenerator, ContentRequest
            from core.content.tts import TTSService, TALENT_VOICE_PROFILES
            from core.database.config import SessionLocal
            from core.database.models import Talent, ContentItem

            # Get talent
            db = SessionLocal()
            talent = db.query(Talent).filter(Talent.id == talent_id).first()
            if not talent:
                click.echo(f"❌ Talent {talent_id} not found")
                db.close()
                return

            click.echo(f"👤 Using talent: {talent.name}")

            # Generate content
            click.echo("🧠 Generating script with OpenAI...")
            generator = ContentGenerator()
            request = ContentRequest(
                talent_name=talent.name, topic=topic, content_type=content_type
            )

            content = await generator.generate_content(request)
            click.echo(f"✅ Script generated: {content.title}")
            click.echo(f"📝 Script length: {len(content.script)} characters")

            # Generate audio with automatic fallback
            click.echo("🎵 Generating audio (will fallback to free TTS if needed)...")
            tts = TTSService()
            voice_settings = TALENT_VOICE_PROFILES.get(talent.name, {}).get(
                tts.provider, {}
            )

            try:
                audio_filename = f"audio_{talent_id}_{topic.replace(' ', '_').replace('/', '_')[:30]}.mp3"
                audio_path = await tts.generate_speech(
                    content.script, voice_settings, audio_filename
                )

                # Check if fallback was used
                if "gtts_fallback" in audio_path:
                    click.echo("⚠️ ElevenLabs quota exceeded - used free gTTS fallback")
                    tts_provider_used = "gTTS (fallback)"
                else:
                    tts_provider_used = tts.provider

            except Exception as tts_error:
                click.echo(f"⚠️ TTS generation failed: {tts_error}")
                click.echo("📝 Continuing with script-only generation...")
                audio_path = None
                tts_provider_used = "none"

            # Save to database
            click.echo("💾 Saving to database...")
            content_item = ContentItem(
                talent_id=talent_id,
                title=content.title,
                description=content.description,
                script=content.script,
                content_type=content_type,
                platform="youtube",
                audio_url=audio_path if audio_path else None,
                status="generated" if audio_path else "script_only",
            )
            db.add(content_item)
            db.commit()
            db.refresh(content_item)
            db.close()

            click.echo("\n🎉 Content generated successfully!")
            click.echo("=" * 50)
            click.echo(f"📺 Title: {content.title}")
            click.echo(f"🆔 Content ID: {content_item.id}")
            click.echo(f"🎵 TTS Provider: {tts_provider_used}")
            if audio_path:
                click.echo(f"📁 Audio file: {audio_path}")
                click.echo(
                    f"⏱️ Estimated duration: {content.estimated_duration // 60}m {content.estimated_duration % 60}s"
                )
            else:
                click.echo("📝 Script-only generation (no audio)")
            click.echo(f"📊 Script words: ~{len(content.script.split())} words")
            click.echo("=" * 50)

            click.echo("\n📋 Generated Content Preview:")
            click.echo(f"Description: {content.description[:200]}...")
            click.echo(f"Tags: {', '.join(content.tags[:5])}")

            click.echo("\n🎯 Next Steps:")
            click.echo("1. Listen to the audio file to review quality")
            click.echo("2. Manually upload to YouTube as audio-only video")
            click.echo("3. Install MoviePy for full video generation later")
            click.echo("4. Set up YouTube API for automated uploads")

        except Exception as e:
            click.echo(f"❌ Generation failed: {e}")
            import traceback

            traceback.print_exc()

    asyncio.run(run_generation())
    """Run a complete demo of the system"""
    click.echo("🎬 Running Talent Manager Demo!")
    click.echo("===============================")

    async def run_demo():
        try:
            # Step 1: Create Alex if not exists
            click.echo("\n1️⃣ Setting up Alex CodeMaster...")

            db = SessionLocal()
            alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()

            if not alex:
                from talents.education_specialist.alex_codemaster import (
                    AlexCodeMasterProfile,
                )

                alex_profile = AlexCodeMasterProfile()
                alex = Talent(
                    name=alex_profile.profile["basic_info"]["name"],
                    specialization=alex_profile.profile["basic_info"]["specialization"],
                    personality=alex_profile.profile["personality"],
                    is_active=True,
                )
                db.add(alex)
                db.commit()
                db.refresh(alex)
                click.echo("✅ Alex CodeMaster created!")
            else:
                click.echo("✅ Alex CodeMaster already exists!")

            db.close()

            # Step 2: Test components
            click.echo("\n2️⃣ Testing system components...")
            pipeline = ContentPipeline()
            results = await pipeline.test_pipeline_components()

            working_components = sum(1 for v in results.values() if v)
            click.echo(f"✅ {working_components}/{len(results)} components working")

            # Step 3: Generate sample content
            click.echo("\n3️⃣ Generating sample content...")
            topic = "Python Functions: Complete Beginner's Guide"
            click.echo(f"📚 Topic: {topic}")

            result = await quick_generate_content(alex.id, topic, "long_form")

            click.echo("✅ Content generated successfully!")
            click.echo(f"📁 Video: {result.get('video_path', 'N/A')}")
            click.echo(f"⏱️ Duration: {result.get('estimated_duration', 0)} seconds")

            click.echo("\n🎉 Demo completed successfully!")
            click.echo("\nNext steps:")
            click.echo("- Run 'python cli.py youtube-auth' to set up YouTube")
            click.echo(
                "- Run 'python cli.py generate --talent-id {} --upload' to create and upload content".format(
                    alex.id
                )
            )

        except Exception as e:
            click.echo(f"❌ Demo failed: {e}")

    asyncio.run(run_demo())


# Add this command to cli.py for smart TTS handling


@cli.command()
def setup_tts():
    """Set up TTS provider with automatic detection and fallback"""
    click.echo("🎵 Setting up Text-to-Speech provider...")

    # Check what's available
    elevenlabs_available = False
    gtts_available = False

    try:
        from elevenlabs.client import ElevenLabs

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if api_key:
            # Test ElevenLabs quota
            try:
                client = ElevenLabs(api_key=api_key)
                # Try a very short test
                test_audio = client.text_to_speech.convert(
                    text="Test",
                    voice_id="21m00Tcm4TlvDq8ikWAM",
                    model_id="eleven_monolingual_v1",
                )
                # If we get here, ElevenLabs is working
                elevenlabs_available = True
                click.echo("✅ ElevenLabs: Available with credits")
            except Exception as e:
                if "quota" in str(e).lower() or "credit" in str(e).lower():
                    click.echo("⚠️ ElevenLabs: Quota exceeded")
                else:
                    click.echo(f"❌ ElevenLabs: Error - {e}")
        else:
            click.echo("❌ ElevenLabs: No API key found")
    except ImportError:
        click.echo("❌ ElevenLabs: Not installed")

    try:
        from gtts import gTTS

        gtts_available = True
        click.echo("✅ gTTS: Available (free)")
    except ImportError:
        click.echo("❌ gTTS: Not installed")

    # Recommend best option
    click.echo("\n🎯 Recommendation:")
    if elevenlabs_available:
        click.echo("✅ Use ElevenLabs (high quality)")
        recommended_provider = "elevenlabs"
    elif gtts_available:
        click.echo("✅ Use gTTS (free, basic quality)")
        recommended_provider = "gtts"
    else:
        click.echo("❌ Install at least one TTS provider:")
        click.echo("   For premium: Keep ElevenLabs, wait for credits to refill")
        click.echo("   For free: poetry add gtts")
        return

    # Update .env file
    env_file = Path(".env")
    if env_file.exists():
        # Read current .env
        with open(env_file, "r") as f:
            lines = f.readlines()

        # Update or add TTS_PROVIDER
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("TTS_PROVIDER="):
                lines[i] = f"TTS_PROVIDER={recommended_provider}\n"
                updated = True
                break

        if not updated:
            lines.append(f"TTS_PROVIDER={recommended_provider}\n")

        # Write back to .env
        with open(env_file, "w") as f:
            f.writelines(lines)

        click.echo(f"✅ Updated .env with TTS_PROVIDER={recommended_provider}")

    click.echo("\n🧪 Testing TTS setup...")

    # Test the TTS system
    async def test_tts():
        try:
            from core.content.tts import TTSService

            tts = TTSService()

            test_audio = await tts.generate_speech(
                "Hello, this is a test of the TTS system.",
                filename="tts_setup_test.mp3",
            )

            click.echo(f"✅ TTS test successful with {tts.provider}")
            click.echo(f"📁 Test audio: {test_audio}")

        except Exception as e:
            click.echo(f"❌ TTS test failed: {e}")

    import asyncio

    asyncio.run(test_tts())


@cli.command()
def install_free_tts():
    """Install free TTS alternative"""
    click.echo("📦 Installing free TTS (gTTS)...")

    try:
        import subprocess

        result = subprocess.run(
            ["poetry", "add", "gtts"], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.echo("✅ gTTS installed successfully!")

            # Update .env to use gTTS
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, "a") as f:
                    f.write("\nTTS_PROVIDER=gtts\n")
                click.echo("✅ Updated .env to use gTTS")

            click.echo("\n🧪 Testing free TTS...")

            # Test gTTS
            async def test_gtts():
                try:
                    from core.content.tts import TTSService

                    tts = TTSService()

                    test_audio = await tts.generate_speech(
                        "Hello, this is a test of the free TTS system.",
                        filename="free_tts_test.mp3",
                    )

                    click.echo(f"✅ Free TTS working! Audio: {test_audio}")

                except Exception as e:
                    click.echo(f"❌ Free TTS test failed: {e}")

            import asyncio

            asyncio.run(test_gtts())

        else:
            click.echo(f"❌ Installation failed: {result.stderr}")

    except Exception as e:
        click.echo(f"❌ Installation error: {e}")
        click.echo("Try manually: poetry add gtts")


if __name__ == "__main__":
    cli()
