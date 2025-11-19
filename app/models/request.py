"""
Request validation models using Pydantic.

These models provide automatic validation, type checking, and
documentation for API request parameters.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class OHLCVQueryParams(BaseModel):
    """
    Query parameters for fetching OHLCV data for a single symbol.
    
    This model validates and parses request parameters for the main
    OHLCV endpoint.
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
        pattern=r'^\d{8}-\d{4}$',
        description="Start time in format YYYYMMDD-HHmm",
        examples=["20250701-0000", "20250801-1530"]
    )
    
    end: Optional[str] = Field(
        None,
        pattern=r'^\d{8}-\d{4}$',
        description="End time in format YYYYMMDD-HHmm (optional, defaults to now)",
        examples=["20250801-2359"]
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
        
        Args:
            v: Time string to validate
            
        Returns:
            Validated time string
            
        Raises:
            ValueError: If time format is invalid
        """
        if v is None:
            return v
            
        try:
            datetime.strptime(v, "%Y%m%d-%H%M")
            return v
        except ValueError:
            raise ValueError(
                f"Invalid time format: {v}. Expected format: YYYYMMDD-HHmm (e.g., 20250701-0000)"
            )
    
    @field_validator('end')
    @classmethod
    def validate_time_range(cls, v: Optional[str], info) -> Optional[str]:
        """
        Ensure end time is not before start time.
        
        Note: Equal times are allowed (e.g., to get a specific candle)
        """
        if v and 'start' in info.data:
            start_dt = datetime.strptime(info.data['start'], "%Y%m%d-%H%M")
            end_dt = datetime.strptime(v, "%Y%m%d-%H%M")
            
            if end_dt < start_dt:  
                raise ValueError("End time cannot be before start time")
        
        return v
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "BINANCE:BTCUSDT.P",
                "start": "20250701-0000",
                "end": "20250801-0000",
                "limit": 1000,
                "offset": 0
            }
        }


class MultiSymbolQueryParams(BaseModel):
    """
    Query parameters for fetching OHLCV data for multiple symbols.
    
    Similar to OHLCVQueryParams but accepts a list of symbols.
    """
    
    symbols: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of trading symbols (max 100)"
    )
    
    start: str = Field(
        ...,
        pattern=r'^\d{8}-\d{4}$',
        description="Start time in format YYYYMMDD-HHmm"
    )
    
    end: Optional[str] = Field(
        None,
        pattern=r'^\d{8}-\d{4}$',
        description="End time in format YYYYMMDD-HHmm (optional)"
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
        """Validate time format."""
        if v is None:
            return v
            
        try:
            datetime.strptime(v, "%Y%m%d-%H%M")
            return v
        except ValueError:
            raise ValueError(
                f"Invalid time format: {v}. Expected: YYYYMMDD-HHmm"
            )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "symbols": ["BINANCE:BTCUSDT.P", "BINANCE:ETHUSDT.P"],
                "start": "20250701-0000",
                "end": "20250801-0000",
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
