"""
app/cache/redis_client.py
=========================
Redis connection pool + core get/set/delete/flush helpers.
"""
from __future__ import annotations
import json, time
from typing import Any, Optional
import redis
from app.core.config import CACHE_TTL, REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

_pool = redis.ConnectionPool(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
    password=REDIS_PASSWORD, decode_responses=True,
    max_connections=50, socket_connect_timeout=2, socket_timeout=2,
)
client: redis.Redis = redis.Redis(connection_pool=_pool)
DEFAULT_TTL: int = CACHE_TTL


def _encode(value: Any) -> str:
    return json.dumps(value, default=str)

def _decode(raw: str) -> Any:
    return json.loads(raw)

def _stat_key(stat: str) -> str:
    return f"cache:stats:{stat}"

def _inc_stat(stat: str) -> None:
    try:
        client.incr(_stat_key(stat))
    except Exception:
        pass


def ping() -> bool:
    try:
        return client.ping()
    except Exception:
        return False


def get(key: str) -> Optional[Any]:
    try:
        start = time.perf_counter()
        raw   = client.get(key)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if raw is None:
            _inc_stat("misses")
            return None
        _inc_stat("hits")
        print(f"[Cache] HIT  key={key!r}  latency={elapsed_ms:.3f}ms")
        return _decode(raw)
    except Exception as exc:
        print(f"[Cache] GET error key={key!r}: {exc}")
        return None


def set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    try:
        client.setex(key, ttl, _encode(value))
        _inc_stat("sets")
        return True
    except Exception as exc:
        print(f"[Cache] SET error key={key!r}: {exc}")
        return False


def delete(key: str) -> bool:
    try:
        result = client.delete(key) > 0
        if result:
            _inc_stat("deletes")
        return result
    except Exception as exc:
        print(f"[Cache] DELETE error key={key!r}: {exc}")
        return False


def flush_pattern(pattern: str) -> int:
    try:
        keys = client.keys(pattern)
        if not keys:
            return 0
        count = client.delete(*keys)
        print(f"[Cache] Flushed {count} keys matching {pattern!r}")
        return count
    except Exception as exc:
        print(f"[Cache] FLUSH error pattern={pattern!r}: {exc}")
        return 0
