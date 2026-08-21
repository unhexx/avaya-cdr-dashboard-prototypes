"""Классификатор и разбор SIP-строк syslog (SM / SBCE). SysMonitor не реализуется; без pcap."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

# PRI → severity (RFC 5424)
_SEV_NAMES = (
    "emerg",
    "alert",
    "crit",
    "err",
    "warning",
    "notice",
    "info",
    "debug",
)

_RFC5424 = re.compile(
    r"^<(?P<pri>\d+)>"
    r"(?P<version>\d+)\s+"
    r"(?P<ts>\S+)\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<app>\S+)\s+"
    r"\S+\s+"  # procid
    r"\S+\s+"  # msgid
    r"(?P<msg>.*)$"
)

_BSD = re.compile(
    r"^<(?P<pri>\d+)>"
    r"(?P<mon>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<msg>.*)$"
)

_CALL_ID = re.compile(r"Call-ID:\s*(\S+)", re.IGNORECASE)
_CSEQ = re.compile(r"CSeq:\s*\d+\s+(\w+)", re.IGNORECASE)
_RESP = re.compile(r"SIP/2\.0\s+(\d{3})")
_METHOD = re.compile(
    r"\b(INVITE|ACK|BYE|CANCEL|REGISTER|OPTIONS|PRACK|UPDATE|REFER|SUBSCRIBE|NOTIFY|INFO|MESSAGE|PUBLISH)\b",
    re.IGNORECASE,
)

_SIP_HINTS = (
    "INVITE",
    "SIP/2.0",
    "CSeq:",
    "Call-ID:",
    "traceSM",
    " SBCE ",
    "SIP:",
)


@dataclass
class NormalizedLogEvent:
    """Нормализованное событие syslog до записи в log_events."""

    kind: str
    event_time: datetime
    message: str
    raw: str
    host: str | None = None
    severity: str | None = None
    call_id: str | None = None
    sip_method: str | None = None
    sip_response: int | None = None
    ds1_board: str | None = None
    alarm_type: str | None = None


def _pri_severity(pri: int) -> str:
    return _SEV_NAMES[pri % 8]


def _parse_ts(token: str) -> datetime | None:
    text = token.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def parse_syslog_header(raw: str) -> tuple[datetime | None, str | None, str | None, str]:
    """(event_time, host, severity, message_body)."""
    line = raw.strip()
    m = _RFC5424.match(line)
    if m:
        ts = _parse_ts(m.group("ts"))
        sev = _pri_severity(int(m.group("pri")))
        return ts, m.group("host"), sev, m.group("msg").strip()
    m = _BSD.match(line)
    if m:
        # Год фикстур проекта
        stamp = f"2026 {m.group('mon')} {int(m.group('day')):02d} {m.group('time')}"
        try:
            ts = datetime.strptime(stamp, "%Y %b %d %H:%M:%S").replace(tzinfo=UTC)
        except ValueError:
            ts = None
        sev = _pri_severity(int(m.group("pri")))
        return ts, m.group("host"), sev, m.group("msg").strip()
    return None, None, None, line


def is_sip_line(message: str) -> bool:
    upper = message.upper()
    return any(hint.upper() in upper for hint in _SIP_HINTS)


def parse_sip_line(raw: str) -> NormalizedLogEvent | None:
    """Разбор одной SIP-строки. None, если не SIP."""
    event_time, host, severity, body = parse_syslog_header(raw)
    if not is_sip_line(body) and not is_sip_line(raw):
        return None
    msg = body or raw.strip()
    call_id = None
    m = _CALL_ID.search(msg)
    if m:
        call_id = m.group(1).rstrip(";")
    sip_response: int | None = None
    rm = _RESP.search(msg)
    if rm:
        sip_response = int(rm.group(1))
    sip_method: str | None = None
    cm = _CSEQ.search(msg)
    if cm:
        sip_method = cm.group(1).upper()
    else:
        mm = _METHOD.search(msg)
        if mm:
            sip_method = mm.group(1).upper()
    if event_time is None:
        event_time = datetime(2026, 8, 21, 0, 0, tzinfo=UTC)
    return NormalizedLogEvent(
        kind="sip",
        event_time=event_time,
        host=host,
        severity=severity,
        call_id=call_id,
        sip_method=sip_method,
        sip_response=sip_response,
        message=msg,
        raw=raw.strip(),
    )


def parse_sip_text(text: str) -> list[NormalizedLogEvent]:
    rows: list[NormalizedLogEvent] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        ev = parse_sip_line(line)
        if ev is not None:
            rows.append(ev)
    return rows
