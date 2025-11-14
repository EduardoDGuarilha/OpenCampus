"""Course SQLModel definitions."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.professor import Professor
    from app.models.review import Review
    from app.models.subject import Subject


class Course(SQLModel, table=True):
    """Persistence model for academic courses."""

    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    institution_id: int = Field(
        foreign_key="institutions.id",
        nullable=False,
        index=True,
    )

    institution: "Institution" = Relationship(back_populates="courses")
    professors: List["Professor"] = Relationship(back_populates="course")
    subjects: List["Subject"] = Relationship(back_populates="course")
    reviews: List["Review"] = Relationship(back_populates="course")


__all__ = ["Course"]
