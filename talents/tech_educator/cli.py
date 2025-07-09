# talents/tech_educator/cli.py
"""
Alex CodeMaster CLI Commands - Fixed imports
"""

import click
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Global enhanced pipeline instance
enhanced_pipeline = None


def get_enhanced_pipeline():
    """Get or create enhanced pipeline"""
    global enhanced_pipeline
    if not enhanced_pipeline:
        try:
            from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

            enhanced_pipeline = EnhancedContentPipeline()
        except Exception as e:
            logger.error(f"Could not create enhanced pipeline: {e}")
            return None
    return enhanced_pipeline


def register_alex_commands(cli_group):
    """Register Alex commands with the main CLI group"""

    @cli_group.group()
    def alex():
        """Alex CodeMaster management commands"""
        pass

    @alex.command()
    @click.option("--topic", help="Video topic (auto-generated if not provided)")
    @click.option(
        "--type",
        default="long_form",
        type=click.Choice(["long_form", "short_form", "tutorial", "tips"]),
        help="Content type",
    )
    @click.option("--upload", is_flag=True, help="Auto-upload to YouTube")
    def generate(topic, type, upload):
        """Generate content for Alex CodeMaster"""

        async def _generate():
            pipeline = get_enhanced_pipeline()
            if not pipeline:
                click.echo("❌ Enhanced pipeline not available")
                return

            click.echo(f"🎬 Generating {type} content for Alex CodeMaster...")
            if topic:
                click.echo(f"Topic: {topic}")
            else:
                click.echo("Topic: Auto-generating based on tech trends...")

            result = await pipeline.create_enhanced_content(
                talent_name="alex_codemaster",
                topic=topic,
                content_type=type,
                auto_upload=upload,
                use_runway=False,  # Start with False for now
            )

            if result.get("success"):
                click.echo(f"\n✅ Content created successfully!")
                click.echo(f"Title: {result.get('title', 'N/A')}")
                click.echo(f"Job ID: {result.get('job_id', 'N/A')}")
                click.echo(f"Content Type: {result.get('content_type', type)}")
                if result.get("video_path"):
                    click.echo(f"Video: {result['video_path']}")
                if result.get("youtube_url"):
                    click.echo(f"YouTube: {result['youtube_url']}")
            else:
                click.echo(
                    f"❌ Generation failed: {result.get('error', 'Unknown error')}"
                )

        asyncio.run(_generate())

    @alex.command()
    def status():
        """Show Alex's system status"""
        pipeline = get_enhanced_pipeline()
        if not pipeline:
            click.echo("❌ Enhanced pipeline not available")
            return

        click.echo("\n🤖 Alex CodeMaster Status")
        click.echo("=" * 40)

        alex = pipeline.alex_codemaster
        click.echo(f"Name: {alex.name}")
        click.echo(f"Specialization: {alex.specialization}")

        # System capabilities
        click.echo(f"\n⚙️ System Status:")
        click.echo(
            f"  Enhanced Pipeline: {'✅ Ready' if pipeline else '❌ Not available'}"
        )
        click.echo(
            f"  Runway: {'✅ Enabled' if pipeline.runway_enabled else '❌ Disabled'}"
        )

        # Voice settings
        voice_settings = alex.get_voice_settings()
        click.echo(f"\n🎤 Voice Settings:")
        click.echo(f"  Provider: {voice_settings.get('provider', 'Unknown')}")
        click.echo(f"  Style: {voice_settings.get('style', 'Unknown')}")

    @alex.command()
    @click.option("--topic", required=True, help="Test topic")
    def test(topic):
        """Test Alex's content generation (dry run)"""

        async def _test():
            pipeline = get_enhanced_pipeline()
            if not pipeline:
                click.echo("❌ Enhanced pipeline not available")
                return

            alex = pipeline.alex_codemaster

            click.echo(f"🧪 Testing content generation for: {topic}")

            try:
                content_request = await alex.generate_content_request(
                    topic=topic, content_type="long_form"
                )

                click.echo(f"\n✅ Content Request Generated:")
                click.echo(f"Topic: {content_request['topic']}")
                click.echo(f"Type: {content_request['content_type']}")
                click.echo(f"Audience: {content_request['target_audience']}")

            except Exception as e:
                click.echo(f"\n❌ Test failed: {e}")

        asyncio.run(_test())
