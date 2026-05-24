"""
app/routes/product_routes.py
=============================
GET    /products         — list all (cached)
GET    /products/{id}    — single product (cached)
POST   /products         — create (write-through)
PUT    /products/{id}    — update + invalidate cache
DELETE /products/{id}    — delete + invalidate cache
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.auth.dependencies import get_current_user
from app.services.product_service import (
    get_all_products, get_product, create_product, update_product, delete_product
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_products(db, user_id=current_user.id)


@router.get("/{product_id}")
def single_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_product(product_id, db, user_id=current_user.id)


@router.post("", status_code=201)
def add_product(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_product(payload, db)


@router.put("/{product_id}")
def edit_product(
    product_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_product(product_id, payload, db)


@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_product(product_id, db)
