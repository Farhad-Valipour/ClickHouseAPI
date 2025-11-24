"""
Tests for time parsing utilities.

Updated to test ISO 8601 format support with backward compatibility.
"""

import pytest
from datetime import datetime, timezone, timedelta

from app.utils.time_parser import (
    parse_time_param,
    format_for_clickhouse,
    validate_time_range
)
from app.core.exceptions import InvalidTimeFormatError


class TestParseTimeParam:
    """Tests for parse_time_param function."""
    
    # ============================================================================
    # ISO 8601 Format Tests
    # ============================================================================
    
    def test_iso8601_basic(self):
        """Test parsing basic ISO 8601 format without timezone."""
        result = parse_time_param("2025-07-01T00:00:00")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.tzinfo is None  # Naive datetime
    
    def test_iso8601_with_utc_z(self):
        """Test parsing ISO 8601 with UTC indicator (Z)."""
        result = parse_time_param("2025-07-01T00:00:00Z")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.tzinfo == timezone.utc  # UTC aware
    
    def test_iso8601_with_timezone_offset_positive(self):
        """Test parsing ISO 8601 with positive timezone offset."""
        result = parse_time_param("2025-07-01T15:30:00+03:00")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 15
        assert result.minute == 30
        # Check timezone offset
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(None) == timedelta(hours=3)
    
    def test_iso8601_with_timezone_offset_negative(self):
        """Test parsing ISO 8601 with negative timezone offset."""
        result = parse_time_param("2025-07-01T10:00:00-05:00")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 10
        assert result.minute == 0
        # Check timezone offset
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(None) == timedelta(hours=-5)
    
    def test_iso8601_with_milliseconds(self):
        """Test parsing ISO 8601 with milliseconds."""
        result = parse_time_param("2025-07-01T12:30:45.123Z")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 12
        assert result.minute == 30
        assert result.second == 45
        assert result.microsecond == 123000  # 0.123 seconds = 123000 microseconds
        assert result.tzinfo == timezone.utc
    
    def test_iso8601_with_microseconds(self):
        """Test parsing ISO 8601 with microseconds."""
        result = parse_time_param("2025-07-01T12:30:45.123456Z")
        
        assert isinstance(result, datetime)
        assert result.microsecond == 123456
        assert result.tzinfo == timezone.utc
    
    def test_iso8601_different_times(self):
        """Test parsing different times in ISO 8601 format."""
        # Midnight
        result1 = parse_time_param("2025-07-01T00:00:00Z")
        assert result1.hour == 0 and result1.minute == 0
        
        # Noon
        result2 = parse_time_param("2025-07-01T12:00:00Z")
        assert result2.hour == 12 and result2.minute == 0
        
        # End of day
        result3 = parse_time_param("2025-07-01T23:59:59Z")
        assert result3.hour == 23 and result3.minute == 59 and result3.second == 59
    
    # ============================================================================
    # Legacy Format Tests (Backward Compatibility)
    # ============================================================================
    
    def test_legacy_format_basic(self):
        """Test parsing legacy format (YYYYMMDD-HHmm)."""
        result = parse_time_param("20250701-0000")
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 7
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0
    
    def test_legacy_format_with_minutes(self):
        """Test parsing legacy time with minutes."""
        result = parse_time_param("20250701-1530")
        
        assert result.hour == 15
        assert result.minute == 30
    
    def test_legacy_format_different_dates(self):
        """Test parsing different dates in legacy format."""
        # January 1st
        result1 = parse_time_param("20250101-0000")
        assert result1.month == 1 and result1.day == 1
        
        # December 31st
        result2 = parse_time_param("20251231-2359")
        assert result2.month == 12 and result2.day == 31
        assert result2.hour == 23 and result2.minute == 59
    
    # ============================================================================
    # Invalid Format Tests
    # ============================================================================
    
    def test_invalid_format_random_string(self):
        """Test that random string raises error."""
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("invalid-time")
    
    def test_invalid_format_incomplete_iso8601(self):
        """Test that incomplete ISO 8601 format raises error."""
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("2025-07-01")  # Missing time part
    
    def test_invalid_format_wrong_separator(self):
        """Test that wrong separator raises error."""
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("2025/07/01T00:00:00")  # Wrong separator
    
    def test_invalid_date_values(self):
        """Test that invalid date values raise error."""
        # Invalid month
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("2025-13-01T00:00:00Z")
        
        # Invalid day
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("2025-07-32T00:00:00Z")
    
    def test_invalid_time_values(self):
        """Test that invalid time values raise error."""
        # Invalid hour
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("2025-07-01T25:00:00Z")
        
        # Invalid minute
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("2025-07-01T00:60:00Z")
    
    def test_invalid_legacy_format(self):
        """Test that invalid legacy format raises error."""
        with pytest.raises(InvalidTimeFormatError):
            parse_time_param("20251301-0000")  # Month 13
    
    def test_wrong_format_patterns(self):
        """Test various wrong format patterns."""
        invalid_formats = [
            "2025-07-01",           # Missing time
            "20250701",             # Missing separator and time
            "2025/07/01-0000",      # Wrong date separator
            "01-07-2025T00:00:00",  # Wrong date order
            "2025-7-1T00:00:00",    # Missing leading zeros
        ]
        
        for invalid_format in invalid_formats:
            with pytest.raises(InvalidTimeFormatError):
                parse_time_param(invalid_format)
    
    # ============================================================================
    # Error Message Tests
    # ============================================================================
    
    def test_error_message_content(self):
        """Test that error message contains helpful information."""
        try:
            parse_time_param("bad-format")
        except InvalidTimeFormatError as e:
            assert "Invalid time format" in e.message
            assert "bad-format" in e.provided
            assert "ISO 8601" in e.expected


class TestFormatForClickHouse:
    """Tests for format_for_clickhouse function."""
    
    def test_format_naive_datetime(self):
        """Test formatting naive datetime for ClickHouse."""
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
    
    def test_format_utc_aware_datetime(self):
        """Test formatting UTC-aware datetime."""
        dt = datetime(2025, 7, 1, 15, 30, 45, tzinfo=timezone.utc)
        result = format_for_clickhouse(dt)
        
        assert result == "2025-07-01 15:30:45"
    
    def test_format_timezone_aware_datetime(self):
        """Test formatting timezone-aware datetime (converts to UTC)."""
        # Create datetime with +03:00 offset
        tz_plus3 = timezone(timedelta(hours=3))
        dt = datetime(2025, 7, 1, 18, 30, 45, tzinfo=tz_plus3)
        result = format_for_clickhouse(dt)
        
        # Should be converted to UTC: 18:30 +03:00 = 15:30 UTC
        assert result == "2025-07-01 15:30:45"
    
    def test_format_negative_timezone_offset(self):
        """Test formatting datetime with negative timezone offset."""
        # Create datetime with -05:00 offset
        tz_minus5 = timezone(timedelta(hours=-5))
        dt = datetime(2025, 7, 1, 10, 0, 0, tzinfo=tz_minus5)
        result = format_for_clickhouse(dt)
        
        # Should be converted to UTC: 10:00 -05:00 = 15:00 UTC
        assert result == "2025-07-01 15:00:00"


class TestValidateTimeRange:
    """Tests for validate_time_range function."""
    
    def test_valid_range_naive_datetimes(self):
        """Test valid time range with naive datetimes."""
        start = datetime(2025, 7, 1, 0, 0, 0)
        end = datetime(2025, 8, 1, 0, 0, 0)
        
        result = validate_time_range(start, end)
        assert result is True
    
    def test_valid_range_utc_datetimes(self):
        """Test valid time range with UTC-aware datetimes."""
        start = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        result = validate_time_range(start, end)
        assert result is True
    
    def test_valid_range_different_timezones(self):
        """Test valid time range with different timezones."""
        tz_plus3 = timezone(timedelta(hours=3))
        tz_minus5 = timezone(timedelta(hours=-5))
        
        start = datetime(2025, 7, 1, 0, 0, 0, tzinfo=tz_minus5)
        end = datetime(2025, 7, 1, 10, 0, 0, tzinfo=tz_plus3)
        
        result = validate_time_range(start, end)
        assert result is True
    
    def test_end_before_start_naive(self):
        """Test that end before start raises error (naive datetimes)."""
        start = datetime(2025, 8, 1, 0, 0, 0)
        end = datetime(2025, 7, 1, 0, 0, 0)
        
        with pytest.raises(ValueError) as exc_info:
            validate_time_range(start, end)
        
        assert "must be after" in str(exc_info.value)
    
    def test_end_before_start_utc(self):
        """Test that end before start raises error (UTC datetimes)."""
        start = datetime(2025, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        with pytest.raises(ValueError):
            validate_time_range(start, end)
    
    def test_same_time_naive(self):
        """Test that same start and end raises error (naive)."""
        start = datetime(2025, 7, 1, 0, 0, 0)
        end = datetime(2025, 7, 1, 0, 0, 0)
        
        with pytest.raises(ValueError):
            validate_time_range(start, end)
    
    def test_same_time_utc(self):
        """Test that same start and end raises error (UTC)."""
        start = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        with pytest.raises(ValueError):
            validate_time_range(start, end)
    
    def test_none_end(self):
        """Test that None end is valid."""
        start = datetime(2025, 7, 1, 0, 0, 0)
        
        result = validate_time_range(start, None)
        assert result is True
    
    def test_none_end_with_timezone(self):
        """Test that None end is valid with timezone-aware start."""
        start = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        result = validate_time_range(start, None)
        assert result is True


class TestIntegration:
    """Integration tests for time utilities."""
    
    def test_parse_and_format_iso8601(self):
        """Test parsing ISO 8601 and formatting for ClickHouse."""
        time_str = "2025-07-01T15:30:00Z"
        
        # Parse
        dt = parse_time_param(time_str)
        
        # Format
        formatted = format_for_clickhouse(dt)
        
        assert formatted == "2025-07-01 15:30:00"
    
    def test_parse_and_format_legacy(self):
        """Test parsing legacy format and formatting for ClickHouse."""
        time_str = "20250701-1530"
        
        # Parse
        dt = parse_time_param(time_str)
        
        # Format
        formatted = format_for_clickhouse(dt)
        
        assert formatted == "2025-07-01 15:30:00"
    
    def test_parse_validate_format_iso8601(self):
        """Test complete workflow with ISO 8601 format."""
        start_str = "2025-07-01T00:00:00Z"
        end_str = "2025-08-01T00:00:00Z"
        
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
    
    def test_parse_validate_format_legacy(self):
        """Test complete workflow with legacy format."""
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
    
    def test_mixed_format_workflow(self):
        """Test workflow with mixed ISO 8601 and legacy formats."""
        # Start with ISO 8601
        start_str = "2025-07-01T00:00:00Z"
        start_dt = parse_time_param(start_str)
        
        # End with legacy
        end_str = "20250801-0000"
        end_dt = parse_time_param(end_str)
        
        # Should work together
        validate_time_range(start_dt, end_dt)
        
        start_formatted = format_for_clickhouse(start_dt)
        end_formatted = format_for_clickhouse(end_dt)
        
        assert start_formatted == "2025-07-01 00:00:00"
        assert end_formatted == "2025-08-01 00:00:00"
    
    def test_timezone_conversion_workflow(self):
        """Test complete workflow with timezone conversion."""
        # Parse time with timezone
        time_str = "2025-07-01T18:30:00+03:00"
        dt = parse_time_param(time_str)
        
        # Format for ClickHouse (should convert to UTC)
        formatted = format_for_clickhouse(dt)
        
        # 18:30 +03:00 = 15:30 UTC
        assert formatted == "2025-07-01 15:30:00"
