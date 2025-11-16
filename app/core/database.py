"""
ClickHouse database connection management.

This module provides a singleton manager for ClickHouse connections,
handling connection pooling, query execution, and error handling.
"""

import clickhouse_connect
from clickhouse_connect.driver.client import Client
from typing import Optional, Any, Dict, List
import time

from app.config import settings
from app.core.exceptions import (
    ConnectionError,
    QueryError,
    TimeoutError as DBTimeoutError,
)


class ClickHouseManager:
    """
    Singleton manager for ClickHouse database connections.
    
    This class handles:
    - Connection lifecycle management
    - Query execution with error handling
    - Connection health checks
    - Graceful shutdown
    
    Usage:
        db = ClickHouseManager()
        result = db.execute_query(query, parameters)
    """
    
    _instance: Optional['ClickHouseManager'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern - ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the manager (only once due to singleton)."""
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._client = None
    
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
            
        except Exception as e:
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
        Execute a parameterized query safely.
        
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
            
        Example:
            query = "SELECT * FROM table WHERE id = {id:UInt32}"
            result = db.execute_query(query, {"id": 123})
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
            
            execution_time = time.time() - start_time
            
            # Log slow queries (will be implemented in Phase 2)
            if execution_time > 1.0:  # queries slower than 1 second
                # TODO: Add structured logging in Phase 2
                pass
            
            return result
            
        except clickhouse_connect.driver.exceptions.ClickHouseError as e:
            error_msg = str(e)
            
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
                    "execution_time": time.time() - start_time
                }
            )
            
        except Exception as e:
            # Unexpected error
            raise QueryError(
                message=f"Unexpected error during query execution: {str(e)}",
                query=query,
                details={
                    "error_type": type(e).__name__,
                    "execution_time": time.time() - start_time
                }
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
            raise QueryError(
                message=f"Command execution failed: {str(e)}",
                query=command
            )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check database connection health.
        
        Returns:
            Dictionary with health status and response time
            
        Example:
            {
                "status": "up",
                "response_time_ms": 12.5,
                "database": "default"
            }
        """
        try:
            start_time = time.time()
            self._client.command("SELECT 1")
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "status": "up",
                "response_time_ms": round(response_time, 2),
                "database": settings.CLICKHOUSE_DATABASE
            }
            
        except Exception as e:
            return {
                "status": "down",
                "error": str(e),
                "database": settings.CLICKHOUSE_DATABASE
            }
    
    def close(self) -> None:
        """
        Close database connection gracefully.
        
        This should be called during application shutdown.
        """
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                # Ignore errors during shutdown
                pass
            finally:
                self._client = None
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()
