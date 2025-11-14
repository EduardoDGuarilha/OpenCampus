"""Professor SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.course import Course
    from app.models.review import Review


class Professor(BaseModel, table=True):
    """Represents a professor associated with a course."""

    __tablename__ = "professors"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    course_id: int = Field(foreign_key="course.id", nullable=False, index=True)

    course: "Course" = Relationship(back_populates="professors")
    reviews: List["Review"] = Relationship(back_populates="professor")


__all__ = ["Professor"]
