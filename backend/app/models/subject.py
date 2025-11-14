"""Subject SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.course import Course
    from app.models.review import Review


class Subject(BaseModel, table=True):
    """Represents an academic subject tied to a course."""

    __tablename__ = "subjects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    course_id: int = Field(
        foreign_key="courses.id",
        nullable=False,
        index=True,
    )

    course: "Course" = Relationship(back_populates="subjects")
    reviews: List["Review"] = Relationship(back_populates="subject")


__all__ = ["Subject"]
