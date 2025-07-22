#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Text Generator - Platform optimized captions and hashtags
"""

import random
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SmartTextGenerator:
    """
    Smart text generation with platform optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._load_templates()
        logger.info("Smart Text Generator initialized")
    
    def _load_templates(self):
        """Load platform-specific templates"""
        self.templates = {
            "fanvue": {
                "lifestyle": [
                    "Just being my authentic self today ✨ What makes you feel most confident?",
                    "Living my best life 🌟 How are you taking care of yourself today?", 
                    "Authentic vibes only 💫 What's bringing you joy lately?",
                    "Real moments, real me 🤍 What's your favorite way to unwind?",
                    "Embracing every part of who I am ✨ What makes you feel empowered?"
                ],
                "fitness": [
                    "Pushing my limits today 💪 What's your fitness motivation?",
                    "Strong body, strong mind 🏋️‍♀️ How do you stay active?",
                    "Fitness is my therapy 🔥 What's your favorite workout?",
                    "Building strength inside and out 💯 What challenges are you conquering?"
                ],
                "fashion": [
                    "Style is self-expression 👗 What's your signature look?",
                    "Comfort meets confidence ✨ How do you define your style?",
                    "Fashion that tells my story 🎨 What outfit makes you feel amazing?"
                ]
            },
            "loyalfans": {
                "artistic": [
                    "Art is the highest form of expression ✨ What inspires your creativity?",
                    "Creating something unique today 🎨 How do you express your artistry?",
                    "Beauty in every moment 💫 What art form speaks to your soul?",
                    "Capturing elegance through my lens 📸 What defines beauty to you?"
                ],
                "fashion": [
                    "Elegance is the only beauty that never fades ✨ What's your definition of timeless style?",
                    "Style is a way to say who you are 👑 How does fashion express your personality?",
                    "Fashion is art you can wear 🖤 What piece makes you feel most sophisticated?"
                ],
                "premium": [
                    "Luxury is in each detail 💎 What defines premium to you?",
                    "Exclusive moments, curated with care ✨ How do you appreciate the finer things?",
                    "Quality over quantity, always 🌟 What's worth the investment?"
                ]
            }
        }
        
        self.hashtags = {
            "fanvue": {
                "core": ["#fanvue", "#authentic", "#realme", "#genuine", "#lifestyle"],
                "lifestyle": ["#dailylife", "#selfcare", "#confidence", "#natural", "#unfiltered"],
                "fitness": ["#fitnessmotivation", "#strongwoman", "#workoutlife", "#healthylifestyle"],
                "fashion": ["#personalstyle", "#comfortablestyle", "#fashioninspo", "#styleconfidence"]
            },
            "loyalfans": {
                "core": ["#loyalfans", "#exclusive", "#premium", "#sophisticated", "#artistic"],
                "artistic": ["#artistry", "#creative", "#elegant", "#refined", "#aesthetic"],
                "fashion": ["#luxury", "#highfashion", "#couture", "#designer", "#chic"],
                "premium": ["#vip", "#exclusive", "#premium", "#luxury", "#highend"]
            }
        }
    
    def generate_platform_caption(
        self,
        image_context: str,
        platform: str = "fanvue",
        content_type: Optional[str] = None,
        tone: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> str:
        """Generate optimized caption for platform"""
        
        # Detect content type if not provided
        if not content_type:
            content_type = self._detect_content_type(image_context, platform)
        
        # Get template
        platform_templates = self.templates.get(platform, self.templates["fanvue"])
        content_templates = platform_templates.get(content_type, platform_templates.get("lifestyle", []))
        
        if not content_templates:
            content_templates = ["Living my best life ✨"]
        
        caption = random.choice(content_templates)
        
        # Generate hashtags if not provided
        if hashtags is None:
            hashtags = self._generate_hashtags(platform, content_type)
        
        # Combine caption and hashtags
        full_caption = f"{caption}\n\n{' '.join(hashtags[:20])}"
        
        logger.info(f"Generated {platform} caption with {len(hashtags)} hashtags")
        return full_caption
    
    def _detect_content_type(self, image_context: str, platform: str) -> str:
        """Detect content type from context"""
        context_lower = image_context.lower()
        
        if any(word in context_lower for word in ["workout", "gym", "fitness", "athletic"]):
            return "fitness"
        elif any(word in context_lower for word in ["fashion", "outfit", "style", "clothing"]):
            return "fashion"
        elif platform == "loyalfans":
            if any(word in context_lower for word in ["artistic", "creative", "portrait"]):
                return "artistic"
            elif any(word in context_lower for word in ["luxury", "premium", "sophisticated"]):
                return "premium"
        
        return "lifestyle" if platform == "fanvue" else "artistic"
    
    def _generate_hashtags(self, platform: str, content_type: str) -> List[str]:
        """Generate relevant hashtags"""
        platform_hashtags = self.hashtags.get(platform, self.hashtags["fanvue"])
        
        # Start with core hashtags
        selected = platform_hashtags["core"].copy()
        
        # Add content-specific hashtags
        if content_type in platform_hashtags:
            content_hashtags = platform_hashtags[content_type]
            selected.extend(random.sample(content_hashtags, min(5, len(content_hashtags))))
        
        # Add some general hashtags
        general = ["#mood", "#vibes", "#energy", "#positivity", "#confidence", "#inspiration"]
        selected.extend(random.sample(general, 3))
        
        return list(dict.fromkeys(selected))  # Remove duplicates
    
    def generate_smart_caption(
        self,
        image_context: str,
        platform: str = "instagram", 
        tone: str = "friendly",
        include_hashtags: bool = True
    ) -> str:
        """Legacy method for backwards compatibility"""
        
        # Map old platform names
        if platform == "instagram":
            platform = "fanvue"
        
        return self.generate_platform_caption(
            image_context=image_context,
            platform=platform,
            hashtags=None if include_hashtags else []
        )
