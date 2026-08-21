"""Нормализованная запись CDR до записи в PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedCdr:
    start_time: datetime
    raw_record: str
    source_system: str
    duration_seconds: int = 0
    ring_duration_seconds: int = 0
    hold_duration_seconds: int = 0
    park_duration_seconds: int = 0
    calling_number: str | None = None
    dialed_number: str | None = None
    connected_number: str | None = None
    direction: str = "unknown"
    disposition: str = "other"
    condition_code: str | None = None
    access_code_dialed: str | None = None
    access_code_used: str | None = None
    trunk_in: str | None = None
    trunk_out: str | None = None
    account_code: str | None = None
    auth_code: str | None = None
    vdn: str | None = None
    agent_extension: str | None = None
    ucid: str | None = None
    call_id: str | None = None
    is_internal: bool = False
    is_transferred: bool = False
    is_conferenced: bool = False
    extra: dict[str, str] = field(default_factory=dict)
