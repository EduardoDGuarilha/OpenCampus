"""Institution SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from .course import Course
    from .review import Review
    from .change_request import ChangeRequest


class Institution(BaseModel, table=True):
    """Represents an academic institution within the platform."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))

    courses: List["Course"] = Relationship(back_populates="institution")
    reviews: List["Review"] = Relationship(back_populates="institution")
    change_requests: List["ChangeRequest"] = Relationship(
        back_populates="institution", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )
