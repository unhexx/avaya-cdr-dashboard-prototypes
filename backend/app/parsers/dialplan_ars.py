"""Парсер SAT `list ars analysis` → строки dialplan_entries (source=ars)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ArsRow:
    """Одна строка ARS ANALYSIS."""

    match_prefix: str
    min_digits: int | None
    max_digits: int | None
    route: str | None
    call_type: str | None
    node_number: str | None
    location: str | None
    raw: str


_HEADER_RE = re.compile(r"Location:\s*(\S+)", re.IGNORECASE)
# Dialed String | Min | Max | Route Pattern | Call Type | [Node Number]
_ROW_RE = re.compile(
    r"^(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$"
)


def _is_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    lower = stripped.lower()
    if lower.startswith("command "):
        return True
    if "ars analysis" in lower:
        return True
    if "dialed" in lower and "string" in lower:
        return True
    if "time zone" in lower:
        return True
    if set(stripped) <= {"-", "=", " "}:
        return True
    if lower in {"string", "min max", "pattern", "number"}:
        return True
    return False


def parse_list_ars_analysis(text: str) -> list[ArsRow]:
    """Разбор колоночного дампа list ars analysis."""
    location: str | None = None
    rows: list[ArsRow] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        loc_match = _HEADER_RE.search(line)
        if loc_match:
            location = loc_match.group(1)
            continue
        if _is_noise(line):
            continue
        match = _ROW_RE.match(line)
        if not match:
            continue
        prefix, amin, amax, route, call_type, node = match.groups()
        rows.append(
            ArsRow(
                match_prefix=prefix,
                min_digits=int(amin),
                max_digits=int(amax),
                route=route,
                call_type=call_type,
                node_number=node,
                location=location,
                raw=line,
            )
        )
    return rows
