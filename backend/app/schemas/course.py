"""Pydantic schemas for Course entity."""

from __future__ import annotations

from typing import Optional

from app.schemas.base import SchemaBase


class CourseBase(SchemaBase):
    """Shared attributes for Course schemas."""

    name: str


class CourseCreate(CourseBase):
    """Schema for creating a course."""

    institution_id: int


class CourseUpdate(SchemaBase):
    """Schema for updating a course."""

    name: Optional[str] = None
    institution_id: Optional[int] = None


class CourseRead(CourseBase):
    """Schema for reading course data."""

    id: int
    institution_id: int


__all__ = [
    "CourseBase",
    "CourseCreate",
    "CourseUpdate",
    "CourseRead",
]
