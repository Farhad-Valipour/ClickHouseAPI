"""
Core module containing essential components.

This module includes:
- database: ClickHouse connection management
- exceptions: Custom exception hierarchy
- logging_config: Structured logging (Phase 2)
"""

from app.core.database import ClickHouseManager
from app.core.exceptions import (
    BaseAPIException,
    DatabaseException,
    ConnectionError,
    QueryError,
    TimeoutError,
    ValidationException,
    InvalidTimeFormatError,
    InvalidSymbolError,
    ResourceNotFoundException,
    DataNotFoundError,
)

__all__ = [
    # Database
    "ClickHouseManager",
    
    # Exceptions
    "BaseAPIException",
    "DatabaseException",
    "ConnectionError",
    "QueryError",
    "TimeoutError",
    "ValidationException",
    "InvalidTimeFormatError",
    "InvalidSymbolError",
    "ResourceNotFoundException",
    "DataNotFoundError",
]
