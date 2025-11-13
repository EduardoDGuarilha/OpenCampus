"""Primary API router definition."""

from fastapi import APIRouter

from app.routes.institution import router as institution_router

api_router = APIRouter()
api_router.include_router(institution_router)


@api_router.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}


__all__ = ["api_router"]
