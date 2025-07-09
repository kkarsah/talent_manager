# talents/tech_educator/alex_codemaster.py
"""
Alex CodeMaster - Simplified version to avoid circular imports
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AlexCodeMaster:
    """Alex CodeMaster - Simplified version"""

    def __init__(self):
        self.name = "Alex CodeMaster"
        self.specialization = "tech_education"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load Alex's configuration"""
        config_path = Path(__file__).parent / "personality.json"

        default_config = {
            "name": "Alex CodeMaster",
            "specialization": "tech_education",
            "voice_settings": {
                "provider": "elevenlabs",
                "voice_id": "alex_tech_voice",
                "style": "enthusiastic",
            },
            "content_strategy": {
                "target_audience": "developers and tech enthusiasts",
                "primary_topics": [
                    "AI coding tools",
                    "Python programming",
                    "Web development",
                    "Developer productivity",
                ],
            },
        }

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
                return default_config
        else:
            # Create default config file
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    async def generate_content_request(self, topic=None, content_type="long_form"):
        """Generate content request for Alex"""
        return {
            "topic": topic or "Default Tech Topic",
            "content_type": content_type,
            "target_audience": self.config["content_strategy"]["target_audience"],
        }

    def get_voice_settings(self):
        """Get Alex's voice settings"""
        return self.config["voice_settings"]
