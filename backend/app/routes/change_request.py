"""API routes for submitting and moderating change requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_session
from app.models import ChangeRequestStatus, ReviewTargetType, User, UserRole
from app.schemas.change_request import ChangeRequestCreate, ChangeRequestRead
from app.services.change_request import ChangeRequestService

router = APIRouter(prefix="/change-requests", tags=["change-requests"])


def get_change_request_service(
    session: Session = Depends(get_session),
) -> ChangeRequestService:
    """Dependency injector for :class:`ChangeRequestService`."""

    return ChangeRequestService(session)


def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the requester has moderator privileges."""

    if current_user.role != UserRole.MODERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only moderators may access change request moderation endpoints.",
        )
    return current_user


@router.get(
    "",
    response_model=list[ChangeRequestRead],
    summary="List change requests",
)
def list_change_requests(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    status_filter: ChangeRequestStatus | None = Query(default=None, alias="status"),
    target_type: ReviewTargetType | None = None,
    service: ChangeRequestService = Depends(get_change_request_service),
    current_user: User = Depends(require_moderator),
) -> list[ChangeRequestRead]:
    """List change requests for moderator review."""

    requests = service.list_change_requests(
        status_filter=status_filter,
        target_type=target_type,
        skip=skip,
        limit=limit,
    )
    return list(requests)


@router.get(
    "/{change_request_id}",
    response_model=ChangeRequestRead,
    summary="Get change request",
)
def get_change_request(
    change_request_id: int,
    service: ChangeRequestService = Depends(get_change_request_service),
    current_user: User = Depends(require_moderator),
) -> ChangeRequestRead:
    """Retrieve a single change request for moderation review."""

    change_request = service.get_change_request(change_request_id)
    return ChangeRequestRead.model_validate(change_request)


@router.post(
    "",
    response_model=ChangeRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create change request",
)
def create_change_request(
    payload: ChangeRequestCreate,
    service: ChangeRequestService = Depends(get_change_request_service),
    current_user: User = Depends(get_current_user),
) -> ChangeRequestRead:
    """Allow any authenticated user to submit a change request."""

    return service.create_change_request(payload, current_user=current_user)


@router.post(
    "/{change_request_id}/approve",
    response_model=ChangeRequestRead,
    summary="Approve change request",
)
def approve_change_request(
    change_request_id: int,
    service: ChangeRequestService = Depends(get_change_request_service),
    current_user: User = Depends(require_moderator),
) -> ChangeRequestRead:
    """Approve a pending change request and apply its modifications."""

    return service.moderate_change_request(
        change_request_id,
        new_status=ChangeRequestStatus.APPROVED,
        current_user=current_user,
    )


@router.post(
    "/{change_request_id}/reject",
    response_model=ChangeRequestRead,
    summary="Reject change request",
)
def reject_change_request(
    change_request_id: int,
    service: ChangeRequestService = Depends(get_change_request_service),
    current_user: User = Depends(require_moderator),
) -> ChangeRequestRead:
    """Reject a pending change request."""

    return service.moderate_change_request(
        change_request_id,
        new_status=ChangeRequestStatus.REJECTED,
        current_user=current_user,
    )


__all__ = ["router", "get_change_request_service"]
