from datetime import datetime
# cli.py - COMPLETELY FIXED VERSION
"""
Talent Manager CLI - Fixed to eliminate ALL circular imports and add Alex commands
"""

import click
import os
import sys
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import Session
import json
from datetime import datetime


# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ONLY SAFE IMPORTS - These should never cause circular imports
from core.database.config import SessionLocal, init_db
from core.database.models import Talent, ContentItem

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
    """Show overall system status"""
    click.echo("📊 Talent Manager System Status")
    click.echo("=" * 40)

    # Database status
    try:
        db = SessionLocal()
        talent_count = db.query(Talent).count()
        content_count = db.query(ContentItem).count()
        click.echo(
            f"📊 Database: ✅ Connected ({talent_count} talents, {content_count} content items)"
        )
        db.close()
    except Exception as e:
        click.echo(f"📊 Database: ❌ Error: {e}")

    # Test imports safely
    pipeline_available = False
    try:
        from core.pipeline.content_pipeline import ContentPipeline

        pipeline_available = True
        click.echo("🧬 Content Pipeline: ✅")
    except Exception as e:
        click.echo("🧬 Content Pipeline: ❌")

    youtube_available = False
    try:
        from platforms.youtube.service import YouTubeService

        youtube_available = True
        click.echo("🎥 YouTube Service: ✅")
    except Exception as e:
        click.echo("🎥 YouTube Service: ❌")

    try:
        from core.content.generator import ContentGenerator

        click.echo("📚 Content Generator: ✅")
    except Exception as e:
        click.echo("📚 Content Generator: ❌")

    try:
        from core.tasks.content_tasks import generate_content_task

        click.echo("⚙️  Celery Tasks: ✅")
    except Exception as e:
        click.echo("⚙️  Celery Tasks: ❌")

    # API Keys
    click.echo("🔑 API Keys:")
    click.echo(
        f"   OpenAI: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}"
    )
    click.echo(
        f"   ElevenLabs: {'✅ Configured' if os.getenv('ELEVENLABS_API_KEY') else '❌ Missing'}"
    )
    click.echo(
        f"   Runway: {'✅ Configured' if os.getenv('RUNWAY_API_KEY') else '❌ Missing'}"
    )
    click.echo(
        f"   YouTube Client: {'✅ Configured' if os.getenv('YOUTUBE_CLIENT_ID') else '❌ Missing'}"
    )


@cli.command()
def list_talents():
    """List all talents"""
    click.echo("🎭 Talent Manager - All Talents")
    click.echo("=" * 40)

    db = SessionLocal()
    talents = db.query(Talent).all()
    db.close()

    if not talents:
        click.echo("No talents found. Create one with: python cli.py create-talent")
        return

    for talent in talents:
        status = "Active" if talent.is_active else "Inactive"
        click.echo(
            f"  [{talent.id}] {talent.name} - {talent.specialization} ({status})"
        )


@cli.command()
@click.option("--name", prompt="Talent name", help="Name of the talent")
@click.option("--specialization", prompt="Specialization", help="Talent specialization")
def create_talent(name, specialization):
    """Create a new talent"""
    click.echo(f"Creating talent: {name}")

    db = SessionLocal()

    # Check if talent already exists
    existing = db.query(Talent).filter(Talent.name == name).first()
    if existing:
        click.echo(f"❌ Talent '{name}' already exists with ID: {existing.id}")
        db.close()
        return

    talent = Talent(
        name=name, specialization=specialization, personality={}, is_active=True
    )

    db.add(talent)
    db.commit()
    db.refresh(talent)
    db.close()

    click.echo(f"✅ Talent '{name}' created successfully with ID: {talent.id}")


@cli.command()
def create_alex():
    """Create Alex CodeMaster talent quickly"""
    click.echo("🎭 Creating Alex CodeMaster talent...")

    db = SessionLocal()

    # Check if Alex already exists
    existing = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    if existing:
        click.echo(f"✅ Alex CodeMaster already exists!")
        click.echo(f"   ID: {existing.id}")
        click.echo(f"   Specialization: {existing.specialization}")
        click.echo(f"   Status: {'Active' if existing.is_active else 'Inactive'}")
        db.close()
        return

    # Create Alex CodeMaster with predefined settings
    alex_personality = {
        "voice_style": "enthusiastic and knowledgeable",
        "visual_style": "modern tech workspace",
        "expertise_areas": ["Python", "JavaScript", "AI tools", "Web development"],
        "target_audience": "developers and tech enthusiasts",
        "content_approach": "hands-on tutorials with practical examples",
        "brand_keywords": ["coding", "programming", "tech", "AI tools", "productivity"],
        "signature_phrases": [
            "What's up developers!",
            "Alex's Pro Tip:",
            "Let me show you something cool",
        ],
    }

    talent = Talent(
        name="Alex CodeMaster",
        specialization="Programming Tutorials",
        personality=alex_personality,
        is_active=True,
    )

    db.add(talent)
    db.commit()
    db.refresh(talent)
    db.close()

    click.echo(f"✅ Alex CodeMaster created successfully!")
    click.echo(f"   ID: {talent.id}")
    click.echo(f"   Now you can use: python cli.py alex generate")


@cli.command()
@click.option("--talent-id", type=int, prompt="Talent ID", help="ID of the talent")
@click.option("--topic", prompt="Content topic", help="Topic for the content")
@click.option(
    "--type",
    "content_type",
    default="long_form",
    type=click.Choice(["long_form", "short", "tutorial"]),
    help="Type of content",
)
def generate(talent_id, topic, content_type):
    """Generate content for a talent (basic version)"""
    click.echo(f"🎬 Generating {content_type} content for talent {talent_id}: {topic}")

    # Check if talent exists
    db = SessionLocal()
    talent = db.query(Talent).filter(Talent.id == talent_id).first()
    db.close()

    if not talent:
        click.echo(f"❌ Talent with ID {talent_id} not found")
        return

    click.echo(f"✅ Found talent: {talent.name}")

    async def _generate():
        try:
            # Try to import and use the content pipeline
            from core.pipeline.content_pipeline import quick_generate_content

            result = await quick_generate_content(talent_id, topic, content_type)

            if result.get("success"):
                click.echo(f"✅ Content generated successfully!")
                click.echo(f"Title: {result.get('title', 'N/A')}")
                if result.get("video_path"):
                    click.echo(f"Video: {result['video_path']}")
            else:
                click.echo(
                    f"❌ Generation failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            click.echo(f"❌ Error during generation: {e}")
            click.echo("💡 This might be due to missing dependencies or configuration")

    asyncio.run(_generate())


@cli.command()
def test_pipeline():
    """Test the complete content pipeline"""
    click.echo("🧪 Testing content pipeline components...")

    async def _test():
        try:
            from core.pipeline.content_pipeline import ContentPipeline

            pipeline = ContentPipeline()
            results = await pipeline.test_pipeline_components()

            click.echo("Test Results:")
            for component, status in results.items():
                emoji = "✅" if status else "❌"
                click.echo(f"  {emoji} {component}")

        except Exception as e:
            click.echo(f"❌ Pipeline test failed: {e}")

    asyncio.run(_test())


@cli.command()
@click.argument("text", default="Hello! This is a test of the TTS system.")
def test_tts(text):
    """Test text-to-speech generation with script cleaning"""
    click.echo("🎤 Testing TTS system with script cleaning...")

    async def _test_tts():
        try:
            from core.content.tts import TTSService
            from core.content.script_cleaner import ScriptCleaner

            # Clean the test text (in case it has formatting)
            clean_text = ScriptCleaner.extract_spoken_content(text)
            click.echo(f"📝 Cleaned text: {clean_text[:100]}...")

            tts_service = TTSService()
            audio_path = await tts_service.generate_speech(
                clean_text, {}, "test_tts.mp3"
            )

            if audio_path and Path(audio_path).exists():
                click.echo(f"✅ TTS test successful! Audio saved to: {audio_path}")
            else:
                click.echo("❌ TTS test failed - no audio file created")

        except Exception as e:
            click.echo(f"❌ TTS test failed: {e}")

    asyncio.run(_test_tts())


@cli.command()
def topics():
    """List available programming topics"""
    try:
        from core.content.generator import PROGRAMMING_TOPICS

        click.echo("📋 Available Programming Topics:")
        click.echo("=" * 40)

        for i, topic in enumerate(PROGRAMMING_TOPICS[:10], 1):
            click.echo(f"  {i:2d}. {topic}")

        if len(PROGRAMMING_TOPICS) > 10:
            click.echo(f"  ... and {len(PROGRAMMING_TOPICS) - 10} more topics")

    except ImportError:
        click.echo("❌ Programming topics not available")


@cli.command()
def youtube_auth():
    """Authenticate with YouTube"""
    click.echo("🎥 Starting YouTube authentication...")

    async def _auth():
        try:
            from platforms.youtube.service import YouTubeService

            yt_service = YouTubeService()

            success = await yt_service.authenticate()
            if success:
                click.echo("✅ YouTube authentication successful!")
            else:
                click.echo("❌ YouTube authentication failed")
        except Exception as e:
            click.echo(f"❌ Authentication error: {e}")

    asyncio.run(_auth())


@cli.command()
def youtube_status():
    """Check YouTube authentication status"""
    try:
        from platforms.youtube.service import YouTubeService

        yt_service = YouTubeService()

        if yt_service.is_authenticated():
            click.echo("✅ YouTube is authenticated and ready")
        else:
            click.echo("❌ YouTube not authenticated. Run: python cli.py youtube-auth")
    except Exception as e:
        click.echo(f"❌ YouTube service error: {e}")


@cli.command()
def demo():
    """Run a complete demo of the system"""
    click.echo("🎬 Running Talent Manager Demo")
    click.echo("=" * 40)

    # Check if Alex exists
    db = SessionLocal()
    alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    db.close()

    if not alex:
        click.echo("Creating Alex CodeMaster...")
        ctx = click.get_current_context()
        ctx.invoke(create_alex)

        # Refresh Alex
        db = SessionLocal()
        alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
        db.close()

    if alex:
        click.echo(f"Using Alex CodeMaster (ID: {alex.id})")

        # Test content generation
        ctx = click.get_current_context()
        ctx.invoke(
            generate,
            talent_id=alex.id,
            topic="Python Tips for Beginners",
            content_type="long_form",
        )
    else:
        click.echo("❌ Could not create or find Alex CodeMaster")


@cli.command()
def run_server():
    """Run the development server"""
    click.echo("🚀 Starting development server...")
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# ===============================
# ALEX CODEMASTER COMMANDS
# ===============================


@cli.group()
def alex():
    """Alex CodeMaster specific commands"""
    pass


@alex.command()
@click.option("--topic", help="Video topic (auto-generated if not provided)")
@click.option(
    "--type",
    "content_type",
    default="long_form",
    type=click.Choice(["long_form", "short_form", "tutorial", "tips"]),
    help="Content type",
)
@click.option("--upload", is_flag=True, help="Auto-upload to YouTube")
def generate(topic, content_type, upload):
    """Generate content for Alex CodeMaster"""

    # Find Alex in database
    db = SessionLocal()
    alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    db.close()

    if not alex:
        click.echo(
            "❌ Alex CodeMaster not found. Create with: python cli.py create-alex"
        )
        return

    # Auto-generate topic if not provided
    if not topic:
        alex_topics = [
            "5 AI Coding Tools That Will Change Your Life in 2025",
            "Python Tips Every Developer Should Know",
            "VS Code Extensions That Make You 10x More Productive",
            "JavaScript Tricks That Will Blow Your Mind",
            "Docker for Developers: Complete Guide",
            "Git Commands Every Developer Must Master",
            "React vs Vue: Which Should You Choose in 2025?",
            "API Development Best Practices",
            "Database Design Mistakes to Avoid",
            "Clean Code Principles That Actually Work",
        ]
        import random

        topic = random.choice(alex_topics)
        click.echo(f"🎲 Auto-generated topic: {topic}")

    click.echo(f"🎬 Generating {content_type} content for Alex CodeMaster...")
    click.echo(f"📝 Topic: {topic}")

    # Try enhanced pipeline first, then fallback to basic
    async def _generate_alex():
        enhanced_success = False

        # Try enhanced pipeline first
        try:
            from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

            enhanced_pipeline = EnhancedContentPipeline()
            click.echo("🚀 Using enhanced pipeline with Alex's personality...")

            result = await enhanced_pipeline.create_enhanced_content(
                talent_name="alex_codemaster",
                topic=topic,
                content_type=content_type,
                auto_upload=upload,
                use_runway=False,  # Start with False for stability
            )

            if result.get("success"):
                enhanced_success = True
                click.echo(f"\n✅ Alex's enhanced content created successfully!")
                click.echo(f"📖 Title: {result.get('title', 'N/A')}")
                click.echo(f"🆔 Job ID: {result.get('job_id', 'N/A')}")
                click.echo(
                    f"🎭 Enhanced with Alex's personality: {result.get('enhanced', False)}"
                )
                click.echo(f"⏱️  Duration: {result.get('duration', 'N/A')} seconds")

                if result.get("video_path"):
                    click.echo(f"🎥 Video: {result['video_path']}")
                if result.get("audio_path"):
                    click.echo(f"🎤 Audio: {result['audio_path']}")
                if result.get("youtube_url"):
                    click.echo(f"📺 YouTube: {result['youtube_url']}")

            else:
                click.echo(
                    f"❌ Enhanced generation failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            click.echo(f"⚠️  Enhanced pipeline not available: {e}")

        # Fallback to basic generation if enhanced failed
        if not enhanced_success:
            click.echo("🔄 Falling back to basic content generation...")
            try:
                from core.pipeline.content_pipeline import quick_generate_content

                result = await quick_generate_content(alex.id, topic, content_type)

                if result.get("success"):
                    click.echo(f"\n✅ Alex's basic content generated!")
                    click.echo(f"📖 Title: {result.get('title', 'N/A')}")
                    if result.get("video_path"):
                        click.echo(f"🎥 Video: {result['video_path']}")

                    click.echo(
                        f"\n💡 Tip: Set up the enhanced pipeline for better Alex content!"
                    )
                else:
                    click.echo(
                        f"❌ Basic generation also failed: {result.get('error')}"
                    )

            except Exception as e:
                click.echo(f"❌ All generation methods failed: {e}")
                click.echo(f"💡 Check your configuration and dependencies")

    asyncio.run(_generate_alex())


@alex.command()
def status():
    """Show Alex CodeMaster status"""
    click.echo("🤖 Alex CodeMaster Status")
    click.echo("=" * 40)

    # Check if Alex exists in database
    db = SessionLocal()
    alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    db.close()

    if alex:
        click.echo(f"✅ Alex CodeMaster found (ID: {alex.id})")
        click.echo(f"📚 Specialization: {alex.specialization}")
        click.echo(f"🔄 Status: {'Active' if alex.is_active else 'Inactive'}")

        if alex.personality:
            click.echo("\n🎭 Personality traits:")
            for key, value in alex.personality.items():
                if isinstance(value, list):
                    click.echo(f"  {key}: {', '.join(value[:3])}...")
                else:
                    click.echo(f"  {key}: {value}")
    else:
        click.echo("❌ Alex CodeMaster not found")
        click.echo("Create with: python cli.py create-alex")

    # Check available pipelines
    click.echo(f"\n⚙️  Available Pipelines:")

    # Enhanced pipeline
    try:
        from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

        click.echo("✅ Enhanced pipeline (with Alex personality)")
    except ImportError:
        click.echo("❌ Enhanced pipeline not available")

    # Basic pipeline
    try:
        from core.pipeline.content_pipeline import ContentPipeline

        click.echo("✅ Basic content pipeline")
    except ImportError:
        click.echo("❌ Basic pipeline not available")

    # Content count
    if alex:
        db = SessionLocal()
        content_count = (
            db.query(ContentItem).filter(ContentItem.talent_id == alex.id).count()
        )
        db.close()
        click.echo(f"\n📊 Content created: {content_count} items")


@alex.command()
@click.option("--topic", required=True, help="Test topic")
def test(topic):
    """Test Alex's content generation (dry run)"""
    click.echo(f"🧪 Testing Alex's content generation for: {topic}")

    db = SessionLocal()
    alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    db.close()

    if not alex:
        click.echo(
            "❌ Alex CodeMaster not found. Create with: python cli.py create-alex"
        )
        return

    async def _test_alex():
        try:
            # Test enhanced pipeline if available
            from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

            enhanced_pipeline = EnhancedContentPipeline()
            alex_instance = enhanced_pipeline.alex_codemaster

            click.echo(f"✅ Alex instance loaded: {alex_instance.name}")
            click.echo(f"🎯 Specialization: {alex_instance.specialization}")

            # Test content request generation
            content_request = await alex_instance.generate_content_request(
                topic=topic, content_type="long_form"
            )

            click.echo(f"\n📝 Content Request Generated:")
            click.echo(f"📖 Topic: {content_request['topic']}")
            click.echo(f"📋 Type: {content_request['content_type']}")
            click.echo(f"👥 Audience: {content_request['target_audience']}")

            click.echo(f"\n✅ Test completed successfully!")
            click.echo(f"💡 Alex is ready to generate content!")

        except ImportError:
            click.echo("❌ Enhanced pipeline not available for testing")
            click.echo("💡 Basic pipeline test not implemented yet")
        except Exception as e:
            click.echo(f"❌ Test failed: {e}")

    asyncio.run(_test_alex())


@alex.command()
def config():
    """Show Alex's configuration"""
    db = SessionLocal()
    alex = db.query(Talent).filter(Talent.name == "Alex CodeMaster").first()
    db.close()

    if not alex:
        click.echo("❌ Alex CodeMaster not found")
        return

    click.echo("🤖 Alex CodeMaster Configuration")
    click.echo("=" * 50)

    click.echo(f"Name: {alex.name}")
    click.echo(f"ID: {alex.id}")
    click.echo(f"Specialization: {alex.specialization}")
    click.echo(f"Status: {'Active' if alex.is_active else 'Inactive'}")

    if alex.personality:
        click.echo(f"\n🎭 Personality Configuration:")
        for key, value in alex.personality.items():
            if isinstance(value, list):
                click.echo(f"  {key}:")
                for item in value[:5]:  # Show first 5 items
                    click.echo(f"    • {item}")
                if len(value) > 5:
                    click.echo(f"    ... and {len(value) - 5} more")
            else:
                click.echo(f"  {key}: {value}")


autonomous_orchestrator = None


def get_or_create_orchestrator():
    """Get or create the autonomous orchestrator with persistent config"""
    global autonomous_orchestrator

    if not autonomous_orchestrator:
        from core.autonomous.talent_orchestrator import AutonomousTalentOrchestrator

        autonomous_orchestrator = AutonomousTalentOrchestrator()

        # Load persistent talent registrations
        config_file = Path("autonomous_config.json")
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)

                for talent_name, talent_config in config.get("talents", {}).items():
                    asyncio.run(
                        autonomous_orchestrator.register_talent(
                            talent_name,
                            talent_config["specialization"],
                            talent_config["config"],
                        )
                    )

                print(f"✅ Loaded {len(config.get('talents', {}))} talents from config")
            except Exception as e:
                print(f"⚠️ Warning: Could not load config: {e}")

    return autonomous_orchestrator


def save_talent_config(talent_name: str, specialization: str, config: dict):
    """Save talent configuration persistently"""
    config_file = Path("autonomous_config.json")

    # Load existing config
    autonomous_config = {}
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                autonomous_config = json.load(f)
        except:
            autonomous_config = {}

    # Update with new talent
    if "talents" not in autonomous_config:
        autonomous_config["talents"] = {}

    autonomous_config["talents"][talent_name] = {
        "specialization": specialization,
        "config": config,
        "registered_at": datetime.now().isoformat(),
    }

    # Save config
    with open(config_file, "w") as f:
        json.dump(autonomous_config, f, indent=2)


@cli.group()
def autonomous():
    """Autonomous talent management commands"""
    pass


@autonomous.command()
@click.option("--talent", required=True, help="Talent name")
@click.option("--specialization", required=True, help="Talent specialization")
@click.option("--research-interval", default=24, help="Research interval in hours")
def register(talent, specialization, research_interval):
    """Register a talent for autonomous operation"""

    click.echo(f"📝 Registering {talent} for autonomous operation...")

    async def _register():
        orchestrator = get_or_create_orchestrator()

        config = {
            "research_interval_hours": research_interval,
            "autonomous_enabled": True,
            "auto_upload": True,
        }

        await orchestrator.register_talent(talent, specialization, config)

        # Save persistently
        save_talent_config(talent, specialization, config)

        click.echo(f"✅ {talent} registered for autonomous operation")

    asyncio.run(_register())


@autonomous.command()
def start():
    """Start autonomous operation for all registered talents"""

    click.echo("🚀 Starting autonomous talent operation...")

    async def _start():
        orchestrator = get_or_create_orchestrator()

        if not orchestrator.active_talents:
            click.echo("❌ No talents registered.")
            click.echo("💡 Run 'python cli.py setup-alex-autonomous' first")
            return

        click.echo(
            f"📊 Starting with {len(orchestrator.active_talents)} registered talents:"
        )
        for name in orchestrator.active_talents.keys():
            click.echo(f"   • {name}")

        await orchestrator.start_autonomous_operation()

    try:
        asyncio.run(_start())
    except KeyboardInterrupt:
        click.echo("\n⏹️ Autonomous operation stopped by user")


@autonomous.command()
@click.option("--talent", help="Specific talent name (optional)")
def status(talent):
    """Check autonomous operation status"""

    async def _status():
        orchestrator = get_or_create_orchestrator()

        status_data = await orchestrator.get_talent_status(talent)

        if talent:
            if "error" in status_data:
                click.echo(f"❌ {status_data['error']}")
                return

            click.echo(f"📊 Status for {talent}:")
            click.echo(f"   Status: {status_data.get('status', 'Unknown')}")
            click.echo(f"   Queue: {status_data.get('queue_length', 0)} items")
            click.echo(f"   Running: {status_data.get('running_jobs', 0)} jobs")

            if status_data.get("next_scheduled"):
                click.echo(f"   Next scheduled: {status_data['next_scheduled']}")
        else:
            click.echo("📊 Overall Autonomous Status:")
            click.echo(
                f"   Orchestrator running: {status_data.get('orchestrator_running', False)}"
            )
            click.echo(f"   Total talents: {status_data.get('total_talents', 0)}")
            click.echo(f"   Active talents: {status_data.get('active_talents', 0)}")
            click.echo(f"   Queue length: {status_data.get('total_queue', 0)}")
            click.echo(f"   Running jobs: {status_data.get('running_jobs', 0)}")

            if status_data.get("talents"):
                click.echo(
                    f"   Registered talents: {', '.join(status_data['talents'])}"
                )

    asyncio.run(_status())


@autonomous.command()
@click.option("--talent", required=True, help="Talent name")
def research(talent):
    """Trigger manual research for a talent"""

    click.echo(f"🔍 Starting research for {talent}...")

    async def _research():
        from core.research.autonomous_researcher import AutonomousResearcher

        specialization = "tech_education"  # Default for Alex

        async with AutonomousResearcher(specialization) as researcher:
            topics = await researcher.research_trending_topics(limit=20)

        click.echo(f"📊 Found {len(topics)} trending topics:")

        for i, topic in enumerate(topics[:10], 1):
            click.echo(f"  {i:2d}. {topic.title[:80]}...")
            click.echo(f"      Source: {topic.source}")
            click.echo(f"      Score: {topic.content_potential:.2f}")
            click.echo(f"      Category: {topic.category}")
            click.echo()

    asyncio.run(_research())


@autonomous.command()
@click.option("--talent", required=True, help="Talent name")
def generate_now(talent):
    """Generate content immediately for a talent"""

    click.echo(f"🎬 Generating autonomous content for {talent}...")

    async def _generate():
        from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

        pipeline = EnhancedContentPipeline()

        result = await pipeline.create_enhanced_content(
            talent_name=talent,
            topic=None,  # Let it pick autonomously
            content_type="long_form",
            auto_upload=True,
        )

        if result.get("success"):
            click.echo("✅ Autonomous content generated successfully!")
            click.echo(f"📖 Title: {result.get('title')}")
            click.echo(f"🎥 Video: {result.get('video_path')}")
            click.echo(f"📺 YouTube: {result.get('youtube_url', 'Not uploaded')}")
        else:
            click.echo(f"❌ Generation failed: {result.get('error')}")

    asyncio.run(_generate())


@cli.command()
def setup_alex_autonomous():
    """Quick setup for Alex's autonomous operation"""

    click.echo("🤖 Setting up Alex for full autonomous operation...")

    async def _setup():
        from core.research.autonomous_researcher import AutonomousResearcher

        # Register Alex with persistent config
        alex_config = {
            "research_interval_hours": 12,
            "autonomous_enabled": True,
            "auto_upload": True,
            "content_frequency": 0.5,
            "quality_threshold": 0.6,
        }

        # Save the config persistently
        save_talent_config("Alex CodeMaster", "tech_education", alex_config)

        # Register with orchestrator
        orchestrator = get_or_create_orchestrator()
        await orchestrator.register_talent(
            "Alex CodeMaster", "tech_education", alex_config
        )

        click.echo("✅ Alex registered for autonomous operation")
        click.echo("🔍 Starting initial research...")

        async with AutonomousResearcher("tech_education") as researcher:
            topics = await researcher.research_trending_topics(limit=10)

        click.echo(f"📊 Found {len(topics)} trending topics for Alex")

        if topics:
            click.echo("🎯 Top 3 topics Alex could cover:")
            for i, topic in enumerate(topics[:3], 1):
                click.echo(
                    f"  {i}. {topic.title[:60]}... (Score: {topic.content_potential:.2f})"
                )

        click.echo("\n🚀 Alex is now ready for autonomous operation!")
        click.echo(
            "Run 'python cli.py autonomous start' to begin autonomous content creation"
        )

    asyncio.run(_setup())


if __name__ == "__main__":
    cli()
