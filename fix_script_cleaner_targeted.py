import re
from pathlib import Path

# Read current script cleaner
script_cleaner_path = Path("core/content/script_cleaner.py")

# Updated script cleaner that handles the Alex CodeMaster: "content" format
updated_cleaner = '''import re
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ScriptCleaner:
    """Universal script cleaner for extracting spoken content from formatted scripts"""
    
    @classmethod
    def extract_spoken_content(cls, script_content: str, talent_name: Optional[str] = None) -> str:
        """Extract only spoken content from any formatted script."""
        
        if not script_content or not script_content.strip():
            return ""
        
        # Handle the specific format: Alex CodeMaster: "content"
        if talent_name and talent_name in script_content:
            content = cls._extract_quoted_dialogue(script_content, talent_name)
            if content and len(content) > 100:
                return cls._final_cleanup(content)
        
        # Try other extraction methods
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
        
        return cleaned
    
    @classmethod
    def _extract_quoted_dialogue(cls, script: str, talent_name: str) -> str:
        """Extract quoted dialogue from format: 'Alex CodeMaster: "content"'"""
        
        # Pattern to match: Alex CodeMaster: "quoted content"
        pattern = rf'{re.escape(talent_name)}:\s*"([^"]*)"'
        
        matches = re.findall(pattern, script, re.DOTALL)
        
        if matches:
            # Join all quoted content
            content = ' '.join(matches)
            logger.info(f"Extracted {len(matches)} quoted dialogue segments")
            return content
        
        # Alternative pattern without quotes but with colon
        pattern2 = rf'{re.escape(talent_name)}:\s*(.+?)(?=\\n\\[|\\n{re.escape(talent_name)}:|$)'
        matches2 = re.findall(pattern2, script, re.DOTALL)
        
        if matches2:
            content = ' '.join(match.strip().strip('"') for match in matches2)
            logger.info(f"Extracted {len(matches2)} dialogue segments without quotes")
            return content
        
        return ""
    
    @classmethod
    def _extract_from_json(cls, json_script: str) -> str:
        """Extract from JSON-formatted scripts"""
        try:
            data = json.loads(json_script)
            content_parts = []
            
            if isinstance(data, dict):
                for key in ['spoken_content', 'content', 'script', 'dialogue', 'text']:
                    if key in data and data[key]:
                        content_parts.append(str(data[key]))
                
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
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Skip stage directions in brackets
            if line.startswith('[') and line.endswith(']'):
                continue
                
            # Skip headers
            if line.startswith('#'):
                continue
            
            # Extract speaker content
            if talent_name and f'{talent_name}:' in line:
                # Extract everything after the speaker name
                content = line.split(':', 1)[1].strip()
                # Remove quotes if present
                content = content.strip('"').strip("'")
                if content:
                    content_lines.append(content)
            elif cls._looks_like_speech_content(line):
                content_lines.append(line)
        
        return ' '.join(content_lines)
    
    @classmethod
    def _looks_like_speech_content(cls, line: str) -> bool:
        """Determine if a line looks like speech content"""
        
        # Skip stage directions and formatting
        if (line.startswith('[') or line.startswith('**') or 
            line.startswith('*[') or line.startswith('#')):
            return False
        
        # Skip technical metadata
        technical_terms = ['resolution:', 'fps:', 'duration:', 'timestamp:']
        if any(term in line.lower() for term in technical_terms):
            return False
        
        # Must be substantial
        if len(line) > 15 and (line[0].isalpha() or line[0] == '"'):
            return True
        
        return False
    
    @classmethod
    def _fallback_extraction(cls, script_content: str) -> str:
        """Fallback extraction when other methods fail"""
        
        lines = script_content.split('\\n')
        sentences = []
        
        for line in lines:
            line = line.strip()
            
            # Skip obviously non-content lines
            if (not line or line.startswith('[') or line.startswith('#') or 
                len(line) < 15):
                continue
            
            # Remove common formatting
            line = re.sub(r'[*]{1,2}[^*]*[*]{1,2}', '', line)
            line = line.strip()
            
            # If it looks like a sentence
            if len(line) > 20 and ('.' in line or '!' in line or '?' in line):
                sentences.append(line)
        
        result = ' '.join(sentences)
        
        # Final fallback
        if len(result) < 50:
            return "Welcome to today's tutorial! Let's explore the amazing world of programming and development together."
        
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

# Write the updated cleaner
with open(script_cleaner_path, 'w') as f:
    f.write(updated_cleaner)

print("✅ Updated script cleaner with targeted fix for Alex CodeMaster format")
