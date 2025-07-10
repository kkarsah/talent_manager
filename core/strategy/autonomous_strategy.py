# core/strategy/autonomous_strategy.py
"""
Autonomous Content Strategy Engine
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import json


class AutonomousContentStrategy:
    """Determines optimal content strategy for talents"""

    def __init__(self, talent_name: str, specialization: str):
        self.talent_name = talent_name
        self.specialization = specialization
        self.content_calendar = []
        self.performance_history = []

    async def plan_content_strategy(
        self, research_topics, days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Plan optimal content strategy for the next period"""

        strategy = {
            "talent": self.talent_name,
            "planning_date": datetime.now(),
            "period_days": days_ahead,
            "content_plan": [],
            "posting_schedule": [],
            "strategy_reasoning": [],
        }

        # Select optimal topics for the period
        selected_topics = self._select_optimal_topics(research_topics, days_ahead)

        # Create content plan
        content_plan = self._create_content_plan(selected_topics, days_ahead)

        # Generate posting schedule
        posting_schedule = self._generate_posting_schedule(content_plan)

        strategy.update(
            {"content_plan": content_plan, "posting_schedule": posting_schedule}
        )

        return strategy

    def _select_optimal_topics(self, topics, days_ahead: int):
        """Select the best topics for content creation"""

        content_frequency = self._get_content_frequency()
        total_content_needed = max(1, int(days_ahead * content_frequency))

        # Filter high-quality topics
        high_quality_topics = [t for t in topics if t.content_potential > 0.5]

        return high_quality_topics[:total_content_needed]

    def _get_content_frequency(self) -> float:
        """Get daily content frequency for talent type"""

        frequency_map = {
            "tech_education": 0.5,  # Every 2 days
            "cooking": 1.0,  # Daily
            "fitness": 0.7,  # 5 times per week
        }

        return frequency_map.get(self.specialization, 0.5)

    def _create_content_plan(self, topics, days_ahead: int) -> List[Dict[str, Any]]:
        """Create detailed content plan from selected topics"""

        content_plan = []

        for topic in topics:
            content_item = {
                "topic": topic.title,
                "source_url": topic.url,
                "source": topic.source,
                "category": topic.category,
                "content_type": self._determine_content_type(topic),
                "talent_angle": self._generate_talent_angle(topic),
                "content_potential": topic.content_potential,
                "creation_priority": topic.content_potential,
            }

            content_plan.append(content_item)

        return content_plan

    def _determine_content_type(self, topic) -> str:
        """Determine optimal content type for topic"""

        if any(keyword in topic.title.lower() for keyword in ["quick", "tip", "trick"]):
            return "short_form"
        else:
            return "long_form"

    def _generate_talent_angle(self, topic) -> str:
        """Generate talent-specific angle for the topic"""

        if self.specialization == "tech_education":
            return f"Developer's guide to {topic.title}"
        else:
            return f"Complete guide to {topic.title}"

    def _generate_posting_schedule(
        self, content_plan: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimal posting schedule"""

        schedule = []
        current_date = datetime.now()

        for i, content in enumerate(content_plan):
            post_date = current_date + timedelta(days=i * 2)  # Every 2 days

            schedule_item = {
                "content_id": f"auto_{int(post_date.timestamp())}",
                "scheduled_date": post_date,
                "content": content,
                "posting_platform": "youtube",
                "auto_generate": True,
                "auto_upload": True,
            }

            schedule.append(schedule_item)

        return schedule
