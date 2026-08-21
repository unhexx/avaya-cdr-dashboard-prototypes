"""Записи: список метаданных, 200 WAV и 409 encrypted."""

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.recordings import get_recordings_service
from app.connectors.sql_source import SqlSourceConnector
from app.main import create_app
from app.services.recordings import (
    InMemoryRecordingsService,
    is_encrypted,
    recording_out,
    reset_recordings_service,
    resolve_media_path,
)


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


def test_resolve_media_path_rejects_traversal(tmp_path: Path) -> None:
    root = tmp_path / "media"
    root.mkdir()
    (root / "ok.wav").write_bytes(b"RIFF....WAVEfmt ")
    with pytest.raises(ValueError):
        resolve_media_path("../etc/passwd", root)
    with pytest.raises(ValueError):
        resolve_media_path("../../etc/passwd", root)
    with pytest.raises(ValueError):
        resolve_media_path("/etc/passwd", root)
    with pytest.raises(ValueError):
        resolve_media_path("subdir/../../etc/passwd", root)
    assert resolve_media_path("ok.wav", root).is_file()


def test_resolve_media_path_rejects_symlink_escape(tmp_path: Path) -> None:
    """Sibling prefix + symlink: is_relative_to must reject (not str.startswith)."""
    root = tmp_path / "rec_test_root"
    root.mkdir()
    sibling = tmp_path / "rec_test_root2"
    sibling.mkdir()
    evil = sibling / "evil.wav"
    evil.write_bytes(b"RIFF....WAVEfmt ")
    escape = root / "escape"
    escape.mkdir()
    link = escape / "evil.wav"
    link.symlink_to(evil)
    # Fragile startswith would accept; is_relative_to must fail after resolve().
    with pytest.raises(ValueError, match="path_traversal"):
        resolve_media_path("escape/evil.wav", root)


def test_garbage_wav_returns_404(
    api: tuple[TestClient, InMemoryRecordingsService],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, svc = api
    garbage = tmp_path / "garbage.wav"
    garbage.write_bytes(b"not-a-riff-wave-payload-at-all")
    monkeypatch.setenv("RECORDINGS_MEDIA_ROOT", str(tmp_path))
    from app.config import get_settings

    get_settings.cache_clear()
    row = {
        "id": 9001,
        "ucid": "garbage-ucid",
        "start_time": datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        "duration_seconds": 1,
        "calling_number": "100",
        "dialed_number": "200",
        "filename": "garbage.wav",
        "mime_type": "audio/wav",
        "encrypted": False,
        "encryption_hint": "none",
        "sql_source_id": "rec-garbage",
    }
    svc._rows.append(row)  # noqa: SLF001
    svc._by_id[9001] = row  # noqa: SLF001
    response = client.get("/api/recordings/9001/audio")
    assert response.status_code == 404
    assert b"RIFF" not in response.content


def test_traversal_filename_audio_404(
    api: tuple[TestClient, InMemoryRecordingsService],
) -> None:
    client, svc = api
    row = {
        "id": 9002,
        "ucid": "trav",
        "start_time": datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
        "duration_seconds": 1,
        "calling_number": "100",
        "dialed_number": "200",
        "filename": "../etc/passwd",
        "mime_type": "audio/wav",
        "encrypted": False,
        "encryption_hint": "none",
        "sql_source_id": "rec-trav",
    }
    svc._rows.append(row)  # noqa: SLF001
    svc._by_id[9002] = row  # noqa: SLF001
    response = client.get("/api/recordings/9002/audio")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "audio_missing"


def test_recording_out_uses_is_encrypted_for_hint_only() -> None:
    row = {
        "id": 1,
        "encrypted": False,
        "encryption_hint": "ipo_r11",
        "filename": "x.wav",
        "start_time": datetime(2026, 8, 21, tzinfo=UTC),
    }
    assert is_encrypted(row) is True
    assert recording_out(row)["encrypted"] is True
    enc_suffix = {
        "id": 2,
        "encrypted": False,
        "encryption_hint": "none",
        "filename": "call.enc",
        "start_time": datetime(2026, 8, 21, tzinfo=UTC),
    }
    assert recording_out(enc_suffix)["encrypted"] is True


@pytest.mark.asyncio
async def test_sql_url_without_select_is_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RECORDINGS_SQL_URL", "postgresql+asyncpg://u:p@127.0.0.1:1/rec")
    from app.config import get_settings

    get_settings.cache_clear()
    conn = SqlSourceConnector()
    await conn.start()
    health = await conn.poll_health()
    assert health["status"] == "degraded"
    assert health["mode"] == "sql_stub"
    assert health["count"] == 0
