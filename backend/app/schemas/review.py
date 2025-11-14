"""Pydantic schemas for Review entity respecting anonymity constraints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.models.review import ReviewTargetType
from app.schemas.base import SchemaBase


class ReviewBase(SchemaBase):
    """Shared attributes across Review schemas."""

    rating_1: int
    rating_2: int
    rating_3: int
    rating_4: int
    rating_5: int
    text: str


class ReviewCreate(ReviewBase):
    """Schema for creating a review without exposing author identity."""

    target_type: ReviewTargetType
    institution_id: Optional[int] = None
    course_id: Optional[int] = None
    professor_id: Optional[int] = None
    subject_id: Optional[int] = None


class ReviewUpdate(SchemaBase):
    """Schema for updating review attributes during moderation."""

    rating_1: Optional[int] = None
    rating_2: Optional[int] = None
    rating_3: Optional[int] = None
    rating_4: Optional[int] = None
    rating_5: Optional[int] = None
    text: Optional[str] = None
    approved: Optional[bool] = None


class ReviewRead(ReviewBase):
    """Schema for reading review data while keeping authors anonymous."""

    id: int
    target_type: ReviewTargetType
    institution_id: Optional[int] = None
    course_id: Optional[int] = None
    professor_id: Optional[int] = None
    subject_id: Optional[int] = None
    approved: bool
    created_at: datetime


__all__ = [
    "ReviewBase",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewRead",
]

