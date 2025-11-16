"""
Application configuration using pydantic-settings.

This module provides type-safe, validated configuration management
with support for environment variables and .env files.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings with validation.
    
    All settings can be overridden via environment variables.
    For example, CLICKHOUSE_HOST environment variable will override
    the default value.
    """
    
    # ========================================================================
    # Application Settings
    # ========================================================================
    
    APP_NAME: str = "ClickHouse OHLCV API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ========================================================================
    # ClickHouse Connection Settings
    # ========================================================================
    
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DATABASE: str = "default"
    CLICKHOUSE_TABLE: str = "ohlcv"
    CLICKHOUSE_SECURE: bool = False
    
    # ========================================================================
    # Connection Pool Settings
    # ========================================================================
    
    POOL_SIZE: int = 10
    """Number of connections to maintain in the pool"""
    
    MAX_OVERFLOW: int = 20
    """Maximum number of connections that can be created beyond pool_size"""
    
    POOL_TIMEOUT: int = 30
    """Timeout in seconds for getting a connection from the pool"""
    
    POOL_RECYCLE: int = 3600
    """Recycle connections after this many seconds (default: 1 hour)"""
    
    # ========================================================================
    # Query Settings
    # ========================================================================
    
    DEFAULT_LIMIT: int = 1000
    """Default number of records to return if not specified"""
    
    MAX_LIMIT: int = 10000
    """Maximum number of records that can be requested"""
    
    QUERY_TIMEOUT: int = 30
    """Query execution timeout in seconds"""
    
    # ========================================================================
    # API Settings
    # ========================================================================
    
    API_PREFIX: str = "/api/v1"
    """URL prefix for API endpoints"""
    
    CORS_ORIGINS: List[str] = ["*"]
    """Allowed CORS origins"""
    
    # ========================================================================
    # Logging Settings (Phase 2)
    # ========================================================================
    
    LOG_LEVEL: str = "INFO"
    """Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"""
    
    LOG_FORMAT: str = "json"
    """Log format: json or text"""
    
    # ========================================================================
    # Security Settings (Future Phases)
    # ========================================================================
    
    API_KEY_ENABLED: bool = False
    """Enable API key authentication (Phase 5)"""
    
    RATE_LIMIT_ENABLED: bool = False
    """Enable rate limiting (Phase 5)"""
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env
    
    def get_clickhouse_url(self) -> str:
        """
        Build ClickHouse connection URL.
        
        Returns:
            Connection URL string
        """
        protocol = "https" if self.CLICKHOUSE_SECURE else "http"
        return f"{protocol}://{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT}"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Create global settings instance
settings = Settings()
