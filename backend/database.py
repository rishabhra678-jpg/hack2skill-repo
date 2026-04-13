"""
NutriMind – Database Setup
SQLite database with SQLAlchemy ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_PATH = os.environ.get("DATABASE_PATH", "./nutrimind.db")
# Read from DATABASE_URL if available (e.g. for Cloud SQL), else fallback to SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

# The check_same_thread param should only be applied when using SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)
