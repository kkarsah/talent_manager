# ============================================================================
# AUTONOMOUS CONTENT STRATEGY ENGINE
# core/strategy/autonomous_strategy.py
# ============================================================================

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
        self, research_topics: List[ResearchTopic], days_ahead: int = 7
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

        # Analyze topic distribution
        topic_analysis = self._analyze_topic_distribution(research_topics)

        # Select optimal topics for the period
        selected_topics = self._select_optimal_topics(research_topics, days_ahead)

        # Create content plan
        content_plan = self._create_content_plan(selected_topics, days_ahead)

        # Generate posting schedule
        posting_schedule = self._generate_posting_schedule(content_plan)

        strategy.update(
            {
                "topic_analysis": topic_analysis,
                "content_plan": content_plan,
                "posting_schedule": posting_schedule,
                "strategy_reasoning": self._explain_strategy_decisions(
                    topic_analysis, content_plan
                ),
            }
        )

        return strategy

    def _analyze_topic_distribution(
        self, topics: List[ResearchTopic]
    ) -> Dict[str, Any]:
        """Analyze the distribution and characteristics of researched topics"""

        analysis = {
            "total_topics": len(topics),
            "sources": {},
            "categories": {},
            "trending_distribution": {},
            "recency_distribution": {},
            "quality_scores": [],
        }

        for topic in topics:
            # Source distribution
            analysis["sources"][topic.source] = (
                analysis["sources"].get(topic.source, 0) + 1
            )

            # Category distribution
            analysis["categories"][topic.category] = (
                analysis["categories"].get(topic.category, 0) + 1
            )

            # Quality tracking
            analysis["quality_scores"].append(topic.content_potential)

        # Calculate averages and insights
        if analysis["quality_scores"]:
            analysis["average_quality"] = sum(analysis["quality_scores"]) / len(
                analysis["quality_scores"]
            )
            analysis["high_quality_count"] = sum(
                1 for score in analysis["quality_scores"] if score > 0.7
            )

        return analysis

    def _select_optimal_topics(
        self, topics: List[ResearchTopic], days_ahead: int
    ) -> List[ResearchTopic]:
        """Select the best topics for content creation"""

        # Determine content frequency based on talent type
        content_frequency = self._get_content_frequency()
        total_content_needed = days_ahead * content_frequency

        # Filter high-quality topics
        high_quality_topics = [t for t in topics if t.content_potential > 0.5]

        # Ensure topic diversity
        selected_topics = self._ensure_topic_diversity(
            high_quality_topics, total_content_needed
        )

        return selected_topics[:total_content_needed]

    def _get_content_frequency(self) -> float:
        """Get daily content frequency for talent type"""

        frequency_map = {
            "tech_education": 0.5,  # Every 2 days
            "cooking": 1.0,  # Daily
            "fitness": 0.7,  # 5 times per week
            "lifestyle": 0.3,  # 2 times per week
        }

        return frequency_map.get(self.specialization, 0.5)

    def _ensure_topic_diversity(
        self, topics: List[ResearchTopic], count: int
    ) -> List[ResearchTopic]:
        """Ensure diversity in selected topics"""

        selected = []
        used_categories = set()
        used_sources = {}

        # Sort by content potential
        sorted_topics = sorted(topics, key=lambda x: x.content_potential, reverse=True)

        for topic in sorted_topics:
            if len(selected) >= count:
                break

            # Encourage category diversity
            category_count = sum(1 for t in selected if t.category == topic.category)
            source_count = used_sources.get(topic.source, 0)

            # Bias against over-representation
            if category_count < 2 and source_count < 3:
                selected.append(topic)
                used_categories.add(topic.category)
                used_sources[topic.source] = source_count + 1

        # Fill remaining slots with best available topics
        for topic in sorted_topics:
            if len(selected) >= count:
                break
            if topic not in selected:
                selected.append(topic)

        return selected

    def _create_content_plan(
        self, topics: List[ResearchTopic], days_ahead: int
    ) -> List[Dict[str, Any]]:
        """Create detailed content plan from selected topics"""

        content_plan = []

        for topic in topics:
            content_item = {
                "topic": topic.title,
                "source_url": topic.url,
                "source": topic.source,
                "category": topic.category,
                "content_type": self._determine_content_type(topic),
                "estimated_duration": self._estimate_content_duration(topic),
                "talent_angle": self._generate_talent_angle(topic),
                "key_points": self._extract_key_points(topic),
                "target_audience": self._identify_target_audience(topic),
                "content_potential": topic.content_potential,
                "creation_priority": self._calculate_priority(topic),
            }

            content_plan.append(content_item)

        # Sort by priority
        content_plan.sort(key=lambda x: x["creation_priority"], reverse=True)

        return content_plan

    def _determine_content_type(self, topic: ResearchTopic) -> str:
        """Determine optimal content type for topic"""

        # Rules based on topic characteristics
        if any(
            keyword in topic.title.lower()
            for keyword in ["quick", "tip", "trick", "hack"]
        ):
            return "short_form"
        elif any(
            keyword in topic.title.lower()
            for keyword in ["guide", "tutorial", "complete", "comprehensive"]
        ):
            return "long_form"
        elif topic.category in ["news", "announcement"]:
            return "news_reaction"
        else:
            return "long_form"  # Default

    def _generate_talent_angle(self, topic: ResearchTopic) -> str:
        """Generate talent-specific angle for the topic"""

        angles = {
            "tech_education": [
                f"Developer's guide to {topic.title}",
                f"Why every programmer should know about {topic.title}",
                f"Hands-on tutorial: {topic.title}",
                f"Pro tips for {topic.title}",
            ],
            "cooking": [
                f"Easy recipe: {topic.title}",
                f"Healthy version of {topic.title}",
                f"Quick weeknight {topic.title}",
                f"Meal prep: {topic.title}",
            ],
            "fitness": [
                f"Complete workout: {topic.title}",
                f"Beginner's guide to {topic.title}",
                f"At-home {topic.title}",
                f"Science behind {topic.title}",
            ],
        }

        talent_angles = angles.get(
            self.specialization, [f"Complete guide to {topic.title}"]
        )

        # Select most appropriate angle based on topic content
        return talent_angles[0]  # For now, use first angle

    def _generate_posting_schedule(
        self, content_plan: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimal posting schedule"""

        schedule = []
        current_date = datetime.now()

        # Get posting preferences for talent
        posting_prefs = self._get_posting_preferences()

        for i, content in enumerate(content_plan):
            # Calculate optimal posting time
            post_date = self._calculate_posting_date(current_date, i, posting_prefs)

            schedule_item = {
                "content_id": f"auto_{int(post_date.timestamp())}",
                "scheduled_date": post_date,
                "content": content,
                "posting_platform": "youtube",  # Primary platform
                "auto_generate": True,
                "auto_upload": True,
            }

            schedule.append(schedule_item)

        return schedule

    def _get_posting_preferences(self) -> Dict[str, Any]:
        """Get posting preferences for talent"""

        preferences = {
            "tech_education": {
                "frequency": "every_2_days",
                "best_days": ["tuesday", "wednesday", "thursday"],
                "best_times": ["10:00", "14:00", "16:00"],  # Peak developer activity
                "avoid_days": ["friday", "saturday"],  # Lower engagement
                "content_spacing_hours": 48,
            },
            "cooking": {
                "frequency": "daily",
                "best_days": ["sunday", "monday", "wednesday", "friday"],
                "best_times": ["11:00", "17:00", "19:00"],  # Meal planning times
                "avoid_days": [],
                "content_spacing_hours": 24,
            },
            "fitness": {
                "frequency": "5_times_week",
                "best_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "best_times": ["06:00", "12:00", "18:00"],  # Workout times
                "avoid_days": ["saturday", "sunday"],
                "content_spacing_hours": 24,
            },
        }

        return preferences.get(self.specialization, preferences["tech_education"])
