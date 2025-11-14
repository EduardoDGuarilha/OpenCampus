"""API router for professor entity operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.schemas.professor import (
    ProfessorCreate,
    ProfessorRead,
    ProfessorUpdate,
)
from app.services.professor import ProfessorService

router = APIRouter(prefix="/professors", tags=["professors"])


def get_professor_service(session: Session = Depends(get_session)) -> ProfessorService:
    """Dependency provider for :class:`ProfessorService`."""

    return ProfessorService(session)


@router.get("", response_model=list[ProfessorRead], summary="List professors")
def list_professors(
    skip: int = 0,
    limit: int = 100,
    course_id: int | None = None,
    service: ProfessorService = Depends(get_professor_service),
) -> list[ProfessorRead]:
    """Retrieve a paginated collection of professors."""

    return list(service.list_professors(course_id=course_id, skip=skip, limit=limit))


@router.get(
    "/{professor_id}",
    response_model=ProfessorRead,
    summary="Get professor by ID",
)
def get_professor(
    professor_id: int,
    service: ProfessorService = Depends(get_professor_service),
) -> ProfessorRead:
    """Fetch a single professor by identifier."""

    professor = service.get_professor(professor_id)
    return ProfessorRead.model_validate(professor)


@router.post(
    "",
    response_model=ProfessorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create professor",
)
def create_professor(
    payload: ProfessorCreate,
    service: ProfessorService = Depends(get_professor_service),
    _current_user: object = Depends(get_current_user),
) -> ProfessorRead:
    """Create a new professor record linked to a course."""

    return service.create_professor(payload)


@router.patch(
    "/{professor_id}",
    response_model=ProfessorRead,
    summary="Update professor",
)
def update_professor(
    professor_id: int,
    payload: ProfessorUpdate,
    service: ProfessorService = Depends(get_professor_service),
    _current_user: object = Depends(get_current_user),
) -> ProfessorRead:
    """Update an existing professor entry."""

    return service.update_professor(professor_id, payload)


@router.delete(
    "/{professor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete professor",
)
def delete_professor(
    professor_id: int,
    service: ProfessorService = Depends(get_professor_service),
    _current_user: object = Depends(get_current_user),
) -> None:
    """Remove a professor entry."""

    service.delete_professor(professor_id)


__all__ = ["router", "get_professor_service"]
