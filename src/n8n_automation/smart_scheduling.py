"""
Smart Scheduling Engine with ML-based Timing

This module implements an intelligent scheduling system that learns
optimal posting times based on engagement data and audience behavior.

Key Features:
- ML-based optimal timing prediction
- Audience behavior analysis
- Platform-specific scheduling
- Time zone optimization
- Engagement pattern learning
- A/B testing for schedule optimization
"""

import logging
import json
import random
import statistics
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import math

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported social media platforms"""
    FANVUE = "fanvue"
    LOYALFANS = "loyalfans"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"

class ContentType(Enum):
    """Types of content for scheduling"""
    LIFESTYLE = "lifestyle"
    FASHION = "fashion"
    FITNESS = "fitness"
    ARTISTIC = "artistic"
    PREMIUM = "premium"
    PROMOTIONAL = "promotional"

class ScheduleConfidence(Enum):
    """Confidence levels for schedule predictions"""
    HIGH = "high"      # >80% confidence
    MEDIUM = "medium"  # 60-80% confidence  
    LOW = "low"        # <60% confidence

@dataclass
class EngagementData:
    """Historical engagement data point"""
    timestamp: datetime
    platform: Platform
    content_type: ContentType
    engagement_rate: float
    views: int
    likes: int
    comments: int
    shares: int
    revenue_impact: float = 0.0

@dataclass
class AudienceProfile:
    """Audience demographics and behavior profile"""
    platform: Platform
    primary_timezone: str
    age_groups: Dict[str, float]  # "18-24": 0.3, "25-34": 0.4, etc.
    peak_activity_hours: List[int]  # Hours when audience is most active
    engagement_patterns: Dict[str, float]  # Day of week patterns
    content_preferences: Dict[ContentType, float]

@dataclass
class ScheduleRecommendation:
    """Recommended posting schedule"""
    platform: Platform
    content_type: ContentType
    optimal_time: datetime
    confidence: ScheduleConfidence
    expected_engagement: float
    reasoning: List[str]
    alternatives: List[Tuple[datetime, float]]  # Alternative times with scores

class SmartSchedulingEngine:
    """
    ML-based Smart Scheduling Engine
    
    Learns optimal posting times from historical engagement data
    and provides intelligent scheduling recommendations.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.engagement_history: List[EngagementData] = []
        self.audience_profiles: Dict[Platform, AudienceProfile] = {}
        self.schedule_performance: Dict[str, List[float]] = {}  # Track A/B test results
        
        logger.info("📅 Smart Scheduling Engine initialized")
        self._initialize_default_profiles()
        self._load_historical_data()
    
    def _initialize_default_profiles(self):
        """Initialize default audience profiles for platforms"""
        default_profiles = {
            Platform.FANVUE: AudienceProfile(
                platform=Platform.FANVUE,
                primary_timezone="UTC",
                age_groups={"18-24": 0.25, "25-34": 0.45, "35-44": 0.25, "45+": 0.05},
                peak_activity_hours=[18, 19, 20, 21, 22],  # Evening hours
                engagement_patterns={
                    "monday": 0.8, "tuesday": 0.85, "wednesday": 0.9,
                    "thursday": 0.95, "friday": 1.0, "saturday": 0.9, "sunday": 0.7
                },
                content_preferences={
                    ContentType.LIFESTYLE: 0.9,
                    ContentType.FASHION: 0.8,
                    ContentType.FITNESS: 0.7,
                    ContentType.ARTISTIC: 0.6,
                    ContentType.PREMIUM: 0.85
                }
            ),
            Platform.LOYALFANS: AudienceProfile(
                platform=Platform.LOYALFANS,
                primary_timezone="UTC",
                age_groups={"18-24": 0.15, "25-34": 0.35, "35-44": 0.35, "45+": 0.15},
                peak_activity_hours=[20, 21, 22, 23],  # Late evening
                engagement_patterns={
                    "monday": 0.7, "tuesday": 0.8, "wednesday": 0.85,
                    "thursday": 0.9, "friday": 0.95, "saturday": 1.0, "sunday": 0.75
                },
                content_preferences={
                    ContentType.ARTISTIC: 0.95,
                    ContentType.PREMIUM: 0.9,
                    ContentType.LIFESTYLE: 0.7,
                    ContentType.FASHION: 0.8,
                    ContentType.FITNESS: 0.6
                }
            ),
            Platform.INSTAGRAM: AudienceProfile(
                platform=Platform.INSTAGRAM,
                primary_timezone="UTC",
                age_groups={"18-24": 0.4, "25-34": 0.35, "35-44": 0.2, "45+": 0.05},
                peak_activity_hours=[12, 13, 17, 18, 19, 20],  # Lunch and evening
                engagement_patterns={
                    "monday": 0.8, "tuesday": 0.9, "wednesday": 1.0,
                    "thursday": 0.95, "friday": 0.85, "saturday": 0.7, "sunday": 0.75
                },
                content_preferences={
                    ContentType.LIFESTYLE: 1.0,
                    ContentType.FASHION: 0.95,
                    ContentType.FITNESS: 0.85,
                    ContentType.ARTISTIC: 0.8,
                    ContentType.PREMIUM: 0.6
                }
            )
        }
        
        self.audience_profiles = default_profiles
        logger.info(f"✅ Initialized audience profiles for {len(default_profiles)} platforms")
    
    def _load_historical_data(self):
        """Load historical engagement data for ML training"""
        # In production, this would load from a database
        # For demo, generate some synthetic historical data
        
        current_time = datetime.now()
        platforms = [Platform.FANVUE, Platform.LOYALFANS, Platform.INSTAGRAM]
        content_types = list(ContentType)
        
        # Generate 30 days of synthetic data
        for days_ago in range(30):
            date = current_time - timedelta(days=days_ago)
            
            for platform in platforms:
                profile = self.audience_profiles[platform]
                
                # Generate 1-3 posts per day per platform
                for _ in range(random.randint(1, 3)):
                    # Pick random hour weighted by peak activity
                    hour = random.choices(
                        range(24),
                        weights=[2 if h in profile.peak_activity_hours else 1 for h in range(24)]
                    )[0]
                    
                    post_time = date.replace(hour=hour, minute=random.randint(0, 59))
                    content_type = random.choice(content_types)
                    
                    # Calculate engagement based on time and content type
                    engagement_rate = self._calculate_synthetic_engagement(
                        post_time, platform, content_type, profile
                    )
                    
                    engagement_data = EngagementData(
                        timestamp=post_time,
                        platform=platform,
                        content_type=content_type,
                        engagement_rate=engagement_rate,
                        views=random.randint(500, 5000),
                        likes=int(random.randint(50, 500) * engagement_rate),
                        comments=int(random.randint(5, 50) * engagement_rate),
                        shares=int(random.randint(2, 20) * engagement_rate),
                        revenue_impact=random.uniform(0, 100) * engagement_rate
                    )
                    
                    self.engagement_history.append(engagement_data)
        
        logger.info(f"✅ Loaded {len(self.engagement_history)} historical data points")
    
    def _calculate_synthetic_engagement(self, post_time: datetime, platform: Platform, 
                                      content_type: ContentType, profile: AudienceProfile) -> float:
        """Calculate synthetic engagement rate for demo data"""
        base_rate = 0.1  # 10% base engagement
        
        # Time of day factor
        hour = post_time.hour
        time_factor = 1.5 if hour in profile.peak_activity_hours else 0.8
        
        # Day of week factor
        day_name = post_time.strftime("%A").lower()
        day_factor = profile.engagement_patterns.get(day_name, 1.0)
        
        # Content type factor
        content_factor = profile.content_preferences.get(content_type, 0.8)
        
        # Add some randomness
        random_factor = random.uniform(0.7, 1.3)
        
        engagement_rate = base_rate * time_factor * day_factor * content_factor * random_factor
        return max(0.01, min(1.0, engagement_rate))  # Clamp between 1% and 100%
    
    def add_engagement_data(self, data: EngagementData):
        """Add new engagement data for learning"""
        self.engagement_history.append(data)
        
        # Update audience profile based on new data
        self._update_audience_profile(data)
        
        logger.info(f"📊 Added engagement data: {data.platform.value} - {data.engagement_rate:.2%}")
    
    def _update_audience_profile(self, data: EngagementData):
        """Update audience profile based on new engagement data"""
        platform = data.platform
        if platform not in self.audience_profiles:
            return
        
        profile = self.audience_profiles[platform]
        
        # Update peak activity hours based on high-engagement posts
        if data.engagement_rate > 0.15:  # Above average engagement
            hour = data.timestamp.hour
            if hour not in profile.peak_activity_hours:
                # Add hour if it shows consistently good performance
                recent_hour_data = [
                    d for d in self.engagement_history[-100:]  # Last 100 posts
                    if d.platform == platform and d.timestamp.hour == hour
                ]
                
                if len(recent_hour_data) >= 3:
                    avg_engagement = statistics.mean(d.engagement_rate for d in recent_hour_data)
                    if avg_engagement > 0.12:
                        profile.peak_activity_hours.append(hour)
                        profile.peak_activity_hours.sort()
        
        # Update content preferences
        if data.content_type in profile.content_preferences:
            current_pref = profile.content_preferences[data.content_type]
            # Weighted update: 90% current + 10% new data
            new_pref = 0.9 * current_pref + 0.1 * data.engagement_rate * 10  # Scale engagement to 0-1
            profile.content_preferences[data.content_type] = max(0.1, min(1.0, new_pref))
    
    def get_optimal_schedule(self, platform: Platform, content_type: ContentType, 
                           target_date: Optional[datetime] = None) -> ScheduleRecommendation:
        """Get optimal posting schedule recommendation"""
        if target_date is None:
            target_date = datetime.now() + timedelta(hours=1)  # Next hour by default
        
        logger.info(f"🔍 Analyzing optimal schedule for {platform.value} - {content_type.value}")
        
        # Get platform profile
        profile = self.audience_profiles.get(platform)
        if not profile:
            return self._get_fallback_recommendation(platform, content_type, target_date)
        
        # Analyze historical performance
        relevant_data = self._get_relevant_historical_data(platform, content_type)
        
        if len(relevant_data) < 5:
            return self._get_fallback_recommendation(platform, content_type, target_date)
        
        # Find optimal time windows
        time_scores = self._analyze_time_performance(relevant_data, profile)
        
        # Get best time for target date
        optimal_time, confidence = self._find_optimal_time(target_date, time_scores, profile)
        
        # Calculate expected engagement
        expected_engagement = self._predict_engagement(optimal_time, platform, content_type, profile)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(optimal_time, time_scores, profile, relevant_data)
        
        # Get alternative times
        alternatives = self._get_alternative_times(target_date, time_scores, optimal_time)
        
        recommendation = ScheduleRecommendation(
            platform=platform,
            content_type=content_type,
            optimal_time=optimal_time,
            confidence=confidence,
            expected_engagement=expected_engagement,
            reasoning=reasoning,
            alternatives=alternatives
        )
        
        logger.info(f"✅ Optimal time found: {optimal_time.strftime('%Y-%m-%d %H:%M')} "
                   f"(confidence: {confidence.value}, expected: {expected_engagement:.1%})")
        
        return recommendation
    
    def _get_relevant_historical_data(self, platform: Platform, content_type: ContentType) -> List[EngagementData]:
        """Get relevant historical data for analysis"""
        return [
            data for data in self.engagement_history
            if data.platform == platform and data.content_type == content_type
        ]
    
    def _analyze_time_performance(self, data: List[EngagementData], profile: AudienceProfile) -> Dict[int, float]:
        """Analyze performance by hour of day"""
        hour_performances = {}
        
        for hour in range(24):
            hour_data = [d for d in data if d.timestamp.hour == hour]
            
            if hour_data:
                avg_engagement = statistics.mean(d.engagement_rate for d in hour_data)
                # Weight by number of data points (more data = higher confidence)
                confidence_weight = min(1.0, len(hour_data) / 10.0)
                hour_performances[hour] = avg_engagement * confidence_weight
            else:
                # Use profile-based estimate for hours with no data
                base_score = 0.1  # Base engagement rate
                if hour in profile.peak_activity_hours:
                    base_score *= 1.5
                hour_performances[hour] = base_score * 0.5  # Lower confidence
        
        return hour_performances
    
    def _find_optimal_time(self, target_date: datetime, time_scores: Dict[int, float], 
                          profile: AudienceProfile) -> Tuple[datetime, ScheduleConfidence]:
        """Find the optimal time on the target date"""
        # Get day of week factor
        day_name = target_date.strftime("%A").lower()
        day_factor = profile.engagement_patterns.get(day_name, 1.0)
        
        # Score each hour on the target date
        hour_scores = {}
        for hour, base_score in time_scores.items():
            # Check if hour is in the future
            potential_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            if potential_time > datetime.now():
                adjusted_score = base_score * day_factor
                hour_scores[hour] = adjusted_score
        
        if not hour_scores:
            # If no future hours today, look at next day
            next_day = target_date + timedelta(days=1)
            next_day_name = next_day.strftime("%A").lower()
            next_day_factor = profile.engagement_patterns.get(next_day_name, 1.0)
            
            for hour, base_score in time_scores.items():
                adjusted_score = base_score * next_day_factor
                hour_scores[hour] = adjusted_score
            
            target_date = next_day
        
        # Find best hour
        best_hour = max(hour_scores.keys(), key=lambda h: hour_scores[h])
        best_score = hour_scores[best_hour]
        
        # Determine confidence based on score and data quality
        if best_score > 0.15 and best_hour in profile.peak_activity_hours:
            confidence = ScheduleConfidence.HIGH
        elif best_score > 0.10:
            confidence = ScheduleConfidence.MEDIUM
        else:
            confidence = ScheduleConfidence.LOW
        
        # Create optimal time with some randomness in minutes to avoid exact patterns
        optimal_time = target_date.replace(
            hour=best_hour,
            minute=random.randint(0, 59),
            second=0,
            microsecond=0
        )
        
        return optimal_time, confidence
    
    def _predict_engagement(self, post_time: datetime, platform: Platform, 
                          content_type: ContentType, profile: AudienceProfile) -> float:
        """Predict engagement rate for a specific time"""
        # Get base engagement from content type preference
        base_engagement = profile.content_preferences.get(content_type, 0.1)
        
        # Time of day factor
        hour = post_time.hour
        time_factor = 1.3 if hour in profile.peak_activity_hours else 0.8
        
        # Day of week factor
        day_name = post_time.strftime("%A").lower()
        day_factor = profile.engagement_patterns.get(day_name, 1.0)
        
        # Calculate predicted engagement
        predicted = base_engagement * time_factor * day_factor * 0.15  # Scale to reasonable %
        
        return max(0.01, min(0.5, predicted))  # Clamp between 1% and 50%
    
    def _generate_reasoning(self, optimal_time: datetime, time_scores: Dict[int, float], 
                          profile: AudienceProfile, historical_data: List[EngagementData]) -> List[str]:
        """Generate human-readable reasoning for the recommendation"""
        reasoning = []
        
        hour = optimal_time.hour
        day_name = optimal_time.strftime("%A")
        
        # Time of day reasoning
        if hour in profile.peak_activity_hours:
            reasoning.append(f"Hour {hour}:00 is a peak activity time for your audience")
        
        # Day of week reasoning
        day_name_lower = day_name.lower()
        day_factor = profile.engagement_patterns.get(day_name_lower, 1.0)
        if day_factor > 0.9:
            reasoning.append(f"{day_name}s typically show high engagement")
        elif day_factor < 0.8:
            reasoning.append(f"{day_name}s show lower engagement, but this is the best available time")
        
        # Historical performance
        hour_data = [d for d in historical_data if d.timestamp.hour == hour]
        if hour_data:
            avg_engagement = statistics.mean(d.engagement_rate for d in hour_data)
            reasoning.append(f"Historical posts at this hour averaged {avg_engagement:.1%} engagement")
        
        # Data confidence
        total_data_points = len(historical_data)
        if total_data_points > 20:
            reasoning.append(f"Recommendation based on {total_data_points} historical posts")
        else:
            reasoning.append(f"Limited data available ({total_data_points} posts), recommendation uses platform averages")
        
        return reasoning
    
    def _get_alternative_times(self, target_date: datetime, time_scores: Dict[int, float], 
                             optimal_hour: int) -> List[Tuple[datetime, float]]:
        """Get alternative posting times with scores"""
        alternatives = []
        
        # Sort hours by score, excluding the optimal hour
        sorted_hours = sorted(
            [(hour, score) for hour, score in time_scores.items() if hour != optimal_hour],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Take top 3 alternatives
        for hour, score in sorted_hours[:3]:
            alt_time = target_date.replace(
                hour=hour,
                minute=random.randint(0, 59),
                second=0,
                microsecond=0
            )
            
            # If time is in the past, move to next day
            if alt_time <= datetime.now():
                alt_time += timedelta(days=1)
            
            alternatives.append((alt_time, score))
        
        return alternatives
    
    def _get_fallback_recommendation(self, platform: Platform, content_type: ContentType, 
                                   target_date: datetime) -> ScheduleRecommendation:
        """Get fallback recommendation when insufficient data"""
        # Use general best practices
        if platform == Platform.FANVUE:
            optimal_hour = 19  # 7 PM
        elif platform == Platform.LOYALFANS:
            optimal_hour = 21  # 9 PM
        else:
            optimal_hour = 18  # 6 PM
        
        optimal_time = target_date.replace(
            hour=optimal_hour,
            minute=random.randint(0, 59),
            second=0,
            microsecond=0
        )
        
        if optimal_time <= datetime.now():
            optimal_time += timedelta(days=1)
        
        return ScheduleRecommendation(
            platform=platform,
            content_type=content_type,
            optimal_time=optimal_time,
            confidence=ScheduleConfidence.LOW,
            expected_engagement=0.1,
            reasoning=["Using general best practices due to insufficient historical data"],
            alternatives=[]
        )
    
    def run_ab_test(self, platform: Platform, content_type: ContentType, 
                   test_times: List[datetime], duration_days: int = 7) -> str:
        """Start an A/B test for optimal posting times"""
        test_id = f"ab_test_{platform.value}_{content_type.value}_{int(datetime.now().timestamp())}"
        
        logger.info(f"🧪 Starting A/B test: {test_id}")
        logger.info(f"Testing {len(test_times)} different times over {duration_days} days")
        
        # In production, this would set up actual A/B testing
        # For now, we'll just log the test setup
        
        test_config = {
            "test_id": test_id,
            "platform": platform.value,
            "content_type": content_type.value,
            "test_times": [t.isoformat() for t in test_times],
            "duration_days": duration_days,
            "start_date": datetime.now().isoformat()
        }
        
        self.schedule_performance[test_id] = []
        
        logger.info(f"✅ A/B test configured: {test_id}")
        return test_id
    
    def get_schedule_analytics(self, platform: Optional[Platform] = None, 
                             days: int = 30) -> Dict[str, Any]:
        """Get analytics on scheduling performance"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter data
        if platform:
            relevant_data = [
                d for d in self.engagement_history
                if d.platform == platform and d.timestamp >= cutoff_date
            ]
        else:
            relevant_data = [
                d for d in self.engagement_history
                if d.timestamp >= cutoff_date
            ]
        
        if not relevant_data:
            return {"error": "No data available for the specified period"}
        
        # Calculate analytics
        total_posts = len(relevant_data)
        avg_engagement = statistics.mean(d.engagement_rate for d in relevant_data)
        
        # Best performing hours
        hour_performance = {}
        for hour in range(24):
            hour_data = [d for d in relevant_data if d.timestamp.hour == hour]
            if hour_data:
                hour_performance[hour] = statistics.mean(d.engagement_rate for d in hour_data)
        
        best_hours = sorted(hour_performance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Best performing days
        day_performance = {}
        for data in relevant_data:
            day_name = data.timestamp.strftime("%A")
            if day_name not in day_performance:
                day_performance[day_name] = []
            day_performance[day_name].append(data.engagement_rate)
        
        day_averages = {day: statistics.mean(rates) for day, rates in day_performance.items()}
        best_days = sorted(day_averages.items(), key=lambda x: x[1], reverse=True)
        
        # Content type performance
        content_performance = {}
        for data in relevant_data:
            ct = data.content_type.value
            if ct not in content_performance:
                content_performance[ct] = []
            content_performance[ct].append(data.engagement_rate)
        
        content_averages = {ct: statistics.mean(rates) for ct, rates in content_performance.items()}
        
        analytics = {
            "period_days": days,
            "total_posts": total_posts,
            "average_engagement": round(avg_engagement, 4),
            "best_hours": [{"hour": f"{hour}:00", "engagement": round(rate, 4)} for hour, rate in best_hours],
            "best_days": [{"day": day, "engagement": round(rate, 4)} for day, rate in best_days],
            "content_performance": {ct: round(rate, 4) for ct, rate in content_averages.items()},
            "platform": platform.value if platform else "all"
        }
        
        return analytics
    
    def export_schedule_data(self) -> Dict[str, Any]:
        """Export all scheduling data for backup/analysis"""
        return {
            "engagement_history": [
                {
                    "timestamp": data.timestamp.isoformat(),
                    "platform": data.platform.value,
                    "content_type": data.content_type.value,
                    "engagement_rate": data.engagement_rate,
                    "views": data.views,
                    "likes": data.likes,
                    "comments": data.comments,
                    "shares": data.shares,
                    "revenue_impact": data.revenue_impact
                }
                for data in self.engagement_history
            ],
            "audience_profiles": {
                platform.value: asdict(profile)
                for platform, profile in self.audience_profiles.items()
            },
            "ab_test_results": self.schedule_performance
        }