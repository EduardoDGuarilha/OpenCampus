"""Security helpers for password hashing and JWT handling."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a secure hash for the provided password."""

    return _pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a password against its stored hash."""

    return _pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Generate a JWT access token for the given subject."""

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode a JWT access token returning its payload."""

    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
]

