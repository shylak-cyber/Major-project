"""
app/cache/strategies.py
=======================
Three caching strategies: CacheAside, WriteThrough, WriteBack.
"""
from __future__ import annotations
from typing import Any, Callable
from app.cache.redis_client import get, set, delete, client, DEFAULT_TTL


class CacheAside:
    """Lazy loading — read from cache, fallback to DB on miss."""

    @staticmethod
    def get_or_load(key: str, loader: Callable[[], Any], ttl: int = DEFAULT_TTL):
        cached = get(key)
        if cached is not None:
            return cached, "HIT"
        print(f"[Cache-Aside] MISS key={key!r} → loading from DB …")
        value = loader()
        if value is not None:
            set(key, value, ttl)
        return value, "MISS"

    @staticmethod
    def invalidate(key: str) -> None:
        delete(key)
        print(f"[Cache-Aside] Invalidated key={key!r}")


class WriteThrough:
    """Every write goes to DB and cache simultaneously."""

    @staticmethod
    def write(key: str, db_writer: Callable[[], Any], ttl: int = DEFAULT_TTL) -> Any:
        value = db_writer()
        if value is not None:
            set(key, value, ttl)
            print(f"[Write-Through] Wrote to DB + cache, key={key!r}")
        return value


class WriteBack:
    """Writes go to cache first; DB is updated lazily on flush."""

    DIRTY_SET = "cache:dirty"

    @staticmethod
    def write(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
        set(key, value, ttl)
        client.sadd(WriteBack.DIRTY_SET, key)
        print(f"[Write-Back] Buffered key={key!r} (dirty, not yet in DB)")

    @staticmethod
    def flush_dirty(flusher: Callable[[str, Any], None]) -> int:
        keys = client.smembers(WriteBack.DIRTY_SET)
        if not keys:
            return 0
        flushed = 0
        for key in keys:
            value = get(key)
            if value is not None:
                flusher(key, value)
                client.srem(WriteBack.DIRTY_SET, key)
                flushed += 1
        print(f"[Write-Back] Flushed {flushed} dirty keys to DB")
        return flushed
