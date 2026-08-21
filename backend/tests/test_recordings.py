"""Записи: список метаданных, 200 WAV и 409 encrypted."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.recordings import get_recordings_service
from app.main import create_app
from app.services.recordings import InMemoryRecordingsService, reset_recordings_service


@pytest.fixture
def api() -> Iterator[tuple[TestClient, InMemoryRecordingsService]]:
    reset_recordings_service()
    svc = InMemoryRecordingsService()
    application = create_app()

    async def _override() -> InMemoryRecordingsService:
        if not svc._rows:  # noqa: SLF001
            await svc.load_fixtures()
        return svc

    application.dependency_overrides[get_recordings_service] = _override
    with TestClient(application) as client:
        yield client, svc
    reset_recordings_service()


def test_list_recordings_from_fixtures(api: tuple[TestClient, InMemoryRecordingsService]) -> None:
    client, _svc = api
    response = client.get("/api/recordings")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 3
    assert len(body["items"]) >= 3
    encrypted = [r for r in body["items"] if r["encrypted"]]
    plain = [r for r in body["items"] if not r["encrypted"]]
    assert plain
    assert encrypted
    assert any(r["encryption_hint"] == "ipo_r11" for r in encrypted)


def test_audio_unencrypted_returns_wav(api: tuple[TestClient, InMemoryRecordingsService]) -> None:
    client, _svc = api
    listed = client.get("/api/recordings").json()["items"]
    plain = next(r for r in listed if not r["encrypted"])
    response = client.get(f"/api/recordings/{plain['id']}/audio")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    data = response.content
    assert data.startswith(b"RIFF")
    assert b"WAVE" in data[:16]
    assert len(data) > 44  # не пустой / не мусор


def test_audio_encrypted_returns_409(api: tuple[TestClient, InMemoryRecordingsService]) -> None:
    client, _svc = api
    listed = client.get("/api/recordings").json()["items"]
    enc = next(r for r in listed if r["encrypted"])
    response = client.get(f"/api/recordings/{enc['id']}/audio")
    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "recording_encrypted"
    assert body["error"]["reason"] == "ipo_encrypted_r11"
    assert body["recording"]["encrypted"] is True
    assert body["recording"]["id"] == enc["id"]


def test_recording_detail_and_404(api: tuple[TestClient, InMemoryRecordingsService]) -> None:
    client, _svc = api
    listed = client.get("/api/recordings").json()["items"]
    rid = listed[0]["id"]
    ok = client.get(f"/api/recordings/{rid}")
    assert ok.status_code == 200
    assert ok.json()["id"] == rid
    missing = client.get("/api/recordings/999999/audio")
    assert missing.status_code == 404


def test_openapi_documents_recordings() -> None:
    reset_recordings_service()
    client = TestClient(create_app())
    spec = client.get("/api/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/api/recordings" in paths
    assert "/api/recordings/{recording_id}/audio" in paths
