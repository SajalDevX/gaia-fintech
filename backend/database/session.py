"""
Database Session Management for GAIA
Handles database connections, sessions, and initialization.
"""

from contextlib import contextmanager
from typing import Generator
import structlog

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from config import get_settings
from .models import Base

logger = structlog.get_logger()
settings = get_settings()

# Create engine based on database URL
# For SQLite, we need special handling for threading
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Call this at application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("database_initialized", url=settings.DATABASE_URL)
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.
    Use with FastAPI's Depends().

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Use when not in a FastAPI route.

    Usage:
        with get_db_context() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def drop_all_tables() -> None:
    """
    Drop all tables. Use with caution - only for testing/development.
    """
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop tables in production!")
    Base.metadata.drop_all(bind=engine)
    logger.warning("database_tables_dropped")


def get_table_stats() -> dict:
    """Get statistics about database tables."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    stats = {"tables": {}}
    with get_db_context() as db:
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                stats["tables"][table] = {"row_count": count}
            except Exception:
                stats["tables"][table] = {"row_count": "error"}

    return stats
