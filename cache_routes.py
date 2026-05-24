"""
app/routes/cache_routes.py
==========================
GET    /cache/stats        — hit/miss counters
DELETE /cache/flush        — clear all cache
GET    /cache/logs         — audit log from DB
POST   /cache/set          — playground: set a key (JSON body)
GET    /cache/get/{key}    — playground: get a key
DELETE /cache/del/{key}    — playground: delete a key
GET    /cache/ttl/{key}    — playground: get TTL of a key
POST   /cache/expire       — playground: set expiry on a key
GET    /cache/keys         — playground: list keys by pattern
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.cache.redis_client import (
    get, set, delete, flush_pattern, DEFAULT_TTL, client
)
from app.cache.stats import get_stats, reset_stats
from app.database.connection import get_db
from app.database.models import CacheLog, User
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/cache", tags=["Cache"])


# ── Pydantic bodies ───────────────────────────────────────────

class CacheSetBody(BaseModel):
    key:   str
    value: str
    ttl:   int = 0          # 0 = no expiry


class ExpireBody(BaseModel):
    key: str
    ttl: int


# ── Routes ───────────────────────────────────────────────────

@router.post("/set")
def cache_set(
    body: CacheSetBody,
    current_user: User = Depends(get_current_user),
):
    """SET key = value  (with optional TTL in seconds, 0 = forever)."""
    if body.ttl and body.ttl > 0:
        ok = set(body.key, body.value, body.ttl)
    else:
        # no expiry — store without TTL
        try:
            client.set(body.key, body.value)
            ok = True
        except Exception as exc:
            print(f"[Cache] SET error key={body.key!r}: {exc}")
            ok = False
    return {"key": body.key, "stored": ok, "ttl": body.ttl}


@router.get("/get/{key}")
def cache_get(
    key: str,
    current_user: User = Depends(get_current_user),
):
    """GET value for a key."""
    try:
        raw = client.get(key)
        return {"key": key, "value": raw, "found": raw is not None}
    except Exception as exc:
        return {"key": key, "value": None, "found": False, "error": str(exc)}


@router.delete("/del/{key}")
def cache_del(
    key: str,
    current_user: User = Depends(get_current_user),
):
    """DELETE a key."""
    deleted = delete(key)
    return {"key": key, "deleted": deleted}


@router.get("/ttl/{key}")
def cache_ttl(
    key: str,
    current_user: User = Depends(get_current_user),
):
    """TTL — returns seconds remaining, -1 if no expiry, -2 if key missing."""
    try:
        ttl = client.ttl(key)
        return {"key": key, "ttl": ttl}
    except Exception as exc:
        return {"key": key, "ttl": -2, "error": str(exc)}


@router.post("/expire")
def cache_expire(
    body: ExpireBody,
    current_user: User = Depends(get_current_user),
):
    """EXPIRE — set a TTL on an existing key."""
    try:
        result = client.expire(body.key, body.ttl)
        return {"key": body.key, "ttl": body.ttl, "result": int(result)}
    except Exception as exc:
        return {"key": body.key, "result": 0, "error": str(exc)}


@router.get("/keys")
def cache_keys(
    pattern: str = Query("*", description="Glob pattern, e.g. user:* or *"),
    current_user: User = Depends(get_current_user),
):
    """KEYS — list all keys matching a glob pattern."""
    try:
        keys = client.keys(pattern)
        return {"pattern": pattern, "keys": keys, "count": len(keys)}
    except Exception as exc:
        return {"pattern": pattern, "keys": [], "count": 0, "error": str(exc)}


@router.get("/stats")
def cache_stats(current_user: User = Depends(get_current_user)):
    """Hit/miss counters and memory info."""
    return get_stats()


@router.delete("/flush")
def flush_cache(
    pattern: str = Query("*", description="Key pattern to flush, e.g. 'product:*'"),
    current_user: User = Depends(get_current_user),
):
    """FLUSHDB — delete all keys matching pattern and reset stats."""
    count = flush_pattern(pattern)
    reset_stats()
    return {"flushed_keys": count, "pattern": pattern, "message": f"Flushed {count} keys. Stats reset."}


@router.get("/logs")
def cache_logs(
    limit: int = Query(50, ge=1, le=500),
    db:    Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recent cache audit log from the database."""
    logs = (
        db.query(CacheLog)
        .order_by(CacheLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    # dashboard expects a plain list, not {"logs": [...]}
    return [
        {
            "id":           l.id,
            "endpoint":     l.endpoint,
            "cache_status": l.cache_status,
            "latency_ms":   l.latency_ms,
            "timestamp":    l.timestamp.isoformat(),
        }
        for l in logs
    ]
