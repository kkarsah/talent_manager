#!/usr/bin/env python3
"""
Alex CodeMaster Continuous Automation
Runs autonomous content generation on schedule
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
import sys

sys.path.append(".")


async def check_and_generate():
    """Check if it's time to generate content and do it"""

    if not os.path.exists("alex_schedule.json"):
        print("❌ No schedule configuration found")
        return False

    with open("alex_schedule.json", "r") as f:
        schedule = json.load(f)

    alex_config = schedule.get("Alex CodeMaster", {})

    if not alex_config.get("enabled", False):
        print("⏸️ Alex CodeMaster scheduling disabled")
        return False

    next_scheduled = alex_config.get("next_scheduled")
    if not next_scheduled:
        print("❓ No schedule time set")
        return False

    scheduled_time = datetime.fromisoformat(next_scheduled)
    current_time = datetime.now()

    if current_time >= scheduled_time:
        print("⏰ Time for scheduled content generation!")

        # Generate content
        success = await generate_alex_content()

        if success:
            # Update next schedule
            if alex_config.get("frequency") == "weekly":
                next_time = scheduled_time + timedelta(weeks=1)
            else:
                next_time = scheduled_time + timedelta(days=1)

            alex_config["next_scheduled"] = next_time.isoformat()
            alex_config["last_success"] = current_time.isoformat()

            schedule["Alex CodeMaster"] = alex_config

            with open("alex_schedule.json", "w") as f:
                json.dump(schedule, f, indent=2)

            print(f"✅ Next content scheduled for: {next_time}")
            return True
        else:
            print("❌ Content generation failed")
            return False
    else:
        time_until = scheduled_time - current_time
        hours = int(time_until.total_seconds() / 3600)
        minutes = int((time_until.total_seconds() % 3600) / 60)
        print(f"⏳ {hours}h {minutes}m until next Alex content")
        return False


async def generate_alex_content():
    """Generate content for Alex CodeMaster"""

    try:
        print("🎬 Generating Alex CodeMaster content...")

        # Import the working pipeline
        from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline

        # Future tech topics for Alex
        topics = [
            "Quantum Computing Breakthrough: Programming for the Quantum Age",
            "Brain-Computer Interfaces: The Next Developer Platform",
            "AI Code Generation: Is Human Programming Obsolete?",
            "Blockchain Smart Contracts: Building Autonomous Organizations",
            "5G Edge Computing: Real-Time Application Revolution",
            "Augmented Reality Development: Programming the Metaverse",
            "Neuromorphic Computing: Hardware That Thinks Like Brains",
            "Digital Twins: Simulating Reality with Code",
        ]

        import random

        topic = random.choice(topics)
        content_type = random.choice(["short_form", "long_form"])

        print(f"📰 Topic: {topic}")
        print(f"📋 Type: {content_type}")

        pipeline = EnhancedContentPipeline()

        result = await pipeline.create_enhanced_content(
            talent_name="Alex CodeMaster",
            topic=topic,
            content_type=content_type,
            auto_upload=False,  # Upload manually to ensure success
        )

        if result.get("success"):
            print("✅ Content generated successfully!")

            # Upload to YouTube manually
            video_path = result.get("video_path")
            if video_path and os.path.exists(video_path):
                youtube_url = await upload_to_youtube(video_path, topic)
                if youtube_url:
                    print(f"🔗 Uploaded: {youtube_url}")

                    # Log it
                    log_generation(topic, content_type, youtube_url, True)
                    return True

        print("❌ Content generation failed")
        return False

    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False


async def upload_to_youtube(video_path, title):
    """Upload video to YouTube"""

    try:
        from platforms.youtube.service import YouTubeService
        from dotenv import load_dotenv

        load_dotenv()

        service = YouTubeService()

        if await service.load_credentials() and service.is_authenticated():
            video_id = await service.upload_video(
                video_path=video_path,
                title=title + " - Alex CodeMaster",
                description=f"Exploring {title.lower()} with insights into future technology trends. Join Alex CodeMaster for cutting-edge tech analysis! #FutureTech #AI #Programming",
                tags=[
                    "Future Tech",
                    "AI",
                    "Programming",
                    "Technology",
                    "Alex CodeMaster",
                ],
                privacy_status="public",
            )

            if video_id:
                return f"https://youtube.com/watch?v={video_id}"

        return None

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None


def log_generation(topic, content_type, youtube_url, success):
    """Log the generation"""

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "talent": "Alex CodeMaster",
        "topic": topic,
        "content_type": content_type,
        "youtube_url": youtube_url,
        "success": success,
        "automated": True,
    }

    try:
        if os.path.exists("generation_log.json"):
            with open("generation_log.json", "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open("generation_log.json", "w") as f:
            json.dump(logs, f, indent=2)

    except Exception as e:
        print(f"❌ Logging error: {e}")


async def main():
    """Main automation loop"""

    print("🤖 Alex CodeMaster Automation Starting...")
    print("🔍 Checking for scheduled content...")

    await check_and_generate()

    print("✅ Automation check complete")


if __name__ == "__main__":
    asyncio.run(main())
