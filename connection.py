"""
app/database/connection.py
==========================
SQLAlchemy engine, session factory, get_db() FastAPI dependency.
"""
from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — yields a DB session, always closes on exit."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
