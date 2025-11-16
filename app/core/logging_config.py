"""
Structured logging configuration.

This module provides JSON-formatted logging with request tracking
and performance metrics.
"""

import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime

from app.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Converts log records to JSON format with consistent structure.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        
        if hasattr(record, "method"):
            log_data["method"] = record.method
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "user_agent"):
            log_data["user_agent"] = record.user_agent
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Setup application logging.
    
    Configures logging based on settings with either JSON or text format.
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("clickhouse_api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on LOG_FORMAT setting
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Create global logger instance
logger = setup_logging()


def log_request(
    request_id: str,
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    user_agent: str = None
) -> None:
    """
    Log HTTP request with structured data.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint/path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_agent: User agent string (optional)
    """
    extra = {
        "request_id": request_id,
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    
    if user_agent:
        extra["user_agent"] = user_agent
    
    if status_code >= 500:
        logger.error("Request failed", extra=extra)
    elif status_code >= 400:
        logger.warning("Request error", extra=extra)
    else:
        logger.info("Request completed", extra=extra)


def log_database_query(
    query_type: str,
    duration_ms: float,
    records_returned: int = None,
    error: str = None
) -> None:
    """
    Log database query execution.
    
    Args:
        query_type: Type of query (SELECT, INSERT, etc.)
        duration_ms: Query duration in milliseconds
        records_returned: Number of records returned (optional)
        error: Error message if query failed (optional)
    """
    extra = {
        "query_type": query_type,
        "duration_ms": duration_ms,
    }
    
    if records_returned is not None:
        extra["records_returned"] = records_returned
    
    if error:
        extra["error"] = error
        logger.error("Database query failed", extra=extra)
    else:
        logger.info("Database query executed", extra=extra)
