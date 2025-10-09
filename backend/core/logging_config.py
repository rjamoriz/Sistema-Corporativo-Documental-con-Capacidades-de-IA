"""
Logging Configuration
Structured JSON logging with rotation
"""
import logging
import sys
from pathlib import Path
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

from core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add level
        log_record['level'] = record.levelname
        
        # Add service name
        log_record['service'] = settings.APP_NAME
        
        # Add version
        log_record['version'] = settings.VERSION


def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT == "json":
        # JSON formatter
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for errors
    error_file_handler = logging.FileHandler(log_dir / "error.log")
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    root_logger.addHandler(error_file_handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Audit log handler (append-only, immutable)
    audit_logger = logging.getLogger("audit")
    audit_handler = logging.FileHandler(log_dir / "audit.log", mode='a')
    audit_handler.setFormatter(formatter)
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False
    
    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_audit_logger():
    """Get audit logger for immutable logs"""
    return logging.getLogger("audit")
