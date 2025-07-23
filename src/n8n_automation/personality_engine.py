"""
Advanced AI Personality Engine

This module implements an advanced AI personality system that adapts communication
style, emotional intelligence, and cultural adaptation for optimal engagement.

Key Features:
- Adaptive communication style based on time and engagement
- Emotional intelligence for sentiment-based responses
- Cultural adaptation based on follower geography
- Seasonal personality shifts for holidays and events
- Deep learning integration for preference modeling
"""

import logging
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class CommunicationStyle(Enum):
    """Different communication styles for adaptation"""
    PLAYFUL = "playful"
    PROFESSIONAL = "professional"
    INTIMATE = "intimate"
    ENERGETIC = "energetic"
    RELAXED = "relaxed"
    MYSTERIOUS = "mysterious"
    AUTHENTIC = "authentic"

class EmotionalTone(Enum):
    """Emotional tones for content"""
    CONFIDENT = "confident"
    FLIRTY = "flirty"
    CARING = "caring"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"
    SENSUAL = "sensual"
    EMPOWERING = "empowering"

class CulturalContext(Enum):
    """Cultural contexts for localization"""
    WESTERN = "western"
    EUROPEAN = "european"
    ASIAN = "asian"
    LATIN = "latin"
    INTERNATIONAL = "international"

class TimeContext(Enum):
    """Time-based contexts"""
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    LATE_NIGHT = "late_night"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"

@dataclass
class PersonalityProfile:
    """AI personality configuration"""
    base_style: CommunicationStyle
    emotional_range: List[EmotionalTone]
    cultural_adaptations: Dict[CulturalContext, float]  # Weights for different cultures
    time_adaptations: Dict[TimeContext, CommunicationStyle]
    seasonal_preferences: Dict[str, Dict[str, Any]]  # Month/season specific traits
    platform_variations: Dict[str, Dict[str, Any]]  # Platform-specific adjustments

@dataclass
class EngagementContext:
    """Context for generating personality-driven content"""
    platform: str
    time_of_day: datetime
    follower_sentiment: Optional[str] = None
    cultural_context: Optional[CulturalContext] = None
    engagement_history: Optional[List[float]] = None
    season: Optional[str] = None
    special_event: Optional[str] = None

@dataclass
class PersonalityResponse:
    """Generated personality-driven response"""
    content: str
    style: CommunicationStyle
    emotional_tone: EmotionalTone
    reasoning: List[str]
    confidence: float
    adaptations_made: List[str]

class AdvancedPersonalityEngine:
    """
    Advanced AI Personality Engine
    
    Creates adaptive, emotionally intelligent content that responds to
    context, audience sentiment, and environmental factors.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.personality_profiles: Dict[str, PersonalityProfile] = {}
        self.engagement_history: List[Dict] = []
        self.sentiment_patterns: Dict[str, List[float]] = {}
        self.cultural_preferences: Dict[CulturalContext, Dict] = {}
        
        logger.info("🧠 Advanced Personality Engine initialized")
        self._setup_default_profiles()
        self._initialize_cultural_contexts()
        self._load_seasonal_patterns()
    
    def _setup_default_profiles(self):
        """Setup default personality profiles for different platforms"""
        
        # Fanvue Profile - Authentic and relatable
        fanvue_profile = PersonalityProfile(
            base_style=CommunicationStyle.AUTHENTIC,
            emotional_range=[
                EmotionalTone.CONFIDENT,
                EmotionalTone.CARING,
                EmotionalTone.THOUGHTFUL,
                EmotionalTone.EMPOWERING
            ],
            cultural_adaptations={
                CulturalContext.WESTERN: 0.8,
                CulturalContext.EUROPEAN: 0.7,
                CulturalContext.INTERNATIONAL: 0.9
            },
            time_adaptations={
                TimeContext.MORNING: CommunicationStyle.ENERGETIC,
                TimeContext.MIDDAY: CommunicationStyle.PROFESSIONAL,
                TimeContext.AFTERNOON: CommunicationStyle.RELAXED,
                TimeContext.EVENING: CommunicationStyle.INTIMATE,
                TimeContext.LATE_NIGHT: CommunicationStyle.MYSTERIOUS,
                TimeContext.WEEKEND: CommunicationStyle.PLAYFUL
            },
            seasonal_preferences={
                "spring": {"energy_level": 0.8, "optimism": 0.9},
                "summer": {"energy_level": 0.9, "playfulness": 0.8},
                "autumn": {"thoughtfulness": 0.8, "warmth": 0.9},
                "winter": {"intimacy": 0.9, "comfort": 0.8}
            },
            platform_variations={
                "fanvue": {"authenticity": 0.9, "relatability": 0.8}
            }
        )
        
        # LoyalFans Profile - Sophisticated and exclusive
        loyalfans_profile = PersonalityProfile(
            base_style=CommunicationStyle.PROFESSIONAL,
            emotional_range=[
                EmotionalTone.CONFIDENT,
                EmotionalTone.SENSUAL,
                EmotionalTone.THOUGHTFUL,
                EmotionalTone.EMPOWERING
            ],
            cultural_adaptations={
                CulturalContext.WESTERN: 0.7,
                CulturalContext.EUROPEAN: 0.9,
                CulturalContext.INTERNATIONAL: 0.8
            },
            time_adaptations={
                TimeContext.MORNING: CommunicationStyle.PROFESSIONAL,
                TimeContext.MIDDAY: CommunicationStyle.PROFESSIONAL,
                TimeContext.AFTERNOON: CommunicationStyle.PROFESSIONAL,
                TimeContext.EVENING: CommunicationStyle.INTIMATE,
                TimeContext.LATE_NIGHT: CommunicationStyle.MYSTERIOUS,
                TimeContext.WEEKEND: CommunicationStyle.PLAYFUL
            },
            seasonal_preferences={
                "spring": {"sophistication": 0.8, "elegance": 0.9},
                "summer": {"confidence": 0.9, "allure": 0.8},
                "autumn": {"mystery": 0.8, "depth": 0.9},
                "winter": {"luxury": 0.9, "intimacy": 0.8}
            },
            platform_variations={
                "loyalfans": {"exclusivity": 0.9, "sophistication": 0.8}
            }
        )
        
        self.personality_profiles = {
            "fanvue": fanvue_profile,
            "loyalfans": loyalfans_profile,
            "default": fanvue_profile  # Use Fanvue as default
        }
        
        logger.info(f"✅ Initialized {len(self.personality_profiles)} personality profiles")
    
    def _initialize_cultural_contexts(self):
        """Initialize cultural adaptation patterns"""
        self.cultural_preferences = {
            CulturalContext.WESTERN: {
                "directness": 0.8,
                "casualness": 0.7,
                "humor": 0.8,
                "individuality": 0.9,
                "time_sensitivity": 0.8
            },
            CulturalContext.EUROPEAN: {
                "sophistication": 0.9,
                "subtlety": 0.8,
                "culture_appreciation": 0.9,
                "elegance": 0.8,
                "intellectual_depth": 0.7
            },
            CulturalContext.ASIAN: {
                "respect": 0.9,
                "harmony": 0.8,
                "subtlety": 0.9,
                "tradition_awareness": 0.7,
                "community_focus": 0.8
            },
            CulturalContext.LATIN: {
                "warmth": 0.9,
                "expressiveness": 0.8,
                "family_focus": 0.8,
                "celebration": 0.9,
                "passion": 0.8
            },
            CulturalContext.INTERNATIONAL: {
                "inclusivity": 0.9,
                "clarity": 0.8,
                "universal_themes": 0.9,
                "adaptability": 0.8,
                "openness": 0.9
            }
        }
        
        logger.info("✅ Cultural contexts initialized")
    
    def _load_seasonal_patterns(self):
        """Load seasonal personality adjustment patterns"""
        # This would typically load from a database or config file
        # For now, we'll use built-in patterns
        
        current_month = datetime.now().month
        
        # Define seasonal adjustments
        seasonal_adjustments = {
            "holiday_seasons": {
                12: {"festive": 0.9, "warmth": 0.8, "gratitude": 0.9},  # December
                1: {"fresh_start": 0.9, "motivation": 0.8, "optimism": 0.8},  # January
                2: {"love": 0.9, "romance": 0.8, "intimacy": 0.7},  # February
                3: {"renewal": 0.8, "energy": 0.8, "growth": 0.7},  # March
                5: {"appreciation": 0.8, "gratitude": 0.9, "care": 0.8},  # May (Mother's Day)
                10: {"mystery": 0.9, "playfulness": 0.8, "transformation": 0.7},  # October
                11: {"gratitude": 0.9, "warmth": 0.8, "reflection": 0.7}  # November
            }
        }
        
        self.current_seasonal_context = seasonal_adjustments["holiday_seasons"].get(
            current_month, {"balance": 0.8}
        )
        
        logger.info(f"✅ Seasonal patterns loaded for month {current_month}")
    
    def generate_personality_content(self, base_content: str, context: EngagementContext) -> PersonalityResponse:
        """Generate personality-adapted content based on context"""
        logger.info(f"🧠 Generating personality content for {context.platform}")
        
        # Get appropriate personality profile
        profile = self.personality_profiles.get(context.platform, self.personality_profiles["default"])
        
        # Determine current style based on context
        current_style = self._determine_communication_style(profile, context)
        
        # Determine emotional tone
        emotional_tone = self._determine_emotional_tone(profile, context)
        
        # Apply cultural adaptations
        cultural_adaptations = self._apply_cultural_adaptations(context.cultural_context)
        
        # Apply time-based adaptations
        time_adaptations = self._apply_time_adaptations(context.time_of_day)
        
        # Apply seasonal adjustments
        seasonal_adjustments = self._apply_seasonal_adjustments()
        
        # Generate adapted content
        adapted_content = self._adapt_content(
            base_content, current_style, emotional_tone, 
            cultural_adaptations, time_adaptations, seasonal_adjustments
        )
        
        # Calculate confidence
        confidence = self._calculate_adaptation_confidence(context)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            current_style, emotional_tone, context, cultural_adaptations
        )
        
        # Track adaptations made
        adaptations_made = self._track_adaptations(
            cultural_adaptations, time_adaptations, seasonal_adjustments
        )
        
        response = PersonalityResponse(
            content=adapted_content,
            style=current_style,
            emotional_tone=emotional_tone,
            reasoning=reasoning,
            confidence=confidence,
            adaptations_made=adaptations_made
        )
        
        # Learn from this generation
        self._learn_from_generation(context, response)
        
        logger.info(f"✅ Personality content generated: {current_style.value}/{emotional_tone.value}")
        
        return response
    
    def _determine_communication_style(self, profile: PersonalityProfile, context: EngagementContext) -> CommunicationStyle:
        """Determine appropriate communication style based on context"""
        
        # Start with base style
        style = profile.base_style
        
        # Adjust for time of day
        time_context = self._get_time_context(context.time_of_day)
        if time_context in profile.time_adaptations:
            style = profile.time_adaptations[time_context]
        
        # Adjust for engagement history
        if context.engagement_history:
            avg_engagement = statistics.mean(context.engagement_history)
            if avg_engagement > 0.15:  # High engagement
                # Keep current style
                pass
            elif avg_engagement < 0.05:  # Low engagement
                # Try a different approach
                if style == CommunicationStyle.PROFESSIONAL:
                    style = CommunicationStyle.PLAYFUL
                elif style == CommunicationStyle.RELAXED:
                    style = CommunicationStyle.ENERGETIC
        
        # Adjust for follower sentiment
        if context.follower_sentiment:
            if context.follower_sentiment == "positive":
                if style == CommunicationStyle.RELAXED:
                    style = CommunicationStyle.ENERGETIC
            elif context.follower_sentiment == "negative":
                style = CommunicationStyle.CARING
        
        return style
    
    def _determine_emotional_tone(self, profile: PersonalityProfile, context: EngagementContext) -> EmotionalTone:
        """Determine appropriate emotional tone"""
        
        # Filter available tones by profile
        available_tones = profile.emotional_range
        
        # Adjust for time of day
        time_context = self._get_time_context(context.time_of_day)
        
        if time_context == TimeContext.MORNING:
            # Prefer energetic tones
            preferred = [EmotionalTone.CONFIDENT, EmotionalTone.EXCITED, EmotionalTone.EMPOWERING]
        elif time_context == TimeContext.EVENING:
            # Prefer intimate tones
            preferred = [EmotionalTone.SENSUAL, EmotionalTone.CARING, EmotionalTone.THOUGHTFUL]
        elif time_context == TimeContext.LATE_NIGHT:
            # Prefer mysterious tones
            preferred = [EmotionalTone.SENSUAL, EmotionalTone.FLIRTY, EmotionalTone.THOUGHTFUL]
        else:
            # Use all available tones
            preferred = available_tones
        
        # Find intersection of available and preferred
        suitable_tones = [tone for tone in preferred if tone in available_tones]
        
        if not suitable_tones:
            suitable_tones = available_tones
        
        # Adjust for platform
        if context.platform == "loyalfans":
            # Prefer sophisticated tones
            sophisticated_tones = [EmotionalTone.CONFIDENT, EmotionalTone.SENSUAL, EmotionalTone.EMPOWERING]
            suitable_tones = [tone for tone in sophisticated_tones if tone in suitable_tones] or suitable_tones
        
        # Random selection with slight bias toward confidence
        if EmotionalTone.CONFIDENT in suitable_tones and random.random() < 0.3:
            return EmotionalTone.CONFIDENT
        else:
            return random.choice(suitable_tones)
    
    def _get_time_context(self, time_of_day: datetime) -> TimeContext:
        """Determine time context from datetime"""
        hour = time_of_day.hour
        day_of_week = time_of_day.weekday()
        
        # Weekend check
        if day_of_week >= 5:  # Saturday or Sunday
            return TimeContext.WEEKEND
        
        # Time of day
        if 5 <= hour < 10:
            return TimeContext.MORNING
        elif 10 <= hour < 14:
            return TimeContext.MIDDAY
        elif 14 <= hour < 18:
            return TimeContext.AFTERNOON
        elif 18 <= hour < 23:
            return TimeContext.EVENING
        else:
            return TimeContext.LATE_NIGHT
    
    def _apply_cultural_adaptations(self, cultural_context: Optional[CulturalContext]) -> Dict[str, float]:
        """Apply cultural adaptations to content"""
        if not cultural_context or cultural_context not in self.cultural_preferences:
            return {}
        
        return self.cultural_preferences[cultural_context]
    
    def _apply_time_adaptations(self, time_of_day: datetime) -> Dict[str, float]:
        """Apply time-based adaptations"""
        hour = time_of_day.hour
        
        adaptations = {}
        
        if 6 <= hour < 10:  # Morning
            adaptations.update({"energy": 0.8, "positivity": 0.9, "motivation": 0.8})
        elif 10 <= hour < 14:  # Midday
            adaptations.update({"professionalism": 0.8, "clarity": 0.9})
        elif 14 <= hour < 18:  # Afternoon
            adaptations.update({"relaxation": 0.7, "approachability": 0.8})
        elif 18 <= hour < 22:  # Evening
            adaptations.update({"intimacy": 0.8, "depth": 0.7, "warmth": 0.8})
        else:  # Late night
            adaptations.update({"mystery": 0.8, "allure": 0.7, "exclusivity": 0.8})
        
        return adaptations
    
    def _apply_seasonal_adjustments(self) -> Dict[str, float]:
        """Apply seasonal personality adjustments"""
        return self.current_seasonal_context
    
    def _adapt_content(self, base_content: str, style: CommunicationStyle, 
                      tone: EmotionalTone, cultural_adaptations: Dict, 
                      time_adaptations: Dict, seasonal_adjustments: Dict) -> str:
        """Adapt content based on personality parameters"""
        
        # Start with base content
        adapted_content = base_content
        
        # Apply style modifications
        style_modifiers = self._get_style_modifiers(style)
        
        # Apply tone modifications  
        tone_modifiers = self._get_tone_modifiers(tone)
        
        # Combine all modifiers
        all_modifiers = {**style_modifiers, **tone_modifiers}
        
        # Apply cultural modifiers
        if cultural_adaptations.get("directness", 0) > 0.8:
            # More direct communication
            adapted_content = self._make_more_direct(adapted_content)
        
        if cultural_adaptations.get("sophistication", 0) > 0.8:
            # More sophisticated language
            adapted_content = self._make_more_sophisticated(adapted_content)
        
        # Apply time modifiers
        if time_adaptations.get("energy", 0) > 0.7:
            # Add energetic language
            adapted_content = self._add_energy(adapted_content)
        
        if time_adaptations.get("intimacy", 0) > 0.7:
            # Add intimate elements
            adapted_content = self._add_intimacy(adapted_content)
        
        # Apply seasonal modifiers
        if seasonal_adjustments.get("festive", 0) > 0.8:
            # Add festive elements
            adapted_content = self._add_festive_elements(adapted_content)
        
        if seasonal_adjustments.get("warmth", 0) > 0.8:
            # Add warmth
            adapted_content = self._add_warmth(adapted_content)
        
        return adapted_content
    
    def _get_style_modifiers(self, style: CommunicationStyle) -> Dict[str, float]:
        """Get modifiers for communication style"""
        style_modifiers = {
            CommunicationStyle.PLAYFUL: {"humor": 0.8, "casualness": 0.9, "emoji_usage": 0.8},
            CommunicationStyle.PROFESSIONAL: {"formality": 0.8, "clarity": 0.9, "directness": 0.7},
            CommunicationStyle.INTIMATE: {"personal_touch": 0.9, "warmth": 0.8, "exclusivity": 0.8},
            CommunicationStyle.ENERGETIC: {"enthusiasm": 0.9, "action_words": 0.8, "exclamation": 0.7},
            CommunicationStyle.RELAXED: {"casualness": 0.8, "approachability": 0.9, "ease": 0.8},
            CommunicationStyle.MYSTERIOUS: {"intrigue": 0.9, "subtlety": 0.8, "allure": 0.8},
            CommunicationStyle.AUTHENTIC: {"genuineness": 0.9, "relatability": 0.8, "honesty": 0.9}
        }
        
        return style_modifiers.get(style, {})
    
    def _get_tone_modifiers(self, tone: EmotionalTone) -> Dict[str, float]:
        """Get modifiers for emotional tone"""
        tone_modifiers = {
            EmotionalTone.CONFIDENT: {"assertiveness": 0.8, "strength": 0.9, "leadership": 0.7},
            EmotionalTone.FLIRTY: {"playfulness": 0.8, "charm": 0.9, "tease": 0.7},
            EmotionalTone.CARING: {"empathy": 0.9, "support": 0.8, "nurturing": 0.8},
            EmotionalTone.EXCITED: {"enthusiasm": 0.9, "energy": 0.8, "anticipation": 0.8},
            EmotionalTone.THOUGHTFUL: {"depth": 0.8, "reflection": 0.9, "wisdom": 0.7},
            EmotionalTone.SENSUAL: {"allure": 0.8, "sophistication": 0.7, "magnetism": 0.8},
            EmotionalTone.EMPOWERING: {"inspiration": 0.9, "strength": 0.8, "motivation": 0.8}
        }
        
        return tone_modifiers.get(tone, {})
    
    def _make_more_direct(self, content: str) -> str:
        """Make content more direct"""
        # Remove hedging words and make statements stronger
        hedging_words = ["maybe", "perhaps", "might", "could", "possibly"]
        for word in hedging_words:
            content = content.replace(f" {word} ", " ")
        
        # Replace weak phrases with stronger ones
        replacements = {
            "I think": "I know",
            "I feel like": "I believe",
            "maybe you could": "you should",
            "if you want": "when you're ready"
        }
        
        for weak, strong in replacements.items():
            content = content.replace(weak, strong)
        
        return content
    
    def _make_more_sophisticated(self, content: str) -> str:
        """Make content more sophisticated"""
        # Replace simple words with more sophisticated alternatives
        replacements = {
            " nice ": " elegant ",
            " cool ": " sophisticated ",
            " awesome ": " magnificent ",
            " great ": " exceptional ",
            " fun ": " delightful "
        }
        
        for simple, sophisticated in replacements.items():
            content = content.replace(simple, sophisticated)
        
        return content
    
    def _add_energy(self, content: str) -> str:
        """Add energetic elements to content"""
        # Add action words and energetic phrases
        if "!" not in content:
            content = content.rstrip(".") + "!"
        
        # Add energetic words
        energetic_additions = [
            "Let's go!", "Ready to shine!", "Feeling amazing!",
            "Energy is high!", "Bringing the vibes!"
        ]
        
        if random.random() < 0.3:  # 30% chance to add energetic phrase
            addition = random.choice(energetic_additions)
            content = f"{addition} {content}"
        
        return content
    
    def _add_intimacy(self, content: str) -> str:
        """Add intimate elements to content"""
        # Add personal touches
        intimate_starters = [
            "Just between us,", "Sharing something special with you...",
            "For my closest followers,", "This one's just for you..."
        ]
        
        if random.random() < 0.4:  # 40% chance to add intimate starter
            starter = random.choice(intimate_starters)
            content = f"{starter} {content}"
        
        return content
    
    def _add_festive_elements(self, content: str) -> str:
        """Add festive seasonal elements"""
        current_month = datetime.now().month
        
        if current_month == 12:  # December
            festive_elements = ["✨", "🎄", "❄️", "🎁"]
        elif current_month == 2:  # February
            festive_elements = ["💖", "❤️", "💕", "🌹"]
        elif current_month == 10:  # October
            festive_elements = ["🎃", "🍂", "👻", "🦇"]
        else:
            festive_elements = ["✨", "🌟", "💫", "🌈"]
        
        if random.random() < 0.5:  # 50% chance to add festive element
            element = random.choice(festive_elements)
            content = f"{content} {element}"
        
        return content
    
    def _add_warmth(self, content: str) -> str:
        """Add warmth to content"""
        warm_additions = [
            "Sending love!", "Warm hugs!", "With love,",
            "Thinking of you!", "Grateful for you!"
        ]
        
        if random.random() < 0.3:  # 30% chance to add warm element
            addition = random.choice(warm_additions)
            content = f"{content} {addition}"
        
        return content
    
    def _calculate_adaptation_confidence(self, context: EngagementContext) -> float:
        """Calculate confidence in personality adaptation"""
        confidence = 0.7  # Base confidence
        
        # Adjust based on available context
        if context.cultural_context:
            confidence += 0.1
        
        if context.engagement_history and len(context.engagement_history) > 5:
            confidence += 0.1
        
        if context.follower_sentiment:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, style: CommunicationStyle, tone: EmotionalTone, 
                          context: EngagementContext, cultural_adaptations: Dict) -> List[str]:
        """Generate reasoning for personality choices"""
        reasoning = []
        
        # Style reasoning
        time_context = self._get_time_context(context.time_of_day)
        reasoning.append(f"Using {style.value} style based on {time_context.value} timing")
        
        # Tone reasoning
        reasoning.append(f"Applied {tone.value} tone for optimal {context.platform} engagement")
        
        # Cultural reasoning
        if cultural_adaptations:
            top_adaptation = max(cultural_adaptations.items(), key=lambda x: x[1])
            reasoning.append(f"Emphasized {top_adaptation[0]} for cultural relevance")
        
        # Engagement reasoning
        if context.engagement_history:
            avg_engagement = statistics.mean(context.engagement_history)
            if avg_engagement > 0.15:
                reasoning.append("Maintaining successful engagement patterns")
            else:
                reasoning.append("Adapting approach to improve engagement")
        
        return reasoning
    
    def _track_adaptations(self, cultural_adaptations: Dict, time_adaptations: Dict, 
                          seasonal_adjustments: Dict) -> List[str]:
        """Track what adaptations were made"""
        adaptations = []
        
        if cultural_adaptations:
            adaptations.append(f"Cultural adaptation applied")
        
        if time_adaptations:
            top_time_adaptation = max(time_adaptations.items(), key=lambda x: x[1])
            adaptations.append(f"Time-based: {top_time_adaptation[0]}")
        
        if seasonal_adjustments:
            top_seasonal = max(seasonal_adjustments.items(), key=lambda x: x[1])
            adaptations.append(f"Seasonal: {top_seasonal[0]}")
        
        return adaptations
    
    def _learn_from_generation(self, context: EngagementContext, response: PersonalityResponse):
        """Learn from personality generation for future improvements"""
        learning_data = {
            "timestamp": context.time_of_day.isoformat(),
            "platform": context.platform,
            "style": response.style.value,
            "tone": response.emotional_tone.value,
            "confidence": response.confidence,
            "cultural_context": context.cultural_context.value if context.cultural_context else None,
            "adaptations": response.adaptations_made
        }
        
        self.engagement_history.append(learning_data)
        
        # Keep only recent history (last 1000 generations)
        if len(self.engagement_history) > 1000:
            self.engagement_history = self.engagement_history[-1000:]
    
    def analyze_personality_performance(self, days: int = 30) -> Dict[str, Any]:
        """Analyze personality adaptation performance"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_data = [
            item for item in self.engagement_history
            if datetime.fromisoformat(item["timestamp"]) >= cutoff_date
        ]
        
        if not recent_data:
            return {"error": "No recent personality data available"}
        
        # Analyze style distribution
        style_distribution = {}
        for item in recent_data:
            style = item["style"]
            style_distribution[style] = style_distribution.get(style, 0) + 1
        
        # Analyze tone distribution
        tone_distribution = {}
        for item in recent_data:
            tone = item["tone"]
            tone_distribution[tone] = tone_distribution.get(tone, 0) + 1
        
        # Analyze confidence trends
        confidence_scores = [item["confidence"] for item in recent_data]
        avg_confidence = statistics.mean(confidence_scores)
        
        # Analyze adaptation frequency
        adaptation_counts = {}
        for item in recent_data:
            for adaptation in item.get("adaptations", []):
                adaptation_counts[adaptation] = adaptation_counts.get(adaptation, 0) + 1
        
        return {
            "analysis_period": f"{days} days",
            "total_generations": len(recent_data),
            "average_confidence": round(avg_confidence, 3),
            "style_distribution": style_distribution,
            "tone_distribution": tone_distribution,
            "top_adaptations": sorted(adaptation_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "recommendations": self._generate_performance_recommendations(recent_data)
        }
    
    def _generate_performance_recommendations(self, recent_data: List[Dict]) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Analyze confidence trends
        confidence_scores = [item["confidence"] for item in recent_data]
        avg_confidence = statistics.mean(confidence_scores)
        
        if avg_confidence < 0.7:
            recommendations.append("Consider collecting more audience feedback to improve adaptation confidence")
        
        # Analyze style diversity
        styles = [item["style"] for item in recent_data]
        unique_styles = set(styles)
        
        if len(unique_styles) < 3:
            recommendations.append("Consider expanding communication style variety for better engagement")
        
        # Analyze cultural adaptation usage
        cultural_adaptations = [
            item for item in recent_data 
            if item.get("cultural_context") is not None
        ]
        
        if len(cultural_adaptations) < len(recent_data) * 0.3:
            recommendations.append("Increase cultural adaptation usage for better global engagement")
        
        return recommendations
    
    def export_personality_data(self) -> Dict[str, Any]:
        """Export personality engine data for backup/analysis"""
        return {
            "personality_profiles": {
                name: asdict(profile) for name, profile in self.personality_profiles.items()
            },
            "engagement_history": self.engagement_history[-100:],  # Last 100 entries
            "cultural_preferences": {
                context.value: prefs for context, prefs in self.cultural_preferences.items()
            },
            "current_seasonal_context": self.current_seasonal_context
        }