"""
Database connection module for the Security Monitoring & Privacy System.

Reads connection details from environment variables (see .env.example)
so credentials never get committed to GitHub.
"""

import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()  # loads variables from a local .env file, if present

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "privacy_db"),
}

# Connection pool so the API doesn't open a brand new connection per request.
_pool = pooling.MySQLConnectionPool(
    pool_name="privacy_db_pool",
    pool_size=5,
    **DB_CONFIG,
)


@contextmanager
def get_connection():
    """Borrow a connection from the pool and always return it, even on error."""
    conn = _pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def test_connection() -> bool:
    """Quick sanity check: can we actually reach the DB and see our tables?"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        print("Connected. Tables found:", tables)
        # MySQL table names can come back in whatever case they were created
        # with, so compare case-insensitively instead of assuming lowercase.
        lowered = {t.lower() for t in tables}
        return "synthetic_data" in lowered or "protected_data" in lowered


if __name__ == "__main__":
    ok = test_connection()
    print("Connection OK" if ok else "Connected, but expected tables were not found.")
