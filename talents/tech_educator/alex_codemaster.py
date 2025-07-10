# talents/tech_educator/alex_codemaster.py
"""
Alex CodeMaster - Future Tech Innovation Specialist
A passionate technology enthusiast exploring the future of innovation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AlexCodeMaster:
    """Alex CodeMaster - Future Technology Innovation Specialist"""

    def __init__(self):
        self.name = "Alex CodeMaster"
        self.specialization = "future_tech_innovation"
        self.persona = "A passionate technology enthusiast exploring the future of innovation and its impact on human life—delivered in an engaging and optimistic tone."
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load Alex's updated configuration"""
        config_path = Path(__file__).parent / "personality.json"

        default_config = {
            "name": "Alex CodeMaster",
            "specialization": "future_tech_innovation",
            "persona_description": self.persona,
            "voice_settings": {
                "provider": "elevenlabs",
                "voice_id": "alex_tech_voice",
                "style": "enthusiastic and optimistic",
                "tone": "engaging, forward-thinking, inspiring",
            },
            "content_strategy": {
                "target_audience": "innovators, entrepreneurs, tech enthusiasts, future-focused individuals",
                "primary_topics": [
                    "AI and Machine Learning trends",
                    "Blockchain and Web3 innovations",
                    "Quantum computing breakthroughs",
                    "Extended Reality developments",
                    "Clean energy and sustainability tech",
                    "Space technology and commercialization",
                ],
                "mission": "Help people understand and leverage emerging technologies for advantage",
                "content_themes": {
                    "trend_analysis": "Breaking down what's happening in emerging tech",
                    "future_predictions": "Evidence-based forecasts for technology adoption",
                    "practical_applications": "How to prepare and adapt to new technologies",
                    "innovation_stories": "Behind-the-scenes looks at breakthroughs",
                },
            },
        }

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load personality config: {e}")

        return default_config

    def get_persona_description(self) -> str:
        """Get Alex's persona description"""
        return self.config.get("persona_description", self.persona)

    def get_content_style(self) -> Dict[str, Any]:
        """Get Alex's content generation style"""
        return {
            "tone": "engaging and optimistic",
            "style": "forward-thinking and inspiring",
            "focus": "emerging technology trends and their impact",
            "approach": "practical applications with future vision",
            "expertise": self.config.get(
                "expertise_areas",
                [
                    "Artificial Intelligence",
                    "Blockchain Technology",
                    "Quantum Computing",
                    "Extended Reality",
                    "Clean Technology",
                    "Space Innovation",
                ],
            ),
        }

    def get_content_hooks(self) -> List[str]:
        """Get Alex's signature content hooks"""
        return self.config.get("content_strategy", {}).get(
            "hooks",
            [
                "The future is happening faster than you think...",
                "This breakthrough will change everything we know about...",
                "Imagine a world where...",
                "What if I told you that by 2030...",
                "This emerging technology is about to disrupt...",
                "The innovation that everyone's talking about...",
                "The future is now, and it's incredible!",
            ],
        )

    def get_signature_phrases(self) -> List[str]:
        """Get Alex's signature phrases"""
        return self.config.get("content_strategy", {}).get(
            "signature_phrases",
            [
                "The future is now, and it's incredible!",
                "Innovation never sleeps, and neither do the opportunities.",
                "Every breakthrough brings us closer to tomorrow.",
                "We're living in the most exciting time in human history.",
                "The convergence of these technologies will be game-changing.",
                "This is where science fiction becomes science fact.",
            ],
        )

    def get_ctas(self) -> List[str]:
        """Get Alex's call-to-action phrases"""
        return self.config.get("content_strategy", {}).get(
            "ctas",
            [
                "What emerging tech excites you most? Let me know below!",
                "Subscribe to stay ahead of the innovation curve!",
                "Which technology should I deep-dive into next?",
                "How will you leverage this trend in your field?",
                "Join the conversation about our tech future!",
                "Hit like if you're excited about the future!",
            ],
        )

    def get_topic_expertise(self) -> List[str]:
        """Get Alex's areas of expertise"""
        return self.config.get("content_strategy", {}).get(
            "primary_topics",
            [
                "Artificial Intelligence and Machine Learning trends",
                "Blockchain and Web3 innovations",
                "Quantum computing breakthroughs",
                "Extended Reality (AR/VR/MR) developments",
                "Clean energy and sustainability tech",
                "Space technology and commercialization",
                "Robotics and automation futures",
                "Digital transformation strategies",
            ],
        )

    def generate_content_prompt(
        self, topic: str, content_type: str = "long_form"
    ) -> str:
        """Generate a content prompt in Alex's style"""
        style = self.get_content_style()
        hooks = self.get_content_hooks()
        signature_phrases = self.get_signature_phrases()

        prompt = f"""
        Create content as Alex CodeMaster, a passionate technology enthusiast exploring the future of innovation.

        Persona: {self.get_persona_description()}

        Topic: {topic}
        Content Type: {content_type}
        
        Style Guidelines:
        - Tone: {style['tone']}
        - Approach: {style['approach']}
        - Focus: {style['focus']}
        
        Content should:
        1. Explore emerging technology trends and their impact
        2. Discuss practical applications for individuals and businesses
        3. Be optimistic and inspiring about the future
        4. Make complex topics accessible and engaging
        5. Include forward-thinking predictions and insights
        
        Use signature phrases like: {', '.join(signature_phrases[:3])}
        
        Start with an engaging hook that captures the excitement of technological innovation.
        End with actionable insights and future implications.
        """

        return prompt

    def __repr__(self):
        return f"AlexCodeMaster(specialization='{self.specialization}', persona='Future Tech Innovator')"


# Alias for backward compatibility
AlexCodeMaster2 = AlexCodeMaster


# Module-level function for easy access
def get_alex_persona() -> AlexCodeMaster:
    """Get Alex CodeMaster instance"""
    return AlexCodeMaster()
