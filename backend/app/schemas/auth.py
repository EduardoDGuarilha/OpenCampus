"""Schemas dedicated to authentication workflows."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Credentials required for token generation."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """OAuth2 compatible token response."""

    access_token: str
    token_type: str = "bearer"


__all__ = ["LoginRequest", "TokenResponse"]

