#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter API v2 Integration for FionaSparx

This module provides comprehensive Twitter API v2 integration for:
- Content posting and threading
- Tweet scheduling
- Analytics and insights
- Cross-promotion to drive traffic to premium platforms
- Engagement tracking and analysis

Features:
- Automated posting with optimal timing
- Thread creation for longer content
- Media upload (images/videos)
- Engagement analytics
- Cross-platform promotion
- Compliance with Twitter policies

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
import hashlib
import hmac
import base64
from urllib.parse import urlencode
import mimetypes

logger = logging.getLogger(__name__)

@dataclass
class TwitterTweet:
    """Twitter tweet data structure"""
    text: str
    media_ids: Optional[List[str]] = None
    reply_to_tweet_id: Optional[str] = None
    quote_tweet_id: Optional[str] = None
    poll_options: Optional[List[str]] = None
    poll_duration_minutes: Optional[int] = None
    geo_place_id: Optional[str] = None
    tagged_user_ids: Optional[List[str]] = None

@dataclass
class TwitterThread:
    """Twitter thread data structure"""
    tweets: List[str]
    media_ids: Optional[List[str]] = None
    first_tweet_media: bool = True

@dataclass
class TwitterAnalytics:
    """Twitter analytics data"""
    tweet_id: str
    impressions: int
    engagements: int
    likes: int
    retweets: int
    replies: int
    profile_clicks: int
    url_clicks: int
    hashtag_clicks: int
    detail_expands: int
    engagement_rate: float
    timestamp: str

class TwitterAPI:
    """
    Twitter API v2 integration for content posting and analytics
    """
    
    def __init__(self, bearer_token: str, api_key: str = None, api_secret: str = None, 
                 access_token: str = None, access_token_secret: str = None):
        """
        Initialize Twitter API client
        
        Args:
            bearer_token: Twitter Bearer Token for API v2
            api_key: Twitter API Key (for OAuth 1.0a operations)
            api_secret: Twitter API Secret
            access_token: Twitter Access Token
            access_token_secret: Twitter Access Token Secret
        """
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        self.base_url = "https://api.twitter.com/2"
        self.upload_url = "https://upload.twitter.com/1.1"
        
        # Rate limiting
        self.rate_limits = {
            'tweets': {'remaining': 300, 'reset': datetime.now()},
            'upload': {'remaining': 300, 'reset': datetime.now()},
            'lookup': {'remaining': 900, 'reset': datetime.now()}
        }
        
        # Content guidelines for Twitter
        self.content_guidelines = {
            'max_tweet_length': 280,
            'max_media_per_tweet': 4,
            'max_thread_length': 25,
            'supported_media_formats': ['JPEG', 'PNG', 'GIF', 'WEBP', 'MP4', 'MOV'],
            'max_image_size_mb': 5,
            'max_video_size_mb': 512
        }
        
        self._validate_credentials()
        logger.info("✅ Twitter API client initialized")
    
    def _validate_credentials(self):
        """Validate API credentials"""
        try:
            response = self._make_request(
                "/users/me",
                params={'user.fields': 'id,name,username,public_metrics'}
            )
            
            if 'errors' in response:
                raise ValueError(f"Invalid credentials: {response['errors'][0]['message']}")
            
            user_data = response.get('data', {})
            logger.info(f"✅ Validated Twitter account: @{user_data.get('username')}")
            
        except Exception as e:
            logger.error(f"❌ Twitter credential validation failed: {e}")
            raise
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, 
                     data: Dict = None, files: Dict = None, use_oauth1: bool = False) -> Dict[str, Any]:
        """Make API request with authentication and rate limiting"""
        
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        # Choose authentication method
        if use_oauth1 and self.api_key:
            # OAuth 1.0a for certain operations (like media upload)
            headers.update(self._get_oauth1_headers(method, url, params or {}))
        else:
            # Bearer token for API v2
            headers['Authorization'] = f"Bearer {self.bearer_token}"
        
        headers['Content-Type'] = 'application/json'
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                if files:
                    # For file uploads, don't set Content-Type
                    del headers['Content-Type']
                    response = requests.post(url, headers=headers, params=params, files=files, timeout=60)
                else:
                    response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Update rate limit info from headers
            self._update_rate_limits(response.headers, endpoint)
            
            response.raise_for_status()
            result = response.json()
            
            if 'errors' in result:
                logger.error(f"Twitter API error: {result['errors']}")
                return {'error': result['errors']}
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter API request failed: {e}")
            return {'error': {'message': str(e), 'type': 'network_error'}}
        except json.JSONDecodeError as e:
            logger.error(f"Twitter API response parsing failed: {e}")
            return {'error': {'message': 'Invalid JSON response', 'type': 'parse_error'}}
    
    def _get_oauth1_headers(self, method: str, url: str, params: Dict) -> Dict[str, str]:
        """Generate OAuth 1.0a headers for authenticated requests"""
        import secrets
        import urllib.parse
        
        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_token': self.access_token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': secrets.token_urlsafe(16),
            'oauth_version': '1.0'
        }
        
        # Create signature base string
        all_params = {**oauth_params, **params}
        param_string = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted(all_params.items())])
        base_string = f"{method.upper()}&{urllib.parse.quote(url)}&{urllib.parse.quote(param_string)}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(self.api_secret)}&{urllib.parse.quote(self.access_token_secret or '')}"
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()
        
        oauth_params['oauth_signature'] = signature
        
        # Create Authorization header
        auth_header = 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(str(v))}"' for k, v in oauth_params.items()])
        
        return {'Authorization': auth_header}
    
    def _update_rate_limits(self, headers: Dict, endpoint: str):
        """Update rate limit information from response headers"""
        if 'x-rate-limit-remaining' in headers:
            remaining = int(headers['x-rate-limit-remaining'])
            reset_time = datetime.fromtimestamp(int(headers.get('x-rate-limit-reset', time.time())))
            
            # Determine endpoint category
            if '/tweets' in endpoint:
                self.rate_limits['tweets'] = {'remaining': remaining, 'reset': reset_time}
            elif '/upload' in endpoint:
                self.rate_limits['upload'] = {'remaining': remaining, 'reset': reset_time}
            else:
                self.rate_limits['lookup'] = {'remaining': remaining, 'reset': reset_time}
    
    def post_tweet(self, tweet: TwitterTweet) -> Dict[str, Any]:
        """
        Post a tweet
        
        Args:
            tweet: TwitterTweet object with content and options
            
        Returns:
            Dict containing tweet ID and status
        """
        try:
            # Validate tweet content
            validation_result = self._validate_tweet_content(tweet)
            if not validation_result['valid']:
                return {'error': validation_result['errors']}
            
            # Prepare tweet data
            tweet_data = {
                'text': tweet.text
            }
            
            # Add optional parameters
            if tweet.media_ids:
                tweet_data['media'] = {'media_ids': tweet.media_ids}
            
            if tweet.reply_to_tweet_id:
                tweet_data['reply'] = {'in_reply_to_tweet_id': tweet.reply_to_tweet_id}
            
            if tweet.quote_tweet_id:
                tweet_data['quote_tweet_id'] = tweet.quote_tweet_id
            
            if tweet.poll_options:
                tweet_data['poll'] = {
                    'options': tweet.poll_options,
                    'duration_minutes': tweet.poll_duration_minutes or 1440  # 24 hours default
                }
            
            if tweet.geo_place_id:
                tweet_data['geo'] = {'place_id': tweet.geo_place_id}
            
            if tweet.tagged_user_ids:
                tweet_data['user'] = {'tagged_user_ids': tweet.tagged_user_ids}
            
            # Post tweet
            response = self._make_request("/tweets", method="POST", data=tweet_data)
            
            if 'error' in response:
                return response
            
            tweet_data = response.get('data', {})
            logger.info(f"✅ Posted tweet: {tweet_data.get('id')}")
            
            return {
                'success': True,
                'tweet_id': tweet_data.get('id'),
                'text': tweet_data.get('text'),
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twitter posting failed: {e}")
            return {'error': {'message': str(e), 'type': 'posting_error'}}
    
    def _validate_tweet_content(self, tweet: TwitterTweet) -> Dict[str, Any]:
        """Validate tweet content against Twitter guidelines"""
        errors = []
        
        # Text length
        if len(tweet.text) > self.content_guidelines['max_tweet_length']:
            errors.append(f"Tweet too long: {len(tweet.text)} > {self.content_guidelines['max_tweet_length']}")
        
        if not tweet.text.strip():
            errors.append("Tweet text cannot be empty")
        
        # Media count
        if tweet.media_ids and len(tweet.media_ids) > self.content_guidelines['max_media_per_tweet']:
            errors.append(f"Too many media items: {len(tweet.media_ids)} > {self.content_guidelines['max_media_per_tweet']}")
        
        # Poll validation
        if tweet.poll_options:
            if len(tweet.poll_options) < 2 or len(tweet.poll_options) > 4:
                errors.append("Poll must have 2-4 options")
            
            if any(len(option) > 25 for option in tweet.poll_options):
                errors.append("Poll options must be 25 characters or less")
        
        # Content policy checks (basic)
        banned_keywords = ['spam', 'fake', 'scam']  # Example list
        text_lower = tweet.text.lower()
        for keyword in banned_keywords:
            if keyword in text_lower:
                errors.append(f"Content policy violation: contains '{keyword}'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def post_thread(self, thread: TwitterThread) -> Dict[str, Any]:
        """
        Post a Twitter thread
        
        Args:
            thread: TwitterThread object with multiple tweets
            
        Returns:
            Dict containing thread information and tweet IDs
        """
        try:
            if len(thread.tweets) > self.content_guidelines['max_thread_length']:
                return {'error': f"Thread too long: {len(thread.tweets)} > {self.content_guidelines['max_thread_length']}"}
            
            thread_results = []
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(thread.tweets):
                # Create tweet object
                tweet = TwitterTweet(text=tweet_text)
                
                # Add media to first tweet if specified
                if i == 0 and thread.first_tweet_media and thread.media_ids:
                    tweet.media_ids = thread.media_ids
                
                # Set reply relationship for threading
                if previous_tweet_id:
                    tweet.reply_to_tweet_id = previous_tweet_id
                
                # Post tweet
                result = self.post_tweet(tweet)
                
                if result.get('success'):
                    tweet_id = result['tweet_id']
                    thread_results.append({
                        'tweet_number': i + 1,
                        'tweet_id': tweet_id,
                        'text': tweet_text[:50] + "..." if len(tweet_text) > 50 else tweet_text
                    })
                    previous_tweet_id = tweet_id
                else:
                    # Thread posting failed
                    return {
                        'error': f"Thread posting failed at tweet {i + 1}: {result.get('error', {}).get('message', 'Unknown error')}",
                        'partial_thread': thread_results
                    }
                
                # Brief delay between tweets to avoid rate limiting
                if i < len(thread.tweets) - 1:
                    time.sleep(1)
            
            logger.info(f"✅ Posted Twitter thread with {len(thread_results)} tweets")
            
            return {
                'success': True,
                'thread_id': thread_results[0]['tweet_id'] if thread_results else None,
                'tweets': thread_results,
                'total_tweets': len(thread_results),
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twitter thread posting failed: {e}")
            return {'error': {'message': str(e), 'type': 'thread_posting_error'}}
    
    def upload_media(self, media_path: str, media_type: str = "image") -> Dict[str, Any]:
        """
        Upload media to Twitter
        
        Args:
            media_path: Path to media file
            media_type: Type of media ('image' or 'video')
            
        Returns:
            Dict containing media ID and upload status
        """
        try:
            if not os.path.exists(media_path):
                return {'error': 'Media file not found'}
            
            # Validate file
            file_size = os.path.getsize(media_path)
            max_size_mb = self.content_guidelines['max_video_size_mb'] if media_type == 'video' else self.content_guidelines['max_image_size_mb']
            
            if file_size > max_size_mb * 1024 * 1024:
                return {'error': f'File too large: {file_size / (1024*1024):.1f}MB > {max_size_mb}MB'}
            
            # Determine media category
            media_category = "tweet_image" if media_type == "image" else "tweet_video"
            
            # Upload media
            with open(media_path, 'rb') as media_file:
                files = {'media': media_file}
                data = {'media_category': media_category}
                
                # Use Twitter v1.1 upload endpoint
                upload_url = f"{self.upload_url}/media/upload.json"
                
                response = requests.post(
                    upload_url,
                    files=files,
                    data=data,
                    headers=self._get_oauth1_headers('POST', upload_url, data),
                    timeout=120
                )
                
                response.raise_for_status()
                result = response.json()
                
                if 'media_id' in result:
                    logger.info(f"✅ Uploaded media: {result['media_id']}")
                    return {
                        'success': True,
                        'media_id': str(result['media_id']),
                        'media_type': media_type,
                        'file_size': file_size
                    }
                else:
                    return {'error': 'Media upload failed - no media ID returned'}
                    
        except Exception as e:
            logger.error(f"Media upload failed: {e}")
            return {'error': {'message': str(e), 'type': 'upload_error'}}
    
    def get_tweet_analytics(self, tweet_id: str) -> TwitterAnalytics:
        """
        Get analytics for a specific tweet
        
        Args:
            tweet_id: Twitter tweet ID
            
        Returns:
            TwitterAnalytics object
        """
        try:
            # Get tweet with metrics
            response = self._make_request(
                f"/tweets/{tweet_id}",
                params={
                    'tweet.fields': 'created_at,public_metrics,non_public_metrics,promoted_metrics',
                    'expansions': 'author_id'
                }
            )
            
            if 'error' in response:
                logger.error(f"Failed to get tweet analytics: {response['error']}")
                return None
            
            tweet_data = response.get('data', {})
            public_metrics = tweet_data.get('public_metrics', {})
            non_public_metrics = tweet_data.get('non_public_metrics', {})
            
            # Calculate engagement rate
            impressions = non_public_metrics.get('impression_count', 0)
            engagements = (
                public_metrics.get('like_count', 0) +
                public_metrics.get('retweet_count', 0) +
                public_metrics.get('reply_count', 0) +
                public_metrics.get('quote_count', 0)
            )
            
            engagement_rate = (engagements / impressions * 100) if impressions > 0 else 0
            
            return TwitterAnalytics(
                tweet_id=tweet_id,
                impressions=impressions,
                engagements=engagements,
                likes=public_metrics.get('like_count', 0),
                retweets=public_metrics.get('retweet_count', 0),
                replies=public_metrics.get('reply_count', 0),
                profile_clicks=non_public_metrics.get('profile_clicks', 0),
                url_clicks=non_public_metrics.get('url_link_clicks', 0),
                hashtag_clicks=non_public_metrics.get('hashtag_clicks', 0),
                detail_expands=non_public_metrics.get('detail_expands', 0),
                engagement_rate=round(engagement_rate, 2),
                timestamp=tweet_data.get('created_at', datetime.now().isoformat())
            )
            
        except Exception as e:
            logger.error(f"Failed to get tweet analytics: {e}")
            return None
    
    def get_user_analytics(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get user-level analytics
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dict containing user analytics
        """
        try:
            # Get user info
            user_response = self._make_request(
                "/users/me",
                params={'user.fields': 'public_metrics,created_at'}
            )
            
            if 'error' in user_response:
                return {'error': user_response['error']}
            
            user_data = user_response.get('data', {})
            public_metrics = user_data.get('public_metrics', {})
            
            # Get recent tweets for engagement analysis
            tweets_response = self._make_request(
                "/users/me/tweets",
                params={
                    'tweet.fields': 'created_at,public_metrics',
                    'max_results': 100,
                    'start_time': (datetime.now() - timedelta(days=days_back)).isoformat()
                }
            )
            
            tweets_data = tweets_response.get('data', [])
            
            # Calculate analytics
            total_tweets = len(tweets_data)
            total_likes = sum(tweet.get('public_metrics', {}).get('like_count', 0) for tweet in tweets_data)
            total_retweets = sum(tweet.get('public_metrics', {}).get('retweet_count', 0) for tweet in tweets_data)
            total_replies = sum(tweet.get('public_metrics', {}).get('reply_count', 0) for tweet in tweets_data)
            
            avg_engagement = (total_likes + total_retweets + total_replies) / max(total_tweets, 1)
            
            return {
                'success': True,
                'user_metrics': {
                    'followers_count': public_metrics.get('followers_count', 0),
                    'following_count': public_metrics.get('following_count', 0),
                    'tweet_count': public_metrics.get('tweet_count', 0),
                    'listed_count': public_metrics.get('listed_count', 0)
                },
                'period_analytics': {
                    'period_days': days_back,
                    'tweets_posted': total_tweets,
                    'total_likes': total_likes,
                    'total_retweets': total_retweets,
                    'total_replies': total_replies,
                    'avg_engagement_per_tweet': round(avg_engagement, 2)
                },
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {'error': {'message': str(e), 'type': 'analytics_error'}}
    
    def create_cross_promotion_tweet(self, platform_name: str, platform_url: str, content_preview: str = None) -> Dict[str, Any]:
        """
        Create a cross-promotion tweet to drive traffic to other platforms
        
        Args:
            platform_name: Name of the platform to promote
            platform_url: URL to link to
            content_preview: Preview of the content
            
        Returns:
            Dict containing tweet creation result
        """
        try:
            # Create promotional tweet text
            if content_preview:
                tweet_text = f"💫 Just dropped new exclusive content! {content_preview[:100]}... Check it out on {platform_name}! 🔥"
            else:
                tweet_text = f"🔥 New exclusive content alert! More premium content available on {platform_name} 💖"
            
            # Add link if it fits
            if len(tweet_text) + len(platform_url) + 1 <= self.content_guidelines['max_tweet_length']:
                tweet_text += f"\n{platform_url}"
            
            # Create and post tweet
            tweet = TwitterTweet(text=tweet_text)
            return self.post_tweet(tweet)
            
        except Exception as e:
            logger.error(f"Cross-promotion tweet creation failed: {e}")
            return {'error': {'message': str(e), 'type': 'cross_promotion_error'}}
    
    def analyze_hashtag_performance(self, hashtags: List[str], days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze hashtag performance based on recent tweets
        
        Args:
            hashtags: List of hashtags to analyze
            days_back: Number of days to look back
            
        Returns:
            Dict containing hashtag performance analysis
        """
        try:
            # Get recent tweets
            tweets_response = self._make_request(
                "/users/me/tweets",
                params={
                    'tweet.fields': 'created_at,public_metrics,text',
                    'max_results': 100,
                    'start_time': (datetime.now() - timedelta(days=days_back)).isoformat()
                }
            )
            
            tweets_data = tweets_response.get('data', [])
            
            # Analyze hashtag performance
            hashtag_stats = {}
            
            for hashtag in hashtags:
                hashtag_clean = hashtag.strip('#').lower()
                tweets_with_hashtag = []
                
                for tweet in tweets_data:
                    tweet_text = tweet.get('text', '').lower()
                    if f"#{hashtag_clean}" in tweet_text:
                        tweets_with_hashtag.append(tweet)
                
                if tweets_with_hashtag:
                    total_likes = sum(tweet.get('public_metrics', {}).get('like_count', 0) for tweet in tweets_with_hashtag)
                    total_retweets = sum(tweet.get('public_metrics', {}).get('retweet_count', 0) for tweet in tweets_with_hashtag)
                    total_replies = sum(tweet.get('public_metrics', {}).get('reply_count', 0) for tweet in tweets_with_hashtag)
                    avg_engagement = (total_likes + total_retweets + total_replies) / len(tweets_with_hashtag)
                    
                    hashtag_stats[hashtag] = {
                        'usage_count': len(tweets_with_hashtag),
                        'avg_engagement': round(avg_engagement, 2),
                        'total_likes': total_likes,
                        'total_retweets': total_retweets,
                        'total_replies': total_replies
                    }
                else:
                    hashtag_stats[hashtag] = {
                        'usage_count': 0,
                        'avg_engagement': 0,
                        'total_likes': 0,
                        'total_retweets': 0,
                        'total_replies': 0
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
            if stats['avg_engagement'] > 10 and stats['usage_count'] > 1
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
            "Use trending hashtags relevant to your niche",
            "Mix popular and niche hashtags for better reach",
            "Monitor hashtag performance regularly"
        ])
        
        return recommendations[:5]
    
    def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Delete a tweet"""
        try:
            response = self._make_request(f"/tweets/{tweet_id}", method="DELETE")
            
            if 'error' in response:
                return response
            
            logger.info(f"✅ Deleted tweet: {tweet_id}")
            return {'success': True, 'deleted_id': tweet_id}
            
        except Exception as e:
            logger.error(f"Tweet deletion failed: {e}")
            return {'error': {'message': str(e), 'type': 'deletion_error'}}
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        return {
            'rate_limits': {
                endpoint: {
                    'remaining': info['remaining'],
                    'reset_time': info['reset'].isoformat()
                }
                for endpoint, info in self.rate_limits.items()
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Example configuration (use environment variables in production)
    BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "your_bearer_token")
    API_KEY = os.getenv("TWITTER_API_KEY", "your_api_key")
    API_SECRET = os.getenv("TWITTER_API_SECRET", "your_api_secret")
    ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "your_access_token")
    ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "your_access_token_secret")
    
    # Initialize Twitter API
    twitter = TwitterAPI(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    # Example tweet
    tweet = TwitterTweet(
        text="Living my best life and sharing authentic moments with you! 💫 What's inspiring you today? #lifestyle #authentic #positive"
    )
    
    # Post tweet (commented out for safety)
    # result = twitter.post_tweet(tweet)
    # print("Tweet result:", json.dumps(result, indent=2))
    
    # Get user analytics
    analytics = twitter.get_user_analytics()
    print("User analytics:", json.dumps(analytics, indent=2))
    
    # Analyze hashtag performance
    hashtags = ["lifestyle", "authentic", "positive", "motivation", "content"]
    hashtag_analysis = twitter.analyze_hashtag_performance(hashtags)
    print("Hashtag analysis:", json.dumps(hashtag_analysis, indent=2))
    
    print("✅ Twitter API test completed")