"""
app/core/config.py
==================
Central config — every module imports from here, never os.getenv directly.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/redis_demo")

# Redis
REDIS_HOST:     str       = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT:     int       = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB:       int       = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD: str|None  = os.getenv("REDIS_PASSWORD") or None
CACHE_TTL:      int       = int(os.getenv("CACHE_TTL_SECONDS", 300))

# JWT / Auth
SECRET_KEY:   str = os.getenv("SECRET_KEY", "fallback-dev-secret-do-not-use-in-production")
ALGORITHM:    str = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Server
APP_PORT: int  = int(os.getenv("APP_PORT", 8000))
DEBUG:    bool = os.getenv("DEBUG", "true").lower() == "true"
