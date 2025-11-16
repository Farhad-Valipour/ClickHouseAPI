"""
OHLCV data endpoints.

These endpoints provide access to OHLCV (Open, High, Low, Close, Volume)
candlestick data stored in ClickHouse.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import time

from app.config import settings
from app.core.database import ClickHouseManager
from app.core.exceptions import (
    DataNotFoundError,
    DatabaseException,
)
from app.models.request import (
    OHLCVQueryParams,
    LatestQueryParams,
)
from app.models.response import (
    OHLCVData,
    OHLCVResponse,
    ResponseMetadata,
)
from app.utils.time_parser import parse_time_param

router = APIRouter(prefix="/ohlcv", tags=["OHLCV"])


@router.get(
    "/",
    response_model=OHLCVResponse,
    summary="Get OHLCV data",
    description="Retrieve OHLCV candlestick data for a symbol within a time range"
)
async def get_ohlcv(
    symbol: str,
    start: str,
    end: str = None,
    limit: int = 1000,
    offset: int = 0
):
    """
    Get OHLCV data for a symbol in a specified time range.
    
    This endpoint retrieves candlestick data with pagination support.
    All queries are parameterized to prevent SQL injection.
    
    Args:
        symbol: Trading symbol (e.g., BINANCE:BTCUSDT.P)
        start: Start time in format YYYYMMDD-HHmm
        end: End time in format YYYYMMDD-HHmm (optional, defaults to now)
        limit: Maximum number of records (1-10000, default: 1000)
        offset: Number of records to skip for pagination (default: 0)
        
    Returns:
        OHLCVResponse containing data array and metadata
        
    Raises:
        HTTPException: If validation fails or database error occurs
        
    Example:
        GET /api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000
    """
    # Validate parameters using Pydantic
    try:
        params = OHLCVQueryParams(
            symbol=symbol,
            start=start,
            end=end,
            limit=min(limit, settings.MAX_LIMIT),
            offset=offset
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    # Parse times
    start_dt = parse_time_param(params.start)
    end_dt = parse_time_param(params.end) if params.end else datetime.utcnow()
    
    # Build safe parameterized query
    query = """
        SELECT 
            candle_time,
            symbol,
            open,
            high,
            low,
            close,
            volume
        FROM {table:Identifier}
        WHERE symbol = {symbol:String}
          AND candle_time >= {start:DateTime64(3)}
          AND candle_time <= {end:DateTime64(3)}
        ORDER BY candle_time ASC
        LIMIT {limit:UInt32}
        OFFSET {offset:UInt32}
    """
    
    # Get database connection
    db = ClickHouseManager()
    
    # Execute query with timing
    start_time = time.time()
    
    try:
        result = db.execute_query(
            query,
            parameters={
                'table': settings.CLICKHOUSE_TABLE,
                'symbol': params.symbol,
                'start': start_dt,
                'end': end_dt,
                'limit': params.limit,
                'offset': params.offset
            }
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    
    query_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Transform results to OHLCVData models
    data = [
        OHLCVData(
            candle_time=row[0],
            symbol=row[1],
            open=float(row[2]),
            high=float(row[3]),
            low=float(row[4]),
            close=float(row[5]),
            volume=float(row[6])
        )
        for row in result.result_rows
    ]
    
    # Build response with metadata
    return OHLCVResponse(
        success=True,
        data=data,
        metadata=ResponseMetadata(
            total_records=len(data),
            limit=params.limit,
            offset=params.offset,
            has_more=len(data) == params.limit,
            query_time_ms=round(query_time, 2),
            timestamp=datetime.utcnow()
        )
    )


@router.get(
    "/latest",
    response_model=OHLCVData,
    summary="Get latest candle",
    description="Retrieve the most recent OHLCV candle for a symbol"
)
async def get_latest(symbol: str):
    """
    Get the latest OHLCV candle for a symbol.
    
    This endpoint retrieves only the most recent candlestick data point.
    
    Args:
        symbol: Trading symbol (e.g., BINANCE:BTCUSDT.P)
        
    Returns:
        Single OHLCVData object
        
    Raises:
        HTTPException: If symbol not found or database error occurs
        
    Example:
        GET /api/v1/ohlcv/latest?symbol=BINANCE:BTCUSDT.P
    """
    # Validate parameters
    try:
        params = LatestQueryParams(symbol=symbol)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    # Build safe parameterized query
    query = """
        SELECT 
            candle_time,
            symbol,
            open,
            high,
            low,
            close,
            volume
        FROM {table:Identifier}
        WHERE symbol = {symbol:String}
        ORDER BY candle_time DESC
        LIMIT 1
    """
    
    # Get database connection
    db = ClickHouseManager()
    
    try:
        result = db.execute_query(
            query,
            parameters={
                'table': settings.CLICKHOUSE_TABLE,
                'symbol': params.symbol
            }
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    
    # Check if data found
    if not result.result_rows:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "DATA_NOT_FOUND",
                "message": f"No data found for symbol: {params.symbol}",
                "details": {"symbol": params.symbol}
            }
        )
    
    # Return single data point
    row = result.result_rows[0]
    return OHLCVData(
        candle_time=row[0],
        symbol=row[1],
        open=float(row[2]),
        high=float(row[3]),
        low=float(row[4]),
        close=float(row[5]),
        volume=float(row[6])
    )
