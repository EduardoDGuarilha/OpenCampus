"""Institution SQLModel definition."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from .course import Course
    from .review import Review


class Institution(BaseModel, table=True):
    """Represents an academic institution available in the platform."""

    __tablename__ = "institutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, sa_column_kwargs={"unique": True})

    courses: List["Course"] = Relationship(back_populates="institution")
    reviews: List["Review"] = Relationship(back_populates="institution")


__all__ = ["Institution"]

