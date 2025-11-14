"""Pydantic schemas package."""

from app.schemas.course import (
    CourseBase,
    CourseCreate,
    CourseRead,
    CourseUpdate,
)
from app.schemas.institution import (
    InstitutionBase,
    InstitutionCreate,
    InstitutionRead,
    InstitutionUpdate,
)

__all__ = [
    "CourseBase",
    "CourseCreate",
    "CourseRead",
    "CourseUpdate",
    "InstitutionBase",
    "InstitutionCreate",
    "InstitutionRead",
    "InstitutionUpdate",
]
