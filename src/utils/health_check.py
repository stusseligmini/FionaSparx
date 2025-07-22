"""
Health Check System
Enterprise-grade health monitoring and system diagnostics

Features:
- Comprehensive system health checks
- AI model availability testing
- Resource utilization monitoring
- Service dependency checks
- Automated health reporting
- Configurable health thresholds

Author: FionaSparx AI Content Creator
Version: 2.0.0 - Enterprise Edition
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import os
import psutil

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    execution_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms
        }

class HealthCheck:
    """Base health check class"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def check(self) -> HealthCheckResult:
        """Perform health check - to be implemented by subclasses"""
        raise NotImplementedError("Health check must implement check() method")

class SystemResourcesHealthCheck(HealthCheck):
    """System resources health check"""
    
    def __init__(self, cpu_warning: float = 80.0, cpu_critical: float = 95.0,
                 memory_warning: float = 85.0, memory_critical: float = 95.0,
                 disk_warning: float = 85.0, disk_critical: float = 95.0):
        super().__init__("system_resources", "System CPU, memory and disk usage")
        self.cpu_warning = cpu_warning
        self.cpu_critical = cpu_critical
        self.memory_warning = memory_warning
        self.memory_critical = memory_critical
        self.disk_warning = disk_warning
        self.disk_critical = disk_critical
    
    def check(self) -> HealthCheckResult:
        """Check system resources"""
        start_time = time.time()
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status
            status = HealthStatus.HEALTHY
            issues = []
            
            # Check CPU
            if cpu_percent >= self.cpu_critical:
                status = HealthStatus.CRITICAL
                issues.append(f"Critical CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent >= self.cpu_warning:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Check Memory
            if memory.percent >= self.memory_critical:
                status = HealthStatus.CRITICAL
                issues.append(f"Critical memory usage: {memory.percent:.1f}%")
            elif memory.percent >= self.memory_warning:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            # Check Disk
            if disk.percent >= self.disk_critical:
                status = HealthStatus.CRITICAL
                issues.append(f"Critical disk usage: {disk.percent:.1f}%")
            elif disk.percent >= self.disk_warning:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            message = "System resources are healthy" if not issues else "; ".join(issues)
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "thresholds": {
                    "cpu_warning": self.cpu_warning,
                    "cpu_critical": self.cpu_critical,
                    "memory_warning": self.memory_warning,
                    "memory_critical": self.memory_critical,
                    "disk_warning": self.disk_warning,
                    "disk_critical": self.disk_critical
                }
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Failed to check system resources: {e}"
            details = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms
        )

class DirectoryHealthCheck(HealthCheck):
    """Directory accessibility and permissions health check"""
    
    def __init__(self, directories: List[str]):
        super().__init__("directories", "Required directories accessibility")
        self.directories = directories
    
    def check(self) -> HealthCheckResult:
        """Check directories"""
        start_time = time.time()
        
        try:
            status = HealthStatus.HEALTHY
            issues = []
            directory_status = {}
            
            for directory in self.directories:
                dir_status = {
                    "exists": os.path.exists(directory),
                    "readable": False,
                    "writable": False
                }
                
                if dir_status["exists"]:
                    dir_status["readable"] = os.access(directory, os.R_OK)
                    dir_status["writable"] = os.access(directory, os.W_OK)
                    
                    if not dir_status["readable"]:
                        issues.append(f"Directory {directory} is not readable")
                        status = HealthStatus.WARNING
                    if not dir_status["writable"]:
                        issues.append(f"Directory {directory} is not writable")
                        status = HealthStatus.WARNING
                else:
                    issues.append(f"Directory {directory} does not exist")
                    status = HealthStatus.CRITICAL
                
                directory_status[directory] = dir_status
            
            message = "All directories are accessible" if not issues else "; ".join(issues)
            
            details = {
                "directories": directory_status,
                "total_checked": len(self.directories),
                "issues_found": len(issues)
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Failed to check directories: {e}"
            details = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms
        )

class AIModelHealthCheck(HealthCheck):
    """AI model availability and functionality health check"""
    
    def __init__(self, text_generator=None, image_generator=None):
        super().__init__("ai_models", "AI model availability and functionality")
        self.text_generator = text_generator
        self.image_generator = image_generator
    
    def check(self) -> HealthCheckResult:
        """Check AI models"""
        start_time = time.time()
        
        try:
            status = HealthStatus.HEALTHY
            issues = []
            model_status = {}
            
            # Check text generator
            if self.text_generator:
                try:
                    test_caption = self.text_generator.generate_smart_caption(
                        image_context="Test health check",
                        platform="instagram",
                        tone="friendly"
                    )
                    model_status["text_generator"] = {
                        "available": True,
                        "functional": len(test_caption) > 0,
                        "test_output_length": len(test_caption)
                    }
                    if not model_status["text_generator"]["functional"]:
                        issues.append("Text generator produced empty output")
                        status = HealthStatus.WARNING
                except Exception as e:
                    model_status["text_generator"] = {
                        "available": False,
                        "functional": False,
                        "error": str(e)
                    }
                    issues.append(f"Text generator failed: {e}")
                    status = HealthStatus.CRITICAL
            else:
                model_status["text_generator"] = {
                    "available": False,
                    "functional": False,
                    "error": "Not initialized"
                }
                issues.append("Text generator not available")
                status = HealthStatus.WARNING
            
            # Check image generator
            if self.image_generator:
                try:
                    # Try a simple test without actually generating image
                    model_status["image_generator"] = {
                        "available": True,
                        "model_loaded": hasattr(self.image_generator, 'pipeline') and self.image_generator.pipeline is not None,
                        "device": getattr(self.image_generator, 'device', 'unknown')
                    }
                    if not model_status["image_generator"]["model_loaded"]:
                        issues.append("Image generator model not loaded")
                        status = HealthStatus.WARNING
                except Exception as e:
                    model_status["image_generator"] = {
                        "available": False,
                        "model_loaded": False,
                        "error": str(e)
                    }
                    issues.append(f"Image generator failed: {e}")
                    status = HealthStatus.CRITICAL
            else:
                model_status["image_generator"] = {
                    "available": False,
                    "model_loaded": False,
                    "error": "Not initialized"
                }
                issues.append("Image generator not available")
                status = HealthStatus.WARNING
            
            message = "All AI models are functional" if not issues else "; ".join(issues)
            
            details = {
                "models": model_status,
                "total_models": 2,
                "functional_models": sum(1 for m in model_status.values() if m.get("functional", False) or m.get("model_loaded", False))
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Failed to check AI models: {e}"
            details = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms
        )

class ConfigurationHealthCheck(HealthCheck):
    """Configuration validity health check"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("configuration", "Configuration validity and completeness")
        self.config = config
    
    def check(self) -> HealthCheckResult:
        """Check configuration"""
        start_time = time.time()
        
        try:
            status = HealthStatus.HEALTHY
            issues = []
            config_status = {}
            
            # Check required sections
            required_sections = ["ai_model", "platforms"]
            for section in required_sections:
                if section in self.config:
                    config_status[section] = {"present": True}
                else:
                    config_status[section] = {"present": False}
                    issues.append(f"Missing required configuration section: {section}")
                    status = HealthStatus.CRITICAL
            
            # Check AI model configuration
            if "ai_model" in self.config:
                ai_config = self.config["ai_model"]
                required_ai_fields = ["image_model", "device"]
                ai_status = {"required_fields": {}}
                
                for field in required_ai_fields:
                    if field in ai_config:
                        ai_status["required_fields"][field] = {"present": True, "value": ai_config[field]}
                    else:
                        ai_status["required_fields"][field] = {"present": False}
                        issues.append(f"Missing required AI model field: {field}")
                        status = HealthStatus.WARNING
                
                config_status["ai_model"].update(ai_status)
            
            # Check platform configurations
            if "platforms" in self.config:
                platforms = self.config["platforms"]
                platform_status = {}
                
                for platform_name, platform_config in platforms.items():
                    if isinstance(platform_config, dict):
                        platform_status[platform_name] = {
                            "valid": True,
                            "enabled": platform_config.get("enabled", True)
                        }
                    else:
                        platform_status[platform_name] = {"valid": False}
                        issues.append(f"Invalid platform configuration for {platform_name}")
                        status = HealthStatus.WARNING
                
                config_status["platforms"] = platform_status
            
            message = "Configuration is valid" if not issues else "; ".join(issues)
            
            details = {
                "configuration_status": config_status,
                "total_issues": len(issues),
                "config_sections": list(self.config.keys())
            }
            
        except Exception as e:
            status = HealthStatus.UNKNOWN
            message = f"Failed to check configuration: {e}"
            details = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms
        )

class HealthCheckManager:
    """Manages and coordinates health checks"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize health check manager"""
        self.config = config
        monitoring_config = config.get("monitoring", {})
        
        self.enabled = monitoring_config.get("enabled", True)
        self.check_interval = monitoring_config.get("health_check_interval", 30)
        
        self.health_checks: List[HealthCheck] = []
        self.last_results: Dict[str, HealthCheckResult] = {}
        
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        self._setup_default_checks()
        
        if self.enabled:
            logger.info(f"🏥 Health check manager initialized with {len(self.health_checks)} checks")
        else:
            logger.info("🏥 Health check manager disabled")
    
    def _setup_default_checks(self):
        """Setup default health checks"""
        # System resources check
        self.add_health_check(SystemResourcesHealthCheck())
        
        # Directory check
        required_dirs = ["logs", "data", "output", "config"]
        self.add_health_check(DirectoryHealthCheck(required_dirs))
        
        # Configuration check
        self.add_health_check(ConfigurationHealthCheck(self.config))
    
    def add_health_check(self, health_check: HealthCheck):
        """Add a health check"""
        self.health_checks.append(health_check)
        logger.debug(f"Added health check: {health_check.name}")
    
    def remove_health_check(self, name: str):
        """Remove a health check by name"""
        self.health_checks = [hc for hc in self.health_checks if hc.name != name]
        if name in self.last_results:
            del self.last_results[name]
        logger.debug(f"Removed health check: {name}")
    
    def set_ai_components(self, text_generator=None, image_generator=None):
        """Set AI components for health checking"""
        # Remove existing AI health check
        self.remove_health_check("ai_models")
        
        # Add new AI health check with components
        self.add_health_check(AIModelHealthCheck(text_generator, image_generator))
        logger.debug("Updated AI model health check with components")
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks"""
        if not self.enabled:
            return {}
        
        results = {}
        
        for health_check in self.health_checks:
            try:
                result = health_check.check()
                results[health_check.name] = result
                self.last_results[health_check.name] = result
                
                # Log based on status
                if result.status == HealthStatus.CRITICAL:
                    logger.error(f"🚨 Health check CRITICAL - {result.name}: {result.message}")
                elif result.status == HealthStatus.WARNING:
                    logger.warning(f"⚠️ Health check WARNING - {result.name}: {result.message}")
                else:
                    logger.debug(f"✅ Health check OK - {result.name}: {result.message}")
                    
            except Exception as e:
                error_result = HealthCheckResult(
                    name=health_check.name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {e}",
                    details={"error": str(e)},
                    timestamp=datetime.now(),
                    execution_time_ms=0
                )
                results[health_check.name] = error_result
                self.last_results[health_check.name] = error_result
                logger.error(f"❌ Health check error - {health_check.name}: {e}")
        
        return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        if not self.last_results:
            self.run_all_checks()
        
        if not self.last_results:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks available",
                "timestamp": datetime.now().isoformat(),
                "checks": {}
            }
        
        # Determine overall status
        statuses = [result.status for result in self.last_results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif HealthStatus.UNKNOWN in statuses:
            overall_status = HealthStatus.WARNING  # Treat unknown as warning
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Count by status
        status_counts = {}
        for status in HealthStatus:
            status_counts[status.value] = sum(1 for s in statuses if s == status)
        
        # Generate summary message
        if overall_status == HealthStatus.HEALTHY:
            message = "All systems operational"
        else:
            issues = [result.message for result in self.last_results.values() 
                     if result.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]]
            message = f"{len(issues)} issues detected"
        
        return {
            "status": overall_status.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(self.last_results),
                "status_counts": status_counts
            },
            "checks": {name: result.to_dict() for name, result in self.last_results.items()}
        }
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if not self.enabled:
            return
        
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._stop_monitoring.clear()
            self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
            logger.info(f"🏥 Health monitoring started (interval: {self.check_interval}s)")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("🏥 Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while not self._stop_monitoring.is_set():
            try:
                self.run_all_checks()
            except Exception as e:
                logger.error(f"❌ Error in health monitoring loop: {e}")
            
            # Wait for next interval
            self._stop_monitoring.wait(self.check_interval)
    
    def export_health_report(self, output_path: str = "logs/health_report.json"):
        """Export health report to file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            health_data = self.get_overall_health()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(health_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🏥 Health report exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error exporting health report: {e}")
            return None