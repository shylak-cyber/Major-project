"""
app/main.py
===========
Application entry point.
- Loads .env
- Checks Redis + PostgreSQL on startup
- Registers all routers
- Starts Uvicorn

Run:  python app/main.py
Docs: http://localhost:8000/docs
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_PORT, DEBUG
from app.cache.redis_client import ping as redis_ping
from app.database.connection import SessionLocal
from app.database.seed import create_tables, seed_demo_data

# ── Routers ───────────────────────────────────────────────────
from app.routes.auth_routes      import router as auth_router
from app.routes.product_routes   import router as product_router
from app.routes.cache_routes     import router as cache_router
from app.routes.benchmark_routes import router as benchmark_router

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="Redis Caching — Major Project",
    description="High-Performance API Caching System using Redis and FastAPI",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cache_router)
app.include_router(benchmark_router)


# ── Startup / Shutdown ────────────────────────────────────────
def startup_checks() -> None:
    print("\n" + "─" * 60)
    print("  Redis Caching Major Project — Startup")
    print("─" * 60)

    redis_ok = redis_ping()
    print(f"  Redis      : {'✓  connected' if redis_ok else '✗  UNREACHABLE'}")
    if not redis_ok:
        print("  [WARN] Start Redis: redis-server  OR  docker run -p 6379:6379 redis:alpine")

    try:
        create_tables()
        print("  PostgreSQL : ✓  tables ready")
        db = SessionLocal()
        seed_demo_data(db)
        db.close()
        print("  Seed data  : ✓  demo products ready")
    except Exception as exc:
        print(f"  PostgreSQL : ✗  ERROR — {exc}")
        print("  Set DATABASE_URL in your .env file.")

    print("─" * 60)
    print("  Swagger UI : http://localhost:8000/docs")
    print("  ReDoc      : http://localhost:8000/redoc")
    print("─" * 60 + "\n")


@app.on_event("startup")
async def on_startup():
    startup_checks()


@app.on_event("shutdown")
async def on_shutdown():
    print("\n[Main] Server shutting down. Goodbye!")


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "message": "Redis Caching Major Project is running 🚀"}
@app.get("/health", tags=["Health"])
def health_check():
    from app.cache.redis_client import ping as redis_ping
    return {"status": "ok", "redis": redis_ping()}

# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=APP_PORT, reload=DEBUG, log_level="info")
