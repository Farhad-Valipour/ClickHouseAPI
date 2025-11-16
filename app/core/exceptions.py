"""
Custom exception hierarchy for API errors.

This module defines a structured exception hierarchy for handling
all types of errors in the application, from database errors to
validation errors.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class BaseAPIException(Exception):
    """
    Base exception for all API errors.
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling and response formatting.
    
    Attributes:
        status_code: HTTP status code for the error
        error_code: Machine-readable error identifier
        message: Human-readable error message
        details: Additional context about the error
    """
    
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code (overrides class default)
            error_code: Error identifier (overrides class default)
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.
        
        Returns:
            Dictionary containing error information
        """
        return {
            "success": False,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# Database Exceptions
# ============================================================================

class DatabaseException(BaseAPIException):
    """Base exception for all database-related errors."""
    
    status_code = 503  # Service Unavailable
    error_code = "DATABASE_ERROR"


class ConnectionError(DatabaseException):
    """Raised when unable to connect to ClickHouse."""
    
    error_code = "DATABASE_CONNECTION_ERROR"
    
    def __init__(
        self,
        message: str = "Unable to connect to database",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, details=details)


class QueryError(DatabaseException):
    """Raised when a database query fails."""
    
    error_code = "DATABASE_QUERY_ERROR"
    
    def __init__(
        self,
        message: str = "Failed to execute database query",
        query: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if query:
            # Don't expose full query in production - just for debugging
            details["query_preview"] = query[:100] + "..." if len(query) > 100 else query
        super().__init__(message=message, details=details)


class TimeoutError(DatabaseException):
    """Raised when a database query times out."""
    
    error_code = "DATABASE_TIMEOUT_ERROR"
    
    def __init__(
        self,
        message: str = "Database query timed out",
        timeout: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if timeout:
            details["timeout_seconds"] = timeout
        super().__init__(message=message, details=details)


# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationException(BaseAPIException):
    """Base exception for all validation errors."""
    
    status_code = 422  # Unprocessable Entity
    error_code = "VALIDATION_ERROR"


class InvalidTimeFormatError(ValidationException):
    """Raised when time format is invalid."""
    
    error_code = "INVALID_TIME_FORMAT"
    
    def __init__(
        self,
        message: str = "Invalid time format",
        provided: Optional[str] = None,
        expected: str = "YYYYMMDD-HHmm",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if provided:
            details["provided"] = provided
        details["expected_format"] = expected
        super().__init__(message=message, details=details)


class InvalidSymbolError(ValidationException):
    """Raised when symbol format is invalid."""
    
    error_code = "INVALID_SYMBOL"
    
    def __init__(
        self,
        message: str = "Invalid symbol format",
        symbol: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if symbol:
            details["symbol"] = symbol
        super().__init__(message=message, details=details)


# ============================================================================
# Resource Exceptions
# ============================================================================

class ResourceNotFoundException(BaseAPIException):
    """Base exception for resource not found errors."""
    
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"


class DataNotFoundError(ResourceNotFoundException):
    """Raised when requested data is not found."""
    
    error_code = "DATA_NOT_FOUND"
    
    def __init__(
        self,
        message: str = "No data found for the given parameters",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if resource:
            details["resource"] = resource
        super().__init__(message=message, details=details)
