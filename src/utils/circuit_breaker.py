"""
Circuit Breaker Pattern Implementation
Enterprise-grade resilience pattern for AI API calls

Features:
- Circuit breaker pattern to prevent cascade failures
- Exponential backoff for retries
- Health monitoring and automatic recovery
- Configurable failure thresholds and timeouts
- Metrics collection for monitoring

Author: FionaSparx AI Content Creator
Version: 2.0.0 - Enterprise Edition
"""

import time
import logging
import asyncio
from typing import Callable, Any, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field
from threading import Lock
import random
import functools

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures detected, circuit is open
    HALF_OPEN = "half_open"  # Testing if service has recovered

@dataclass
class CircuitMetrics:
    """Circuit breaker metrics for monitoring"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    circuit_opened_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_calls == 0:
            return 100.0
        return (self.successful_calls / self.total_calls) * 100.0
    
    def failure_rate(self) -> float:
        """Calculate failure rate percentage"""
        return 100.0 - self.success_rate()

class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """Circuit breaker implementation for AI API resilience"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 expected_exception: type = Exception,
                 name: str = "default"):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time to wait before attempting half-open state
            expected_exception: Exception type that should trigger circuit opening
            name: Name for logging and monitoring
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._lock = Lock()
        self.metrics = CircuitMetrics()
        
        logger.info(f"🔒 Circuit breaker '{name}' initialized (threshold: {failure_threshold}, timeout: {timeout}s)")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self._call(func, *args, **kwargs)
        return wrapper
    
    def _call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            self.metrics.total_calls += 1
            
            # Check if circuit should be opened due to failures
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"🔄 Circuit breaker '{self.name}' entering HALF_OPEN state")
                else:
                    self.metrics.failed_calls += 1
                    raise CircuitBreakerError(f"Circuit breaker '{self.name}' is OPEN")
        
        # Attempt to execute the function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self.timeout
    
    def _on_success(self):
        """Handle successful function execution"""
        with self._lock:
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._reset()
                logger.info(f"✅ Circuit breaker '{self.name}' reset to CLOSED state")
            
            self._failure_count = 0
            self.metrics.consecutive_failures = 0
    
    def _on_failure(self):
        """Handle failed function execution"""
        with self._lock:
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = time.time()
            self._failure_count += 1
            self.metrics.consecutive_failures += 1
            
            if self._failure_count >= self.failure_threshold:
                if self._state != CircuitState.OPEN:
                    self._trip()
    
    def _trip(self):
        """Trip the circuit breaker to OPEN state"""
        self._state = CircuitState.OPEN
        self._last_failure_time = time.time()
        self.metrics.circuit_opened_count += 1
        logger.warning(f"⚡ Circuit breaker '{self.name}' OPENED after {self._failure_count} failures")
    
    def _reset(self):
        """Reset circuit breaker to CLOSED state"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
    
    def force_open(self):
        """Manually force circuit breaker to open"""
        with self._lock:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.time()
            self.metrics.circuit_opened_count += 1
            logger.warning(f"🚨 Circuit breaker '{self.name}' manually forced OPEN")
    
    def force_close(self):
        """Manually force circuit breaker to close"""
        with self._lock:
            self._reset()
            logger.info(f"🔧 Circuit breaker '{self.name}' manually forced CLOSED")
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit breaker state"""
        return self._state
    
    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit breaker is closed"""
        return self._state == CircuitState.CLOSED
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "current_failures": self._failure_count,
            "metrics": {
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "success_rate": self.metrics.success_rate(),
                "failure_rate": self.metrics.failure_rate(),
                "circuit_opened_count": self.metrics.circuit_opened_count,
                "consecutive_failures": self.metrics.consecutive_failures,
                "last_failure_time": self.metrics.last_failure_time,
                "last_success_time": self.metrics.last_success_time
            }
        }

class ExponentialBackoff:
    """Exponential backoff for retry logic"""
    
    def __init__(self, 
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 multiplier: float = 2.0,
                 jitter: bool = True):
        """
        Initialize exponential backoff
        
        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            multiplier: Multiplier for each retry
            jitter: Add random jitter to prevent thundering herd
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        delay = min(self.base_delay * (self.multiplier ** attempt), self.max_delay)
        
        if self.jitter:
            # Add ±20% jitter
            jitter_range = delay * 0.2
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)

class ResilientAIWrapper:
    """Wrapper for AI operations with circuit breaker and retry logic"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize resilient AI wrapper"""
        self.config = config
        error_config = config.get("error_handling", {})
        
        # Initialize circuit breakers for different AI operations
        self.text_circuit = CircuitBreaker(
            failure_threshold=error_config.get("circuit_breaker_failure_threshold", 5),
            timeout=error_config.get("circuit_breaker_timeout", 60),
            name="text_generation"
        )
        
        self.image_circuit = CircuitBreaker(
            failure_threshold=error_config.get("circuit_breaker_failure_threshold", 5),
            timeout=error_config.get("circuit_breaker_timeout", 60),
            name="image_generation"
        )
        
        # Initialize exponential backoff
        self.backoff = ExponentialBackoff(
            base_delay=error_config.get("retry_delay_base", 1.0),
            max_delay=60.0,
            multiplier=2.0,
            jitter=True
        )
        
        self.max_retries = error_config.get("max_retries", 3)
        self.exponential_backoff_enabled = error_config.get("exponential_backoff_enabled", True)
        
        logger.info("🛡️ Resilient AI wrapper initialized with circuit breakers")
    
    def execute_with_resilience(self, 
                               operation: Callable,
                               circuit_breaker: CircuitBreaker,
                               operation_name: str,
                               *args, **kwargs) -> Any:
        """Execute operation with resilience patterns"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Use circuit breaker
                @circuit_breaker
                def protected_operation():
                    return operation(*args, **kwargs)
                
                result = protected_operation()
                
                if attempt > 0:
                    logger.info(f"✅ {operation_name} succeeded on attempt {attempt + 1}")
                
                return result
                
            except CircuitBreakerError as e:
                logger.error(f"🚫 {operation_name} blocked by circuit breaker: {e}")
                raise e
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    if self.exponential_backoff_enabled:
                        delay = self.backoff.get_delay(attempt)
                        logger.warning(f"⚠️ {operation_name} failed (attempt {attempt + 1}), retrying in {delay:.2f}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.warning(f"⚠️ {operation_name} failed (attempt {attempt + 1}), retrying immediately: {e}")
                else:
                    logger.error(f"❌ {operation_name} failed after {self.max_retries + 1} attempts: {e}")
        
        # If we get here, all retries failed
        raise last_exception
    
    def generate_text_resilient(self, text_generator, *args, **kwargs) -> str:
        """Generate text with resilience patterns"""
        return self.execute_with_resilience(
            text_generator.generate_smart_caption,
            self.text_circuit,
            "Text generation",
            *args, **kwargs
        )
    
    def generate_image_resilient(self, image_generator, *args, **kwargs) -> Any:
        """Generate image with resilience patterns"""
        return self.execute_with_resilience(
            image_generator.generate_enhanced_image,
            self.image_circuit,
            "Image generation",
            *args, **kwargs
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all circuit breakers"""
        return {
            "text_generation": self.text_circuit.get_metrics(),
            "image_generation": self.image_circuit.get_metrics(),
            "overall_health": self._calculate_overall_health()
        }
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall health status"""
        circuits = [self.text_circuit, self.image_circuit]
        
        open_circuits = sum(1 for circuit in circuits if circuit.is_open)
        total_circuits = len(circuits)
        
        if open_circuits == 0:
            return "healthy"
        elif open_circuits < total_circuits:
            return "degraded"
        else:
            return "unhealthy"
    
    def reset_all_circuits(self):
        """Reset all circuit breakers"""
        self.text_circuit.force_close()
        self.image_circuit.force_close()
        logger.info("🔧 All circuit breakers reset")