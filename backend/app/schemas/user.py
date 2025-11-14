"""User Pydantic schemas ensuring LGPD compliance."""

from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from app.models.user import UserRole
from app.schemas.base import SchemaBase


class UserBase(SchemaBase):
    """Shared attributes for user operations."""

    course_id: Optional[int] = None
    role: UserRole
    validated: bool = False


class UserCreate(UserBase):
    """Schema for creating a user account."""

    cpf: str
    email: EmailStr
    password: str


class UserUpdate(SchemaBase):
    """Schema for updating user attributes."""

    cpf: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    course_id: Optional[int] = None
    role: Optional[UserRole] = None
    validated: Optional[bool] = None


class UserRead(UserBase):
    """Schema for returning non-sensitive user data."""

    id: int


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
]
