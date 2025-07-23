"""
N8N Automation Manager

Main interface for the comprehensive N8N automation system.
Integrates all components and provides a unified API for automation.

Key Features:
- Unified automation interface
- Component orchestration
- Configuration management
- Monitoring and health checks
- Event-driven automation
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .master_controller import MasterController, WorkflowDefinition, WorkflowPriority
from .webhook_system import WebhookServer, EventType
from .smart_scheduling import SmartSchedulingEngine, Platform, ContentType

logger = logging.getLogger(__name__)

class N8NAutomationManager:
    """
    Main N8N Automation Manager
    
    Orchestrates the entire automation system including:
    - Master Controller Workflow
    - Webhook System
    - Smart Scheduling Engine
    - Integration with existing FionaSparx components
    """
    
    def __init__(self, fiona_sparx_instance, config: Dict = None):
        self.fiona_sparx = fiona_sparx_instance
        self.config = config or {}
        
        # Initialize core components
        self.master_controller = MasterController(config.get("master_controller", {}))
        self.webhook_server = WebhookServer(self.master_controller, config.get("webhooks", {}))
        self.scheduling_engine = SmartSchedulingEngine(config.get("scheduling", {}))
        
        # Runtime state
        self.running = False
        self.start_time = None
        
        logger.info("🎯 N8N Automation Manager initialized")
        self._setup_integration()
    
    def _setup_integration(self):
        """Setup integration between components"""
        # Register content generation workflows
        self._register_content_workflows()
        
        # Setup webhook handlers for existing FionaSparx functionality
        self._setup_fiona_webhooks()
        
        logger.info("✅ Component integration setup complete")
    
    def _register_content_workflows(self):
        """Register content generation workflows with master controller"""
        content_workflows = [
            WorkflowDefinition(
                id="fanvue_content_auto",
                name="Fanvue Content Auto-Generation",
                description="Automated Fanvue content generation based on scheduling",
                priority=WorkflowPriority.HIGH,
                schedule="0 */4 * * *",  # Every 4 hours
                dependencies=["smart_scheduling_engine"]
            ),
            WorkflowDefinition(
                id="loyalfans_content_auto",
                name="LoyalFans Content Auto-Generation", 
                description="Automated LoyalFans content generation based on scheduling",
                priority=WorkflowPriority.HIGH,
                schedule="0 */6 * * *",  # Every 6 hours
                dependencies=["smart_scheduling_engine"]
            ),
            WorkflowDefinition(
                id="quality_assessment_auto",
                name="Automated Quality Assessment",
                description="Regular quality assessment of generated content",
                priority=WorkflowPriority.MEDIUM,
                schedule="0 */2 * * *"  # Every 2 hours
            ),
            WorkflowDefinition(
                id="performance_optimization",
                name="Performance Optimization Workflow",
                description="Analyze and optimize content performance",
                priority=WorkflowPriority.MEDIUM,
                schedule="0 0 * * *"  # Daily at midnight
            )
        ]
        
        for workflow in content_workflows:
            self.master_controller.register_workflow(workflow)
        
        logger.info(f"📝 Registered {len(content_workflows)} content workflows")
    
    def _setup_fiona_webhooks(self):
        """Setup webhook integration with FionaSparx functionality"""
        # Add custom webhook handlers that integrate with FionaSparx
        async def handle_generate_content_webhook(event):
            """Handle content generation via webhook"""
            platform = event.body.get("platform", "fanvue")
            content_type = event.body.get("content_type", "lifestyle")
            count = event.body.get("count", 3)
            
            logger.info(f"🎨 Generating {count} {platform} content via webhook")
            
            try:
                if platform == "fanvue":
                    content = self.fiona_sparx.generate_fanvue_content()
                elif platform == "loyalfans":
                    content = self.fiona_sparx.generate_loyalfans_content()
                else:
                    content = self.fiona_sparx.generate_general_content()
                
                # Schedule the content using smart scheduling
                if content:
                    schedule_info = await self._schedule_content(content, platform, content_type)
                    
                    return {
                        "success": True,
                        "generated_content": len(content),
                        "scheduling": schedule_info
                    }
                else:
                    return {
                        "success": False,
                        "error": "Content generation failed"
                    }
                    
            except Exception as e:
                logger.error(f"Content generation webhook failed: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Override the default content generation handler
        for endpoint_path, endpoint in self.webhook_server.endpoints.items():
            if endpoint.id == "content_generation_trigger":
                endpoint.handler = handle_generate_content_webhook
                break
    
    async def _schedule_content(self, content: List[Dict], platform: str, content_type: str) -> Dict:
        """Schedule content using the smart scheduling engine"""
        try:
            platform_enum = Platform(platform.lower())
            content_type_enum = ContentType(content_type.lower())
            
            schedule_recommendations = []
            
            for i, content_item in enumerate(content):
                # Get optimal schedule for each piece of content
                target_time = datetime.now() + timedelta(hours=i+1)  # Space out content
                
                recommendation = self.scheduling_engine.get_optimal_schedule(
                    platform_enum, content_type_enum, target_time
                )
                
                schedule_recommendations.append({
                    "content_id": content_item.get("image_path", f"content_{i+1}"),
                    "optimal_time": recommendation.optimal_time.isoformat(),
                    "confidence": recommendation.confidence.value,
                    "expected_engagement": recommendation.expected_engagement
                })
            
            return {
                "platform": platform,
                "content_type": content_type,
                "scheduled_items": len(schedule_recommendations),
                "recommendations": schedule_recommendations
            }
            
        except Exception as e:
            logger.error(f"Content scheduling failed: {e}")
            return {
                "error": f"Scheduling failed: {e}"
            }
    
    async def start(self, host: str = "localhost", port: int = 8080):
        """Start the entire N8N automation system"""
        if self.running:
            logger.warning("N8N Automation Manager is already running")
            return
        
        self.running = True
        self.start_time = datetime.now()
        
        logger.info("🚀 Starting N8N Automation System")
        
        try:
            # Start webhook server
            await self.webhook_server.start_server(host, port)
            
            # Start master controller
            controller_task = asyncio.create_task(self.master_controller.start())
            
            logger.info("✅ N8N Automation System started successfully")
            logger.info(f"🔗 Webhook server running on http://{host}:{port}")
            logger.info("📊 Access system status at: /webhooks/health")
            
            # Keep running
            await controller_task
            
        except Exception as e:
            logger.error(f"Failed to start N8N Automation System: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the entire N8N automation system"""
        if not self.running:
            return
        
        logger.info("⏹️ Stopping N8N Automation System")
        
        self.running = False
        
        # Stop components
        await self.webhook_server.stop_server()
        await self.master_controller.stop()
        
        logger.info("✅ N8N Automation System stopped")
    
    async def trigger_workflow(self, workflow_id: str, parameters: Dict = None) -> str:
        """Manually trigger a specific workflow"""
        logger.info(f"🔄 Manual trigger for workflow: {workflow_id}")
        
        execution_id = await self.master_controller.execute_workflow(workflow_id)
        
        return execution_id
    
    async def generate_content_with_scheduling(self, platform: str, content_type: str = "lifestyle", 
                                             count: int = 3, auto_schedule: bool = True) -> Dict:
        """Generate content and optionally schedule it"""
        logger.info(f"🎨 Generating {count} {platform} content with smart scheduling")
        
        try:
            # Generate content using FionaSparx
            if platform.lower() == "fanvue":
                content = self.fiona_sparx.generate_fanvue_content()
            elif platform.lower() == "loyalfans":
                content = self.fiona_sparx.generate_loyalfans_content()
            else:
                content = self.fiona_sparx.generate_general_content()
            
            result = {
                "success": True,
                "platform": platform,
                "generated_content": len(content) if content else 0,
                "content_items": content
            }
            
            if auto_schedule and content:
                schedule_info = await self._schedule_content(content, platform, content_type)
                result["scheduling"] = schedule_info
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation with scheduling failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_performance(self, platform: Optional[str] = None, days: int = 30) -> Dict:
        """Analyze content performance and scheduling effectiveness"""
        logger.info(f"📊 Analyzing performance for {days} days")
        
        try:
            # Get scheduling analytics
            platform_enum = Platform(platform.lower()) if platform else None
            scheduling_analytics = self.scheduling_engine.get_schedule_analytics(
                platform=platform_enum, days=days
            )
            
            # Get system status
            system_status = self.master_controller.get_system_status()
            
            # Get webhook statistics
            webhook_stats = self.webhook_server.get_endpoint_stats()
            
            performance_report = {
                "analysis_period": f"{days} days",
                "platform": platform if platform else "all",
                "scheduling_analytics": scheduling_analytics,
                "system_health": {
                    "automation_running": self.running,
                    "uptime": str(datetime.now() - self.start_time) if self.start_time else "0",
                    "workflows": system_status["master_controller"],
                    "webhook_endpoints": webhook_stats["total_endpoints"]
                },
                "automation_stats": {
                    "total_executions": sum(system_status["execution_status"].values()),
                    "success_rate": self._calculate_success_rate(system_status["execution_status"]),
                    "webhook_activity": webhook_stats.get("rate_limit_status", {})
                }
            }
            
            return performance_report
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_success_rate(self, execution_status: Dict) -> float:
        """Calculate workflow success rate"""
        total = sum(execution_status.values())
        if total == 0:
            return 1.0
        
        successful = execution_status.get("completed", 0)
        return successful / total
    
    async def run_ab_test(self, platform: str, content_type: str, test_duration_days: int = 7) -> str:
        """Run A/B test for optimal posting times"""
        logger.info(f"🧪 Starting A/B test for {platform} {content_type}")
        
        try:
            platform_enum = Platform(platform.lower())
            content_type_enum = ContentType(content_type.lower())
            
            # Generate test times (morning, afternoon, evening)
            base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            test_times = [
                base_time.replace(hour=9),   # Morning
                base_time.replace(hour=15),  # Afternoon
                base_time.replace(hour=19),  # Evening
                base_time.replace(hour=22)   # Late evening
            ]
            
            test_id = self.scheduling_engine.run_ab_test(
                platform_enum, content_type_enum, test_times, test_duration_days
            )
            
            return test_id
            
        except Exception as e:
            logger.error(f"A/B test setup failed: {e}")
            raise
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "automation_manager": {
                "running": self.running,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "uptime": str(datetime.now() - self.start_time) if self.start_time else "0"
            },
            "master_controller": self.master_controller.get_system_status(),
            "webhook_server": {
                "running": self.webhook_server.server["running"] if self.webhook_server.server else False,
                "endpoints": self.webhook_server.get_endpoint_stats()
            },
            "scheduling_engine": {
                "total_historical_data": len(self.scheduling_engine.engagement_history),
                "platforms_configured": len(self.scheduling_engine.audience_profiles),
                "active_ab_tests": len(self.scheduling_engine.schedule_performance)
            }
        }
    
    def export_configuration(self) -> Dict:
        """Export system configuration for backup"""
        return {
            "config": self.config,
            "workflows": {
                wf_id: {
                    "id": wf.id,
                    "name": wf.name,
                    "description": wf.description,
                    "priority": wf.priority.value,
                    "schedule": wf.schedule,
                    "enabled": wf.enabled
                }
                for wf_id, wf in self.master_controller.workflows.items()
            },
            "webhook_endpoints": self.webhook_server.get_endpoint_stats(),
            "scheduling_data": self.scheduling_engine.export_schedule_data()
        }
    
    async def health_check(self) -> Dict:
        """Comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "issues": []
        }
        
        # Check automation manager
        if not self.running:
            health_status["components"]["automation_manager"] = "stopped"
            health_status["issues"].append("Automation manager is not running")
        else:
            health_status["components"]["automation_manager"] = "healthy"
        
        # Check master controller
        controller_status = self.master_controller.get_system_status()
        if controller_status["master_controller"]["running"]:
            health_status["components"]["master_controller"] = "healthy"
        else:
            health_status["components"]["master_controller"] = "stopped"
            health_status["issues"].append("Master controller is not running")
        
        # Check webhook server
        if self.webhook_server.server and self.webhook_server.server["running"]:
            health_status["components"]["webhook_server"] = "healthy"
        else:
            health_status["components"]["webhook_server"] = "stopped"
            health_status["issues"].append("Webhook server is not running")
        
        # Check FionaSparx integration
        try:
            # Test basic FionaSparx functionality
            test_result = self.fiona_sparx.test_components()
            if test_result:
                health_status["components"]["fiona_sparx"] = "healthy"
            else:
                health_status["components"]["fiona_sparx"] = "degraded"
                health_status["issues"].append("FionaSparx component tests failed")
        except Exception as e:
            health_status["components"]["fiona_sparx"] = "error"
            health_status["issues"].append(f"FionaSparx error: {e}")
        
        # Determine overall status
        if health_status["issues"]:
            if len(health_status["issues"]) > 2:
                health_status["status"] = "critical"
            else:
                health_status["status"] = "degraded"
        
        return health_status

# Utility functions for easier integration

def create_n8n_automation(fiona_sparx_instance, config_file: Optional[str] = None) -> N8NAutomationManager:
    """Create and configure N8N automation manager"""
    config = {}
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    return N8NAutomationManager(fiona_sparx_instance, config)

async def quick_start_automation(fiona_sparx_instance, host: str = "localhost", port: int = 8080):
    """Quick start function for the N8N automation system"""
    automation = create_n8n_automation(fiona_sparx_instance)
    
    logger.info("🚀 Quick starting N8N Automation System")
    
    try:
        await automation.start(host, port)
    except KeyboardInterrupt:
        logger.info("⏹️ Received shutdown signal")
        await automation.stop()
    except Exception as e:
        logger.error(f"Quick start failed: {e}")
        await automation.stop()
        raise