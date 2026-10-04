"""
Database connection pool and query execution utilities for PostgreSQL.
Uses direct psycopg2 with ThreadedConnectionPool and RealDictCursor. NO ORM.
"""
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple, Union

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[pool.ThreadedConnectionPool] = None


def init_db_pool(
    database_url: str,
    minconn: int = 1,
    maxconn: int = 20
) -> pool.ThreadedConnectionPool:
    """Initialize the global PostgreSQL connection pool."""
    global _pool
    if _pool is None or _pool.closed:
        logger.info("Initializing PostgreSQL connection pool (min=%d, max=%d)...", minconn, maxconn)
        _pool = pool.ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=database_url,
            cursor_factory=RealDictCursor
        )
    return _pool


def close_db_pool() -> None:
    """Close all connections in the pool."""
    global _pool
    if _pool and not _pool.closed:
        logger.info("Closing PostgreSQL connection pool...")
        _pool.closeall()
        _pool = None


def get_db_pool() -> pool.ThreadedConnectionPool:
    """Get the active database pool or raise RuntimeError."""
    global _pool
    if _pool is None or _pool.closed:
        raise RuntimeError("Database connection pool is not initialized. Call init_db_pool() first.")
    return _pool


@contextmanager
def get_db_connection():
    """
    Context manager yielding a pooled database connection.
    Automatically commits on normal exit and rolls back on exception.
    """
    p = get_db_pool()
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


@contextmanager
def get_db_cursor(commit: bool = True):
    """
    Context manager yielding a cursor with RealDictCursor.
    Handles commit/rollback automatically.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            yield cursor
        if commit:
            conn.commit()


def execute_query(query: str, params: Optional[Union[Tuple, Dict, List]] = None, commit: bool = True) -> int:
    """Execute an INSERT/UPDATE/DELETE query and return affected row count."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            rowcount = cursor.rowcount
        if commit:
            conn.commit()
        return rowcount


def fetch_one(query: str, params: Optional[Union[Tuple, Dict, List]] = None) -> Optional[Dict[str, Any]]:
    """Execute a SELECT query and return one row as a dictionary, or None."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None


def fetch_all(query: str, params: Optional[Union[Tuple, Dict, List]] = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return all matching rows as a list of dicts."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(r) for r in rows] if rows else []


def check_db_health() -> bool:
    """Verify database connection health by executing SELECT 1."""
    try:
        result = fetch_one("SELECT 1 AS healthy;")
        return bool(result and result.get("healthy") == 1)
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return False
