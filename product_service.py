"""
app/services/product_service.py
================================
CRUD + cache-aside logic for products.
"""
from __future__ import annotations
import time
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.models import Product, CacheLog
from app.cache.strategies import CacheAside, WriteThrough
from app.cache.redis_client import flush_pattern


def _log(db: Session, endpoint: str, status: str, latency: float, user_id: int | None = None):
    db.add(CacheLog(endpoint=endpoint, cache_status=status, latency_ms=latency, user_id=user_id))
    db.commit()


def get_all_products(db: Session, user_id: int | None = None) -> dict:
    key = "products:all"
    t0  = time.perf_counter()
    def loader():
        rows = db.query(Product).all()
        return [p.to_dict() for p in rows]
    data, cache_status = CacheAside.get_or_load(key, loader)
    latency = (time.perf_counter() - t0) * 1000
    _log(db, "/products", cache_status, latency, user_id)
    return {"products": data, "cache_status": cache_status, "latency_ms": round(latency, 3)}


def get_product(product_id: int, db: Session, user_id: int | None = None) -> dict:
    key = f"product:{product_id}"
    t0  = time.perf_counter()
    def loader():
        p = db.query(Product).filter(Product.id == product_id).first()
        return p.to_dict() if p else None
    data, cache_status = CacheAside.get_or_load(key, loader)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")
    latency = (time.perf_counter() - t0) * 1000
    _log(db, f"/products/{product_id}", cache_status, latency, user_id)
    return {"product": data, "cache_status": cache_status, "latency_ms": round(latency, 3)}


def create_product(payload: dict, db: Session) -> dict:
    product = Product(**payload)
    def db_writer():
        db.add(product)
        db.commit()
        db.refresh(product)
        return product.to_dict()
    key  = f"product:{product.id}" if product.id else "product:new"
    data = WriteThrough.write(key, db_writer)
    flush_pattern("products:all")
    return {"product": data, "message": "Created and cached."}


def update_product(product_id: int, payload: dict, db: Session) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")
    for k, v in payload.items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    CacheAside.invalidate(f"product:{product_id}")
    flush_pattern("products:all")
    return {"product": product.to_dict(), "message": "Updated, cache invalidated."}


def delete_product(product_id: int, db: Session) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")
    db.delete(product)
    db.commit()
    CacheAside.invalidate(f"product:{product_id}")
    flush_pattern("products:all")
    return {"message": f"Product {product_id} deleted, cache invalidated."}
