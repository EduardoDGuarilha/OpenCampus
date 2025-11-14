"""Service layer for user account operations."""

from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Course, User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.auth.security import hash_password


class UserService:
    """Encapsulate business rules for managing user accounts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_users(self, *, skip: int = 0, limit: int = 100) -> Sequence[UserRead]:
        statement = select(User).offset(skip).limit(limit)
        users = self.session.exec(statement).all()
        return [UserRead.model_validate(user) for user in users]

    def get_user(self, user_id: int) -> User:
        user = self.session.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    def create_user(self, payload: UserCreate) -> UserRead:
        cpf = payload.cpf.strip()
        email = payload.email.lower()

        self._ensure_unique_cpf(cpf)
        self._ensure_unique_email(email)

        if payload.course_id is not None:
            self._ensure_course_exists(payload.course_id)

        user = User(
            cpf=cpf,
            email=email,
            password_hash=hash_password(payload.password),
            course_id=payload.course_id,
            role=payload.role,
            validated=payload.validated,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserRead.model_validate(user)

    def update_user(self, user_id: int, payload: UserUpdate) -> UserRead:
        user = self.get_user(user_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "cpf" in update_data:
            new_cpf = update_data["cpf"].strip()
            if new_cpf != user.cpf:
                self._ensure_unique_cpf(new_cpf, exclude_user_id=user.id)
                user.cpf = new_cpf

        if "email" in update_data:
            new_email = update_data["email"].lower()
            if new_email != user.email:
                self._ensure_unique_email(new_email, exclude_user_id=user.id)
                user.email = new_email

        if "password" in update_data:
            user.password_hash = hash_password(update_data["password"])

        if "course_id" in update_data:
            course_id = update_data["course_id"]
            if course_id is not None:
                self._ensure_course_exists(course_id)
            user.course_id = course_id

        if "role" in update_data and update_data["role"] is not None:
            user.role = update_data["role"]

        if "validated" in update_data and update_data["validated"] is not None:
            user.validated = update_data["validated"]

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserRead.model_validate(user)

    def _ensure_unique_cpf(self, cpf: str, *, exclude_user_id: int | None = None) -> None:
        statement = select(User).where(User.cpf == cpf)
        if exclude_user_id is not None:
            statement = statement.where(User.id != exclude_user_id)

        if self.session.exec(statement).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF already registered.",
            )

    def _ensure_unique_email(self, email: str, *, exclude_user_id: int | None = None) -> None:
        statement = select(User).where(User.email == email)
        if exclude_user_id is not None:
            statement = statement.where(User.id != exclude_user_id)

        if self.session.exec(statement).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered.",
            )

    def _ensure_course_exists(self, course_id: int) -> None:
        course = self.session.get(Course, course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )


__all__ = ["UserService"]

