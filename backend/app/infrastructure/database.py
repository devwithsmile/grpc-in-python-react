"""
Database setup and session management for Library Service.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from ..models.base import Base
from ..utils.logger import LoggerConfig, log_exception

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://library_user:library_password@localhost:5432/librarydb")

# Create engine with connection pooling and error handling
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={},
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Global logger for database operations
db_logger = LoggerConfig.get_logger("database")


class DatabaseError(Exception):
    """Custom database error with context."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None, operation: str = None):
        self.message = message
        self.original_error = original_error
        self.operation = operation
        super().__init__(self.message)


def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(engine)
        db_logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        log_exception(db_logger, "Failed to create database tables", e)
        raise DatabaseError("Failed to create database tables", e, "create_tables")


def get_session() -> Session:
    """Get a database session."""
    try:
        session = SessionLocal()
        db_logger.debug("Database session created")
        return session
    except SQLAlchemyError as e:
        log_exception(db_logger, "Failed to create database session", e)
        raise DatabaseError("Failed to create database session", e, "get_session")


def close_session(session: Session):
    """Close a database session."""
    try:
        session.close()
        db_logger.debug("Database session closed")
    except SQLAlchemyError as e:
        log_exception(db_logger, "Failed to close database session", e)
        # Don't raise here as we're in cleanup


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic cleanup and error handling.
    
    Usage:
        with get_db_session() as session:
            # Use session here
            pass
        # Session is automatically closed
    """
    session = None
    try:
        session = get_session()
        yield session
        session.commit()
        db_logger.debug("Database transaction committed")
    except IntegrityError as e:
        if session:
            session.rollback()
        log_exception(db_logger, "Database integrity error", e)
        raise DatabaseError("Database integrity constraint violation", e, "database_operation")
    except OperationalError as e:
        if session:
            session.rollback()
        log_exception(db_logger, "Database operational error", e)
        raise DatabaseError("Database connection or operation failed", e, "database_operation")
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        log_exception(db_logger, "Database error", e)
        raise DatabaseError("Database operation failed", e, "database_operation")
    except Exception as e:
        if session:
            session.rollback()
        log_exception(db_logger, "Unexpected database error", e)
        raise DatabaseError("Unexpected database error", e, "database_operation")
    finally:
        if session:
            close_session(session)


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_logger.info("Database connection test successful")
        return True
    except SQLAlchemyError as e:
        log_exception(db_logger, "Database connection test failed", e)
        return False


def get_connection_info() -> dict:
    """
    Get database connection information (without sensitive data).
    
    Returns:
        Dictionary with connection information
    """
    return {
        "database_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "unknown",
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "invalid": engine.pool.invalid()
    } 