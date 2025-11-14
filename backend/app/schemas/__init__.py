"""Pydantic schemas package."""

from app.schemas.comment import (
    CommentBase,
    CommentCreate,
    CommentRead,
    CommentUpdate,
)
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
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from app.schemas.subject import (
    SubjectBase,
    SubjectCreate,
    SubjectRead,
    SubjectUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
)

__all__ = [
    "CommentBase",
    "CommentCreate",
    "CommentRead",
    "CommentUpdate",
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
    "ReviewBase",
    "ReviewCreate",
    "ReviewRead",
    "ReviewUpdate",
    "SubjectBase",
    "SubjectCreate",
    "SubjectRead",
    "SubjectUpdate",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
