"""Base service module placeholder."""

from typing import Protocol


class ServiceProtocol(Protocol):
    """Protocol for service interfaces."""

    def __call__(self, *args, **kwargs):  # type: ignore[override]
        ...
