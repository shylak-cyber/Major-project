"""
app/services/benchmark_service.py
==================================
Redis vs PostgreSQL latency measurement logic.
"""
from __future__ import annotations
import statistics, time
from sqlalchemy.orm import Session
from app.database.models import Product, CacheLog
from app.cache.redis_client import get, set, DEFAULT_TTL


def benchmark_product(product_id: int, db: Session, iterations: int = 50) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": f"Product {product_id} not found."}

    # DB timings
    db_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        db.query(Product).filter(Product.id == product_id).first()
        db.expire_all()
        db_times.append((time.perf_counter() - t0) * 1000)

    # Cache timings (warm)
    cache_key = f"product:{product_id}"
    set(cache_key, product.to_dict(), DEFAULT_TTL)
    cache_times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        get(cache_key)
        cache_times.append((time.perf_counter() - t0) * 1000)

    avg_db    = statistics.mean(db_times)
    avg_cache = statistics.mean(cache_times)
    speedup   = round(avg_db / avg_cache, 1) if avg_cache > 0 else 0

    return {
        "product_id":       product_id,
        "iterations":       iterations,
        "db_avg_ms":        round(avg_db, 4),
        "db_min_ms":        round(min(db_times), 4),
        "db_max_ms":        round(max(db_times), 4),
        "cache_avg_ms":     round(avg_cache, 4),
        "cache_min_ms":     round(min(cache_times), 4),
        "cache_max_ms":     round(max(cache_times), 4),
        "speedup_factor":   f"{speedup}x",
        "winner":           "Redis" if avg_cache < avg_db else "PostgreSQL",
    }


def benchmark_summary(db: Session) -> dict:
    total_logs  = db.query(CacheLog).count()
    hits        = db.query(CacheLog).filter(CacheLog.cache_status == "HIT").count()
    misses      = db.query(CacheLog).filter(CacheLog.cache_status == "MISS").count()
    hit_logs    = db.query(CacheLog).filter(CacheLog.cache_status == "HIT").all()
    miss_logs   = db.query(CacheLog).filter(CacheLog.cache_status == "MISS").all()
    avg_hit_ms  = round(statistics.mean([l.latency_ms for l in hit_logs]),  4) if hit_logs  else 0
    avg_miss_ms = round(statistics.mean([l.latency_ms for l in miss_logs]), 4) if miss_logs else 0
    return {
        "total_requests": total_logs,
        "cache_hits":     hits,
        "cache_misses":   misses,
        "hit_rate_pct":   round((hits / total_logs) * 100, 2) if total_logs else 0,
        "avg_hit_latency_ms":  avg_hit_ms,
        "avg_miss_latency_ms": avg_miss_ms,
        "speedup_estimate":    f"{round(avg_miss_ms / avg_hit_ms, 1)}x" if avg_hit_ms > 0 else "N/A",
    }
