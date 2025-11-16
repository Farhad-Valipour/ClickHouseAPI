"""
Main FastAPI application with Phase 2 enhancements.

Phase 2 Features:
- Structured logging
- Logging middleware
- Async endpoints
- Enhanced error handling
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.core.exceptions import BaseAPIException
from app.core.database import ClickHouseManager
from app.core.logging_config import logger
from app.middleware.logging import LoggingMiddleware
from app.routers import health_router
from app.routers.ohlcv import router as ohlcv_router


# ============================================================================
# Create FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    A production-ready REST API for accessing OHLCV (Open, High, Low, Close, Volume) 
    data from ClickHouse database.
    
    ## Phase 2 Features
    
    * 📊 **Structured Logging**: JSON-formatted logs with request tracking
    * ⚡ **Async Endpoints**: Non-blocking I/O for better performance
    * 🔍 **Request Tracking**: Unique request IDs for debugging
    * 📈 **Performance Metrics**: Query timing and monitoring
    
    ## Features
    
    * 🔒 **Secure**: SQL injection protected with parameterized queries
    * ⚡ **Fast**: Optimized queries with connection pooling
    * 📊 **Paginated**: Support for large datasets with pagination
    * ✅ **Validated**: Automatic request validation with Pydantic
    * 📚 **Documented**: Auto-generated OpenAPI documentation
    
    ## Endpoints
    
    * **Health Checks**: `/health`, `/health/ready`, `/health/live`
    * **OHLCV Data**: `/api/v1/ohlcv`, `/api/v1/ohlcv/latest`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.DEBUG,
)


# ============================================================================
# Middleware
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware (Phase 2)
app.add_middleware(LoggingMiddleware)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle all custom API exceptions with logging."""
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions with logging."""
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": str(exc),
            "details": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with logging."""
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred. Please try again later.",
            "details": {} if settings.is_production() else {"error": str(exc)},
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks with enhanced logging."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"ClickHouse: {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Log Format: {settings.LOG_FORMAT}")
    
    # Initialize database connection
    db = ClickHouseManager()
    try:
        db.connect()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        logger.warning("API will start but database endpoints may fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks with enhanced logging."""
    logger.info(f"Shutting down {settings.APP_NAME}")
    
    # Close database connections
    db = ClickHouseManager()
    db.close()
    logger.info("Database connections closed successfully")
    logger.info("Shutdown complete")


# ============================================================================
# Include Routers
# ============================================================================

# Health check endpoints (no prefix)
app.include_router(
    health_router,
    tags=["Health"]
)

# OHLCV data endpoints (with API prefix) - Async version
app.include_router(
    ohlcv_router,
    prefix=settings.API_PREFIX,
    tags=["OHLCV"]
)


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Information",
    description="Get basic information about the API"
)
async def root():
    """Root endpoint providing API information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "phase": "Phase 2 - Production Ready",
        "features": {
            "structured_logging": True,
            "async_endpoints": True,
            "request_tracking": True,
            "performance_metrics": True
        },
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "ohlcv": f"{settings.API_PREFIX}/ohlcv"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
