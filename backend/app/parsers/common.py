"""Общие разборы длительности, хеш raw_record, коды состояния CM."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, date, datetime, time, timedelta

_UCID = re.compile(r"^\d{18,20}$")
_TRUNK = re.compile(r"^T\d+", re.IGNORECASE)
_HHMMSS = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")


def sha256_raw(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_hms(value: str) -> int:
    """'00:01:23' / '1:23' / '83' → секунды."""
    text = value.strip().strip('"')
    if not text:
        return 0
    if text.isdigit():
        return int(text)
    match = _HHMMSS.match(text)
    if not match:
        return 0
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def parse_mmss_token(token: str) -> int:
    """Четыре цифры CM unformatted: MMSS."""
    digits = token.strip()
    if not digits.isdigit():
        return 0
    padded = digits.zfill(4)
    return int(padded[:-2]) * 60 + int(padded[-2:])


def parse_hhmm_token(token: str) -> time:
    digits = token.strip().zfill(4)
    hour = int(digits[:2])
    minute = int(digits[2:])
    return time(hour=min(hour, 23), minute=min(minute, 59))


def combine_date_time(day: date, clock: time) -> datetime:
    return datetime(
        day.year, day.month, day.day, clock.hour, clock.minute, clock.second, tzinfo=UTC
    )


def parse_cm_date(token: str) -> date | None:
    text = token.strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def is_ucid(token: str) -> bool:
    return bool(_UCID.match(token.strip()))


def is_trunk(token: str) -> bool:
    return bool(_TRUNK.match(token.strip()))


def map_condition_code(code: str, duration_seconds: int) -> tuple[str, str]:
    """(direction, disposition) по condition code Avaya CM. Неизвестное → other."""
    key = code.strip().upper()
    answered = duration_seconds > 0
    table: dict[str, tuple[str, str]] = {
        "7": ("inbound", "abandoned" if not answered else "answered"),
        "8": ("outbound", "answered" if answered else "failed"),
        "9": ("inbound", "answered" if answered else "no_answer"),
        "A": ("unknown", "conferenced"),
        "C": ("unknown", "conferenced"),
        "0": ("unknown", "failed"),
        "4": ("inbound", "answered" if answered else "no_answer"),
        "10": ("inbound", "answered" if answered else "abandoned"),
    }
    if key in table:
        return table[key]
    return "unknown", "other"


def add_duration(start: datetime, seconds: int) -> datetime:
    return start + timedelta(seconds=max(seconds, 0))
