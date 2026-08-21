"""Классификатор и разбор E1/DS1 syslog (MEDPRO). SysMonitor не реализуется."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from app.parsers.syslog_sip import NormalizedLogEvent, parse_syslog_header

_E1_HINTS = (
    "DS1",
    "LOS",
    "RAI",
    "AIS",
    "SLIP",
    "MEDPRO",
    "board 0",
    "BPV",
    "CRC=",
)

_ALARM_TYPES = ("LOS", "RAI", "AIS", "SLIP", "CRC", "BPV")
_BOARD = re.compile(r"DS1\s+(\S+)", re.IGNORECASE)
_ALARM = re.compile(
    r"\b(LOS|RAI|AIS|SLIP|CRC|BPV)\b",
    re.IGNORECASE,
)


def is_e1_line(message: str) -> bool:
    upper = message.upper()
    return any(hint.upper() in upper for hint in _E1_HINTS)


def is_alarm_line(message: str) -> bool:
    """CM alarm / SBCE ALARM (не DS1)."""
    upper = message.upper()
    if "ALARM" in upper and "DS1" not in upper:
        return True
    if "MAJOR ALARM" in upper or "MINOR ALARM" in upper:
        return True
    return False


def parse_e1_line(raw: str) -> NormalizedLogEvent | None:
    """Разбор одной E1/DS1-строки. None, если не E1."""
    event_time, host, severity, body = parse_syslog_header(raw)
    msg = body or raw.strip()
    if not is_e1_line(msg) and not is_e1_line(raw):
        return None
    ds1_board = None
    bm = _BOARD.search(msg)
    if bm:
        ds1_board = bm.group(1)
    alarm_type = None
    am = _ALARM.search(msg)
    if am:
        alarm_type = am.group(1).upper()
        if alarm_type not in _ALARM_TYPES:
            alarm_type = alarm_type
    if event_time is None:
        event_time = datetime(2026, 8, 21, 0, 0, tzinfo=UTC)
    return NormalizedLogEvent(
        kind="e1",
        event_time=event_time,
        host=host,
        severity=severity,
        ds1_board=ds1_board,
        alarm_type=alarm_type,
        message=msg,
        raw=raw.strip(),
    )


def parse_alarm_line(raw: str) -> NormalizedLogEvent | None:
    event_time, host, severity, body = parse_syslog_header(raw)
    msg = body or raw.strip()
    if not is_alarm_line(msg):
        return None
    if event_time is None:
        event_time = datetime(2026, 8, 21, 0, 0, tzinfo=UTC)
    return NormalizedLogEvent(
        kind="alarm",
        event_time=event_time,
        host=host,
        severity=severity,
        message=msg,
        raw=raw.strip(),
    )


def parse_e1_text(text: str) -> list[NormalizedLogEvent]:
    rows: list[NormalizedLogEvent] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        ev = parse_e1_line(line)
        if ev is not None:
            rows.append(ev)
    return rows
