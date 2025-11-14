"""Pydantic schemas for Subject entity."""

from __future__ import annotations

from typing import Optional

from app.schemas.base import SchemaBase


class SubjectBase(SchemaBase):
    """Shared attributes across Subject schemas."""

    name: str


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""

    course_id: int


class SubjectUpdate(SchemaBase):
    """Schema for updating subject attributes."""

    name: Optional[str] = None
    course_id: Optional[int] = None


class SubjectRead(SubjectBase):
    """Schema for reading subject data."""

    id: int
    course_id: int


__all__ = [
    "SubjectBase",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectRead",
]
