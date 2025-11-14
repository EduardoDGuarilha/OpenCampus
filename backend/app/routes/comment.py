"""API routes exposing comment operations while enforcing business rules."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.models import User
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.services.comment import CommentService


router = APIRouter(prefix="/comments", tags=["comments"])


def get_comment_service(session: Session = Depends(get_session)) -> CommentService:
    """Dependency injector for :class:`CommentService`."""

    return CommentService(session)


@router.get("", response_model=list[CommentRead], summary="List comments")
def list_comments(
    review_id: int = Query(..., description="Identifier of the review to fetch comments for."),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    service: CommentService = Depends(get_comment_service),
) -> list[CommentRead]:
    """Retrieve comments for an approved review, preserving anonymity."""

    comments = service.list_comments(review_id, skip=skip, limit=limit)
    return list(comments)


@router.post(
    "",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create comment",
)
def create_comment(
    payload: CommentCreate,
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    """Create a new comment on an approved review for the current user."""

    return service.create_comment(payload, current_user=current_user)


@router.patch(
    "/{comment_id}",
    response_model=CommentRead,
    summary="Update comment",
)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    """Update an existing comment when the requester is authorized."""

    return service.update_comment(comment_id, payload, current_user=current_user)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
)
def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a comment using service-level permission checks."""

    service.delete_comment(comment_id, current_user=current_user)


__all__ = ["router", "get_comment_service"]

