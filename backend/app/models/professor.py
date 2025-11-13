"""Professor SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String, UniqueConstraint
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from .course import Course
    from .review import Review
    from .change_request import ChangeRequest


class Professor(BaseModel, table=True):
    """Represents a professor associated with a course."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    course_id: int = Field(foreign_key="course.id")

    course: "Course" = Relationship(back_populates="professors")
    reviews: List["Review"] = Relationship(back_populates="professor")
    change_requests: List["ChangeRequest"] = Relationship(
        back_populates="professor", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )

    __table_args__ = (
        UniqueConstraint("course_id", "name", name="uq_professor_course_name"),
        {"sqlite_autoincrement": True},
    )
