"""Comment SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModel
from app.models.user import User

if TYPE_CHECKING:  # pragma: no cover
    from app.models.review import Review


class Comment(BaseModel, table=True):
    """Represents a moderated comment associated with a review."""

    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    review_id: int = Field(foreign_key="reviews.id", nullable=False, index=True)
    text: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_official: bool = Field(default=False, nullable=False)

    user: User = Relationship(back_populates="comments")
    review: "Review" = Relationship(back_populates="comments")


__all__ = ["Comment"]
