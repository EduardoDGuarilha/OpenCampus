"""Tests for moderator-only route protections."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.main import create_app
from app.models import UserRole


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Return a FastAPI test client without triggering database setup."""

    app = create_app()
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def non_moderator_user() -> Any:
    """Provide a sample non-moderator user-like object."""

    class _UserMock:
        role = UserRole.STUDENT

    return _UserMock()


ProtectedEndpoint = tuple[str, str, dict[str, Any]]


def _protected_endpoints() -> list[ProtectedEndpoint]:
    """Return HTTP method, URL and kwargs for moderator-protected routes."""

    return [
        ("post", "/api/v1/courses/", {"json": {"name": "New Course", "institution_id": 1}}),
        ("put", "/api/v1/courses/1", {"json": {"name": "Updated"}}),
        ("delete", "/api/v1/courses/1", {}),
        ("post", "/api/v1/institutions", {"json": {"name": "Inst"}}),
        ("patch", "/api/v1/institutions/1", {"json": {"name": "Inst"}}),
        ("delete", "/api/v1/institutions/1", {}),
        ("post", "/api/v1/professors", {"json": {"name": "Prof", "course_id": 1}}),
        ("patch", "/api/v1/professors/1", {"json": {"name": "Prof"}}),
        ("delete", "/api/v1/professors/1", {}),
        ("post", "/api/v1/subjects", {"json": {"name": "Subject", "course_id": 1}}),
        ("patch", "/api/v1/subjects/1", {"json": {"name": "Subject"}}),
        ("delete", "/api/v1/subjects/1", {}),
    ]


@pytest.mark.parametrize("method,url,request_kwargs", _protected_endpoints())
def test_requires_authentication(
    client: TestClient,
    method: str,
    url: str,
    request_kwargs: dict[str, Any],
) -> None:
    """Missing credentials should yield HTTP 401 on protected endpoints."""

    response = client.request(method, url, **request_kwargs)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("method,url,request_kwargs", _protected_endpoints())
def test_requires_moderator_role(
    client: TestClient,
    non_moderator_user: Any,
    method: str,
    url: str,
    request_kwargs: dict[str, Any],
) -> None:
    """Authenticated non-moderator users must receive HTTP 403."""

    client.app.dependency_overrides[get_current_user] = lambda: non_moderator_user
    try:
        response = client.request(method, url, **request_kwargs)
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == status.HTTP_403_FORBIDDEN
