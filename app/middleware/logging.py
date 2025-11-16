"""
Logging middleware for request/response tracking.

This middleware logs all incoming requests and their responses
with performance metrics.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging_config import log_request


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    This middleware:
    - Generates unique request IDs
    - Tracks request duration
    - Logs request/response details
    - Adds request ID to response headers
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Get user agent
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Log request
        log_request(
            request_id=request_id,
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            user_agent=user_agent
        )
        
        return response
