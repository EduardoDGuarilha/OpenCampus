"""Authentication endpoints for token issuance and registration."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.dependencies import authenticate_user
from app.auth.security import create_access_token
from app.database.session import get_session
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    """Provide the user service for dependency injection."""

    return UserService(session)


@router.post("/login", response_model=TokenResponse, summary="Authenticate user")
def login_for_access_token(
    payload: LoginRequest, session: Session = Depends(get_session)
) -> TokenResponse:
    """Issue a JWT when the provided credentials are valid."""

    user = authenticate_user(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
def register_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRead:
    """Register a new platform user using the domain rules."""

    return service.create_user(payload)


__all__ = ["router", "get_user_service"]

