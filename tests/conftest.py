"""
Pytest configuration and fixtures.

This module provides shared fixtures for testing the API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from datetime import datetime

from app.main import app
from app.core.database import ClickHouseManager


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    
    Returns:
        TestClient instance
    """
    return TestClient(app)


@pytest.fixture
def mock_db(monkeypatch):
    """
    Create a mock database manager for testing.
    
    This fixture mocks the ClickHouseManager to avoid actual
    database connections during tests.
    
    Returns:
        Mock ClickHouseManager instance
    """
    mock_manager = Mock(spec=ClickHouseManager)
    
    # Mock connect method
    mock_manager.connect = Mock(return_value=None)
    
    # Mock get_client method
    mock_manager.get_client = Mock(return_value=Mock())
    
    # Mock health_check method
    mock_manager.health_check = Mock(return_value={
        "status": "up",
        "response_time_ms": 10.5,
        "database": "default"
    })
    
    # Patch the ClickHouseManager class
    monkeypatch.setattr(
        "app.core.database.ClickHouseManager.__new__",
        lambda cls: mock_manager
    )
    
    return mock_manager


@pytest.fixture
def sample_ohlcv_data():
    """
    Sample OHLCV data for testing.
    
    Returns:
        List of tuples representing OHLCV records
    """
    return [
        (
            datetime(2025, 7, 1, 0, 0, 0),
            "BINANCE:BTCUSDT.P",
            50000.0,
            51000.0,
            49500.0,
            50500.0,
            1234567.89
        ),
        (
            datetime(2025, 7, 1, 0, 1, 0),
            "BINANCE:BTCUSDT.P",
            50500.0,
            50800.0,
            50300.0,
            50600.0,
            987654.32
        ),
    ]


@pytest.fixture
def mock_query_result(sample_ohlcv_data):
    """
    Create a mock query result object.
    
    Args:
        sample_ohlcv_data: Sample data fixture
        
    Returns:
        Mock query result with result_rows
    """
    mock_result = MagicMock()
    mock_result.result_rows = sample_ohlcv_data
    return mock_result


@pytest.fixture
def valid_time_params():
    """
    Valid time parameters for testing.
    
    Returns:
        Dictionary with valid time parameters
    """
    return {
        "start": "20250701-0000",
        "end": "20250801-0000"
    }


@pytest.fixture
def invalid_time_params():
    """
    Invalid time parameters for testing.
    
    Returns:
        Dictionary with invalid time parameters
    """
    return {
        "start": "invalid-time",
        "end": "20250801-0000"
    }
