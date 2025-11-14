"""Institution SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.course import Course
    from app.models.review import Review


class Institution(BaseModel, table=True):
    """Represents an academic institution available in the platform."""

    __tablename__ = "institutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    courses: List["Course"] = Relationship(back_populates="institution")
    reviews: List["Review"] = Relationship(back_populates="institution")


__all__ = ["Institution"]

