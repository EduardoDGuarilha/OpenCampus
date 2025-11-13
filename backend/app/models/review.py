"""Review SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    Text,
    UniqueConstraint,
)
from sqlmodel import Field, Relationship

from .base import BaseModel
from .enums import ReviewTargetType

if TYPE_CHECKING:  # pragma: no cover - typing only imports
    from .user import User
    from .institution import Institution
    from .course import Course
    from .professor import Professor
    from .subject import Subject
    from .comment import Comment


class Review(BaseModel, table=True):
    """Anonymous review emitted by students pending moderation."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    target_type: ReviewTargetType = Field(
        sa_column=Column(SAEnum(ReviewTargetType, name="review_target_type"), nullable=False)
    )
    institution_id: Optional[int] = Field(default=None, foreign_key="institution.id")
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    professor_id: Optional[int] = Field(default=None, foreign_key="professor.id")
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")

    # Institution specific scores
    governance_score: Optional[int] = Field(default=None, ge=1, le=5)
    infrastructure_score: Optional[int] = Field(default=None, ge=1, le=5)
    support_score: Optional[int] = Field(default=None, ge=1, le=5)

    # Course specific scores
    curriculum_score: Optional[int] = Field(default=None, ge=1, le=5)
    workload_score: Optional[int] = Field(default=None, ge=1, le=5)
    employability_score: Optional[int] = Field(default=None, ge=1, le=5)

    # Professor specific scores
    didactics_score: Optional[int] = Field(default=None, ge=1, le=5)
    availability_score: Optional[int] = Field(default=None, ge=1, le=5)
    fairness_score: Optional[int] = Field(default=None, ge=1, le=5)

    # Subject specific scores
    content_relevance_score: Optional[int] = Field(default=None, ge=1, le=5)
    assessment_fairness_score: Optional[int] = Field(default=None, ge=1, le=5)
    workload_balance_score: Optional[int] = Field(default=None, ge=1, le=5)

    text: str = Field(sa_column=Column(Text, nullable=False))
    approved: bool = Field(sa_column=Column(Boolean, nullable=False, default=False), default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )

    author: "User" = Relationship(back_populates="reviews")
    institution: Optional["Institution"] = Relationship(back_populates="reviews")
    course: Optional["Course"] = Relationship(back_populates="reviews")
    professor: Optional["Professor"] = Relationship(back_populates="reviews")
    subject: Optional["Subject"] = Relationship(back_populates="reviews")
    comments: List["Comment"] = Relationship(back_populates="review")

    __table_args__ = (
        UniqueConstraint("user_id", "institution_id", name="uq_review_user_institution"),
        UniqueConstraint("user_id", "course_id", name="uq_review_user_course"),
        UniqueConstraint("user_id", "professor_id", name="uq_review_user_professor"),
        UniqueConstraint("user_id", "subject_id", name="uq_review_user_subject"),
        CheckConstraint(
            (
                "(" "target_type = 'INSTITUTION' AND institution_id IS NOT NULL "
                "AND course_id IS NULL AND professor_id IS NULL AND subject_id IS NULL"
                ") OR ("
                "target_type = 'COURSE' AND course_id IS NOT NULL AND institution_id IS NULL "
                "AND professor_id IS NULL AND subject_id IS NULL"
                ") OR ("
                "target_type = 'PROFESSOR' AND professor_id IS NOT NULL AND institution_id IS NULL "
                "AND course_id IS NULL AND subject_id IS NULL"
                ") OR ("
                "target_type = 'SUBJECT' AND subject_id IS NOT NULL AND institution_id IS NULL "
                "AND course_id IS NULL AND professor_id IS NULL"
                ")"
            ),
            name="ck_review_target_reference",
        ),
        {"sqlite_autoincrement": True},
    )
