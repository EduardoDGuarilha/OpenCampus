"""Application configuration utilities."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Define application settings and environment configuration."""

    project_name: str = "OpenCampus API"
    api_v1_prefix: str = "/api/v1"
    sqlite_file: Path = Path("opencampus.db")
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Return the database URL for SQLModel."""
        return f"sqlite:///{self.sqlite_file.resolve()}"

    @property
    def database_url_async(self) -> str:
        """Return the async database URL (reserved for future use)."""
        return f"sqlite+aiosqlite:///{self.sqlite_file.resolve()}"


@lru_cache

def get_settings() -> Settings:
    """Provide a cached settings instance."""

    return Settings()


settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
