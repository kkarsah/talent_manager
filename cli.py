# cli.py

import click
import os
import sys
from dotenv import load_dotenv
import asyncio
from pathlib import Path
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.config import SessionLocal, init_db
from core.database.models import Talent, ContentItem

# Import only what exists in content_tasks
try:
    from core.tasks.content_tasks import (
        generate_content_task,
        check_content_schedule,
    )

    CELERY_TASKS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Celery tasks not available: {e}")
    CELERY_TASKS_AVAILABLE = False

# Import pipeline functions
try:
    from core.pipeline.content_pipeline import (
        ContentPipeline,
        quick_generate_content,
        quick_generate_and_upload,
    )

    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Pipeline not available: {e}")
    PIPELINE_AVAILABLE = False

# Import other components
try:
    from core.content.generator import PROGRAMMING_TOPICS, get_random_topic

    CONTENT_GEN_AVAILABLE = True
except ImportError:
    CONTENT_GEN_AVAILABLE = False

try:
    from platforms.youtube.service import YouTubeService

    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

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
def list_talents():
    """List all talents"""
    db = SessionLocal()
    try:
        talents = db.query(Talent).all()
        if not talents:
            click.echo(
                "No talents found. Create one with 'python cli.py create-talent'"
            )
            return

        click.echo(f"Found {len(talents)} talent(s):")
        for talent in talents:
            status = "Active" if talent.is_active else "Inactive"
            click.echo(
                f"  [{talent.id}] {talent.name} - {talent.specialization} ({status})"
            )
    finally:
        db.close()


@cli.command()
@click.option("--name", prompt="Talent name", help="Name of the talent")
@click.option(
    "--specialization", prompt="Specialization", help="What the talent specializes in"
)
def create_talent(name, specialization):
    """Create a new talent"""
    db = SessionLocal()
    try:
        talent = Talent(
            name=name,
            specialization=specialization,
            personality={"tone": "friendly", "expertise": "intermediate"},
            is_active=True,
        )
        db.add(talent)
        db.commit()
        db.refresh(talent)
        click.echo(f"✅ Created talent: {talent.name} (ID: {talent.id})")
    except Exception as e:
        click.echo(f"❌ Failed to create talent: {e}")
    finally:
        db.close()


@cli.command()
def create_alex():
    """Create Alex CodeMaster talent quickly"""
    db = SessionLocal()
    try:
        # Check if Alex already exists
        existing = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
        if existing:
            click.echo("✅ Alex CodeMaster already exists!")
            click.echo(f"   ID: {existing.id}")
            return

        talent = Talent(
            name="Alex CodeMaster",
            specialization="Programming Tutorials",
            personality={
                "tone": "friendly and encouraging",
                "expertise_level": "intermediate to advanced",
                "teaching_style": "hands-on with practical examples",
            },
            is_active=True,
        )
        db.add(talent)
        db.commit()
        db.refresh(talent)
        click.echo(f"✅ Created Alex CodeMaster (ID: {talent.id})")
    except Exception as e:
        click.echo(f"❌ Failed to create Alex: {e}")
    finally:
        db.close()


@cli.command()
def youtube_status():
    """Check YouTube authentication status"""
    if not YOUTUBE_AVAILABLE:
        click.echo("❌ YouTube service not available (missing dependencies)")
        return

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
def youtube_auth():
    """Authenticate with YouTube"""
    if not YOUTUBE_AVAILABLE:
        click.echo("❌ YouTube service not available (missing dependencies)")
        return

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
def test_pipeline():
    """Test the complete content pipeline"""
    if not PIPELINE_AVAILABLE:
        click.echo("❌ Content pipeline not available (missing dependencies)")
        return

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
            working_components = sum(1 for v in results.values() if v)
            total_components = len(results)
            health_percentage = (working_components / total_components) * 100

            click.echo(
                f"\n📊 System Health: {health_percentage:.1f}% ({working_components}/{total_components} components working)"
            )

            if health_percentage >= 75:
                click.echo("✅ System is ready for content generation!")
            else:
                click.echo(
                    "⚠️  Some components need attention before full functionality"
                )

        except Exception as e:
            click.echo(f"❌ Pipeline test failed: {e}")

    asyncio.run(run_test())


@cli.command()
@click.option(
    "--talent-id",
    type=int,
    prompt="Talent ID",
    help="ID of the talent to generate content for",
)
@click.option("--topic", help="Specific topic (optional, random if not provided)")
@click.option(
    "--content-type", default="long_form", help="Content type (long_form, short_form)"
)
@click.option("--upload", is_flag=True, help="Upload to YouTube after generation")
def generate(talent_id, topic, content_type, upload):
    """Generate content for a talent"""
    if not PIPELINE_AVAILABLE:
        click.echo("❌ Content pipeline not available (missing dependencies)")
        return

    click.echo(f"🎬 Generating content for talent {talent_id}...")
    if topic:
        click.echo(f"📚 Topic: {topic}")
    else:
        click.echo("📚 Topic: Random topic will be selected")

    async def run_generation():
        try:
            if upload:
                if not YOUTUBE_AVAILABLE:
                    click.echo(
                        "❌ YouTube upload requested but YouTube service not available"
                    )
                    return

                result = await quick_generate_and_upload(talent_id, topic, content_type)
                click.echo("✅ Content generated and uploaded to YouTube!")
                if "youtube_url" in result:
                    click.echo(f"🎥 YouTube URL: {result['youtube_url']}")
            else:
                result = await quick_generate_content(talent_id, topic, content_type)
                click.echo("✅ Content generated!")

            click.echo(f"📁 Files created in content/ directory")
            if "video_path" in result:
                click.echo(f"🎥 Video: {result['video_path']}")
            if "title" in result:
                click.echo(f"📝 Title: {result['title']}")

        except Exception as e:
            click.echo(f"❌ Generation failed: {e}")

    asyncio.run(run_generation())


@cli.command()
def topics():
    """List available programming topics"""
    if not CONTENT_GEN_AVAILABLE:
        click.echo("❌ Content generator not available")
        return

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
def demo():
    """Run a complete demo of the system"""
    click.echo("🚀 Running Talent Manager Demo...")

    async def run_demo():
        try:
            # Step 1: Create Alex if not exists
            click.echo("\n1️⃣ Setting up Alex CodeMaster...")
            db = SessionLocal()
            alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()

            if not alex:
                alex = Talent(
                    name="Alex CodeMaster",
                    specialization="Programming Tutorials",
                    personality={"tone": "friendly", "expertise": "programming"},
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
            if PIPELINE_AVAILABLE:
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
            else:
                click.echo("\n2️⃣ ⚠️ Pipeline not available, skipping content generation")

            click.echo("\n🎉 Demo completed successfully!")
            click.echo("\nNext steps:")
            click.echo("- Run 'python cli.py youtube-auth' to set up YouTube")
            click.echo(
                f"- Run 'python cli.py generate --talent-id {alex.id} --upload' to create and upload content"
            )

        except Exception as e:
            click.echo(f"❌ Demo failed: {e}")

    asyncio.run(run_demo())


@cli.command()
def status():
    """Show overall system status"""
    click.echo("📊 Talent Manager System Status")
    click.echo("=" * 40)

    # Database
    try:
        db = SessionLocal()
        talent_count = db.query(Talent).count()
        content_count = db.query(ContentItem).count()
        db.close()
        click.echo(
            f"📊 Database: ✅ Connected ({talent_count} talents, {content_count} content items)"
        )
    except Exception as e:
        click.echo(f"📊 Database: ❌ Error: {e}")

    # Services
    click.echo(f"🧬 Content Pipeline: {'✅' if PIPELINE_AVAILABLE else '❌'}")
    click.echo(f"🎥 YouTube Service: {'✅' if YOUTUBE_AVAILABLE else '❌'}")
    click.echo(f"📚 Content Generator: {'✅' if CONTENT_GEN_AVAILABLE else '❌'}")
    click.echo(f"⚙️  Celery Tasks: {'✅' if CELERY_TASKS_AVAILABLE else '❌'}")

    # Environment
    api_keys = {
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "ElevenLabs": bool(os.getenv("ELEVENLABS_API_KEY")),
        "YouTube Client": bool(os.getenv("YOUTUBE_CLIENT_ID")),
    }

    click.echo("\n🔑 API Keys:")
    for service, configured in api_keys.items():
        status = "✅ Configured" if configured else "❌ Missing"
        click.echo(f"   {service}: {status}")


if __name__ == "__main__":
    cli()
