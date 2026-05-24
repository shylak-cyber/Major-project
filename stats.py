"""
app/cache/stats.py
==================
Cache hit/miss statistics stored in Redis itself.
"""
from __future__ import annotations
from app.cache.redis_client import client, _stat_key


def get_stats() -> dict:
    try:
        hits    = int(client.get(_stat_key("hits"))    or 0)
        misses  = int(client.get(_stat_key("misses"))  or 0)
        sets    = int(client.get(_stat_key("sets"))    or 0)
        deletes = int(client.get(_stat_key("deletes")) or 0)
        total   = hits + misses
        hit_rate = round((hits / total) * 100, 2) if total > 0 else 0.0
        info = client.info("memory")
        return {
            "hits": hits, "misses": misses, "sets": sets, "deletes": deletes,
            "total_requests": total, "hit_rate_pct": hit_rate,
            "redis_memory": info.get("used_memory_human", "N/A"),
        }
    except Exception as exc:
        return {"error": str(exc)}


def reset_stats() -> None:
    for stat in ("hits", "misses", "sets", "deletes"):
        try:
            client.delete(_stat_key(stat))
        except Exception:
            pass
