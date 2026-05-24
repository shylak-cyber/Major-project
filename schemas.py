"""
app/auth/schemas.py
===================
Pydantic models for auth request/response validation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.core.config import TOKEN_EXPIRE


class UserCreate(BaseModel):
    username: str
    email:    EmailStr
    password: str
    model_config = {"json_schema_extra": {"example": {
        "username": "rahul_dev", "email": "rahul@example.com", "password": "StrongPass@123"
    }}}


class UserLogin(BaseModel):
    username: str
    password: str
    model_config = {"json_schema_extra": {"example": {
        "username": "rahul_dev", "password": "StrongPass@123"
    }}}


class UserOut(BaseModel):
    id:         int
    username:   str
    email:      str
    is_active:  bool
    created_at: datetime
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int = TOKEN_EXPIRE * 60


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id:  Optional[int] = None
