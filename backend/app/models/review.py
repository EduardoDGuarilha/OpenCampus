"""Review SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.comment import Comment
    from app.models.course import Course
    from app.models.institution import Institution
    from app.models.professor import Professor
    from app.models.subject import Subject
    from app.models.user import User


class ReviewTargetType(str, Enum):
    """Possible targets for an academic review."""

    INSTITUTION = "INSTITUTION"
    COURSE = "COURSE"
    PROFESSOR = "PROFESSOR"
    SUBJECT = "SUBJECT"


class Review(BaseModel, table=True):
    """Represents an anonymous moderated review for academic entities."""

    __tablename__ = "reviews"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    target_type: ReviewTargetType = Field(nullable=False, index=True)

    institution_id: Optional[int] = Field(
        default=None,
        foreign_key="institutions.id",
        index=True,
    )
    course_id: Optional[int] = Field(
        default=None,
        foreign_key="course.id",
        index=True,
    )
    professor_id: Optional[int] = Field(
        default=None,
        foreign_key="professors.id",
        index=True,
    )
    subject_id: Optional[int] = Field(
        default=None,
        foreign_key="subjects.id",
        index=True,
    )

    rating_1: int = Field(nullable=False, ge=1, le=5)
    rating_2: int = Field(nullable=False, ge=1, le=5)
    rating_3: int = Field(nullable=False, ge=1, le=5)
    rating_4: int = Field(nullable=False, ge=1, le=5)
    rating_5: int = Field(nullable=False, ge=1, le=5)

    text: str = Field(nullable=False)
    approved: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: "User" = Relationship(back_populates="reviews")
    institution: Optional["Institution"] = Relationship(back_populates="reviews")
    course: Optional["Course"] = Relationship(back_populates="reviews")
    professor: Optional["Professor"] = Relationship(back_populates="reviews")
    subject: Optional["Subject"] = Relationship(back_populates="reviews")
    comments: List["Comment"] = Relationship(back_populates="review")


__all__ = ["Review", "ReviewTargetType"]
