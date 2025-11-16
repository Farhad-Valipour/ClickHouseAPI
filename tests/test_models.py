"""
Tests for Pydantic models and validation.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models.request import OHLCVQueryParams, LatestQueryParams
from app.models.response import OHLCVData, ResponseMetadata, OHLCVResponse


class TestOHLCVQueryParams:
    """Tests for OHLCVQueryParams model."""
    
    def test_valid_params(self):
        """Test creation with valid parameters."""
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="20250701-0000",
            end="20250801-0000",
            limit=1000,
            offset=0
        )
        
        assert params.symbol == "BINANCE:BTCUSDT.P"
        assert params.start == "20250701-0000"
        assert params.end == "20250801-0000"
        assert params.limit == 1000
        assert params.offset == 0
    
    def test_invalid_time_format(self):
        """Test that invalid time format raises error."""
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="invalid-time",
                end="20250801-0000"
            )
    
    def test_end_before_start(self):
        """Test that end before start raises error."""
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="20250801-0000",
                end="20250701-0000"  # Before start
            )
    
    def test_limit_validation(self):
        """Test limit validation."""
        # Valid limits
        params = OHLCVQueryParams(
            symbol="TEST",
            start="20250701-0000",
            limit=1
        )
        assert params.limit == 1
        
        params = OHLCVQueryParams(
            symbol="TEST",
            start="20250701-0000",
            limit=10000
        )
        assert params.limit == 10000
        
        # Invalid limits
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="TEST",
                start="20250701-0000",
                limit=0  # Too low
            )
        
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="TEST",
                start="20250701-0000",
                limit=10001  # Too high
            )
    
    def test_offset_validation(self):
        """Test offset validation."""
        # Valid offset
        params = OHLCVQueryParams(
            symbol="TEST",
            start="20250701-0000",
            offset=100
        )
        assert params.offset == 100
        
        # Negative offset should fail
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="TEST",
                start="20250701-0000",
                offset=-1
            )
    
    def test_optional_end(self):
        """Test that end parameter is optional."""
        params = OHLCVQueryParams(
            symbol="TEST",
            start="20250701-0000"
            # No end parameter
        )
        
        assert params.end is None
    
    def test_symbol_validation(self):
        """Test symbol validation."""
        # Valid symbol
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="20250701-0000"
        )
        assert params.symbol == "BINANCE:BTCUSDT.P"
        
        # Empty symbol should fail
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="",
                start="20250701-0000"
            )


class TestLatestQueryParams:
    """Tests for LatestQueryParams model."""
    
    def test_valid_params(self):
        """Test creation with valid symbol."""
        params = LatestQueryParams(symbol="BINANCE:BTCUSDT.P")
        assert params.symbol == "BINANCE:BTCUSDT.P"
    
    def test_empty_symbol(self):
        """Test that empty symbol raises error."""
        with pytest.raises(ValidationError):
            LatestQueryParams(symbol="")


class TestOHLCVData:
    """Tests for OHLCVData model."""
    
    def test_valid_data(self):
        """Test creation with valid OHLCV data."""
        data = OHLCVData(
            candle_time=datetime(2025, 7, 1, 0, 0),
            symbol="BINANCE:BTCUSDT.P",
            open=50000.0,
            high=51000.0,
            low=49500.0,
            close=50500.0,
            volume=1234567.89
        )
        
        assert data.symbol == "BINANCE:BTCUSDT.P"
        assert data.open == 50000.0
        assert data.high == 51000.0
        assert data.low == 49500.0
        assert data.close == 50500.0
        assert data.volume == 1234567.89
    
    def test_datetime_serialization(self):
        """Test that datetime is properly serialized."""
        data = OHLCVData(
            candle_time=datetime(2025, 7, 1, 0, 0),
            symbol="TEST",
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=1000.0
        )
        
        json_data = data.model_dump(mode='json')
        assert isinstance(json_data['candle_time'], str)


class TestResponseMetadata:
    """Tests for ResponseMetadata model."""
    
    def test_valid_metadata(self):
        """Test creation with valid metadata."""
        metadata = ResponseMetadata(
            total_records=100,
            limit=1000,
            offset=0,
            has_more=False,
            query_time_ms=45.2
        )
        
        assert metadata.total_records == 100
        assert metadata.limit == 1000
        assert metadata.offset == 0
        assert metadata.has_more is False
        assert metadata.query_time_ms == 45.2
        assert isinstance(metadata.timestamp, datetime)


class TestOHLCVResponse:
    """Tests for OHLCVResponse model."""
    
    def test_valid_response(self):
        """Test creation with valid response data."""
        data = [
            OHLCVData(
                candle_time=datetime(2025, 7, 1, 0, 0),
                symbol="TEST",
                open=100.0,
                high=110.0,
                low=90.0,
                close=105.0,
                volume=1000.0
            )
        ]
        
        metadata = ResponseMetadata(
            total_records=1,
            limit=1000,
            offset=0,
            has_more=False,
            query_time_ms=45.2
        )
        
        response = OHLCVResponse(
            success=True,
            data=data,
            metadata=metadata
        )
        
        assert response.success is True
        assert len(response.data) == 1
        assert response.metadata.total_records == 1
