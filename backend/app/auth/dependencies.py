"""Authentication dependencies for FastAPI routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select

from app.auth.security import decode_token, verify_password
from app.core.config import settings
from app.database.session import get_session
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
    scheme_name="JWT",
)


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Validate credentials returning the user when successful."""

    normalized_email = email.lower()
    statement = select(User).where(User.email == normalized_email)
    user = session.exec(statement).first()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """Retrieve the currently authenticated user from the JWT token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except JWTError as exc:  # pragma: no cover - error path
        raise credentials_exception from exc

    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:  # pragma: no cover - safety net
        raise credentials_exception from exc

    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user


__all__ = ["authenticate_user", "get_current_user", "oauth2_scheme"]
