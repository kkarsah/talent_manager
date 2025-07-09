# core/database/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    Float,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Talent(Base):
    """AI Talent persona model"""

    __tablename__ = "talents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    personality = Column(JSON)  # Store personality traits, tone, style
    avatar_url = Column(String(255))
    voice_id = Column(String(100))  # ElevenLabs voice ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content_items = relationship("ContentItem", back_populates="talent")
    performance_metrics = relationship("PerformanceMetric", back_populates="talent")


class ContentItem(Base):
    """Generated content items"""

    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    script = Column(Text)
    content_type = Column(String(50))  # "long_form", "short", "reel"
    platform = Column(String(50))  # "youtube", "tiktok", "instagram"
    video_url = Column(String(255))
    audio_url = Column(String(255))
    thumbnail_url = Column(String(255))
    platform_url = Column(String(255))
    status = Column(
        String(50), default="draft"
    )  # draft, generated, uploaded, published
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    talent = relationship("Talent", back_populates="content_items")
    performance_metrics = relationship(
        "PerformanceMetric", back_populates="content_item"
    )


class PerformanceMetric(Base):
    """Performance tracking for content"""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    platform = Column(String(50))
    platform_id = Column(String(100))  # Platform-specific content ID

    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)

    # Performance metrics
    click_through_rate = Column(Float, default=0.0)
    watch_time_minutes = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)

    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    talent = relationship("Talent", back_populates="performance_metrics")
    content_item = relationship("ContentItem", back_populates="performance_metrics")


class PlatformAuth(Base):
    """Store platform authentication tokens"""

    __tablename__ = "platform_auth"

    id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.id"))
    platform = Column(String(50))
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrendingTopic(Base):
    """Track trending topics for content inspiration"""

    __tablename__ = "trending_topics"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200), nullable=False)
    category = Column(String(100))  # "tech", "science", "lifestyle", etc.
    platform = Column(String(50))
    search_volume = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
