"""Загрузка syslog-фикстур SIP/E1 и фильтрация для GET /api/logs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.parsers.syslog_e1 import is_alarm_line, is_e1_line, parse_alarm_line, parse_e1_line
from app.parsers.syslog_sip import (
    NormalizedLogEvent,
    is_sip_line,
    parse_sip_line,
    parse_syslog_header,
)
from app.services.cdr_ingest import find_fixtures_root


def _syslog_dir(root: Path | None = None) -> Path:
    base = root or find_fixtures_root()
    return base / "syslog"


def parse_syslog_line(raw: str) -> NormalizedLogEvent | None:
    """Эвристика kind: sip | e1 | alarm | other."""
    line = raw.strip()
    if not line:
        return None
    _ts, _host, _sev, body = parse_syslog_header(line)
    msg = body or line
    if is_sip_line(msg) or is_sip_line(line):
        return parse_sip_line(line)
    if is_e1_line(msg) or is_e1_line(line):
        return parse_e1_line(line)
    if is_alarm_line(msg):
        return parse_alarm_line(line)
    event_time, host, severity, message = parse_syslog_header(line)
    if event_time is None:
        event_time = datetime(2026, 8, 21, 0, 0, tzinfo=UTC)
    return NormalizedLogEvent(
        kind="other",
        event_time=event_time,
        host=host,
        severity=severity,
        message=message or line,
        raw=line,
    )


def load_fixture_logs(root: Path | None = None) -> list[NormalizedLogEvent]:
    directory = _syslog_dir(root)
    rows: list[NormalizedLogEvent] = []
    if not directory.is_dir():
        return rows
    for path in sorted(directory.glob("*.log")):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if not line.strip():
                continue
            if path.name.startswith("sip"):
                ev = parse_sip_line(line) or parse_syslog_line(line)
            elif path.name.startswith("e1"):
                ev = parse_e1_line(line) or parse_syslog_line(line)
            else:
                ev = parse_syslog_line(line)
            if ev is not None:
                rows.append(ev)
    rows.sort(key=lambda e: e.event_time, reverse=True)
    return rows


def _event_out(ev: NormalizedLogEvent, idx: int) -> dict[str, Any]:
    return {
        "id": idx,
        "pbx_node_id": None,
        "kind": ev.kind,
        "event_time": ev.event_time.isoformat(),
        "host": ev.host,
        "severity": ev.severity,
        "call_id": ev.call_id,
        "sip_method": ev.sip_method,
        "sip_response": ev.sip_response,
        "ds1_board": ev.ds1_board,
        "alarm_type": ev.alarm_type,
        "message": ev.message,
        "raw": ev.raw,
    }


def list_logs(
    *,
    kind: str | None = None,
    from_: datetime | None = None,
    to: datetime | None = None,
    q: str | None = None,
    call_id: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    events = load_fixture_logs(root)
    if kind:
        events = [e for e in events if e.kind == kind]
    if from_ is not None:
        events = [e for e in events if e.event_time >= from_]
    if to is not None:
        events = [e for e in events if e.event_time <= to]
    if call_id:
        needle = call_id.lower()
        events = [e for e in events if e.call_id and needle in e.call_id.lower()]
    if q:
        needle = q.lower()
        events = [e for e in events if needle in e.message.lower() or needle in e.raw.lower()]
    items = [_event_out(e, i + 1) for i, e in enumerate(events)]
    return {"items": items, "total": len(items)}


def ingest_log_fixtures(root: Path | None = None) -> dict[str, int]:
    """Подсчёт разобранных строк фикстур (персистенция в БД — следующий срез)."""
    rows = load_fixture_logs(root)
    by_kind: dict[str, int] = {}
    for row in rows:
        by_kind[row.kind] = by_kind.get(row.kind, 0) + 1
    return {
        "logs": len(rows),
        "logs_sip": by_kind.get("sip", 0),
        "logs_e1": by_kind.get("e1", 0),
        "logs_alarm": by_kind.get("alarm", 0),
    }
