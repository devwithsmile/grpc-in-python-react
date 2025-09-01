"""
Simple database setup for Library Service.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..models.base import Base

# Simple database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://library_user:library_password@localhost:5432/librarydb")

# Create engine with explicit psycopg driver
engine = create_engine(DATABASE_URL, echo=False, connect_args={})

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(engine)

def get_session() -> Session:
    """Get a database session."""
    return SessionLocal()

def close_session(session: Session):
    """Close a database session."""
    session.close() 