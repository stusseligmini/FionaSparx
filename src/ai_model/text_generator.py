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
        logger.info("✅ Smart Text Generator initialized with platform optimization")
    
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
                "Living my truth and loving every moment of it ☀️ {hashtags}",
                "Authentic vibes only 🌈 What's bringing you joy today? {hashtags}",
                "Being genuine is my superpower ✨ How do you stay true to yourself? {hashtags}",
                "Natural beauty, inside and out 🌸 Embracing who I truly am {hashtags}"
            ],
            "fanvue_fashion": [
                "Fashion is my way of expressing who I am inside ✨ What's your style saying about you? {hashtags}",
                "Feeling confident in my own skin and style today 💫 {hashtags}",
                "Every outfit tells a story - what's yours? 👗 {hashtags}",
                "Style is about feeling good in what you wear 🌟 {hashtags}",
                "Confidence is the best accessory you can wear 💎 {hashtags}",
                "Comfort meets style in this look 😊 What makes you feel most comfortable? {hashtags}",
                "Personal style evolution in progress ✨ How has your style changed? {hashtags}",
                "Wearing what makes me feel like ME 💫 {hashtags}"
            ],
            "fanvue_fitness": [
                "Strong is the new beautiful 💪 Working on being the best version of myself {hashtags}",
                "Every workout is a step towards my goals 🔥 What motivates you to stay active? {hashtags}",
                "Fitness isn't just about the body, it's about mental strength too 🌟 {hashtags}",
                "Celebrating progress, not perfection 💫 {hashtags}",
                "Empowered women empower women 👑 {hashtags}",
                "Pushing my limits today 💪 What challenge are you conquering? {hashtags}",
                "Strong body, strong mind, strong heart ❤️ {hashtags}",
                "Fitness is my therapy session 🧘‍♀️ How do you take care of your mental health? {hashtags}"
            ],
            
            # LoyalFans-optimized templates (premium, exclusive, sophisticated)
            "loyalfans_artistic": [
                "Art is the highest form of expression ✨ Creating something unique today {hashtags}",
                "Elegance is not about being noticed, it's about being remembered 💫 {hashtags}",
                "Sophistication meets creativity in every frame 🎨 {hashtags}",
                "Premium content for those who appreciate the finer things 💎 {hashtags}",
                "Exclusive moments captured with artistic vision 🌟 {hashtags}",
                "Where artistry meets elegance ✨ Curating beauty in every detail {hashtags}",
                "Creative expression at its finest 🎭 For those who understand true art {hashtags}",
                "Sophisticated aesthetics for discerning eyes 👁️ {hashtags}"
            ],
            "loyalfans_lifestyle": [
                "Luxury is in each detail, elegance is in each moment ✨ {hashtags}",
                "Curating a life of beauty and sophistication 💫 {hashtags}",
                "Premium experiences for those who understand quality 🌟 {hashtags}",
                "Refined taste meets exclusive content 💎 {hashtags}",
                "Sophisticated lifestyle, exclusive access 👑 {hashtags}",
                "Where luxury meets authenticity ✨ Premium moments, exclusively yours {hashtags}",
                "Elevated living for the discerning few 💫 {hashtags}",
                "Quality over quantity, always 🌟 Exclusive content for exclusive people {hashtags}"
            ],
            "loyalfans_fashion": [
                "High fashion meets personal style ✨ Exclusive looks for discerning eyes {hashtags}",
                "Designer dreams and luxury lifestyle 💫 {hashtags}",
                "Premium fashion content for sophisticated tastes 🌟 {hashtags}",
                "Exclusive fashion moments, curated with care 💎 {hashtags}",
                "Luxury style, exclusive access 👑 {hashtags}",
                "Couture consciousness ✨ Where fashion becomes art {hashtags}",
                "Elegance never goes out of style 💫 Premium fashion for premium people {hashtags}",
                "Designer details for those who notice 🔍 {hashtags}"
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
            "fanvue_lifestyle": [
                "#fanvue", "#lifestyle", "#authentic", "#realme", "#dailylife", 
                "#genuine", "#natural", "#candid", "#unfiltered", "#confidence",
                "#selfcare", "#positivity", "#mindfulness", "#wellness", "#gratitude"
            ],
            "fanvue_fashion": [
                "#fanvue", "#fashion", "#style", "#confident", "#beautiful", 
                "#elegant", "#chic", "#trendy", "#ootd", "#styleinspo",
                "#personalstyle", "#fashionista", "#comfortable", "#authentic"
            ],
            "fanvue_fitness": [
                "#fanvue", "#fitness", "#strong", "#healthy", "#empowered", 
                "#confidence", "#wellness", "#selfcare", "#fitnessmotivation",
                "#strongwoman", "#workoutlife", "#healthylifestyle", "#mindandbody"
            ],
            
            # LoyalFans-optimized hashtags  
            "loyalfans_artistic": [
                "#loyalfans", "#artistic", "#creative", "#unique", "#sophisticated", 
                "#elegant", "#exclusive", "#premium", "#artistry", "#aesthetic",
                "#refined", "#curated", "#artistic", "#creative", "#masterpiece"
            ],
            "loyalfans_lifestyle": [
                "#loyalfans", "#lifestyle", "#luxury", "#exclusive", "#premium", 
                "#sophisticated", "#elegant", "#refined", "#highend", "#vip",
                "#luxurylifestyle", "#exclusiveaccess", "#premiumcontent"
            ],
            "loyalfans_fashion": [
                "#loyalfans", "#fashion", "#highfashion", "#luxury", "#exclusive", 
                "#designer", "#premium", "#sophisticated", "#couture", "#chic",
                "#luxuryfashion", "#designerfashion", "#premiumstyle", "#elegance"
            ]
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
            
            logger.info(f"✅ Generated smart caption for {category} on {platform} ({len(caption)} chars)")
            return caption
            
        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            return self._get_fallback_caption(platform)
    
    def generate_platform_caption(self, image_context, platform="fanvue", content_type=None, tone=None, hashtags=None):
        """New method for explicit platform optimization (matches main.py expectations)"""
        return self.generate_smart_caption(image_context, platform, tone or "friendly")
    
    def _detect_category_with_platform(self, context, platform="instagram"):
        """Detect category from context with platform-specific optimization"""
        context_lower = context.lower()
        
        # Platform-specific category detection
        if platform == "fanvue":
            if any(word in context_lower for word in ["workout", "fitness", "gym", "athletic", "strong", "exercise"]):
                return "fanvue_fitness"
            elif any(word in context_lower for word in ["fashion", "elegant", "style", "outfit", "dress", "clothing"]):
                return "fanvue_fashion"
            else:
                return "fanvue_lifestyle"
                
        elif platform == "loyalfans":
            if any(word in context_lower for word in ["artistic", "creative", "art", "unique", "sophisticated", "aesthetic"]):
                return "loyalfans_artistic"
            elif any(word in context_lower for word in ["fashion", "elegant", "style", "luxury", "designer", "couture"]):
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
            category_hashtags = self.hashtag_groups[category]
            hashtags.extend(category_hashtags[:12])  # Take more category-specific hashtags
        
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
            hashtags.extend(["#contentcreator", "#realvibes", "#authenticity"])
        elif platform == "loyalfans":
            # Additional LoyalFans-specific hashtags  
            hashtags.extend(["#exclusivecontent", "#vip", "#premiumexperience"])
        
        # Add time-based hashtags for engagement (only for general platforms)
        if not category.startswith(('fanvue_', 'loyalfans_')):
            today = datetime.now()
            day_hashtags = [
                f"#{today.strftime('%A').lower()}",
                f"#{today.strftime('%B').lower()}"
            ]
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
        """Optimize caption for specific platform"""
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
            
        elif platform == "fanvue":
            # Ensure caption is engaging and authentic
            if "?" not in caption:
                # Add engagement question if none exists
                engagement_questions = [
                    " What's inspiring you today?",
                    " How are you taking care of yourself?",
                    " What makes you feel confident?",
                    " What's bringing you joy lately?"
                ]
                caption += random.choice(engagement_questions)
                
        elif platform == "loyalfans":
            # Ensure sophisticated tone
            caption = caption.replace("awesome", "exceptional")
            caption = caption.replace("cool", "elegant")
            caption = caption.replace("nice", "sophisticated")
            
        return caption
    
    def _get_fallback_caption(self, platform="instagram"):
        """Fallback caption if something goes wrong"""
        if platform == "fanvue":
            fallbacks = [
                "Living my authentic truth ✨ What makes you feel most like yourself? #fanvue #authentic #lifestyle #realme",
                "Real moments, real connections 💫 How do you stay genuine in today's world? #fanvue #genuine #authentic #dailylife",
                "Being confident in who I am ❤️ What gives you confidence? #fanvue #confidence #authentic #selfcare"
            ]
        elif platform == "loyalfans":
            fallbacks = [
                "Curating moments of elegance ✨ For those who appreciate the finer things #loyalfans #exclusive #sophisticated #premium",
                "Luxury is in the details 💎 Premium content for discerning tastes #loyalfans #luxury #exclusive #refined",
                "Sophisticated artistry meets exclusive access ✨ #loyalfans #artistic #premium #exclusive"
            ]
        else:
            fallbacks = [
                "New day, new possibilities ✨ #motivation #lifestyle #ai",
                "Authentic content with AI support 💫 #authentic #ai #content",
                "Creativity meets technology 🚀 #creativity #ai #innovation"
            ]
        
        return random.choice(fallbacks)
    
    def generate_story_text(self, context="daily"):
        """Generate text for stories"""
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
            ],
            "fanvue": [
                "Real moments ✨",
                "Authentic vibes 💫",
                "Being genuine 🌟"
            ],
            "loyalfans": [
                "Exclusive peek ✨",
                "Premium moments 💎",
                "Sophisticated vibes 🌟"
            ]
        }
        
        templates = story_templates.get(context, story_templates["daily"])
        return random.choice(templates)
    
    def assess_caption_quality(self, caption, platform):
        """Assess the quality of generated caption"""
        score = 0
        feedback = []
        
        # Length check
        if platform == "fanvue" and len(caption) > 2200:
            feedback.append("Caption too long for Fanvue")
        elif platform == "loyalfans" and len(caption) > 2000:
            feedback.append("Caption too long for LoyalFans")
        else:
            score += 20
        
        # Hashtag count
        hashtag_count = len(re.findall(r'#\w+', caption))
        if platform == "fanvue" and hashtag_count <= 20:
            score += 15
        elif platform == "loyalfans" and hashtag_count <= 15:
            score += 15
        
        # Engagement elements
        if "?" in caption:
            score += 15
        
        # Platform-specific checks
        if platform == "fanvue" and any(word in caption.lower() for word in ["authentic", "real", "genuine"]):
            score += 20
        elif platform == "loyalfans" and any(word in caption.lower() for word in ["exclusive", "premium", "sophisticated"]):
            score += 20
        
        # Emoji usage
        emoji_count = len(re.findall(r'[^\w\s,.]', caption))
        if 2 <= emoji_count <= 8:
            score += 15
        
        return {
            "score": min(100, score),
            "feedback": feedback,
            "hashtag_count": hashtag_count,
            "length": len(caption)
        }
