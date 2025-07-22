"""
Performance Monitoring System
Enterprise-grade performance monitoring and metrics collection

Features:
- Real-time performance metrics collection
- System resource monitoring
- AI operation performance tracking
- Configurable alerting thresholds
- Historical data retention
- Export capabilities for external monitoring

Author: FionaSparx AI Content Creator
Version: 2.0.0 - Enterprise Edition
"""

import time
import psutil
import threading
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }

@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    gpu_memory_used_mb: Optional[float] = None
    gpu_memory_total_mb: Optional[float] = None
    gpu_utilization_percent: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_available_gb": self.memory_available_gb,
            "disk_usage_percent": self.disk_usage_percent,
            "disk_free_gb": self.disk_free_gb,
            "gpu_memory_used_mb": self.gpu_memory_used_mb,
            "gpu_memory_total_mb": self.gpu_memory_total_mb,
            "gpu_utilization_percent": self.gpu_utilization_percent
        }

@dataclass
class AIOperationMetrics:
    """AI operation performance metrics"""
    operation_type: str
    execution_time_ms: float
    success: bool
    model_used: str
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    error_message: Optional[str] = None
    memory_peak_mb: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "operation_type": self.operation_type,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "model_used": self.model_used,
            "input_size": self.input_size,
            "output_size": self.output_size,
            "error_message": self.error_message,
            "memory_peak_mb": self.memory_peak_mb
        }

class MetricsCollector:
    """Metrics collection and storage"""
    
    def __init__(self, max_history_size: int = 1000):
        """Initialize metrics collector"""
        self.max_history_size = max_history_size
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.system_metrics_history: deque = deque(maxlen=max_history_size)
        self.ai_metrics_history: deque = deque(maxlen=max_history_size)
        self._lock = threading.Lock()
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric"""
        with self._lock:
            self.metrics_history.append(metric)
    
    def add_system_metrics(self, metrics: SystemMetrics):
        """Add system metrics"""
        with self._lock:
            timestamped_metrics = {
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics.to_dict()
            }
            self.system_metrics_history.append(timestamped_metrics)
    
    def add_ai_metrics(self, metrics: AIOperationMetrics):
        """Add AI operation metrics"""
        with self._lock:
            timestamped_metrics = {
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics.to_dict()
            }
            self.ai_metrics_history.append(timestamped_metrics)
    
    def get_recent_metrics(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent performance metrics"""
        with self._lock:
            recent = list(self.metrics_history)[-count:]
            return [metric.to_dict() for metric in recent]
    
    def get_recent_system_metrics(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent system metrics"""
        with self._lock:
            return list(self.system_metrics_history)[-count:]
    
    def get_recent_ai_metrics(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent AI operation metrics"""
        with self._lock:
            return list(self.ai_metrics_history)[-count:]
    
    def clear_history(self):
        """Clear all metric history"""
        with self._lock:
            self.metrics_history.clear()
            self.system_metrics_history.clear()
            self.ai_metrics_history.clear()

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        """Initialize system monitor"""
        self.gpu_available = self._check_gpu_availability()
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU monitoring is available"""
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except:
            logger.info("🔍 GPU monitoring not available (pynvml not installed)")
            return False
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024**3)
            )
            
            # GPU metrics if available
            if self.gpu_available:
                try:
                    gpu_metrics = self._get_gpu_metrics()
                    metrics.gpu_memory_used_mb = gpu_metrics.get("memory_used_mb")
                    metrics.gpu_memory_total_mb = gpu_metrics.get("memory_total_mb")
                    metrics.gpu_utilization_percent = gpu_metrics.get("utilization_percent")
                except Exception as e:
                    logger.debug(f"Failed to get GPU metrics: {e}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error collecting system metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0
            )
    
    def _get_gpu_metrics(self) -> Dict[str, float]:
        """Get GPU metrics using pynvml"""
        try:
            import pynvml
            
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count == 0:
                return {}
            
            # Get metrics from first GPU
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # Memory info
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_used_mb = memory_info.used / (1024**2)
            memory_total_mb = memory_info.total / (1024**2)
            
            # Utilization
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            return {
                "memory_used_mb": memory_used_mb,
                "memory_total_mb": memory_total_mb,
                "utilization_percent": utilization.gpu
            }
            
        except Exception as e:
            logger.debug(f"GPU metrics error: {e}")
            return {}

class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize performance monitor"""
        self.config = config
        monitoring_config = config.get("monitoring", {})
        
        self.enabled = monitoring_config.get("enabled", True)
        self.metrics_interval = monitoring_config.get("metrics_interval", 60)
        self.max_history_size = monitoring_config.get("max_history_size", 1000)
        
        self.collector = MetricsCollector(self.max_history_size)
        self.system_monitor = SystemMonitor()
        
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        if self.enabled:
            self.start_monitoring()
            logger.info(f"📊 Performance monitoring started (interval: {self.metrics_interval}s)")
        else:
            logger.info("📊 Performance monitoring disabled")
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._stop_monitoring.clear()
            self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("📊 Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while not self._stop_monitoring.is_set():
            try:
                # Collect system metrics
                system_metrics = self.system_monitor.get_system_metrics()
                self.collector.add_system_metrics(system_metrics)
                
                # Create performance metrics
                self.collector.add_metric(PerformanceMetric(
                    name="system.cpu.usage",
                    value=system_metrics.cpu_percent,
                    unit="percent",
                    timestamp=datetime.now(),
                    tags={"component": "system"}
                ))
                
                self.collector.add_metric(PerformanceMetric(
                    name="system.memory.usage",
                    value=system_metrics.memory_percent,
                    unit="percent",
                    timestamp=datetime.now(),
                    tags={"component": "system"}
                ))
                
                if system_metrics.gpu_memory_total_mb:
                    gpu_usage_percent = (system_metrics.gpu_memory_used_mb / system_metrics.gpu_memory_total_mb) * 100
                    self.collector.add_metric(PerformanceMetric(
                        name="system.gpu.memory.usage",
                        value=gpu_usage_percent,
                        unit="percent",
                        timestamp=datetime.now(),
                        tags={"component": "gpu"}
                    ))
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
            
            # Wait for next interval
            self._stop_monitoring.wait(self.metrics_interval)
    
    def record_ai_operation(self,
                           operation_type: str,
                           execution_time_ms: float,
                           success: bool,
                           model_used: str,
                           input_size: Optional[int] = None,
                           output_size: Optional[int] = None,
                           error_message: Optional[str] = None):
        """Record AI operation metrics"""
        if not self.enabled:
            return
        
        metrics = AIOperationMetrics(
            operation_type=operation_type,
            execution_time_ms=execution_time_ms,
            success=success,
            model_used=model_used,
            input_size=input_size,
            output_size=output_size,
            error_message=error_message
        )
        
        self.collector.add_ai_metrics(metrics)
        
        # Add as performance metric too
        self.collector.add_metric(PerformanceMetric(
            name=f"ai.{operation_type}.execution_time",
            value=execution_time_ms,
            unit="milliseconds",
            timestamp=datetime.now(),
            tags={
                "operation": operation_type,
                "model": model_used,
                "success": str(success)
            }
        ))
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            current_system = self.system_monitor.get_system_metrics()
            recent_ai_metrics = self.collector.get_recent_ai_metrics(50)
            
            # Calculate AI operation statistics
            ai_stats = self._calculate_ai_stats(recent_ai_metrics)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_health": {
                    "cpu_usage": current_system.cpu_percent,
                    "memory_usage": current_system.memory_percent,
                    "disk_usage": current_system.disk_usage_percent,
                    "gpu_memory_usage": (current_system.gpu_memory_used_mb / current_system.gpu_memory_total_mb * 100) if current_system.gpu_memory_total_mb else None
                },
                "ai_operations": ai_stats,
                "monitoring_enabled": self.enabled,
                "metrics_collected": len(self.collector.metrics_history)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating performance summary: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _calculate_ai_stats(self, ai_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate AI operation statistics"""
        if not ai_metrics:
            return {"total_operations": 0}
        
        total_ops = len(ai_metrics)
        successful_ops = sum(1 for metric in ai_metrics if metric["metrics"]["success"])
        
        execution_times = [metric["metrics"]["execution_time_ms"] for metric in ai_metrics]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Group by operation type
        operation_counts = {}
        for metric in ai_metrics:
            op_type = metric["metrics"]["operation_type"]
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
        
        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "success_rate": (successful_ops / total_ops) * 100 if total_ops > 0 else 0,
            "average_execution_time_ms": avg_execution_time,
            "operations_by_type": operation_counts
        }
    
    def export_metrics(self, output_path: str = "logs/performance_metrics.json"):
        """Export collected metrics to file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": self.collector.get_recent_system_metrics(),
                "ai_metrics": self.collector.get_recent_ai_metrics(),
                "performance_metrics": self.collector.get_recent_metrics(),
                "summary": self.get_performance_summary()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Performance metrics exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error exporting metrics: {e}")
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        try:
            system_metrics = self.system_monitor.get_system_metrics()
            
            # Define health thresholds
            cpu_warning = 80.0
            memory_warning = 85.0
            disk_warning = 90.0
            
            health_issues = []
            if system_metrics.cpu_percent > cpu_warning:
                health_issues.append(f"High CPU usage: {system_metrics.cpu_percent:.1f}%")
            if system_metrics.memory_percent > memory_warning:
                health_issues.append(f"High memory usage: {system_metrics.memory_percent:.1f}%")
            if system_metrics.disk_usage_percent > disk_warning:
                health_issues.append(f"High disk usage: {system_metrics.disk_usage_percent:.1f}%")
            
            # Determine overall health
            if not health_issues:
                health_status = "healthy"
            elif len(health_issues) == 1:
                health_status = "warning"
            else:
                health_status = "critical"
            
            return {
                "status": health_status,
                "issues": health_issues,
                "system_metrics": system_metrics.to_dict(),
                "monitoring_active": self._monitoring_thread.is_alive() if self._monitoring_thread else False
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting health status: {e}")
            return {
                "status": "error",
                "issues": [f"Health check failed: {e}"],
                "monitoring_active": False
            }

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_type: str, model_used: str):
        self.monitor = monitor
        self.operation_type = operation_type
        self.model_used = model_used
        self.start_time = None
        self.success = False
        self.error_message = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.success = True
        else:
            self.success = False
            self.error_message = str(exc_val) if exc_val else "Unknown error"
        
        self.monitor.record_ai_operation(
            operation_type=self.operation_type,
            execution_time_ms=execution_time_ms,
            success=self.success,
            model_used=self.model_used,
            error_message=self.error_message
        )