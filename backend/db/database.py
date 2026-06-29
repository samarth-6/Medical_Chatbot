import os
import psycopg
from psycopg_pool import ConnectionPool
_pool: ConnectionPool | None = None

def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
            open=True,
        )
    return _pool


def get_connection():
    """Legacy helper — borrows a connection from the pool.
    Caller must call .close() to return it to the pool."""
    return get_pool().getconn()
