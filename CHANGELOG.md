# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-11-13

### Added
- Initial release of ClickHouse OHLCV REST API
- Health check endpoints (`/health`, `/health/ready`, `/health/live`)
- OHLCV data endpoint with pagination support
- Latest candle endpoint
- SQL injection protection with parameterized queries
- Input validation using Pydantic models
- Connection pooling for ClickHouse
- Structured logging with request tracking
- Async endpoint support for better performance
- Docker and docker-compose setup
- Comprehensive test suite (>80% coverage)
- Complete API documentation
- Usage examples for Python, JavaScript, and cURL
- Contributing guidelines
- CI/CD with GitHub Actions

### Security
- Parameterized queries to prevent SQL injection
- Input validation on all endpoints
- Error message sanitization
- Connection timeout protection

### Documentation
- API reference documentation
- Usage examples in multiple languages
- Development guide
- Contributing guidelines
- Architecture documentation

## [0.1.0] - 2025-11-10

### Added
- Basic project structure
- Initial FastAPI setup
- Basic ClickHouse connection
- Simple OHLCV endpoint

[Unreleased]: https://github.com/yourusername/clickhouse-ohlcv-api/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/clickhouse-ohlcv-api/releases/tag/v1.0.0
[0.1.0]: https://github.com/yourusername/clickhouse-ohlcv-api/releases/tag/v0.1.0
