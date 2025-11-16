# Development Guide

Guide for setting up and developing the ClickHouse OHLCV API.

---

## Prerequisites

- Python 3.11 or higher
- pip and virtualenv
- Git
- Docker and docker-compose (optional)
- ClickHouse server (or use Docker)

---

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd clickhouse-ohlcv-api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

### 4. Setup Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 5. Start ClickHouse (Docker)

```bash
docker-compose up -d clickhouse
```

### 6. Initialize Database

```bash
# Run initialization script
docker exec -i clickhouse-server clickhouse-client < scripts/init-db.sql
```

### 7. Run Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or use the shortcut
python -m app.main
```

Visit http://localhost:8000/docs to see the API documentation.

---

## Project Structure

```
clickhouse-ohlcv-api/
├── app/                      # Application code
│   ├── core/                # Core functionality
│   │   ├── database.py     # Database connection
│   │   ├── exceptions.py   # Custom exceptions
│   │   └── logging_config.py  # Logging setup
│   ├── models/              # Pydantic models
│   │   ├── request.py      # Request schemas
│   │   └── response.py     # Response schemas
│   ├── routers/             # API endpoints
│   │   ├── health.py       # Health checks
│   │   └── ohlcv.py        # OHLCV endpoints
│   ├── utils/               # Utilities
│   ├── config.py            # Settings
│   └── main.py              # FastAPI app
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── requirements.txt         # Dependencies
```

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Run single file
pytest tests/test_health.py

# Run single test
pytest tests/test_health.py::test_basic_health_check

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

### Run by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

---

## Code Quality

### Formatting with Black

```bash
# Check formatting
black --check .

# Format code
black .
```

### Linting with Flake8

```bash
flake8 app/ tests/
```

### Type Checking with MyPy

```bash
mypy app/
```

### Run All Checks

```bash
# Format
black .

# Lint
flake8 app/ tests/

# Type check
mypy app/

# Test
pytest --cov=app
```

---

## Database Management

### Connect to ClickHouse

```bash
# Via Docker
docker exec -it clickhouse-server clickhouse-client

# Direct connection
clickhouse-client --host localhost --port 9000
```

### Common Queries

```sql
-- Show databases
SHOW DATABASES;

-- Use database
USE default;

-- Show tables
SHOW TABLES;

-- Describe table
DESCRIBE ohlcv;

-- Count records
SELECT count() FROM ohlcv;

-- Sample data
SELECT * FROM ohlcv LIMIT 10;

-- Check by symbol
SELECT symbol, count() 
FROM ohlcv 
GROUP BY symbol;
```

### Insert Sample Data

```sql
INSERT INTO ohlcv VALUES
    ('2025-07-01 00:00:00', 'BINANCE:BTCUSDT.P', 50000, 51000, 49500, 50500, 1234567),
    ('2025-07-01 00:01:00', 'BINANCE:BTCUSDT.P', 50500, 50800, 50300, 50600, 987654),
    ('2025-07-01 00:02:00', 'BINANCE:BTCUSDT.P', 50600, 50900, 50400, 50700, 876543);
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Run Tests

```bash
pytest --cov=app
```

### 4. Check Code Quality

```bash
black .
flake8 app/ tests/
mypy app/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 6. Push and Create PR

```bash
git push origin feature/new-feature
```

---

## Debugging

### Enable Debug Logging

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Use Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

### View Logs

```bash
# Docker logs
docker-compose logs -f api

# Application logs (if DEBUG=true)
# Logs will show in console
```

### Test API with curl

```bash
# Health check
curl http://localhost:8000/health

# Test endpoint
curl -v "http://localhost:8000/api/v1/ohlcv?symbol=TEST&start=20250701-0000"

# Check headers
curl -I http://localhost:8000/health
```

---

## Environment Variables

### Development (.env)

```bash
# Application
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=default
CLICKHOUSE_TABLE=ohlcv
```

### Testing (.env.test)

```bash
DEBUG=true
ENVIRONMENT=test
LOG_LEVEL=WARNING
CLICKHOUSE_HOST=localhost
CLICKHOUSE_DATABASE=test
```

### Production

```bash
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

---

## Common Issues

### Issue: Import Error

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
python -m app.main
```

### Issue: Database Connection

**Problem**: `ConnectionError: Failed to connect to ClickHouse`

**Solution**:
```bash
# Check if ClickHouse is running
docker ps | grep clickhouse

# Start if not running
docker-compose up -d clickhouse

# Check connection
clickhouse-client --query "SELECT 1"
```

### Issue: Port Already in Use

**Problem**: `Address already in use: 8000`

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: Permission Denied

**Problem**: Permission errors with Docker

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Re-login or run
newgrp docker
```

---

## Performance Testing

### Load Testing with Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class OHLCVUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_ohlcv(self):
        self.client.get(
            "/api/v1/ohlcv",
            params={
                "symbol": "BINANCE:BTCUSDT.P",
                "start": "20250701-0000",
                "end": "20250801-0000"
            }
        )
    
    @task(2)
    def get_latest(self):
        self.client.get(
            "/api/v1/ohlcv/latest",
            params={"symbol": "BINANCE:BTCUSDT.P"}
        )
```

Run test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Docker Development

### Build Image

```bash
docker build -t clickhouse-ohlcv-api:dev .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e DEBUG=true \
  -e CLICKHOUSE_HOST=host.docker.internal \
  --name api-dev \
  clickhouse-ohlcv-api:dev
```

### View Logs

```bash
docker logs -f api-dev
```

### Execute Commands in Container

```bash
docker exec -it api-dev bash
```

### Docker Compose Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart service
docker-compose restart api

# Stop all
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

---

## Git Workflow

### Commit Message Format

Use conventional commits:

```
type(scope): subject

- feat: new feature
- fix: bug fix
- docs: documentation
- style: formatting
- refactor: code restructure
- test: add tests
- chore: maintenance

Examples:
feat(api): add pagination support
fix(db): handle connection timeout
docs(readme): update installation guide
```

### Pre-commit Checks

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Run tests
pytest --cov=app --cov-fail-under=80 || exit 1

# Format code
black . || exit 1

# Lint
flake8 app/ tests/ || exit 1

echo "All checks passed!"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Useful Commands

```bash
# Create migration script
python scripts/create_migration.py

# Seed database with test data
python scripts/seed_data.py

# Export API schema
python -c "from app.main import app; import json; print(json.dumps(app.openapi()))" > openapi.json

# Generate client code
openapi-generator-cli generate -i openapi.json -g python -o client/

# Profile code
python -m cProfile -s cumtime app/main.py
```

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **ClickHouse Docs**: https://clickhouse.com/docs
- **Pydantic Docs**: https://docs.pydantic.dev
- **pytest Docs**: https://docs.pytest.org

---

## Getting Help

- Check documentation in `docs/`
- Search existing issues
- Ask in discussions
- Read API docs at `/docs`

Happy coding! 🚀
