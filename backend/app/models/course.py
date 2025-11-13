"""Course SQLModel definition."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from .institution import Institution
    from .professor import Professor
    from .subject import Subject
    from .user import User
    from .review import Review
    from .change_request import ChangeRequest


class Course(BaseModel, table=True):
    """Academic course offered by an institution."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    institution_id: int = Field(foreign_key="institution.id")

    institution: "Institution" = Relationship(back_populates="courses")
    professors: List["Professor"] = Relationship(back_populates="course")
    subjects: List["Subject"] = Relationship(back_populates="course")
    students: List["User"] = Relationship(back_populates="course")
    reviews: List["Review"] = Relationship(back_populates="course")
    change_requests: List["ChangeRequest"] = Relationship(
        back_populates="course", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )

    __table_args__ = (  # type: ignore[assignment]
        {"sqlite_autoincrement": True},
    )
