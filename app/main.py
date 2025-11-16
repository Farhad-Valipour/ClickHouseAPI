"""
Main FastAPI application.

This module creates and configures the FastAPI application with
routers, middleware, exception handlers, and lifecycle events.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

from app.config import settings
from app.core.exceptions import BaseAPIException
from app.core.database import ClickHouseManager
from app.routers import health_router, ohlcv_router


# ============================================================================
# Create FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    A production-ready REST API for accessing OHLCV (Open, High, Low, Close, Volume) 
    data from ClickHouse database.
    
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
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request Timing Middleware
# ============================================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add processing time header to all responses.
    
    This middleware tracks how long each request takes to process
    and adds the information to the response headers.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """
    Handle all custom API exceptions.
    
    This handler ensures consistent error response format for all
    custom exceptions in the application.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions (typically from validation).
    
    Converts Python ValueError to a proper API error response.
    """
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
    """
    Handle all unhandled exceptions.
    
    This is the last resort handler that catches any exception that
    wasn't handled by more specific handlers. It ensures the API
    never returns unformatted error responses.
    
    Note: In production, we don't expose internal error details.
    """
    # TODO: Add structured logging in Phase 2
    # logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
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
    """
    Application startup tasks.
    
    This runs once when the application starts. We use it to:
    - Initialize database connections
    - Verify configuration
    - Log startup information
    """
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 ClickHouse: {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}")
    
    # Initialize database connection
    db = ClickHouseManager()
    try:
        db.connect()
        print("✅ Database connection established")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
        print("   API will start but database endpoints may fail")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks.
    
    This runs once when the application shuts down. We use it to:
    - Close database connections gracefully
    - Cleanup resources
    - Log shutdown information
    """
    print(f"🛑 Shutting down {settings.APP_NAME}")
    
    # Close database connections
    db = ClickHouseManager()
    db.close()
    print("✅ Database connections closed")


# ============================================================================
# Include Routers
# ============================================================================

# Health check endpoints (no prefix)
app.include_router(
    health_router,
    tags=["Health"]
)

# OHLCV data endpoints (with API prefix)
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
    """
    Root endpoint providing API information.
    
    Returns basic information about the API including version,
    available endpoints, and documentation links.
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
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
# Run Application (for development)
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
