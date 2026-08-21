"""Liveness /api/health без живой АТС."""

import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.config import get_settings
from app.main import create_app


def test_health_returns_fixtures_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_FIXTURES", "true")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://avaya:avaya@127.0.0.1:1/avaya_cdr",
    )
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert body["fixtures"] is True
    assert body["db"] in {"ok", "down"}


def test_health_openapi_documents_route() -> None:
    client = TestClient(create_app())
    spec = client.get("/api/openapi.json")
    assert spec.status_code == 200
    assert "/api/health" in spec.json()["paths"]
