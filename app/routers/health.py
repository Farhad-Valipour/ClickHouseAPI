"""
Health check endpoints.

These endpoints provide health status information for monitoring
and orchestration tools (e.g., Kubernetes health probes).
"""

from fastapi import APIRouter
from datetime import datetime

from app.config import settings
from app.core.database import ClickHouseManager
from app.models.response import (
    HealthResponse,
    DetailedHealthResponse,
    HealthCheck,
)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Basic health check",
    description="Returns basic health status of the API",
    tags=["Health"]
)
async def health_check():
    """
    Basic health check endpoint.
    
    This is a simple endpoint that returns the API status and version.
    Useful for basic uptime monitoring.
    
    Returns:
        HealthResponse with status and version
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/health/ready",
    response_model=DetailedHealthResponse,
    summary="Readiness check",
    description="Returns detailed health status including database connectivity",
    tags=["Health"]
)
async def readiness_check():
    """
    Readiness check endpoint.
    
    This endpoint checks if the API is ready to serve requests by
    verifying that all dependencies (like the database) are available.
    
    Useful for Kubernetes readiness probes.
    
    Returns:
        DetailedHealthResponse with status of all components
    """
    db = ClickHouseManager()
    
    # Check database health
    db_health = db.health_check()
    
    # Check API health (always up if we can respond)
    api_health = HealthCheck(status="up")
    
    # Determine overall status
    all_healthy = db_health["status"] == "up"
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    return DetailedHealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        checks={
            "database": HealthCheck(
                status=db_health["status"],
                response_time_ms=db_health.get("response_time_ms"),
                error=db_health.get("error")
            ),
            "api": api_health
        }
    )


@router.get(
    "/health/live",
    summary="Liveness check",
    description="Simple ping endpoint for liveness probes",
    tags=["Health"]
)
async def liveness_check():
    """
    Liveness check endpoint.
    
    This is the simplest health check that just verifies the API
    process is running and can respond to requests.
    
    Useful for Kubernetes liveness probes.
    
    Returns:
        Simple status message
    """
    return {"status": "ok"}
