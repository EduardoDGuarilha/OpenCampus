"""Course SQLModel definitions."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field

from .base import BaseModel


class Course(BaseModel, table=True):
    """Persistence model for academic courses."""

    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    institution_id: int = Field(
        foreign_key="institutions.id",
        nullable=False,
        index=True,
    )

    institution: Mapped["Institution"] = relationship(back_populates="courses")
    professors: Mapped[list["Professor"]] = relationship(back_populates="course")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="course")
    reviews: Mapped[list["Review"]] = relationship(back_populates="course")


__all__ = ["Course"]
