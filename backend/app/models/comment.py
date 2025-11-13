"""Comment SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Text
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover - typing imports only
    from .user import User
    from .review import Review


class Comment(BaseModel, table=True):
    """Represents a comment on an approved review."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    review_id: int = Field(foreign_key="review.id", index=True)
    text: str = Field(sa_column=Column(Text, nullable=False))
    is_official: bool = Field(sa_column=Column(Boolean, nullable=False, default=False), default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )

    author: "User" = Relationship(back_populates="comments")
    review: "Review" = Relationship(back_populates="comments")

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
