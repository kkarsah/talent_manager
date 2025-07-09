# talents/tech_educator/models.py
"""
Alex CodeMaster Database Models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from datetime import datetime

from core.models import Base


class AlexContent(Base):
    """Alex CodeMaster specific content tracking"""

    __tablename__ = "alex_content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    topic = Column(String(255))
    content_type = Column(String(50))

    # Alex-specific data
    personality_version = Column(String(10), default="1.0")
    enhanced_script = Column(JSON)  # Enhanced script with Alex's personality
    visual_scenes = Column(JSON)  # Runway scene prompts
    alex_pro_tips = Column(JSON)  # Alex's pro tips included
    tools_mentioned = Column(JSON)  # Tech tools mentioned
    code_examples = Column(JSON)  # Code examples included

    # Generation metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generation_time = Column(Float)
    runway_used = Column(Boolean, default=False)
    scenes_generated = Column(Integer, default=0)
    total_duration = Column(Float)

    # File paths
    video_path = Column(String(500))
    audio_path = Column(String(500))
    thumbnail_path = Column(String(500))

    # Performance tracking
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # YouTube integration
    youtube_video_id = Column(String(100))
    youtube_url = Column(String(500))
    published_at = Column(DateTime)

    # Status and costs
    status = Column(String(50), default="generating")
    generation_cost = Column(Float, default=0.0)
    error_message = Column(Text)
