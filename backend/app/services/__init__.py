"""Domain service layer package with lazy imports."""

from importlib import import_module
from typing import Any, Dict

_MODULE_MAP: Dict[str, str] = {
    "ChangeRequestService": "change_request",
    "CommentService": "comment",
    "ProfessorService": "professor",
    "ReviewService": "review",
    "SubjectService": "subject",
    "UserService": "user",
    "create_course": "course",
    "delete_course": "course",
    "get_course": "course",
    "list_courses": "course",
    "update_course": "course",
    "create_institution": "institution",
    "delete_institution": "institution",
    "get_institution": "institution",
    "list_institutions": "institution",
    "update_institution": "institution",
}

__all__ = sorted(_MODULE_MAP)


def __getattr__(name: str) -> Any:
    """Import service symbols on demand."""

    module_name = _MODULE_MAP.get(name)
    if module_name is None:
        raise AttributeError(f"module 'app.services' has no attribute {name!r}")
    module = import_module(f"app.services.{module_name}")
    return getattr(module, name)
