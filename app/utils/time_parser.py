"""
Time parsing and formatting utilities.

This module provides functions for parsing time parameters from
requests and formatting them for ClickHouse queries.
"""

from datetime import datetime
from typing import Optional

from app.core.exceptions import InvalidTimeFormatError


def parse_time_param(time_str: str) -> datetime:
    """
    Parse time parameter from request format to datetime.
    
    Expected format: YYYYMMDD-HHmm (e.g., 20250701-0000)
    
    Args:
        time_str: Time string in format YYYYMMDD-HHmm
        
    Returns:
        Parsed datetime object
        
    Raises:
        InvalidTimeFormatError: If time format is invalid
        
    Example:
        >>> parse_time_param("20250701-0000")
        datetime(2025, 7, 1, 0, 0)
    """
    try:
        return datetime.strptime(time_str, "%Y%m%d-%H%M")
    except ValueError as e:
        raise InvalidTimeFormatError(
            message=f"Invalid time format: {time_str}",
            provided=time_str,
            expected="YYYYMMDD-HHmm",
            details={"error": str(e)}
        )


def format_for_clickhouse(dt: datetime) -> str:
    """
    Format datetime for ClickHouse query.
    
    ClickHouse expects format: YYYY-MM-DD HH:MM:SS
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Formatted string for ClickHouse
        
    Example:
        >>> dt = datetime(2025, 7, 1, 0, 0)
        >>> format_for_clickhouse(dt)
        '2025-07-01 00:00:00'
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_time_range(
    start: datetime,
    end: Optional[datetime] = None
) -> bool:
    """
    Validate that time range is logical.
    
    Args:
        start: Start datetime
        end: End datetime (optional)
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If end is before start
        
    Example:
        >>> start = datetime(2025, 7, 1)
        >>> end = datetime(2025, 8, 1)
        >>> validate_time_range(start, end)
        True
    """
    if end is None:
        return True
    
    if end <= start:
        raise ValueError(
            f"End time ({end}) must be after start time ({start})"
        )
    
    return True
