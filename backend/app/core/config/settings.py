"""Application configuration module.

This module will host configuration settings and environment parsing logic.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Placeholder settings class for future configuration."""

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Return application settings instance."""
    return Settings()


__all__ = ["Settings", "get_settings"]
