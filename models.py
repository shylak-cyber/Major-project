"""
app/database/models.py
======================
SQLAlchemy ORM models: User, Product, CacheLog
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(64),  unique=True, nullable=False, index=True)
    email           = Column(String(128), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    last_login      = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    price       = Column(Float, nullable=False)
    stock       = Column(Integer, default=0)
    category    = Column(String(64), index=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "description": self.description, "price": self.price,
            "stock": self.stock, "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Product id={self.id} name={self.name!r} price={self.price}>"


class CacheLog(Base):
    __tablename__ = "cache_logs"
    id           = Column(Integer, primary_key=True, index=True)
    endpoint     = Column(String(256), nullable=False)
    cache_status = Column(String(8),   nullable=False)   # "HIT" | "MISS"
    latency_ms   = Column(Float,       nullable=False)
    user_id      = Column(Integer,     nullable=True)
    timestamp    = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<CacheLog id={self.id} status={self.cache_status!r} latency={self.latency_ms:.3f}ms>"
