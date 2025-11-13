"""Primary API router definition."""

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}


__all__ = ["api_router"]
