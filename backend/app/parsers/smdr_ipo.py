"""SMDR IP Office: CSV по заголовкам, не по позициям колонок."""

from __future__ import annotations

import csv
import io
import re
from datetime import UTC, datetime

from app.parsers.common import parse_hms
from app.parsers.types import NormalizedCdr

_EXTN = re.compile(r"Extn(\d+)", re.IGNORECASE)
_VDN = re.compile(r"Vdn(\d+)", re.IGNORECASE)

_DIR = {"I": "inbound", "O": "outbound", "L": "internal"}


def _cell(row: dict[str, str], *names: str) -> str:
    lower = {k.strip().lower(): (v or "").strip().strip('"') for k, v in row.items()}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return ""


def _parse_start(value: str) -> datetime | None:
    text = value.strip().strip('"')
    for fmt in ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%y %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def parse_smdr_csv(text: str) -> list[NormalizedCdr]:
    reader = csv.DictReader(io.StringIO(text))
    rows: list[NormalizedCdr] = []
    for row in reader:
        raw = ",".join((row.get(h) or "") for h in (reader.fieldnames or []))
        start = _parse_start(_cell(row, "Call Start", "Start"))
        if start is None:
            continue
        duration = parse_hms(_cell(row, "Connected Time", "Duration"))
        ring = parse_hms(_cell(row, "Ring Time", "Ring Duration"))
        hold = parse_hms(_cell(row, "Hold Time"))
        park = parse_hms(_cell(row, "Park Time"))
        direction = _DIR.get(_cell(row, "Direction").upper(), "unknown")
        continuation = _cell(row, "Continuation") in {"1", "true", "Y", "yes"}
        internal = _cell(row, "Is Internal") in {"1", "true", "Y", "yes"}
        party1 = _cell(row, "Party1Device")
        party2 = _cell(row, "Party2Device")
        extn = _EXTN.search(party1)
        vdn_m = _VDN.search(party2) or _VDN.search(party1)
        caller = _cell(row, "Caller")
        called = _cell(row, "Called Number", "Called")
        dialled = _cell(row, "Dialled Number", "Dialed Number")
        if duration == 0:
            disposition = "abandoned" if direction == "inbound" else "no_answer"
        elif continuation:
            disposition = "transferred"
        else:
            disposition = "answered"
        rows.append(
            NormalizedCdr(
                start_time=start,
                duration_seconds=duration,
                ring_duration_seconds=ring,
                hold_duration_seconds=hold,
                park_duration_seconds=park,
                calling_number=caller or None,
                dialed_number=called or dialled or None,
                connected_number=called or None,
                direction=direction,
                disposition=disposition,
                account_code=_cell(row, "Account") or None,
                ucid=_cell(row, "Unique Call ID") or None,
                call_id=_cell(row, "Call ID") or None,
                agent_extension=extn.group(1) if extn else None,
                vdn=vdn_m.group(1) if vdn_m else None,
                is_internal=internal,
                is_transferred=continuation,
                raw_record=raw,
                source_system="ipo",
            )
        )
    return rows
