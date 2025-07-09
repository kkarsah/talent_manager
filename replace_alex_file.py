#!/usr/bin/env python3
"""
Script to replace alex_codemaster.py with the correct version
"""

from pathlib import Path


def create_correct_alex_file():
    """Create the correct alex_codemaster.py file"""

    alex_path = Path("talents/tech_educator/alex_codemaster.py")

    # The complete correct content
    correct_content = '''# talents/tech_educator/alex_codemaster.py
"""
Alex CodeMaster - Complete implementation with both required classes
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AlexCodeMaster:
    """Alex CodeMaster - Main implementation"""

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


class AlexCodeMasterProfile:
    """
    Alex CodeMaster Profile - Compatibility class for existing imports
    This class provides the expected interface for main.py and cli.py
    """
    
    def __init__(self):
        self.profile = self._load_profile()
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load Alex's complete profile from personality.json"""
        config_path = Path(__file__).parent / "personality.json"
        
        # Default profile structure that matches expected format
        default_profile = {
            "basic_info": {
                "name": "Alex CodeMaster",
                "specialization": "tech_education",
                "description": "Tech educator focused on coding tutorials and developer productivity"
            },
            "personality": {
                "style": "enthusiastic and educational",
                "tone": "professional yet approachable",
                "expertise_areas": [
                    "Python programming",
                    "Web development", 
                    "AI coding tools",
                    "Developer productivity"
                ],
                "signature_phrases": [
                    "What's up developers!",
                    "Alex's Pro Tip:",
                    "Let me show you something cool",
                    "Here's the thing developers:",
                    "Trust me on this one:"
                ],
                "hooks": [
                    "What's up developers!",
                    "Ready to level up your coding game?",
                    "Every developer needs to know this...",
                    "Let me show you something that will blow your mind..."
                ],
                "ctas": [
                    "Drop your questions in the comments below!",
                    "Subscribe for more coding tutorials!",
                    "What tool should I review next?"
                ]
            },
            "voice_settings": {
                "provider": "elevenlabs",
                "voice_id": "alex_tech_voice",
                "style": "enthusiastic"
            },
            "content_strategy": {
                "target_audience": "developers and tech enthusiasts",
                "primary_topics": [
                    "AI coding tools",
                    "Python programming", 
                    "Web development",
                    "Developer productivity"
                ]
            }
        }
        
        # Try to load from personality.json
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    personality_data = json.load(f)
                    
                # Convert personality.json format to expected profile format
                profile = {
                    "basic_info": {
                        "name": personality_data.get("name", "Alex CodeMaster"),
                        "specialization": personality_data.get("specialization", "tech_education"),
                        "description": "Tech educator focused on coding tutorials and developer productivity"
                    },
                    "personality": {
                        "style": "enthusiastic and educational",
                        "tone": "professional yet approachable",
                        "expertise_areas": personality_data.get("content_strategy", {}).get("primary_topics", default_profile["personality"]["expertise_areas"]),
                        "signature_phrases": personality_data.get("content_strategy", {}).get("signature_phrases", default_profile["personality"]["signature_phrases"]),
                        "hooks": personality_data.get("content_strategy", {}).get("hooks", default_profile["personality"]["hooks"]),
                        "ctas": personality_data.get("content_strategy", {}).get("ctas", default_profile["personality"]["ctas"])
                    },
                    "voice_settings": personality_data.get("voice_settings", default_profile["voice_settings"]),
                    "content_strategy": personality_data.get("content_strategy", default_profile["content_strategy"])
                }
                
                logger.info("Successfully loaded Alex profile from personality.json")
                return profile
                
            except Exception as e:
                logger.warning(f"Could not load personality.json: {e}, using defaults")
                return default_profile
        else:
            logger.info("personality.json not found, using default profile")
            return default_profile
    
    def get_basic_info(self) -> Dict[str, Any]:
        """Get basic info for compatibility"""
        return self.profile["basic_info"]
    
    def get_personality(self) -> Dict[str, Any]:
        """Get personality for compatibility"""
        return self.profile["personality"]
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice settings for compatibility"""
        return self.profile["voice_settings"]


# For backwards compatibility, create a default instance
def create_alex_profile():
    """Factory function to create Alex profile"""
    return AlexCodeMasterProfile()


# Export commonly used classes
__all__ = ["AlexCodeMaster", "AlexCodeMasterProfile", "create_alex_profile"]
'''

    print(f"📝 Creating correct alex_codemaster.py file...")

    # Backup existing file if it exists
    if alex_path.exists():
        backup_path = alex_path.with_suffix(".py.original_backup")
        with open(alex_path, "r") as f:
            original_content = f.read()
        with open(backup_path, "w") as f:
            f.write(original_content)
        print(f"📁 Backed up original file to: {backup_path}")

    # Ensure directory exists
    alex_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the correct content
    with open(alex_path, "w") as f:
        f.write(correct_content)

    print(f"✅ Created correct alex_codemaster.py at {alex_path}")

    # Test the file by trying to import it
    try:
        import sys

        sys.path.insert(0, str(Path(".").resolve()))

        from talents.tech_educator.alex_codemaster import (
            AlexCodeMasterProfile,
            AlexCodeMaster,
        )

        # Test instantiation
        profile = AlexCodeMasterProfile()
        alex = AlexCodeMaster()

        print("✅ File creation successful - classes can be imported and instantiated")
        return True

    except Exception as e:
        print(f"❌ File creation failed - import test error: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Alex CodeMaster File Creator")
    print("=" * 40)

    success = create_correct_alex_file()

    if success:
        print("\n🎉 Success! The alex_codemaster.py file has been created correctly.")
        print("✅ Both AlexCodeMaster and AlexCodeMasterProfile classes are available.")
        print("🏃 You can now run: python cli.py test-pipeline")
    else:
        print("\n⚠️  File was created but there might be issues.")
        print("💡 Try running the import fixer script as well.")
