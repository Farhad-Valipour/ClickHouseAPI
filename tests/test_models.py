"""
Tests for Pydantic models and validation.

Updated to test ISO 8601 format support with backward compatibility.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models.request import OHLCVQueryParams, LatestQueryParams, MultiSymbolQueryParams
from app.models.response import OHLCVData, ResponseMetadata, OHLCVResponse


class TestOHLCVQueryParams:
    """Tests for OHLCVQueryParams model."""
    
    # ============================================================================
    # ISO 8601 Format Tests
    # ============================================================================
    
    def test_valid_params_iso8601_utc(self):
        """Test creation with valid ISO 8601 UTC parameters."""
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00Z",
            end="2025-08-01T00:00:00Z",
            limit=1000,
            offset=0
        )
        
        assert params.symbol == "BINANCE:BTCUSDT.P"
        assert params.start == "2025-07-01T00:00:00Z"
        assert params.end == "2025-08-01T00:00:00Z"
        assert params.limit == 1000
        assert params.offset == 0
    
    def test_valid_params_iso8601_basic(self):
        """Test creation with basic ISO 8601 format (no timezone)."""
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00",
            end="2025-08-01T00:00:00",
            limit=1000
        )
        
        assert params.start == "2025-07-01T00:00:00"
        assert params.end == "2025-08-01T00:00:00"
    
    def test_valid_params_iso8601_timezone_offset(self):
        """Test creation with ISO 8601 timezone offset."""
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00+03:00",
            end="2025-08-01T00:00:00+03:00",
            limit=1000
        )
        
        assert params.start == "2025-07-01T00:00:00+03:00"
        assert params.end == "2025-08-01T00:00:00+03:00"
    
    def test_valid_params_iso8601_milliseconds(self):
        """Test creation with ISO 8601 milliseconds."""
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00.000Z",
            end="2025-08-01T23:59:59.999Z",
            limit=1000
        )
        
        assert params.start == "2025-07-01T00:00:00.000Z"
        assert params.end == "2025-08-01T23:59:59.999Z"
    
    # ============================================================================
    # Legacy Format Tests (Backward Compatibility)
    # ============================================================================
    
    def test_valid_params_legacy_format(self):
        """Test creation with legacy format (backward compatibility)."""
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
    
    def test_mixed_formats(self):
        """Test creation with mixed ISO 8601 and legacy formats."""
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00Z",  # ISO 8601
            end="20250801-0000",           # Legacy
            limit=1000
        )
        
        assert params.start == "2025-07-01T00:00:00Z"
        assert params.end == "20250801-0000"
    
    # ============================================================================
    # Invalid Format Tests
    # ============================================================================
    
    def test_invalid_time_format_iso8601(self):
        """Test that invalid ISO 8601 format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="invalid-time",
                end="2025-08-01T00:00:00Z"
            )
        
        errors = exc_info.value.errors()
        assert any("Invalid time format" in str(e) for e in errors)
    
    def test_invalid_time_format_incomplete(self):
        """Test that incomplete time format raises error."""
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="2025-07-01",  # Missing time part
                end="2025-08-01T00:00:00Z"
            )
    
    def test_invalid_time_format_wrong_separator(self):
        """Test that wrong separator raises error."""
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="2025/07/01T00:00:00",  # Wrong separator
                end="2025-08-01T00:00:00Z"
            )
    
    # ============================================================================
    # Time Range Validation Tests
    # ============================================================================
    
    def test_end_before_start_iso8601(self):
        """Test that end before start raises error (ISO 8601)."""
        with pytest.raises(ValidationError) as exc_info:
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="2025-08-01T00:00:00Z",
                end="2025-07-01T00:00:00Z"  # Before start
            )
        
        errors = exc_info.value.errors()
        assert any("End time cannot be before start time" in str(e) for e in errors)
    
    def test_end_before_start_legacy(self):
        """Test that end before start raises error (legacy format)."""
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="BINANCE:BTCUSDT.P",
                start="20250801-0000",
                end="20250701-0000"  # Before start
            )
    
    def test_equal_start_end_iso8601(self):
        """Test that equal start and end times are allowed."""
        # Note: The validation now allows equal times (for getting specific candle)
        # Based on original code at line 94: if end_dt < start_dt (not <=)
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00Z",
            end="2025-07-01T00:00:00Z"
        )
        
        assert params.start == params.end
    
    # ============================================================================
    # Limit and Offset Validation Tests
    # ============================================================================
    
    def test_limit_validation(self):
        """Test limit validation."""
        # Valid limits
        params = OHLCVQueryParams(
            symbol="TEST",
            start="2025-07-01T00:00:00Z",
            limit=1
        )
        assert params.limit == 1
        
        params = OHLCVQueryParams(
            symbol="TEST",
            start="2025-07-01T00:00:00Z",
            limit=10000
        )
        assert params.limit == 10000
        
        # Invalid limits
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="TEST",
                start="2025-07-01T00:00:00Z",
                limit=0  # Too low
            )
        
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="TEST",
                start="2025-07-01T00:00:00Z",
                limit=10001  # Too high
            )
    
    def test_offset_validation(self):
        """Test offset validation."""
        # Valid offset
        params = OHLCVQueryParams(
            symbol="TEST",
            start="2025-07-01T00:00:00Z",
            offset=100
        )
        assert params.offset == 100
        
        # Negative offset should fail
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="TEST",
                start="2025-07-01T00:00:00Z",
                offset=-1
            )
    
    # ============================================================================
    # Optional End Parameter Tests
    # ============================================================================
    
    def test_optional_end_iso8601(self):
        """Test that end parameter is optional (ISO 8601)."""
        params = OHLCVQueryParams(
            symbol="TEST",
            start="2025-07-01T00:00:00Z"
            # No end parameter
        )
        
        assert params.end is None
    
    def test_optional_end_legacy(self):
        """Test that end parameter is optional (legacy)."""
        params = OHLCVQueryParams(
            symbol="TEST",
            start="20250701-0000"
            # No end parameter
        )
        
        assert params.end is None
    
    # ============================================================================
    # Symbol Validation Tests
    # ============================================================================
    
    def test_symbol_validation(self):
        """Test symbol validation."""
        # Valid symbol
        params = OHLCVQueryParams(
            symbol="BINANCE:BTCUSDT.P",
            start="2025-07-01T00:00:00Z"
        )
        assert params.symbol == "BINANCE:BTCUSDT.P"
        
        # Empty symbol should fail
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol="",
                start="2025-07-01T00:00:00Z"
            )
    
    def test_symbol_length_validation(self):
        """Test symbol length validation."""
        # Max length symbol (50 chars)
        long_symbol = "A" * 50
        params = OHLCVQueryParams(
            symbol=long_symbol,
            start="2025-07-01T00:00:00Z"
        )
        assert params.symbol == long_symbol
        
        # Too long symbol should fail
        too_long = "A" * 51
        with pytest.raises(ValidationError):
            OHLCVQueryParams(
                symbol=too_long,
                start="2025-07-01T00:00:00Z"
            )


class TestMultiSymbolQueryParams:
    """Tests for MultiSymbolQueryParams model."""
    
    def test_valid_params_iso8601(self):
        """Test creation with valid ISO 8601 parameters."""
        params = MultiSymbolQueryParams(
            symbols=["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"],
            start="2025-07-01T00:00:00Z",
            end="2025-08-01T00:00:00Z",
            limit=1000
        )
        
        assert len(params.symbols) == 2
        assert params.start == "2025-07-01T00:00:00Z"
        assert params.end == "2025-08-01T00:00:00Z"
    
    def test_valid_params_legacy(self):
        """Test creation with legacy format."""
        params = MultiSymbolQueryParams(
            symbols=["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"],
            start="20250701-0000",
            end="20250801-0000",
            limit=1000
        )
        
        assert params.start == "20250701-0000"
        assert params.end == "20250801-0000"
    
    def test_invalid_time_format(self):
        """Test that invalid time format raises error."""
        with pytest.raises(ValidationError):
            MultiSymbolQueryParams(
                symbols=["BINANCE:BTCUSDT.P"],
                start="invalid-format",
                end="2025-08-01T00:00:00Z"
            )
    
    def test_symbols_validation(self):
        """Test symbols list validation."""
        # Valid symbols
        params = MultiSymbolQueryParams(
            symbols=["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"],
            start="2025-07-01T00:00:00Z"
        )
        assert len(params.symbols) == 2
        
        # Empty symbols list should fail
        with pytest.raises(ValidationError):
            MultiSymbolQueryParams(
                symbols=[],
                start="2025-07-01T00:00:00Z"
            )
    
    def test_max_symbols_validation(self):
        """Test maximum symbols validation."""
        # 100 symbols (max)
        symbols = [f"SYMBOL{i}" for i in range(100)]
        params = MultiSymbolQueryParams(
            symbols=symbols,
            start="2025-07-01T00:00:00Z"
        )
        assert len(params.symbols) == 100
        
        # 101 symbols should fail
        symbols_too_many = [f"SYMBOL{i}" for i in range(101)]
        with pytest.raises(ValidationError):
            MultiSymbolQueryParams(
                symbols=symbols_too_many,
                start="2025-07-01T00:00:00Z"
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
    
    def test_symbol_too_long(self):
        """Test that too long symbol raises error."""
        long_symbol = "A" * 51
        with pytest.raises(ValidationError):
            LatestQueryParams(symbol=long_symbol)


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
        # Should be in ISO 8601 format
        assert 'T' in json_data['candle_time']


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
    
    def test_timestamp_auto_generation(self):
        """Test that timestamp is auto-generated."""
        metadata = ResponseMetadata(
            total_records=100,
            limit=1000,
            offset=0,
            has_more=False,
            query_time_ms=45.2
        )
        
        # Timestamp should be recent (within last second)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        assert (now - metadata.timestamp) < timedelta(seconds=1)


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
    
    def test_empty_data_response(self):
        """Test response with empty data array."""
        metadata = ResponseMetadata(
            total_records=0,
            limit=1000,
            offset=0,
            has_more=False,
            query_time_ms=12.3
        )
        
        response = OHLCVResponse(
            success=True,
            data=[],
            metadata=metadata
        )
        
        assert response.success is True
        assert len(response.data) == 0
        assert response.metadata.total_records == 0
    
    def test_multiple_records_response(self):
        """Test response with multiple data records."""
        data = [
            OHLCVData(
                candle_time=datetime(2025, 7, 1, i, 0),
                symbol="TEST",
                open=100.0 + i,
                high=110.0 + i,
                low=90.0 + i,
                close=105.0 + i,
                volume=1000.0
            )
            for i in range(5)
        ]
        
        metadata = ResponseMetadata(
            total_records=5,
            limit=1000,
            offset=0,
            has_more=False,
            query_time_ms=78.9
        )
        
        response = OHLCVResponse(
            success=True,
            data=data,
            metadata=metadata
        )
        
        assert response.success is True
        assert len(response.data) == 5
        assert response.metadata.total_records == 5
