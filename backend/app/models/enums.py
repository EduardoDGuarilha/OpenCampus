"""Domain enumerations for SQLModel entities."""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Available roles for authenticated users."""

    STUDENT = "STUDENT"
    PROFESSOR = "PROFESSOR"
    INSTITUTION = "INSTITUTION"
    MODERATOR = "MODERATOR"


class ReviewTargetType(str, Enum):
    """Supported review targets."""

    INSTITUTION = "INSTITUTION"
    COURSE = "COURSE"
    PROFESSOR = "PROFESSOR"
    SUBJECT = "SUBJECT"


class ChangeRequestStatus(str, Enum):
    """Possible statuses for change requests moderation."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
