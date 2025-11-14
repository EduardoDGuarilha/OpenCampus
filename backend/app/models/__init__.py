"""Data models package."""

from app.models.course import Course
from app.models.institution import Institution
from app.models.professor import Professor
from app.models.user import User, UserRole

__all__ = ["Institution", "Course", "Professor", "User", "UserRole"]
