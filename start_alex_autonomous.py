#!/usr/bin/env python3
"""
Simple Alex autonomous startup script
Bypasses the CLI registration issues
"""

import asyncio
import sys

sys.path.append(".")

from core.autonomous.talent_orchestrator import AutonomousTalentOrchestrator
from core.research.autonomous_researcher import AutonomousResearcher


async def start_alex_autonomous():
    """Start Alex's autonomous operation directly"""

    print("🤖 Starting Alex CodeMaster autonomous operation...")

    # Create orchestrator
    orchestrator = AutonomousTalentOrchestrator()

    # Register Alex
    alex_config = {
        "research_interval_hours": 12,
        "autonomous_enabled": True,
        "auto_upload": True,
        "content_frequency": 0.5,
        "quality_threshold": 0.6,
    }

    await orchestrator.register_talent("Alex CodeMaster", "tech_education", alex_config)
    print("✅ Alex registered for autonomous operation")

    # Show current research
    print("🔍 Latest research results:")
    async with AutonomousResearcher("tech_education") as researcher:
        topics = await researcher.research_trending_topics(limit=5)

    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic.title[:60]}... (Score: {topic.content_potential:.2f})")

    print("\n🚀 Starting autonomous operation...")
    print("   • Research interval: Every 12 hours")
    print("   • Content creation: Every 2 days")
    print("   • Auto-upload: Enabled")
    print("\nPress Ctrl+C to stop autonomous operation")

    # Start autonomous operation
    await orchestrator.start_autonomous_operation()


if __name__ == "__main__":
    try:
        asyncio.run(start_alex_autonomous())
    except KeyboardInterrupt:
        print("\n⏹️ Autonomous operation stopped by user")
        print("Alex CodeMaster is now paused.")
