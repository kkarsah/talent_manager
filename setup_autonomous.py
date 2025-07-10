#!/usr/bin/env python3
"""
Quick setup script for autonomous system
Run this to create all necessary files
"""

import os
from pathlib import Path


def create_directories():
    """Create required directories"""
    dirs = ["core/research", "core/strategy", "core/autonomous"]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Autonomous system module\n")

    print("✅ Created directory structure")


def create_autonomous_researcher():
    """Create the autonomous researcher file"""

    code = '''# core/research/autonomous_researcher.py
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
                "webdev": "https://www.reddit.com/r/webdev/hot.json"
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
                    "javascript": "https://www.reddit.com/r/javascript/hot.json"
                }
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
        top_topics = sorted(scored_topics, key=lambda x: x.content_potential, reverse=True)[:limit]
        
        logger.info(f"✅ Research complete: {len(top_topics)} high-quality topics found")
        
        return top_topics
    
    async def _research_reddit(self) -> List[ResearchTopic]:
        """Research trending topics from Reddit"""
        
        topics = []
        
        for subreddit_name, url in self.research_sources.get("reddit", {}).items():
            try:
                async with self.session.get(url, headers={'User-Agent': 'TalentManager/1.0'}) as response:
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
                                publish_date=datetime.fromtimestamp(post_data["created_utc"]),
                                keywords=self._extract_keywords(post_data["title"]),
                                audience_match=0.0,
                                talent_expertise_match=0.0,
                                content_potential=0.0,
                                raw_data=post_data
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
            async with self.session.get(self.research_sources["hackernews"]) as response:
                story_ids = await response.json()
            
            # Get details for top 15 stories
            for story_id in story_ids[:15]:
                try:
                    async with self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json") as response:
                        story_data = await response.json()
                        
                        if story_data and story_data.get("title"):
                            topic = ResearchTopic(
                                title=story_data["title"],
                                url=story_data.get("url", ""),
                                source="hackernews",
                                category="tech_news",
                                trending_score=story_data.get("score", 0) / 500,
                                publish_date=datetime.fromtimestamp(story_data.get("time", 0)),
                                keywords=self._extract_keywords(story_data["title"]),
                                audience_match=0.0,
                                talent_expertise_match=0.0,
                                content_potential=0.0,
                                raw_data=story_data
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
            
            async with self.session.get(self.research_sources["dev_to"], params=params) as response:
                if response.status == 200:
                    articles = await response.json()
                    
                    for article in articles:
                        topic = ResearchTopic(
                            title=article["title"],
                            url=article["url"],
                            source="dev_to",
                            category="tutorial",
                            trending_score=article.get("positive_reactions_count", 0) / 100,
                            publish_date=datetime.fromisoformat(article["published_at"].replace('Z', '+00:00')),
                            keywords=self._extract_keywords(f"{article['title']} {' '.join(article.get('tag_list', []))}"),
                            audience_match=0.0,
                            talent_expertise_match=0.0,
                            content_potential=0.0,
                            raw_data=article
                        )
                        
                        topics.append(topic)
                        
        except Exception as e:
            logger.warning(f"Dev.to research failed: {e}")
        
        return topics
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        
        text = re.sub(r'[^\\w\\s]', ' ', text.lower())
        words = text.split()
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return list(dict.fromkeys(keywords))[:10]
    
    def _score_topics(self, topics: List[ResearchTopic]) -> List[ResearchTopic]:
        """Score topics based on relevance, trending, and content potential"""
        
        talent_expertise = self._get_talent_expertise_keywords()
        
        for topic in topics:
            topic.audience_match = self._calculate_audience_match(topic)
            topic.talent_expertise_match = self._calculate_expertise_match(topic, talent_expertise)
            topic.content_potential = self._calculate_content_potential(topic)
        
        return topics
    
    def _get_talent_expertise_keywords(self) -> Dict[str, float]:
        """Get talent expertise keywords with weights"""
        
        expertise_maps = {
            "tech_education": {
                "python": 10, "javascript": 9, "react": 8, "api": 9,
                "github": 8, "vscode": 9, "docker": 7, "git": 8,
                "ai": 9, "typescript": 7, "tutorial": 10, "guide": 9,
                "tips": 10, "coding": 10, "programming": 10, "development": 9
            }
        }
        
        return expertise_maps.get(self.talent_specialization, {})
    
    def _calculate_audience_match(self, topic: ResearchTopic) -> float:
        """Calculate how well topic matches target audience"""
        
        audience_keywords = {
            "tech_education": ["developer", "programmer", "coding", "tutorial", "guide", "learn"]
        }
        
        target_keywords = audience_keywords.get(self.talent_specialization, [])
        
        matches = sum(1 for keyword in target_keywords if keyword in topic.title.lower())
        return min(matches / len(target_keywords), 1.0) if target_keywords else 0.5
    
    def _calculate_expertise_match(self, topic: ResearchTopic, expertise: Dict[str, float]) -> float:
        """Calculate how well topic matches talent expertise"""
        
        total_score = 0
        max_possible = 0
        
        for keyword, weight in expertise.items():
            max_possible += weight
            if keyword in topic.title.lower() or keyword in ' '.join(topic.keywords):
                total_score += weight
        
        return total_score / max_possible if max_possible > 0 else 0.0
    
    def _calculate_content_potential(self, topic: ResearchTopic) -> float:
        """Calculate overall content potential score"""
        
        recency_weight = 0.2
        trending_weight = 0.3
        expertise_weight = 0.3
        audience_weight = 0.2
        
        days_old = (datetime.now() - topic.publish_date).days
        recency_score = max(0, 1 - (days_old / 30))
        trending_score = min(topic.trending_score, 1.0)
        
        content_potential = (
            recency_score * recency_weight +
            trending_score * trending_weight +
            topic.talent_expertise_match * expertise_weight +
            topic.audience_match * audience_weight
        )
        
        return content_potential
'''

    file_path = Path("core/research/autonomous_researcher.py")
    file_path.write_text(code)
    print("✅ Created autonomous researcher")


def create_content_strategy():
    """Create the content strategy file"""

    code = '''# core/strategy/autonomous_strategy.py
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
    
    async def plan_content_strategy(self, research_topics, days_ahead: int = 7) -> Dict[str, Any]:
        """Plan optimal content strategy for the next period"""
        
        strategy = {
            "talent": self.talent_name,
            "planning_date": datetime.now(),
            "period_days": days_ahead,
            "content_plan": [],
            "posting_schedule": [],
            "strategy_reasoning": []
        }
        
        # Select optimal topics for the period
        selected_topics = self._select_optimal_topics(research_topics, days_ahead)
        
        # Create content plan
        content_plan = self._create_content_plan(selected_topics, days_ahead)
        
        # Generate posting schedule
        posting_schedule = self._generate_posting_schedule(content_plan)
        
        strategy.update({
            "content_plan": content_plan,
            "posting_schedule": posting_schedule
        })
        
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
            "cooking": 1.0,         # Daily
            "fitness": 0.7          # 5 times per week
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
                "creation_priority": topic.content_potential
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
    
    def _generate_posting_schedule(self, content_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimal posting schedule"""
        
        schedule = []
        current_date = datetime.now()
        
        for i, content in enumerate(content_plan):
            post_date = current_date + timedelta(days=i*2)  # Every 2 days
            
            schedule_item = {
                "content_id": f"auto_{int(post_date.timestamp())}",
                "scheduled_date": post_date,
                "content": content,
                "posting_platform": "youtube",
                "auto_generate": True,
                "auto_upload": True
            }
            
            schedule.append(schedule_item)
        
        return schedule
'''

    file_path = Path("core/strategy/autonomous_strategy.py")
    file_path.write_text(code)
    print("✅ Created content strategy")


def create_talent_orchestrator():
    """Create the talent orchestrator file"""

    code = '''# core/autonomous/talent_orchestrator.py
"""
Autonomous Talent Orchestrator
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AutonomousJob:
    """Represents an autonomous content creation job"""
    job_id: str
    talent_name: str
    topic: str
    content_type: str
    scheduled_time: datetime
    priority: float
    status: str
    research_data: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AutonomousTalentOrchestrator:
    """Orchestrates multiple autonomous talents"""
    
    def __init__(self):
        self.active_talents = {}
        self.job_queue = []
        self.running_jobs = {}
        self.completed_jobs = []
        self.is_running = False
        
    async def register_talent(self, talent_name: str, specialization: str, config: Dict[str, Any]):
        """Register a talent for autonomous operation"""
        
        from core.research.autonomous_researcher import AutonomousResearcher
        from core.strategy.autonomous_strategy import AutonomousContentStrategy
        
        talent_config = {
            "name": talent_name,
            "specialization": specialization,
            "config": config,
            "researcher": AutonomousResearcher(specialization),
            "strategy": AutonomousContentStrategy(talent_name, specialization),
            "last_research": None,
            "last_content": None,
            "research_interval_hours": config.get("research_interval_hours", 24),
            "content_creation_enabled": config.get("autonomous_enabled", True)
        }
        
        self.active_talents[talent_name] = talent_config
        logger.info(f"✅ Registered autonomous talent: {talent_name}")
        
    async def start_autonomous_operation(self):
        """Start autonomous operation for all registered talents"""
        
        logger.info("🚀 Starting autonomous talent operation...")
        self.is_running = True
        
        try:
            # Start main autonomous loop
            await asyncio.gather(
                self._autonomous_research_loop(),
                self._autonomous_creation_loop(),
                return_exceptions=True
            )
        except KeyboardInterrupt:
            logger.info("⏹️ Autonomous operation stopped by user")
        finally:
            self.is_running = False
    
    async def _autonomous_research_loop(self):
        """Continuously research new topics for all talents"""
        
        while self.is_running:
            try:
                for talent_name, talent_config in self.active_talents.items():
                    if not talent_config["content_creation_enabled"]:
                        continue
                        
                    # Check if research is needed
                    if self._should_research(talent_config):
                        logger.info(f"🔍 Starting research for {talent_name}")
                        
                        # Perform research
                        async with talent_config["researcher"] as researcher:
                            topics = await researcher.research_trending_topics(limit=50)
                            
                        # Create content strategy
                        strategy = await talent_config["strategy"].plan_content_strategy(topics, days_ahead=7)
                        
                        # Queue content creation jobs
                        await self._queue_content_jobs(talent_name, strategy)
                        
                        # Update last research time
                        talent_config["last_research"] = datetime.now()
                        
                        logger.info(f"✅ Research completed for {talent_name}: {len(strategy['content_plan'])} topics queued")
                
                # Wait before next research cycle
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Research loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _autonomous_creation_loop(self):
        """Monitor and trigger content creation"""
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check for scheduled content
                ready_jobs = [
                    job for job in self.job_queue 
                    if (job.scheduled_time <= current_time and job.status == "scheduled")
                ]
                
                for job in ready_jobs[:2]:  # Limit concurrent jobs
                    if job.job_id not in self.running_jobs:
                        await self._execute_content_job(job)
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Creation loop error: {e}")
                await asyncio.sleep(300)
    
    def _should_research(self, talent_config: Dict[str, Any]) -> bool:
        """Check if talent should perform new research"""
        
        if not talent_config["last_research"]:
            return True
            
        hours_since_research = (datetime.now() - talent_config["last_research"]).total_seconds() / 3600
        return hours_since_research >= talent_config["research_interval_hours"]
    
    async def _queue_content_jobs(self, talent_name: str, strategy: Dict[str, Any]):
        """Queue content creation jobs from strategy"""
        
        for schedule_item in strategy["posting_schedule"]:
            job = AutonomousJob(
                job_id=f"auto_{talent_name}_{int(datetime.now().timestamp())}_{len(self.job_queue)}",
                talent_name=talent_name,
                topic=schedule_item["content"]["talent_angle"],
                content_type=schedule_item["content"]["content_type"],
                scheduled_time=schedule_item["scheduled_date"],
                priority=schedule_item["content"]["creation_priority"],
                status="scheduled",
                research_data=schedule_item["content"],
                created_at=datetime.now()
            )
            
            self.job_queue.append(job)
    
    async def _execute_content_job(self, job: AutonomousJob):
        """Execute a content creation job"""
        
        logger.info(f"🎬 Starting autonomous content creation: {job.talent_name} - {job.topic}")
        
        job.status = "running"
        self.running_jobs[job.job_id] = job
        
        # Remove from queue
        if job in self.job_queue:
            self.job_queue.remove(job)
        
        try:
            # Get talent's enhanced pipeline
            from core.pipeline.enhanced_content_pipeline import EnhancedContentPipeline
            
            pipeline = EnhancedContentPipeline()
            
            # Execute content creation
            result = await pipeline.create_enhanced_content(
                talent_name=job.talent_name,
                topic=job.topic,
                content_type=job.content_type,
                auto_upload=True
            )
            
            # Update job with results
            job.status = "completed" if result.get("success") else "failed"
            job.result = result
            job.completed_at = datetime.now()
            
            if result.get("success"):
                logger.info(f"✅ Autonomous content completed: {job.talent_name} - {result.get('title')}")
            else:
                logger.error(f"❌ Autonomous content failed: {job.talent_name} - {result.get('error')}")
                job.error = result.get("error")
                
        except Exception as e:
            logger.error(f"❌ Job execution error: {e}")
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.now()
        finally:
            # Move to completed
            if job.job_id in self.running_jobs:
                self.running_jobs.pop(job.job_id)
                self.completed_jobs.append(job)
    
    async def get_talent_status(self, talent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of autonomous talents"""
        
        if talent_name:
            talent_config = self.active_talents.get(talent_name)
            if not talent_config:
                return {"error": f"Talent {talent_name} not found"}
            
            # Get talent-specific status
            talent_jobs = [job for job in self.job_queue if job.talent_name == talent_name]
            talent_running = [job for job in self.running_jobs.values() if job.talent_name == talent_name]
            
            return {
                "talent": talent_name,
                "status": "active" if talent_config["content_creation_enabled"] else "paused",
                "last_research": talent_config["last_research"],
                "queue_length": len(talent_jobs),
                "running_jobs": len(talent_running),
                "next_scheduled": talent_jobs[0].scheduled_time if talent_jobs else None
            }
        else:
            # Get overall status
            return {
                "orchestrator_running": self.is_running,
                "total_talents": len(self.active_talents),
                "active_talents": len([t for t in self.active_talents.values() if t["content_creation_enabled"]]),
                "total_queue": len(self.job_queue),
                "running_jobs": len(self.running_jobs),
                "talents": list(self.active_talents.keys())
            }
'''

    file_path = Path("core/autonomous/talent_orchestrator.py")
    file_path.write_text(code)
    print("✅ Created talent orchestrator")


def install_dependencies():
    """Install required dependencies"""
    import subprocess
    import sys

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "aiohttp", "feedparser"]
        )
        print("✅ Installed dependencies (aiohttp, feedparser)")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Please run manually: pip install aiohttp feedparser")


def main():
    """Main setup function"""
    print("🚀 Setting up autonomous system...")

    create_directories()
    create_autonomous_researcher()
    create_content_strategy()
    create_talent_orchestrator()
    install_dependencies()

    print("\n✅ Autonomous system setup complete!")
    print("\nNext steps:")
    print("1. Add the CLI commands to your cli.py file")
    print("2. Run: python cli.py setup-alex-autonomous")
    print("3. Run: python cli.py autonomous start")

    print("\nFiles created:")
    print("- core/research/autonomous_researcher.py")
    print("- core/strategy/autonomous_strategy.py")
    print("- core/autonomous/talent_orchestrator.py")


if __name__ == "__main__":
    main()
