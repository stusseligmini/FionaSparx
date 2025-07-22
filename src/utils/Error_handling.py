"""
Enhanced Error Handling Module with Circuit Breaker Patterns

This module provides resilience patterns for handling failures gracefully, 
including circuit breakers, retries, and fallback mechanisms.

Key Features:
- Circuit breaker pattern to prevent cascading failures
- Smart retry mechanisms with exponential backoff
- Fallback strategies for graceful degradation
- Error monitoring and reporting
- Self-healing capabilities

Author: FionaSparx AI Content Creator
Version: 1.0.0
"""

import time
import logging
import random
import functools
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Tilstander for circuit breaker"""
    CLOSED = "closed"      # Normal operasjon, tillater forespørsler
    OPEN = "open"          # Feilmodus, blokkerer forespørsler
    HALF_OPEN = "half_open"  # Test-modus, prøver forespørsler forsiktig


@dataclass
class CircuitBreakerConfig:
    """Konfigurasjon for circuit breaker"""
    failure_threshold: int = 5       # Antall feil før åpning
    reset_timeout: int = 30          # Sekunder før halvåpning
    test_requests: int = 2           # Antall testforespørsler i halvåpen tilstand
    timeout: float = 10.0            # Tidsavbrudd for operasjoner (sekunder)
    track_exceptions: list = None    # Spesifikke exceptions som skal spores


class CircuitBreaker:
    """
    Implementasjon av Circuit Breaker-mønsteret for resilience
    
    Forhindrer kaskaderende feil ved å avbryte operasjoner som feiler gjentatte ganger.
    """
    
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.successful_test_calls = 0
        
        logger.info(f"Circuit Breaker '{name}' initialisert i {self.state.value} tilstand")
    
    def __call__(self, func):
        """Dekoratør for funksjoner som skal beskyttes av circuit breaker"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(lambda: func(*args, **kwargs))
        return wrapper
    
    def execute(self, callable_func):
        """Utfør operasjon med circuit breaker-beskyttelse"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit '{self.name}' er åpen, forespørsler blokkert",
                    self.last_failure_time
                )
                
        try:
            result = callable_func()
            self._on_success()
            return result
            
        except Exception as e:
            return self._on_failure(e)
    
    def _on_success(self):
        """Håndter vellykket operasjon"""
        if self.state == CircuitState.HALF_OPEN:
            self.successful_test_calls += 1
            if self.successful_test_calls >= self.config.test_requests:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self, exception):
        """Håndter mislykket operasjon"""
        exceptions_to_track = self.config.track_exceptions
        
        # Hvis ingen spesifikke exceptions er angitt, spor alt
        # Ellers, sjekk om feilen er en av typene som skal spores
        if exceptions_to_track is None or any(
            isinstance(exception, ex_type) for ex_type in exceptions_to_track
        ):
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    self._transition_to_open()
            
            elif self.state == CircuitState.HALF_OPEN:
                self._transition_to_open()
        
        raise exception
    
    def _should_attempt_reset(self):
        """Sjekk om det er på tide å prøve å tilbakestille kretsen"""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.reset_timeout
    
    def _transition_to_open(self):
        """Endre tilstand til åpen"""
        prev_state = self.state
        self.state = CircuitState.OPEN
        self.successful_test_calls = 0
        logger.warning(f"Circuit Breaker '{self.name}' endret fra {prev_state.value} til {self.state.value}")
    
    def _transition_to_half_open(self):
        """Endre tilstand til halvåpen"""
        prev_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.successful_test_calls = 0
        logger.info(f"Circuit Breaker '{self.name}' endret fra {prev_state.value} til {self.state.value}")
    
    def _transition_to_closed(self):
        """Endre tilstand til lukket"""
        prev_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.successful_test_calls = 0
        logger.info(f"Circuit Breaker '{self.name}' endret fra {prev_state.value} til {self.state.value}")
    
    def reset(self):
        """Manuell tilbakestilling av kretsen til lukket tilstand"""
        self._transition_to_closed()


class CircuitBreakerOpenError(Exception):
    """Feil som kastes når circuit breaker er åpen"""
    
    def __init__(self, message, last_failure_time):
        self.last_failure_time = last_failure_time
        time_ago = datetime.now() - last_failure_time if last_failure_time else "ukjent tid"
        super().__init__(f"{message} (siste feil for {time_ago} siden)")


def retry(max_attempts=3, backoff_factor=2, max_backoff=30, exceptions=(Exception,)):
    """
    Dekoratør for å automatisk gjøre nye forsøk på funksjoner som feiler
    med eksponentiell backoff
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_attempts:
                        logger.error(f"Maks antall forsøk ({max_attempts}) nådd for {func.__name__}")
                        raise
                    
                    # Beregn ventetid med jitter for å unngå thundering herd
                    wait_time = min(backoff_factor ** attempt + random.uniform(0, 1), max_backoff)
                    logger.warning(f"Forsøk {attempt} mislyktes for {func.__name__}. Prøver igjen om {wait_time:.2f}s. Feil: {e}")
                    time.sleep(wait_time)
        return wrapper
    return decorator


class FallbackHandler:
    """
    Håndterer fallback-strategier når operasjoner mislykkes
    """
    
    @staticmethod
    def with_fallback(main_func, fallback_func, exceptions=(Exception,)):
        """Utfør en funksjon med fallback hvis den mislykkes"""
        try:
            return main_func()
        except exceptions as e:
            logger.warning(f"Hovedfunksjon mislyktes, bruker fallback. Feil: {e}")
            return fallback_func(e)
