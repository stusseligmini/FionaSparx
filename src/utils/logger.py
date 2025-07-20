import logging
import logging.handlers
import os
from datetime import datetime
import json

def setup_logging(config):
    """Sett opp avansert logging system"""
    
    # Opprett logs-mappe
    os.makedirs("logs", exist_ok=True)
    
    # Konfigurer hovedlogger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Fjern eksisterende handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Format for logg-meldinger
    formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - roterende filer
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/fiona_sparx.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error handler - separat fil for feil
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # JSON handler for strukturerte logger (for analyse)
    json_handler = JSONLogHandler('logs/structured.log')
    json_handler.setLevel(logging.INFO)
    logger.addHandler(json_handler)
    
    # Sett logging-nivå for eksterne biblioteker
    logging.getLogger('diffusers').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    return logger

class JSONLogHandler(logging.Handler):
    """Custom handler for JSON-strukturerte logger"""
    
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
    
    def emit(self, record):
        """Emit en JSON-formatert logg-oppføring"""
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Legg til exception info hvis tilgjengelig
            if record.exc_info:
                log_entry["exception"] = self.format(record)
            
            # Skriv til fil
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception:
            self.handleError(record)

class PerformanceLogger:
    """Logger for ytelsesmålinger"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
        
    def log_generation_time(self, content_type, duration, success=True):
        """Logg tid for innholdsgenerering"""
        self.logger.info(
            f"Generation {content_type}: {duration:.2f}s {'✅' if success else '❌'}"
        )
    
    def log_publish_time(self, platform, duration, success=True):
        """Logg tid for publisering"""
        self.logger.info(
            f"Publish {platform}: {duration:.2f}s {'✅' if success else '❌'}"
        )
    
    def log_engagement_metrics(self, content_id, platform, metrics):
        """Logg engagement-målinger"""
        self.logger.info(
            f"Engagement {content_id} on {platform}: "
            f"Likes: {metrics.get('likes', 0)}, "
            f"Comments: {metrics.get('comments', 0)}, "
            f"Shares: {metrics.get('shares', 0)}"
        )

# Opprett global performance logger
performance_logger = PerformanceLogger()
