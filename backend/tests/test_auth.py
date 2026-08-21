"""Опциональный HTTP Basic: пустой пользователь — открытый API."""

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


def test_open_api_when_basic_user_empty() -> None:
    client = TestClient(create_app())
    assert client.get("/api/health").status_code == 200


def test_basic_auth_rejects_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_BASIC_AUTH_USER", "ops")
    monkeypatch.setenv("APP_BASIC_AUTH_PASSWORD", "secret")
    get_settings.cache_clear()
    client = TestClient(create_app())
    assert client.get("/api/health").status_code == 401


def test_basic_auth_accepts_matching_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_BASIC_AUTH_USER", "ops")
    monkeypatch.setenv("APP_BASIC_AUTH_PASSWORD", "secret")
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/api/health", auth=("ops", "secret"))
    assert response.status_code == 200
