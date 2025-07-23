"""
Webhook System for N8N Automation

This module provides webhook endpoints for triggering automation workflows
and receiving external events from social media platforms and other services.

Key Features:
- HTTP webhook endpoints
- Event processing and routing
- Authentication and security
- Rate limiting and throttling
- Event logging and monitoring
"""

import logging
import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

class WebhookMethod(Enum):
    """HTTP methods supported by webhooks"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class EventType(Enum):
    """Types of events that can trigger workflows"""
    SOCIAL_MEDIA_POST = "social_media_post"
    ENGAGEMENT_UPDATE = "engagement_update"
    REVENUE_EVENT = "revenue_event"
    SYSTEM_ALERT = "system_alert"
    CONTENT_REQUEST = "content_request"
    SCHEDULE_TRIGGER = "schedule_trigger"
    MANUAL_TRIGGER = "manual_trigger"

@dataclass
class WebhookEndpoint:
    """Definition of a webhook endpoint"""
    id: str
    path: str
    method: WebhookMethod
    event_type: EventType
    handler: Callable
    auth_required: bool = True
    rate_limit: int = 100  # requests per minute
    secret: Optional[str] = None

@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    endpoint_id: str
    event_type: EventType
    timestamp: datetime
    headers: Dict[str, str]
    body: Dict[str, Any]
    source_ip: str
    authenticated: bool = False

class WebhookServer:
    """
    HTTP Webhook Server for N8N Automation
    
    Handles incoming webhook requests and routes them to appropriate
    workflow triggers and event handlers.
    """
    
    def __init__(self, master_controller, config: Dict = None):
        self.master_controller = master_controller
        self.config = config or {}
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.rate_limits: Dict[str, List[float]] = {}  # IP -> [timestamp, ...]
        self.server = None
        
        logger.info("🔗 Webhook Server initialized")
        self._setup_default_endpoints()
    
    def _setup_default_endpoints(self):
        """Setup default webhook endpoints"""
        default_endpoints = [
            WebhookEndpoint(
                id="content_generation_trigger",
                path="/webhooks/generate-content",
                method=WebhookMethod.POST,
                event_type=EventType.CONTENT_REQUEST,
                handler=self._handle_content_generation
            ),
            WebhookEndpoint(
                id="engagement_update",
                path="/webhooks/engagement",
                method=WebhookMethod.POST,
                event_type=EventType.ENGAGEMENT_UPDATE,
                handler=self._handle_engagement_update
            ),
            WebhookEndpoint(
                id="revenue_event",
                path="/webhooks/revenue",
                method=WebhookMethod.POST,
                event_type=EventType.REVENUE_EVENT,
                handler=self._handle_revenue_event
            ),
            WebhookEndpoint(
                id="system_alert",
                path="/webhooks/alert",
                method=WebhookMethod.POST,
                event_type=EventType.SYSTEM_ALERT,
                handler=self._handle_system_alert
            ),
            WebhookEndpoint(
                id="manual_trigger",
                path="/webhooks/trigger/<workflow_id>",
                method=WebhookMethod.POST,
                event_type=EventType.MANUAL_TRIGGER,
                handler=self._handle_manual_trigger
            ),
            WebhookEndpoint(
                id="health_check",
                path="/webhooks/health",
                method=WebhookMethod.GET,
                event_type=EventType.SYSTEM_ALERT,
                handler=self._handle_health_check,
                auth_required=False
            )
        ]
        
        for endpoint in default_endpoints:
            self.register_endpoint(endpoint)
        
        logger.info(f"✅ Registered {len(default_endpoints)} webhook endpoints")
    
    def register_endpoint(self, endpoint: WebhookEndpoint):
        """Register a new webhook endpoint"""
        self.endpoints[endpoint.path] = endpoint
        logger.info(f"📝 Registered webhook: {endpoint.method.value} {endpoint.path}")
    
    async def start_server(self, host: str = "localhost", port: int = 8080):
        """Start the webhook server"""
        logger.info(f"🚀 Starting webhook server on {host}:{port}")
        
        # In a real implementation, we would use a proper HTTP framework like FastAPI or aiohttp
        # For this minimal implementation, we'll simulate the server
        self.server = {
            "host": host,
            "port": port,
            "running": True,
            "start_time": datetime.now()
        }
        
        logger.info(f"✅ Webhook server started on {host}:{port}")
        return self.server
    
    async def stop_server(self):
        """Stop the webhook server"""
        if self.server:
            self.server["running"] = False
            logger.info("⏹️ Webhook server stopped")
    
    async def handle_request(self, method: str, path: str, headers: Dict, body: str, source_ip: str) -> Dict:
        """Handle incoming webhook request"""
        event_id = f"evt_{int(time.time() * 1000)}"
        
        # Find matching endpoint
        endpoint = self._find_endpoint(method, path)
        if not endpoint:
            return {
                "status": 404,
                "error": "Endpoint not found",
                "event_id": event_id
            }
        
        # Rate limiting
        if not self._check_rate_limit(source_ip, endpoint):
            return {
                "status": 429,
                "error": "Rate limit exceeded",
                "event_id": event_id
            }
        
        # Parse body
        try:
            parsed_body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed_body = {"raw": body}
        
        # Create event
        event = WebhookEvent(
            event_id=event_id,
            endpoint_id=endpoint.id,
            event_type=endpoint.event_type,
            timestamp=datetime.now(),
            headers=headers,
            body=parsed_body,
            source_ip=source_ip
        )
        
        # Authentication
        if endpoint.auth_required:
            if not self._authenticate_request(endpoint, headers, body):
                return {
                    "status": 401,
                    "error": "Authentication failed",
                    "event_id": event_id
                }
            event.authenticated = True
        
        # Handle the event
        try:
            result = await endpoint.handler(event)
            
            logger.info(f"✅ Webhook event processed: {event_id}")
            
            return {
                "status": 200,
                "event_id": event_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Webhook event failed: {event_id} - {e}")
            
            return {
                "status": 500,
                "error": str(e),
                "event_id": event_id
            }
    
    def _find_endpoint(self, method: str, path: str) -> Optional[WebhookEndpoint]:
        """Find matching endpoint for request"""
        for endpoint_path, endpoint in self.endpoints.items():
            if endpoint.method.value == method:
                # Simple path matching (in production, use proper URL routing)
                if endpoint_path == path or self._path_matches(endpoint_path, path):
                    return endpoint
        return None
    
    def _path_matches(self, pattern: str, path: str) -> bool:
        """Check if path matches pattern with wildcards"""
        # Simple wildcard matching for patterns like /webhooks/trigger/<workflow_id>
        if "<" in pattern and ">" in pattern:
            # Extract the pattern parts
            pattern_parts = pattern.split("/")
            path_parts = path.split("/")
            
            if len(pattern_parts) != len(path_parts):
                return False
            
            for pattern_part, path_part in zip(pattern_parts, path_parts):
                if pattern_part.startswith("<") and pattern_part.endswith(">"):
                    continue  # Wildcard matches anything
                elif pattern_part != path_part:
                    return False
            
            return True
        
        return pattern == path
    
    def _check_rate_limit(self, source_ip: str, endpoint: WebhookEndpoint) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Initialize or clean old entries
        if source_ip not in self.rate_limits:
            self.rate_limits[source_ip] = []
        
        # Remove old entries
        self.rate_limits[source_ip] = [
            timestamp for timestamp in self.rate_limits[source_ip]
            if timestamp > window_start
        ]
        
        # Check limit
        if len(self.rate_limits[source_ip]) >= endpoint.rate_limit:
            return False
        
        # Add current request
        self.rate_limits[source_ip].append(current_time)
        return True
    
    def _authenticate_request(self, endpoint: WebhookEndpoint, headers: Dict, body: str) -> bool:
        """Authenticate webhook request"""
        # Simple authentication scheme
        auth_header = headers.get("authorization", "")
        
        if endpoint.secret:
            # HMAC authentication
            expected_signature = self._generate_signature(endpoint.secret, body)
            signature_header = headers.get("x-signature", "")
            
            return hmac.compare_digest(expected_signature, signature_header)
        
        # Bearer token authentication
        expected_token = self.config.get("webhook_token", "default_token")
        return auth_header == f"Bearer {expected_token}"
    
    def _generate_signature(self, secret: str, body: str) -> str:
        """Generate HMAC signature for request"""
        return hmac.new(
            secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    # Event Handlers
    
    async def _handle_content_generation(self, event: WebhookEvent) -> Dict:
        """Handle content generation request"""
        logger.info(f"🎨 Content generation triggered via webhook: {event.event_id}")
        
        # Extract parameters from request
        platform = event.body.get("platform", "fanvue")
        content_type = event.body.get("content_type", "lifestyle")
        count = event.body.get("count", 1)
        
        # Trigger content generation workflow
        execution_id = await self.master_controller.execute_workflow("content_generation_pipeline")
        
        return {
            "message": "Content generation triggered",
            "execution_id": execution_id,
            "parameters": {
                "platform": platform,
                "content_type": content_type,
                "count": count
            }
        }
    
    async def _handle_engagement_update(self, event: WebhookEvent) -> Dict:
        """Handle engagement update from social media platforms"""
        logger.info(f"📊 Engagement update received: {event.event_id}")
        
        # Extract engagement data
        platform = event.body.get("platform")
        post_id = event.body.get("post_id")
        engagement_data = event.body.get("engagement", {})
        
        # Process engagement data
        # In production, this would update analytics database
        
        # Trigger analytics workflow if significant change
        if engagement_data.get("growth_rate", 0) > 0.1:
            execution_id = await self.master_controller.execute_workflow("engagement_analytics")
            
            return {
                "message": "Engagement data processed",
                "triggered_analytics": True,
                "execution_id": execution_id
            }
        
        return {
            "message": "Engagement data processed",
            "triggered_analytics": False
        }
    
    async def _handle_revenue_event(self, event: WebhookEvent) -> Dict:
        """Handle revenue-related events"""
        logger.info(f"💰 Revenue event received: {event.event_id}")
        
        # Extract revenue data
        event_type = event.body.get("event_type")  # purchase, subscription, etc.
        amount = event.body.get("amount", 0)
        platform = event.body.get("platform")
        source = event.body.get("source")  # which content/post led to this
        
        # Trigger revenue optimization workflow
        execution_id = await self.master_controller.execute_workflow("revenue_optimization")
        
        return {
            "message": "Revenue event processed",
            "execution_id": execution_id,
            "revenue_impact": amount
        }
    
    async def _handle_system_alert(self, event: WebhookEvent) -> Dict:
        """Handle system alerts and errors"""
        logger.info(f"🚨 System alert received: {event.event_id}")
        
        alert_type = event.body.get("type", "unknown")
        severity = event.body.get("severity", "medium")
        message = event.body.get("message", "No message provided")
        
        # Trigger crisis management workflow for critical alerts
        if severity in ["critical", "high"]:
            execution_id = await self.master_controller.execute_workflow("crisis_management")
            
            return {
                "message": "Critical alert processed",
                "execution_id": execution_id,
                "alert_handled": True
            }
        
        return {
            "message": "Alert logged",
            "alert_handled": False
        }
    
    async def _handle_manual_trigger(self, event: WebhookEvent) -> Dict:
        """Handle manual workflow triggers"""
        # Extract workflow ID from path
        path_parts = event.headers.get("path", "").split("/")
        workflow_id = path_parts[-1] if len(path_parts) > 0 else None
        
        if not workflow_id:
            raise ValueError("Workflow ID not provided in path")
        
        logger.info(f"🔄 Manual trigger for workflow: {workflow_id}")
        
        # Execute the requested workflow
        execution_id = await self.master_controller.execute_workflow(workflow_id)
        
        return {
            "message": f"Workflow {workflow_id} triggered manually",
            "execution_id": execution_id
        }
    
    async def _handle_health_check(self, event: WebhookEvent) -> Dict:
        """Handle health check requests"""
        system_status = self.master_controller.get_system_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": {
                "running": self.server["running"] if self.server else False,
                "uptime": str(datetime.now() - self.server["start_time"]) if self.server else "0"
            },
            "master_controller": system_status
        }
    
    def get_endpoint_stats(self) -> Dict:
        """Get statistics about webhook endpoints"""
        return {
            "total_endpoints": len(self.endpoints),
            "endpoints": [
                {
                    "id": endpoint.id,
                    "path": endpoint.path,
                    "method": endpoint.method.value,
                    "event_type": endpoint.event_type.value,
                    "auth_required": endpoint.auth_required,
                    "rate_limit": endpoint.rate_limit
                }
                for endpoint in self.endpoints.values()
            ],
            "rate_limit_status": {
                ip: len(timestamps)
                for ip, timestamps in self.rate_limits.items()
            }
        }

# Utility functions for webhook integration

def create_webhook_payload(event_type: str, data: Dict) -> str:
    """Create a properly formatted webhook payload"""
    payload = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "version": "1.0"
    }
    return json.dumps(payload)

def verify_webhook_signature(secret: str, payload: str, signature: str) -> bool:
    """Verify webhook signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Remove any prefix like 'sha256='
    if '=' in signature:
        signature = signature.split('=')[1]
    
    return hmac.compare_digest(expected_signature, signature)