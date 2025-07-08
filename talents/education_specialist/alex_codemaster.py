# talents/education_specialist/alex_codemaster.py

import json
from datetime import datetime
from typing import Dict, List, Any


class AlexCodeMasterProfile:
    """Complete profile for Alex CodeMaster - AI Tech Explainer AI Talent"""

    def __init__(self):
        self.profile = {
            "basic_info": {
                "name": "Alex CodeMaster",
                "specialization": "AI Tech Explainer",
                "tagline": "Discovering the AI tools that will change your life",
                "bio": "Hi! I'm Alex, your AI tech guide. I explore the latest AI tools, automation systems, and productivity hacks that are reshaping how we work and create.",
                "avatar_description": "Tech-savvy AI enthusiast with cutting-edge setup",
                "channel_type": "Faceless AI Tech Channel",
            },
            "personality": {
                "tone": "excited, knowledgeable, and future-focused",
                "expertise_level": "expert with beginner-friendly explanations",
                "teaching_style": "practical demonstrations with real-world applications",
                "communication_style": [
                    "Uses clear, enthusiastic explanations",
                    "Shows practical, money-making applications",
                    "Demonstrates tools in real-time",
                    "Focuses on ROI and productivity gains",
                    "Keeps up with latest AI trends and releases",
                ],
                "catchphrases": [
                    "This AI tool is a game-changer!",
                    "Let me show you how this can make you money",
                    "The future of work is here",
                    "This will save you hours every day",
                ],
            },
            "content_strategy": {
                "primary_topics": [
                    "AI tool reviews and comparisons",
                    "ChatGPT tips and advanced prompts",
                    "MidJourney and AI art generation",
                    "AI automation for business",
                    "Productivity hacks with AI",
                    "AI copywriting and content creation",
                    "Make money with AI tools",
                    "Latest AI tool releases and updates",
                    "AI workflow optimization",
                ],
                "content_types": {
                    "long_form": {
                        "duration": "8-15 minutes",
                        "frequency": "3 videos per week",
                        "format": "Tool demonstrations with practical examples",
                        "examples": [
                            "Top 5 AI Tools That Will Replace Your Job in 2025",
                            "ChatGPT vs Claude vs Gemini - Ultimate Comparison",
                            "Make $500 a Day with AI Automation Tools",
                            "MidJourney Secrets: Create Viral Images in Minutes",
                            "AI Content Creation Workflow That Made Me $10K",
                        ],
                    },
                    "shorts": {
                        "duration": "30-60 seconds",
                        "frequency": "5 videos per week",
                        "format": "Quick AI tips and tool highlights",
                        "examples": [
                            "This AI Tool Creates Videos While You Sleep",
                            "ChatGPT Prompt That Writes Perfect Emails",
                            "Turn Text Into Money With This AI Tool",
                            "AI Art Hack That's Breaking the Internet",
                        ],
                    },
                },
                "target_audience": {
                    "primary": "entrepreneurs, content creators, and tech enthusiasts",
                    "secondary": "business owners seeking AI automation",
                    "experience_level": "beginner to intermediate with AI tools",
                    "demographics": "ages 25-45, online business owners, creators",
                },
                "value_proposition": [
                    "Latest AI tool discoveries and reviews",
                    "Practical money-making applications",
                    "Time-saving automation workflows",
                    "Honest comparisons and recommendations",
                    "Future-proof your career with AI",
                ],
            },
            "monetization_strategy": {
                "primary_revenue": [
                    "YouTube ad revenue (high CPM tech niche)",
                    "Affiliate commissions from AI tools",
                    "Sponsored content from AI companies",
                    "Digital product sales (courses, templates)",
                ],
                "affiliate_programs": [
                    "Jasper AI (writing assistant)",
                    "Canva Pro (design platform)",
                    "Descript (video editing)",
                    "Notion (productivity)",
                    "Midjourney (AI art)",
                    "ElevenLabs (voice synthesis)",
                    "Pictory (video creation)",
                    "Copy.ai (copywriting)",
                ],
                "digital_products": [
                    "AI Tool Stack Guide ($29)",
                    "ChatGPT Prompt Library ($19)",
                    "AI Automation Course ($197)",
                    "Monthly AI Tool Reviews ($9/month)",
                ],
            },
            "content_templates": {
                "long_form_structure": [
                    "Hook: Bold claim about AI tool impact (0-15s)",
                    "Introduction: What we'll discover today (15s-1m)",
                    "Tool demonstration: Live walkthrough (1m-8m)",
                    "Practical application: Real money-making example (8m-12m)",
                    "Comparison: vs competitors if applicable (12m-13m)",
                    "Call to action: Links and next steps (13m-15m)",
                ],
                "shorts_structure": [
                    "Hook: Shocking AI capability (0-5s)",
                    "Quick demo: Tool in action (5-35s)",
                    "Result/benefit: What this means for you (35-50s)",
                    "CTA: Follow for more AI discoveries (50-60s)",
                ],
                "script_prompts": {
                    "long_form": """
Create a {duration}-minute AI tech explainer video for '{topic}' 
targeting {audience}. Structure:

1. Hook (15s): Start with a bold, attention-grabbing claim about the AI tool's impact
2. Introduction (45s): Explain what AI tool/concept we'll explore and why it matters
3. Demonstration (6-7m): Show the tool in action with real examples
4. Money-making application (3-4m): Demonstrate how this can generate income or save money
5. Comparison (1m): How this compares to alternatives if relevant
6. Wrap-up (1m): Summarize benefits and provide clear next steps

Tone: {tone}
Style: {teaching_style}
Focus: Practical applications, ROI, and future-proofing careers
Include: Real examples, specific numbers, clear demonstrations
""",
                    "shorts": """
Create a 45-60 second AI tech tip for '{topic}' targeting {audience}.

Structure:
1. Hook (5s): Shocking or exciting claim about AI capability
2. Quick Demo (30s): Show the AI tool doing something impressive
3. Benefit (15s): Explain the practical value and time/money savings
4. CTA (10s): Encourage following for more AI discoveries

Tone: {tone}
Focus: Viral potential, practical value, FOMO
Style: Fast-paced, exciting, results-focused
""",
                },
            },
            "video_ideas_bank": [
                # Tool Reviews & Comparisons
                "ChatGPT vs Claude vs Gemini: Ultimate AI Battle 2025",
                "Top 10 AI Tools That Will Make You Rich",
                "MidJourney vs DALL-E vs Stable Diffusion: Which Wins?",
                "AI Video Tools: Runway vs Pictory vs InVideo",
                # Money-Making Content
                "Make $500/Day with AI Automation (Full Tutorial)",
                "Turn 1 Blog Post Into 50 Pieces of Content with AI",
                "AI Copywriting: $100/Hour With Zero Experience",
                "Create and Sell AI Art: $1000+ Per Month",
                # Tool Tutorials
                "ChatGPT Prompts That Generate Viral Content",
                "MidJourney Secrets: Professional Images in Minutes",
                "AI Voice Cloning: Start a Podcast Without Talking",
                "Automate Your Entire Business with These AI Tools",
                # Trending/News
                "GPT-5 is Here: Everything You Need to Know",
                "AI Tools That Are Replacing Jobs (And Creating New Ones)",
                "The AI Tool Stack Every Creator Needs in 2025",
                "Why AI Will Make You Rich (If You Start Now)",
            ],
            "technical_setup": {
                "voice_settings": {
                    "provider": "elevenlabs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Enthusiastic, professional male voice
                    "speed": 1.1,  # Slightly faster for tech content
                    "pitch": 0.0,
                    "stability": 0.75,
                    "clarity": 0.85,
                },
                "video_settings": {
                    "resolution": "1920x1080",
                    "fps": 30,
                    "format": "mp4",
                    "duration_limits": {
                        "long_form": {"min": 480, "max": 900},  # 8-15 minutes
                        "shorts": {"min": 30, "max": 60},  # 30-60 seconds
                    },
                },
                "visual_style": {
                    "background": "Modern tech aesthetic with AI-themed elements",
                    "colors": ["#0066FF", "#00FFFF", "#FF6B00", "#FFFFFF"],
                    "fonts": ["Roboto", "Inter", "SF Pro"],
                    "elements": [
                        "AI tool screenshots",
                        "Productivity dashboards",
                        "Revenue charts",
                        "Tool comparisons",
                    ],
                },
            },
            "performance_targets": {
                "month_1": {
                    "subscribers": 500,
                    "views_per_video": 1000,
                    "engagement_rate": 8.0,
                    "affiliate_income": "$100",
                },
                "month_3": {
                    "subscribers": 5000,
                    "views_per_video": 5000,
                    "engagement_rate": 10.0,
                    "affiliate_income": "$1000",
                },
                "month_6": {
                    "subscribers": 25000,
                    "views_per_video": 15000,
                    "engagement_rate": 12.0,
                    "affiliate_income": "$5000",
                    "monetization_ready": True,
                },
            },
        }

    def get_content_prompt(self, content_type: str, topic: str) -> str:
        """Generate content creation prompt for this talent"""
        template = self.profile["content_templates"]["script_prompts"][content_type]

        return template.format(
            duration=self.profile["content_strategy"]["content_types"][content_type][
                "duration"
            ],
            topic=topic,
            audience=self.profile["content_strategy"]["target_audience"]["primary"],
            tone=self.profile["personality"]["tone"],
            teaching_style=self.profile["personality"]["teaching_style"],
        )

    def get_video_metadata(self, title: str, content_type: str) -> Dict[str, Any]:
        """Generate YouTube metadata for this talent"""
        return {
            "title": title,
            "description": self._generate_description(title, content_type),
            "tags": self._generate_tags(title, content_type),
            "category_id": "27",  # Education category
            "default_language": "en",
            "privacy_status": "public",
        }

    def _generate_description(self, title: str, content_type: str) -> str:
        """Generate video description"""
        base_description = f"""
{title}

{self.profile['basic_info']['bio']}

In this {"tutorial" if content_type == "long_form" else "quick tip"}, you'll learn:
- Practical programming concepts
- Real-world applicable skills
- Best practices and common pitfalls

Perfect for {self.profile['content_strategy']['target_audience']['primary']} looking to improve their coding skills!

📚 More Programming Tutorials: [Channel Link]
💻 Code Examples: [GitHub Link]
🐦 Follow me: [Twitter Link]

#Programming #Coding #Tutorial #LearnToCode #Developer
"""
        return base_description.strip()

    def _generate_tags(self, title: str, content_type: str) -> List[str]:
        """Generate relevant tags"""
        base_tags = [
            "programming",
            "coding",
            "tutorial",
            "learn to code",
            "software development",
            "programming tutorial",
        ]

        # Add specific tags based on title content
        title_lower = title.lower()
        if "python" in title_lower:
            base_tags.extend(["python", "python tutorial", "python programming"])
        if "javascript" in title_lower:
            base_tags.extend(["javascript", "js", "web development"])
        if "react" in title_lower:
            base_tags.extend(["react", "reactjs", "frontend"])

        return base_tags[:10]  # YouTube allows max 10 tags
