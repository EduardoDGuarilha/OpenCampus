"""Service layer for subject entity operations."""

from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Course, Subject
from app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate


class SubjectService:
    """Encapsulate business rules for managing subjects."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_subjects(
        self, *, course_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> Sequence[SubjectRead]:
        statement = select(Subject).order_by(Subject.name).offset(skip).limit(limit)
        if course_id is not None:
            statement = statement.where(Subject.course_id == course_id)

        subjects = self.session.exec(statement).all()
        return [SubjectRead.model_validate(subject) for subject in subjects]

    def get_subject(self, subject_id: int) -> Subject:
        subject = self.session.get(Subject, subject_id)
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found.",
            )
        return subject

    def create_subject(self, payload: SubjectCreate) -> SubjectRead:
        normalized_name = self._normalize_name(payload.name)
        self._ensure_course_exists(payload.course_id)
        self._ensure_unique_within_course(normalized_name, payload.course_id)

        subject = Subject(name=normalized_name, course_id=payload.course_id)
        self.session.add(subject)
        self.session.commit()
        self.session.refresh(subject)
        return SubjectRead.model_validate(subject)

    def update_subject(
        self,
        subject_id: int,
        payload: SubjectUpdate,
        *,
        commit: bool = True,
    ) -> SubjectRead:
        subject = self.get_subject(subject_id)
        update_data = payload.model_dump(exclude_unset=True)

        new_name = subject.name
        if "name" in update_data:
            raw_name = update_data["name"]
            if raw_name is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="name cannot be null.",
                )
            new_name = self._normalize_name(raw_name)

        target_course_id = subject.course_id
        if "course_id" in update_data:
            course_id = update_data["course_id"]
            if course_id is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="course_id cannot be null.",
                )
            self._ensure_course_exists(course_id)
            target_course_id = course_id

        if ("name" in update_data) or ("course_id" in update_data):
            self._ensure_unique_within_course(
                new_name, target_course_id, exclude_subject_id=subject.id
            )

        subject.name = new_name
        subject.course_id = target_course_id

        self.session.add(subject)
        if commit:
            self.session.commit()
            self.session.refresh(subject)
        else:
            self.session.flush()
        return SubjectRead.model_validate(subject)

    def delete_subject(self, subject_id: int) -> None:
        subject = self.get_subject(subject_id)
        self.session.delete(subject)
        self.session.commit()

    def _normalize_name(self, name: str) -> str:
        normalized = " ".join(name.split()).strip()
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Subject name cannot be empty.",
            )
        return normalized

    def _ensure_course_exists(self, course_id: int) -> None:
        course = self.session.get(Course, course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

    def _ensure_unique_within_course(
        self, name: str, course_id: int, *, exclude_subject_id: int | None = None
    ) -> None:
        statement = select(Subject).where(
            Subject.course_id == course_id, Subject.name == name
        )
        if exclude_subject_id is not None:
            statement = statement.where(Subject.id != exclude_subject_id)

        if self.session.exec(statement).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A subject with this name already exists for the course.",
            )


__all__ = ["SubjectService"]

