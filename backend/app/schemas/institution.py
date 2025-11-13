"""Institution Pydantic schemas."""

from __future__ import annotations

from typing import Optional

from .base import SchemaBase


class InstitutionBase(SchemaBase):
    """Shared Institution schema attributes."""

    name: str


class InstitutionCreate(InstitutionBase):
    """Schema for creating a new institution."""


class InstitutionUpdate(SchemaBase):
    """Schema for updating an institution."""

    name: Optional[str] = None


class InstitutionRead(InstitutionBase):
    """Schema for reading institution data."""

    id: int


__all__ = [
    "InstitutionCreate",
    "InstitutionUpdate",
    "InstitutionRead",
]
