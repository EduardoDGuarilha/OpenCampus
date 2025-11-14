"""Professor SQLModel definition."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field

from .base import BaseModel


class Professor(BaseModel, table=True):
    """Represents a professor associated with a course."""

    __tablename__ = "professors"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    course_id: int = Field(
        foreign_key="courses.id",
        nullable=False,
        index=True,
    )

    course: Mapped["Course"] = relationship(back_populates="professors")
    reviews: Mapped[list["Review"]] = relationship(back_populates="professor")


__all__ = ["Professor"]
