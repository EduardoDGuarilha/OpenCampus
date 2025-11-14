"""Course service layer implementations."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from sqlmodel import Session, select

from app.models import Course, Institution


def list_courses(session: Session) -> list[Course]:
    """Return all courses ordered alphabetically."""

    statement = select(Course).order_by(Course.name)
    return list(session.exec(statement).all())


def get_course(session: Session, course_id: int) -> Optional[Course]:
    """Retrieve a single course by its identifier."""

    return session.get(Course, course_id)


def _ensure_institution_exists(session: Session, institution_id: int) -> None:
    """Raise an error if the referenced institution does not exist."""

    institution = session.get(Institution, institution_id)
    if institution is None:
        raise ValueError("Institution not found")


def create_course(session: Session, payload: Mapping[str, Any]) -> Course:
    """Create a new course ensuring the institution exists."""

    institution_id = payload.get("institution_id")
    if institution_id is None:
        raise ValueError("Institution is required")

    _ensure_institution_exists(session, int(institution_id))

    course = Course(**payload)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def update_course(
    session: Session, course: Course, payload: Mapping[str, Any]
) -> Course:
    """Update an existing course, validating the institution when provided."""

    if "institution_id" in payload and payload["institution_id"] is not None:
        _ensure_institution_exists(session, int(payload["institution_id"]))

    for field, value in payload.items():
        setattr(course, field, value)

    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def delete_course(session: Session, course: Course) -> None:
    """Remove a course from the database."""

    session.delete(course)
    session.commit()
