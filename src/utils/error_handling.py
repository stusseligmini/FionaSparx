#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Handling Utilities for FionaSparx
Provides circuit breaker, retry mechanisms, and fallback handlers
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker pattern for handling API failures gracefully"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time < self.timeout:
                raise Exception("Circuit breaker is OPEN - refusing call")
            else:
                self.state = CircuitState.HALF_OPEN
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
            
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        
    def _on_failure(self):
        """Handle failure - increment count and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed. Last error: {e}")
                        
            raise last_exception
        return wrapper
    return decorator

class FallbackHandler:
    """Provides fallback mechanisms for failed operations"""
    
    def __init__(self):
        self.fallback_strategies: Dict[str, Callable] = {}
        
    def register_fallback(self, operation: str, fallback_func: Callable):
        """Register a fallback function for a specific operation"""
        self.fallback_strategies[operation] = fallback_func
        logger.info(f"Registered fallback for operation: {operation}")
        
    def execute_with_fallback(self, operation: str, primary_func: Callable, *args, **kwargs) -> Any:
        """Execute primary function with fallback if it fails"""
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary operation '{operation}' failed: {e}")
            
            if operation in self.fallback_strategies:
                logger.info(f"Executing fallback for operation: {operation}")
                try:
                    return self.fallback_strategies[operation](*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise fallback_error
            else:
                logger.error(f"No fallback registered for operation: {operation}")
                raise e

class ErrorAggregator:
    """Collects and manages error information for reporting"""
    
    def __init__(self):
        self.errors: List[Dict] = []
        
    def add_error(self, operation: str, error: Exception, context: Optional[Dict] = None):
        """Add an error to the collection"""
        error_info = {
            "timestamp": time.time(),
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self.errors.append(error_info)
        logger.error(f"Error in {operation}: {error}")
        
    def get_error_summary(self) -> Dict:
        """Get summary of collected errors"""
        if not self.errors:
            return {"total_errors": 0, "summary": "No errors recorded"}
            
        error_types = {}
        for error in self.errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "recent_errors": self.errors[-5:] if len(self.errors) > 5 else self.errors
        }
        
    def clear_errors(self):
        """Clear the error collection"""
        self.errors.clear()
        logger.info("Error collection cleared")

# Global instances for easy access
default_circuit_breaker = CircuitBreaker()
default_fallback_handler = FallbackHandler()
default_error_aggregator = ErrorAggregator()