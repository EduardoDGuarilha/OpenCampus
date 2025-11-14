"""Pydantic schemas for Comment entity with anonymous authorship."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.schemas.base import SchemaBase


class CommentBase(SchemaBase):
    """Shared attributes across comment schemas."""

    text: str


class CommentCreate(CommentBase):
    """Schema for creating comments without exposing user identity."""

    review_id: int


class CommentUpdate(SchemaBase):
    """Schema for updating comment content."""

    text: Optional[str] = None


class CommentRead(CommentBase):
    """Schema for reading comments while keeping authors anonymous."""

    id: int
    review_id: int
    created_at: datetime
    is_official: bool


__all__ = [
    "CommentBase",
    "CommentCreate",
    "CommentUpdate",
    "CommentRead",
]
