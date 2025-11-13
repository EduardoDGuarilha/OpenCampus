"""Institution SQLModel definitions."""

from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class Institution(SQLModel, table=True):
    """Persistence model for academic institutions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)


__all__ = ["Institution"]
