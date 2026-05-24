"""
app/auth/password.py
====================
bcrypt password hashing and verification.
"""
from __future__ import annotations
from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)


def _truncate(password: str) -> str:
    """bcrypt hard limit is 72 bytes."""
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")


def hash_password(plain: str) -> str:
    password_bytes = plain.encode("utf-8")[:72]   # truncate manually
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
