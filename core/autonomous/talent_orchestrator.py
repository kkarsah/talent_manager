# ============================================================================
# AUTONOMOUS TALENT ORCHESTRATOR
# core/autonomous/talent_orchestrator.py
# ============================================================================

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

    async def register_talent(
        self, talent_name: str, specialization: str, config: Dict[str, Any]
    ):
        """Register a talent for autonomous operation"""

        talent_config = {
            "name": talent_name,
            "specialization": specialization,
            "config": config,
            "researcher": AutonomousResearcher(specialization),
            "strategy": AutonomousContentStrategy(talent_name, specialization),
            "last_research": None,
            "last_content": None,
            "research_interval_hours": config.get("research_interval_hours", 24),
            "content_creation_enabled": config.get("autonomous_enabled", True),
        }

        self.active_talents[talent_name] = talent_config
        logger.info(f"✅ Registered autonomous talent: {talent_name}")

    async def start_autonomous_operation(self):
        """Start autonomous operation for all registered talents"""

        logger.info("🚀 Starting autonomous talent operation...")
        self.is_running = True

        # Start main autonomous loop
        await asyncio.gather(
            self._autonomous_research_loop(),
            self._autonomous_creation_loop(),
            self._job_queue_processor(),
            return_exceptions=True,
        )

    async def stop_autonomous_operation(self):
        """Stop autonomous operation"""

        logger.info("⏹️ Stopping autonomous operation...")
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
                            topics = await researcher.research_trending_topics(
                                limit=100
                            )

                        # Create content strategy
                        strategy = await talent_config[
                            "strategy"
                        ].plan_content_strategy(topics, days_ahead=7)

                        # Queue content creation jobs
                        await self._queue_content_jobs(talent_name, strategy)

                        # Update last research time
                        talent_config["last_research"] = datetime.now()

                        logger.info(
                            f"✅ Research completed for {talent_name}: {len(strategy['content_plan'])} topics queued"
                        )

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
                for talent_name, talent_config in self.active_talents.items():
                    if not talent_config["content_creation_enabled"]:
                        continue

                    # Look for jobs ready to execute
                    ready_jobs = [
                        job
                        for job in self.job_queue
                        if (
                            job.talent_name == talent_name
                            and job.scheduled_time <= current_time
                            and job.status == "scheduled"
                        )
                    ]

                    for job in ready_jobs:
                        if len(self.running_jobs) < 3:  # Limit concurrent jobs
                            await self._execute_content_job(job)

                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"❌ Creation loop error: {e}")
                await asyncio.sleep(300)

    async def _job_queue_processor(self):
        """Process the job queue and manage job lifecycle"""

        while self.is_running:
            try:
                # Clean up completed jobs
                completed_job_ids = [
                    job_id
                    for job_id, job in self.running_jobs.items()
                    if job.status in ["completed", "failed"]
                ]

                for job_id in completed_job_ids:
                    completed_job = self.running_jobs.pop(job_id)
                    self.completed_jobs.append(completed_job)

                    # Keep only last 100 completed jobs
                    if len(self.completed_jobs) > 100:
                        self.completed_jobs = self.completed_jobs[-100:]

                # Log status
                if self.running_jobs or self.job_queue:
                    logger.info(
                        f"📊 Jobs - Queue: {len(self.job_queue)}, Running: {len(self.running_jobs)}, Completed: {len(self.completed_jobs)}"
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"❌ Job processor error: {e}")
                await asyncio.sleep(60)

    def _should_research(self, talent_config: Dict[str, Any]) -> bool:
        """Check if talent should perform new research"""

        if not talent_config["last_research"]:
            return True

        hours_since_research = (
            datetime.now() - talent_config["last_research"]
        ).total_seconds() / 3600
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
                created_at=datetime.now(),
            )

            self.job_queue.append(job)

        # Sort queue by priority and schedule time
        self.job_queue.sort(key=lambda x: (x.priority, x.scheduled_time), reverse=True)

    async def _execute_content_job(self, job: AutonomousJob):
        """Execute a content creation job"""

        logger.info(
            f"🎬 Starting autonomous content creation: {job.talent_name} - {job.topic}"
        )

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
                auto_upload=True,
                research_context=job.research_data,
            )

            # Update job with results
            job.status = "completed" if result.get("success") else "failed"
            job.result = result
            job.completed_at = datetime.now()

            if result.get("success"):
                logger.info(
                    f"✅ Autonomous content completed: {job.talent_name} - {result.get('title')}"
                )

                # Update talent's last content time
                if job.talent_name in self.active_talents:
                    self.active_talents[job.talent_name][
                        "last_content"
                    ] = datetime.now()
            else:
                logger.error(
                    f"❌ Autonomous content failed: {job.talent_name} - {result.get('error')}"
                )
                job.error = result.get("error")

        except Exception as e:
            logger.error(f"❌ Job execution error: {e}")
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.now()

    async def get_talent_status(
        self, talent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get status of autonomous talents"""

        if talent_name:
            talent_config = self.active_talents.get(talent_name)
            if not talent_config:
                return {"error": f"Talent {talent_name} not found"}

            # Get talent-specific status
            talent_jobs = [
                job for job in self.job_queue if job.talent_name == talent_name
            ]
            talent_running = [
                job
                for job in self.running_jobs.values()
                if job.talent_name == talent_name
            ]
            talent_completed = [
                job for job in self.completed_jobs if job.talent_name == talent_name
            ]

            return {
                "talent": talent_name,
                "status": (
                    "active" if talent_config["content_creation_enabled"] else "paused"
                ),
                "last_research": talent_config["last_research"],
                "last_content": talent_config["last_content"],
                "queue_length": len(talent_jobs),
                "running_jobs": len(talent_running),
                "completed_today": len(
                    [
                        j
                        for j in talent_completed
                        if j.completed_at
                        and j.completed_at.date() == datetime.now().date()
                    ]
                ),
                "next_scheduled": (
                    talent_jobs[0].scheduled_time if talent_jobs else None
                ),
            }
        else:
            # Get overall status
            return {
                "orchestrator_running": self.is_running,
                "total_talents": len(self.active_talents),
                "active_talents": len(
                    [
                        t
                        for t in self.active_talents.values()
                        if t["content_creation_enabled"]
                    ]
                ),
                "total_queue": len(self.job_queue),
                "running_jobs": len(self.running_jobs),
                "completed_today": len(
                    [
                        j
                        for j in self.completed_jobs
                        if j.completed_at
                        and j.completed_at.date() == datetime.now().date()
                    ]
                ),
                "talents": list(self.active_talents.keys()),
            }
