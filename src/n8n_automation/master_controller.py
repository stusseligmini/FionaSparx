"""
Master Controller Workflow

This module implements the master controller that orchestrates all other workflows
in the FionaSparx N8N automation system.

Key Features:
- Workflow orchestration and scheduling
- Resource allocation and monitoring
- Error handling and recovery
- Performance optimization
- Workflow health monitoring
"""

import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status states for workflows"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    SCHEDULED = "scheduled"

class WorkflowPriority(Enum):
    """Priority levels for workflow execution"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class WorkflowDefinition:
    """Definition of a workflow"""
    id: str
    name: str
    description: str
    priority: WorkflowPriority
    schedule: Optional[str] = None  # Cron expression
    dependencies: List[str] = None  # List of workflow IDs this depends on
    max_retries: int = 3
    timeout: int = 300  # seconds
    enabled: bool = True

@dataclass
class WorkflowExecution:
    """Execution instance of a workflow"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    retry_count: int = 0

class MasterController:
    """
    Master Controller Workflow - Orchestrates all automation workflows
    
    This is the central orchestrator that manages all other workflows
    in the FionaSparx automation system.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.running = False
        self.scheduler_task = None
        
        logger.info("🎯 Master Controller initialized")
        self._setup_default_workflows()
    
    def _setup_default_workflows(self):
        """Setup default workflows from problem statement"""
        default_workflows = [
            WorkflowDefinition(
                id="content_generation_pipeline",
                name="Content Generation Pipeline",
                description="Parallel content generation for all platforms",
                priority=WorkflowPriority.HIGH,
                schedule="0 */6 * * *"  # Every 6 hours
            ),
            WorkflowDefinition(
                id="smart_scheduling_engine",
                name="Smart Scheduling Engine", 
                description="ML-based optimal timing for content posting",
                priority=WorkflowPriority.MEDIUM,
                schedule="0 */1 * * *"  # Every hour
            ),
            WorkflowDefinition(
                id="engagement_analytics",
                name="Engagement Analytics Pipeline",
                description="Real-time learning from social media",
                priority=WorkflowPriority.HIGH,
                schedule="*/15 * * * *"  # Every 15 minutes
            ),
            WorkflowDefinition(
                id="revenue_optimization",
                name="Revenue Optimization Workflow",
                description="Track conversions from social media to FanVue/LoyalFans",
                priority=WorkflowPriority.CRITICAL,
                schedule="*/30 * * * *"  # Every 30 minutes
            ),
            WorkflowDefinition(
                id="crisis_management",
                name="Crisis Management Workflow",
                description="Handle API errors and fallback strategies",
                priority=WorkflowPriority.CRITICAL,
                schedule="*/5 * * * *"  # Every 5 minutes
            )
        ]
        
        for workflow in default_workflows:
            self.register_workflow(workflow)
        
        logger.info(f"✅ Registered {len(default_workflows)} default workflows")
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """Register a new workflow"""
        self.workflows[workflow.id] = workflow
        logger.info(f"📝 Registered workflow: {workflow.name} ({workflow.id})")
    
    async def start(self):
        """Start the master controller"""
        if self.running:
            logger.warning("Master controller is already running")
            return
        
        self.running = True
        logger.info("🚀 Starting Master Controller")
        
        # Start the scheduler task
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        try:
            await self.scheduler_task
        except asyncio.CancelledError:
            logger.info("Master Controller stopped")
    
    async def stop(self):
        """Stop the master controller"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏹️ Master Controller stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._process_scheduled_workflows()
                await self._monitor_running_workflows()
                await self._cleanup_completed_workflows()
                
                # Wait 10 seconds before next iteration
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _process_scheduled_workflows(self):
        """Process workflows that are scheduled to run"""
        current_time = datetime.now()
        
        for workflow_id, workflow in self.workflows.items():
            if not workflow.enabled:
                continue
            
            # Simple time-based scheduling (in production, use proper cron parsing)
            if self._should_run_workflow(workflow, current_time):
                await self.execute_workflow(workflow_id)
    
    def _should_run_workflow(self, workflow: WorkflowDefinition, current_time: datetime) -> bool:
        """Determine if a workflow should run based on schedule"""
        # Simplified scheduling logic - in production use proper cron parsing
        if not workflow.schedule:
            return False
        
        # For demo, run workflows at different intervals based on priority
        if workflow.priority == WorkflowPriority.CRITICAL:
            return current_time.minute % 5 == 0  # Every 5 minutes
        elif workflow.priority == WorkflowPriority.HIGH:
            return current_time.minute % 15 == 0  # Every 15 minutes
        elif workflow.priority == WorkflowPriority.MEDIUM:
            return current_time.minute % 30 == 0  # Every 30 minutes
        else:
            return current_time.minute == 0 and current_time.hour % 6 == 0  # Every 6 hours
    
    async def execute_workflow(self, workflow_id: str) -> str:
        """Execute a specific workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = f"{workflow_id}_{int(time.time())}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.SCHEDULED,
            start_time=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        logger.info(f"🔄 Executing workflow: {workflow.name} (execution: {execution_id})")
        
        try:
            # Check dependencies first
            if not await self._check_dependencies(workflow):
                execution.status = WorkflowStatus.FAILED
                execution.error = "Dependencies not met"
                execution.end_time = datetime.now()
                return execution_id
            
            execution.status = WorkflowStatus.RUNNING
            
            # Execute the actual workflow (delegate to specific workflow handlers)
            result = await self._execute_workflow_logic(workflow)
            
            execution.status = WorkflowStatus.COMPLETED
            execution.result = result
            execution.end_time = datetime.now()
            
            logger.info(f"✅ Workflow completed: {workflow.name}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now()
            
            logger.error(f"❌ Workflow failed: {workflow.name} - {e}")
            
            # Handle retries
            if execution.retry_count < workflow.max_retries:
                execution.retry_count += 1
                execution.status = WorkflowStatus.SCHEDULED
                logger.info(f"🔄 Retrying workflow: {workflow.name} (attempt {execution.retry_count})")
        
        return execution_id
    
    async def _check_dependencies(self, workflow: WorkflowDefinition) -> bool:
        """Check if workflow dependencies are met"""
        if not workflow.dependencies:
            return True
        
        for dep_id in workflow.dependencies:
            # Check if dependency workflow has completed successfully recently
            recent_executions = [
                exec for exec in self.executions.values()
                if exec.workflow_id == dep_id and 
                exec.status == WorkflowStatus.COMPLETED and
                exec.end_time and 
                (datetime.now() - exec.end_time).total_seconds() < 3600  # Within last hour
            ]
            
            if not recent_executions:
                logger.warning(f"Dependency not met: {dep_id} for workflow {workflow.id}")
                return False
        
        return True
    
    async def _execute_workflow_logic(self, workflow: WorkflowDefinition) -> Dict:
        """Execute the actual workflow logic"""
        # This is where we delegate to specific workflow implementations
        
        if workflow.id == "content_generation_pipeline":
            return await self._execute_content_generation()
        elif workflow.id == "smart_scheduling_engine":
            return await self._execute_smart_scheduling()
        elif workflow.id == "engagement_analytics":
            return await self._execute_engagement_analytics()
        elif workflow.id == "revenue_optimization":
            return await self._execute_revenue_optimization()
        elif workflow.id == "crisis_management":
            return await self._execute_crisis_management()
        else:
            # Default workflow execution
            await asyncio.sleep(1)  # Simulate work
            return {"status": "completed", "message": f"Executed {workflow.name}"}
    
    async def _execute_content_generation(self) -> Dict:
        """Execute content generation pipeline"""
        logger.info("🎨 Executing Content Generation Pipeline")
        # Simulate content generation work
        await asyncio.sleep(2)
        return {
            "status": "completed",
            "generated_content": {
                "fanvue": 3,
                "loyalfans": 3,
                "instagram": 2
            },
            "execution_time": 2.0
        }
    
    async def _execute_smart_scheduling(self) -> Dict:
        """Execute smart scheduling engine"""
        logger.info("📅 Executing Smart Scheduling Engine")
        # Simulate ML-based scheduling analysis
        await asyncio.sleep(1)
        return {
            "status": "completed",
            "optimal_times": {
                "fanvue": "18:00",
                "loyalfans": "20:00",
                "instagram": "12:00"
            },
            "confidence_score": 0.85
        }
    
    async def _execute_engagement_analytics(self) -> Dict:
        """Execute engagement analytics pipeline"""
        logger.info("📊 Executing Engagement Analytics Pipeline")
        # Simulate real-time analytics processing
        await asyncio.sleep(1.5)
        return {
            "status": "completed",
            "metrics": {
                "total_engagement": 1250,
                "growth_rate": 0.12,
                "top_content_type": "lifestyle"
            },
            "insights": ["Afternoon posts perform 20% better", "Video content gets 3x engagement"]
        }
    
    async def _execute_revenue_optimization(self) -> Dict:
        """Execute revenue optimization workflow"""
        logger.info("💰 Executing Revenue Optimization Workflow")
        # Simulate revenue tracking and optimization
        await asyncio.sleep(1)
        return {
            "status": "completed",
            "revenue_data": {
                "daily_revenue": 450.00,
                "conversion_rate": 0.08,
                "top_traffic_source": "fanvue_post_123"
            },
            "optimizations": ["Increase CTAs on high-performing posts", "Schedule more content during peak hours"]
        }
    
    async def _execute_crisis_management(self) -> Dict:
        """Execute crisis management workflow"""
        logger.info("🚨 Executing Crisis Management Workflow")
        # Simulate system health checks and crisis handling
        await asyncio.sleep(0.5)
        return {
            "status": "completed",
            "system_health": {
                "api_status": "healthy",
                "error_rate": 0.02,
                "uptime": "99.8%"
            },
            "actions_taken": []
        }
    
    async def _monitor_running_workflows(self):
        """Monitor running workflows for timeouts"""
        current_time = datetime.now()
        
        for execution in self.executions.values():
            if execution.status == WorkflowStatus.RUNNING:
                if execution.start_time:
                    elapsed = (current_time - execution.start_time).total_seconds()
                    workflow = self.workflows.get(execution.workflow_id)
                    
                    if workflow and elapsed > workflow.timeout:
                        execution.status = WorkflowStatus.FAILED
                        execution.error = f"Workflow timed out after {elapsed}s"
                        execution.end_time = current_time
                        
                        logger.warning(f"⏰ Workflow timed out: {workflow.name}")
    
    async def _cleanup_completed_workflows(self):
        """Clean up old completed workflow executions"""
        current_time = datetime.now()
        cleanup_threshold = timedelta(hours=24)  # Keep executions for 24 hours
        
        to_remove = []
        for execution_id, execution in self.executions.items():
            if execution.end_time:
                age = current_time - execution.end_time
                if age > cleanup_threshold:
                    to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.executions[execution_id]
        
        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} old executions")
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get status of a specific workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        # Get recent executions
        recent_executions = [
            {
                "execution_id": exec.execution_id,
                "status": exec.status.value,
                "start_time": exec.start_time.isoformat() if exec.start_time else None,
                "end_time": exec.end_time.isoformat() if exec.end_time else None,
                "error": exec.error
            }
            for exec in self.executions.values()
            if exec.workflow_id == workflow_id
        ][-10:]  # Last 10 executions
        
        return {
            "workflow": {
                "id": workflow.id,
                "name": workflow.name,
                "status": "enabled" if workflow.enabled else "disabled",
                "priority": workflow.priority.name,
                "schedule": workflow.schedule
            },
            "recent_executions": recent_executions
        }
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        total_workflows = len(self.workflows)
        enabled_workflows = sum(1 for w in self.workflows.values() if w.enabled)
        
        # Count executions by status
        status_counts = {}
        for status in WorkflowStatus:
            status_counts[status.value] = sum(
                1 for exec in self.executions.values() if exec.status == status
            )
        
        return {
            "master_controller": {
                "running": self.running,
                "total_workflows": total_workflows,
                "enabled_workflows": enabled_workflows
            },
            "execution_status": status_counts,
            "system_health": "healthy" if self.running else "stopped"
        }