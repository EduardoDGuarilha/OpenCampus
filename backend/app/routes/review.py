"""API router exposing review operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.models import ReviewTargetType, User, UserRole
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


def get_review_service(session: Session = Depends(get_session)) -> ReviewService:
    """Dependency injector for :class:`ReviewService`."""

    return ReviewService(session)


def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the requester has moderator privileges."""

    if current_user.role != UserRole.MODERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators may access review moderation endpoints.",
        )
    return current_user


@router.get("", response_model=list[ReviewRead], summary="List reviews")
def list_reviews(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    target_type: ReviewTargetType | None = None,
    target_id: int | None = None,
    user_id: int | None = None,
    include_pending: bool = False,
    service: ReviewService = Depends(get_review_service),
) -> list[ReviewRead]:
    """Retrieve reviews honoring visibility rules for pending entries."""

    reviews = service.list_reviews(
        target_type=target_type,
        target_id=target_id,
        user_id=user_id,
        include_pending=include_pending,
        skip=skip,
        limit=limit,
    )
    return list(reviews)


@router.get(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Get review by ID",
)
def get_review(
    review_id: int,
    include_pending: bool = False,
    service: ReviewService = Depends(get_review_service),
) -> ReviewRead:
    """Return a single review, restricting pending access by default."""

    review = service.get_review(review_id, include_pending=include_pending)
    return ReviewRead.model_validate(review)


@router.post(
    "",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create review",
)
def create_review(
    payload: ReviewCreate,
    service: ReviewService = Depends(get_review_service),
    current_user: User = Depends(get_current_user),
) -> ReviewRead:
    """Create a new review delegating validation to the service layer."""

    return service.create_review(payload, current_user=current_user)


@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Update review",
)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    service: ReviewService = Depends(get_review_service),
    current_user: User = Depends(get_current_user),
) -> ReviewRead:
    """Update review content using the service for permission checks."""

    return service.update_review(review_id, payload, current_user=current_user)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review",
)
def delete_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a review leveraging the service authorization rules."""

    service.delete_review(review_id, current_user=current_user)


@router.get(
    "/moderation/pending",
    response_model=list[ReviewRead],
    summary="List pending reviews for moderation",
)
def list_pending_reviews_for_moderation(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    target_type: ReviewTargetType | None = None,
    target_id: int | None = None,
    service: ReviewService = Depends(get_review_service),
    current_user: User = Depends(require_moderator),
) -> list[ReviewRead]:
    """Return pending reviews restricted to moderators."""

    reviews = service.list_pending_reviews(
        target_type=target_type,
        target_id=target_id,
        skip=skip,
        limit=limit,
    )
    return list(reviews)


@router.post(
    "/{review_id}/approve",
    response_model=ReviewRead,
    summary="Approve review",
)
def approve_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user: User = Depends(require_moderator),
) -> ReviewRead:
    """Approve a pending review as a moderator."""

    return service.approve_review(review_id, current_user=current_user)


@router.post(
    "/{review_id}/reject",
    response_model=ReviewRead,
    summary="Reject review",
)
def reject_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user: User = Depends(require_moderator),
) -> ReviewRead:
    """Reject a pending review as a moderator."""

    return service.reject_review(review_id, current_user=current_user)


@router.get(
    "/metrics",
    summary="Compute review metrics",
)
def compute_review_metrics(
    target_type: ReviewTargetType = Query(..., description="Target entity type"),
    target_id: int = Query(..., description="Target entity identifier"),
    service: ReviewService = Depends(get_review_service),
) -> dict[str, float | int | None]:
    """Expose aggregated metrics limited to approved reviews."""

    metrics = service.compute_metrics(target_type=target_type, target_id=target_id)
    return dict(metrics)


__all__ = ["router", "get_review_service"]
