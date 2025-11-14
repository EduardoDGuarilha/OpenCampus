"""Service layer for professor entity operations."""

from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Course, Professor
from app.schemas.professor import ProfessorCreate, ProfessorRead, ProfessorUpdate


class ProfessorService:
    """Encapsulate business rules for managing professors."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_professors(
        self, *, course_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> Sequence[ProfessorRead]:
        statement = select(Professor).order_by(Professor.name).offset(skip).limit(limit)
        if course_id is not None:
            statement = statement.where(Professor.course_id == course_id)

        professors = self.session.exec(statement).all()
        return [ProfessorRead.model_validate(professor) for professor in professors]

    def get_professor(self, professor_id: int) -> Professor:
        professor = self.session.get(Professor, professor_id)
        if professor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professor not found.",
            )
        return professor

    def create_professor(self, payload: ProfessorCreate) -> ProfessorRead:
        normalized_name = self._normalize_name(payload.name)
        self._ensure_course_exists(payload.course_id)

        professor = Professor(name=normalized_name, course_id=payload.course_id)
        self.session.add(professor)
        self.session.commit()
        self.session.refresh(professor)
        return ProfessorRead.model_validate(professor)

    def update_professor(
        self,
        professor_id: int,
        payload: ProfessorUpdate,
        *,
        commit: bool = True,
    ) -> ProfessorRead:
        professor = self.get_professor(professor_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data:
            professor.name = self._normalize_name(update_data["name"])

        if "course_id" in update_data:
            course_id = update_data["course_id"]
            if course_id is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="course_id cannot be null.",
                )
            self._ensure_course_exists(course_id)
            professor.course_id = course_id

        self.session.add(professor)
        if commit:
            self.session.commit()
            self.session.refresh(professor)
        else:
            self.session.flush()
        return ProfessorRead.model_validate(professor)

    def delete_professor(self, professor_id: int) -> None:
        professor = self.get_professor(professor_id)
        self.session.delete(professor)
        self.session.commit()

    def _normalize_name(self, name: str) -> str:
        normalized = " ".join(name.split()).strip()
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Professor name cannot be empty.",
            )
        return normalized

    def _ensure_course_exists(self, course_id: int) -> None:
        course = self.session.get(Course, course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )


__all__ = ["ProfessorService"]
