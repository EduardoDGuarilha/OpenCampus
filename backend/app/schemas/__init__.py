"""Pydantic schemas package with lazy imports to avoid side effects."""

from importlib import import_module
from typing import Any, Dict

_MODULE_MAP: Dict[str, str] = {
    "LoginRequest": "auth",
    "TokenResponse": "auth",
    "ChangeRequestBase": "change_request",
    "ChangeRequestCreate": "change_request",
    "ChangeRequestRead": "change_request",
    "ChangeRequestUpdate": "change_request",
    "CommentBase": "comment",
    "CommentCreate": "comment",
    "CommentRead": "comment",
    "CommentUpdate": "comment",
    "CourseBase": "course",
    "CourseCreate": "course",
    "CourseRead": "course",
    "CourseUpdate": "course",
    "InstitutionBase": "institution",
    "InstitutionCreate": "institution",
    "InstitutionRead": "institution",
    "InstitutionUpdate": "institution",
    "ProfessorBase": "professor",
    "ProfessorCreate": "professor",
    "ProfessorRead": "professor",
    "ProfessorUpdate": "professor",
    "ReviewBase": "review",
    "ReviewCreate": "review",
    "ReviewRead": "review",
    "ReviewUpdate": "review",
    "SubjectBase": "subject",
    "SubjectCreate": "subject",
    "SubjectRead": "subject",
    "SubjectUpdate": "subject",
    "UserBase": "user",
    "UserCreate": "user",
    "UserRead": "user",
    "UserUpdate": "user",
}

__all__ = sorted(_MODULE_MAP)


def __getattr__(name: str) -> Any:
    """Dynamically import schema symbols on demand."""

    module_name = _MODULE_MAP.get(name)
    if module_name is None:
        raise AttributeError(f"module 'app.schemas' has no attribute {name!r}")
    module = import_module(f"app.schemas.{module_name}")
    return getattr(module, name)
