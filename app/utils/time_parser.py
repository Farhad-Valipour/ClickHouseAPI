"""
Time parsing and formatting utilities.

This module provides functions for parsing time parameters from
requests and formatting them for ClickHouse queries.

Supports ISO 8601 format with backward compatibility for legacy format.
"""

from datetime import datetime
from typing import Optional
import re

from app.core.exceptions import InvalidTimeFormatError


# ISO 8601 regex pattern
# Matches: 2025-07-01T00:00:00, 2025-07-01T00:00:00Z, 2025-07-01T00:00:00+03:00, 2025-07-01T00:00:00.000Z
ISO8601_PATTERN = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})?$'
)

# Legacy format pattern (YYYYMMDD-HHmm)
LEGACY_PATTERN = re.compile(r'^\d{8}-\d{4}$')


def parse_time_param(time_str: str) -> datetime:
    """
    Parse time parameter from request format to datetime.
    
    Supports both ISO 8601 format (recommended) and legacy format.
    
    Supported ISO 8601 formats:
    - 2025-07-01T00:00:00 (basic)
    - 2025-07-01T00:00:00Z (UTC)
    - 2025-07-01T00:00:00+03:00 (with timezone offset)
    - 2025-07-01T00:00:00.000Z (with milliseconds)
    
    Legacy format (deprecated):
    - YYYYMMDD-HHmm (e.g., 20250701-0000)
    
    Args:
        time_str: Time string in ISO 8601 or legacy format
        
    Returns:
        Parsed datetime object (timezone-aware if timezone provided, otherwise naive)
        
    Raises:
        InvalidTimeFormatError: If time format is invalid
        
    Examples:
        >>> parse_time_param("2025-07-01T00:00:00Z")
        datetime(2025, 7, 1, 0, 0, tzinfo=timezone.utc)
        
        >>> parse_time_param("2025-07-01T15:30:00+03:00")
        datetime(2025, 7, 1, 15, 30, tzinfo=timezone(timedelta(seconds=10800)))
        
        >>> parse_time_param("20250701-0000")  # Legacy format (deprecated)
        datetime(2025, 7, 1, 0, 0)
    """
    # Try ISO 8601 format first (recommended)
    if ISO8601_PATTERN.match(time_str):
        try:
            # Try parsing with different ISO 8601 formats
            
            # Format with timezone (Z or offset)
            if time_str.endswith('Z'):
                # Remove 'Z' and parse, then make it UTC aware
                base_str = time_str[:-1]
                if '.' in base_str:
                    # With milliseconds: 2025-07-01T00:00:00.000Z
                    dt = datetime.strptime(base_str, "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    # Without milliseconds: 2025-07-01T00:00:00Z
                    dt = datetime.strptime(base_str, "%Y-%m-%dT%H:%M:%S")
                # Make it timezone-aware (UTC)
                from datetime import timezone
                return dt.replace(tzinfo=timezone.utc)
            
            elif '+' in time_str or (time_str.count('-') > 2):
                # With timezone offset: 2025-07-01T00:00:00+03:00
                # Use fromisoformat which handles timezone offsets
                return datetime.fromisoformat(time_str)
            
            else:
                # Basic format without timezone: 2025-07-01T00:00:00
                if '.' in time_str:
                    # With milliseconds: 2025-07-01T00:00:00.000
                    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    # Standard: 2025-07-01T00:00:00
                    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                    
        except ValueError as e:
            raise InvalidTimeFormatError(
                message=f"Invalid ISO 8601 time format: {time_str}",
                provided=time_str,
                expected="ISO 8601 (e.g., 2025-07-01T00:00:00Z, 2025-07-01T00:00:00+03:00)",
                details={"error": str(e)}
            )
    
    # Try legacy format (YYYYMMDD-HHmm) - for backward compatibility
    elif LEGACY_PATTERN.match(time_str):
        try:
            return datetime.strptime(time_str, "%Y%m%d-%H%M")
        except ValueError as e:
            raise InvalidTimeFormatError(
                message=f"Invalid legacy time format: {time_str}",
                provided=time_str,
                expected="YYYYMMDD-HHmm (legacy format, deprecated)",
                details={"error": str(e)}
            )
    
    # Invalid format
    else:
        raise InvalidTimeFormatError(
            message=f"Invalid time format: {time_str}",
            provided=time_str,
            expected="ISO 8601 format (e.g., 2025-07-01T00:00:00Z) or legacy format (YYYYMMDD-HHmm)",
            details={
                "supported_formats": [
                    "2025-07-01T00:00:00",
                    "2025-07-01T00:00:00Z",
                    "2025-07-01T00:00:00+03:00",
                    "2025-07-01T00:00:00.000Z",
                    "20250701-0000 (legacy, deprecated)"
                ]
            }
        )


def format_for_clickhouse(dt: datetime) -> str:
    """
    Format datetime for ClickHouse query.
    
    ClickHouse expects format: YYYY-MM-DD HH:MM:SS
    
    If datetime is timezone-aware, it will be converted to UTC first.
    
    Args:
        dt: Datetime object to format (can be timezone-aware or naive)
        
    Returns:
        Formatted string for ClickHouse
        
    Examples:
        >>> dt = datetime(2025, 7, 1, 0, 0)
        >>> format_for_clickhouse(dt)
        '2025-07-01 00:00:00'
        
        >>> from datetime import timezone
        >>> dt_utc = datetime(2025, 7, 1, 0, 0, tzinfo=timezone.utc)
        >>> format_for_clickhouse(dt_utc)
        '2025-07-01 00:00:00'
    """
    # If datetime is timezone-aware, convert to UTC
    if dt.tzinfo is not None:
        from datetime import timezone
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_time_range(
    start: datetime,
    end: Optional[datetime] = None
) -> bool:
    """
    Validate that time range is logical.
    
    Handles both timezone-aware and naive datetimes.
    If both datetimes have timezones, they are compared after converting to UTC.
    
    Args:
        start: Start datetime (can be timezone-aware or naive)
        end: End datetime (optional, can be timezone-aware or naive)
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If end is before start
        
    Examples:
        >>> start = datetime(2025, 7, 1)
        >>> end = datetime(2025, 8, 1)
        >>> validate_time_range(start, end)
        True
        
        >>> from datetime import timezone
        >>> start_utc = datetime(2025, 7, 1, 0, 0, tzinfo=timezone.utc)
        >>> end_utc = datetime(2025, 8, 1, 0, 0, tzinfo=timezone.utc)
        >>> validate_time_range(start_utc, end_utc)
        True
    """
    if end is None:
        return True
    
    # Convert both to UTC if they are timezone-aware for comparison
    compare_start = start
    compare_end = end
    
    if start.tzinfo is not None and end.tzinfo is not None:
        from datetime import timezone
        compare_start = start.astimezone(timezone.utc)
        compare_end = end.astimezone(timezone.utc)
    
    if compare_end <= compare_start:
        raise ValueError(
            f"End time ({end}) must be after start time ({start})"
        )
    
    return True


def parse_iso8601_or_legacy(time_str: str) -> datetime:
    """
    Alias for parse_time_param for backward compatibility.
    
    This function is kept for any code that might be using it directly.
    
    Args:
        time_str: Time string in ISO 8601 or legacy format
        
    Returns:
        Parsed datetime object
    """
    return parse_time_param(time_str)
