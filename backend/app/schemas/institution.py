"""Pydantic schemas for Institution use cases."""

from __future__ import annotations

from typing import Optional

from pydantic import constr

from .base import SchemaBase


NameStr = constr(strip_whitespace=True, min_length=1, max_length=255)


class InstitutionBase(SchemaBase):
    """Shared attributes for Institution schemas."""

    name: NameStr


class InstitutionCreate(InstitutionBase):
    """Schema for creating an Institution."""


class InstitutionUpdate(SchemaBase):
    """Schema for updating an Institution."""

    name: Optional[NameStr] = None


class InstitutionRead(InstitutionBase):
    """Schema for reading Institution data."""

    id: int
