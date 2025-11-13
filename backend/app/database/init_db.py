"""Database initialization script placeholder."""

from app.database.session import init_db


def run() -> None:
    """Execute database initialization steps."""
    init_db()


if __name__ == "__main__":
    run()
