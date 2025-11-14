"""API router for subject entity operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database.session import get_session
from app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate
from app.services.subject import SubjectService
from app.routes.course import require_moderator

router = APIRouter(prefix="/subjects", tags=["subjects"])


def get_subject_service(session: Session = Depends(get_session)) -> SubjectService:
    """Dependency provider for :class:`SubjectService`."""

    return SubjectService(session)


@router.get("", response_model=list[SubjectRead], summary="List subjects")
def list_subjects(
    skip: int = 0,
    limit: int = 100,
    course_id: int | None = None,
    service: SubjectService = Depends(get_subject_service),
) -> list[SubjectRead]:
    """Retrieve a paginated collection of subjects."""

    return list(service.list_subjects(course_id=course_id, skip=skip, limit=limit))


@router.get(
    "/{subject_id}",
    response_model=SubjectRead,
    summary="Get subject by ID",
)
def get_subject(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
) -> SubjectRead:
    """Fetch a single subject by identifier."""

    subject = service.get_subject(subject_id)
    return SubjectRead.model_validate(subject)


@router.post(
    "",
    response_model=SubjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create subject",
)
def create_subject(
    payload: SubjectCreate,
    service: SubjectService = Depends(get_subject_service),
    _moderator: object = Depends(require_moderator),
) -> SubjectRead:
    """Create a new subject linked to a course."""

    return service.create_subject(payload)


@router.patch(
    "/{subject_id}",
    response_model=SubjectRead,
    summary="Update subject",
)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    service: SubjectService = Depends(get_subject_service),
    _moderator: object = Depends(require_moderator),
) -> SubjectRead:
    """Update an existing subject entry."""

    return service.update_subject(subject_id, payload)


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete subject",
)
def delete_subject(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
    _moderator: object = Depends(require_moderator),
) -> None:
    """Delete a subject by its identifier."""

    service.delete_subject(subject_id)


__all__ = ["router", "get_subject_service"]
