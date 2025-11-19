"""
OHLCV data endpoints with async support.

These async endpoints provide better performance under high load
by not blocking the event loop during database operations.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import time

from app.config import settings
from app.core.database import ClickHouseManager
from app.core.exceptions import DatabaseException
from app.models.request import OHLCVQueryParams, LatestQueryParams
from app.models.response import OHLCVData, OHLCVResponse, ResponseMetadata, LatestOHLCVResponse, LatestResponseMetadata
from app.utils.time_parser import parse_time_param
from app.core.logging_config import logger

router = APIRouter(prefix="/ohlcv", tags=["OHLCV"])


@router.get(
    "/",
    response_model=OHLCVResponse,
    summary="Get OHLCV data",
    description="Retrieve OHLCV candlestick data for a symbol within a time range (async)"
)
async def get_ohlcv(
    symbol: str,
    start: str,
    end: str = None,
    limit: int = 1000,
    offset: int = 0
):
    """
    Get OHLCV data for a symbol in a specified time range (async).
    
    This async endpoint provides better performance under high load.
    
    Args:
        symbol: Trading symbol (e.g., BINANCE:BTCUSDT.P)
        start: Start time in format YYYYMMDD-HHmm
        end: End time in format YYYYMMDD-HHmm (optional, defaults to now)
        limit: Maximum number of records (1-10000, default: 1000)
        offset: Number of records to skip for pagination (default: 0)
        
    Returns:
        OHLCVResponse containing data array and metadata
    """
    # Validate parameters
    try:
        params = OHLCVQueryParams(
            symbol=symbol,
            start=start,
            end=end,
            limit=min(limit, settings.MAX_LIMIT),
            offset=offset
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
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
    
    # Execute query with timing (async)
    start_time = time.time()
    
    try:
        result = await db.execute_query_async(
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
        logger.error(f"Database error: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    
    query_time = (time.time() - start_time) * 1000
    
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
    
    logger.info(
        f"Retrieved {len(data)} records for {params.symbol} in {query_time:.2f}ms"
    )
    
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
    response_model=LatestOHLCVResponse,
    summary="Get latest candle",
    description="Retrieve the most recent OHLCV candle for a symbol (async)"
)
async def get_latest(symbol: str):
    """
    Get the latest OHLCV candle for a symbol (async).
    
    Returns data in consistent format with main endpoint, preparing for
    future "latest N candles" feature.
    
    Args:
        symbol: Trading symbol (e.g., BINANCE:BTCUSDT.P)
        
    Returns:
        LatestOHLCVResponse with data array containing single element and metadata
    """
    # Validate parameters
    try:
        params = LatestQueryParams(symbol=symbol)
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
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

    # Execute query with timing
    start_time = time.time()
    
    try:
        result = await db.execute_query_async(
            query,
            parameters={
                'table': settings.CLICKHOUSE_TABLE,
                'symbol': params.symbol
            }
        )
    except DatabaseException as e:
        logger.error(f"Database error: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    query_time = (time.time() - start_time) * 1000
    
    # Check if data found
    if not result.result_rows:
        logger.warning(f"No data found for symbol: {params.symbol}")
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "DATA_NOT_FOUND",
                "message": f"No data found for symbol: {params.symbol}",
                "details": {"symbol": params.symbol}
            }
        )
    
    
    # Transform result to OHLCVData model (as array with single element)
    row = result.result_rows[0]

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
    ]



    logger.info(f"Retrieved latest candle for {params.symbol} in {query_time:.2f}ms")
    

    # Build response with metadata (consistent with main endpoint)

    return LatestOHLCVResponse(
        success=True,
        data=data,
        metadata=LatestResponseMetadata(
            total_records=1,
            limit=1,
            offset=0,
            has_more=False,  # For single latest candle, no more data available
            query_time_ms=round(query_time, 2),
            timestamp=datetime.utcnow()
        )
    )