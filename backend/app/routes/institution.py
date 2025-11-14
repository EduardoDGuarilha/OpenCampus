"""API router for Institution entity operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionRead,
    InstitutionUpdate,
)
from app.services.institution import InstitutionService


router = APIRouter(prefix="/institutions", tags=["institutions"])


def get_institution_service(
    session: Session = Depends(get_session),
) -> InstitutionService:
    """Dependency provider for :class:`InstitutionService`."""

    return InstitutionService(session)


@router.get("", response_model=list[InstitutionRead], summary="List institutions")
def list_institutions(
    skip: int = 0,
    limit: int = 100,
    service: InstitutionService = Depends(get_institution_service),
) -> list[InstitutionRead]:
    """Retrieve a paginated list of institutions."""

    institutions = service.list_institutions(skip=skip, limit=limit)
    return list(institutions)


@router.get(
    "/{institution_id}",
    response_model=InstitutionRead,
    summary="Get institution by ID",
)
def get_institution(
    institution_id: int,
    service: InstitutionService = Depends(get_institution_service),
) -> InstitutionRead:
    """Fetch a single institution by its identifier."""

    institution = service.get_institution(institution_id)
    return InstitutionRead.model_validate(institution)


@router.post(
    "",
    response_model=InstitutionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create institution",
)
def create_institution(
    payload: InstitutionCreate,
    service: InstitutionService = Depends(get_institution_service),
    _current_user: object = Depends(get_current_user),
) -> InstitutionRead:
    """Create a new institution entry."""

    return service.create_institution(payload)


@router.patch(
    "/{institution_id}",
    response_model=InstitutionRead,
    summary="Update institution",
)
def update_institution(
    institution_id: int,
    payload: InstitutionUpdate,
    service: InstitutionService = Depends(get_institution_service),
    _current_user: object = Depends(get_current_user),
) -> InstitutionRead:
    """Update an existing institution."""

    return service.update_institution(institution_id, payload)


@router.delete(
    "/{institution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete institution",
)
def delete_institution(
    institution_id: int,
    service: InstitutionService = Depends(get_institution_service),
    _current_user: object = Depends(get_current_user),
) -> None:
    """Delete an institution by its identifier."""

    service.delete_institution(institution_id)


__all__ = ["router", "get_institution_service"]

