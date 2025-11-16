# ClickHouse OHLCV REST API

> A production-ready REST API for accessing OHLCV (Open, High, Low, Close, Volume) data from ClickHouse

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🔒 **Secure**: SQL injection protected with parameterized queries
- ⚡ **Fast**: Optimized queries with connection pooling
- 📊 **Paginated**: Support for large datasets with built-in pagination
- ✅ **Validated**: Automatic request validation using Pydantic
- 📚 **Documented**: Auto-generated OpenAPI (Swagger) documentation
- 🐳 **Docker Ready**: Includes Docker and docker-compose setup
- 🏥 **Health Checks**: Built-in health check endpoints for monitoring

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
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your ClickHouse connection details

# 3. Run the application
uvicorn app.main:app --reload

# 4. Visit http://localhost:8000/docs
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
    - `start` (required): Start time (format: YYYYMMDD-HHmm)
    - `end` (optional): End time (format: YYYYMMDD-HHmm)
    - `limit` (optional): Max records (default: 1000, max: 10000)
    - `offset` (optional): Skip records (default: 0)

- `GET /api/v1/ohlcv/latest` - Get the latest candle for a symbol
  - Query Parameters:
    - `symbol` (required): Trading symbol

### Example Requests

```bash
# Get OHLCV data for Bitcoin
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000&limit=100"

# Get latest candle
curl "http://localhost:8000/api/v1/ohlcv/latest?symbol=BINANCE:BTCUSDT.P"

# Health check
curl "http://localhost:8000/health/ready"
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

## 🛠️ Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

## 🏗️ Architecture

```
├── app/
│   ├── core/              # Core functionality
│   ├── models/            # Pydantic models
│   ├── routers/           # API endpoints
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry
```

## 🧪 Testing

```bash
pytest --cov=app
```

## 📊 Database Schema

See `scripts/init-db.sql` for the complete ClickHouse schema.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the data community**
