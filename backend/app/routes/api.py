"""Primary API router definition."""

from fastapi import APIRouter

from app.routes.comment import router as comment_router
from app.routes.course import router as course_router
from app.routes.institution import router as institution_router
from app.routes.professor import router as professor_router
from app.routes.review import router as review_router
from app.routes.subject import router as subject_router
from app.routes.user import router as user_router

api_router = APIRouter()
api_router.include_router(institution_router)
api_router.include_router(course_router)
api_router.include_router(professor_router)
api_router.include_router(subject_router)
api_router.include_router(review_router)
api_router.include_router(comment_router)
api_router.include_router(user_router)


@api_router.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}


__all__ = ["api_router"]
