# ============================================================================
# CORE AUTONOMOUS RESEARCH ENGINE
# core/research/autonomous_researcher.py
# ============================================================================

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

    def __init__(self, talent_specialization: str = "general"):
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
            "github_trending": "https://api.github.com/search/repositories",
            "dev_to": "https://dev.to/api/articles",
            "stackoverflow": "https://api.stackexchange.com/2.3/questions",
            "tech_blogs": [
                "https://blog.openai.com/rss/",
                "https://github.blog/feed/",
                "https://stackoverflow.blog/feed/",
                "https://www.freecodecamp.org/news/rss/",
                "https://css-tricks.com/feed/",
                "https://smashingmagazine.com/feed/",
                "https://www.netlify.com/blog/index.xml",
            ],
        }

        # Specialization-specific sources
        specialization_sources = {
            "tech_education": {
                **base_sources,
                "reddit": {
                    **base_sources["reddit"],
                    "learnprogramming": "https://www.reddit.com/r/learnprogramming/hot.json",
                    "coding": "https://www.reddit.com/r/coding/hot.json",
                    "python": "https://www.reddit.com/r/Python/hot.json",
                    "javascript": "https://www.reddit.com/r/javascript/hot.json",
                },
                "youtube_trending": "https://www.googleapis.com/youtube/v3/videos",
                "tech_blogs": base_sources["tech_blogs"]
                + [
                    "https://realpython.com/atom.xml",
                    "https://javascript.plainenglish.io/feed",
                    "https://blog.logrocket.com/feed/",
                ],
            },
            "cooking": {
                "reddit": {
                    "cooking": "https://www.reddit.com/r/Cooking/hot.json",
                    "recipes": "https://www.reddit.com/r/recipes/hot.json",
                    "mealprep": "https://www.reddit.com/r/MealPrepSunday/hot.json",
                },
                "food_blogs": [
                    "https://www.seriouseats.com/rss",
                    "https://www.foodnetwork.com/feeds/all-latest-recipes.rss",
                    "https://www.allrecipes.com/rss/daily-dish/",
                ],
            },
            "fitness": {
                "reddit": {
                    "fitness": "https://www.reddit.com/r/fitness/hot.json",
                    "bodyweightfitness": "https://www.reddit.com/r/bodyweightfitness/hot.json",
                },
                "fitness_blogs": [
                    "https://www.bodybuilding.com/rss/all-articles.xml",
                    "https://www.nerdfitness.com/feed/",
                ],
            },
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

        # Research from all sources concurrently
        research_tasks = [
            self._research_reddit(),
            self._research_hackernews(),
            self._research_github_trending(),
            self._research_dev_to(),
            self._research_tech_blogs(),
            self._research_stackoverflow(),
        ]

        results = await asyncio.gather(*research_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_topics.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Research task failed: {result}")

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

                        for post in data["data"]["children"][:20]:
                            post_data = post["data"]

                            topic = ResearchTopic(
                                title=post_data["title"],
                                url=post_data.get("url", ""),
                                source=f"reddit_{subreddit_name}",
                                category=subreddit_name,
                                trending_score=post_data.get("score", 0)
                                / 1000,  # Normalize
                                publish_date=datetime.fromtimestamp(
                                    post_data["created_utc"]
                                ),
                                keywords=self._extract_keywords(post_data["title"]),
                                audience_match=0.0,  # Will be calculated later
                                talent_expertise_match=0.0,  # Will be calculated later
                                content_potential=0.0,  # Will be calculated later
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

            # Get details for top 30 stories
            for story_id in story_ids[:30]:
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
                                trending_score=story_data.get("score", 0)
                                / 500,  # Normalize
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
                    logger.warning(f"Failed to fetch HN story {story_id}: {e}")

        except Exception as e:
            logger.warning(f"Hacker News research failed: {e}")

        return topics

    async def _research_github_trending(self) -> List[ResearchTopic]:
        """Research trending GitHub repositories"""

        topics = []

        try:
            # Search for repositories trending in the last week
            last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            params = {
                "q": f"created:>{last_week}",
                "sort": "stars",
                "order": "desc",
                "per_page": 30,
            }

            async with self.session.get(
                self.research_sources["github_trending"], params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    for repo in data.get("items", []):
                        topic = ResearchTopic(
                            title=f"{repo['name']}: {repo.get('description', '')[:100]}",
                            url=repo["html_url"],
                            source="github_trending",
                            category=repo.get("language", "general").lower(),
                            trending_score=repo["stargazers_count"] / 1000,  # Normalize
                            publish_date=datetime.fromisoformat(
                                repo["created_at"].replace("Z", "+00:00")
                            ),
                            keywords=self._extract_keywords(
                                f"{repo['name']} {repo.get('description', '')}"
                            ),
                            audience_match=0.0,
                            talent_expertise_match=0.0,
                            content_potential=0.0,
                            raw_data=repo,
                        )

                        topics.append(topic)

        except Exception as e:
            logger.warning(f"GitHub trending research failed: {e}")

        return topics

    async def _research_dev_to(self) -> List[ResearchTopic]:
        """Research trending articles from Dev.to"""

        topics = []

        try:
            params = {"per_page": 30, "top": 7}  # Top articles from last 7 days

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
                            / 100,  # Normalize
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

    async def _research_tech_blogs(self) -> List[ResearchTopic]:
        """Research latest posts from tech blogs"""

        topics = []

        for blog_url in self.research_sources.get("tech_blogs", []):
            try:
                async with self.session.get(blog_url) as response:
                    if response.status == 200:
                        feed_content = await response.text()
                        feed = feedparser.parse(feed_content)

                        for entry in feed.entries[:10]:  # Latest 10 posts per blog
                            publish_date = datetime.now()
                            if (
                                hasattr(entry, "published_parsed")
                                and entry.published_parsed
                            ):
                                publish_date = datetime(*entry.published_parsed[:6])

                            topic = ResearchTopic(
                                title=entry.title,
                                url=entry.link,
                                source=f"blog_{urlparse(blog_url).netloc}",
                                category="blog_post",
                                trending_score=1.0,  # Blog posts get base score
                                publish_date=publish_date,
                                keywords=self._extract_keywords(
                                    f"{entry.title} {getattr(entry, 'summary', '')}"
                                ),
                                audience_match=0.0,
                                talent_expertise_match=0.0,
                                content_potential=0.0,
                                raw_data={
                                    "title": entry.title,
                                    "summary": getattr(entry, "summary", ""),
                                },
                            )

                            topics.append(topic)

            except Exception as e:
                logger.warning(f"Blog research failed for {blog_url}: {e}")

        return topics

    async def _research_stackoverflow(self) -> List[ResearchTopic]:
        """Research trending questions from Stack Overflow"""

        topics = []

        try:
            params = {
                "order": "desc",
                "sort": "votes",
                "site": "stackoverflow",
                "pagesize": 30,
                "fromdate": int((datetime.now() - timedelta(days=7)).timestamp()),
            }

            async with self.session.get(
                self.research_sources["stackoverflow"], params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    for question in data.get("items", []):
                        topic = ResearchTopic(
                            title=question["title"],
                            url=question["link"],
                            source="stackoverflow",
                            category="problem_solving",
                            trending_score=question.get("score", 0) / 50,  # Normalize
                            publish_date=datetime.fromtimestamp(
                                question["creation_date"]
                            ),
                            keywords=self._extract_keywords(
                                f"{question['title']} {' '.join(question.get('tags', []))}"
                            ),
                            audience_match=0.0,
                            talent_expertise_match=0.0,
                            content_potential=0.0,
                            raw_data=question,
                        )

                        topics.append(topic)

        except Exception as e:
            logger.warning(f"Stack Overflow research failed: {e}")

        return topics

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""

        # Clean and normalize text
        text = re.sub(r"[^\w\s]", " ", text.lower())
        words = text.split()

        # Filter out common words and short words
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
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        # Return unique keywords, limited to most relevant
        return list(dict.fromkeys(keywords))[:10]

    def _score_topics(self, topics: List[ResearchTopic]) -> List[ResearchTopic]:
        """Score topics based on relevance, trending, and content potential"""

        talent_expertise = self._get_talent_expertise_keywords()

        for topic in topics:
            # Calculate audience match (how well topic matches target audience)
            topic.audience_match = self._calculate_audience_match(topic)

            # Calculate talent expertise match
            topic.talent_expertise_match = self._calculate_expertise_match(
                topic, talent_expertise
            )

            # Calculate overall content potential
            topic.content_potential = self._calculate_content_potential(topic)

        return topics

    def _get_talent_expertise_keywords(self) -> Dict[str, float]:
        """Get talent expertise keywords with weights"""

        expertise_maps = {
            "tech_education": {
                "python": 10,
                "javascript": 9,
                "react": 8,
                "node": 7,
                "api": 9,
                "github": 8,
                "vscode": 9,
                "docker": 7,
                "aws": 6,
                "git": 8,
                "machine learning": 8,
                "ai": 9,
                "typescript": 7,
                "vue": 6,
                "angular": 6,
                "backend": 8,
                "frontend": 8,
                "database": 7,
                "testing": 7,
                "debugging": 8,
                "performance": 7,
                "security": 6,
                "tutorial": 10,
                "guide": 9,
                "tips": 10,
                "tricks": 9,
                "beginners": 8,
                "advanced": 7,
                "coding": 10,
                "programming": 10,
                "development": 9,
            },
            "cooking": {
                "recipe": 10,
                "cooking": 10,
                "baking": 8,
                "meal": 9,
                "ingredients": 8,
                "kitchen": 7,
                "food": 9,
                "healthy": 8,
                "quick": 9,
                "easy": 10,
                "dinner": 8,
                "lunch": 7,
                "breakfast": 7,
                "dessert": 6,
                "vegetarian": 7,
                "protein": 6,
                "nutrition": 7,
                "prep": 8,
                "techniques": 9,
            },
            "fitness": {
                "workout": 10,
                "exercise": 10,
                "fitness": 10,
                "strength": 9,
                "cardio": 8,
                "muscle": 8,
                "training": 9,
                "bodyweight": 7,
                "gym": 7,
                "nutrition": 8,
                "weight": 7,
                "health": 8,
                "flexibility": 6,
                "endurance": 7,
                "recovery": 6,
                "beginner": 8,
                "advanced": 6,
                "routine": 9,
                "form": 7,
            },
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
                "beginner",
            ],
            "cooking": ["recipe", "cook", "meal", "food", "kitchen", "easy", "quick"],
            "fitness": [
                "workout",
                "fitness",
                "exercise",
                "health",
                "training",
                "muscle",
            ],
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

        # Weighted combination of factors
        recency_weight = 0.2
        trending_weight = 0.3
        expertise_weight = 0.3
        audience_weight = 0.2

        # Recency score (newer is better, but not too new)
        days_old = (datetime.now() - topic.publish_date).days
        recency_score = max(0, 1 - (days_old / 30))  # Optimal: 0-30 days old

        # Normalize trending score
        trending_score = min(topic.trending_score, 1.0)

        # Calculate final score
        content_potential = (
            recency_score * recency_weight
            + trending_score * trending_weight
            + topic.talent_expertise_match * expertise_weight
            + topic.audience_match * audience_weight
        )

        return content_potential
