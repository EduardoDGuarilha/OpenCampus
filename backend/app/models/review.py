"""Review SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from .course import Course
    from .institution import Institution
    from .professor import Professor
    from .subject import Subject
    from .user import User


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
        foreign_key="courses.id",
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
    rejected: bool = Field(default=False, nullable=False, index=True)
    resolved_by: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )
    resolved_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="reviews")
    institution: Mapped[Optional["Institution"]] = relationship(back_populates="reviews")
    course: Mapped[Optional["Course"]] = relationship(back_populates="reviews")
    professor: Mapped[Optional["Professor"]] = relationship(back_populates="reviews")
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="reviews")
    comments: Mapped[list["Comment"]] = relationship(back_populates="review")


__all__ = ["Review", "ReviewTargetType"]
