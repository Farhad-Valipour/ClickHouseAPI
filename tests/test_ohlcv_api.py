"""
Tests for OHLCV data endpoints.

Updated to test ISO 8601 format support with backward compatibility.
"""

import pytest
from fastapi import status
from unittest.mock import Mock


# ============================================================================
# ISO 8601 Format Tests
# ============================================================================

def test_get_ohlcv_success_iso8601(client, mock_db, mock_query_result):
    """Test successful OHLCV data retrieval with ISO 8601 format."""
    # Mock execute_query to return sample data
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert "metadata" in data
    assert isinstance(data["data"], list)


def test_get_ohlcv_success_iso8601_timezone_offset(client, mock_db, mock_query_result):
    """Test successful OHLCV data retrieval with ISO 8601 timezone offset."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00+03:00",
            "end": "2025-08-01T00:00:00+03:00",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_get_ohlcv_success_iso8601_basic(client, mock_db, mock_query_result):
    """Test successful OHLCV data retrieval with basic ISO 8601 format."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00",
            "end": "2025-08-01T00:00:00",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


# ============================================================================
# Legacy Format Tests (Backward Compatibility)
# ============================================================================

def test_get_ohlcv_success_legacy_format(client, mock_db, mock_query_result):
    """Test successful OHLCV data retrieval with legacy format."""
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


def test_get_ohlcv_mixed_formats(client, mock_db, mock_query_result):
    """Test OHLCV with mixed ISO 8601 and legacy formats."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",  # ISO 8601
            "end": "20250801-0000",           # Legacy
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


# ============================================================================
# Invalid Format Tests
# ============================================================================

def test_get_ohlcv_invalid_time_format(client):
    """Test OHLCV endpoint with invalid time format."""
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "invalid-time",
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_ohlcv_invalid_iso8601_incomplete(client):
    """Test OHLCV endpoint with incomplete ISO 8601 format."""
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01",  # Missing time part
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_ohlcv_invalid_iso8601_wrong_separator(client):
    """Test OHLCV endpoint with wrong separator."""
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025/07/01T00:00:00",  # Wrong separator
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Missing Parameters Tests
# ============================================================================

def test_get_ohlcv_missing_required_params(client):
    """Test OHLCV endpoint with missing required parameters."""
    response = client.get("/api/v1/ohlcv")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_ohlcv_missing_start(client):
    """Test OHLCV endpoint with missing start parameter."""
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Pagination Tests
# ============================================================================

def test_get_ohlcv_pagination_iso8601(client, mock_db, mock_query_result):
    """Test OHLCV endpoint pagination with ISO 8601."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "limit": 10,
            "offset": 5
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["metadata"]["limit"] == 10
    assert data["metadata"]["offset"] == 5


def test_get_ohlcv_pagination_legacy(client, mock_db, mock_query_result):
    """Test OHLCV endpoint pagination with legacy format."""
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
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "limit": 99999  # Way over MAX_LIMIT
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Should be capped at MAX_LIMIT (10000)
    assert data["metadata"]["limit"] <= 10000


# ============================================================================
# Response Structure Tests
# ============================================================================

def test_get_ohlcv_response_structure(client, mock_db, mock_query_result):
    """Test that OHLCV response has correct structure."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z"
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
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z"
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


def test_get_ohlcv_timestamp_format(client, mock_db, mock_query_result):
    """Test that timestamps in response are in ISO 8601 format."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    data = response.json()
    
    # Check metadata timestamp
    assert "T" in data["metadata"]["timestamp"]  # ISO 8601 format
    
    # Check candle_time if data exists
    if len(data["data"]) > 0:
        assert "T" in data["data"][0]["candle_time"]  # ISO 8601 format


# ============================================================================
# Latest Endpoint Tests
# ============================================================================

def test_get_latest_success(client, mock_db, mock_query_result):
    """Test successful latest candle retrieval."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv/latest",
        params={"symbol": "BINANCE:BTCUSDT.P"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert "metadata" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1


def test_get_latest_response_structure(client, mock_db, mock_query_result):
    """Test latest endpoint response structure."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv/latest",
        params={"symbol": "BINANCE:BTCUSDT.P"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Should have single element in data array
    assert len(data["data"]) == 1
    
    record = data["data"][0]
    required_fields = [
        "candle_time", "symbol", "open", 
        "high", "low", "close", "volume"
    ]
    for field in required_fields:
        assert field in record


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


# ============================================================================
# Optional End Parameter Tests
# ============================================================================

def test_get_ohlcv_without_end_time_iso8601(client, mock_db, mock_query_result):
    """Test OHLCV endpoint without end time (defaults to now) - ISO 8601."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z"
            # No end parameter
        }
    )
    
    assert response.status_code == status.HTTP_200_OK


def test_get_ohlcv_without_end_time_legacy(client, mock_db, mock_query_result):
    """Test OHLCV endpoint without end time - legacy format."""
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


# ============================================================================
# Root Endpoint Test
# ============================================================================

def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "service" in data
    assert "version" in data
    assert "docs" in data
    assert "endpoints" in data


# ============================================================================
# Edge Cases Tests
# ============================================================================

def test_get_ohlcv_with_milliseconds(client, mock_db, mock_query_result):
    """Test OHLCV with ISO 8601 milliseconds format."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00.000Z",
            "end": "2025-08-01T23:59:59.999Z",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_get_ohlcv_zero_offset(client, mock_db, mock_query_result):
    """Test OHLCV with zero offset."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "offset": 0
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["metadata"]["offset"] == 0


def test_get_ohlcv_minimum_limit(client, mock_db, mock_query_result):
    """Test OHLCV with minimum limit (1)."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "limit": 1
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["metadata"]["limit"] == 1


def test_get_ohlcv_special_symbols(client, mock_db, mock_query_result):
    """Test OHLCV with special symbol characters."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "NASDAQ:AAPL",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Metadata Validation Tests
# ============================================================================

def test_get_ohlcv_metadata_has_more_true(client, mock_db):
    """Test has_more flag when there's more data available."""
    # Create a result with exactly limit records
    mock_result = Mock()
    mock_result.result_rows = [(None, None, 1.0, 1.0, 1.0, 1.0, 1.0)] * 100
    mock_db.execute_query = Mock(return_value=mock_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # When we get exactly limit records, has_more should be True
    assert data["metadata"]["has_more"] is True


def test_get_ohlcv_metadata_has_more_false(client, mock_db):
    """Test has_more flag when there's no more data."""
    # Create a result with fewer than limit records
    mock_result = Mock()
    mock_result.result_rows = [(None, None, 1.0, 1.0, 1.0, 1.0, 1.0)] * 50
    mock_db.execute_query = Mock(return_value=mock_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z",
            "limit": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # When we get fewer than limit records, has_more should be False
    assert data["metadata"]["has_more"] is False


def test_get_ohlcv_query_time_present(client, mock_db, mock_query_result):
    """Test that query_time_ms is present in metadata."""
    mock_db.execute_query = Mock(return_value=mock_query_result)
    
    response = client.get(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "2025-07-01T00:00:00Z",
            "end": "2025-08-01T00:00:00Z"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "query_time_ms" in data["metadata"]
    assert isinstance(data["metadata"]["query_time_ms"], (int, float))
    assert data["metadata"]["query_time_ms"] >= 0
