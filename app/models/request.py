"""
Request validation models using Pydantic.

These models provide automatic validation, type checking, and
documentation for API request parameters.

Updated to support ISO 8601 format with backward compatibility.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


# ISO 8601 regex pattern for validation
ISO8601_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})?$'

# Legacy format pattern (for backward compatibility)
LEGACY_PATTERN = r'^\d{8}-\d{4}$'


class OHLCVQueryParams(BaseModel):
    """
    Query parameters for fetching OHLCV data for a single symbol.
    
    This model validates and parses request parameters for the main
    OHLCV endpoint.
    
    Time format: ISO 8601 (e.g., 2025-07-01T00:00:00Z)
    Legacy format also supported: YYYYMMDD-HHmm (deprecated)
    """
    
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Trading symbol (e.g., BINANCE:BTCUSDT.P)",
        examples=["BINANCE:BTCUSDT.P", "NASDAQ:AAPL"]
    )
    
    start: str = Field(
        ...,
        description="Start time in ISO 8601 format (e.g., 2025-07-01T00:00:00Z) or legacy format (YYYYMMDD-HHmm)",
        examples=["2025-07-01T00:00:00Z", "2025-08-01T15:30:00+00:00", "20250701-0000"]
    )
    
    end: Optional[str] = Field(
        None,
        description="End time in ISO 8601 format (optional, defaults to now). Legacy format also supported.",
        examples=["2025-08-01T23:59:59Z", "2025-08-01T23:59:59+03:00", "20250801-2359"]
    )
    
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of records to return (1-10000)"
    )
    
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip (for pagination)"
    )
    
    @field_validator('start', 'end')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate time format and ensure it's a valid datetime.
        
        Accepts both ISO 8601 format (recommended) and legacy format (deprecated).
        
        Args:
            v: Time string to validate
            
        Returns:
            Validated time string
            
        Raises:
            ValueError: If time format is invalid
        """
        if v is None:
            return v
        
        # Check if matches ISO 8601 pattern
        iso_match = re.match(ISO8601_PATTERN, v)
        
        # Check if matches legacy pattern
        legacy_match = re.match(LEGACY_PATTERN, v)
        
        if not iso_match and not legacy_match:
            raise ValueError(
                f"Invalid time format: {v}. Expected ISO 8601 format "
                f"(e.g., 2025-07-01T00:00:00Z, 2025-07-01T00:00:00+03:00) "
                f"or legacy format (YYYYMMDD-HHmm)"
            )
        
        # Try to parse to ensure it's a valid datetime
        try:
            if iso_match:
                # ISO 8601 format
                if v.endswith('Z'):
                    base_str = v[:-1]
                    if '.' in base_str:
                        datetime.strptime(base_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        datetime.strptime(base_str, "%Y-%m-%dT%H:%M:%S")
                elif '+' in v or v.count('-') > 2:
                    # With timezone offset
                    datetime.fromisoformat(v)
                else:
                    # Basic format
                    if '.' in v:
                        datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            else:
                # Legacy format
                datetime.strptime(v, "%Y%m%d-%H%M")
            
            return v
            
        except ValueError:
            raise ValueError(
                f"Invalid time value: {v}. Could not parse as datetime. "
                f"Use ISO 8601 format (e.g., 2025-07-01T00:00:00Z) "
                f"or legacy format (YYYYMMDD-HHmm)"
            )
    
    @field_validator('end')
    @classmethod
    def validate_time_range(cls, v: Optional[str], info) -> Optional[str]:
        """
        Ensure end time is not before start time.
        
        Note: Equal times are allowed (e.g., to get a specific candle)
        Handles both ISO 8601 and legacy formats.
        """
        if v and 'start' in info.data:
            start_str = info.data['start']
            
            # Parse both times
            try:
                # Detect format and parse accordingly
                if re.match(ISO8601_PATTERN, start_str):
                    # ISO 8601
                    if start_str.endswith('Z'):
                        base = start_str[:-1]
                        start_dt = datetime.strptime(base.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    elif '+' in start_str or start_str.count('-') > 2:
                        start_dt = datetime.fromisoformat(start_str).replace(tzinfo=None)
                    else:
                        start_dt = datetime.strptime(start_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                else:
                    # Legacy format
                    start_dt = datetime.strptime(start_str, "%Y%m%d-%H%M")
                
                if re.match(ISO8601_PATTERN, v):
                    # ISO 8601
                    if v.endswith('Z'):
                        base = v[:-1]
                        end_dt = datetime.strptime(base.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    elif '+' in v or v.count('-') > 2:
                        end_dt = datetime.fromisoformat(v).replace(tzinfo=None)
                    else:
                        end_dt = datetime.strptime(v.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                else:
                    # Legacy format
                    end_dt = datetime.strptime(v, "%Y%m%d-%H%M")
                
                if end_dt < start_dt:
                    raise ValueError("End time cannot be before start time")
                    
            except ValueError as e:
                if "End time cannot be before start time" in str(e):
                    raise
                # If parsing fails, let it pass - will be caught by validate_time_format
                pass
        
        return v
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "BINANCE:BTCUSDT.P",
                "start": "2025-07-01T00:00:00Z",
                "end": "2025-08-01T00:00:00Z",
                "limit": 1000,
                "offset": 0
            }
        }


class MultiSymbolQueryParams(BaseModel):
    """
    Query parameters for fetching OHLCV data for multiple symbols.
    
    Similar to OHLCVQueryParams but accepts a list of symbols.
    
    Time format: ISO 8601 (e.g., 2025-07-01T00:00:00Z)
    Legacy format also supported: YYYYMMDD-HHmm (deprecated)
    """
    
    symbols: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of trading symbols (max 100)"
    )
    
    start: str = Field(
        ...,
        description="Start time in ISO 8601 format or legacy format (YYYYMMDD-HHmm)",
        examples=["2025-07-01T00:00:00Z", "20250701-0000"]
    )
    
    end: Optional[str] = Field(
        None,
        description="End time in ISO 8601 format or legacy format (optional)",
        examples=["2025-08-01T00:00:00Z", "20250801-0000"]
    )
    
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of records per symbol"
    )
    
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip per symbol"
    )
    
    @field_validator('symbols')
    @classmethod
    def validate_symbols(cls, v: List[str]) -> List[str]:
        """
        Validate each symbol in the list.
        
        Args:
            v: List of symbols
            
        Returns:
            Validated list of symbols
            
        Raises:
            ValueError: If any symbol is invalid
        """
        for symbol in v:
            if not symbol or len(symbol) > 50:
                raise ValueError(
                    f"Invalid symbol: {symbol}. Must be 1-50 characters."
                )
        return v
    
    @field_validator('start', 'end')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate time format.
        
        Accepts both ISO 8601 format (recommended) and legacy format (deprecated).
        """
        if v is None:
            return v
        
        # Check if matches ISO 8601 pattern
        iso_match = re.match(ISO8601_PATTERN, v)
        
        # Check if matches legacy pattern
        legacy_match = re.match(LEGACY_PATTERN, v)
        
        if not iso_match and not legacy_match:
            raise ValueError(
                f"Invalid time format: {v}. Expected ISO 8601 format "
                f"(e.g., 2025-07-01T00:00:00Z) or legacy format (YYYYMMDD-HHmm)"
            )
        
        # Try to parse to ensure it's a valid datetime
        try:
            if iso_match:
                # ISO 8601 format
                if v.endswith('Z'):
                    base_str = v[:-1]
                    if '.' in base_str:
                        datetime.strptime(base_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        datetime.strptime(base_str, "%Y-%m-%dT%H:%M:%S")
                elif '+' in v or v.count('-') > 2:
                    datetime.fromisoformat(v)
                else:
                    if '.' in v:
                        datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            else:
                # Legacy format
                datetime.strptime(v, "%Y%m%d-%H%M")
            
            return v
            
        except ValueError:
            raise ValueError(
                f"Invalid time value: {v}. Use ISO 8601 format "
                f"(e.g., 2025-07-01T00:00:00Z) or legacy format (YYYYMMDD-HHmm)"
            )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "symbols": ["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"],
                "start": "2025-07-01T00:00:00Z",
                "end": "2025-08-01T00:00:00Z",
                "limit": 1000,
                "offset": 0
            }
        }


class LatestQueryParams(BaseModel):
    """
    Query parameters for fetching the latest candle for a symbol.
    
    Simple model with just the symbol parameter.
    """
    
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Trading symbol",
        examples=["BINANCE:BTCUSDT.P"]
    )
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """
        Validate symbol format.
        
        Args:
            v: Symbol string
            
        Returns:
            Validated symbol
            
        Raises:
            ValueError: If symbol is invalid
        """
        if not v or len(v) > 50:
            raise ValueError("Symbol must be 1-50 characters")
        return v
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "BINANCE:BTCUSDT.P"
            }
        }
