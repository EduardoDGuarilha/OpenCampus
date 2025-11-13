"""Database session management utilities."""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config.settings import get_settings


settings = get_settings()
engine = create_engine("sqlite:///./opencampus.db", echo=False, future=True)


def init_db() -> None:
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Provide a SQLModel session context."""
    with Session(engine) as session:
        yield session


__all__ = ["engine", "init_db", "get_session"]
