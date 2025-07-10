# core/research/autonomous_researcher.py
"""
Autonomous Research Engine for discovering trending topics
"""

import asyncio
import aiohttp
import feedparser
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


@dataclass
class ResearchTopic:
    """Structured topic from research"""

    title: str
    url: str
    source: str
    category: str
    trending_score: float
    publish_date: datetime
    keywords: List[str]
    audience_match: float
    talent_expertise_match: float
    content_potential: float
    raw_data: Dict[str, Any]


class AutonomousResearcher:
    """Universal research engine for all talents"""

    def __init__(self, talent_specialization: str = "tech_education"):
        self.talent_specialization = talent_specialization
        self.research_sources = self._get_research_sources()
        self.session = None

    def _get_research_sources(self) -> Dict[str, Any]:
        """Get research sources based on talent specialization"""

        base_sources = {
            "reddit": {
                "programming": "https://www.reddit.com/r/programming/hot.json",
                "technology": "https://www.reddit.com/r/technology/hot.json",
                "webdev": "https://www.reddit.com/r/webdev/hot.json",
            },
            "hackernews": "https://hacker-news.firebaseio.com/v0/topstories.json",
            "dev_to": "https://dev.to/api/articles",
        }

        specialization_sources = {
            "tech_education": {
                **base_sources,
                "reddit": {
                    **base_sources["reddit"],
                    "learnprogramming": "https://www.reddit.com/r/learnprogramming/hot.json",
                    "python": "https://www.reddit.com/r/Python/hot.json",
                    "javascript": "https://www.reddit.com/r/javascript/hot.json",
                },
            }
        }

        return specialization_sources.get(self.talent_specialization, base_sources)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def research_trending_topics(self, limit: int = 50) -> List[ResearchTopic]:
        """Research trending topics from all sources"""

        logger.info(f"🔍 Starting autonomous research for {self.talent_specialization}")

        all_topics = []

        # Research from sources
        try:
            reddit_topics = await self._research_reddit()
            all_topics.extend(reddit_topics)
        except Exception as e:
            logger.warning(f"Reddit research failed: {e}")

        try:
            hn_topics = await self._research_hackernews()
            all_topics.extend(hn_topics)
        except Exception as e:
            logger.warning(f"HackerNews research failed: {e}")

        try:
            devto_topics = await self._research_dev_to()
            all_topics.extend(devto_topics)
        except Exception as e:
            logger.warning(f"Dev.to research failed: {e}")

        # Score and rank topics
        scored_topics = self._score_topics(all_topics)

        # Return top topics
        top_topics = sorted(
            scored_topics, key=lambda x: x.content_potential, reverse=True
        )[:limit]

        logger.info(
            f"✅ Research complete: {len(top_topics)} high-quality topics found"
        )

        return top_topics

    async def _research_reddit(self) -> List[ResearchTopic]:
        """Research trending topics from Reddit"""

        topics = []

        for subreddit_name, url in self.research_sources.get("reddit", {}).items():
            try:
                async with self.session.get(
                    url, headers={"User-Agent": "TalentManager/1.0"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for post in data["data"]["children"][:10]:
                            post_data = post["data"]

                            topic = ResearchTopic(
                                title=post_data["title"],
                                url=post_data.get("url", ""),
                                source=f"reddit_{subreddit_name}",
                                category=subreddit_name,
                                trending_score=post_data.get("score", 0) / 1000,
                                publish_date=datetime.fromtimestamp(
                                    post_data["created_utc"]
                                ),
                                keywords=self._extract_keywords(post_data["title"]),
                                audience_match=0.0,
                                talent_expertise_match=0.0,
                                content_potential=0.0,
                                raw_data=post_data,
                            )

                            topics.append(topic)

            except Exception as e:
                logger.warning(f"Reddit research failed for {subreddit_name}: {e}")

        return topics

    async def _research_hackernews(self) -> List[ResearchTopic]:
        """Research trending topics from Hacker News"""

        topics = []

        try:
            # Get top story IDs
            async with self.session.get(
                self.research_sources["hackernews"]
            ) as response:
                story_ids = await response.json()

            # Get details for top 15 stories
            for story_id in story_ids[:15]:
                try:
                    async with self.session.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    ) as response:
                        story_data = await response.json()

                        if story_data and story_data.get("title"):
                            topic = ResearchTopic(
                                title=story_data["title"],
                                url=story_data.get("url", ""),
                                source="hackernews",
                                category="tech_news",
                                trending_score=story_data.get("score", 0) / 500,
                                publish_date=datetime.fromtimestamp(
                                    story_data.get("time", 0)
                                ),
                                keywords=self._extract_keywords(story_data["title"]),
                                audience_match=0.0,
                                talent_expertise_match=0.0,
                                content_potential=0.0,
                                raw_data=story_data,
                            )

                            topics.append(topic)

                except Exception as e:
                    continue

        except Exception as e:
            logger.warning(f"Hacker News research failed: {e}")

        return topics

    async def _research_dev_to(self) -> List[ResearchTopic]:
        """Research trending articles from Dev.to"""

        topics = []

        try:
            params = {"per_page": 20, "top": 7}

            async with self.session.get(
                self.research_sources["dev_to"], params=params
            ) as response:
                if response.status == 200:
                    articles = await response.json()

                    for article in articles:
                        topic = ResearchTopic(
                            title=article["title"],
                            url=article["url"],
                            source="dev_to",
                            category="tutorial",
                            trending_score=article.get("positive_reactions_count", 0)
                            / 100,
                            publish_date=datetime.fromisoformat(
                                article["published_at"].replace("Z", "+00:00")
                            ),
                            keywords=self._extract_keywords(
                                f"{article['title']} {' '.join(article.get('tag_list', []))}"
                            ),
                            audience_match=0.0,
                            talent_expertise_match=0.0,
                            content_potential=0.0,
                            raw_data=article,
                        )

                        topics.append(topic)

        except Exception as e:
            logger.warning(f"Dev.to research failed: {e}")

        return topics

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""

        text = re.sub(r"[^\w\s]", " ", text.lower())
        words = text.split()

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
        }

        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        return list(dict.fromkeys(keywords))[:10]

    def _score_topics(self, topics: List[ResearchTopic]) -> List[ResearchTopic]:
        """Score topics based on relevance, trending, and content potential"""

        talent_expertise = self._get_talent_expertise_keywords()

        for topic in topics:
            topic.audience_match = self._calculate_audience_match(topic)
            topic.talent_expertise_match = self._calculate_expertise_match(
                topic, talent_expertise
            )
            topic.content_potential = self._calculate_content_potential(topic)

        return topics

    def _get_talent_expertise_keywords(self) -> Dict[str, float]:
        """Get talent expertise keywords with weights"""

        expertise_maps = {
            "tech_education": {
                "python": 10,
                "javascript": 9,
                "react": 8,
                "api": 9,
                "github": 8,
                "vscode": 9,
                "docker": 7,
                "git": 8,
                "ai": 9,
                "typescript": 7,
                "tutorial": 10,
                "guide": 9,
                "tips": 10,
                "coding": 10,
                "programming": 10,
                "development": 9,
            }
        }

        return expertise_maps.get(self.talent_specialization, {})

    def _calculate_audience_match(self, topic: ResearchTopic) -> float:
        """Calculate how well topic matches target audience"""

        audience_keywords = {
            "tech_education": [
                "developer",
                "programmer",
                "coding",
                "tutorial",
                "guide",
                "learn",
            ]
        }

        target_keywords = audience_keywords.get(self.talent_specialization, [])

        matches = sum(
            1 for keyword in target_keywords if keyword in topic.title.lower()
        )
        return min(matches / len(target_keywords), 1.0) if target_keywords else 0.5

    def _calculate_expertise_match(
        self, topic: ResearchTopic, expertise: Dict[str, float]
    ) -> float:
        """Calculate how well topic matches talent expertise"""

        total_score = 0
        max_possible = 0

        for keyword, weight in expertise.items():
            max_possible += weight
            if keyword in topic.title.lower() or keyword in " ".join(topic.keywords):
                total_score += weight

        return total_score / max_possible if max_possible > 0 else 0.0

    def _calculate_content_potential(self, topic: ResearchTopic) -> float:
        """Calculate overall content potential score"""

        recency_weight = 0.2
        trending_weight = 0.3
        expertise_weight = 0.3
        audience_weight = 0.2

        # Fix timezone issue - convert both to naive datetime
        current_time = datetime.now()
        topic_time = topic.publish_date

        # If topic.publish_date is timezone-aware, convert to naive
        if topic_time.tzinfo is not None:
            topic_time = topic_time.replace(tzinfo=None)

        # Calculate days old
        try:
            days_old = (current_time - topic_time).days
        except TypeError:
            # Fallback if there's still an issue
            days_old = 1

        recency_score = max(0, 1 - (days_old / 30))  # Optimal: 0-30 days old
        trending_score = min(topic.trending_score, 1.0)

        content_potential = (
            recency_score * recency_weight
            + trending_score * trending_weight
            + topic.talent_expertise_match * expertise_weight
            + topic.audience_match * audience_weight
        )

        return content_potential
