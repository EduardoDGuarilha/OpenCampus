"""Routes package."""

from app.routes.api import api_router
from app.routes.course import router as course_router
from app.routes.institution import router as institution_router

__all__ = ["api_router", "course_router", "institution_router"]
