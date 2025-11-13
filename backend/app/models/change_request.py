"""ChangeRequest SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Enum as SAEnum, JSON
from sqlmodel import Field, Relationship

from .base import BaseModel
from .enums import ChangeRequestStatus, ReviewTargetType

if TYPE_CHECKING:  # pragma: no cover - typing only imports
    from .user import User
    from .institution import Institution
    from .course import Course
    from .professor import Professor
    from .subject import Subject


class ChangeRequest(BaseModel, table=True):
    """Represents suggested adjustments awaiting moderation."""

    id: Optional[int] = Field(default=None, primary_key=True)
    target_type: ReviewTargetType = Field(
        sa_column=Column(SAEnum(ReviewTargetType, name="change_request_target"), nullable=False)
    )
    suggested_data: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    status: ChangeRequestStatus = Field(
        default=ChangeRequestStatus.PENDING,
        sa_column=Column(SAEnum(ChangeRequestStatus, name="change_request_status"), nullable=False),
    )
    created_by: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    resolved_by: Optional[int] = Field(default=None, foreign_key="user.id")
    resolved_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    from_official_source: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False), default=False
    )

    institution_id: Optional[int] = Field(default=None, foreign_key="institution.id")
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    professor_id: Optional[int] = Field(default=None, foreign_key="professor.id")
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")

    creator: "User" = Relationship(
        back_populates="created_change_requests",
        sa_relationship_kwargs={"foreign_keys": "ChangeRequest.created_by"},
    )
    resolver: Optional["User"] = Relationship(
        back_populates="resolved_change_requests",
        sa_relationship_kwargs={"foreign_keys": "ChangeRequest.resolved_by"},
    )
    institution: Optional["Institution"] = Relationship(back_populates="change_requests")
    course: Optional["Course"] = Relationship(back_populates="change_requests")
    professor: Optional["Professor"] = Relationship(back_populates="change_requests")
    subject: Optional["Subject"] = Relationship(back_populates="change_requests")

    __table_args__ = (
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
            name="ck_change_request_target_reference",
        ),
        {"sqlite_autoincrement": True},
    )
