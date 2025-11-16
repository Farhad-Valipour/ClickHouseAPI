"""
Response models for API endpoints.

These models ensure consistent response formatting and automatic
JSON serialization with proper type handling.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class OHLCVData(BaseModel):
    """
    Single OHLCV candle data point.
    
    Represents one candlestick with open, high, low, close prices
    and volume.
    """
    
    candle_time: datetime = Field(
        ...,
        description="Timestamp of the candle"
    )
    
    symbol: str = Field(
        ...,
        description="Trading symbol"
    )
    
    open: float = Field(
        ...,
        description="Opening price"
    )
    
    high: float = Field(
        ...,
        description="Highest price"
    )
    
    low: float = Field(
        ...,
        description="Lowest price"
    )
    
    close: float = Field(
        ...,
        description="Closing price"
    )
    
    volume: float = Field(
        ...,
        description="Trading volume"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "candle_time": "2025-07-01T00:00:00",
                "symbol": "BINANCE:BTCUSDT.P",
                "open": 50000.0,
                "high": 51000.0,
                "low": 49500.0,
                "close": 50500.0,
                "volume": 1234567.89
            }
        }


class ResponseMetadata(BaseModel):
    """
    Metadata for paginated API responses.
    
    Provides information about the current page, total records,
    and whether more data is available.
    """
    
    total_records: int = Field(
        ...,
        description="Total number of records returned in this response"
    )
    
    limit: int = Field(
        ...,
        description="Limit used in the query"
    )
    
    offset: int = Field(
        ...,
        description="Offset used in the query"
    )
    
    has_more: bool = Field(
        ...,
        description="Whether more records are available"
    )
    
    query_time_ms: float = Field(
        ...,
        description="Query execution time in milliseconds"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response generation timestamp"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OHLCVResponse(BaseModel):
    """
    Standard response for OHLCV data endpoints.
    
    Contains the data array and metadata about the response.
    """
    
    success: bool = Field(
        default=True,
        description="Whether the request was successful"
    )
    
    data: List[OHLCVData] = Field(
        ...,
        description="Array of OHLCV data points"
    )
    
    metadata: ResponseMetadata = Field(
        ...,
        description="Response metadata including pagination info"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {
                        "candle_time": "2025-07-01T00:00:00",
                        "symbol": "BINANCE:BTCUSDT.P",
                        "open": 50000.0,
                        "high": 51000.0,
                        "low": 49500.0,
                        "close": 50500.0,
                        "volume": 1234567.89
                    }
                ],
                "metadata": {
                    "total_records": 1,
                    "limit": 1000,
                    "offset": 0,
                    "has_more": False,
                    "query_time_ms": 45.2,
                    "timestamp": "2025-11-13T10:30:45.123Z"
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    
    Used for all error responses to ensure consistency.
    """
    
    success: bool = Field(
        default=False,
        description="Always false for errors"
    )
    
    error_code: str = Field(
        ...,
        description="Machine-readable error code"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details and context"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error occurrence timestamp"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid time format",
                "details": {
                    "field": "start",
                    "provided": "bad-format",
                    "expected": "YYYYMMDD-HHmm"
                },
                "timestamp": "2025-11-13T10:30:45.123Z"
            }
        }


# ============================================================================
# Health Check Models
# ============================================================================

class HealthCheck(BaseModel):
    """Health status for a single component."""
    
    status: str = Field(
        ...,
        description="Health status: 'up' or 'down'"
    )
    
    response_time_ms: Optional[float] = Field(
        None,
        description="Response time in milliseconds"
    )
    
    error: Optional[str] = Field(
        None,
        description="Error message if status is down"
    )


class HealthResponse(BaseModel):
    """Basic health check response."""
    
    status: str = Field(
        ...,
        description="Overall health status: 'healthy' or 'unhealthy'"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-11-13T10:30:45.123Z"
            }
        }


class DetailedHealthResponse(BaseModel):
    """Detailed health check response with component status."""
    
    status: str = Field(
        ...,
        description="Overall health status"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    
    checks: Dict[str, HealthCheck] = Field(
        ...,
        description="Individual component health checks"
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-11-13T10:30:45.123Z",
                "checks": {
                    "database": {
                        "status": "up",
                        "response_time_ms": 12.5
                    },
                    "api": {
                        "status": "up"
                    }
                }
            }
        }
