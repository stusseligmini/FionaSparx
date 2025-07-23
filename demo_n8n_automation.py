#!/usr/bin/env python3
"""
Comprehensive N8N Automation System Demo

This script demonstrates all components of the N8N automation system
working together in a realistic scenario.
"""

import asyncio
import logging
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from n8n_automation.automation_manager import create_n8n_automation
from n8n_automation.personality_engine import EngagementContext, CulturalContext
from n8n_automation.smart_scheduling import Platform, ContentType
from utils.cli_progress import ConsoleUI, Colors

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def comprehensive_demo():
    """Comprehensive demo of the N8N automation system"""
    
    ConsoleUI.print_header("N8N Automation System - Comprehensive Demo", color=Colors.BLUE)
    
    # Initialize FionaSparx (simplified for demo)
    class DemoFionaSparx:
        def test_components(self):
            return True
        
        def generate_fanvue_content(self):
            return [{"content": "demo fanvue content", "quality": "good"}]
        
        def generate_loyalfans_content(self):
            return [{"content": "demo loyalfans content", "quality": "excellent"}]
    
    fiona = DemoFionaSparx()
    
    # Create automation system
    ConsoleUI.print_section("Initializing N8N Automation System")
    automation = create_n8n_automation(fiona)
    
    try:
        # Demo 1: Smart Scheduling
        ConsoleUI.print_section("Demo 1: Smart Scheduling Engine")
        
        platforms = [Platform.FANVUE, Platform.LOYALFANS]
        content_types = [ContentType.LIFESTYLE, ContentType.ARTISTIC]
        
        for platform in platforms:
            for content_type in content_types:
                recommendation = automation.scheduling_engine.get_optimal_schedule(
                    platform, content_type
                )
                
                ConsoleUI.print_info(f"{platform.value.title()} - {content_type.value.title()}:")
                print(f"  Optimal time: {recommendation.optimal_time.strftime('%H:%M')}")
                print(f"  Confidence: {recommendation.confidence.value}")
                print(f"  Expected engagement: {recommendation.expected_engagement:.1%}")
        
        # Demo 2: AI Personality Engine
        ConsoleUI.print_section("Demo 2: AI Personality Engine")
        
        base_content = "Sharing some exciting news with my amazing followers!"
        
        contexts = [
            {
                "platform": "fanvue",
                "time": datetime.now().replace(hour=19),
                "cultural": CulturalContext.WESTERN,
                "description": "Evening Fanvue post"
            },
            {
                "platform": "loyalfans", 
                "time": datetime.now().replace(hour=22),
                "cultural": CulturalContext.EUROPEAN,
                "description": "Late evening LoyalFans post"
            }
        ]
        
        for ctx in contexts:
            context = EngagementContext(
                platform=ctx["platform"],
                time_of_day=ctx["time"],
                cultural_context=ctx["cultural"]
            )
            
            response = automation.scheduling_engine.personality_engine.generate_personality_content(
                base_content, context
            ) if hasattr(automation.scheduling_engine, 'personality_engine') else None
            
            if response:
                ConsoleUI.print_info(f"{ctx['description']}:")
                print(f"  Adapted content: {response.content}")
                print(f"  Style/Tone: {response.style.value}/{response.emotional_tone.value}")
            else:
                # Use standalone personality engine
                from n8n_automation.personality_engine import AdvancedPersonalityEngine
                personality_engine = AdvancedPersonalityEngine()
                response = personality_engine.generate_personality_content(base_content, context)
                
                ConsoleUI.print_info(f"{ctx['description']}:")
                print(f"  Adapted content: {response.content}")
                print(f"  Style/Tone: {response.style.value}/{response.emotional_tone.value}")
        
        # Demo 3: Webhook System
        ConsoleUI.print_section("Demo 3: Webhook System")
        
        # Start webhook server
        await automation.webhook_server.start_server("localhost", 8080)
        
        # Simulate webhook requests
        demo_requests = [
            {
                "method": "POST",
                "path": "/webhooks/generate-content",
                "headers": {"authorization": "Bearer default_token"},
                "body": '{"platform": "fanvue", "content_type": "lifestyle"}',
                "source_ip": "127.0.0.1",
                "description": "Content generation trigger"
            },
            {
                "method": "POST",
                "path": "/webhooks/engagement",
                "headers": {"authorization": "Bearer default_token"},
                "body": '{"platform": "fanvue", "post_id": "123", "engagement": {"likes": 150, "growth_rate": 0.15}}',
                "source_ip": "127.0.0.1",
                "description": "Engagement data update"
            },
            {
                "method": "GET",
                "path": "/webhooks/health",
                "headers": {},
                "body": "",
                "source_ip": "127.0.0.1",
                "description": "Health check"
            }
        ]
        
        for req in demo_requests:
            ConsoleUI.print_info(f"Testing: {req['description']}")
            result = await automation.webhook_server.handle_request(
                req["method"], req["path"], req["headers"], req["body"], req["source_ip"]
            )
            print(f"  Status: {result['status']}")
            print(f"  Event ID: {result.get('event_id', 'N/A')}")
            if result.get('result'):
                print(f"  Result: {str(result['result'])[:100]}...")
        
        await automation.webhook_server.stop_server()
        
        # Demo 4: Master Controller Workflows
        ConsoleUI.print_section("Demo 4: Master Controller Workflows")
        
        # Show registered workflows
        workflows = automation.master_controller.workflows
        ConsoleUI.print_info(f"Registered workflows: {len(workflows)}")
        
        for wf_id, workflow in list(workflows.items())[:5]:  # Show first 5
            print(f"  {workflow.name} ({workflow.priority.name} priority)")
        
        # Demo workflow execution
        ConsoleUI.print_info("Simulating workflow execution:")
        execution_id = await automation.master_controller.execute_workflow("engagement_analytics")
        print(f"  Executed engagement_analytics: {execution_id}")
        
        # Demo 5: Performance Analytics
        ConsoleUI.print_section("Demo 5: Performance Analytics")
        
        analytics = await automation.analyze_performance(days=30)
        
        ConsoleUI.print_info("System Performance Overview:")
        print(f"  Analysis period: {analytics['analysis_period']}")
        print(f"  Automation running: {analytics['system_health']['automation_running']}")
        print(f"  Total workflows: {analytics['system_health']['workflows']['total_workflows']}")
        print(f"  Webhook endpoints: {analytics['system_health']['webhook_endpoints']}")
        
        if analytics.get('scheduling_analytics'):
            sched_analytics = analytics['scheduling_analytics']
            print(f"  Total posts analyzed: {sched_analytics.get('total_posts', 0)}")
            print(f"  Average engagement: {sched_analytics.get('average_engagement', 0):.1%}")
        
        # Demo 6: Health Check
        ConsoleUI.print_section("Demo 6: System Health Check")
        
        health = await automation.health_check()
        
        ConsoleUI.print_info(f"Overall status: {health['status'].upper()}")
        for component, status in health['components'].items():
            print(f"  {component}: {status}")
        
        if health['issues']:
            ConsoleUI.print_warning("Issues found:")
            for issue in health['issues']:
                print(f"  - {issue}")
        else:
            ConsoleUI.print_success("No issues found!")
        
        # Demo 7: Configuration Export
        ConsoleUI.print_section("Demo 7: Configuration Export")
        
        config = automation.export_configuration()
        
        ConsoleUI.print_info("System configuration exported:")
        print(f"  Workflows: {len(config['workflows'])}")
        print(f"  Webhook endpoints: {config['webhook_endpoints']['total_endpoints']}")
        print(f"  Scheduling data points: {len(config['scheduling_data']['engagement_history'])}")
        
        ConsoleUI.print_success("🎉 Comprehensive demo completed successfully!")
        
        # Summary
        ConsoleUI.print_section("Demo Summary")
        print("✅ Smart Scheduling Engine: ML-based timing recommendations")
        print("✅ AI Personality Engine: Adaptive communication styles")  
        print("✅ Webhook System: Real-time event processing")
        print("✅ Master Controller: Workflow orchestration")
        print("✅ Performance Analytics: Comprehensive monitoring")
        print("✅ Health Monitoring: System status and diagnostics")
        print("✅ Configuration Management: Export/import capabilities")
        print("\n🎯 N8N Automation System is fully operational!")
        
    except Exception as e:
        ConsoleUI.print_error(f"Demo failed: {e}")
        logger.error(f"Demo error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(comprehensive_demo())