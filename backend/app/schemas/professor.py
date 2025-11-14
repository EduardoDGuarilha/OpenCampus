"""Pydantic schemas for Professor entity."""

from __future__ import annotations

from typing import Optional

from app.schemas.base import SchemaBase


class ProfessorBase(SchemaBase):
    """Shared attributes across Professor schemas."""

    name: str


class ProfessorCreate(ProfessorBase):
    """Schema for creating a professor."""

    course_id: int


class ProfessorUpdate(SchemaBase):
    """Schema for updating professor attributes."""

    name: Optional[str] = None
    course_id: Optional[int] = None


class ProfessorRead(ProfessorBase):
    """Schema for reading professor data."""

    id: int
    course_id: int


__all__ = [
    "ProfessorBase",
    "ProfessorCreate",
    "ProfessorUpdate",
    "ProfessorRead",
]
