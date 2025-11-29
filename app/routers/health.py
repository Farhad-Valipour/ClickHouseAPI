"""
Health check endpoints.

These endpoints provide health status information for monitoring
and orchestration tools (e.g., Kubernetes health probes).
"""

from fastapi import APIRouter
from datetime import datetime
import time

from app.config import settings
from app.core.database import ClickHouseManager
from app.core.logging_config import logger


router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Check API and database health status",
    tags=["Health"],
    responses={
        200: {"description": "API is healthy"},
        503: {"description": "API is unhealthy"},
    }
)
async def health_check():
    """
    Check the health status of the API and database connection.
    
    **Returns:**
    - `success`: Whether the health check passed
    - `status`: Overall health status (healthy/unhealthy)
    - `timestamp`: Current server timestamp
    - `database`: Database connection status
    - `version`: API version
    - `query_time_ms`: Health check execution time
    """
    start_time = time.time()
    
    try:
        db = ClickHouseManager()
        
        # Check database connection
        db_start = time.time()
        db_health = db.health_check()
        ping_duration = (time.time() - db_start) * 1000
        
        # Calculate total query time
        query_time_ms = (time.time() - start_time) * 1000
        
        if db_health["status"] != "up":
            logger.error("Database connection failed")
            return {
                "success": False,
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": {
                    "connected": False,
                    "error": db_health.get("error", "Failed to ping database")
                },
                "version": settings.APP_VERSION,
                "query_time_ms": round(query_time_ms, 2)
            }
        
        logger.info(f"Health check successful, ping_ms={round(ping_duration, 2)}")
        
        return {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connected": True,
                "ping_ms": round(ping_duration, 2)
            },
            "version": settings.APP_VERSION,
            "query_time_ms": round(query_time_ms, 2)
        }
    
    except Exception as e:
        query_time_ms = (time.time() - start_time) * 1000
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connected": False,
                "error": str(e)
            },
            "version": settings.APP_VERSION,
            "query_time_ms": round(query_time_ms, 2)
        }


@router.get(
    "/health/ready",
    summary="Readiness check",
    description="Check if API is ready to handle requests",
    tags=["Health"]
)
async def readiness_check():
    """
    Check if the API is ready to handle requests.
    Used by orchestration systems like Kubernetes.
    """
    try:
        db = ClickHouseManager()
        
        # Check if database manager is initialized
        if db._client is None:
            return {
                "success": False,
                "ready": False,
                "reason": "Database not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Verify connection
        db_health = db.health_check()
        
        if db_health["status"] != "up":
            return {
                "success": False,
                "ready": False,
                "reason": "Database connection unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "ready": False,
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get(
    "/health/live",
    summary="Liveness check",
    description="Check if API is alive",
    tags=["Health"]
)
async def liveness_check():
    """
    Check if the API is alive.
    Used by orchestration systems like Kubernetes.
    """
    return {
        "success": True,
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
