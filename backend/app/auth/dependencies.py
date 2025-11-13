"""Authentication dependency placeholders."""


def get_current_user():
    """Placeholder for retrieving the current authenticated user."""
    raise NotImplementedError


__all__ = ["get_current_user"]
