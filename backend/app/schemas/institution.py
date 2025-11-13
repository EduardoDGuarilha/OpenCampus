"""Pydantic schemas for Institution entity."""

from __future__ import annotations

from typing import Optional

from app.schemas.base import SchemaBase


class InstitutionBase(SchemaBase):
    """Shared attributes for Institution schemas."""

    name: str


class InstitutionCreate(InstitutionBase):
    """Schema for creating an institution."""


class InstitutionUpdate(SchemaBase):
    """Schema for updating an institution."""

    name: Optional[str] = None


class InstitutionRead(InstitutionBase):
    """Schema for reading institution data."""

    id: int


__all__ = [
    "InstitutionBase",
    "InstitutionCreate",
    "InstitutionUpdate",
    "InstitutionRead",
]
