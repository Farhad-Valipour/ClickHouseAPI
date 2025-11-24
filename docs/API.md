# API Reference

Complete API documentation for ClickHouse OHLCV REST API with ISO 8601 time format support.

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
| `start` | string | Yes | Start time in ISO 8601 format (see [Time Format](#time-format)) |
| `end` | string | No | End time in ISO 8601 format (defaults to now) |
| `limit` | integer | No | Max records (default: 1000, max: 10000) |
| `offset` | integer | No | Skip N records (default: 0) |

**Example Request (ISO 8601 - Recommended):**
```bash
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&end=2025-08-01T00:00:00Z&limit=100"
```

**Example Request (Legacy Format - Deprecated):**
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
    "limit": 1,
    "offset": 0,
    "has_more": false,
    "query_time_ms": 12.3,
    "timestamp": "2025-11-13T10:30:45.123Z"
  }
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
curl ".../ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&limit=100&offset=0"

# Get second page (records 100-199)
curl ".../ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&limit=100&offset=100"
```

The `metadata.has_more` field indicates if more records are available.

---

## Time Format

### Input Time Parameters (Request)

The API supports **ISO 8601 format** (recommended) with backward compatibility for legacy format.

#### ISO 8601 Format (Recommended) ✅

**Supported Formats:**

1. **Basic Format** (assumes UTC if no timezone specified)
   ```
   2025-07-01T00:00:00
   ```

2. **UTC Format** (recommended for clarity)
   ```
   2025-07-01T00:00:00Z
   ```

3. **With Timezone Offset**
   ```
   2025-07-01T00:00:00+03:00    # UTC+3
   2025-07-01T00:00:00-05:00    # UTC-5
   ```

4. **With Milliseconds**
   ```
   2025-07-01T00:00:00.000Z
   2025-07-01T15:30:45.123Z
   ```

**Examples:**
```bash
# UTC format (recommended)
?start=2025-07-01T00:00:00Z&end=2025-08-01T00:00:00Z

# With timezone offset
?start=2025-07-01T00:00:00+03:00&end=2025-08-01T00:00:00+03:00

# With milliseconds
?start=2025-07-01T00:00:00.000Z&end=2025-08-01T23:59:59.999Z

# Basic format (assumes UTC)
?start=2025-07-01T00:00:00&end=2025-08-01T00:00:00
```

#### Legacy Format (Deprecated) ⚠️

For backward compatibility, the old format is still supported but deprecated:

```
YYYYMMDD-HHmm
```

**Examples:**
- `20250701-0000` - July 1, 2025 at midnight
- `20250801-1530` - August 1, 2025 at 3:30 PM

**Note:** This format will be removed in a future version. Please migrate to ISO 8601.

#### Timezone Handling

- All times are converted to UTC internally
- If no timezone is specified in ISO 8601 format, UTC is assumed
- Response timestamps are always in UTC
- Timezone offsets are properly handled and converted

### Output Time Format (Response)

All timestamps in responses use **ISO 8601 format**:

```json
{
  "candle_time": "2025-07-01T15:30:00",
  "timestamp": "2025-11-13T10:30:45.123Z"
}
```

---

## Validation

### Time Format Validation

**Valid ISO 8601 Examples:**
```
✓ 2025-07-01T00:00:00
✓ 2025-07-01T00:00:00Z
✓ 2025-07-01T00:00:00+03:00
✓ 2025-07-01T00:00:00-05:00
✓ 2025-07-01T00:00:00.000Z
✓ 2025-07-01T00:00:00.123456Z
```

**Valid Legacy Examples (Deprecated):**
```
✓ 20250701-0000
✓ 20250801-1530
```

**Invalid Examples:**
```
✗ 2025-07-01              # Missing time part
✗ 2025/07/01T00:00:00     # Wrong date separator
✗ 01-07-2025T00:00:00     # Wrong date order
✗ 2025-7-1T00:00:00       # Missing leading zeros
✗ invalid-time            # Not a valid format
```

### Error Response for Invalid Time Format

```json
{
  "detail": "Invalid time format: invalid-time. Expected ISO 8601 format (e.g., 2025-07-01T00:00:00Z, 2025-07-01T00:00:00+03:00) or legacy format (YYYYMMDD-HHmm)"
}
```

---

## Migration Guide

### From Legacy to ISO 8601

If you're currently using the legacy format, here's how to migrate:

**Before (Legacy):**
```bash
curl ".../ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000"
```

**After (ISO 8601):**
```bash
curl ".../ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&end=2025-08-01T00:00:00Z"
```

**Conversion Rules:**
- `20250701-0000` → `2025-07-01T00:00:00Z`
- `20250801-1530` → `2025-08-01T15:30:00Z`

**Benefits of ISO 8601:**
- ✅ International standard
- ✅ Timezone support
- ✅ Better readability
- ✅ Millisecond precision
- ✅ Compatible with most programming languages and databases

---

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

The interactive documentation includes:
- Try-it-out functionality with ISO 8601 format
- Request/response examples
- Parameter validation
- Schema definitions
