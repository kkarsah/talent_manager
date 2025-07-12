"""
Improve script cleaner to better filter out production notes
"""

def update_script_cleaner():
    """Update the script cleaner with better filtering"""
    
    improved_cleaner = '''import re
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ScriptCleaner:
    """Enhanced script cleaner that removes production notes and formatting"""
    
    @classmethod
    def extract_spoken_content(cls, script_content: str, talent_name: Optional[str] = None) -> str:
        """Extract only what should be spoken by the TTS"""
        
        if not script_content or not script_content.strip():
            return ""
        
        # Try different extraction methods based on format
        if script_content.strip().startswith('{'):
            content = cls._extract_from_json(script_content)
        else:
            content = cls._extract_from_markdown(script_content, talent_name)
        
        # Final cleanup
        cleaned = cls._final_cleanup(content)
        
        # Ensure we have substantial content
        if len(cleaned) < 50:
            logger.warning("Cleaned script too short, using fallback")
            cleaned = cls._fallback_extraction(script_content)
        
        logger.info(f"Script cleaned: {len(script_content)} → {len(cleaned)} chars")
        return cleaned
    
    @classmethod
    def _extract_from_markdown(cls, script: str, talent_name: str = None) -> str:
        """Extract spoken content from markdown-formatted scripts"""
        
        lines = script.split('\\n')
        spoken_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Skip production notes and formatting
            if cls._should_skip_line(line):
                continue
            
            # Extract dialogue from speaker format
            if talent_name and f'{talent_name}:' in line:
                dialogue = cls._extract_dialogue(line, talent_name)
                if dialogue:
                    spoken_lines.append(dialogue)
            elif cls._is_narrative_content(line):
                spoken_lines.append(line)
        
        return ' '.join(spoken_lines)
    
    @classmethod
    def _should_skip_line(cls, line: str) -> bool:
        """Determine if a line should be skipped (production notes, etc.)"""
        
        # Skip patterns that are clearly production notes
        skip_patterns = [
            r'^#+',  # Headers (# ## ###)
            r'^\\*\\*\\[',  # [SCENE: description]
            r'^\\[',  # [Visual: description] or [Audio: settings]
            r'^---+',  # Dividers
            r'^```',  # Code blocks
            r'\\*\\*Title:\\*\\*',  # Metadata
            r'\\*\\*Description:\\*\\*',
            r'\\*\\*Tags:\\*\\*',
            r'Video Metadata:',
            r'Technical Production:',
            r'TIMESTAMP:',
            r'SCENE:',
            r'VISUAL:',
            r'AUDIO:',
            r'\\*\\*\\[INTRO\\]\\*\\*',
            r'\\*\\*\\[OUTRO\\]\\*\\*',
            r'\\*\\*\\[MAIN CONTENT\\]\\*\\*',
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns)
    
    @classmethod
    def _extract_dialogue(cls, line: str, talent_name: str) -> str:
        """Extract dialogue from speaker format: 'Alex CodeMaster: "content"'"""
        
        # Pattern: Speaker: "quoted content"
        pattern1 = rf'{re.escape(talent_name)}:\\s*"([^"]*)"'
        match = re.search(pattern1, line)
        if match:
            return match.group(1).strip()
        
        # Pattern: Speaker: content (without quotes)
        pattern2 = rf'{re.escape(talent_name)}:\\s*(.+?)$'
        match = re.search(pattern2, line)
        if match:
            content = match.group(1).strip()
            # Remove quotes if present
            content = content.strip('"').strip("'")
            return content
        
        return ""
    
    @classmethod
    def _is_narrative_content(cls, line: str) -> bool:
        """Check if line looks like narrative content that should be spoken"""
        
        # Skip if it has too much formatting
        if line.count('*') > 3 or line.count('[') > 1:
            return False
        
        # Skip technical terms
        technical_terms = [
            'resolution:', 'fps:', 'duration:', 'metadata', 'json', 'css', 
            'html', 'file_path:', 'url:', 'api_key:', 'timestamp:'
        ]
        
        if any(term in line.lower() for term in technical_terms):
            return False
        
        # Must be substantial and sentence-like
        if len(line) > 15 and (line[0].isalpha() or line[0].isdigit()):
            return True
        
        return False
    
    @classmethod
    def _extract_from_json(cls, json_script: str) -> str:
        """Extract from JSON-formatted scripts"""
        try:
            data = json.loads(json_script)
            
            # Look for spoken content keys
            if isinstance(data, dict):
                for key in ['spoken_content', 'dialogue', 'content', 'script', 'text']:
                    if key in data and data[key]:
                        return str(data[key])
            
            return json_script
                
        except json.JSONDecodeError:
            return cls._extract_from_markdown(json_script)
    
    @classmethod
    def _final_cleanup(cls, content: str) -> str:
        """Final cleanup of extracted content"""
        
        if not content:
            return ""
        
        # Remove remaining markdown formatting
        content = re.sub(r'\\*\\*([^*]*)\\*\\*', r'\\1', content)  # **bold**
        content = re.sub(r'\\*([^*]*)\\*', r'\\1', content)  # *italic*
        content = re.sub(r'`([^`]*)`', r'\\1', content)  # `code`
        content = re.sub(r'\\[([^\\]]*)\\]', '', content)  # [stage directions]
        
        # Remove multiple spaces
        content = re.sub(r'\\s+', ' ', content)
        content = content.strip()
        
        return content
    
    @classmethod
    def _fallback_extraction(cls, script_content: str) -> str:
        """Fallback when primary extraction fails"""
        
        lines = script_content.split('\\n')
        sentences = []
        
        for line in lines:
            line = line.strip()
            
            # Skip obvious non-content
            if (not line or line.startswith('#') or line.startswith('[') or 
                line.startswith('```') or len(line) < 15):
                continue
            
            # Remove formatting
            line = re.sub(r'\\*\\*[^*]*\\*\\*', '', line)
            line = re.sub(r'\\*[^*]*\\*', '', line)
            line = line.strip()
            
            # Keep substantial sentences
            if len(line) > 20 and any(punct in line for punct in '.!?'):
                sentences.append(line)
        
        result = ' '.join(sentences)
        
        # Minimal fallback
        if len(result) < 50:
            return "Welcome to this tutorial. Let's explore the content together."
        
        return result
'''

    # Write the improved cleaner
    with open('core/content/script_cleaner.py', 'w') as f:
        f.write(improved_cleaner)
    
    print("✅ Updated script cleaner to filter production notes")

if __name__ == "__main__":
    update_script_cleaner()
