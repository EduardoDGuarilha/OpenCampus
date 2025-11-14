"""Pydantic schemas for ChangeRequest entity."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from app.models.change_request import ChangeRequestStatus
from app.models.review import ReviewTargetType
from app.schemas.base import SchemaBase


class ChangeRequestBase(SchemaBase):
    """Shared attributes for change request schemas."""

    target_type: ReviewTargetType
    payload: Dict[str, Any]


class ChangeRequestCreate(ChangeRequestBase):
    """Schema used when submitting a new change request."""


class ChangeRequestUpdate(SchemaBase):
    """Schema for moderators updating a change request."""

    payload: Optional[Dict[str, Any]] = None
    status: Optional[ChangeRequestStatus] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None


class ChangeRequestRead(ChangeRequestBase):
    """Schema for reading change request data."""

    id: int
    status: ChangeRequestStatus
    created_by: int
    created_at: datetime
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None


__all__ = [
    "ChangeRequestBase",
    "ChangeRequestCreate",
    "ChangeRequestUpdate",
    "ChangeRequestRead",
]
