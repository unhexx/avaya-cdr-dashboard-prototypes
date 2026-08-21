"""Чистые парсеры CDR/SMDR/SAT. Без I/O к АТС."""

from app.parsers.cdr_cm import detect_cm_format, parse_cm_text
from app.parsers.sat_health import (
    is_sat_allowed,
    parse_display_alarms,
    parse_status_ds1,
    parse_status_health,
)
from app.parsers.smdr_ipo import parse_smdr_csv
from app.parsers.types import NormalizedCdr

__all__ = [
    "NormalizedCdr",
    "detect_cm_format",
    "is_sat_allowed",
    "parse_cm_text",
    "parse_display_alarms",
    "parse_smdr_csv",
    "parse_status_ds1",
    "parse_status_health",
]
