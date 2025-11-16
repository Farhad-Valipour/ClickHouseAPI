# معماری پروژه ClickHouse OHLCV API - نسخه بهبود یافته

## 📋 فهرست مطالب
1. [نگاه کلی](#نگاه-کلی)
2. [ساختار پروژه](#ساختار-پروژه)
3. [معماری لایه‌ها](#معماری-لایه‌ها)
4. [اجزای کلیدی](#اجزای-کلیدی)
5. [Data Flow](#data-flow)
6. [تصمیمات طراحی](#تصمیمات-طراحی)
7. [امنیت](#امنیت)
8. [Performance](#performance)
9. [نقشه راه توسعه](#نقشه-راه-توسعه)

---

## 🎯 نگاه کلی

### هدف پروژه
یک REST API سرویس حرفه‌ای و امن برای دسترسی به داده‌های OHLCV در ClickHouse که:
- ✅ Production-ready و امن
- ✅ Scalable و performant
- ✅ قابل استفاده مجدد در پروژه‌های مختلف
- ✅ آماده برای انتشار عمومی در GitHub

### Use Cases
1. دریافت داده‌های قیمت (OHLCV) در بازه زمانی مشخص
2. فیلتر بر اساس symbol(s)
3. Pagination برای حجم بالای داده
4. دریافت آخرین داده برای هر symbol

### Technology Stack
- **Web Framework**: FastAPI (async, high-performance)
- **Database Client**: clickhouse-connect (official, async support)
- **Validation**: Pydantic v2 (type-safe)
- **Configuration**: pydantic-settings
- **Testing**: pytest + pytest-asyncio
- **Logging**: structlog
- **Container**: Docker + docker-compose

---

## 📁 ساختار پروژه

```
clickhouse-ohlcv-api/
│
├── 📁 app/                                  # کد اصلی application
│   ├── __init__.py                         # Package marker
│   ├── main.py                             # Entry point - FastAPI app
│   ├── config.py                           # Configuration management
│   │
│   ├── 📁 core/                            # هسته اصلی سیستم
│   │   ├── __init__.py
│   │   ├── database.py                    # Connection pool management
│   │   ├── exceptions.py                  # Custom exception hierarchy
│   │   └── logging_config.py              # Logging configuration
│   │
│   ├── 📁 models/                          # Data models
│   │   ├── __init__.py
│   │   ├── request.py                     # Request schemas (Pydantic)
│   │   └── response.py                    # Response schemas (Pydantic)
│   │
│   ├── 📁 routers/                         # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py                      # Health check endpoint
│   │   └── ohlcv.py                       # OHLCV data endpoints
│   │
│   └── 📁 utils/                           # Helper utilities
│       ├── __init__.py
│       └── time_parser.py                 # Time parsing utilities
│
├── 📁 tests/                                # Test suite
│   ├── __init__.py
│   ├── conftest.py                        # Pytest fixtures & config
│   ├── test_health.py                     # Health endpoint tests
│   ├── test_ohlcv_api.py                  # OHLCV endpoint tests
│   └── test_time_parser.py                # Utility tests
│
├── 📁 docs/                                 # Documentation
│   ├── API.md                             # API reference
│   ├── DEPLOYMENT.md                      # Deployment guide
│   └── EXAMPLES.md                        # Usage examples
│
├── 📁 scripts/                              # Utility scripts
│   ├── seed_data.py                       # Sample data generator
│   └── setup_db.py                        # Database initialization
│
├── .env.example                            # Environment variables template
├── .gitignore                              # Git ignore rules
├── requirements.txt                        # Production dependencies
├── requirements-dev.txt                    # Development dependencies
├── pytest.ini                              # Pytest configuration
├── Dockerfile                              # Docker image definition
├── docker-compose.yml                      # Local development stack
├── README.md                               # Project overview
└── LICENSE                                 # MIT License

Total Structure:
- 7 Python modules
- 15 Python files
- 8 configuration files
- 3 documentation files
```

---

## 🏗️ معماری لایه‌ها

### Layered Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│              (HTTP Clients, Browser, etc.)               │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  CORS    │  │  Logging │  │  Error   │             │
│  │Middleware│  │Middleware│  │ Handler  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer (Routers)                │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  /health         │  │  /api/v1/ohlcv   │            │
│  │  Health Check    │  │  OHLCV Endpoints │            │
│  └──────────────────┘  └──────────────────┘            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Validation Layer (Models)                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  Pydantic Models                               │    │
│  │  - Request Validation                          │    │
│  │  - Response Serialization                      │    │
│  │  - Type Safety                                 │    │
│  └────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│            Data Access Layer (Database)                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  Connection Pool Manager                       │    │
│  │  - Connection lifecycle                        │    │
│  │  - Query execution                             │    │
│  │  - Error handling                              │    │
│  └────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │ ClickHouse Protocol
                         ▼
              ┌──────────────────────┐
              │   ClickHouse DB      │
              │   (OHLCV Table)      │
              └──────────────────────┘
```

### مسئولیت هر لایه:

#### 1. **API Gateway Layer**
- CORS handling
- Request logging
- Global error handling
- Rate limiting (future)

#### 2. **Presentation Layer (Routers)**
- HTTP endpoint definition
- Request routing
- Response formatting
- API documentation (OpenAPI)

#### 3. **Validation Layer (Models)**
- Input validation
- Type checking
- Data serialization/deserialization
- Business rule validation

#### 4. **Data Access Layer**
- Connection management
- Query building (safe, parameterized)
- Result processing
- Database error handling

---

## 🔧 اجزای کلیدی

### 1. Core Module (`app/core/`)

#### 1.1 `database.py` - Connection Management
**مسئولیت‌ها:**
- ایجاد و مدیریت connection pool
- Health check برای database
- Graceful shutdown
- Query execution wrapper

**Key Features:**
- Singleton pattern برای connection pool
- Lazy initialization
- Connection retry logic
- Query timeout management

**پیاده‌سازی:**
```python
class ClickHouseManager:
    - __init__(): تنظیمات اولیه
    - connect(): ایجاد connection
    - get_client(): دریافت client از pool
    - execute_query(): اجرای query با error handling
    - health_check(): بررسی سلامت connection
    - close(): بستن تمام connections
```

---

#### 1.2 `exceptions.py` - Exception Hierarchy
**مسئولیت‌ها:**
- تعریف custom exceptions
- Error code management
- Structured error responses

**Exception Hierarchy:**
```
BaseAPIException (Abstract)
├── DatabaseException
│   ├── ConnectionError
│   ├── QueryError
│   └── TimeoutError
├── ValidationException
│   ├── InvalidTimeFormatError
│   └── InvalidSymbolError
└── ResourceNotFoundException
    └── DataNotFoundError
```

**ساختار Exception:**
```python
class BaseAPIException:
    - status_code: int
    - error_code: str
    - message: str
    - details: Optional[dict]
```

---

#### 1.3 `logging_config.py` - Logging Setup
**مسئولیت‌ها:**
- Structured logging configuration
- Log format standardization
- Log level management
- Request ID tracking

**Log Format:**
```json
{
    "timestamp": "2025-11-13T10:30:45.123Z",
    "level": "INFO",
    "service": "clickhouse-api",
    "request_id": "abc-123-xyz",
    "message": "Query executed successfully",
    "duration_ms": 45,
    "query_type": "SELECT",
    "records_returned": 1000
}
```

---

### 2. Models Module (`app/models/`)

#### 2.1 `request.py` - Request Models

**OHLCVQueryParams:**
```python
class OHLCVQueryParams(BaseModel):
    symbol: str                        # Required
    start: str                         # YYYYMMDD-HHmm format
    end: Optional[str]                 # YYYYMMDD-HHmm format
    limit: int = 1000                  # Default: 1000, Max: 10000
    offset: int = 0                    # For pagination
    
    # Validators
    @validator('symbol')
    def validate_symbol(cls, v):
        # Check format, length, etc.
        
    @validator('start', 'end')
    def validate_time_format(cls, v):
        # Validate time format
```

**MultiSymbolQueryParams:**
```python
class MultiSymbolQueryParams(BaseModel):
    symbols: List[str]                 # Multiple symbols
    start: str
    end: Optional[str]
    limit: int = 1000
    offset: int = 0
```

---

#### 2.2 `response.py` - Response Models

**OHLCVData:**
```python
class OHLCVData(BaseModel):
    candle_time: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**OHLCVResponse:**
```python
class OHLCVResponse(BaseModel):
    success: bool = True
    data: List[OHLCVData]
    metadata: ResponseMetadata
    
class ResponseMetadata(BaseModel):
    total_records: int
    returned_records: int
    limit: int
    offset: int
    has_more: bool
    query_time_ms: float
    timestamp: datetime
```

**ErrorResponse:**
```python
class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime
```

---

### 3. Routers Module (`app/routers/`)

#### 3.1 `health.py` - Health Check

**Endpoints:**
```
GET /health
GET /health/ready
GET /health/live
```

**Response Structure:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-11-13T10:30:45.123Z",
    "checks": {
        "database": {
            "status": "up",
            "response_time_ms": 12
        },
        "api": {
            "status": "up"
        }
    }
}
```

---

#### 3.2 `ohlcv.py` - OHLCV Endpoints

**Endpoints:**

**1. Get OHLCV Data**
```
GET /api/v1/ohlcv?symbol=AAPL&start=20250701-0000&end=20250801-0000&limit=1000&offset=0
```

**2. Get Multiple Symbols**
```
GET /api/v1/ohlcv/multi?symbols=AAPL,GOOGL,MSFT&start=20250701-0000&end=20250801-0000
```

**3. Get Latest Candle**
```
GET /api/v1/ohlcv/latest?symbol=AAPL
```

**4. Get Latest for Multiple Symbols**
```
GET /api/v1/ohlcv/latest/multi?symbols=AAPL,GOOGL,MSFT
```

---

### 4. Utils Module (`app/utils/`)

#### 4.1 `time_parser.py` - Time Utilities

**Functions:**
```python
def parse_time_param(time_str: str) -> datetime:
    """Parse YYYYMMDD-HHmm to datetime"""
    
def format_for_clickhouse(dt: datetime) -> str:
    """Format datetime for ClickHouse query"""
    
def validate_time_range(start: datetime, end: datetime) -> bool:
    """Validate time range logic"""
```

---

### 5. Configuration (`app/config.py`)

**Environment Variables:**
```python
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ClickHouse OHLCV API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ClickHouse
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DATABASE: str = "default"
    CLICKHOUSE_TABLE: str = "ohlcv"
    
    # Connection Pool
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30
    
    # Query Settings
    DEFAULT_LIMIT: int = 1000
    MAX_LIMIT: int = 10000
    QUERY_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

---

## 🔄 Data Flow

### Request Flow Example: GET /api/v1/ohlcv

```
1. Client Request
   ↓
   GET /api/v1/ohlcv?symbol=AAPL&start=20250701-0000&end=20250801-0000
   
2. FastAPI Router (ohlcv.py)
   ↓
   - Route matching
   - Extract query parameters
   
3. Pydantic Validation (models/request.py)
   ↓
   - Validate symbol format
   - Validate time format
   - Validate limit/offset ranges
   - Parse datetime values
   
4. Database Layer (core/database.py)
   ↓
   - Get connection from pool
   - Build parameterized query:
     SELECT * FROM ohlcv 
     WHERE symbol = {symbol:String}
       AND candle_time >= {start:DateTime64(3)}
       AND candle_time <= {end:DateTime64(3)}
     ORDER BY candle_time ASC
     LIMIT {limit:UInt32} OFFSET {offset:UInt32}
   
5. ClickHouse Query Execution
   ↓
   - Execute query
   - Return result set
   
6. Data Transformation (models/response.py)
   ↓
   - Convert rows to OHLCVData models
   - Build metadata (total, has_more, etc.)
   - Create OHLCVResponse
   
7. Response Serialization
   ↓
   - Pydantic to JSON
   - Apply JSON encoders (datetime → ISO string)
   
8. Client Response
   ↓
   {
     "success": true,
     "data": [...],
     "metadata": {
       "total_records": 1000,
       "has_more": true,
       ...
     }
   }
```

### Error Flow Example:

```
1. Client Request (Invalid)
   ↓
   GET /api/v1/ohlcv?symbol=INVALID&start=bad-date
   
2. Pydantic Validation FAILS
   ↓
   - ValidationException raised
   
3. Global Exception Handler
   ↓
   - Catch exception
   - Log error
   - Build ErrorResponse
   
4. Client Response (422)
   ↓
   {
     "success": false,
     "error_code": "VALIDATION_ERROR",
     "message": "Invalid time format",
     "details": {
       "field": "start",
       "provided": "bad-date",
       "expected": "YYYYMMDD-HHmm"
     }
   }
```

---

## 🎨 تصمیمات طراحی

### 1. چرا Parameterized Queries؟
**مشکل:**
```python
# ❌ SQL Injection vulnerability
query = f"SELECT * FROM ohlcv WHERE symbol = '{symbol}'"
```

**راه حل:**
```python
# ✅ Safe parameterized query
query = "SELECT * FROM ohlcv WHERE symbol = {symbol:String}"
params = {'symbol': symbol}
```

**مزایا:**
- ✅ امنیت کامل در برابر SQL injection
- ✅ Type safety با ClickHouse types
- ✅ Better performance (query caching)

---

### 2. چرا Connection Pooling؟

**بدون Pool:**
```python
# ❌ هر request یک connection جدید
def get_data():
    client = clickhouse_connect.get_client(...)  # Slow!
    result = client.query(...)
    client.close()
```

**با Pool:**
```python
# ✅ Connection reuse
def get_data():
    client = pool.get_client()  # Fast!
    result = client.query(...)
    # Connection returned to pool automatically
```

**مزایا:**
- ✅ کاهش overhead اتصال
- ✅ Scalability بهتر
- ✅ مدیریت منابع بهینه

---

### 3. چرا Pydantic Models؟

**مزایا:**
- ✅ Type safety در compile time
- ✅ خودکار validation
- ✅ خودکار documentation (OpenAPI)
- ✅ IDE autocomplete
- ✅ Easy serialization/deserialization

**مثال:**
```python
# ❌ بدون Pydantic
def get_ohlcv(symbol: str, limit: str):  # limit باید int باشه!
    limit = int(limit)  # Manual conversion
    if limit > 10000:   # Manual validation
        raise ValueError("...")
        
# ✅ با Pydantic
def get_ohlcv(params: OHLCVQueryParams):
    # limit تضمینی int هست
    # validation خودکار انجام شده
```

---

### 4. چرا Async Endpoints؟

**Performance Comparison:**
```python
# Sync (blocking)
def get_data():
    result = client.query(...)  # Blocks thread
    return result

# Async (non-blocking)
async def get_data():
    result = await client.query(...)  # Doesn't block
    return result
```

**مزایا:**
- ✅ Concurrent requests بیشتر
- ✅ بهره‌وری بهتر از CPU
- ✅ کاهش latency در high load

---

### 5. چرا Structured Logging؟

**Traditional Logging:**
```
INFO: User AAPL query completed in 45ms with 1000 records
```

**Structured Logging:**
```json
{
  "level": "INFO",
  "message": "Query completed",
  "symbol": "AAPL",
  "duration_ms": 45,
  "records": 1000,
  "user_id": "123"
}
```

**مزایا:**
- ✅ قابل parse و analysis
- ✅ آسان برای monitoring tools
- ✅ Query و filter آسان

---

## 🔒 امنیت

### Security Layers

#### 1. **Input Validation**
- Pydantic validation برای تمام inputs
- Type checking
- Range validation (limit, offset)
- Format validation (dates, symbols)

#### 2. **SQL Injection Prevention**
- ✅ Parameterized queries only
- ❌ هیچ string concatenation در SQL
- ❌ هیچ user input مستقیم در query

#### 3. **Rate Limiting** (Future - Phase 5)
```python
# Per IP: 100 requests/minute
# Per API Key: 1000 requests/minute
```

#### 4. **Authentication** (Future - Phase 5)
```python
# API Key based authentication
# Header: X-API-Key: your-key-here
```

#### 5. **Error Information Hiding**
```python
# ❌ Don't expose internal details
"Database error: Connection refused at 192.168.1.10:8123"

# ✅ Generic error for users
"Database temporarily unavailable. Please try again."
```

---

## ⚡ Performance

### Optimization Strategies

#### 1. **Connection Pooling**
- Pre-established connections
- Reuse connections
- Reduced connection overhead

#### 2. **Pagination**
- Default limit: 1000 records
- Max limit: 10,000 records
- Cursor-based pagination support

#### 3. **Query Optimization**
```sql
-- ✅ Indexed columns first
WHERE symbol = '...' AND candle_time >= '...'

-- ✅ ORDER BY only when needed
ORDER BY candle_time ASC

-- ✅ LIMIT always specified
LIMIT 1000 OFFSET 0
```

#### 4. **Async Operations**
- Non-blocking I/O
- Concurrent request handling
- Better CPU utilization

#### 5. **Response Compression** (Future)
```python
# Gzip compression for large responses
middleware = GZipMiddleware(app, minimum_size=1000)
```

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Response Time (p95) | < 500ms | For queries returning < 1000 records |
| Response Time (p99) | < 1s | For queries returning < 10000 records |
| Concurrent Requests | 100+ | With connection pooling |
| Throughput | 1000+ req/s | On standard hardware |
| Error Rate | < 0.1% | Excluding user errors (4xx) |

---

## 🗺️ نقشه راه توسعه

### Phase 1: Critical Fixes ✅ (1 روز)
**Status**: Ready to implement

**Deliverables:**
1. ✅ `app/core/database.py` - Connection pooling
2. ✅ `app/core/exceptions.py` - Exception hierarchy
3. ✅ `app/models/request.py` - Request models
4. ✅ `app/models/response.py` - Response models
5. ✅ `app/routers/ohlcv.py` - Refactored with safety
6. ✅ `app/routers/health.py` - Health checks
7. ✅ `requirements.txt` - Updated dependencies

**Files Changed**: 7 new files, 2 modified

---

### Phase 2: Production Ready (1 روز)

**Deliverables:**
1. `app/core/logging_config.py` - Structured logging
2. Async endpoints
3. Enhanced error handling
4. Configuration improvements
5. Docker compose setup

**Files Changed**: 5 files

---

### Phase 3: Developer Experience (1 روز)

**Deliverables:**
1. `tests/conftest.py` - Test fixtures
2. Complete test suite
3. `docs/API.md` - API documentation
4. `docs/EXAMPLES.md` - Usage examples
5. README improvements

**Files Changed**: 6 files

---

### Phase 4: GitHub Ready (نیم روز)

**Deliverables:**
1. `CONTRIBUTING.md`
2. `LICENSE`
3. GitHub Actions CI/CD
4. Issue templates
5. Code of conduct

**Files Changed**: 5 files

---

### Phase 5: Advanced Features (آینده)

**Potential Features:**
1. API Key authentication
2. Rate limiting
3. Caching layer (Redis)
4. WebSocket support
5. GraphQL endpoint
6. Aggregation queries
7. Bulk operations

---

## 📊 Metrics & Monitoring

### Application Metrics
```python
# To be implemented in Phase 2
- request_count_total
- request_duration_seconds
- request_errors_total
- database_query_duration_seconds
- database_connection_pool_size
- database_connection_pool_usage
```

### Health Indicators
```python
- API availability
- Database connectivity
- Response time trends
- Error rate trends
- Connection pool saturation
```

---

## 🧪 Testing Strategy

### Test Coverage Target: >80%

#### Unit Tests
- Time parser functions
- Validation logic
- Exception handling
- Model serialization

#### Integration Tests
- API endpoints (full flow)
- Database queries
- Error scenarios
- Pagination

#### Performance Tests
- Load testing (future)
- Stress testing (future)
- Concurrent requests (future)

---

## 📝 Documentation Structure

### User Documentation
1. **README.md** - Quick start & overview
2. **docs/API.md** - Complete API reference
3. **docs/EXAMPLES.md** - Usage examples & recipes
4. **docs/DEPLOYMENT.md** - Production deployment guide

### Developer Documentation
1. **ARCHITECTURE.md** - این سند!
2. **CONTRIBUTING.md** - Contribution guidelines
3. **docs/DEVELOPMENT.md** - Local development setup

---

## 🎯 Success Criteria

### Technical
- ✅ Zero SQL injection vulnerabilities
- ✅ <500ms response time (p95)
- ✅ >80% test coverage
- ✅ Zero high-severity security issues

### User Experience
- ✅ Clear error messages
- ✅ Complete API documentation
- ✅ Easy local setup (<5 minutes)
- ✅ Docker support

### Community (GitHub)
- ✅ Clear README with examples
- ✅ Active issue responses
- ✅ Contribution guidelines
- ✅ CI/CD pipeline

---

## 🔗 مراجع و منابع

### ClickHouse
- [ClickHouse Documentation](https://clickhouse.com/docs)
- [clickhouse-connect](https://github.com/ClickHouse/clickhouse-connect)

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)

### Best Practices
- [12-Factor App](https://12factor.net)
- [REST API Design](https://restfulapi.net)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)

---

## 📞 پشتیبانی

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: TBD

---

**آخرین بروزرسانی**: 2025-11-13
**نسخه**: 2.0 (بهبود یافته)
**وضعیت**: در حال توسعه - Phase 1
