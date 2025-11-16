"""
Custom middleware for request processing.

This module contains middleware for:
- Request logging
- Request ID tracking
- Performance monitoring
"""

from app.middleware.logging import LoggingMiddleware

__all__ = [
    "LoggingMiddleware",
]
