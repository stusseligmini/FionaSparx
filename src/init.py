"""
FionaSparx AI Content Creator - Utils Package

Dette er en samling av hjelpeverktøy for FionaSparx AI Content Creator-plattformen.
Gir funksjonalitet for logging, planlegging, feilhåndtering, CLI-forbedringer, 
kvalitetsvurdering og plattformspesifikke maler.
"""

# Import eksisterende funksjonalitet
from .logger import setup_logging, JSONLogHandler, PerformanceLogger
from .scheduler import ContentScheduler

# Import nye moduler
from .Error_handling import CircuitBreaker, retry, FallbackHandler
from .cli_progress import ProgressBar, ConsoleUI, ProgressStyle, Colors
from .quality_assessment import ContentQualityAssessor, ContentType, QualityLevel, QualityScore
from .platform_templates import PlatformTemplateManager

__all__ = [
    # Eksisterende
    'setup_logging', 'JSONLogHandler', 'PerformanceLogger',
    'ContentScheduler',
    
    # Nye
    'CircuitBreaker', 'retry', 'FallbackHandler',
    'ProgressBar', 'ConsoleUI', 'ProgressStyle', 'Colors',
    'ContentQualityAssessor', 'ContentType', 'QualityLevel', 'QualityScore',
    'PlatformTemplateManager'
]

# Versjon av utils-pakken
__version__ = '1.1.0'
