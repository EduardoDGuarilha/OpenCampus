"""User SQLModel definitions."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from .base import BaseModel


if TYPE_CHECKING:  # pragma: no cover
    from app.models.comment import Comment
    from app.models.review import Review


class UserRole(str, Enum):
    """Available roles for authenticated platform participants."""

    STUDENT = "STUDENT"
    PROFESSOR = "PROFESSOR"
    INSTITUTION = "INSTITUTION"
    MODERATOR = "MODERATOR"


class User(BaseModel, table=True):
    """Persistence model representing platform accounts."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    cpf: str = Field(sa_column=Column("cpf", String, unique=True, nullable=False))
    email: str = Field(sa_column=Column("email", String, unique=True, nullable=False))
    password_hash: str = Field(nullable=False)
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    role: UserRole = Field(nullable=False)
    validated: bool = Field(default=False, nullable=False)

    reviews: List["Review"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")


__all__ = ["User", "UserRole"]
