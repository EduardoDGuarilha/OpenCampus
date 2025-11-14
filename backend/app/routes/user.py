"""API router handling user management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    """Provide a :class:`UserService` instance for route handlers."""

    return UserService(session)


def _ensure_moderator(current_user: User) -> None:
    """Guard utility ensuring the requester is a moderator."""

    if current_user.role != UserRole.MODERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators can access this resource.",
        )


@router.get("", response_model=list[UserRead], summary="List users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> list[UserRead]:
    """Return a paginated list of users for moderators."""

    _ensure_moderator(current_user)
    users = service.list_users(skip=skip, limit=limit)
    return list(users)


@router.get("/me", response_model=UserRead, summary="Retrieve current user")
def read_current_user(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """Fetch the authenticated user profile without exposing sensitive data."""

    user = service.get_user(current_user.id)
    return UserRead.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by ID",
)
def read_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """Retrieve user details for moderators."""

    _ensure_moderator(current_user)
    user = service.get_user(user_id)
    return UserRead.model_validate(user)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """Create a new user account."""

    return service.create_user(payload)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update user",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """Update a user profile while ensuring appropriate permissions."""

    if current_user.role != UserRole.MODERATOR and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this user.",
        )

    return service.update_user(user_id, payload)


__all__ = ["router", "get_user_service"]

