"""Коннектор sql-source для метаданных записей (MariaDB/PostgreSQL или фикстуры)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.services.cdr_ingest import find_fixtures_root


def _parse_dt(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def map_sql_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Маппинг строки ACR/sidecar → канонический dict для recording_meta."""
    filename = raw.get("filename") or raw.get("path") or raw.get("file_name")
    encrypted = bool(raw.get("encrypted") or raw.get("is_encrypted"))
    hint = raw.get("encryption_hint")
    if not encrypted and isinstance(filename, str) and filename.endswith(".enc"):
        encrypted = True
        hint = hint or "ipo_r11"
    return {
        "sql_source_id": str(raw.get("sql_source_id") or raw.get("id") or ""),
        "ucid": raw.get("ucid") or raw.get("unique_call_id") or raw.get("callid"),
        "start_time": _parse_dt(raw.get("start_time") or raw.get("created")),
        "duration_seconds": raw.get("duration_seconds")
        if raw.get("duration_seconds") is not None
        else raw.get("duration"),
        "calling_number": raw.get("calling_number") or raw.get("caller"),
        "dialed_number": raw.get("dialed_number") or raw.get("called"),
        "filename": filename,
        "mime_type": raw.get("mime_type")
        or ("audio/wav" if not encrypted else "application/octet-stream"),
        "encrypted": encrypted,
        "encryption_hint": hint or ("ipo_r11" if encrypted else "none"),
        "extra": {
            k: v
            for k, v in raw.items()
            if k
            not in {
                "sql_source_id",
                "id",
                "ucid",
                "unique_call_id",
                "callid",
                "start_time",
                "created",
                "duration_seconds",
                "duration",
                "calling_number",
                "caller",
                "dialed_number",
                "called",
                "filename",
                "path",
                "file_name",
                "mime_type",
                "encrypted",
                "is_encrypted",
                "encryption_hint",
            }
        },
    }


def load_fixture_recordings(root: Path | None = None) -> list[dict[str, Any]]:
    """Читает docs/fixtures/sql/recordings.json — источник правды для CI."""
    base = root or find_fixtures_root()
    path = base / "sql" / "recordings.json"
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("recordings", payload) if isinstance(payload, dict) else payload
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(rows, start=1):
        mapped = map_sql_row(raw)
        mapped["id"] = i
        out.append(mapped)
    return out


class SqlSourceConnector:
    """ADR 0005: SELECT метаданных; живой DSN опционален, иначе фикстуры."""

    name = "sql_source"

    def __init__(self) -> None:
        self._rows: list[dict[str, Any]] = []
        self._sql_stub = False

    async def start(self) -> None:
        settings = get_settings()
        if settings.recordings_sql_url:
            # Живой SELECT откладываем: v1 CI работает на фикстурах.
            # DSN задан → stub (degraded), без ложного «ok / sql».
            self._rows = []
            self._sql_stub = True
            return
        self._sql_stub = False
        self._rows = load_fixture_recordings()

    async def stop(self) -> None:
        self._rows = []
        self._sql_stub = False

    async def poll_health(self) -> dict[str, Any]:
        settings = get_settings()
        if settings.recordings_sql_url:
            return {
                "name": self.name,
                "status": "degraded",
                "mode": "sql_stub",
                "count": 0,
                "detail": "RECORDINGS_SQL_URL set; live SELECT not implemented in this slice",
            }
        return {
            "name": self.name,
            "status": "ok",
            "mode": "fixtures",
            "count": len(self._rows),
        }

    async def ingest_once(self) -> Sequence[dict[str, Any]]:
        if not self._rows:
            await self.start()
        return list(self._rows)
