"""
ClickHouse database connection management with async support.

This module provides a singleton manager for ClickHouse connections,
handling connection pooling, async query execution, and error handling.
"""

import clickhouse_connect
from clickhouse_connect.driver.client import Client
from typing import Optional, Any, Dict
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config import settings
from app.core.exceptions import (
    ConnectionError,
    QueryError,
    TimeoutError as DBTimeoutError,
)
from app.core.logging_config import logger, log_database_query


class ClickHouseManager:
    """
    Singleton manager for ClickHouse database connections with async support.
    
    This class handles:
    - Connection lifecycle management
    - Async query execution with thread pool
    - Connection health checks
    - Graceful shutdown
    
    Usage:
        db = ClickHouseManager()
        result = await db.execute_query_async(query, parameters)
    """
    
    _instance: Optional['ClickHouseManager'] = None
    _client: Optional[Client] = None
    _executor: Optional[ThreadPoolExecutor] = None
    
    def __new__(cls):
        """Singleton pattern - ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the manager (only once due to singleton)."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._client = None
            self._executor = ThreadPoolExecutor(max_workers=settings.POOL_SIZE)
    
    def connect(self) -> None:
        """
        Establish connection to ClickHouse.
        
        Raises:
            ConnectionError: If unable to connect to database
        """
        if self._client is not None:
            return  # Already connected
            
        try:
            self._client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_PORT,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
                database=settings.CLICKHOUSE_DATABASE,
                connect_timeout=settings.POOL_TIMEOUT,
                send_receive_timeout=settings.QUERY_TIMEOUT,
            )
            
            # Test connection
            self._client.command("SELECT 1")
            logger.info(
                f"Connected to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}"
            )
            
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {str(e)}")
            raise ConnectionError(
                message=f"Failed to connect to ClickHouse: {str(e)}",
                details={
                    "host": settings.CLICKHOUSE_HOST,
                    "port": settings.CLICKHOUSE_PORT,
                    "database": settings.CLICKHOUSE_DATABASE,
                }
            )
    
    def get_client(self) -> Client:
        """
        Get the ClickHouse client, connecting if necessary.
        
        Returns:
            ClickHouse client instance
            
        Raises:
            ConnectionError: If unable to get or create connection
        """
        if self._client is None:
            self.connect()
        return self._client
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Execute a parameterized query safely (synchronous).
        
        Args:
            query: SQL query with placeholders (e.g., {param:Type})
            parameters: Dictionary of parameter values
            timeout: Query timeout in seconds (overrides default)
            
        Returns:
            Query result object
            
        Raises:
            QueryError: If query execution fails
            DBTimeoutError: If query times out
            ConnectionError: If connection is lost
        """
        client = self.get_client()
        parameters = parameters or {}
        timeout = timeout or settings.QUERY_TIMEOUT
        
        start_time = time.time()
        
        try:
            result = client.query(
                query,
                parameters=parameters,
                query_formats={'default': 'Native'}
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log query execution
            log_database_query(
                query_type="SELECT",
                duration_ms=round(execution_time, 2),
                records_returned=len(result.result_rows)
            )
            
            return result
            
        except clickhouse_connect.driver.exceptions.ClickHouseError as e:
            error_msg = str(e)
            execution_time = (time.time() - start_time) * 1000
            
            # Log failed query
            log_database_query(
                query_type="SELECT",
                duration_ms=round(execution_time, 2),
                error=error_msg
            )
            
            # Check for timeout
            if "timeout" in error_msg.lower():
                raise DBTimeoutError(
                    message="Query execution timed out",
                    timeout=timeout,
                    details={"error": error_msg}
                )
            
            # General query error
            raise QueryError(
                message=f"Query execution failed: {error_msg}",
                query=query,
                details={
                    "parameters": str(parameters),
                    "execution_time": execution_time
                }
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            log_database_query(
                query_type="SELECT",
                duration_ms=round(execution_time, 2),
                error=str(e)
            )
            
            raise QueryError(
                message=f"Unexpected error during query execution: {str(e)}",
                query=query,
                details={
                    "error_type": type(e).__name__,
                    "execution_time": execution_time
                }
            )
    
    async def execute_query_async(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Execute a parameterized query safely (asynchronous).
        
        This method runs the synchronous query in a thread pool to avoid
        blocking the event loop.
        
        Args:
            query: SQL query with placeholders
            parameters: Dictionary of parameter values
            timeout: Query timeout in seconds
            
        Returns:
            Query result object
            
        Raises:
            QueryError: If query execution fails
            DBTimeoutError: If query times out
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.execute_query,
            query,
            parameters,
            timeout
        )
    
    def execute_command(
        self,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a command that doesn't return data (DDL, etc.).
        
        Args:
            command: SQL command
            parameters: Dictionary of parameter values
            
        Returns:
            Command result as string
            
        Raises:
            QueryError: If command execution fails
        """
        client = self.get_client()
        parameters = parameters or {}
        
        try:
            return client.command(command, parameters=parameters)
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            raise QueryError(
                message=f"Command execution failed: {str(e)}",
                query=command
            )
    
    async def execute_command_async(
        self,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute command asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.execute_command,
            command,
            parameters
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check database connection health.
        
        Returns:
            Dictionary with health status and response time
        """
        try:
            start_time = time.time()
            self._client.command("SELECT 1")
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "up",
                "response_time_ms": round(response_time, 2),
                "database": settings.CLICKHOUSE_DATABASE
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "down",
                "error": str(e),
                "database": settings.CLICKHOUSE_DATABASE
            }
    
    async def health_check_async(self) -> Dict[str, Any]:
        """Check database health asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.health_check
        )
    
    def close(self) -> None:
        """
        Close database connection and thread pool gracefully.
        """
        if self._client is not None:
            try:
                self._client.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {str(e)}")
            finally:
                self._client = None
        
        if self._executor is not None:
            try:
                self._executor.shutdown(wait=True)
                logger.info("Thread pool executor closed")
            except Exception as e:
                logger.warning(f"Error closing executor: {str(e)}")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()
