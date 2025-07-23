#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Business API Integration for FionaSparx

This module provides comprehensive Instagram Business API integration for:
- Content posting and scheduling
- Story posting  
- Analytics and insights
- Cross-promotion to drive traffic to premium platforms
- Engagement tracking and analysis

Features:
- Automated posting with optimal timing
- Story creation and posting
- Hashtag optimization
- Engagement analytics
- Cross-platform promotion
- Compliance with Instagram policies

Author: FionaSparx AI Content Creator
Version: 2.0.0
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import os
import time
from urllib.parse import urlencode
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

@dataclass
class InstagramPost:
    """Instagram post data structure"""
    caption: str
    image_url: str
    hashtags: List[str]
    media_type: str = "IMAGE"
    scheduled_time: Optional[str] = None
    location_id: Optional[str] = None
    user_tags: Optional[List[Dict[str, str]]] = None

@dataclass
class InstagramStory:
    """Instagram story data structure"""
    media_url: str
    media_type: str = "IMAGE"
    text_overlay: Optional[str] = None
    stickers: Optional[List[Dict[str, Any]]] = None
    link_url: Optional[str] = None

@dataclass
class InstagramInsights:
    """Instagram analytics data"""
    post_id: str
    impressions: int
    reach: int
    engagement: int
    likes: int
    comments: int
    shares: int
    saves: int
    engagement_rate: float
    timestamp: str

class InstagramAPI:
    """
    Instagram Business API integration for content posting and analytics
    """
    
    def __init__(self, access_token: str, business_account_id: str, app_id: str = None):
        """
        Initialize Instagram API client
        
        Args:
            access_token: Facebook/Instagram access token
            business_account_id: Instagram Business Account ID
            app_id: Facebook App ID (optional)
        """
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.app_id = app_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Rate limiting
        self.rate_limit_remaining = 200
        self.rate_limit_reset = datetime.now()
        self.last_request_time = 0
        
        # Content guidelines for Instagram
        self.content_guidelines = {
            'max_caption_length': 2200,
            'max_hashtags': 30,
            'image_min_size': (320, 320),
            'image_max_size': (1080, 1080),
            'supported_formats': ['JPEG', 'JPG', 'PNG'],
            'max_file_size_mb': 30
        }
        
        self._validate_credentials()
        logger.info("✅ Instagram API client initialized")
    
    def _validate_credentials(self):
        """Validate API credentials"""
        try:
            response = self._make_request(
                f"/{self.business_account_id}",
                params={'fields': 'id,username,name,profile_picture_url'}
            )
            
            if response.get('error'):
                raise ValueError(f"Invalid credentials: {response['error']['message']}")
            
            logger.info(f"✅ Validated Instagram account: @{response.get('username')}")
            
        except Exception as e:
            logger.error(f"❌ Instagram credential validation failed: {e}")
            raise
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Make API request with rate limiting and error handling"""
        
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < 0.5:  # Minimum 500ms between requests
            time.sleep(0.5 - time_since_last)
        
        url = f"{self.base_url}{endpoint}"
        
        if not params:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, params=params, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            self.last_request_time = time.time()
            
            # Update rate limit info from headers
            if 'x-app-usage' in response.headers:
                usage = json.loads(response.headers['x-app-usage'])
                self.rate_limit_remaining = 100 - usage.get('call_count', 0)
            
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                logger.error(f"Instagram API error: {result['error']}")
                return {'error': result['error']}
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API request failed: {e}")
            return {'error': {'message': str(e), 'type': 'network_error'}}
        except json.JSONDecodeError as e:
            logger.error(f"Instagram API response parsing failed: {e}")
            return {'error': {'message': 'Invalid JSON response', 'type': 'parse_error'}}
    
    def post_content(self, post: InstagramPost, publish_immediately: bool = True) -> Dict[str, Any]:
        """
        Post content to Instagram
        
        Args:
            post: Instagram post data
            publish_immediately: Whether to publish immediately or schedule
            
        Returns:
            Dict containing post ID and status
        """
        try:
            # Validate post content
            validation_result = self._validate_post_content(post)
            if not validation_result['valid']:
                return {'error': validation_result['errors']}
            
            # Step 1: Create media container
            container_result = self._create_media_container(post)
            if 'error' in container_result:
                return container_result
            
            container_id = container_result['id']
            
            # Step 2: Wait for media processing (if required)
            if not self._wait_for_media_processing(container_id):
                return {'error': 'Media processing timeout'}
            
            # Step 3: Publish or schedule the media
            if publish_immediately:
                publish_result = self._publish_media(container_id)
            else:
                publish_result = self._schedule_media(container_id, post.scheduled_time)
            
            if 'error' in publish_result:
                return publish_result
            
            # Log successful post
            logger.info(f"✅ Posted to Instagram: {publish_result.get('id')}")
            
            # Add cross-promotion if configured
            if hasattr(self, 'cross_promotion_enabled') and self.cross_promotion_enabled:
                self._add_cross_promotion_story(post, publish_result['id'])
            
            return {
                'success': True,
                'post_id': publish_result['id'],
                'container_id': container_id,
                'published_at': datetime.now().isoformat(),
                'caption': post.caption[:100] + "..." if len(post.caption) > 100 else post.caption
            }
            
        except Exception as e:
            logger.error(f"Instagram posting failed: {e}")
            return {'error': {'message': str(e), 'type': 'posting_error'}}
    
    def _validate_post_content(self, post: InstagramPost) -> Dict[str, Any]:
        """Validate post content against Instagram guidelines"""
        errors = []
        
        # Caption length
        if len(post.caption) > self.content_guidelines['max_caption_length']:
            errors.append(f"Caption too long: {len(post.caption)} > {self.content_guidelines['max_caption_length']}")
        
        # Hashtag count
        if len(post.hashtags) > self.content_guidelines['max_hashtags']:
            errors.append(f"Too many hashtags: {len(post.hashtags)} > {self.content_guidelines['max_hashtags']}")
        
        # Image validation (if local file)
        if post.image_url.startswith('file://') or os.path.exists(post.image_url):
            try:
                with Image.open(post.image_url) as img:
                    width, height = img.size
                    min_size = self.content_guidelines['image_min_size']
                    max_size = self.content_guidelines['image_max_size']
                    
                    if width < min_size[0] or height < min_size[1]:
                        errors.append(f"Image too small: {width}x{height} < {min_size}")
                    
                    if width > max_size[0] or height > max_size[1]:
                        errors.append(f"Image too large: {width}x{height} > {max_size}")
                    
                    if img.format not in self.content_guidelines['supported_formats']:
                        errors.append(f"Unsupported format: {img.format}")
                        
            except Exception as e:
                errors.append(f"Image validation failed: {e}")
        
        # Content policy checks (basic)
        banned_keywords = ['nude', 'explicit', 'adult', 'xxx']  # Example list
        caption_lower = post.caption.lower()
        for keyword in banned_keywords:
            if keyword in caption_lower:
                errors.append(f"Content policy violation: contains '{keyword}'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _create_media_container(self, post: InstagramPost) -> Dict[str, Any]:
        """Create media container for Instagram post"""
        
        # Prepare caption with hashtags
        full_caption = post.caption
        if post.hashtags:
            hashtag_string = " ".join([f"#{tag.strip('#')}" for tag in post.hashtags])
            full_caption = f"{post.caption}\n\n{hashtag_string}"
        
        # Prepare parameters
        params = {
            'image_url': post.image_url,
            'caption': full_caption,
            'media_type': post.media_type
        }
        
        # Add optional parameters
        if post.location_id:
            params['location_id'] = post.location_id
        
        if post.user_tags:
            # Format user tags for Instagram API
            tags = []
            for tag in post.user_tags:
                tags.append({
                    'username': tag['username'],
                    'x': tag.get('x', 0.5),  # Default center position
                    'y': tag.get('y', 0.5)
                })
            params['user_tags'] = json.dumps(tags)
        
        return self._make_request(
            f"/{self.business_account_id}/media",
            method="POST",
            data=params
        )
    
    def _wait_for_media_processing(self, container_id: str, max_wait: int = 60) -> bool:
        """Wait for media processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = self._make_request(
                f"/{container_id}",
                params={'fields': 'status_code,status'}
            )
            
            if 'error' in status_response:
                logger.error(f"Error checking media status: {status_response['error']}")
                return False
            
            status_code = status_response.get('status_code')
            
            if status_code == 'FINISHED':
                return True
            elif status_code == 'ERROR':
                logger.error(f"Media processing failed: {status_response.get('status')}")
                return False
            elif status_code in ['IN_PROGRESS', 'PUBLISHED']:
                time.sleep(2)  # Wait 2 seconds before checking again
                continue
            else:
                logger.warning(f"Unknown status code: {status_code}")
                time.sleep(2)
        
        logger.error("Media processing timeout")
        return False
    
    def _publish_media(self, container_id: str) -> Dict[str, Any]:
        """Publish media container"""
        return self._make_request(
            f"/{self.business_account_id}/media_publish",
            method="POST",
            data={'creation_id': container_id}
        )
    
    def _schedule_media(self, container_id: str, scheduled_time: str) -> Dict[str, Any]:
        """Schedule media for later publishing"""
        # Convert scheduled_time to Unix timestamp
        try:
            dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            unix_timestamp = int(dt.timestamp())
            
            # Instagram requires scheduling at least 10 minutes in the future
            min_schedule_time = datetime.now().timestamp() + 600  # 10 minutes
            if unix_timestamp < min_schedule_time:
                return {'error': 'Scheduled time must be at least 10 minutes in the future'}
            
            return self._make_request(
                f"/{self.business_account_id}/media_publish",
                method="POST",
                data={
                    'creation_id': container_id,
                    'published': False,
                    'scheduled_publish_time': unix_timestamp
                }
            )
            
        except Exception as e:
            return {'error': f'Invalid scheduled time format: {e}'}
    
    def post_story(self, story: InstagramStory) -> Dict[str, Any]:
        """
        Post Instagram Story
        
        Args:
            story: Instagram story data
            
        Returns:
            Dict containing story ID and status
        """
        try:
            # Prepare story parameters
            params = {
                'media_type': story.media_type,
                'media_url': story.media_url if story.media_type == "IMAGE" else story.media_url
            }
            
            # Add text overlay if provided
            if story.text_overlay:
                params['caption'] = story.text_overlay
            
            # Add link sticker if provided (requires business account)
            if story.link_url:
                params['link'] = story.link_url
            
            # Create story
            response = self._make_request(
                f"/{self.business_account_id}/media",
                method="POST",
                data=params
            )
            
            if 'error' in response:
                return response
            
            container_id = response['id']
            
            # Publish story
            publish_result = self._make_request(
                f"/{self.business_account_id}/media_publish",
                method="POST",
                data={'creation_id': container_id}
            )
            
            if 'error' in publish_result:
                return publish_result
            
            logger.info(f"✅ Posted Instagram Story: {publish_result.get('id')}")
            
            return {
                'success': True,
                'story_id': publish_result['id'],
                'container_id': container_id,
                'published_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Instagram Story posting failed: {e}")
            return {'error': {'message': str(e), 'type': 'story_posting_error'}}
    
    def get_media_insights(self, media_id: str, metrics: List[str] = None) -> InstagramInsights:
        """
        Get insights for a specific media post
        
        Args:
            media_id: Instagram media ID
            metrics: List of metrics to fetch
            
        Returns:
            InstagramInsights object
        """
        if not metrics:
            metrics = [
                'impressions', 'reach', 'engagement', 'likes', 
                'comments', 'shares', 'saves'
            ]
        
        try:
            # Get basic media info
            media_info = self._make_request(
                f"/{media_id}",
                params={'fields': 'id,timestamp,like_count,comments_count'}
            )
            
            if 'error' in media_info:
                logger.error(f"Failed to get media info: {media_info['error']}")
                return None
            
            # Get insights
            insights_response = self._make_request(
                f"/{media_id}/insights",
                params={'metric': ','.join(metrics)}
            )
            
            if 'error' in insights_response:
                logger.error(f"Failed to get insights: {insights_response['error']}")
                return None
            
            # Parse insights data
            insights_data = {}
            for insight in insights_response.get('data', []):
                metric_name = insight['name']
                value = insight['values'][0]['value'] if insight['values'] else 0
                insights_data[metric_name] = value
            
            # Calculate engagement rate
            reach = insights_data.get('reach', 1)
            total_engagement = (
                insights_data.get('likes', 0) + 
                insights_data.get('comments', 0) + 
                insights_data.get('shares', 0) + 
                insights_data.get('saves', 0)
            )
            engagement_rate = (total_engagement / reach) * 100 if reach > 0 else 0
            
            return InstagramInsights(
                post_id=media_id,
                impressions=insights_data.get('impressions', 0),
                reach=insights_data.get('reach', 0),
                engagement=insights_data.get('engagement', total_engagement),
                likes=insights_data.get('likes', media_info.get('like_count', 0)),
                comments=insights_data.get('comments', media_info.get('comments_count', 0)),
                shares=insights_data.get('shares', 0),
                saves=insights_data.get('saves', 0),
                engagement_rate=round(engagement_rate, 2),
                timestamp=media_info.get('timestamp', datetime.now().isoformat())
            )
            
        except Exception as e:
            logger.error(f"Failed to get media insights: {e}")
            return None
    
    def get_account_insights(self, period: str = "day", metrics: List[str] = None) -> Dict[str, Any]:
        """
        Get account-level insights
        
        Args:
            period: Time period ('day', 'week', 'days_28')
            metrics: List of metrics to fetch
            
        Returns:
            Dict containing account insights
        """
        if not metrics:
            metrics = [
                'impressions', 'reach', 'profile_views', 
                'website_clicks', 'follower_count'
            ]
        
        try:
            response = self._make_request(
                f"/{self.business_account_id}/insights",
                params={
                    'metric': ','.join(metrics),
                    'period': period
                }
            )
            
            if 'error' in response:
                return {'error': response['error']}
            
            # Parse insights
            insights = {}
            for insight in response.get('data', []):
                metric_name = insight['name']
                values = insight.get('values', [])
                if values:
                    insights[metric_name] = values[-1]['value']  # Latest value
                else:
                    insights[metric_name] = 0
            
            return {
                'success': True,
                'period': period,
                'insights': insights,
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get account insights: {e}")
            return {'error': {'message': str(e), 'type': 'insights_error'}}
    
    def get_recent_media(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get recent media posts"""
        try:
            response = self._make_request(
                f"/{self.business_account_id}/media",
                params={
                    'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp,like_count,comments_count',
                    'limit': limit
                }
            )
            
            if 'error' in response:
                return []
            
            return response.get('data', [])
            
        except Exception as e:
            logger.error(f"Failed to get recent media: {e}")
            return []
    
    def create_cross_promotion_story(self, main_post_id: str, platform_name: str, platform_url: str) -> Dict[str, Any]:
        """
        Create a cross-promotion story to drive traffic to other platforms
        
        Args:
            main_post_id: ID of the main post to promote
            platform_name: Name of the platform to promote (e.g., "FanVue", "LoyalFans")
            platform_url: URL to link to
            
        Returns:
            Dict containing story creation result
        """
        try:
            # Get the original post for context
            main_post = self._make_request(
                f"/{main_post_id}",
                params={'fields': 'media_url,caption'}
            )
            
            if 'error' in main_post:
                return main_post
            
            # Create promotional story content
            promo_text = f"🔥 New content alert! More exclusive content on {platform_name}"
            
            story = InstagramStory(
                media_url=main_post['media_url'],
                media_type="IMAGE",
                text_overlay=promo_text,
                link_url=platform_url
            )
            
            return self.post_story(story)
            
        except Exception as e:
            logger.error(f"Cross-promotion story creation failed: {e}")
            return {'error': {'message': str(e), 'type': 'cross_promotion_error'}}
    
    def _add_cross_promotion_story(self, original_post: InstagramPost, post_id: str):
        """Add cross-promotion story after successful post"""
        try:
            # Example cross-promotion URLs (would be configured)
            promo_urls = {
                'fanvue': 'https://fanvue.com/fionasparx',
                'loyalfans': 'https://loyalfans.com/fionasparx'
            }
            
            # Create promotional story for each platform
            for platform, url in promo_urls.items():
                self.create_cross_promotion_story(post_id, platform.title(), url)
                time.sleep(5)  # Space out story posts
                
        except Exception as e:
            logger.warning(f"Cross-promotion failed: {e}")
    
    def analyze_hashtag_performance(self, hashtags: List[str], days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze hashtag performance based on recent posts
        
        Args:
            hashtags: List of hashtags to analyze
            days_back: Number of days to look back
            
        Returns:
            Dict containing hashtag performance analysis
        """
        try:
            # Get recent posts
            recent_media = self.get_recent_media(limit=50)
            
            # Filter posts from the specified time period
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filtered_media = []
            
            for media in recent_media:
                post_date = datetime.fromisoformat(media['timestamp'].replace('Z', '+00:00'))
                if post_date >= cutoff_date:
                    filtered_media.append(media)
            
            # Analyze hashtag performance
            hashtag_stats = {}
            
            for hashtag in hashtags:
                hashtag_clean = hashtag.strip('#').lower()
                posts_with_hashtag = []
                
                for media in filtered_media:
                    caption = media.get('caption', '').lower()
                    if f"#{hashtag_clean}" in caption:
                        posts_with_hashtag.append(media)
                
                if posts_with_hashtag:
                    total_likes = sum(post.get('like_count', 0) for post in posts_with_hashtag)
                    total_comments = sum(post.get('comments_count', 0) for post in posts_with_hashtag)
                    avg_engagement = (total_likes + total_comments) / len(posts_with_hashtag)
                    
                    hashtag_stats[hashtag] = {
                        'usage_count': len(posts_with_hashtag),
                        'avg_engagement': round(avg_engagement, 2),
                        'total_likes': total_likes,
                        'total_comments': total_comments
                    }
                else:
                    hashtag_stats[hashtag] = {
                        'usage_count': 0,
                        'avg_engagement': 0,
                        'total_likes': 0,
                        'total_comments': 0
                    }
            
            # Sort by performance
            sorted_hashtags = sorted(
                hashtag_stats.items(),
                key=lambda x: x[1]['avg_engagement'],
                reverse=True
            )
            
            return {
                'success': True,
                'analysis_period_days': days_back,
                'hashtag_performance': dict(sorted_hashtags),
                'top_performing': [tag[0] for tag in sorted_hashtags[:5]],
                'recommendations': self._generate_hashtag_recommendations(hashtag_stats)
            }
            
        except Exception as e:
            logger.error(f"Hashtag analysis failed: {e}")
            return {'error': {'message': str(e), 'type': 'hashtag_analysis_error'}}
    
    def _generate_hashtag_recommendations(self, hashtag_stats: Dict[str, Dict]) -> List[str]:
        """Generate hashtag recommendations based on performance"""
        recommendations = []
        
        # Find high-performing hashtags
        high_performers = [
            tag for tag, stats in hashtag_stats.items()
            if stats['avg_engagement'] > 50 and stats['usage_count'] > 1
        ]
        
        if high_performers:
            recommendations.append(f"Continue using high-performing hashtags: {', '.join(high_performers[:3])}")
        
        # Find underused hashtags
        low_usage = [
            tag for tag, stats in hashtag_stats.items()
            if stats['usage_count'] == 0
        ]
        
        if low_usage:
            recommendations.append(f"Consider removing unused hashtags: {', '.join(low_usage[:3])}")
        
        # General recommendations
        recommendations.extend([
            "Mix popular and niche hashtags for better reach",
            "Research trending hashtags in your niche",
            "Keep hashtags relevant to your content"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_optimal_posting_times(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze optimal posting times based on engagement patterns
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dict containing optimal posting time analysis
        """
        try:
            # Get recent posts with insights
            recent_media = self.get_recent_media(limit=100)
            
            # Filter by date and get engagement data
            cutoff_date = datetime.now() - timedelta(days=days_back)
            engagement_by_hour = {}
            engagement_by_day = {}
            
            for media in recent_media:
                post_date = datetime.fromisoformat(media['timestamp'].replace('Z', '+00:00'))
                if post_date >= cutoff_date:
                    hour = post_date.hour
                    day = post_date.strftime('%A')
                    
                    engagement = media.get('like_count', 0) + media.get('comments_count', 0)
                    
                    # Track by hour
                    if hour not in engagement_by_hour:
                        engagement_by_hour[hour] = []
                    engagement_by_hour[hour].append(engagement)
                    
                    # Track by day
                    if day not in engagement_by_day:
                        engagement_by_day[day] = []
                    engagement_by_day[day].append(engagement)
            
            # Calculate averages
            avg_by_hour = {
                hour: sum(engagements) / len(engagements)
                for hour, engagements in engagement_by_hour.items()
            }
            
            avg_by_day = {
                day: sum(engagements) / len(engagements)
                for day, engagements in engagement_by_day.items()
            }
            
            # Find optimal times
            best_hours = sorted(avg_by_hour.items(), key=lambda x: x[1], reverse=True)[:5]
            best_days = sorted(avg_by_day.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'success': True,
                'analysis_period_days': days_back,
                'optimal_hours': [{'hour': hour, 'avg_engagement': eng} for hour, eng in best_hours],
                'optimal_days': [{'day': day, 'avg_engagement': eng} for day, eng in best_days],
                'recommendations': [
                    f"Best posting hour: {best_hours[0][0]}:00" if best_hours else "Need more data",
                    f"Best posting day: {best_days[0][0]}" if best_days else "Need more data",
                    "Consider posting when your audience is most active"
                ]
            }
            
        except Exception as e:
            logger.error(f"Optimal timing analysis failed: {e}")
            return {'error': {'message': str(e), 'type': 'timing_analysis_error'}}
    
    def delete_media(self, media_id: str) -> Dict[str, Any]:
        """Delete a media post"""
        try:
            response = self._make_request(f"/{media_id}", method="DELETE")
            
            if 'error' in response:
                return response
            
            logger.info(f"✅ Deleted Instagram media: {media_id}")
            return {'success': True, 'deleted_id': media_id}
            
        except Exception as e:
            logger.error(f"Media deletion failed: {e}")
            return {'error': {'message': str(e), 'type': 'deletion_error'}}
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        return {
            'remaining_calls': self.rate_limit_remaining,
            'reset_time': self.rate_limit_reset.isoformat(),
            'last_request': self.last_request_time
        }

# Example usage and testing
if __name__ == "__main__":
    # Example configuration (use environment variables in production)
    ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "your_access_token")
    BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "your_account_id")
    
    # Initialize Instagram API
    instagram = InstagramAPI(ACCESS_TOKEN, BUSINESS_ACCOUNT_ID)
    
    # Example post
    post = InstagramPost(
        caption="Living my best life and sharing authentic moments with you! 💫 What's making you smile today?",
        image_url="https://example.com/image.jpg",
        hashtags=["lifestyle", "authentic", "positive", "dailylife", "motivation"]
    )
    
    # Post content (commented out for safety)
    # result = instagram.post_content(post)
    # print("Post result:", json.dumps(result, indent=2))
    
    # Get account insights
    insights = instagram.get_account_insights()
    print("Account insights:", json.dumps(insights, indent=2))
    
    # Analyze optimal posting times
    timing = instagram.get_optimal_posting_times()
    print("Optimal timing:", json.dumps(timing, indent=2))
    
    print("✅ Instagram API test completed")