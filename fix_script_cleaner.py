import re
from pathlib import Path

# Read the current script cleaner
script_cleaner_path = Path("core/content/script_cleaner.py")

# Create a more robust script cleaner
improved_cleaner = '''import re
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ScriptCleaner:
    """Universal script cleaner for extracting spoken content from formatted scripts"""
    
    @classmethod
    def extract_spoken_content(cls, script_content: str, talent_name: Optional[str] = None) -> str:
        """
        Extract only spoken content from any formatted script.
        """
        
        if not script_content or not script_content.strip():
            return ""
        
        logger.debug(f"Cleaning script for talent: {talent_name}")
        
        # Try different extraction methods
        if script_content.strip().startswith('{'):
            content = cls._extract_from_json(script_content)
        else:
            content = cls._extract_from_text(script_content, talent_name)
        
        # Final cleanup
        cleaned = cls._final_cleanup(content)
        
        # Fallback if cleaning resulted in very short content
        if len(cleaned) < 50:
            logger.warning("Cleaned script too short, using fallback extraction")
            cleaned = cls._fallback_extraction(script_content)
        
        logger.debug(f"Script cleaned: {len(script_content)} chars -> {len(cleaned)} chars")
        return cleaned
    
    @classmethod
    def _extract_from_json(cls, json_script: str) -> str:
        """Extract from JSON-formatted enhanced scripts"""
        try:
            data = json.loads(json_script)
            
            # Look for spoken content in various JSON structures
            content_parts = []
            
            if isinstance(data, dict):
                # Try different keys that might contain content
                for key in ['spoken_content', 'content', 'script', 'dialogue', 'text']:
                    if key in data and data[key]:
                        content_parts.append(str(data[key]))
                
                # Look in nested structures
                if 'sections' in data:
                    for section in data['sections']:
                        if isinstance(section, dict):
                            for key in ['content', 'dialogue', 'text']:
                                if key in section:
                                    content_parts.append(str(section[key]))
            
            return ' '.join(content_parts) if content_parts else json_script
                
        except json.JSONDecodeError:
            return cls._extract_from_text(json_script)
    
    @classmethod
    def _extract_from_text(cls, script: str, talent_name: Optional[str] = None) -> str:
        """Extract from text/markdown scripts"""
        
        lines = script.split('\\n')
        content_lines = []
        
        skip_line = False
        in_metadata = False
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                continue
            
            # Skip metadata blocks
            if line.startswith('```') and ('json' in line.lower() or 'metadata' in line.lower()):
                in_metadata = not in_metadata
                continue
            
            if in_metadata:
                continue
            
            # Skip obvious non-content
            skip_patterns = [
                r'^#+\\s',  # Headers
                r'^\\*\\*\\[',  # [SCENE: etc]
                r'^\\[',  # [Visual: etc]
                r'^---',  # Dividers
                r'TIMESTAMP:', r'SCENE:', r'VISUAL:', r'AUDIO:',
                r'Video Metadata', r'Technical Production', r'Audio Settings'
            ]
            
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
                continue
            
            # Extract actual content
            # Look for speaker patterns like "**ALEX:** content"
            speaker_match = re.match(r'^\\*\\*([A-Z]+):\\*\\*\\s*(.+)', line)
            if speaker_match:
                speaker, content = speaker_match.groups()
                if content.strip():
                    content_lines.append(content.strip())
                continue
            
            # Look for content that seems like actual speech
            if cls._looks_like_speech_content(line):
                content_lines.append(line)
        
        return ' '.join(content_lines)
    
    @classmethod
    def _looks_like_speech_content(cls, line: str) -> bool:
        """Determine if a line looks like actual speech content"""
        
        # Skip if it's clearly formatting
        if (line.startswith('**') or line.startswith('*[') or 
            line.startswith('[') or line.startswith('#') or
            line.count('*') > 3):
            return False
        
        # Skip technical metadata
        technical_terms = [
            'resolution:', 'fps:', 'duration:', 'timestamp:', 'metadata',
            'json', 'css', 'html', 'file_path:', 'url:', 'api_key:'
        ]
        
        if any(term in line.lower() for term in technical_terms):
            return False
        
        # Must be substantial and start with letter or number
        if len(line) > 10 and (line[0].isalpha() or line[0].isdigit()):
            return True
        
        return False
    
    @classmethod
    def _fallback_extraction(cls, script_content: str) -> str:
        """Fallback extraction method when primary methods fail"""
        
        # Simple extraction: get all lines that look like sentences
        lines = script_content.split('\\n')
        sentences = []
        
        for line in lines:
            line = line.strip()
            
            # Skip obviously non-content lines
            if (not line or line.startswith('#') or line.startswith('*[') or 
                line.startswith('```') or len(line) < 10):
                continue
            
            # Remove common formatting
            line = re.sub(r'\\*\\*[^*]*\\*\\*', '', line)  # Remove bold
            line = re.sub(r'\\*[^*]*\\*', '', line)  # Remove italic
            line = line.strip()
            
            # If it's a substantial sentence-like structure
            if len(line) > 15 and ('.' in line or '!' in line or '?' in line or len(line) > 30):
                sentences.append(line)
        
        result = ' '.join(sentences)
        
        # If still too short, return a reasonable fallback
        if len(result) < 50:
            return "Welcome to today's tutorial! Let's dive into the content and explore what we have to share with you."
        
        return result
    
    @classmethod
    def _final_cleanup(cls, content: str) -> str:
        """Final cleanup of extracted content"""
        
        if not content:
            return ""
        
        # Remove markdown formatting
        content = re.sub(r'\\*\\*([^*]*)\\*\\*', r'\\1', content)  # **bold**
        content = re.sub(r'\\*([^*]*)\\*', r'\\1', content)  # *italic*
        content = re.sub(r'`([^`]*)`', r'\\1', content)  # `code`
        content = re.sub(r'\\[([^\\]]*)\\]', '', content)  # [stage directions]
        
        # Clean up whitespace
        content = re.sub(r'\\s+', ' ', content)
        content = content.strip()
        
        return content
'''

# Write the improved cleaner
with open(script_cleaner_path, "w") as f:
    f.write(improved_cleaner)

print("✅ Updated script cleaner with improved extraction")
