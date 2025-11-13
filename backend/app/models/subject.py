"""Subject SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from .course import Course
    from .review import Review
    from .change_request import ChangeRequest


class Subject(BaseModel, table=True):
    """Academic subject belonging to a course."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    course_id: int = Field(foreign_key="course.id")

    course: "Course" = Relationship(back_populates="subjects")
    reviews: List["Review"] = Relationship(back_populates="subject")
    change_requests: List["ChangeRequest"] = Relationship(
        back_populates="subject", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )
