"""Course API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.models.user import User, UserRole
from app.schemas import CourseCreate, CourseRead, CourseUpdate
from app.services import (
    create_course,
    delete_course,
    get_course,
    list_courses,
    update_course,
)

router = APIRouter(prefix="/courses", tags=["courses"])


def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the authenticated user has moderator privileges."""

    if current_user.role != UserRole.MODERATOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return current_user


def _handle_value_error(error: ValueError) -> None:
    """Translate service validation errors into HTTP exceptions."""

    detail = str(error)
    if "not found" in detail.lower():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from error
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from error


@router.get("/", response_model=list[CourseRead])
def list_courses_endpoint(
    session: Session = Depends(get_session),
) -> list[CourseRead]:
    """Return all courses ordered alphabetically."""

    courses = list_courses(session)
    return [CourseRead.model_validate(course) for course in courses]


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course_endpoint(
    payload: CourseCreate,
    session: Session = Depends(get_session),
    _moderator: User = Depends(require_moderator),
) -> CourseRead:
    """Create a new course entry."""

    try:
        course = create_course(session, payload.model_dump())
    except ValueError as error:  # pragma: no cover - thin translation layer
        _handle_value_error(error)

    return CourseRead.model_validate(course)


@router.get("/{course_id}", response_model=CourseRead)
def retrieve_course_endpoint(
    course_id: int,
    session: Session = Depends(get_session),
) -> CourseRead:
    """Retrieve a single course by identifier."""

    course = get_course(session, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return CourseRead.model_validate(course)


@router.put("/{course_id}", response_model=CourseRead)
def update_course_endpoint(
    course_id: int,
    payload: CourseUpdate,
    session: Session = Depends(get_session),
    _moderator: User = Depends(require_moderator),
) -> CourseRead:
    """Update a course's attributes."""

    course = get_course(session, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    data = payload.model_dump(exclude_unset=True)
    try:
        updated = update_course(session, course, data)
    except ValueError as error:  # pragma: no cover - thin translation layer
        _handle_value_error(error)

    return CourseRead.model_validate(updated)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_endpoint(
    course_id: int,
    session: Session = Depends(get_session),
    _moderator: User = Depends(require_moderator),
) -> None:
    """Delete a course."""

    course = get_course(session, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    delete_course(session, course)


__all__ = ["router", "require_moderator"]
