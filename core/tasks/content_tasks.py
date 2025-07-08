import asyncio
import logging
from datetime import datetime
from celery import shared_task
from core.database.config import SessionLocal
from core.database.models import Talent

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="generate_content")
def generate_content_task(
    self, talent_id: int, topic: str = None, content_type: str = "long_form"
):
    try:
        logger.info(f"Starting content generation for talent {talent_id}")

        from core.pipeline.content_pipeline import quick_generate_content

        # Run the async content generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                quick_generate_content(talent_id, topic, content_type)
            )
            return {
                "status": "success",
                "talent_id": talent_id,
                "topic": topic,
                "result": result,
                "generated_at": datetime.now().isoformat(),
            }
        finally:
            loop.close()

    except Exception as exc:
        logger.error(f"Content generation failed for talent {talent_id}: {exc}")
        return {"status": "failed", "talent_id": talent_id, "error": str(exc)}


@shared_task(name="check_content_schedule")
def check_content_schedule(talent_id: int):
    db = SessionLocal()
    try:
        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        if not talent:
            return {"status": "error", "message": "Talent not found"}

        return {
            "status": "needs_content",
            "talent_name": talent.name,
            "recommendation": "Generate new content",
            "checked_at": datetime.now().isoformat(),
        }
    finally:
        db.close()
