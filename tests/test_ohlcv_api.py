"""
Tests for OHLCV data endpoints.
"""

import pytest
from fastapi import status
from unittest.mock import Mock


def test_get_ohlcv_success(client, mock_db, mock_query_result):
    """Test successful OHLCV data retrieval."""
    # Mock execute_query to return sample data
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000",
            "end": "20250801-0000",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert "metadata" in data
    assert isinstance(data["data"], list)


def test_get_ohlcv_invalid_time_format(client):
    """Test OHLCV endpoint with invalid time format."""
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "invalid-time",
            "end": "20250801-0000"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_ohlcv_missing_required_params(client):
    """Test OHLCV endpoint with missing required parameters."""
    response = client.get("/api/v1/ohlcv")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_ohlcv_pagination(client, mock_db, mock_query_result):
    """Test OHLCV endpoint pagination."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000",
            "end": "20250801-0000",
            "limit": 10,
            "offset": 5
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["metadata"]["limit"] == 10
    assert data["metadata"]["offset"] == 5


def test_get_ohlcv_max_limit(client, mock_db, mock_query_result):
    """Test that limit is capped at MAX_LIMIT."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000",
            "end": "20250801-0000",
            "limit": 99999  # Way over MAX_LIMIT
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Should be capped at MAX_LIMIT (10000)
    assert data["metadata"]["limit"] <= 10000


def test_get_ohlcv_response_structure(client, mock_db, mock_query_result):
    """Test that OHLCV response has correct structure."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000",
            "end": "20250801-0000"
        }
    )
    
    data = response.json()
    
    # Check main structure
    assert "success" in data
    assert "data" in data
    assert "metadata" in data
    
    # Check metadata structure
    metadata = data["metadata"]
    required_metadata_fields = [
        "total_records", "limit", "offset", 
        "has_more", "query_time_ms", "timestamp"
    ]
    for field in required_metadata_fields:
        assert field in metadata


def test_get_ohlcv_data_structure(client, mock_db, mock_query_result):
    """Test that OHLCV data records have correct structure."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000",
            "end": "20250801-0000"
        }
    )
    
    data = response.json()
    
    if len(data["data"]) > 0:
        record = data["data"][0]
        required_fields = [
            "candle_time", "symbol", "open", 
            "high", "low", "close", "volume"
        ]
        for field in required_fields:
            assert field in record


def test_get_latest_success(client, mock_db, mock_query_result):
    """Test successful latest candle retrieval."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv/latest",
        params={"symbol": "BINANCE:BTCUSDT.P"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    required_fields = [
        "candle_time", "symbol", "open", 
        "high", "low", "close", "volume"
    ]
    for field in required_fields:
        assert field in data


def test_get_latest_not_found(client, mock_db):
    """Test latest candle endpoint when no data found."""
    # Mock empty result
    mock_result = Mock()
    mock_result.result_rows = []
    mock_db.execute_query = Mock(return_value=mock_result)
    
    response = client.get(
        "/api/v1/ohlcv/latest",
        params={"symbol": "NONEXISTENT"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    
    assert data["success"] is False
    assert data["error_code"] == "DATA_NOT_FOUND"


def test_get_latest_missing_symbol(client):
    """Test latest endpoint with missing symbol parameter."""
    response = client.get("/api/v1/ohlcv/latest")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_ohlcv_without_end_time(client, mock_db, mock_query_result):
    """Test OHLCV endpoint without end time (defaults to now)."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000"
            # No end parameter
        }
    )
    
    assert response.status_code == status.HTTP_200_OK


def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "service" in data
    assert "version" in data
    assert "docs" in data
    assert "endpoints" in data
