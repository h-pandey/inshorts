"""
Enhanced logging configuration with comprehensive debugging support.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger

from .config import settings


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records."""
    
    def filter(self, record):
        # Add request ID if available
        if hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', 'N/A')
        return True


def setup_log_directory() -> Path:
    """Setup log directory and return path."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir


def create_file_handler(log_file: str, level: str = "INFO") -> logging.FileHandler:
    """Create a file handler with JSON formatting."""
    log_dir = setup_log_directory()
    file_path = log_dir / log_file
    
    handler = logging.FileHandler(file_path, encoding='utf-8')
    handler.setLevel(getattr(logging, level))
    
    # JSON formatter for file logs
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(json_formatter)
    
    return handler


def create_console_handler(level: str = "INFO") -> logging.StreamHandler:
    """Create a console handler with colored output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level))
    
    # Colored formatter for console
    console_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    formatter = ColoredFormatter(console_format, datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    # Add request context filter
    handler.addFilter(RequestContextFilter())
    
    return handler


def configure_logging() -> None:
    """Configure comprehensive application logging."""
    
    # Setup log directory
    log_dir = setup_log_directory()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = create_console_handler(settings.log_level)
    root_logger.addHandler(console_handler)
    
    # Add file handlers
    if settings.debug:
        # Debug file handler
        debug_handler = create_file_handler("debug.log", "DEBUG")
        root_logger.addHandler(debug_handler)
    
    # Application log file
    app_handler = create_file_handler("app.log", settings.log_level)
    root_logger.addHandler(app_handler)
    
    # Error log file
    error_handler = create_file_handler("error.log", "ERROR")
    root_logger.addHandler(error_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log startup message
    logger = get_logger(__name__)
    logger.info(
        "Logging system initialized",
        log_level=settings.log_level,
        debug_mode=settings.debug,
        log_directory=str(log_dir)
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_function_call(func_name: str, **kwargs):
    """Log function call with parameters."""
    logger = get_logger("function_calls")
    logger.debug(f"Calling {func_name}", function=func_name, parameters=kwargs)


def log_database_operation(operation: str, collection: str, **kwargs):
    """Log database operations."""
    logger = get_logger("database")
    logger.info(
        f"Database {operation}",
        operation=operation,
        collection=collection,
        **kwargs
    )


def log_api_request(method: str, path: str, status_code: int, duration_ms: float, **kwargs):
    """Log API requests."""
    logger = get_logger("api")
    logger.info(
        f"API {method} {path}",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )


def log_llm_request(model: str, tokens_used: int, cost: float, **kwargs):
    """Log LLM API requests."""
    logger = get_logger("llm")
    logger.info(
        f"LLM request to {model}",
        model=model,
        tokens_used=tokens_used,
        cost=cost,
        **kwargs
    )


def log_performance(operation: str, duration_ms: float, **kwargs):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(
        f"Performance: {operation}",
        operation=operation,
        duration_ms=duration_ms,
        **kwargs
    )
