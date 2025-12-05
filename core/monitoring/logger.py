"""Centralized logging configuration for Mare Enterprise."""

import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json
from pathlib import Path

from core.config.settings import config


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class MareLogger:
    """Mare Enterprise logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger with appropriate handlers and formatters."""
        if self.logger.handlers:
            return  # Already configured
        
        # Set log level
        log_level = getattr(logging, config.monitoring.log_level.upper())
        self.logger.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Use JSON formatter in production, simple formatter in development
        if config.environment == "production":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler for production
        if config.environment == "production":
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / "mare.log")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with extra fields support."""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self.logger.log(level, message, extra=extra)


# Global logger instances
_loggers: Dict[str, MareLogger] = {}


def get_logger(name: str) -> MareLogger:
    """Get or create a logger instance."""
    if name not in _loggers:
        _loggers[name] = MareLogger(name)
    return _loggers[name]


# Default logger
logger = get_logger("mare")


# Metrics tracking
class MetricsTracker:
    """Simple metrics tracking for agent execution."""

    def __init__(self):
        self._metrics = {}

    def timer(self, metric_name: str, tags: Dict[str, Any] = None):
        """Context manager for timing operations."""
        from contextlib import contextmanager
        import time

        @contextmanager
        def _timer():
            start = time.time()
            try:
                yield
            finally:
                duration = time.time() - start
                self.record(metric_name, duration, tags)

        return _timer()

    def record(self, metric_name: str, value: float, tags: Dict[str, Any] = None):
        """Record a metric value."""
        key = f"{metric_name}:{tags}" if tags else metric_name
        if key not in self._metrics:
            self._metrics[key] = []
        self._metrics[key].append(value)
        logger.debug(f"Metric recorded: {metric_name} = {value}", tags=tags)

    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        return self._metrics


# Global metrics tracker
metrics = MetricsTracker()


def record_agent_execution(agent_name: str, elapsed_time: float, success: bool):
    """Record agent execution metrics."""
    metrics.record("agent_execution_time", elapsed_time, {"agent": agent_name, "success": success})
    logger.info(
        f"Agent execution recorded: {agent_name}",
        elapsed_time=elapsed_time,
        success=success
    )