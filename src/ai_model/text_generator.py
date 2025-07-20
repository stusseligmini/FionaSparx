"""
Smart Text Generator - Enhanced for Fanvue and LoyalFans optimization

This module provides intelligent text generation with platform-specific optimizations.
It includes specialized templates, hashtags, and tone adjustments for different platforms,
with particular focus on Fanvue and LoyalFans content creation.

Key Features:
- Platform-specific caption templates
- Dynamic hashtag generation
- Context-aware category detection  
- Tone and style adaptation
- Fallback mechanisms for error handling

Author: FionaSparx AI Content Creator
Version: 2.0.0 - Platform Optimized
"""

import random
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SmartTextGenerator:
    """Intelligent tekstgenerator med kontekstforståelse"""
    
    def __init__(self, config):
        self.config = config
        self.setup_templates()
    
    def setup_templates(self):
        """Sett opp avanserte maler"""
        # Enhanced caption templates optimized for different platforms
        self.caption_templates = {
            "motivational": [
                "Every day is a new opportunity to create something beautiful ✨ {hashtags}",
                "Dreams become reality when you believe in yourself 💫 {hashtags}",
                "First they said it was impossible, then I did it anyway 🚀 {hashtags}",
                "Strength comes not from what you can do, but from overcoming what you thought you couldn't 💪 {hashtags}"
            ],
            "lifestyle": [
                "Life is too short not to live it to the fullest 🌟 {hashtags}",
                "Small moments, big memories 📸 {hashtags}",
                "Authenticity is the new trend 💯 {hashtags}",
                "Good vibes and positive energy all day ☀️ {hashtags}"
            ],
            "fashion": [
                "Style is not what you wear, but how you wear it 👗 {hashtags}",
                "Fashion fades, style is eternal ✨ {hashtags}",
                "Today's outfit: confidence and a smile 😊 {hashtags}",
                "Clothes are just costumes, personality is what truly shines 💫 {hashtags}"
            ],
            "fitness": [
                "The body achieves what the mind believes 💪 {hashtags}",
                "Progress over perfection, always 🏃‍♀️ {hashtags}",
                "Strongest version of myself, every day 🔥 {hashtags}",
                "The gym is my happy place 😊 {hashtags}"
            ],
            "travel": [
                "New places, new experiences, new me 🌍 {hashtags}",
                "Adventure is waiting everywhere, just open your eyes ✈️ {hashtags}",
                "Travel is not about the destination, but about the journey 🗺️ {hashtags}",
                "Collect moments, not things 📱 {hashtags}"
            ],
            
            # Fanvue-optimized templates (authentic, relatable, lifestyle-focused)
            "fanvue_lifestyle": [
                "Just being my authentic self today 💫 What makes you feel most confident? {hashtags}",
                "Real moments, real me ✨ Life isn't always perfect and that's perfectly okay {hashtags}",
                "Embracing every part of my journey 🌟 The ups, the downs, and everything in between {hashtags}",
                "Confidence isn't about being perfect, it's about being real 💯 {hashtags}",
                "Living my truth and loving every moment of it ☀️ {hashtags}"
            ],
            "fanvue_fashion": [
                "Fashion is my way of expressing who I am inside ✨ What's your style saying about you? {hashtags}",
                "Feeling confident in my own skin and style today 💫 {hashtags}",
                "Every outfit tells a story - what's yours? 👗 {hashtags}",
                "Style is about feeling good in what you wear 🌟 {hashtags}",
                "Confidence is the best accessory you can wear 💎 {hashtags}"
            ],
            "fanvue_fitness": [
                "Strong is the new beautiful 💪 Working on being the best version of myself {hashtags}",
                "Every workout is a step towards my goals 🔥 What motivates you to stay active? {hashtags}",
                "Fitness isn't just about the body, it's about mental strength too 🌟 {hashtags}",
                "Celebrating progress, not perfection 💫 {hashtags}",
                "Empowered women empower women 👑 {hashtags}"
            ],
            
            # LoyalFans-optimized templates (premium, exclusive, sophisticated)
            "loyalfans_artistic": [
                "Art is the highest form of expression ✨ Creating something unique today {hashtags}",
                "Elegance is not about being noticed, it's about being remembered 💫 {hashtags}",
                "Sophistication meets creativity in every frame 🎨 {hashtags}",
                "Premium content for those who appreciate the finer things 💎 {hashtags}",
                "Exclusive moments captured with artistic vision 🌟 {hashtags}"
            ],
            "loyalfans_lifestyle": [
                "Luxury is in each detail, elegance is in each moment ✨ {hashtags}",
                "Curating a life of beauty and sophistication 💫 {hashtags}",
                "Premium experiences for those who understand quality 🌟 {hashtags}",
                "Refined taste meets exclusive content 💎 {hashtags}",
                "Sophisticated lifestyle, exclusive access 👑 {hashtags}"
            ],
            "loyalfans_fashion": [
                "High fashion meets personal style ✨ Exclusive looks for discerning eyes {hashtags}",
                "Designer dreams and luxury lifestyle 💫 {hashtags}",
                "Premium fashion content for sophisticated tastes 🌟 {hashtags}",
                "Exclusive fashion moments, curated with care 💎 {hashtags}",
                "Luxury style, exclusive access 👑 {hashtags}"
            ]
        }
        
        # Enhanced hashtag groups optimized for Fanvue and LoyalFans
        self.hashtag_groups = {
            "lifestyle": ["#lifestyle", "#authenticity", "#dailylife", "#goodvibes", "#mindfulness"],
            "motivation": ["#motivation", "#inspiration", "#goals", "#mindset", "#growth"],
            "fashion": ["#fashion", "#style", "#ootd", "#fashionista", "#styleinspo"],
            "fitness": ["#fitness", "#workout", "#healthy", "#strongwoman", "#fitlife"],
            "travel": ["#travel", "#adventure", "#explore", "#wanderlust", "#travelgram"],
            "general": ["#ai", "#content", "#creator", "#authentic", "#life", "#inspiration"],
            
            # Fanvue-optimized hashtags
            "fanvue_lifestyle": ["#fanvue", "#lifestyle", "#authentic", "#realme", "#dailylife", "#genuine", "#natural", "#candid"],
            "fanvue_fashion": ["#fanvue", "#fashion", "#style", "#confident", "#beautiful", "#elegant", "#chic", "#trendy"],
            "fanvue_fitness": ["#fanvue", "#fitness", "#strong", "#healthy", "#empowered", "#confidence", "#wellness", "#selfcare"],
            
            # LoyalFans-optimized hashtags  
            "loyalfans_artistic": ["#loyalfans", "#artistic", "#creative", "#unique", "#sophisticated", "#elegant", "#exclusive", "#premium"],
            "loyalfans_lifestyle": ["#loyalfans", "#lifestyle", "#luxury", "#exclusive", "#premium", "#sophisticated", "#elegant", "#refined"],
            "loyalfans_fashion": ["#loyalfans", "#fashion", "#highfashion", "#luxury", "#exclusive", "#designer", "#premium", "#sophisticated"]
        }
    
    def generate_smart_caption(self, image_context, platform="instagram", tone="friendly"):
        """Generate smart caption based on context with platform optimization"""
        try:
            # Determine category based on context and platform
            category = self._detect_category_with_platform(image_context, platform)
            
            # Choose appropriate template
            templates = self.caption_templates.get(category, self.caption_templates["lifestyle"])
            base_caption = random.choice(templates)
            
            # Generate platform-optimized hashtags
            hashtags = self._generate_smart_hashtags(category, platform)
            
            # Replace hashtag placeholder
            caption = base_caption.format(hashtags=hashtags)
            
            # Optimize for platform
            caption = self._optimize_for_platform(caption, platform)
            
            logger.info(f"✅ Generated smart caption for {category} on {platform}")
            return caption
            
        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            return self._get_fallback_caption()
    
    def _detect_category_with_platform(self, context, platform="instagram"):
        """Detect category from context with platform-specific optimization"""
        context_lower = context.lower()
        
        # Platform-specific category detection
        if platform == "fanvue":
            if any(word in context_lower for word in ["workout", "fitness", "gym", "athletic", "strong"]):
                return "fanvue_fitness"
            elif any(word in context_lower for word in ["fashion", "elegant", "style", "outfit", "dress"]):
                return "fanvue_fashion"
            else:
                return "fanvue_lifestyle"
                
        elif platform == "loyalfans":
            if any(word in context_lower for word in ["artistic", "creative", "art", "unique", "sophisticated"]):
                return "loyalfans_artistic"
            elif any(word in context_lower for word in ["fashion", "elegant", "style", "luxury", "designer"]):
                return "loyalfans_fashion"
            else:
                return "loyalfans_lifestyle"
        
        # Default Instagram/general detection
        if any(word in context_lower for word in ["workout", "fitness", "gym", "athletic"]):
            return "fitness"
        elif any(word in context_lower for word in ["travel", "outdoor", "nature", "adventure"]):
            return "travel"
        elif any(word in context_lower for word in ["fashion", "elegant", "style", "outfit"]):
            return "fashion"
        elif any(word in context_lower for word in ["motivation", "confident", "strong", "success"]):
            return "motivational"
        else:
            return "lifestyle"
    
    def _generate_smart_hashtags(self, category, platform, max_hashtags=25):
        """Generate smart hashtags optimized for platform"""
        hashtags = []
        
        # Add category-specific hashtags
        if category in self.hashtag_groups:
            hashtags.extend(self.hashtag_groups[category][:10])
        
        # Add general hashtags if not platform-specific
        if not category.startswith(('fanvue_', 'loyalfans_')):
            hashtags.extend(self.hashtag_groups["general"][:5])
        
        # Add platform-specific hashtags
        if platform == "instagram":
            hashtags.extend(["#instagood", "#photooftheday", "#beautiful"])
        elif platform == "twitter":
            hashtags = hashtags[:5]  # Twitter has fewer hashtags
        elif platform == "fanvue":
            # Additional Fanvue-specific hashtags
            hashtags.extend(["#contentcreator", "#authentic", "#realme"])
        elif platform == "loyalfans":
            # Additional LoyalFans-specific hashtags  
            hashtags.extend(["#exclusive", "#premium", "#vip"])
        
        # Add time-based hashtags for engagement
        today = datetime.now()
        day_hashtags = [
            f"#{today.strftime('%A').lower()}",
            f"#{today.strftime('%B').lower()}"
        ]
        
        # Only add date hashtags for general platforms
        if not category.startswith(('fanvue_', 'loyalfans_')):
            hashtags.extend(day_hashtags)
        
        # Adjust max hashtags based on platform
        if platform == "fanvue":
            max_hashtags = 20
        elif platform == "loyalfans":
            max_hashtags = 15
        elif platform == "twitter":
            max_hashtags = 5
        
        # Remove duplicates and limit count
        hashtags = list(dict.fromkeys(hashtags))  # Remove duplicates while preserving order
        hashtags = hashtags[:max_hashtags]
        
        return " ".join(hashtags)
    
    def _optimize_for_platform(self, caption, platform):
        """Optimaliser for spesifikk plattform"""
        if platform == "twitter":
            # Twitter har tegnbegrensning
            if len(caption) > 280:
                # Kort ned caption
                caption_parts = caption.split(" #")
                shortened = caption_parts[0][:200] + "..."
                hashtags = " #" + " #".join(caption_parts[1:3])  # Kun første 2 hashtags
                caption = shortened + hashtags
                
        elif platform == "linkedin":
            # LinkedIn er mer profesjonell
            caption = re.sub(r'[✨💫🚀💪🌟📸💯☀️👗😊💫🔥🏃‍♀️🌍✈️🗺️📱]', '', caption)
            caption = caption.replace("likevel", "allikevel")
            
        return caption
    
    def _get_fallback_caption(self):
        """Fallback caption if something goes wrong"""
        fallbacks = [
            "New day, new possibilities ✨ #motivation #lifestyle #ai",
            "Authentic content with AI support 💫 #authentic #ai #content",
            "Creativity meets technology 🚀 #creativity #ai #innovation",
            "Living my best life ✨ #authentic #lifestyle #confidence",
            "Embracing every moment 💫 #grateful #positive #life"
        ]
        return random.choice(fallbacks)
    
    def generate_story_text(self, context="daily"):
        """Generer tekst for stories"""
        story_templates = {
            "daily": [
                "Dagens vibe ✨",
                "Bare en vanlig dag 😊",
                "Små øyeblikk som betyr alt 💫"
            ],
            "behind_scenes": [
                "Bak kulissene 🎬",
                "Prosessen ✨",
                "Sånn lager jeg innhold 💻"
            ]
        }
        
        templates = story_templates.get(context, story_templates["daily"])
        return random.choice(templates)
