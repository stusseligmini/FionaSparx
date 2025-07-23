#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Models for FionaSparx AI Content Creator

This module defines the database schema and models for the comprehensive
AI-powered social media automation system.

Tables:
- Users: Creator profiles and authentication
- Platforms: Social media platform configurations
- Content: Generated content items
- Analytics: Performance metrics and insights
- Subscribers: Subscriber profiles and behavior data
- Campaigns: Marketing campaigns and automation schedules
- AI_Models: AI model configurations and training data
- Security: API keys, tokens, and security configurations

Author: FionaSparx AI Content Creator
Version: 2.0.0
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import uuid
import os

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types"""
    FANVUE = "fanvue"
    LOYALFANS = "loyalfans"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    ONLYFANS = "onlyfans"

class ContentType(Enum):
    """Content types"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    STORY = "story"
    CAROUSEL = "carousel"
    REEL = "reel"

class ContentStatus(Enum):
    """Content status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"

class SubscriberTier(Enum):
    """Subscriber tier levels"""
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
    EXCLUSIVE = "exclusive"

@dataclass
class User:
    """Creator/User profile"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    display_name: str = ""
    bio: str = ""
    profile_image_url: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)
    subscription_tier: str = "basic"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True

@dataclass
class Platform:
    """Social media platform configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    platform_type: str = ""
    platform_username: str = ""
    api_credentials: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    last_sync: str = field(default_factory=lambda: datetime.now().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Content:
    """Generated content item"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    platform_id: str = ""
    content_type: str = ""
    title: str = ""
    caption: str = ""
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    status: str = ContentStatus.DRAFT.value
    scheduled_at: Optional[str] = None
    published_at: Optional[str] = None
    external_id: str = ""  # Platform-specific ID after publishing
    ai_generated: bool = True
    template_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Analytics:
    """Content and platform analytics"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    platform_id: str = ""
    metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    engagement_data: Dict[str, Any] = field(default_factory=dict)
    revenue_data: Dict[str, float] = field(default_factory=dict)
    audience_insights: Dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=lambda: datetime.now().isoformat())
    period_start: str = ""
    period_end: str = ""

@dataclass
class Subscriber:
    """Subscriber profile and behavior"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    platform_id: str = ""
    external_subscriber_id: str = ""
    username: str = ""
    tier: str = SubscriberTier.FREE.value
    engagement_score: float = 0.0
    lifetime_value: float = 0.0
    behavior_data: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    churn_risk: float = 0.0
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())
    subscribed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Campaign:
    """Marketing campaign or automation schedule"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    name: str = ""
    description: str = ""
    campaign_type: str = ""  # daily_posting, cross_promotion, engagement_boost
    platforms: List[str] = field(default_factory=list)
    schedule: Dict[str, Any] = field(default_factory=dict)
    content_rules: Dict[str, Any] = field(default_factory=dict)
    targeting: Dict[str, Any] = field(default_factory=dict)
    budget: Dict[str, float] = field(default_factory=dict)
    status: str = "active"
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    start_date: str = ""
    end_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AIModel:
    """AI model configuration and training data"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    model_type: str = ""  # content_generator, engagement_predictor, etc.
    model_name: str = ""
    version: str = "1.0"
    configuration: Dict[str, Any] = field(default_factory=dict)
    training_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    is_trained: bool = False
    is_active: bool = True
    model_file_path: str = ""
    last_trained: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SecurityConfig:
    """Security configuration and API key management"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    service_name: str = ""
    api_keys: Dict[str, str] = field(default_factory=dict)  # Encrypted
    tokens: Dict[str, str] = field(default_factory=dict)  # Encrypted
    permissions: List[str] = field(default_factory=list)
    encryption_key_hash: str = ""
    last_rotated: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class DatabaseManager:
    """
    Database manager for FionaSparx AI system
    Handles all database operations with security and encryption
    """
    
    def __init__(self, database_path: str = "data/fionasparx.db", encryption_key: str = None):
        """
        Initialize database manager
        
        Args:
            database_path: Path to SQLite database file
            encryption_key: Encryption key for sensitive data
        """
        self.database_path = database_path
        self.encryption_key = encryption_key or os.getenv("DB_ENCRYPTION_KEY", "default_key_change_in_production")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        
        self._initialize_database()
        logger.info("✅ Database manager initialized")
    
    def _initialize_database(self):
        """Initialize database with all required tables"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    bio TEXT,
                    profile_image_url TEXT,
                    preferences TEXT,
                    subscription_tier TEXT DEFAULT 'basic',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Platforms table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS platforms (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    platform_type TEXT NOT NULL,
                    platform_username TEXT,
                    api_credentials TEXT,
                    configuration TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    last_sync TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    platform_id TEXT,
                    content_type TEXT NOT NULL,
                    title TEXT,
                    caption TEXT,
                    media_urls TEXT,
                    hashtags TEXT,
                    metadata TEXT,
                    quality_score REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'draft',
                    scheduled_at TEXT,
                    published_at TEXT,
                    external_id TEXT,
                    ai_generated BOOLEAN DEFAULT 1,
                    template_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE SET NULL
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id TEXT PRIMARY KEY,
                    content_id TEXT,
                    platform_id TEXT,
                    metrics TEXT,
                    engagement_data TEXT,
                    revenue_data TEXT,
                    audience_insights TEXT,
                    recorded_at TEXT NOT NULL,
                    period_start TEXT,
                    period_end TEXT,
                    FOREIGN KEY (content_id) REFERENCES content (id) ON DELETE CASCADE,
                    FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE CASCADE
                )
            ''')
            
            # Subscribers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    platform_id TEXT NOT NULL,
                    external_subscriber_id TEXT,
                    username TEXT,
                    tier TEXT DEFAULT 'free',
                    engagement_score REAL DEFAULT 0.0,
                    lifetime_value REAL DEFAULT 0.0,
                    behavior_data TEXT,
                    preferences TEXT,
                    interaction_history TEXT,
                    churn_risk REAL DEFAULT 0.0,
                    last_active TEXT,
                    subscribed_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE CASCADE
                )
            ''')
            
            # Campaigns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    campaign_type TEXT NOT NULL,
                    platforms TEXT,
                    schedule TEXT,
                    content_rules TEXT,
                    targeting TEXT,
                    budget TEXT,
                    status TEXT DEFAULT 'active',
                    performance_metrics TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # AI Models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_models (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    version TEXT DEFAULT '1.0',
                    configuration TEXT,
                    training_data TEXT,
                    performance_metrics TEXT,
                    is_trained BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    model_file_path TEXT,
                    last_trained TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Security configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_configs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    api_keys TEXT,
                    tokens TEXT,
                    permissions TEXT,
                    encryption_key_hash TEXT,
                    last_rotated TEXT,
                    expires_at TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Learning insights table (from learning engine)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    insight_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    recommendation TEXT NOT NULL,
                    impact_prediction REAL,
                    supporting_data TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Content performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_performance (
                    id TEXT PRIMARY KEY,
                    content_id TEXT NOT NULL,
                    platform_id TEXT NOT NULL,
                    posted_at TEXT NOT NULL,
                    engagement_metrics TEXT,
                    quality_score REAL,
                    reach INTEGER DEFAULT 0,
                    conversion_rate REAL DEFAULT 0.0,
                    revenue_generated REAL DEFAULT 0.0,
                    optimal_timing_score REAL DEFAULT 0.0,
                    FOREIGN KEY (content_id) REFERENCES content (id) ON DELETE CASCADE,
                    FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE CASCADE
                )
            ''')
            
            # Subscriber profiles (for learning engine)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriber_profiles (
                    user_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    engagement_score REAL DEFAULT 0.0,
                    preferred_content_types TEXT,
                    active_hours TEXT,
                    interaction_patterns TEXT,
                    spending_behavior TEXT,
                    lifetime_value REAL DEFAULT 0.0,
                    churn_risk REAL DEFAULT 0.0,
                    personalization_preferences TEXT,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_content_user_id ON content(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_content_platform_id ON content(platform_id)",
                "CREATE INDEX IF NOT EXISTS idx_content_status ON content(status)",
                "CREATE INDEX IF NOT EXISTS idx_content_scheduled_at ON content(scheduled_at)",
                "CREATE INDEX IF NOT EXISTS idx_analytics_content_id ON analytics(content_id)",
                "CREATE INDEX IF NOT EXISTS idx_analytics_recorded_at ON analytics(recorded_at)",
                "CREATE INDEX IF NOT EXISTS idx_subscribers_user_id ON subscribers(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_subscribers_platform_id ON subscribers(platform_id)",
                "CREATE INDEX IF NOT EXISTS idx_subscribers_tier ON subscribers(tier)",
                "CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON campaigns(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)",
                "CREATE INDEX IF NOT EXISTS idx_learning_insights_user_id ON learning_insights(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_learning_insights_type ON learning_insights(insight_type)",
                "CREATE INDEX IF NOT EXISTS idx_content_performance_content_id ON content_performance(content_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            logger.info("📊 Database tables and indexes created")
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            # Simple encryption using SHA256 hash (in production, use proper encryption like AES)
            key_hash = hashlib.sha256(self.encryption_key.encode()).hexdigest()
            data_hash = hashlib.sha256((data + key_hash).encode()).hexdigest()
            return f"encrypted_{data_hash}"
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        # This is a placeholder - in production, implement proper decryption
        if encrypted_data.startswith("encrypted_"):
            return "[ENCRYPTED_DATA]"
        return encrypted_data
    
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users 
                    (id, username, email, display_name, bio, profile_image_url, 
                     preferences, subscription_tier, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user.id, user.username, user.email, user.display_name,
                    user.bio, user.profile_image_url, json.dumps(user.preferences),
                    user.subscription_tier, user.created_at, user.updated_at, user.is_active
                ))
                conn.commit()
                logger.info(f"✅ Created user: {user.username}")
                return True
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    def create_platform(self, platform: Platform) -> bool:
        """Create a new platform configuration"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Encrypt API credentials
                encrypted_credentials = json.dumps({
                    key: self._encrypt_data(value) for key, value in platform.api_credentials.items()
                })
                
                cursor.execute('''
                    INSERT INTO platforms 
                    (id, user_id, platform_type, platform_username, api_credentials,
                     configuration, is_active, last_sync, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    platform.id, platform.user_id, platform.platform_type,
                    platform.platform_username, encrypted_credentials,
                    json.dumps(platform.configuration), platform.is_active,
                    platform.last_sync, platform.created_at
                ))
                conn.commit()
                logger.info(f"✅ Created platform: {platform.platform_type} for user {platform.user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to create platform: {e}")
            return False
    
    def create_content(self, content: Content) -> bool:
        """Create a new content item"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO content 
                    (id, user_id, platform_id, content_type, title, caption,
                     media_urls, hashtags, metadata, quality_score, status,
                     scheduled_at, published_at, external_id, ai_generated,
                     template_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    content.id, content.user_id, content.platform_id, content.content_type,
                    content.title, content.caption, json.dumps(content.media_urls),
                    json.dumps(content.hashtags), json.dumps(content.metadata),
                    content.quality_score, content.status, content.scheduled_at,
                    content.published_at, content.external_id, content.ai_generated,
                    content.template_id, content.created_at, content.updated_at
                ))
                conn.commit()
                logger.info(f"✅ Created content: {content.id}")
                return True
        except Exception as e:
            logger.error(f"Failed to create content: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        id=row[0], username=row[1], email=row[2], display_name=row[3],
                        bio=row[4], profile_image_url=row[5], 
                        preferences=json.loads(row[6]) if row[6] else {},
                        subscription_tier=row[7], created_at=row[8], updated_at=row[9],
                        is_active=bool(row[10])
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def get_user_platforms(self, user_id: str) -> List[Platform]:
        """Get all platforms for a user"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM platforms WHERE user_id = ? AND is_active = 1", (user_id,))
                rows = cursor.fetchall()
                
                platforms = []
                for row in rows:
                    # Decrypt API credentials
                    encrypted_creds = json.loads(row[4]) if row[4] else {}
                    decrypted_creds = {
                        key: self._decrypt_data(value) for key, value in encrypted_creds.items()
                    }
                    
                    platform = Platform(
                        id=row[0], user_id=row[1], platform_type=row[2],
                        platform_username=row[3], api_credentials=decrypted_creds,
                        configuration=json.loads(row[5]) if row[5] else {},
                        is_active=bool(row[6]), last_sync=row[7], created_at=row[8]
                    )
                    platforms.append(platform)
                
                return platforms
        except Exception as e:
            logger.error(f"Failed to get user platforms: {e}")
            return []
    
    def get_content_by_status(self, user_id: str, status: str) -> List[Content]:
        """Get content by status"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM content 
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                ''', (user_id, status))
                rows = cursor.fetchall()
                
                content_items = []
                for row in rows:
                    content = Content(
                        id=row[0], user_id=row[1], platform_id=row[2], content_type=row[3],
                        title=row[4], caption=row[5],
                        media_urls=json.loads(row[6]) if row[6] else [],
                        hashtags=json.loads(row[7]) if row[7] else [],
                        metadata=json.loads(row[8]) if row[8] else {},
                        quality_score=row[9], status=row[10], scheduled_at=row[11],
                        published_at=row[12], external_id=row[13], ai_generated=bool(row[14]),
                        template_id=row[15], created_at=row[16], updated_at=row[17]
                    )
                    content_items.append(content)
                
                return content_items
        except Exception as e:
            logger.error(f"Failed to get content by status: {e}")
            return []
    
    def update_content_status(self, content_id: str, status: str, external_id: str = None) -> bool:
        """Update content status"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                update_fields = ["status = ?", "updated_at = ?"]
                values = [status, datetime.now().isoformat()]
                
                if status == ContentStatus.PUBLISHED.value:
                    update_fields.append("published_at = ?")
                    values.append(datetime.now().isoformat())
                
                if external_id:
                    update_fields.append("external_id = ?")
                    values.append(external_id)
                
                values.append(content_id)
                
                cursor.execute(f'''
                    UPDATE content 
                    SET {", ".join(update_fields)}
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update content status: {e}")
            return False
    
    def create_analytics_record(self, analytics: Analytics) -> bool:
        """Create analytics record"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analytics 
                    (id, content_id, platform_id, metrics, engagement_data,
                     revenue_data, audience_insights, recorded_at, period_start, period_end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analytics.id, analytics.content_id, analytics.platform_id,
                    json.dumps(analytics.metrics), json.dumps(analytics.engagement_data),
                    json.dumps(analytics.revenue_data), json.dumps(analytics.audience_insights),
                    analytics.recorded_at, analytics.period_start, analytics.period_end
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to create analytics record: {e}")
            return False
    
    def get_analytics_summary(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Get analytics summary for user"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get content performance
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_content,
                        AVG(quality_score) as avg_quality,
                        COUNT(CASE WHEN status = 'published' THEN 1 END) as published_content
                    FROM content 
                    WHERE user_id = ? AND created_at >= datetime('now', '-{} days')
                '''.format(days_back), (user_id,))
                
                content_stats = cursor.fetchone()
                
                # Get analytics data
                cursor.execute('''
                    SELECT a.metrics, a.engagement_data, a.revenue_data
                    FROM analytics a
                    JOIN content c ON a.content_id = c.id
                    WHERE c.user_id = ? AND a.recorded_at >= datetime('now', '-{} days')
                '''.format(days_back), (user_id,))
                
                analytics_rows = cursor.fetchall()
                
                # Aggregate analytics
                total_engagement = 0
                total_revenue = 0
                
                for row in analytics_rows:
                    metrics = json.loads(row[0]) if row[0] else {}
                    revenue_data = json.loads(row[2]) if row[2] else {}
                    
                    total_engagement += sum(metrics.values()) if metrics else 0
                    total_revenue += sum(revenue_data.values()) if revenue_data else 0
                
                return {
                    'total_content': content_stats[0] or 0,
                    'published_content': content_stats[2] or 0,
                    'avg_quality_score': round(content_stats[1] or 0, 2),
                    'total_engagement': total_engagement,
                    'total_revenue': round(total_revenue, 2),
                    'period_days': days_back,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to maintain database performance"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
                
                # Clean up old analytics data
                cursor.execute('''
                    DELETE FROM analytics 
                    WHERE recorded_at < ?
                ''', (cutoff_date,))
                
                analytics_deleted = cursor.rowcount
                
                # Clean up old learning insights
                cursor.execute('''
                    DELETE FROM learning_insights 
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                insights_deleted = cursor.rowcount
                
                # Archive old content (don't delete, just mark as archived)
                cursor.execute('''
                    UPDATE content 
                    SET status = 'archived', updated_at = ?
                    WHERE created_at < ? AND status != 'archived'
                ''', (datetime.now().isoformat(), cutoff_date))
                
                content_archived = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"🧹 Cleanup completed: {analytics_deleted} analytics, {insights_deleted} insights, {content_archived} content archived")
                
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                tables = [
                    'users', 'platforms', 'content', 'analytics', 
                    'subscribers', 'campaigns', 'ai_models', 'security_configs'
                ]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                
                # Database file size
                stats['database_size_bytes'] = os.path.getsize(self.database_path)
                stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

# Database migration functions
def migrate_database(db_manager: DatabaseManager, target_version: int = 2):
    """Migrate database to target version"""
    try:
        current_version = _get_database_version(db_manager)
        
        if current_version >= target_version:
            logger.info(f"Database already at version {current_version}")
            return True
        
        logger.info(f"Migrating database from version {current_version} to {target_version}")
        
        # Apply migrations
        if current_version < 2:
            _migrate_to_v2(db_manager)
        
        _set_database_version(db_manager, target_version)
        logger.info("✅ Database migration completed")
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False

def _get_database_version(db_manager: DatabaseManager) -> int:
    """Get current database version"""
    try:
        with sqlite3.connect(db_manager.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS database_version (
                    version INTEGER PRIMARY KEY
                )
            ''')
            
            cursor.execute("SELECT version FROM database_version ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 1
    except:
        return 1

def _set_database_version(db_manager: DatabaseManager, version: int):
    """Set database version"""
    with sqlite3.connect(db_manager.database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO database_version (version) VALUES (?)", (version,))
        conn.commit()

def _migrate_to_v2(db_manager: DatabaseManager):
    """Migrate to version 2 - add new columns and tables"""
    with sqlite3.connect(db_manager.database_path) as conn:
        cursor = conn.cursor()
        
        # Add new columns to existing tables (if they don't exist)
        try:
            cursor.execute("ALTER TABLE content ADD COLUMN template_id TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE platforms ADD COLUMN last_sync TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()

# Example usage and testing
if __name__ == "__main__":
    # Initialize database manager
    db = DatabaseManager("data/test_fionasparx.db")
    
    # Create test user
    user = User(
        username="fiona_sparx",
        email="fiona@example.com",
        display_name="Fiona Sparx",
        bio="AI-powered content creator",
        subscription_tier="premium"
    )
    
    db.create_user(user)
    
    # Create test platform
    platform = Platform(
        user_id=user.id,
        platform_type="fanvue",
        platform_username="fionasparx",
        api_credentials={"api_key": "test_key_123", "secret": "test_secret_456"},
        configuration={"auto_post": True, "cross_promote": True}
    )
    
    db.create_platform(platform)
    
    # Create test content
    content = Content(
        user_id=user.id,
        platform_id=platform.id,
        content_type="image",
        title="Daily Lifestyle Post",
        caption="Living my best life! 💫 #lifestyle #authentic",
        media_urls=["https://example.com/image1.jpg"],
        hashtags=["lifestyle", "authentic", "fanvue"],
        quality_score=4.2
    )
    
    db.create_content(content)
    
    # Test queries
    retrieved_user = db.get_user(user.id)
    print(f"Retrieved user: {retrieved_user.username}")
    
    user_platforms = db.get_user_platforms(user.id)
    print(f"User platforms: {len(user_platforms)}")
    
    draft_content = db.get_content_by_status(user.id, "draft")
    print(f"Draft content: {len(draft_content)}")
    
    # Get analytics summary
    analytics_summary = db.get_analytics_summary(user.id)
    print(f"Analytics summary: {json.dumps(analytics_summary, indent=2)}")
    
    # Get database stats
    stats = db.get_database_stats()
    print(f"Database stats: {json.dumps(stats, indent=2)}")
    
    print("✅ Database models test completed")