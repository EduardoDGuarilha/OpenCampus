"""Change request SQLModel definition."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field

from .base import BaseModel
from .review import ReviewTargetType


class ChangeRequestStatus(str, Enum):
    """Statuses applicable to change requests moderated by the platform."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ChangeRequest(BaseModel, table=True):
    """Represents a request to modify academic catalog data."""

    __tablename__ = "change_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    target_type: ReviewTargetType = Field(nullable=False, index=True)
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    status: ChangeRequestStatus = Field(
        default=ChangeRequestStatus.PENDING,
        nullable=False,
        index=True,
    )
    created_by: int = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    resolved_by: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )
    resolved_at: Optional[datetime] = Field(default=None, nullable=True)


__all__ = ["ChangeRequest", "ChangeRequestStatus"]
