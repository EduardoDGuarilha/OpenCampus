"""Institution SQLModel definition."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field

from .base import BaseModel


class Institution(BaseModel, table=True):
    """Represents an academic institution available in the platform."""

    __tablename__ = "institutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    courses: Mapped[list["Course"]] = relationship(back_populates="institution")
    reviews: Mapped[list["Review"]] = relationship(back_populates="institution")


__all__ = ["Institution"]

