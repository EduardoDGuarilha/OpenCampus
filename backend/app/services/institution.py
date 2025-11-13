"""Service layer for Institution entity operations."""

from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionRead, InstitutionUpdate


class InstitutionService:
    """Business rules and persistence operations for institutions."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _normalize_name(self, name: str) -> str:
        normalized = " ".join(name.split()).strip()
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Institution name cannot be empty.",
            )
        return normalized

    def _ensure_unique_name(self, name: str, exclude_id: int | None = None) -> None:
        query = select(Institution).where(Institution.name == name)
        if exclude_id is not None:
            query = query.where(Institution.id != exclude_id)

        exists = self.session.exec(query).first()
        if exists is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An institution with this name already exists.",
            )

    def list_institutions(self, *, skip: int = 0, limit: int = 100) -> Sequence[InstitutionRead]:
        statement = select(Institution).offset(skip).limit(limit)
        institutions = self.session.exec(statement).all()
        return [InstitutionRead.model_validate(institution) for institution in institutions]

    def get_institution(self, institution_id: int) -> Institution:
        institution = self.session.get(Institution, institution_id)
        if institution is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found.",
            )
        return institution

    def create_institution(self, payload: InstitutionCreate) -> InstitutionRead:
        normalized_name = self._normalize_name(payload.name)
        self._ensure_unique_name(normalized_name)

        institution = Institution(name=normalized_name)
        self.session.add(institution)
        self.session.commit()
        self.session.refresh(institution)
        return InstitutionRead.model_validate(institution)

    def update_institution(self, institution_id: int, payload: InstitutionUpdate) -> InstitutionRead:
        institution = self.get_institution(institution_id)

        if payload.name is not None:
            normalized_name = self._normalize_name(payload.name)
            if normalized_name != institution.name:
                self._ensure_unique_name(normalized_name, exclude_id=institution.id)
                institution.name = normalized_name

        self.session.add(institution)
        self.session.commit()
        self.session.refresh(institution)
        return InstitutionRead.model_validate(institution)

    def delete_institution(self, institution_id: int) -> None:
        institution = self.get_institution(institution_id)

        self.session.delete(institution)
        self.session.commit()


__all__ = ["InstitutionService"]

