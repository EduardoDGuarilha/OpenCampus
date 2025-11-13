"""Institution service layer implementations."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from sqlmodel import Session, select

from app.models import Institution


def list_institutions(session: Session) -> list[Institution]:
    """Return all institutions ordered alphabetically."""

    statement = select(Institution).order_by(Institution.name)
    return list(session.exec(statement).all())


def get_institution(session: Session, institution_id: int) -> Optional[Institution]:
    """Retrieve a single institution by its identifier."""

    return session.get(Institution, institution_id)


def create_institution(session: Session, payload: Mapping[str, Any]) -> Institution:
    """Create a new institution from the provided payload."""

    institution = Institution(**payload)
    session.add(institution)
    session.commit()
    session.refresh(institution)
    return institution


def update_institution(
    session: Session, institution: Institution, payload: Mapping[str, Any]
) -> Institution:
    """Update an existing institution using the provided payload."""

    for field, value in payload.items():
        setattr(institution, field, value)

    session.add(institution)
    session.commit()
    session.refresh(institution)
    return institution


def delete_institution(session: Session, institution: Institution) -> None:
    """Remove an institution from the database."""

    session.delete(institution)
    session.commit()
