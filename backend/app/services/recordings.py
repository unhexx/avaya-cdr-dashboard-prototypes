"""Сервис метаданных записей и раздачи аудио (200 WAV / 409 encrypted)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from app.config import get_settings
from app.connectors.sql_source import load_fixture_recordings
from app.services.cdr_ingest import find_fixtures_root


def _iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    return value


def is_encrypted(row: dict[str, Any]) -> bool:
    """Флаг SQL, hint ipo_r11 или суффикс .enc — без расшифровки."""
    if row.get("encrypted"):
        return True
    hint = (row.get("encryption_hint") or "").lower()
    if hint in {"ipo_r11", "ipo_encrypted_r11"}:
        return True
    filename = row.get("filename") or ""
    return isinstance(filename, str) and filename.endswith(".enc")


def recording_out(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "ucid": row.get("ucid"),
        "cdr_id": row.get("cdr_id"),
        "start_time": _iso(row.get("start_time")),
        "duration_seconds": row.get("duration_seconds"),
        "calling_number": row.get("calling_number"),
        "dialed_number": row.get("dialed_number"),
        "filename": row.get("filename"),
        "mime_type": row.get("mime_type"),
        "encrypted": bool(row.get("encrypted")),
        "encryption_hint": row.get("encryption_hint"),
        "sql_source_id": row.get("sql_source_id"),
    }


def resolve_media_path(filename: str, media_root: Path) -> Path:
    """Безопасный join: отказ при path traversal."""
    if not filename or ".." in Path(filename).parts or filename.startswith(("/", "\\")):
        raise ValueError("invalid_filename")
    root = media_root.resolve()
    target = (root / filename).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError("path_traversal")
    return target


def default_media_root() -> Path:
    settings = get_settings()
    if settings.recordings_media_root:
        return Path(settings.recordings_media_root)
    return find_fixtures_root() / "recordings"


class RecordingsService(Protocol):
    async def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        ucid: str | None = None,
        encrypted: bool | None = None,
    ) -> dict[str, Any]: ...

    async def get(self, recording_id: int) -> dict[str, Any] | None: ...

    async def get_audio(self, recording_id: int) -> tuple[str, bytes] | dict[str, Any]: ...

    async def load_fixtures(self) -> int: ...


class InMemoryRecordingsService:
    """In-memory каталог из sql-фикстур; аудио с диска RECORDINGS_MEDIA_ROOT."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self._rows: list[dict[str, Any]] = list(rows or [])
        self._by_id: dict[int, dict[str, Any]] = {int(r["id"]): r for r in self._rows}

    async def load_fixtures(self) -> int:
        loaded = load_fixture_recordings()
        self._rows = loaded
        self._by_id = {int(r["id"]): r for r in self._rows}
        return len(self._rows)

    async def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        ucid: str | None = None,
        encrypted: bool | None = None,
    ) -> dict[str, Any]:
        items = list(self._rows)
        if ucid:
            items = [r for r in items if (r.get("ucid") or "") == ucid]
        if encrypted is not None:
            items = [r for r in items if bool(r.get("encrypted")) is encrypted]
        items = sorted(
            items,
            key=lambda r: r.get("start_time") or datetime.min,
            reverse=True,
        )
        total = len(items)
        page = max(1, page)
        page_size = max(1, min(page_size, 500))
        start = (page - 1) * page_size
        slice_ = items[start : start + page_size]
        return {
            "items": [recording_out(r) for r in slice_],
            "page": page,
            "page_size": page_size,
            "total": total,
        }

    async def get(self, recording_id: int) -> dict[str, Any] | None:
        row = self._by_id.get(recording_id)
        if row is None:
            return None
        return recording_out(row)

    async def get_audio(self, recording_id: int) -> tuple[str, bytes] | dict[str, Any]:
        """Возвращает (mime, bytes) или dict ошибки encrypted/not_found/missing_file."""
        row = self._by_id.get(recording_id)
        if row is None:
            return {"error": "not_found"}
        meta = recording_out(row)
        if is_encrypted(row) and not get_settings().recordings_allow_encrypted_audio:
            return {
                "error": "encrypted",
                "recording": meta,
            }
        filename = row.get("filename")
        if not filename:
            return {"error": "missing_file", "recording": meta}
        try:
            path = resolve_media_path(str(filename), default_media_root())
        except ValueError:
            return {"error": "missing_file", "recording": meta}
        if not path.is_file():
            return {"error": "missing_file", "recording": meta}
        data = path.read_bytes()
        # Никогда не отдаём мусор: для WAV проверяем RIFF/WAVE
        mime = row.get("mime_type") or "audio/wav"
        if mime == "audio/wav" and not (data.startswith(b"RIFF") and b"WAVE" in data[:16]):
            return {"error": "missing_file", "recording": meta}
        return (str(mime), data)


_default_service: InMemoryRecordingsService | None = None


def get_default_recordings_service() -> InMemoryRecordingsService:
    global _default_service
    if _default_service is None:
        _default_service = InMemoryRecordingsService()
    return _default_service


def reset_recordings_service() -> None:
    global _default_service
    _default_service = None
