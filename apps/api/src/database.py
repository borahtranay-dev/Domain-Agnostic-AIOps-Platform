"""Database connection and session management for API subsystem."""
from typing import Generator, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.config import settings

# SQLAlchemy Engine & Session Factory
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for ORM Models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding database sessions with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Tuple[bool, str]:
    """Verify PostgreSQL connectivity by executing a basic ping query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1;"))
            return True, "PostgreSQL connection healthy"
    except Exception as e:
        return False, f"PostgreSQL connection failed: {str(e)}"
