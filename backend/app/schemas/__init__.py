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
from app.schemas.professor import (
    ProfessorBase,
    ProfessorCreate,
    ProfessorRead,
    ProfessorUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
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
    "ProfessorBase",
    "ProfessorCreate",
    "ProfessorRead",
    "ProfessorUpdate",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
