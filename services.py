"""
app/auth/services.py
====================
register_user() and login_user() business logic.
"""
from __future__ import annotations
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, UserOut, Token
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.models import User


def register_user(payload: UserCreate, db: Session) -> UserOut:
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = User(
        username        = payload.username,
        email           = payload.email,
        hashed_password = hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[Auth] New user registered: {user.username!r} (id={user.id})")
    return UserOut.model_validate(user)


def login_user(payload: UserLogin, db: Session) -> Token:
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": user.username, "uid": user.id})
    print(f"[Auth] Login successful: {user.username!r}")
    return Token(access_token=token)
