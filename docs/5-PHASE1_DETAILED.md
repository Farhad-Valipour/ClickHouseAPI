# Phase 1: Critical Fixes - مستندات تفصیلی

## 🎯 هدف Phase 1
رفع مشکلات حیاتی امنیتی و بنیادی پروژه و آماده‌سازی برای توسعه بعدی

**زمان تخمینی**: 1 روز کاری (6-8 ساعت)
**اولویت**: بالا 🔥

---

## 📋 Checklist کلی

- [ ] Setup Core Module
  - [ ] `app/core/database.py` - Connection Manager
  - [ ] `app/core/exceptions.py` - Exception Hierarchy
  - [ ] `app/core/__init__.py` - Package exports

- [ ] Setup Models Module
  - [ ] `app/models/request.py` - Request Schemas
  - [ ] `app/models/response.py` - Response Schemas
  - [ ] `app/models/__init__.py` - Package exports

- [ ] Refactor Routers
  - [ ] `app/routers/health.py` - Health Check (NEW)
  - [ ] `app/routers/ohlcv.py` - Refactored with safety
  - [ ] `app/routers/__init__.py` - Update exports

- [ ] Update Configuration
  - [ ] `app/config.py` - Enhanced settings
  - [ ] `.env.example` - Complete template

- [ ] Update Dependencies
  - [ ] `requirements.txt` - Add new packages

- [ ] Update Main App
  - [ ] `app/main.py` - Add exception handlers

---

## 📁 فایل‌های جدید و تغییرات

### فایل‌های جدید (7 فایل)
```
app/core/
├── __init__.py                 # 🆕 NEW
├── database.py                 # 🆕 NEW (~150 lines)
└── exceptions.py               # 🆕 NEW (~100 lines)

app/models/
├── __init__.py                 # 🆕 NEW
├── request.py                  # 🆕 NEW (~80 lines)
└── response.py                 # 🆕 NEW (~70 lines)

app/routers/
└── health.py                   # 🆕 NEW (~60 lines)
```

### فایل‌های تغییر یافته (5 فایل)
```
app/config.py                   # ✏️ MODIFY (expand)
app/main.py                     # ✏️ MODIFY (add handlers)
app/routers/ohlcv.py            # ✏️ MODIFY (complete refactor)
app/routers/__init__.py         # ✏️ MODIFY (add health router)
requirements.txt                # ✏️ MODIFY (add packages)
.env.example                    # ✏️ MODIFY (expand variables)
```

### فایل‌های حذف شده (1 فایل)
```
app/clickhouse_client.py        # ❌ DELETE (replaced by core/database.py)
```

---

## 🔧 جزئیات هر فایل

### 1. `app/core/database.py`

**مسئولیت**: مدیریت connection pool و اجرای query های امن

**کلاس‌ها:**
```python
class ClickHouseManager:
    """Singleton manager for ClickHouse connections"""
    
    Attributes:
        _instance: Singleton instance
        _client: ClickHouse client instance
        _pool: Connection pool (future)
        config: Settings instance
        
    Methods:
        __new__(): Singleton constructor
        connect(): Establish connection
        get_client(): Get client instance
        execute_query(): Execute parameterized query
        execute_query_batch(): Execute multiple queries
        health_check(): Check database health
        close(): Close all connections
        
    Usage:
        db = ClickHouseManager()
        result = db.execute_query(query, parameters)
```

**Security Features:**
- ✅ Only parameterized queries allowed
- ✅ Query validation before execution
- ✅ Timeout enforcement
- ✅ Error sanitization (no internal details exposed)

**Error Handling:**
```python
try:
    result = db.execute_query(query, params)
except ConnectionError:
    # Handle connection issues
except QueryError:
    # Handle query execution issues
except TimeoutError:
    # Handle timeout
```

**Configuration:**
```python
# From app/config.py
CLICKHOUSE_HOST: str
CLICKHOUSE_PORT: int
CLICKHOUSE_USER: str
CLICKHOUSE_PASSWORD: str
CLICKHOUSE_DATABASE: str
POOL_SIZE: int = 10
POOL_TIMEOUT: int = 30
QUERY_TIMEOUT: int = 30
```

---

### 2. `app/core/exceptions.py`

**مسئولیت**: تعریف exception hierarchy و error responses

**Exception Hierarchy:**
```
BaseAPIException
├── status_code: int
├── error_code: str
├── message: str
└── details: Optional[dict]

DatabaseException(BaseAPIException)
├── ConnectionError(DatabaseException)
├── QueryError(DatabaseException)
└── TimeoutError(DatabaseException)

ValidationException(BaseAPIException)
├── InvalidTimeFormatError(ValidationException)
└── InvalidSymbolError(ValidationException)

ResourceNotFoundException(BaseAPIException)
└── DataNotFoundError(ResourceNotFoundException)
```

**کلاس‌های اصلی:**

#### `BaseAPIException`
```python
class BaseAPIException(Exception):
    """Base exception for all API errors"""
    
    Attributes:
        status_code: HTTP status code (default: 500)
        error_code: Unique error identifier
        message: User-friendly error message
        details: Additional error context
        
    Methods:
        to_dict(): Convert to error response dict
        
    Usage:
        raise BaseAPIException(
            status_code=400,
            error_code="INVALID_INPUT",
            message="Invalid parameters provided",
            details={"field": "symbol", "error": "Too long"}
        )
```

#### `DatabaseException`
```python
class DatabaseException(BaseAPIException):
    """Base for all database-related errors"""
    status_code = 503  # Service Unavailable
    error_code = "DATABASE_ERROR"
```

#### `ValidationException`
```python
class ValidationException(BaseAPIException):
    """Base for all validation errors"""
    status_code = 422  # Unprocessable Entity
    error_code = "VALIDATION_ERROR"
```

**Error Response Format:**
```json
{
    "success": false,
    "error_code": "QUERY_ERROR",
    "message": "Failed to execute query",
    "details": {
        "field": "symbol",
        "reason": "Invalid format"
    },
    "timestamp": "2025-11-13T10:30:45.123Z"
}
```

---

### 3. `app/models/request.py`

**مسئولیت**: Pydantic models برای validation ورودی‌ها

**Models:**

#### `OHLCVQueryParams`
```python
class OHLCVQueryParams(BaseModel):
    """Query parameters for single symbol OHLCV data"""
    
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Trading symbol (e.g., BINANCE:BTCUSDT.P)"
    )
    
    start: str = Field(
        ...,
        regex=r'^\d{8}-\d{4}$',
        description="Start time in format YYYYMMDD-HHmm"
    )
    
    end: Optional[str] = Field(
        None,
        regex=r'^\d{8}-\d{4}$',
        description="End time in format YYYYMMDD-HHmm (optional, defaults to now)"
    )
    
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of records to return"
    )
    
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip (for pagination)"
    )
    
    # Custom validators
    @validator('start', 'end')
    def validate_time_format(cls, v):
        """Validate and parse time format"""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y%m%d-%H%M")
            return v
        except ValueError:
            raise ValueError(
                f"Invalid time format: {v}. Expected YYYYMMDD-HHmm"
            )
    
    @validator('end')
    def validate_time_range(cls, v, values):
        """Ensure end time is after start time"""
        if v and 'start' in values:
            start_dt = datetime.strptime(values['start'], "%Y%m%d-%H%M")
            end_dt = datetime.strptime(v, "%Y%m%d-%H%M")
            if end_dt <= start_dt:
                raise ValueError("End time must be after start time")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BINANCE:BTCUSDT.P",
                "start": "20250701-0000",
                "end": "20250801-0000",
                "limit": 1000,
                "offset": 0
            }
        }
```

#### `MultiSymbolQueryParams`
```python
class MultiSymbolQueryParams(BaseModel):
    """Query parameters for multiple symbols"""
    
    symbols: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of trading symbols"
    )
    
    start: str = Field(...)
    end: Optional[str] = Field(None)
    limit: int = Field(default=1000, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)
    
    @validator('symbols')
    def validate_symbols(cls, v):
        """Validate each symbol"""
        for symbol in v:
            if not symbol or len(symbol) > 50:
                raise ValueError(f"Invalid symbol: {symbol}")
        return v
```

#### `LatestQueryParams`
```python
class LatestQueryParams(BaseModel):
    """Parameters for getting latest candle"""
    
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Trading symbol"
    )
```

---

### 4. `app/models/response.py`

**مسئولیت**: Pydantic models برای response formatting

**Models:**

#### `OHLCVData`
```python
class OHLCVData(BaseModel):
    """Single OHLCV candle data"""
    
    candle_time: datetime = Field(
        ...,
        description="Candle timestamp"
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
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        schema_extra = {
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
```

#### `ResponseMetadata`
```python
class ResponseMetadata(BaseModel):
    """Metadata for paginated responses"""
    
    total_records: int = Field(
        ...,
        description="Total number of records returned"
    )
    
    limit: int = Field(
        ...,
        description="Limit used in query"
    )
    
    offset: int = Field(
        ...,
        description="Offset used in query"
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
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

#### `OHLCVResponse`
```python
class OHLCVResponse(BaseModel):
    """Standard OHLCV API response"""
    
    success: bool = Field(
        default=True,
        description="Whether request was successful"
    )
    
    data: List[OHLCVData] = Field(
        ...,
        description="Array of OHLCV data"
    )
    
    metadata: ResponseMetadata = Field(
        ...,
        description="Response metadata"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "success": true,
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
                    "has_more": false,
                    "query_time_ms": 45.2,
                    "timestamp": "2025-11-13T10:30:45.123Z"
                }
            }
        }
```

#### `ErrorResponse`
```python
class ErrorResponse(BaseModel):
    """Standard error response"""
    
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
    
    details: Optional[dict] = Field(
        None,
        description="Additional error details"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error occurrence timestamp"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

### 5. `app/routers/health.py`

**مسئولیت**: Health check endpoints برای monitoring

**Endpoints:**

#### `GET /health`
```python
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check
    
    Returns:
        - status: "healthy" or "unhealthy"
        - version: API version
        - timestamp: Current time
    """
```

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-11-13T10:30:45.123Z"
}
```

#### `GET /health/ready`
```python
@router.get("/health/ready", response_model=DetailedHealthResponse)
async def readiness_check():
    """
    Readiness check (includes database check)
    
    Returns:
        - status: Overall health status
        - checks: Individual component checks
        - version: API version
        - timestamp: Current time
    """
```

**Response:**
```json
{
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
```

#### `GET /health/live`
```python
@router.get("/health/live")
async def liveness_check():
    """
    Liveness check (simple ping)
    
    Returns:
        Simple "ok" response for Kubernetes liveness probe
    """
```

**Response:**
```json
{"status": "ok"}
```

---

### 6. `app/routers/ohlcv.py` (Refactored)

**تغییرات اصلی:**

#### Before (خطرناک):
```python
@router.get("/")
def get_ohlcv(symbol: str, start: str, end: str = None):
    # ❌ SQL Injection vulnerability
    query = f"""
    SELECT * FROM {config.CLICKHOUSE_TABLE}
    WHERE symbol = '{symbol}' AND {time_filter}
    """
    data = run_query(query)
    return JSONResponse(content=data)
```

#### After (امن):
```python
@router.get("/", response_model=OHLCVResponse)
async def get_ohlcv(params: OHLCVQueryParams = Depends()):
    """
    Get OHLCV data for a symbol in time range
    
    Security:
    - ✅ Parameterized queries (SQL injection safe)
    - ✅ Input validation (Pydantic)
    - ✅ Pagination enforced
    - ✅ Timeout protection
    """
    
    # Parse times
    start_dt = parse_time_param(params.start)
    end_dt = parse_time_param(params.end) if params.end else datetime.utcnow()
    
    # Build safe query
    query = """
        SELECT 
            candle_time,
            symbol,
            open,
            high,
            low,
            close,
            volume
        FROM {table:Identifier}
        WHERE symbol = {symbol:String}
          AND candle_time >= {start:DateTime64(3)}
          AND candle_time <= {end:DateTime64(3)}
        ORDER BY candle_time ASC
        LIMIT {limit:UInt32}
        OFFSET {offset:UInt32}
    """
    
    # Execute with parameters
    db = ClickHouseManager()
    start_time = time.time()
    
    result = await db.execute_query(
        query,
        parameters={
            'table': config.CLICKHOUSE_TABLE,
            'symbol': params.symbol,
            'start': start_dt,
            'end': end_dt,
            'limit': params.limit,
            'offset': params.offset
        }
    )
    
    query_time = (time.time() - start_time) * 1000  # ms
    
    # Transform to models
    data = [
        OHLCVData(
            candle_time=row[0],
            symbol=row[1],
            open=row[2],
            high=row[3],
            low=row[4],
            close=row[5],
            volume=row[6]
        )
        for row in result.result_rows
    ]
    
    # Build response
    return OHLCVResponse(
        data=data,
        metadata=ResponseMetadata(
            total_records=len(data),
            limit=params.limit,
            offset=params.offset,
            has_more=len(data) == params.limit,
            query_time_ms=query_time
        )
    )
```

**نقاط کلیدی:**
1. ✅ Dependency injection برای parameters
2. ✅ Parameterized query
3. ✅ Response model
4. ✅ Metadata
5. ✅ Query timing
6. ✅ Proper error handling (via exception handlers)

---

### 7. `app/config.py` (Enhanced)

**تغییرات:**

#### Before:
```python
CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASS = os.getenv("CLICKHOUSE_PASS", "")
CLICKHOUSE_TABLE = os.getenv("CLICKHOUSE_TABLE", "ohlcv")
```

#### After:
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    APP_NAME: str = "ClickHouse OHLCV API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ClickHouse Connection
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DATABASE: str = "default"
    CLICKHOUSE_TABLE: str = "ohlcv"
    CLICKHOUSE_SECURE: bool = False
    
    # Connection Pool Settings
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600  # 1 hour
    
    # Query Settings
    DEFAULT_LIMIT: int = 1000
    MAX_LIMIT: int = 10000
    QUERY_TIMEOUT: int = 30
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security (for future phases)
    API_KEY_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def get_clickhouse_url(self) -> str:
        """Build ClickHouse connection URL"""
        protocol = "https" if self.CLICKHOUSE_SECURE else "http"
        return f"{protocol}://{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT}"

# Singleton instance
settings = Settings()
```

---

### 8. `app/main.py` (Enhanced)

**تغییرات اصلی:**

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings
from app.core.exceptions import BaseAPIException
from app.core.database import ClickHouseManager
from app.routers import ohlcv, health

# Create app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A production-ready REST API for ClickHouse OHLCV data",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# Validation exception handler
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log the error (будет реализовано в Phase 2)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup():
    """Initialize connections on startup"""
    db = ClickHouseManager()
    db.connect()

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    """Close connections on shutdown"""
    db = ClickHouseManager()
    db.close()

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(
    ohlcv.router, 
    prefix=settings.API_PREFIX,
    tags=["OHLCV"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
```

---

### 9. `requirements.txt` (Updated)

**تغییرات:**

#### Before:
```txt
fastapi
uvicorn
requests
python-dotenv
pytest
```

#### After:
```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# ClickHouse Client
clickhouse-connect==0.6.23

# Configuration & Validation
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Async Support
asyncio==3.4.3
aiofiles==23.2.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2  # For TestClient

# Development (optional, در requirements-dev.txt)
# black==23.11.0
# flake8==6.1.0
# mypy==1.7.0
```

---

### 10. `.env.example` (Enhanced)

```bash
# Application Settings
APP_NAME=ClickHouse OHLCV API
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# ClickHouse Connection
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=default
CLICKHOUSE_TABLE=ohlcv
CLICKHOUSE_SECURE=false

# Connection Pool
POOL_SIZE=10
MAX_OVERFLOW=20
POOL_TIMEOUT=30
POOL_RECYCLE=3600

# Query Settings
DEFAULT_LIMIT=1000
MAX_LIMIT=10000
QUERY_TIMEOUT=30

# API Settings
API_PREFIX=/api/v1
CORS_ORIGINS=["*"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security (Future)
API_KEY_ENABLED=false
RATE_LIMIT_ENABLED=false
```

---

## ✅ Validation Checklist

بعد از اتمام Phase 1، بررسی کن:

### Security
- [ ] هیچ SQL injection vulnerability نداره
- [ ] تمام queries parameterized هستن
- [ ] Input validation کامل هست
- [ ] Error messages حاوی اطلاعات حساس نیستن

### Functionality
- [ ] Health check کار می‌کنه
- [ ] OHLCV endpoint با symbol تکی کار می‌کنه
- [ ] Pagination درست کار می‌کنه
- [ ] Time range filtering درست هست
- [ ] Latest endpoint کار می‌کنه

### Code Quality
- [ ] تمام functions type hints دارن
- [ ] Docstrings برای تمام public functions
- [ ] Code readable و maintainable هست
- [ ] No code duplication

### Testing
- [ ] حداقل یک test برای هر endpoint
- [ ] Test برای validation errors
- [ ] Test برای database errors

---

## 🚀 آماده برای شروع کدنویسی؟

حالا که ساختار کامل Phase 1 رو داریم، می‌تونیم شروع به پیاده‌سازی کنیم!

**ترتیب پیشنهادی پیاده‌سازی:**
1. Core modules (database, exceptions)
2. Models (request, response)
3. Health router
4. Refactor OHLCV router
5. Update config & main
6. Test everything

آماده‌ای؟
