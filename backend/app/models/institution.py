"""Institution SQLModel definitions."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.course import Course


class Institution(SQLModel, table=True):
    """Persistence model for academic institutions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    courses: List["Course"] = Relationship(back_populates="institution")


__all__ = ["Institution"]
