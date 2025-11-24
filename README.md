# ClickHouse OHLCV REST API

> A production-ready REST API for accessing OHLCV (Open, High, Low, Close, Volume) data from ClickHouse with ISO 8601 time format support

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## ✨ Features

- 🔒 **Secure**: SQL injection protected with parameterized queries
- ⚡ **Fast**: Optimized queries with async support and connection pooling
- 📊 **Paginated**: Support for large datasets with built-in pagination
- ✅ **Validated**: Automatic request validation using Pydantic
- 📚 **Documented**: Auto-generated OpenAPI (Swagger) documentation
- 🐳 **Docker Ready**: Includes Docker and docker-compose setup
- 🏥 **Health Checks**: Built-in health check endpoints for monitoring
- 🌍 **ISO 8601**: Modern time format with timezone support
- ⏱️ **Backward Compatible**: Legacy format still supported

## 🆕 What's New

### ISO 8601 Time Format Support

The API now supports the international standard **ISO 8601** time format with full timezone support:

- ✅ **UTC Format**: `2025-07-01T00:00:00Z`
- ✅ **Timezone Offsets**: `2025-07-01T00:00:00+03:00`
- ✅ **Milliseconds**: `2025-07-01T00:00:00.000Z`
- ✅ **Basic Format**: `2025-07-01T00:00:00`

**Legacy format** (`YYYYMMDD-HHmm`) is still supported for backward compatibility but deprecated.

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd clickhouse-ohlcv-api

# Start services
docker-compose up -d

# API will be available at http://localhost:8000
# ClickHouse will be available at http://localhost:8123
```

Visit http://localhost:8000/docs for interactive API documentation.

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# 3. Install package in editable mode
pip install -e .

# 4. Configure environment
cp .env.example .env
# Edit .env with your ClickHouse connection details

# 5. Run the application
uvicorn app.main:app --reload

# 6. Visit http://localhost:8000/docs
```

## 📖 API Documentation

### Endpoints

#### Health Checks

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check with database status
- `GET /health/live` - Simple liveness probe

#### OHLCV Data

- `GET /api/v1/ohlcv` - Get OHLCV data for a symbol
  - Query Parameters:
    - `symbol` (required): Trading symbol (e.g., BINANCE:BTCUSDT.P)
    - `start` (required): Start time in ISO 8601 format (e.g., `2025-07-01T00:00:00Z`)
    - `end` (optional): End time in ISO 8601 format (defaults to now)
    - `limit` (optional): Max records (default: 1000, max: 10000)
    - `offset` (optional): Skip records (default: 0)

- `GET /api/v1/ohlcv/latest` - Get the latest candle for a symbol
  - Query Parameters:
    - `symbol` (required): Trading symbol

### Example Requests

#### Using ISO 8601 Format (Recommended)

```bash
# Get OHLCV data for Bitcoin (ISO 8601)
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&end=2025-08-01T00:00:00Z&limit=100"

# With timezone offset
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00%2B03:00&end=2025-08-01T00:00:00%2B03:00"

# Get latest candle
curl "http://localhost:8000/api/v1/ohlcv/latest?symbol=BINANCE:BTCUSDT.P"

# Health check
curl "http://localhost:8000/health/ready"
```

#### Using Legacy Format (Deprecated)

```bash
# Legacy format still works for backward compatibility
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000"
```

### Python Example

```python
import requests

# Using ISO 8601 format
response = requests.get(
    "http://localhost:8000/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "2025-07-01T00:00:00Z",
        "end": "2025-08-01T00:00:00Z",
        "limit": 1000
    }
)

data = response.json()
print(f"Retrieved {data['metadata']['total_records']} records")

for candle in data['data']:
    print(f"{candle['candle_time']}: ${candle['close']:,.2f}")
```

### Response Format

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
    "limit": 1000,
    "offset": 0,
    "has_more": false,
    "query_time_ms": 45.2,
    "timestamp": "2025-11-13T10:30:45.123Z"
  }
}
```

## 🌍 Time Format

### Input Parameters (Request)

The API supports **ISO 8601** format (recommended) with backward compatibility:

**ISO 8601 Formats (Recommended):**
- `2025-07-01T00:00:00` - Basic format
- `2025-07-01T00:00:00Z` - UTC (recommended)
- `2025-07-01T00:00:00+03:00` - With timezone offset
- `2025-07-01T00:00:00.000Z` - With milliseconds

**Legacy Format (Deprecated):**
- `20250701-0000` - Old format (still works but deprecated)

### Output (Response)

All timestamps in responses use **ISO 8601 format**:
```json
{
  "candle_time": "2025-07-01T15:30:00",
  "timestamp": "2025-11-13T10:30:45.123Z"
}
```

## 🛠️ Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

### Key Environment Variables

```bash
# ClickHouse Connection
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DATABASE=default
CLICKHOUSE_TABLE=ohlcv_data

# API Settings
MAX_LIMIT=10000
DEFAULT_LIMIT=1000
```

## 🏗️ Project Structure

```
clickhouse-ohlcv-api/
├── app/
│   ├── core/                 # Core functionality
│   │   ├── database.py       # ClickHouse connection
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── logging_config.py # Logging setup
│   ├── models/               # Pydantic models
│   │   ├── request.py        # Request validation
│   │   └── response.py       # Response models
│   ├── routers/              # API endpoints
│   │   ├── health.py         # Health checks
│   │   └── ohlcv.py          # OHLCV endpoints
│   ├── utils/                # Utility functions
│   │   └── time_parser.py    # Time parsing (ISO 8601)
│   ├── config.py             # Configuration
│   └── main.py               # Application entry
├── tests/                    # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_time_parser.py   # Time parser tests
│   ├── test_models.py        # Model tests
│   └── test_ohlcv_api.py     # API tests
├── docs/                     # Documentation
│   ├── API.md                # API reference
│   └── EXAMPLES.md           # Usage examples
├── pyproject.toml            # Project metadata (PEP 621)
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md                 # This file
```

## 🧪 Testing

The project includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_time_parser.py -v

# Run specific test
pytest tests/test_time_parser.py::TestParseTimeParam::test_iso8601_basic -v
```

### Test Coverage

- ✅ 50+ time parser tests (ISO 8601 + legacy)
- ✅ 30+ model validation tests
- ✅ 40+ API endpoint tests
- ✅ 120+ total test cases
- ✅ 95%+ code coverage

## 📊 Database Schema

The API expects a ClickHouse table with the following structure:

```sql
CREATE TABLE ohlcv_data (
    candle_time DateTime64(3),
    symbol String,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64
) ENGINE = MergeTree()
ORDER BY (symbol, candle_time);
```

See `scripts/init-db.sql` for the complete schema.

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone <your-repo-url>
cd clickhouse-ohlcv-api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Run tests
pytest
```

### Code Quality Tools

```bash
# Format code
black .
isort .

# Lint
flake8 app tests

# Type checking
mypy app

# Run all checks
black . && isort . && flake8 app tests && mypy app && pytest
```

## 📚 Documentation

- **API Reference**: [docs/API.md](docs/API.md)
- **Usage Examples**: [docs/EXAMPLES.md](docs/EXAMPLES.md)
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

## 🔄 Migration Guide

### From Legacy to ISO 8601

If you're currently using the legacy format, here's how to migrate:

**Before (Legacy):**
```python
params = {
    "start": "20250701-0000",
    "end": "20250801-0000"
}
```

**After (ISO 8601):**
```python
params = {
    "start": "2025-07-01T00:00:00Z",
    "end": "2025-08-01T00:00:00Z"
}
```

**Benefits:**
- ✅ International standard
- ✅ Timezone support
- ✅ Better readability
- ✅ Millisecond precision

See [docs/EXAMPLES.md](docs/EXAMPLES.md#migration-from-legacy-format) for detailed migration examples.

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t clickhouse-ohlcv-api .

# Run container
docker run -p 8000:8000 --env-file .env clickhouse-ohlcv-api
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black . && isort .`
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database: [ClickHouse](https://clickhouse.com/)
- Validation: [Pydantic](https://pydantic.dev/)
- Testing: [Pytest](https://pytest.org/)

---

**Made with ❤️ for the data community**

For questions or issues, please open an issue on GitHub.
