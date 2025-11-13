"""FastAPI application factory for OpenCampus."""

from fastapi import FastAPI

from app.core.config import settings
from app.database.session import init_db
from app.routes import api_router


def create_app() -> FastAPI:
    """Create and configure a FastAPI application instance."""
    application = FastAPI(title=settings.project_name)

    @application.on_event("startup")
    def on_startup() -> None:
        """Initialize resources when the application starts."""
        init_db()

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    return application


app = create_app()

__all__ = ["app", "create_app"]
