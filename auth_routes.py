"""
app/routes/auth_routes.py
=========================
POST /auth/register  — create account
POST /auth/login     — get JWT token
GET  /auth/me        — current user profile
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, UserOut, Token
from app.auth.services import register_user, login_user
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return register_user(payload, db)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    return login_user(payload, db)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
