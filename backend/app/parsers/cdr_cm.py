"""Парсеры IP-CDR Communication Manager: unformatted / expanded / customized."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, time

from app.parsers.common import (
    combine_date_time,
    is_trunk,
    is_ucid,
    map_condition_code,
    parse_cm_date,
    parse_hhmm_token,
    parse_hms,
    parse_mmss_token,
)
from app.parsers.types import NormalizedCdr

_DATE_START = re.compile(r"^\d{2}/\d{2}/\d{2}")


def detect_cm_format(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "|" in stripped or "\t" in stripped[:80]:
            return "customized"
        if _DATE_START.match(stripped):
            return "expanded"
        return "unformatted"
    return "unformatted"


def parse_cm_text(text: str, *, default_day: date | None = None) -> list[NormalizedCdr]:
    fmt = detect_cm_format(text)
    if fmt == "customized":
        return parse_customized(text)
    if fmt == "expanded":
        return parse_expanded(text)
    return parse_unformatted(text, default_day=default_day)


def parse_unformatted(text: str, *, default_day: date | None = None) -> list[NormalizedCdr]:
    day = default_day or datetime.now(UTC).date()
    rows: list[NormalizedCdr] = []
    for line in text.splitlines():
        raw = line.rstrip("\n")
        tokens = raw.split()
        if len(tokens) < 6:
            continue
        clock = parse_hhmm_token(tokens[0])
        duration = parse_mmss_token(tokens[1])
        cond = tokens[2]
        start = combine_date_time(day, clock)
        direction, disposition = map_condition_code(cond, duration)
        ext = tokens[7] if len(tokens) > 7 else None
        rows.append(
            NormalizedCdr(
                start_time=start,
                duration_seconds=duration,
                condition_code=cond,
                access_code_dialed=tokens[3],
                access_code_used=tokens[4],
                dialed_number=tokens[5],
                calling_number=tokens[6] if len(tokens) > 6 else None,
                agent_extension=ext,
                connected_number=ext,
                direction=direction,
                disposition=disposition,
                is_conferenced=disposition == "conferenced",
                raw_record=raw.strip(),
                source_system="cm",
            )
        )
    return rows


def parse_expanded(text: str) -> list[NormalizedCdr]:
    rows: list[NormalizedCdr] = []
    for line in text.splitlines():
        raw = line.rstrip("\n")
        tokens = raw.split()
        if len(tokens) < 6:
            continue
        day = parse_cm_date(tokens[0])
        if day is None:
            continue
        clock = (
            datetime.strptime(tokens[1], "%H:%M").time()
            if ":" in tokens[1]
            else parse_hhmm_token(tokens[1])
        )
        duration = parse_hms(tokens[2]) if ":" in tokens[2] else parse_mmss_token(tokens[2])
        cond = tokens[3]
        code_dial = tokens[4]
        code_used = tokens[5]
        rest = tokens[6:]
        dialed = rest[0] if rest else None
        calling = rest[1] if len(rest) > 1 else None
        trunks: list[str] = []
        ext: str | None = None
        ucid: str | None = None
        for token in rest[2:]:
            if is_ucid(token):
                ucid = token
            elif is_trunk(token):
                trunks.append(token.upper())
            elif ext is None:
                ext = token
        direction, disposition = map_condition_code(cond, duration)
        start = combine_date_time(day, clock)
        rows.append(
            NormalizedCdr(
                start_time=start,
                duration_seconds=duration,
                condition_code=cond,
                access_code_dialed=code_dial,
                access_code_used=code_used,
                dialed_number=dialed,
                calling_number=calling,
                agent_extension=ext,
                connected_number=ext,
                trunk_in=trunks[0] if trunks else None,
                trunk_out=trunks[1] if len(trunks) > 1 else None,
                ucid=ucid,
                direction=direction,
                disposition=disposition,
                is_conferenced=disposition == "conferenced",
                raw_record=raw.strip(),
                source_system="cm",
            )
        )
    return rows


def parse_customized(text: str, *, delimiter: str | None = None) -> list[NormalizedCdr]:
    lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    sep = delimiter or ("|" if "|" in lines[0] else "&")
    header = [h.strip().lower() for h in lines[0].split(sep)]
    rows: list[NormalizedCdr] = []
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(sep)]
        rec = {header[i]: parts[i] if i < len(parts) else "" for i in range(len(header))}
        day = parse_cm_date(rec.get("date") or rec.get("cdr_date") or "")
        clock_raw = rec.get("time") or rec.get("tod") or "00:00:00"
        try:
            if clock_raw.count(":") == 1:
                clock = datetime.strptime(clock_raw, "%H:%M").time()
            else:
                clock = datetime.strptime(clock_raw, "%H:%M:%S").time()
        except ValueError:
            clock = time(0, 0)
        if rec.get("duration_s"):
            duration = parse_hms(rec["duration_s"])
        else:
            duration = parse_hms(rec.get("duration") or "0")
        cond = rec.get("cond") or rec.get("condition") or rec.get("condition_code") or ""
        disp_override = rec.get("disposition")
        direction, disposition = map_condition_code(cond, duration)
        if disp_override:
            disposition = disp_override
        start = combine_date_time(day or datetime.now(UTC).date(), clock)
        rows.append(
            NormalizedCdr(
                start_time=start,
                duration_seconds=duration,
                condition_code=cond or None,
                dialed_number=rec.get("dialed") or rec.get("dialed_number") or None,
                calling_number=rec.get("calling") or rec.get("calling_number") or None,
                agent_extension=rec.get("ext") or rec.get("extension") or None,
                connected_number=rec.get("ext") or None,
                trunk_in=rec.get("in_trk") or rec.get("trunk_in") or None,
                trunk_out=rec.get("out_trk") or rec.get("trunk_out") or None,
                ucid=rec.get("ucid") or None,
                direction=direction,
                disposition=disposition,
                is_conferenced=disposition == "conferenced",
                raw_record=line.strip(),
                source_system="cm",
            )
        )
    return rows
