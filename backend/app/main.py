from fastapi import FastAPI

app = FastAPI(title="OpenCampus API")


def create_app() -> FastAPI:
    """Create and configure a FastAPI application instance."""
    return app


__all__ = ["app", "create_app"]
