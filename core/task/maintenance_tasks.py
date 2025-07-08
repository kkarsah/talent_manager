# core/tasks/maintenance_tasks.py

import logging
from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import func
from core.database.config import SessionLocal
from core.database.models import ContentItem, PerformanceMetric

logger = logging.getLogger(__name__)


@shared_task(name="cleanup_old_results")
def cleanup_old_results():
    """
    Clean up old Celery task results and temporary data
    """
    logger.info("Starting cleanup of old task results")

    try:
        from celery_app import celery_app

        # Clean up task results older than 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)

        # This would clean up Celery results if using database backend
        # For Redis backend, results expire automatically based on configuration

        # Clean up any temporary files older than 24 hours
        _cleanup_temp_files()

        # Clean up old performance metrics (keep last 90 days)
        cleanup_count = _cleanup_old_metrics()

        logger.info(f"Cleanup completed. Removed {cleanup_count} old metric records")

        return {
            "status": "success",
            "metrics_cleaned": cleanup_count,
            "cleaned_at": datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "failed_at": datetime.now().isoformat(),
        }


@shared_task(name="system_health_check")
def system_health_check():
    """
    Perform comprehensive system health check
    """
    logger.info("Performing system health check")

    health_status = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "components": {},
    }

    try:
        # Check database connectivity
        db = SessionLocal()
        try:
            talent_count = db.query(func.count(ContentItem.id)).scalar()
            health_status["components"]["database"] = {
                "status": "healthy",
                "content_count": talent_count,
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"
        finally:
            db.close()

        # Check Redis connectivity
        try:
            from celery_app import celery_app

            result = celery_app.control.ping()
            health_status["components"]["redis"] = {
                "status": "healthy" if result else "unhealthy"
            }
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Check API keys configuration
        import os

        api_status = {}
        required_apis = ["OPENAI_API_KEY", "YOUTUBE_CLIENT_ID"]

        for api in required_apis:
            api_status[api.lower()] = "configured" if os.getenv(api) else "missing"

        health_status["components"]["apis"] = api_status

        # Check recent task failures
        recent_failures = _check_recent_task_failures()
        health_status["components"]["tasks"] = {
            "recent_failures": recent_failures,
            "status": "healthy" if recent_failures < 5 else "degraded",
        }

        if recent_failures >= 10:
            health_status["status"] = "unhealthy"

        logger.info(f"Health check completed. Status: {health_status['status']}")
        return health_status

    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "status": "unhealthy",
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }


@shared_task(name="backup_database")
def backup_database():
    """
    Create a backup of important database tables
    """
    logger.info("Starting database backup")

    try:
        import json
        from pathlib import Path

        # Create backup directory
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"talent_manager_backup_{timestamp}.json"

        db = SessionLocal()
        try:
            # Backup talents
            talents = db.query(ContentItem).all()

            backup_data = {
                "backup_timestamp": datetime.now().isoformat(),
                "talents": [],
                "content_items": [],
                "performance_metrics": [],
            }

            # Export data (simplified - you might want more sophisticated backup)
            for talent in db.query(ContentItem).all():
                backup_data["content_items"].append(
                    {
                        "id": talent.id,
                        "title": talent.title,
                        "content_type": talent.content_type,
                        "status": talent.status,
                        "created_at": (
                            talent.created_at.isoformat() if talent.created_at else None
                        ),
                    }
                )

            # Save backup
            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"Database backup completed: {backup_file}")

            return {
                "status": "success",
                "backup_file": str(backup_file),
                "backup_size": backup_file.stat().st_size,
                "backed_up_at": datetime.now().isoformat(),
            }

        finally:
            db.close()

    except Exception as exc:
        logger.error(f"Database backup failed: {exc}")
        return {
            "status": "failed",
            "error": str(exc),
            "failed_at": datetime.now().isoformat(),
        }


def _cleanup_temp_files():
    """Clean up temporary files"""
    import os
    from pathlib import Path

    temp_dirs = ["content/temp", "content/audio", "content/video"]
    cutoff_time = datetime.now() - timedelta(hours=24)

    for temp_dir in temp_dirs:
        temp_path = Path(temp_dir)
        if temp_path.exists():
            for file_path in temp_path.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            logger.debug(f"Deleted old temp file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to delete {file_path}: {e}")


def _cleanup_old_metrics():
    """Clean up old performance metrics"""
    db = SessionLocal()
    try:
        ninety_days_ago = datetime.now() - timedelta(days=90)

        old_metrics = db.query(PerformanceMetric).filter(
            PerformanceMetric.collected_at < ninety_days_ago
        )

        count = old_metrics.count()
        old_metrics.delete()
        db.commit()

        return count

    except Exception as e:
        logger.error(f"Failed to cleanup old metrics: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def _check_recent_task_failures():
    """Check for recent task failures (simplified)"""
    # This is a simplified version - in production you might track this in database
    # or use Celery's task history
    try:
        from celery_app import celery_app

        # Get active tasks
        active_tasks = celery_app.control.active()
        reserved_tasks = celery_app.control.reserved()

        # For now, return 0 - you could implement more sophisticated failure tracking
        return 0

    except Exception:
        return 0
