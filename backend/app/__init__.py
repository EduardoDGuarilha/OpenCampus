"""OpenCampus backend application package."""

from importlib import import_module
from typing import Any

__all__ = ["app", "create_app"]


def __getattr__(name: str) -> Any:
    """Lazily import application objects to avoid side effects during tests."""

    if name in __all__:
        module = import_module("app.main")
        return getattr(module, name)
    raise AttributeError(f"module 'app' has no attribute {name!r}")
