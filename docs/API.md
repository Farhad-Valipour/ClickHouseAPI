# API Reference

Complete API documentation for ClickHouse OHLCV REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required (Phase 1-3).
API Key authentication will be added in Phase 5.

---

## Endpoints

### Health Checks

#### GET `/health`

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-13T10:30:45.123Z"
}
```

**Status Codes:**
- `200 OK`: API is healthy

---

#### GET `/health/ready`

Readiness check with component status.

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

**Status Codes:**
- `200 OK`: Always returns 200, check `status` field

---

#### GET `/health/live`

Simple liveness probe.

**Response:**
```json
{
  "status": "ok"
}
```

---

### OHLCV Data

#### GET `/api/v1/ohlcv`

Get OHLCV candlestick data for a symbol.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading symbol (e.g., BINANCE:BTCUSDT.P) |
| `start` | string | Yes | Start time in format YYYYMMDD-HHmm |
| `end` | string | No | End time in format YYYYMMDD-HHmm (defaults to now) |
| `limit` | integer | No | Max records (default: 1000, max: 10000) |
| `offset` | integer | No | Skip N records (default: 0) |

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000&limit=100"
```

**Response:**
```json
{
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
    "limit": 100,
    "offset": 0,
    "has_more": false,
    "query_time_ms": 45.2,
    "timestamp": "2025-11-13T10:30:45.123Z"
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `422 Unprocessable Entity`: Validation error
- `503 Service Unavailable`: Database error

---

#### GET `/api/v1/ohlcv/latest`

Get the most recent candle for a symbol.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Trading symbol |

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ohlcv/latest?symbol=BINANCE:BTCUSDT.P"
```

**Response:**
```json
{
  "candle_time": "2025-07-01T00:00:00",
  "symbol": "BINANCE:BTCUSDT.P",
  "open": 50000.0,
  "high": 51000.0,
  "low": 49500.0,
  "close": 50500.0,
  "volume": 1234567.89
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: No data found for symbol
- `422 Unprocessable Entity`: Validation error

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "additional": "context"
  },
  "timestamp": "2025-11-13T10:30:45.123Z"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `INVALID_TIME_FORMAT` | Time format is incorrect |
| `DATA_NOT_FOUND` | Requested data not found |
| `DATABASE_ERROR` | Database operation failed |
| `DATABASE_CONNECTION_ERROR` | Cannot connect to database |
| `DATABASE_QUERY_ERROR` | Query execution failed |
| `DATABASE_TIMEOUT_ERROR` | Query timed out |
| `INTERNAL_ERROR` | Unexpected server error |

---

## Rate Limiting

Currently no rate limiting (Phase 1-3).
Will be added in Phase 5.

---

## Response Headers

All responses include these headers:

- `X-Request-ID`: Unique request identifier
- `X-Process-Time`: Request processing time in seconds

---

## Pagination

Use `limit` and `offset` parameters for pagination:

```bash
# Get first page (records 0-99)
curl ".../ohlcv?symbol=AAPL&start=...&limit=100&offset=0"

# Get second page (records 100-199)
curl ".../ohlcv?symbol=AAPL&start=...&limit=100&offset=100"
```

The `metadata.has_more` field indicates if more records are available.

---

## Time Format

All time parameters use the format: `YYYYMMDD-HHmm`

**Examples:**
- `20250701-0000` - July 1, 2025 at midnight
- `20250801-1530` - August 1, 2025 at 3:30 PM

**Response timestamps** use ISO 8601 format: `2025-07-01T15:30:00`

---

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
