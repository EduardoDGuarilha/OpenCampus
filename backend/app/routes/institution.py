"""Institution API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database.session import get_session
from app.schemas import InstitutionCreate, InstitutionRead, InstitutionUpdate
from app.services import (
    create_institution,
    delete_institution,
    get_institution,
    list_institutions,
    update_institution,
)

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("/", response_model=list[InstitutionRead])
def list_institutions_endpoint(
    session: Session = Depends(get_session),
) -> list[InstitutionRead]:
    """Return all institutions."""

    institutions = list_institutions(session)
    return [InstitutionRead.model_validate(institution) for institution in institutions]


@router.post("/", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED)
def create_institution_endpoint(
    payload: InstitutionCreate,
    session: Session = Depends(get_session),
) -> InstitutionRead:
    """Create a new institution entry."""

    institution = create_institution(session, payload.model_dump())
    return InstitutionRead.model_validate(institution)


@router.get("/{institution_id}", response_model=InstitutionRead)
def retrieve_institution_endpoint(
    institution_id: int,
    session: Session = Depends(get_session),
) -> InstitutionRead:
    """Retrieve a single institution by identifier."""

    institution = get_institution(session, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    return InstitutionRead.model_validate(institution)


@router.put("/{institution_id}", response_model=InstitutionRead)
def update_institution_endpoint(
    institution_id: int,
    payload: InstitutionUpdate,
    session: Session = Depends(get_session),
) -> InstitutionRead:
    """Update an institution's attributes."""

    institution = get_institution(session, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    updated = update_institution(session, institution, payload.model_dump(exclude_unset=True))
    return InstitutionRead.model_validate(updated)


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_institution_endpoint(
    institution_id: int,
    session: Session = Depends(get_session),
) -> None:
    """Delete an institution."""

    institution = get_institution(session, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    delete_institution(session, institution)


__all__ = ["router"]
