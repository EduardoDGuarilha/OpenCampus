"""Comment SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from .review import Review
    from .user import User


class Comment(BaseModel, table=True):
    """Represents a moderated comment associated with a review."""

    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    review_id: int = Field(foreign_key="reviews.id", nullable=False, index=True)
    text: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_official: bool = Field(default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="comments")
    review: Mapped["Review"] = relationship(back_populates="comments")


__all__ = ["Comment"]
