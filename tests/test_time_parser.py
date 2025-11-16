"""
Tests for time parsing utilities.
"""

import pytest
from datetime import datetime

from app.utils.time_parser import (
    parse_time_param,
    format_for_clickhouse,
    validate_time_range
)
from app.core.exceptions import InvalidTimeFormatError


class TestParseTimeParam:
    """Tests for parse_time_param function."""
    
    def test_valid_time(self):
        """Test parsing valid time string."""
        result = parse_time_param("20250701-0000")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0
    
    def test_valid_time_with_minutes(self):
        """Test parsing time with minutes."""
        result = parse_time_param("20250701-1530")
        
        assert result.hour == 15
        assert result.minute == 30
    
    def test_invalid_format(self):
        """Test that invalid format raises error."""
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("invalid-time")
    
    def test_invalid_date(self):
        """Test that invalid date raises error."""
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("20251301-0000")  # Month 13
    
    def test_wrong_format_pattern(self):
        """Test various wrong format patterns."""
        invalid_formats = [
            "2025-07-01",
            "20250701",
            "2025/07/01-0000",
            "01-07-2025-0000",
        ]
        
        for invalid_format in invalid_formats:
            with pytest.raises(InvalidTimeFormatError):
                parse_time_param(invalid_format)


class TestFormatForClickHouse:
    """Tests for format_for_clickhouse function."""
    
    def test_format_datetime(self):
        """Test formatting datetime for ClickHouse."""
        dt = datetime(2025, 7, 1, 15, 30, 45)
        result = format_for_clickhouse(dt)
        
        assert result == "2025-07-01 15:30:45"
    
    def test_format_midnight(self):
        """Test formatting midnight time."""
        dt = datetime(2025, 7, 1, 0, 0, 0)
        result = format_for_clickhouse(dt)
        
        assert result == "2025-07-01 00:00:00"
    
    def test_format_end_of_day(self):
        """Test formatting end of day."""
        dt = datetime(2025, 7, 1, 23, 59, 59)
        result = format_for_clickhouse(dt)
        
        assert result == "2025-07-01 23:59:59"


class TestValidateTimeRange:
    """Tests for validate_time_range function."""
    
    def test_valid_range(self):
        """Test valid time range."""
        start = datetime(2025, 7, 1, 0, 0, 0)
        end = datetime(2025, 8, 1, 0, 0, 0)
        
        result = validate_time_range(start, end)
        assert result is True
    
    def test_end_before_start(self):
        """Test that end before start raises error."""
        start = datetime(2025, 8, 1, 0, 0, 0)
        end = datetime(2025, 7, 1, 0, 0, 0)
        
        with pytest.raises(ValueError):
            validate_time_range(start, end)
    
    def test_same_time(self):
        """Test that same start and end raises error."""
        start = datetime(2025, 7, 1, 0, 0, 0)
        end = datetime(2025, 7, 1, 0, 0, 0)
        
        with pytest.raises(ValueError):
            validate_time_range(start, end)
    
    def test_none_end(self):
        """Test that None end is valid."""
        start = datetime(2025, 7, 1, 0, 0, 0)
        
        result = validate_time_range(start, None)
        assert result is True


class TestIntegration:
    """Integration tests for time utilities."""
    
    def test_parse_and_format(self):
        """Test parsing and formatting together."""
        time_str = "20250701-1530"
        
        # Parse
        dt = parse_time_param(time_str)
        
        # Format
        formatted = format_for_clickhouse(dt)
        
        assert formatted == "2025-07-01 15:30:00"
    
    def test_parse_validate_format(self):
        """Test complete workflow."""
        start_str = "20250701-0000"
        end_str = "20250801-0000"
        
        # Parse
        start_dt = parse_time_param(start_str)
        end_dt = parse_time_param(end_str)
        
        # Validate
        validate_time_range(start_dt, end_dt)
        
        # Format
        start_formatted = format_for_clickhouse(start_dt)
        end_formatted = format_for_clickhouse(end_dt)
        
        assert start_formatted == "2025-07-01 00:00:00"
        assert end_formatted == "2025-08-01 00:00:00"
