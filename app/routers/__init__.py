"""
API routers for different endpoints.

This module contains routers for:
- Health checks
- OHLCV data endpoints
"""

from app.routers.health import router as health_router
from app.routers.ohlcv import router as ohlcv_router

__all__ = [
    "health_router",
    "ohlcv_router",
]
