"""
app/routes/benchmark_routes.py
===============================
GET /benchmark/product/{id}  — Redis vs DB latency for one product
GET /benchmark/summary       — aggregate stats from cache_logs table
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.auth.dependencies import get_current_user
from app.services.benchmark_service import benchmark_product, benchmark_summary

router = APIRouter(prefix="/benchmark", tags=["Benchmark"])


@router.get("/product/{product_id}")
def bench_product(
    product_id: int,
    iterations: int = Query(50, ge=10, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return benchmark_product(product_id, db, iterations)


@router.get("/summary")
def bench_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return benchmark_summary(db)
