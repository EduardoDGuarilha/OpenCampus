"""User SQLModel definition."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, String
from sqlmodel import Field, Relationship

from .base import BaseModel
from .enums import UserRole

if TYPE_CHECKING:  # pragma: no cover - typing only imports
    from .course import Course
    from .review import Review
    from .comment import Comment
    from .change_request import ChangeRequest


class User(BaseModel, table=True):
    """Represents a platform user with role-based permissions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    cpf: str = Field(sa_column=Column(String(11), unique=True, nullable=False))
    email: str = Field(sa_column=Column(String(320), unique=True, index=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    role: UserRole = Field(sa_column=Column(SAEnum(UserRole, name="user_role"), nullable=False))
    validated: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )

    course: Optional["Course"] = Relationship(back_populates="students")
    reviews: List["Review"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    created_change_requests: List["ChangeRequest"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "ChangeRequest.created_by"},
    )
    resolved_change_requests: List["ChangeRequest"] = Relationship(
        back_populates="resolver",
        sa_relationship_kwargs={"foreign_keys": "ChangeRequest.resolved_by"},
    )

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
