"""Database connection verification helper for API foundation."""
import psycopg2
from typing import Tuple
from src.config import settings


def check_database_connection() -> Tuple[bool, str]:
    """Verify PostgreSQL connectivity by executing a basic ping query."""
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            connect_timeout=3,
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            if result and result[0] == 1:
                conn.close()
                return True, "PostgreSQL connection healthy"
        conn.close()
        return False, "Unexpected query result"
    except Exception as e:
        return False, f"PostgreSQL connection failed: {str(e)}"
