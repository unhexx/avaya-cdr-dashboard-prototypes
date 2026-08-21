"""Чистые парсеры CDR/SMDR. Без I/O к АТС."""

from app.parsers.cdr_cm import detect_cm_format, parse_cm_text
from app.parsers.smdr_ipo import parse_smdr_csv
from app.parsers.types import NormalizedCdr

__all__ = [
    "NormalizedCdr",
    "detect_cm_format",
    "parse_cm_text",
    "parse_smdr_csv",
]
