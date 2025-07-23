#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management for FionaSparx AI Content Creator

This module handles all configuration settings, environment variables,
and application settings with security and validation.

Features:
- Environment-based configuration
- Secure API key management
- Configuration validation
- Default fallbacks
- Development/Production modes
- Feature flags

Author: FionaSparx AI Content Creator
Version: 2.0.0
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import secrets
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class AIModelConfig:
    """AI Model configuration"""
    text_model: str = "gpt-4"
    text_api_key: str = ""
    text_endpoint: str = "https://api.openai.com/v1"
    image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    image_api_key: str = ""
    image_endpoint: str = "https://api.stability.ai/v1"
    huggingface_token: str = ""
    use_local_models: bool = False

@dataclass
class PlatformConfig:
    """Platform API configuration"""
    # Instagram
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    
    # Twitter
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    # TikTok
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_access_token: str = ""
    
    # Adult content platforms
    fanvue_api_key: str = ""
    fanvue_user_id: str = ""
    fanvue_webhook_secret: str = ""
    loyalfans_api_key: str = ""
    loyalfans_user_id: str = ""
    loyalfans_webhook_secret: str = ""

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    db_encryption_key: str = ""
    api_rate_limit: int = 100
    api_rate_limit_window: int = 3600
    content_moderation_enabled: bool = True
    adult_content_filter: str = "strict"

@dataclass
class ContentConfig:
    """Content generation configuration"""
    default_platform: str = "fanvue"
    default_content_type: str = "lifestyle"
    default_quality_threshold: float = 3.5
    default_image_size: str = "768x768"
    max_image_size_mb: int = 30
    supported_image_formats: List[str] = field(default_factory=lambda: ["JPEG", "PNG", "WEBP"])
    max_caption_length: int = 2200
    max_hashtags: int = 30
    auto_hashtag_generation: bool = True

@dataclass
class SchedulingConfig:
    """Scheduling and automation configuration"""
    auto_posting_enabled: bool = True
    posting_hours: List[str] = field(default_factory=lambda: ["08:00", "12:00", "17:00", "20:00"])
    timezone: str = "Europe/Oslo"
    cross_promotion_enabled: bool = True
    cross_promotion_delay_minutes: int = 30
    content_backup_enabled: bool = True
    backup_retention_days: int = 90

@dataclass
class N8NConfig:
    """N8N workflow configuration"""
    n8n_url: str = "http://localhost:5678"
    n8n_api_key: str = ""
    n8n_webhook_url: str = "http://localhost:5678/webhook"
    daily_posting_workflow_id: str = ""
    engagement_analysis_workflow_id: str = ""
    content_generation_workflow_id: str = ""

@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling features"""
    ai_learning_enabled: bool = True
    ai_personality_enabled: bool = True
    ai_response_generation: bool = True
    instagram_stories_enabled: bool = True
    twitter_threads_enabled: bool = True
    tiktok_posting_enabled: bool = False
    a_b_testing_enabled: bool = True
    subscriber_segmentation: bool = True
    revenue_optimization: bool = True

class ConfigManager:
    """
    Configuration manager for FionaSparx AI system
    Handles loading, validation, and access to all configuration settings
    """
    
    def __init__(self, config_dir: str = "config", env_file: str = ".env"):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory containing configuration files
            env_file: Environment file name
        """
        self.config_dir = Path(config_dir)
        self.env_file = env_file
        
        # Load environment variables
        self._load_environment()
        
        # Initialize configuration objects
        self.app = self._load_app_config()
        self.ai_models = self._load_ai_config()
        self.platforms = self._load_platform_config()
        self.security = self._load_security_config()
        self.content = self._load_content_config()
        self.scheduling = self._load_scheduling_config()
        self.n8n = self._load_n8n_config()
        self.features = self._load_feature_flags()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info("✅ Configuration manager initialized")
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        env_path = self.config_dir / self.env_file
        
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"📄 Loaded environment from {env_path}")
        else:
            logger.warning(f"⚠️  Environment file not found: {env_path}")
            
            # Create example file if it doesn't exist
            example_path = self.config_dir / "api-keys.example.env"
            if example_path.exists():
                logger.info(f"💡 Example configuration available at {example_path}")
    
    def _load_app_config(self) -> Dict[str, Any]:
        """Load application configuration"""
        return {
            'name': os.getenv('APP_NAME', 'FionaSparx AI Content Creator'),
            'version': os.getenv('APP_VERSION', '2.0.0'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'database_path': os.getenv('DATABASE_PATH', 'data/fionasparx.db'),
            'log_file': os.getenv('LOG_FILE', 'logs/fionasparx.log')
        }
    
    def _load_ai_config(self) -> AIModelConfig:
        """Load AI model configuration"""
        return AIModelConfig(
            text_model=os.getenv('TEXT_MODEL', 'gpt-4'),
            text_api_key=os.getenv('TEXT_MODEL_API_KEY', ''),
            text_endpoint=os.getenv('TEXT_MODEL_ENDPOINT', 'https://api.openai.com/v1'),
            image_model=os.getenv('IMAGE_MODEL', 'stabilityai/stable-diffusion-xl-base-1.0'),
            image_api_key=os.getenv('IMAGE_MODEL_API_KEY', ''),
            image_endpoint=os.getenv('IMAGE_MODEL_ENDPOINT', 'https://api.stability.ai/v1'),
            huggingface_token=os.getenv('HUGGINGFACE_API_KEY', ''),
            use_local_models=os.getenv('USE_LOCAL_MODELS', 'false').lower() == 'true'
        )
    
    def _load_platform_config(self) -> PlatformConfig:
        """Load platform API configuration"""
        return PlatformConfig(
            # Instagram
            instagram_access_token=os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
            instagram_business_account_id=os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', ''),
            instagram_app_id=os.getenv('INSTAGRAM_APP_ID', ''),
            instagram_app_secret=os.getenv('INSTAGRAM_APP_SECRET', ''),
            
            # Twitter
            twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN', ''),
            twitter_api_key=os.getenv('TWITTER_API_KEY', ''),
            twitter_api_secret=os.getenv('TWITTER_API_SECRET', ''),
            twitter_access_token=os.getenv('TWITTER_ACCESS_TOKEN', ''),
            twitter_access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''),
            
            # TikTok
            tiktok_client_key=os.getenv('TIKTOK_CLIENT_KEY', ''),
            tiktok_client_secret=os.getenv('TIKTOK_CLIENT_SECRET', ''),
            tiktok_access_token=os.getenv('TIKTOK_ACCESS_TOKEN', ''),
            
            # Adult content platforms
            fanvue_api_key=os.getenv('FANVUE_API_KEY', ''),
            fanvue_user_id=os.getenv('FANVUE_USER_ID', ''),
            fanvue_webhook_secret=os.getenv('FANVUE_WEBHOOK_SECRET', ''),
            loyalfans_api_key=os.getenv('LOYALFANS_API_KEY', ''),
            loyalfans_user_id=os.getenv('LOYALFANS_USER_ID', ''),
            loyalfans_webhook_secret=os.getenv('LOYALFANS_WEBHOOK_SECRET', '')
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        # Generate secure defaults if not provided
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        if not jwt_secret:
            jwt_secret = secrets.token_urlsafe(32)
            logger.warning("🔑 Generated temporary JWT secret. Set JWT_SECRET_KEY in production!")
        
        db_encryption_key = os.getenv('DB_ENCRYPTION_KEY')
        if not db_encryption_key:
            db_encryption_key = secrets.token_urlsafe(32)
            logger.warning("🔑 Generated temporary DB encryption key. Set DB_ENCRYPTION_KEY in production!")
        
        return SecurityConfig(
            jwt_secret_key=jwt_secret,
            jwt_algorithm=os.getenv('JWT_ALGORITHM', 'HS256'),
            jwt_expiration_hours=int(os.getenv('JWT_EXPIRATION_HOURS', '24')),
            db_encryption_key=db_encryption_key,
            api_rate_limit=int(os.getenv('API_RATE_LIMIT', '100')),
            api_rate_limit_window=int(os.getenv('API_RATE_LIMIT_WINDOW', '3600')),
            content_moderation_enabled=os.getenv('CONTENT_MODERATION_ENABLED', 'true').lower() == 'true',
            adult_content_filter=os.getenv('ADULT_CONTENT_FILTER', 'strict')
        )
    
    def _load_content_config(self) -> ContentConfig:
        """Load content generation configuration"""
        formats = os.getenv('SUPPORTED_IMAGE_FORMATS', 'JPEG,PNG,WEBP').split(',')
        
        return ContentConfig(
            default_platform=os.getenv('DEFAULT_PLATFORM', 'fanvue'),
            default_content_type=os.getenv('DEFAULT_CONTENT_TYPE', 'lifestyle'),
            default_quality_threshold=float(os.getenv('DEFAULT_QUALITY_THRESHOLD', '3.5')),
            default_image_size=os.getenv('DEFAULT_IMAGE_SIZE', '768x768'),
            max_image_size_mb=int(os.getenv('MAX_IMAGE_SIZE_MB', '30')),
            supported_image_formats=[fmt.strip() for fmt in formats],
            max_caption_length=int(os.getenv('MAX_CAPTION_LENGTH', '2200')),
            max_hashtags=int(os.getenv('MAX_HASHTAGS', '30')),
            auto_hashtag_generation=os.getenv('AUTO_HASHTAG_GENERATION', 'true').lower() == 'true'
        )
    
    def _load_scheduling_config(self) -> SchedulingConfig:
        """Load scheduling configuration"""
        posting_hours = os.getenv('POSTING_HOURS', '08:00,12:00,17:00,20:00').split(',')
        
        return SchedulingConfig(
            auto_posting_enabled=os.getenv('AUTO_POSTING_ENABLED', 'true').lower() == 'true',
            posting_hours=[hour.strip() for hour in posting_hours],
            timezone=os.getenv('TIMEZONE', 'Europe/Oslo'),
            cross_promotion_enabled=os.getenv('CROSS_PROMOTION_ENABLED', 'true').lower() == 'true',
            cross_promotion_delay_minutes=int(os.getenv('CROSS_PROMOTION_DELAY_MINUTES', '30')),
            content_backup_enabled=os.getenv('CONTENT_BACKUP_ENABLED', 'true').lower() == 'true',
            backup_retention_days=int(os.getenv('BACKUP_RETENTION_DAYS', '90'))
        )
    
    def _load_n8n_config(self) -> N8NConfig:
        """Load N8N workflow configuration"""
        return N8NConfig(
            n8n_url=os.getenv('N8N_URL', 'http://localhost:5678'),
            n8n_api_key=os.getenv('N8N_API_KEY', ''),
            n8n_webhook_url=os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook'),
            daily_posting_workflow_id=os.getenv('N8N_DAILY_POSTING_WORKFLOW_ID', ''),
            engagement_analysis_workflow_id=os.getenv('N8N_ENGAGEMENT_ANALYSIS_WORKFLOW_ID', ''),
            content_generation_workflow_id=os.getenv('N8N_CONTENT_GENERATION_WORKFLOW_ID', '')
        )
    
    def _load_feature_flags(self) -> FeatureFlags:
        """Load feature flags"""
        return FeatureFlags(
            ai_learning_enabled=os.getenv('AI_LEARNING_ENABLED', 'true').lower() == 'true',
            ai_personality_enabled=os.getenv('AI_PERSONALITY_ENABLED', 'true').lower() == 'true',
            ai_response_generation=os.getenv('AI_RESPONSE_GENERATION', 'true').lower() == 'true',
            instagram_stories_enabled=os.getenv('INSTAGRAM_STORIES_ENABLED', 'true').lower() == 'true',
            twitter_threads_enabled=os.getenv('TWITTER_THREADS_ENABLED', 'true').lower() == 'true',
            tiktok_posting_enabled=os.getenv('TIKTOK_POSTING_ENABLED', 'false').lower() == 'true',
            a_b_testing_enabled=os.getenv('A_B_TESTING_ENABLED', 'true').lower() == 'true',
            subscriber_segmentation=os.getenv('SUBSCRIBER_SEGMENTATION', 'true').lower() == 'true',
            revenue_optimization=os.getenv('REVENUE_OPTIMIZATION', 'true').lower() == 'true'
        )
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        validation_errors = []
        
        # Validate critical settings
        if self.app['environment'] == 'production':
            if not self.security.jwt_secret_key or self.security.jwt_secret_key.startswith('temp_'):
                validation_errors.append("JWT_SECRET_KEY must be set in production")
            
            if not self.security.db_encryption_key or self.security.db_encryption_key.startswith('temp_'):
                validation_errors.append("DB_ENCRYPTION_KEY must be set in production")
        
        # Validate API keys for enabled platforms
        if self.features.instagram_stories_enabled:
            if not self.platforms.instagram_access_token:
                validation_errors.append("Instagram access token required when Instagram features enabled")
        
        if self.features.twitter_threads_enabled:
            if not self.platforms.twitter_bearer_token:
                validation_errors.append("Twitter bearer token required when Twitter features enabled")
        
        # Validate content settings
        if self.content.default_quality_threshold < 1.0 or self.content.default_quality_threshold > 5.0:
            validation_errors.append("Quality threshold must be between 1.0 and 5.0")
        
        # Log validation results
        if validation_errors:
            for error in validation_errors:
                logger.error(f"❌ Configuration error: {error}")
            
            if self.app['environment'] == 'production':
                raise ValueError(f"Configuration validation failed: {validation_errors}")
            else:
                logger.warning("⚠️  Configuration warnings detected (development mode)")
        else:
            logger.info("✅ Configuration validation passed")
    
    def get_platform_credentials(self, platform: str) -> Dict[str, str]:
        """Get credentials for a specific platform"""
        credentials = {}
        
        if platform.lower() == 'instagram':
            credentials = {
                'access_token': self.platforms.instagram_access_token,
                'business_account_id': self.platforms.instagram_business_account_id,
                'app_id': self.platforms.instagram_app_id,
                'app_secret': self.platforms.instagram_app_secret
            }
        elif platform.lower() == 'twitter':
            credentials = {
                'bearer_token': self.platforms.twitter_bearer_token,
                'api_key': self.platforms.twitter_api_key,
                'api_secret': self.platforms.twitter_api_secret,
                'access_token': self.platforms.twitter_access_token,
                'access_token_secret': self.platforms.twitter_access_token_secret
            }
        elif platform.lower() == 'tiktok':
            credentials = {
                'client_key': self.platforms.tiktok_client_key,
                'client_secret': self.platforms.tiktok_client_secret,
                'access_token': self.platforms.tiktok_access_token
            }
        elif platform.lower() == 'fanvue':
            credentials = {
                'api_key': self.platforms.fanvue_api_key,
                'user_id': self.platforms.fanvue_user_id,
                'webhook_secret': self.platforms.fanvue_webhook_secret
            }
        elif platform.lower() == 'loyalfans':
            credentials = {
                'api_key': self.platforms.loyalfans_api_key,
                'user_id': self.platforms.loyalfans_user_id,
                'webhook_secret': self.platforms.loyalfans_webhook_secret
            }
        
        # Filter out empty credentials
        return {k: v for k, v in credentials.items() if v}
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Check if a platform is enabled and configured"""
        credentials = self.get_platform_credentials(platform)
        
        # Platform-specific checks
        if platform.lower() == 'instagram':
            return (self.features.instagram_stories_enabled and 
                   'access_token' in credentials and 
                   'business_account_id' in credentials)
        elif platform.lower() == 'twitter':
            return (self.features.twitter_threads_enabled and 
                   'bearer_token' in credentials)
        elif platform.lower() == 'tiktok':
            return (self.features.tiktok_posting_enabled and 
                   'client_key' in credentials and 
                   'access_token' in credentials)
        elif platform.lower() in ['fanvue', 'loyalfans']:
            return 'api_key' in credentials
        
        return False
    
    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled and configured platforms"""
        platforms = ['instagram', 'twitter', 'tiktok', 'fanvue', 'loyalfans']
        return [platform for platform in platforms if self.is_platform_enabled(platform)]
    
    def update_feature_flag(self, feature: str, enabled: bool):
        """Update a feature flag"""
        if hasattr(self.features, feature):
            setattr(self.features, feature, enabled)
            logger.info(f"🎛️  Updated feature flag: {feature} = {enabled}")
        else:
            logger.error(f"❌ Unknown feature flag: {feature}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging"""
        return {
            'app': self.app,
            'environment': self.app['environment'],
            'enabled_platforms': self.get_enabled_platforms(),
            'ai_models': {
                'text_model': self.ai_models.text_model,
                'image_model': self.ai_models.image_model,
                'use_local': self.ai_models.use_local_models
            },
            'features': {
                'ai_learning': self.features.ai_learning_enabled,
                'auto_posting': self.scheduling.auto_posting_enabled,
                'cross_promotion': self.scheduling.cross_promotion_enabled
            },
            'security': {
                'content_moderation': self.security.content_moderation_enabled,
                'rate_limiting': f"{self.security.api_rate_limit}/{self.security.api_rate_limit_window}s"
            }
        }
    
    def save_configuration(self, config_file: str = "fionasparx_config.json"):
        """Save current configuration to file (excluding sensitive data)"""
        config_path = self.config_dir / config_file
        
        # Create safe configuration (no API keys)
        safe_config = {
            'app': self.app,
            'content': {
                'default_platform': self.content.default_platform,
                'default_content_type': self.content.default_content_type,
                'default_quality_threshold': self.content.default_quality_threshold,
                'max_caption_length': self.content.max_caption_length,
                'max_hashtags': self.content.max_hashtags
            },
            'scheduling': {
                'auto_posting_enabled': self.scheduling.auto_posting_enabled,
                'posting_hours': self.scheduling.posting_hours,
                'timezone': self.scheduling.timezone,
                'cross_promotion_enabled': self.scheduling.cross_promotion_enabled
            },
            'features': {
                'ai_learning_enabled': self.features.ai_learning_enabled,
                'ai_personality_enabled': self.features.ai_personality_enabled,
                'instagram_stories_enabled': self.features.instagram_stories_enabled,
                'twitter_threads_enabled': self.features.twitter_threads_enabled,
                'tiktok_posting_enabled': self.features.tiktok_posting_enabled,
                'a_b_testing_enabled': self.features.a_b_testing_enabled
            }
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(safe_config, f, indent=2)
            logger.info(f"💾 Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")

# Global configuration instance
config = None

def get_config() -> ConfigManager:
    """Get global configuration instance"""
    global config
    if config is None:
        config = ConfigManager()
    return config

def reload_config():
    """Reload configuration from files"""
    global config
    config = ConfigManager()
    logger.info("🔄 Configuration reloaded")

# Example usage and testing
if __name__ == "__main__":
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Print configuration summary
    summary = config_manager.get_configuration_summary()
    print("Configuration Summary:")
    print(json.dumps(summary, indent=2))
    
    # Check enabled platforms
    enabled_platforms = config_manager.get_enabled_platforms()
    print(f"\nEnabled platforms: {enabled_platforms}")
    
    # Test platform credentials
    for platform in ['instagram', 'fanvue', 'loyalfans']:
        credentials = config_manager.get_platform_credentials(platform)
        has_creds = len(credentials) > 0
        print(f"{platform}: {'✅' if has_creds else '❌'} ({len(credentials)} credentials)")
    
    # Save configuration
    config_manager.save_configuration()
    
    print("✅ Configuration test completed")