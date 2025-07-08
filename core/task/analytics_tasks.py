# core/tasks/analytics_tasks.py

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.database.config import SessionLocal
from core.database.models import Talent, ContentItem, PerformanceMetric
from platforms.youtube.service import YouTubeService

logger = logging.getLogger(__name__)


@shared_task(name="collect_all_metrics")
def collect_all_metrics():
    """
    Collect performance metrics for all published content
    """
    logger.info("Starting performance metrics collection")

    db = SessionLocal()
    try:
        # Get all published content from last 30 days that needs metrics update
        thirty_days_ago = datetime.now() - timedelta(days=30)

        content_items = (
            db.query(ContentItem)
            .filter(
                ContentItem.status.in_(["published", "uploaded"]),
                ContentItem.created_at >= thirty_days_ago,
                ContentItem.platform_url.isnot(None),
            )
            .all()
        )

        logger.info(f"Found {len(content_items)} content items to analyze")

        # Run async metrics collection
        results = asyncio.run(_collect_metrics_async(content_items))

        # Save results to database
        metrics_saved = 0
        for content_id, metrics in results.items():
            if metrics:
                _save_metrics_to_db(db, content_id, metrics)
                metrics_saved += 1

        db.commit()

        logger.info(
            f"Metrics collection completed. Saved {metrics_saved} metric records"
        )

        return {
            "status": "success",
            "content_analyzed": len(content_items),
            "metrics_saved": metrics_saved,
            "collected_at": datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Metrics collection failed: {exc}")
        db.rollback()
        return {
            "status": "failed",
            "error": str(exc),
            "failed_at": datetime.now().isoformat(),
        }
    finally:
        db.close()


@shared_task(name="analyze_talent_performance")
def analyze_talent_performance(talent_id: int):
    """
    Analyze performance trends for a specific talent
    """
    logger.info(f"Analyzing performance for talent {talent_id}")

    db = SessionLocal()
    try:
        talent = db.query(Talent).filter(Talent.id == talent_id).first()
        if not talent:
            return {"status": "error", "message": "Talent not found"}

        # Get performance data from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)

        performance_data = (
            db.query(ContentItem, PerformanceMetric)
            .join(PerformanceMetric, ContentItem.id == PerformanceMetric.content_id)
            .filter(
                ContentItem.talent_id == talent_id,
                PerformanceMetric.collected_at >= thirty_days_ago,
            )
            .all()
        )

        if not performance_data:
            return {
                "status": "success",
                "talent_name": talent.name,
                "message": "No performance data available",
                "analyzed_at": datetime.now().isoformat(),
            }

        # Analyze the data
        analysis = _analyze_performance_data(performance_data)

        # Add talent info
        analysis.update(
            {
                "talent_id": talent_id,
                "talent_name": talent.name,
                "analyzed_at": datetime.now().isoformat(),
            }
        )

        logger.info(f"Performance analysis completed for {talent.name}")
        return analysis

    except Exception as exc:
        logger.error(f"Performance analysis failed for talent {talent_id}: {exc}")
        return {
            "status": "failed",
            "talent_id": talent_id,
            "error": str(exc),
            "failed_at": datetime.now().isoformat(),
        }
    finally:
        db.close()


@shared_task(name="generate_content_insights")
def generate_content_insights(talent_id: int):
    """
    Generate insights and recommendations for content strategy
    """
    logger.info(f"Generating content insights for talent {talent_id}")

    db = SessionLocal()
    try:
        # Get performance analysis
        performance = analyze_talent_performance(talent_id)
        if performance.get("status") == "failed":
            return performance

        # Get content patterns
        content_patterns = _analyze_content_patterns(db, talent_id)

        # Generate recommendations
        recommendations = _generate_recommendations(performance, content_patterns)

        insights = {
            "status": "success",
            "talent_id": talent_id,
            "performance_summary": performance,
            "content_patterns": content_patterns,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
        }

        logger.info(f"Content insights generated for talent {talent_id}")
        return insights

    except Exception as exc:
        logger.error(f"Content insights generation failed: {exc}")
        return {
            "status": "failed",
            "talent_id": talent_id,
            "error": str(exc),
            "failed_at": datetime.now().isoformat(),
        }
    finally:
        db.close()


@shared_task(name="optimize_posting_schedule")
def optimize_posting_schedule(talent_id: int):
    """
    Analyze posting times and engagement to optimize schedule
    """
    logger.info(f"Optimizing posting schedule for talent {talent_id}")

    db = SessionLocal()
    try:
        # Get historical posting data with performance
        posting_data = (
            db.query(ContentItem, PerformanceMetric)
            .join(PerformanceMetric)
            .filter(
                ContentItem.talent_id == talent_id,
                ContentItem.created_at >= datetime.now() - timedelta(days=60),
            )
            .all()
        )

        if len(posting_data) < 5:
            return {
                "status": "insufficient_data",
                "talent_id": talent_id,
                "message": "Need at least 5 posts with metrics for optimization",
            }

        # Analyze posting patterns
        schedule_analysis = _analyze_posting_patterns(posting_data)

        # Generate optimized schedule
        optimized_schedule = _generate_optimized_schedule(schedule_analysis)

        result = {
            "status": "success",
            "talent_id": talent_id,
            "current_patterns": schedule_analysis,
            "optimized_schedule": optimized_schedule,
            "recommendations": _generate_schedule_recommendations(schedule_analysis),
            "optimized_at": datetime.now().isoformat(),
        }

        logger.info(f"Posting schedule optimized for talent {talent_id}")
        return result

    except Exception as exc:
        logger.error(f"Schedule optimization failed: {exc}")
        return {
            "status": "failed",
            "talent_id": talent_id,
            "error": str(exc),
            "failed_at": datetime.now().isoformat(),
        }
    finally:
        db.close()


# Helper functions
async def _collect_metrics_async(content_items: List[ContentItem]) -> Dict[int, Dict]:
    """Collect metrics asynchronously for multiple content items"""
    youtube_service = YouTubeService()
    results = {}

    for content in content_items:
        try:
            if content.platform == "youtube" and content.platform_url:
                # Extract video ID from URL
                video_id = (
                    content.platform_url.split("/")[-1]
                    if "/" in content.platform_url
                    else content.platform_url
                )

                # Get analytics from YouTube
                metrics = await youtube_service.get_video_analytics(video_id)
                results[content.id] = metrics

                # Small delay to avoid rate limits
                await asyncio.sleep(1)

        except Exception as exc:
            logger.warning(f"Failed to get metrics for content {content.id}: {exc}")
            results[content.id] = None

    return results


def _save_metrics_to_db(db: Session, content_id: int, metrics: Dict[str, Any]):
    """Save metrics to database"""
    try:
        # Check if metrics already exist for today
        today = datetime.now().date()
        existing = (
            db.query(PerformanceMetric)
            .filter(
                PerformanceMetric.content_id == content_id,
                func.date(PerformanceMetric.collected_at) == today,
            )
            .first()
        )

        if existing:
            # Update existing metrics
            existing.views = metrics.get("views", 0)
            existing.likes = metrics.get("likes", 0)
            existing.comments = metrics.get("comments", 0)
            existing.shares = metrics.get("shares", 0)
            existing.watch_time = metrics.get("watch_time", 0)
            existing.collected_at = datetime.now()
        else:
            # Create new metrics record
            metric = PerformanceMetric(
                content_id=content_id,
                platform="youtube",
                views=metrics.get("views", 0),
                likes=metrics.get("likes", 0),
                comments=metrics.get("comments", 0),
                shares=metrics.get("shares", 0),
                watch_time=metrics.get("watch_time", 0),
                collected_at=datetime.now(),
            )
            db.add(metric)

    except Exception as exc:
        logger.error(f"Failed to save metrics for content {content_id}: {exc}")


def _analyze_performance_data(performance_data: List) -> Dict[str, Any]:
    """Analyze performance data and return insights"""
    if not performance_data:
        return {"status": "no_data"}

    # Extract metrics
    views = [item[1].views for item in performance_data]
    likes = [item[1].likes for item in performance_data]
    comments = [item[1].comments for item in performance_data]

    # Calculate statistics
    total_views = sum(views)
    avg_views = total_views / len(views) if views else 0
    best_performing = max(performance_data, key=lambda x: x[1].views)

    # Calculate engagement rate
    total_engagement = sum(likes) + sum(comments)
    engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0

    return {
        "status": "success",
        "total_content": len(performance_data),
        "total_views": total_views,
        "average_views": round(avg_views, 2),
        "total_engagement": total_engagement,
        "engagement_rate": round(engagement_rate, 2),
        "best_performing": {
            "title": best_performing[0].title,
            "views": best_performing[1].views,
            "topic": (
                best_performing[0].description[:100] + "..."
                if best_performing[0].description
                else ""
            ),
        },
    }


def _analyze_content_patterns(db: Session, talent_id: int) -> Dict[str, Any]:
    """Analyze content patterns and topics"""
    thirty_days_ago = datetime.now() - timedelta(days=30)

    content_items = (
        db.query(ContentItem)
        .filter(
            ContentItem.talent_id == talent_id,
            ContentItem.created_at >= thirty_days_ago,
        )
        .all()
    )

    # Analyze content types
    content_types = {}
    posting_times = []

    for content in content_items:
        # Count content types
        content_type = content.content_type or "unknown"
        content_types[content_type] = content_types.get(content_type, 0) + 1

        # Track posting times
        posting_times.append(content.created_at.hour)

    # Find most common posting time
    most_common_hour = (
        max(set(posting_times), key=posting_times.count) if posting_times else None
    )

    return {
        "content_types": content_types,
        "total_content": len(content_items),
        "posting_frequency": len(content_items) / 30,  # posts per day
        "most_common_posting_hour": most_common_hour,
        "posting_times_distribution": {
            hour: posting_times.count(hour) for hour in set(posting_times)
        },
    }


def _generate_recommendations(performance: Dict, patterns: Dict) -> List[str]:
    """Generate content strategy recommendations"""
    recommendations = []

    if performance.get("engagement_rate", 0) < 2:
        recommendations.append(
            "Engagement rate is low. Consider more interactive content or better CTAs."
        )

    if performance.get("average_views", 0) < 1000:
        recommendations.append(
            "Views are below average. Consider trending topics or better thumbnails."
        )

    if patterns.get("posting_frequency", 0) < 0.5:
        recommendations.append(
            "Posting frequency is low. Aim for at least 3-4 posts per week."
        )

    content_types = patterns.get("content_types", {})
    if len(content_types) == 1:
        recommendations.append(
            "Diversify content types. Mix long-form and short content."
        )

    return recommendations


def _analyze_posting_patterns(posting_data: List) -> Dict[str, Any]:
    """Analyze when posts perform best"""
    # Group by posting time and calculate average performance
    hour_performance = {}
    day_performance = {}

    for content, metrics in posting_data:
        hour = content.created_at.hour
        day = content.created_at.strftime("%A")

        if hour not in hour_performance:
            hour_performance[hour] = []
        hour_performance[hour].append(metrics.views)

        if day not in day_performance:
            day_performance[day] = []
        day_performance[day].append(metrics.views)

    # Calculate averages
    best_hours = {
        hour: sum(views) / len(views) for hour, views in hour_performance.items()
    }
    best_days = {day: sum(views) / len(views) for day, views in day_performance.items()}

    return {
        "best_hours": sorted(best_hours.items(), key=lambda x: x[1], reverse=True)[:3],
        "best_days": sorted(best_days.items(), key=lambda x: x[1], reverse=True)[:3],
        "hour_performance": best_hours,
        "day_performance": best_days,
    }


def _generate_optimized_schedule(analysis: Dict) -> Dict[str, Any]:
    """Generate optimized posting schedule"""
    best_hours = [hour for hour, _ in analysis["best_hours"]]
    best_days = [day for day, _ in analysis["best_days"]]

    return {
        "recommended_posting_times": best_hours,
        "recommended_days": best_days,
        "optimal_frequency": "3-4 posts per week",
        "content_mix": {"long_form": "60%", "shorts": "40%"},
    }


def _generate_schedule_recommendations(analysis: Dict) -> List[str]:
    """Generate schedule-specific recommendations"""
    recommendations = []

    best_hour = analysis["best_hours"][0][0] if analysis["best_hours"] else None
    if best_hour:
        recommendations.append(f"Post around {best_hour}:00 for best engagement")

    best_day = analysis["best_days"][0][0] if analysis["best_days"] else None
    if best_day:
        recommendations.append(f"{best_day} appears to be your best performing day")

    return recommendations
