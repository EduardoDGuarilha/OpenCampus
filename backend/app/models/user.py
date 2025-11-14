"""User SQLModel definitions."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field

from .base import BaseModel


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
    course_id: Optional[int] = Field(
        default=None,
        foreign_key="courses.id",
    )
    role: UserRole = Field(nullable=False)
    validated: bool = Field(default=False, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")


__all__ = ["User", "UserRole"]
